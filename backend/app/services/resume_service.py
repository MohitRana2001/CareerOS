import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models import JobDescription, ResumeDocument, ResumeVersion
from app.schemas import ResumeCreateRequest, ResumeVersionCreateRequest


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
        statement: Select[tuple[ResumeDocument]] = (
            select(ResumeDocument).where(ResumeDocument.user_id == user_id).order_by(ResumeDocument.created_at.desc())
        )
        return list(self.db.execute(statement).scalars())

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

    def create_version(
        self,
        user_id: uuid.UUID,
        resume_id: uuid.UUID,
        payload: ResumeVersionCreateRequest,
    ) -> ResumeVersion:
        resume = self.get_resume(user_id, resume_id)

        if payload.based_on_version_id is not None:
            base_version = self.get_version(user_id, resume_id, payload.based_on_version_id)
            if base_version.resume_document_id != resume.id:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid base version")

        if payload.job_description_id is not None:
            jd_exists = self.db.execute(
                select(JobDescription).where(
                    JobDescription.id == payload.job_description_id,
                    JobDescription.user_id == user_id,
                )
            ).scalar_one_or_none()
            if jd_exists is None:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid job description")

        current_max = self.db.execute(
            select(func.max(ResumeVersion.version_no)).where(ResumeVersion.resume_document_id == resume.id)
        ).scalar_one_or_none()
        next_version = (current_max or 0) + 1

        version = ResumeVersion(
            id=uuid.uuid4(),
            resume_document_id=resume.id,
            version_no=next_version,
            based_on_version_id=payload.based_on_version_id,
            job_description_id=payload.job_description_id,
            latex_source=payload.latex_source,
            pdf_file_url=None,
            compile_status="PENDING",
            created_by=payload.created_by.value,
            created_at=datetime.now(UTC),
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    def list_versions(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> list[ResumeVersion]:
        self.get_resume(user_id, resume_id)
        statement: Select[tuple[ResumeVersion]] = (
            select(ResumeVersion).where(ResumeVersion.resume_document_id == resume_id).order_by(ResumeVersion.version_no.desc())
        )
        return list(self.db.execute(statement).scalars())

    def get_version(self, user_id: uuid.UUID, resume_id: uuid.UUID, version_id: uuid.UUID) -> ResumeVersion:
        self.get_resume(user_id, resume_id)
        row = self.db.execute(
            select(ResumeVersion).where(
                ResumeVersion.id == version_id,
                ResumeVersion.resume_document_id == resume_id,
            )
        ).scalar_one_or_none()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found")
        return row
