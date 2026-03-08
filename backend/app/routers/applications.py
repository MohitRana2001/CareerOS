import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import Application, ApplicationNote, User
from app.schemas import (
    ApplicationCreateRequest,
    ApplicationNoteRequest,
    ApplicationResponse,
    ApplicationUpdateRequest,
)

router = APIRouter()

VALID_APPLICATION_STATUSES = {
    "NOT_APPLIED",
    "APPLIED",
    "SCREENING",
    "INTERVIEW",
    "OFFER",
    "REJECTED",
}


@router.post("", response_model=ApplicationResponse)
def create_application(
    payload: ApplicationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationResponse:
    if payload.status not in VALID_APPLICATION_STATUSES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid status")

    now = datetime.now(UTC)
    application = Application(
        id=uuid.uuid4(),
        user_id=current_user.id,
        company_name=payload.company_name,
        position_title=payload.position_title,
        applied_date=payload.applied_date,
        status=payload.status,
        created_at=now,
        updated_at=now,
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return ApplicationResponse(
        id=application.id,
        company_name=application.company_name,
        position_title=application.position_title,
        applied_date=application.applied_date,
        status=application.status,
        created_at=application.created_at,
    )


@router.get("", response_model=list[ApplicationResponse])
def list_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ApplicationResponse]:
    rows = db.execute(
        select(Application).where(Application.user_id == current_user.id).order_by(Application.created_at.desc())
    ).scalars()

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
    row = db.execute(
        select(Application).where(Application.id == application_id, Application.user_id == current_user.id)
    ).scalar_one_or_none()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    if payload.status is not None and payload.status not in VALID_APPLICATION_STATUSES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid status")

    if payload.company_name is not None:
        row.company_name = payload.company_name
    if payload.position_title is not None:
        row.position_title = payload.position_title
    if payload.applied_date is not None:
        row.applied_date = payload.applied_date
    if payload.status is not None:
        row.status = payload.status
    row.updated_at = datetime.now(UTC)

    db.add(row)
    db.commit()
    db.refresh(row)

    return ApplicationResponse(
        id=row.id,
        company_name=row.company_name,
        position_title=row.position_title,
        applied_date=row.applied_date,
        status=row.status,
        created_at=row.created_at,
    )


@router.post("/{application_id}/notes")
def add_application_note(
    application_id: uuid.UUID,
    payload: ApplicationNoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    row = db.execute(
        select(Application).where(Application.id == application_id, Application.user_id == current_user.id)
    ).scalar_one_or_none()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    note = ApplicationNote(
        id=uuid.uuid4(),
        application_id=application_id,
        note=payload.note,
        created_at=datetime.now(UTC),
    )
    db.add(note)
    db.commit()

    return {"message": "Note added"}
