from fastapi import APIRouter

router = APIRouter()


@router.post("/google/callback")
def google_callback() -> dict[str, str]:
    return {"message": "TODO: implement OAuth callback"}


@router.get("/me")
def me() -> dict[str, str]:
    return {"message": "TODO: return authenticated user"}
