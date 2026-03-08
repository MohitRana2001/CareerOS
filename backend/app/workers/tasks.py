"""Celery tasks for async job orchestration."""

import uuid
from datetime import UTC, datetime

import httpx
from celery import Celery
from sqlalchemy import func, select

from app.ai.gemini_client import GeminiClientError, generate_tailored_content
from app.ai.prompts import build_tailor_prompt
from app.config import settings
from app.db import SessionLocal
from app.models import JobDescription, ResumeDocument, ResumeVersion, TailorRun

celery = Celery("resume_tailor", broker=settings.redis_url, backend=settings.redis_url)


@celery.task(name="extract_resume")
def extract_resume(resume_document_id: str) -> dict[str, str]:
    return {"status": "QUEUED", "resume_document_id": resume_document_id}


@celery.task(bind=True, name="tailor_resume", max_retries=3)
def tailor_resume(self, tailor_run_id: str) -> dict[str, str]:
    run_uuid = uuid.UUID(tailor_run_id)

    try:
        with SessionLocal() as db:
            run = db.get(TailorRun, run_uuid)
            if run is None:
                return {"status": "NOT_FOUND", "tailor_run_id": tailor_run_id}

            if run.output_resume_version_id is not None and run.status == "SUCCEEDED":
                return {
                    "status": "SUCCEEDED",
                    "tailor_run_id": tailor_run_id,
                    "resume_version_id": str(run.output_resume_version_id),
                }

            run.status = "RUNNING"
            run.failure_stage = None
            run.failure_reason = None
            run.updated_at = datetime.now(UTC)
            db.add(run)
            db.commit()

            resume = db.get(ResumeDocument, run.resume_document_id)
            jd = db.get(JobDescription, run.job_description_id)
            if resume is None or jd is None:
                raise RuntimeError("Run resources are missing")

            latest_version = db.execute(
                select(ResumeVersion)
                .where(ResumeVersion.resume_document_id == run.resume_document_id)
                .order_by(ResumeVersion.version_no.desc())
                .limit(1)
            ).scalar_one_or_none()

            resume_source = _resume_source_text(resume, latest_version)
            prompt = build_tailor_prompt(
                resume_text=resume_source,
                jd_text=jd.raw_text,
                prompt_version=run.prompt_version,
            )
            output = generate_tailored_content(prompt, run.model_name)

            if run.output_resume_version_id is not None:
                # Another worker attempt may have already created output.
                run.status = "SUCCEEDED"
                run.updated_at = datetime.now(UTC)
                db.add(run)
                db.commit()
                return {
                    "status": "SUCCEEDED",
                    "tailor_run_id": tailor_run_id,
                    "resume_version_id": str(run.output_resume_version_id),
                }

            next_version_no = (
                db.execute(
                    select(func.max(ResumeVersion.version_no)).where(ResumeVersion.resume_document_id == run.resume_document_id)
                ).scalar_one_or_none()
                or 0
            ) + 1

            tailored_latex = _to_latex(output.tailored_summary, output.rewritten_bullets)
            new_version = ResumeVersion(
                id=uuid.uuid4(),
                resume_document_id=run.resume_document_id,
                version_no=next_version_no,
                based_on_version_id=latest_version.id if latest_version else None,
                job_description_id=run.job_description_id,
                latex_source=tailored_latex,
                pdf_file_url=None,
                compile_status="PENDING",
                created_by="SYSTEM",
                created_at=datetime.now(UTC),
            )
            db.add(new_version)
            db.flush()

            run.output_resume_version_id = new_version.id
            run.status = "SUCCEEDED"
            run.updated_at = datetime.now(UTC)
            db.add(run)
            db.commit()

            return {
                "status": "SUCCEEDED",
                "tailor_run_id": tailor_run_id,
                "resume_version_id": str(new_version.id),
            }

    except (httpx.HTTPError, GeminiClientError) as exc:
        if self.request.retries < self.max_retries:
            _mark_run_retrying(run_uuid, str(exc))
            countdown = 5 * (2**self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)

        _mark_run_failed(run_uuid, "GEMINI", str(exc))
        return {"status": "FAILED", "tailor_run_id": tailor_run_id, "error": str(exc)}
    except Exception as exc:  # pragma: no cover
        _mark_run_failed(run_uuid, "WORKER", str(exc))
        return {"status": "FAILED", "tailor_run_id": tailor_run_id, "error": str(exc)}


@celery.task(name="compile_pdf")
def compile_pdf(resume_version_id: str) -> dict[str, str]:
    return {"status": "QUEUED", "resume_version_id": resume_version_id}


@celery.task(name="export_drive")
def export_drive(resume_version_id: str, drive_folder_id: str) -> dict[str, str]:
    return {
        "status": "QUEUED",
        "resume_version_id": resume_version_id,
        "drive_folder_id": drive_folder_id,
    }


def _mark_run_retrying(run_id: uuid.UUID, reason: str) -> None:
    with SessionLocal() as db:
        run = db.get(TailorRun, run_id)
        if run is None:
            return
        run.status = "PENDING"
        run.failure_stage = "GEMINI"
        run.failure_reason = reason
        run.updated_at = datetime.now(UTC)
        db.add(run)
        db.commit()


def _mark_run_failed(run_id: uuid.UUID, stage: str, reason: str) -> None:
    with SessionLocal() as db:
        run = db.get(TailorRun, run_id)
        if run is None:
            return
        run.status = "FAILED"
        run.failure_stage = stage
        run.failure_reason = reason
        run.updated_at = datetime.now(UTC)
        db.add(run)
        db.commit()


def _resume_source_text(resume: ResumeDocument, latest_version: ResumeVersion | None) -> str:
    if latest_version is not None:
        return latest_version.latex_source
    if resume.canonical_json is not None:
        return str(resume.canonical_json)
    return resume.source_file_url or "No resume content provided"


def _to_latex(summary: str, bullets: list[str]) -> str:
    lines = ["% AI-tailored version", f"% Summary: {summary}"]
    lines.extend([f"\\\\item {bullet}" for bullet in bullets])
    return "\\n".join(lines)
