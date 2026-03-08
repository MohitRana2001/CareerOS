from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import AuthTokenResponse, GoogleCallbackRequest, UserResponse
from app.security import create_access_token
from app.services.auth_service import AuthService, verify_google_id_token

router = APIRouter()


@router.post("/google/callback", response_model=AuthTokenResponse)
def google_callback(payload: GoogleCallbackRequest, db: Session = Depends(get_db)) -> AuthTokenResponse:
    identity = verify_google_id_token(payload.id_token)
    user = AuthService(db).upsert_google_user(identity)
    token = create_access_token(str(user.id))
    return AuthTokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        google_sub=current_user.google_sub,
        email=current_user.email,
        full_name=current_user.full_name,
    )
