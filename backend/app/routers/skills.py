from fastapi import APIRouter

router = APIRouter()


@router.get("/resumes/{resume_id}/versions/{version_id}/skills-gap")
def skills_gap(resume_id: str, version_id: str) -> dict[str, str]:
    return {"message": f"TODO: skills gap for resume {resume_id} version {version_id}"}
