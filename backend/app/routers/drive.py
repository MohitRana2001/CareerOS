from fastapi import APIRouter

router = APIRouter()


@router.post("/exports")
def export_to_drive() -> dict[str, str]:
    return {"message": "TODO: queue Drive export"}


@router.get("/exports/{export_id}")
def get_export(export_id: str) -> dict[str, str]:
    return {"message": f"TODO: get export {export_id}"}
