import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import (
    ApplicationCreateRequest,
    ApplicationNoteRequest,
    ApplicationResponse,
    ApplicationUpdateRequest,
    MessageResponse,
)
from app.services.application_service import ApplicationService

router = APIRouter()


@router.post("", response_model=ApplicationResponse)
def create_application(
    payload: ApplicationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationResponse:
    app = ApplicationService(db).create_application(current_user.id, payload)
    return ApplicationResponse(
        id=app.id,
        company_name=app.company_name,
        position_title=app.position_title,
        applied_date=app.applied_date,
        status=app.status,
        created_at=app.created_at,
    )


@router.get("", response_model=list[ApplicationResponse])
def list_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ApplicationResponse]:
    rows = ApplicationService(db).list_applications(current_user.id)
    return [
        ApplicationResponse(
            id=row.id,
            company_name=row.company_name,
            position_title=row.position_title,
            applied_date=row.applied_date,
            status=row.status,
            created_at=row.created_at,
        )
        for row in rows
    ]


@router.patch("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: uuid.UUID,
    payload: ApplicationUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationResponse:
    row = ApplicationService(db).update_application(current_user.id, application_id, payload)
    return ApplicationResponse(
        id=row.id,
        company_name=row.company_name,
        position_title=row.position_title,
        applied_date=row.applied_date,
        status=row.status,
        created_at=row.created_at,
    )


@router.post("/{application_id}/notes", response_model=MessageResponse)
def add_application_note(
    application_id: uuid.UUID,
    payload: ApplicationNoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    ApplicationService(db).add_note(current_user.id, application_id, payload.note)
    return MessageResponse(message="Note added")
