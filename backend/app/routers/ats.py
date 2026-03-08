import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import AtsScoreResponse
from app.services.resume_service import ResumeService

router = APIRouter()


@router.get("/resumes/{resume_id}/versions/{version_id}/ats", response_model=AtsScoreResponse)
def get_ats(
    resume_id: uuid.UUID,
    version_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AtsScoreResponse:
    result = ResumeService(db).get_ats(current_user.id, resume_id, version_id)
    return AtsScoreResponse(score=result["score"], breakdown=result["breakdown"])
