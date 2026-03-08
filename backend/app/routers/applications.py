from fastapi import APIRouter

router = APIRouter()


@router.post("")
def create_application() -> dict[str, str]:
    return {"message": "TODO: create application"}


@router.get("")
def list_applications() -> dict[str, str]:
    return {"message": "TODO: list applications"}


@router.patch("/{application_id}")
def update_application(application_id: str) -> dict[str, str]:
    return {"message": f"TODO: update application {application_id}"}


@router.post("/{application_id}/notes")
def add_application_note(application_id: str) -> dict[str, str]:
    return {"message": f"TODO: add note for {application_id}"}
