from fastapi import APIRouter

router = APIRouter()


@router.post("/upload-url")
def create_upload_url() -> dict[str, str]:
    return {"message": "TODO: signed upload URL"}


@router.post("")
def create_resume() -> dict[str, str]:
    return {"message": "TODO: create resume from uploaded file"}


@router.get("")
def list_resumes() -> dict[str, str]:
    return {"message": "TODO: list resumes with filters"}


@router.get("/{resume_id}")
def get_resume(resume_id: str) -> dict[str, str]:
    return {"message": f"TODO: get resume {resume_id}"}


@router.patch("/{resume_id}")
def patch_resume(resume_id: str) -> dict[str, str]:
    return {"message": f"TODO: update resume {resume_id}"}


@router.post("/{resume_id}/versions/{version_id}/compile")
def compile_resume(resume_id: str, version_id: str) -> dict[str, str]:
    return {"message": f"TODO: compile resume {resume_id} version {version_id}"}
