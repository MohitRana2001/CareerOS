import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import SkillsGapResponse
from app.services.resume_service import ResumeService

router = APIRouter()


@router.get("/resumes/{resume_id}/versions/{version_id}/skills-gap", response_model=SkillsGapResponse)
def skills_gap(
    resume_id: uuid.UUID,
    version_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SkillsGapResponse:
    result = ResumeService(db).get_skills_gap(current_user.id, resume_id, version_id)
    return SkillsGapResponse(
        critical_missing=result["critical_missing"],
        nice_to_have_missing=result["nice_to_have_missing"],
    )
