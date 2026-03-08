import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class OkResponse(BaseModel):
    status: str = "ok"


class IdResponse(BaseModel):
    id: str


class GoogleCallbackRequest(BaseModel):
    google_sub: str = Field(min_length=3)
    email: str
    full_name: str | None = None


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: uuid.UUID
    google_sub: str
    email: str
    full_name: str | None = None


class ResumeCreateRequest(BaseModel):
    source_file_url: str | None = None
    source_file_type: str


class ResumeResponse(BaseModel):
    id: uuid.UUID
    source_file_url: str | None
    source_file_type: str
    canonical_json: dict | None
    created_at: datetime


class ApplicationCreateRequest(BaseModel):
    company_name: str
    position_title: str
    applied_date: date | None = None
    status: str = "NOT_APPLIED"


class ApplicationUpdateRequest(BaseModel):
    company_name: str | None = None
    position_title: str | None = None
    applied_date: date | None = None
    status: str | None = None


class ApplicationResponse(BaseModel):
    id: uuid.UUID
    company_name: str
    position_title: str
    applied_date: date | None
    status: str
    created_at: datetime


class ApplicationNoteRequest(BaseModel):
    note: str
