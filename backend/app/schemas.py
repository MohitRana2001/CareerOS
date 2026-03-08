import uuid
from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class SourceFileType(StrEnum):
    PDF = "pdf"
    DOCX = "docx"


class ApplicationStatus(StrEnum):
    NOT_APPLIED = "NOT_APPLIED"
    APPLIED = "APPLIED"
    SCREENING = "SCREENING"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"


class ResumeCreatedBy(StrEnum):
    SYSTEM = "SYSTEM"
    USER = "USER"


class RunStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class OkResponse(StrictModel):
    status: str = "ok"


class IdResponse(StrictModel):
    id: str


class GoogleCallbackRequest(StrictModel):
    id_token: str = Field(min_length=20)


class AuthTokenResponse(StrictModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(StrictModel):
    id: uuid.UUID
    google_sub: str
    email: str
    full_name: str | None = None


class ResumeCreateRequest(StrictModel):
    source_file_url: str | None = Field(default=None, max_length=2048)
    source_file_type: SourceFileType


class ResumeResponse(StrictModel):
    id: uuid.UUID
    source_file_url: str | None
    source_file_type: SourceFileType
    canonical_json: dict | None
    created_at: datetime


class ResumeVersionCreateRequest(StrictModel):
    based_on_version_id: uuid.UUID | None = None
    job_description_id: uuid.UUID | None = None
    latex_source: str = Field(min_length=1)
    created_by: ResumeCreatedBy = ResumeCreatedBy.USER


class ResumeVersionResponse(StrictModel):
    id: uuid.UUID
    resume_document_id: uuid.UUID
    version_no: int
    based_on_version_id: uuid.UUID | None
    job_description_id: uuid.UUID | None
    latex_source: str
    compile_status: RunStatus
    created_by: ResumeCreatedBy
    created_at: datetime


class JobDescriptionCreateRequest(StrictModel):
    company_name: str | None = Field(default=None, max_length=256)
    position_title: str | None = Field(default=None, max_length=256)
    source_url: str | None = Field(default=None, max_length=2048)
    raw_text: str = Field(min_length=30)


class JobDescriptionResponse(StrictModel):
    id: uuid.UUID
    company_name: str | None
    position_title: str | None
    source_url: str | None
    raw_text: str
    extracted_requirements: dict | None
    created_at: datetime


class TailorRunCreateRequest(StrictModel):
    resume_document_id: uuid.UUID
    job_description_id: uuid.UUID
    idempotency_key: str = Field(min_length=6, max_length=128)
    model_name: str | None = Field(default="gemini-2.5-pro")
    prompt_version: str | None = Field(default="v1")


class TailorRunResponse(StrictModel):
    id: uuid.UUID
    resume_document_id: uuid.UUID
    job_description_id: uuid.UUID
    status: RunStatus
    idempotency_key: str
    model_name: str | None
    prompt_version: str | None
    failure_stage: str | None
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime


class ApplicationCreateRequest(StrictModel):
    company_name: str = Field(min_length=1, max_length=256)
    position_title: str = Field(min_length=1, max_length=256)
    applied_date: date | None = None
    status: ApplicationStatus = ApplicationStatus.NOT_APPLIED


class ApplicationUpdateRequest(StrictModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=256)
    position_title: str | None = Field(default=None, min_length=1, max_length=256)
    applied_date: date | None = None
    status: ApplicationStatus | None = None


class ApplicationResponse(StrictModel):
    id: uuid.UUID
    company_name: str
    position_title: str
    applied_date: date | None
    status: ApplicationStatus
    created_at: datetime


class ApplicationNoteRequest(StrictModel):
    note: str = Field(min_length=1, max_length=3000)


class MessageResponse(StrictModel):
    message: str
