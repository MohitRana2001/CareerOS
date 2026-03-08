import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import DriveExportCreateRequest, DriveExportResponse
from app.services.drive_service import DriveService

router = APIRouter()


@router.post("/exports", response_model=DriveExportResponse)
def export_to_drive(
    payload: DriveExportCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DriveExportResponse:
    row = DriveService(db).create_export(current_user.id, payload.resume_version_id)
    return DriveExportResponse(
        id=row.id,
        resume_version_id=row.resume_version_id,
        status=row.status,
        failure_reason=row.failure_reason,
        drive_file_id=row.drive_file_id,
        drive_share_url=row.drive_share_url,
        exported_at=row.exported_at,
        created_at=row.created_at,
    )


@router.get("/exports/{export_id}", response_model=DriveExportResponse)
def get_export(
    export_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DriveExportResponse:
    row = DriveService(db).get_export(current_user.id, export_id)
    return DriveExportResponse(
        id=row.id,
        resume_version_id=row.resume_version_id,
        status=row.status,
        failure_reason=row.failure_reason,
        drive_file_id=row.drive_file_id,
        drive_share_url=row.drive_share_url,
        exported_at=row.exported_at,
        created_at=row.created_at,
    )
