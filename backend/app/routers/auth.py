import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import AuthTokenResponse, GoogleCallbackRequest, UserResponse
from app.security import create_access_token

router = APIRouter()


@router.post("/google/callback", response_model=AuthTokenResponse)
def google_callback(payload: GoogleCallbackRequest, db: Session = Depends(get_db)) -> AuthTokenResponse:
    user = db.execute(select(User).where(User.google_sub == payload.google_sub)).scalar_one_or_none()
    now = datetime.now(UTC)

    if user is None:
        user = User(
            id=uuid.uuid4(),
            google_sub=payload.google_sub,
            email=payload.email,
            full_name=payload.full_name,
            created_at=now,
            updated_at=now,
        )
        db.add(user)
    else:
        user.email = payload.email
        user.full_name = payload.full_name
        user.updated_at = now

    db.commit()
    db.refresh(user)

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
