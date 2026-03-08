"""Celery tasks for async job orchestration."""

import uuid
from datetime import UTC, datetime

from celery import Celery

from app.config import settings
from app.db import SessionLocal
from app.models import TailorRun

celery = Celery("resume_tailor", broker=settings.redis_url, backend=settings.redis_url)


@celery.task(name="extract_resume")
def extract_resume(resume_document_id: str) -> dict[str, str]:
    return {"status": "QUEUED", "resume_document_id": resume_document_id}


@celery.task(name="tailor_resume")
def tailor_resume(tailor_run_id: str) -> dict[str, str]:
    run_uuid = uuid.UUID(tailor_run_id)
    with SessionLocal() as db:
        run = db.get(TailorRun, run_uuid)
        if run is None:
            return {"status": "NOT_FOUND", "tailor_run_id": tailor_run_id}

        run.status = "RUNNING"
        run.updated_at = datetime.now(UTC)
        db.add(run)
        db.commit()

        # Week 2 placeholder behavior: mark orchestration path successful.
        run.status = "SUCCEEDED"
        run.updated_at = datetime.now(UTC)
        db.add(run)
        db.commit()

    return {"status": "SUCCEEDED", "tailor_run_id": tailor_run_id}


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
