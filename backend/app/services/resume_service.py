import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ResumeDocument
from app.schemas import ResumeCreateRequest


class ResumeService:
    def __init__(self, db: Session):
        self.db = db

    def create_resume(self, user_id: uuid.UUID, payload: ResumeCreateRequest) -> ResumeDocument:
        now = datetime.now(UTC)
        resume = ResumeDocument(
            id=uuid.uuid4(),
            user_id=user_id,
            source_file_url=payload.source_file_url,
            source_file_type=payload.source_file_type.value,
            canonical_json=None,
            created_at=now,
            updated_at=now,
        )
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def list_resumes(self, user_id: uuid.UUID) -> list[ResumeDocument]:
        return list(
            self.db.execute(
                select(ResumeDocument).where(ResumeDocument.user_id == user_id).order_by(ResumeDocument.created_at.desc())
            ).scalars()
        )

    def get_resume(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> ResumeDocument:
        row = self.db.execute(
            select(ResumeDocument).where(
                ResumeDocument.id == resume_id,
                ResumeDocument.user_id == user_id,
            )
        ).scalar_one_or_none()

        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
        return row
