"""Celery task stubs for Phase 1 async flows."""

from celery import Celery

from app.config import settings

celery = Celery("resume_tailor", broker=settings.redis_url, backend=settings.redis_url)


@celery.task(name="extract_resume")
def extract_resume(resume_document_id: str) -> dict[str, str]:
    return {"status": "TODO", "resume_document_id": resume_document_id}


@celery.task(name="tailor_resume")
def tailor_resume(tailor_run_id: str) -> dict[str, str]:
    return {"status": "TODO", "tailor_run_id": tailor_run_id}


@celery.task(name="compile_pdf")
def compile_pdf(resume_version_id: str) -> dict[str, str]:
    return {"status": "TODO", "resume_version_id": resume_version_id}


@celery.task(name="export_drive")
def export_drive(resume_version_id: str, drive_folder_id: str) -> dict[str, str]:
    return {
        "status": "TODO",
        "resume_version_id": resume_version_id,
        "drive_folder_id": drive_folder_id,
    }
