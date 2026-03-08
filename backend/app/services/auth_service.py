import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import User


@dataclass
class GoogleIdentity:
    sub: str
    email: str
    full_name: str | None


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def upsert_google_user(self, identity: GoogleIdentity) -> User:
        user = self.db.execute(select(User).where(User.google_sub == identity.sub)).scalar_one_or_none()
        now = datetime.now(UTC)

        if user is None:
            user = User(
                id=uuid.uuid4(),
                google_sub=identity.sub,
                email=identity.email,
                full_name=identity.full_name,
                created_at=now,
                updated_at=now,
            )
            self.db.add(user)
        else:
            user.email = identity.email
            user.full_name = identity.full_name
            user.updated_at = now

        self.db.commit()
        self.db.refresh(user)
        return user


def verify_google_id_token(id_token: str) -> GoogleIdentity:
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_CLIENT_ID is not configured",
        )

    try:
        response = httpx.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
            timeout=10.0,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Google verification failed") from exc

    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")

    payload = response.json()
    if payload.get("aud") != settings.google_client_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token audience")
    if payload.get("email_verified") not in ("true", True):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google email is not verified")

    sub = payload.get("sub")
    email = payload.get("email")
    if not sub or not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google identity payload")

    return GoogleIdentity(sub=sub, email=email, full_name=payload.get("name"))
