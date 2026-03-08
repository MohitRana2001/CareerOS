import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import ResumeDocument, User
from app.schemas import ResumeCreateRequest, ResumeResponse

router = APIRouter()


@router.post("/upload-url")
def create_upload_url(_: User = Depends(get_current_user)) -> dict[str, str]:
    return {"message": "TODO: signed upload URL"}


@router.post("", response_model=ResumeResponse)
def create_resume(
    payload: ResumeCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeResponse:
    if payload.source_file_type not in {"pdf", "docx"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid file type")

    now = datetime.now(UTC)
    resume = ResumeDocument(
        id=uuid.uuid4(),
        user_id=current_user.id,
        source_file_url=payload.source_file_url,
        source_file_type=payload.source_file_type,
        canonical_json=None,
        created_at=now,
        updated_at=now,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
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
    rows = db.execute(
        select(ResumeDocument)
        .where(ResumeDocument.user_id == current_user.id)
        .order_by(ResumeDocument.created_at.desc())
    ).scalars()

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
    row = db.execute(
        select(ResumeDocument).where(
            ResumeDocument.id == resume_id,
            ResumeDocument.user_id == current_user.id,
        )
    ).scalar_one_or_none()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    return ResumeResponse(
        id=row.id,
        source_file_url=row.source_file_url,
        source_file_type=row.source_file_type,
        canonical_json=row.canonical_json,
        created_at=row.created_at,
    )


@router.patch("/{resume_id}")
def patch_resume(resume_id: str) -> dict[str, str]:
    return {"message": f"TODO: update resume {resume_id}"}


@router.post("/{resume_id}/versions/{version_id}/compile")
def compile_resume(resume_id: str, version_id: str) -> dict[str, str]:
    return {"message": f"TODO: compile resume {resume_id} version {version_id}"}
