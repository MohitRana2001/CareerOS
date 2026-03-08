import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import (
    ExportStatus,
    JobStatusResponse,
    ResumeCreateRequest,
    ResumePatchRequest,
    ResumeResponse,
    ResumeVersionCreateRequest,
    ResumeVersionResponse,
    UploadUrlResponse,
)
from app.services.resume_service import ResumeService

router = APIRouter()


@router.post("/upload-url", response_model=UploadUrlResponse)
def create_upload_url(_: User = Depends(get_current_user)) -> UploadUrlResponse:
    upload_id = uuid.uuid4().hex
    return UploadUrlResponse(
        upload_url=f"https://upload.example.com/put/{upload_id}",
        file_url=f"https://storage.example.com/careeros/uploads/{upload_id}.pdf",
        expires_in_seconds=900,
    )


@router.post("", response_model=ResumeResponse)
def create_resume(
    payload: ResumeCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeResponse:
    resume = ResumeService(db).create_resume(current_user.id, payload)
    return ResumeResponse(
        id=resume.id,
        source_file_url=resume.source_file_url,
        source_file_type=resume.source_file_type,
        canonical_json=resume.canonical_json,
        created_at=resume.created_at,
    )


@router.get("", response_model=list[ResumeResponse])
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ResumeResponse]:
    rows = ResumeService(db).list_resumes(current_user.id)
    return [
        ResumeResponse(
            id=row.id,
            source_file_url=row.source_file_url,
            source_file_type=row.source_file_type,
            canonical_json=row.canonical_json,
            created_at=row.created_at,
        )
        for row in rows
    ]


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeResponse:
    row = ResumeService(db).get_resume(current_user.id, resume_id)
    return ResumeResponse(
        id=row.id,
        source_file_url=row.source_file_url,
        source_file_type=row.source_file_type,
        canonical_json=row.canonical_json,
        created_at=row.created_at,
    )


@router.post("/{resume_id}/versions", response_model=ResumeVersionResponse)
def create_resume_version(
    resume_id: uuid.UUID,
    payload: ResumeVersionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeVersionResponse:
    version = ResumeService(db).create_version(current_user.id, resume_id, payload)
    return ResumeVersionResponse(
        id=version.id,
        resume_document_id=version.resume_document_id,
        version_no=version.version_no,
        based_on_version_id=version.based_on_version_id,
        job_description_id=version.job_description_id,
        latex_source=version.latex_source,
        compile_status=version.compile_status,
        created_by=version.created_by,
        created_at=version.created_at,
    )


@router.get("/{resume_id}/versions", response_model=list[ResumeVersionResponse])
def list_resume_versions(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ResumeVersionResponse]:
    rows = ResumeService(db).list_versions(current_user.id, resume_id)
    return [
        ResumeVersionResponse(
            id=row.id,
            resume_document_id=row.resume_document_id,
            version_no=row.version_no,
            based_on_version_id=row.based_on_version_id,
            job_description_id=row.job_description_id,
            latex_source=row.latex_source,
            compile_status=row.compile_status,
            created_by=row.created_by,
            created_at=row.created_at,
        )
        for row in rows
    ]


@router.get("/{resume_id}/versions/{version_id}", response_model=ResumeVersionResponse)
def get_resume_version(
    resume_id: uuid.UUID,
    version_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeVersionResponse:
    row = ResumeService(db).get_version(current_user.id, resume_id, version_id)
    return ResumeVersionResponse(
        id=row.id,
        resume_document_id=row.resume_document_id,
        version_no=row.version_no,
        based_on_version_id=row.based_on_version_id,
        job_description_id=row.job_description_id,
        latex_source=row.latex_source,
        compile_status=row.compile_status,
        created_by=row.created_by,
        created_at=row.created_at,
    )


@router.patch("/{resume_id}", response_model=ResumeResponse)
def patch_resume(
    resume_id: uuid.UUID,
    payload: ResumePatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeResponse:
    resume = ResumeService(db).patch_resume(current_user.id, resume_id, payload)
    return ResumeResponse(
        id=resume.id,
        source_file_url=resume.source_file_url,
        source_file_type=resume.source_file_type,
        canonical_json=resume.canonical_json,
        created_at=resume.created_at,
    )


@router.post("/{resume_id}/versions/{version_id}/compile", response_model=JobStatusResponse)
def compile_resume(
    resume_id: uuid.UUID,
    version_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobStatusResponse:
    version = ResumeService(db).queue_compile(current_user.id, resume_id, version_id)
    now = datetime.now(UTC)
    return JobStatusResponse(
        id=version.id,
        status=ExportStatus.RUNNING,
        failure_reason=None,
        created_at=version.created_at,
        updated_at=now,
    )
