import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import MessageResponse, ResumeCreateRequest, ResumeResponse
from app.services.resume_service import ResumeService

router = APIRouter()


@router.post("/upload-url", response_model=MessageResponse)
def create_upload_url(_: User = Depends(get_current_user)) -> MessageResponse:
    return MessageResponse(message="TODO: signed upload URL")


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


@router.patch("/{resume_id}", response_model=MessageResponse)
def patch_resume(resume_id: str) -> MessageResponse:
    return MessageResponse(message=f"TODO: update resume {resume_id}")


@router.post("/{resume_id}/versions/{version_id}/compile", response_model=MessageResponse)
def compile_resume(resume_id: str, version_id: str) -> MessageResponse:
    return MessageResponse(message=f"TODO: compile resume {resume_id} version {version_id}")
