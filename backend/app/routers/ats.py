from fastapi import APIRouter

router = APIRouter()


@router.get("/resumes/{resume_id}/versions/{version_id}/ats")
def get_ats(resume_id: str, version_id: str) -> dict[str, str]:
    return {"message": f"TODO: ATS score for resume {resume_id} version {version_id}"}
