import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Application, ApplicationNote
from app.schemas import ApplicationCreateRequest, ApplicationUpdateRequest


class ApplicationService:
    def __init__(self, db: Session):
        self.db = db

    def create_application(self, user_id: uuid.UUID, payload: ApplicationCreateRequest) -> Application:
        now = datetime.now(UTC)
        app = Application(
            id=uuid.uuid4(),
            user_id=user_id,
            company_name=payload.company_name,
            position_title=payload.position_title,
            applied_date=payload.applied_date,
            status=payload.status.value,
            created_at=now,
            updated_at=now,
        )
        self.db.add(app)
        self.db.commit()
        self.db.refresh(app)
        return app

    def list_applications(self, user_id: uuid.UUID) -> list[Application]:
        return list(
            self.db.execute(
                select(Application).where(Application.user_id == user_id).order_by(Application.created_at.desc())
            ).scalars()
        )

    def update_application(
        self,
        user_id: uuid.UUID,
        application_id: uuid.UUID,
        payload: ApplicationUpdateRequest,
    ) -> Application:
        row = self.db.execute(
            select(Application).where(Application.id == application_id, Application.user_id == user_id)
        ).scalar_one_or_none()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

        if payload.company_name is not None:
            row.company_name = payload.company_name
        if payload.position_title is not None:
            row.position_title = payload.position_title
        if payload.applied_date is not None:
            row.applied_date = payload.applied_date
        if payload.status is not None:
            row.status = payload.status.value
        row.updated_at = datetime.now(UTC)

        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def add_note(self, user_id: uuid.UUID, application_id: uuid.UUID, note_text: str) -> None:
        application = self.db.execute(
            select(Application).where(Application.id == application_id, Application.user_id == user_id)
        ).scalar_one_or_none()
        if application is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

        note = ApplicationNote(
            id=uuid.uuid4(),
            application_id=application_id,
            note=note_text,
            created_at=datetime.now(UTC),
        )
        self.db.add(note)
        self.db.commit()
