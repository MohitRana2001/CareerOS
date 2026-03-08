import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import DriveExport, ResumeDocument, ResumeVersion
from app.workers.tasks import export_drive


class DriveService:
    def __init__(self, db: Session):
        self.db = db

    def create_export(self, user_id: uuid.UUID, resume_version_id: uuid.UUID) -> DriveExport:
        version = self.db.get(ResumeVersion, resume_version_id)
        if version is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found")

        resume = self.db.get(ResumeDocument, version.resume_document_id)
        if resume is None or resume.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found")

        export = DriveExport(
            id=uuid.uuid4(),
            user_id=user_id,
            resume_version_id=resume_version_id,
            drive_file_id=None,
            drive_share_url=None,
            status="PENDING",
            failure_reason=None,
            exported_at=None,
            created_at=datetime.now(UTC),
        )
        self.db.add(export)
        self.db.commit()
        self.db.refresh(export)

        export_drive.delay(str(resume_version_id), str(export.id))
        return export

    def get_export(self, user_id: uuid.UUID, export_id: uuid.UUID) -> DriveExport:
        export = self.db.execute(
            select(DriveExport).where(DriveExport.id == export_id, DriveExport.user_id == user_id)
        ).scalar_one_or_none()
        if export is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drive export not found")
        return export

    @staticmethod
    def build_share_url(file_id: str) -> str:
        return f"{settings.drive_share_base_url}/{file_id}/view"
