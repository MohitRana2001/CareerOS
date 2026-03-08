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


class ExportStatus(StrEnum):
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
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "based_on_version_id": "f40fd2b1-6dfe-4f3e-a0f8-9dba238f67e8",
                    "job_description_id": "8f4f8643-6cc7-49e6-8c43-06f3322b7d2d",
                    "latex_source": "\\\\item Built FastAPI services with PostgreSQL and Redis for scalable APIs",
                    "created_by": "SYSTEM",
                }
            ]
        },
    )

    based_on_version_id: uuid.UUID | None = None
    job_description_id: uuid.UUID | None = None
    latex_source: str = Field(min_length=1)
    created_by: ResumeCreatedBy = ResumeCreatedBy.USER


class ResumeVersionResponse(StrictModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "id": "4f3390ac-dad0-4444-a4a5-49b03d8e86c5",
                    "resume_document_id": "c67a4eb8-6481-4685-a364-76cdaf6b552f",
                    "version_no": 3,
                    "based_on_version_id": "f40fd2b1-6dfe-4f3e-a0f8-9dba238f67e8",
                    "job_description_id": "8f4f8643-6cc7-49e6-8c43-06f3322b7d2d",
                    "latex_source": "\\\\item Designed distributed systems...",
                    "compile_status": "PENDING",
                    "created_by": "SYSTEM",
                    "created_at": "2026-03-09T10:30:00Z",
                }
            ]
        },
    )

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
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "company_name": "Acme Inc",
                    "position_title": "Backend Engineer",
                    "source_url": "https://jobs.acme.com/backend-engineer",
                    "raw_text": "We are looking for strong Python, FastAPI, PostgreSQL, Redis, Docker, and AWS skills.",
                }
            ]
        },
    )

    company_name: str | None = Field(default=None, max_length=256)
    position_title: str | None = Field(default=None, max_length=256)
    source_url: str | None = Field(default=None, max_length=2048)
    raw_text: str = Field(min_length=30)


class JobDescriptionResponse(StrictModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "id": "8f4f8643-6cc7-49e6-8c43-06f3322b7d2d",
                    "company_name": "Acme Inc",
                    "position_title": "Backend Engineer",
                    "source_url": "https://jobs.acme.com/backend-engineer",
                    "raw_text": "We are looking for strong Python...",
                    "extracted_requirements": {"keywords": ["python", "fastapi", "postgresql", "redis", "docker", "aws"]},
                    "created_at": "2026-03-09T10:20:00Z",
                }
            ]
        },
    )

    id: uuid.UUID
    company_name: str | None
    position_title: str | None
    source_url: str | None
    raw_text: str
    extracted_requirements: dict | None
    created_at: datetime


class TailorRunCreateRequest(StrictModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "resume_document_id": "c67a4eb8-6481-4685-a364-76cdaf6b552f",
                    "job_description_id": "8f4f8643-6cc7-49e6-8c43-06f3322b7d2d",
                    "idempotency_key": "acme-backend-20260309",
                    "model_name": "gemini-2.5-pro",
                    "prompt_version": "v1",
                }
            ]
        },
    )

    resume_document_id: uuid.UUID
    job_description_id: uuid.UUID
    idempotency_key: str = Field(min_length=6, max_length=128)
    model_name: str | None = Field(default="gemini-2.5-pro")
    prompt_version: str | None = Field(default="v1")


class TailorRunResponse(StrictModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "id": "a662fced-56b5-4888-8f8f-1f4f4839f9a2",
                    "resume_document_id": "c67a4eb8-6481-4685-a364-76cdaf6b552f",
                    "job_description_id": "8f4f8643-6cc7-49e6-8c43-06f3322b7d2d",
                    "status": "RUNNING",
                    "idempotency_key": "acme-backend-20260309",
                    "model_name": "gemini-2.5-pro",
                    "prompt_version": "v1",
                    "run_attempt_count": 1,
                    "ats_keyword_alignment": {
                        "required_keywords": ["python", "fastapi", "postgresql", "redis", "docker", "aws"],
                        "matched_keywords": ["python", "fastapi", "postgresql", "redis", "docker"],
                        "missing_keywords": ["aws"],
                        "alignment_score": 83,
                    },
                    "model_trace_metadata": {
                        "provider": "gemini",
                        "model": "gemini-2.5-pro",
                        "prompt_version": "v1",
                        "prompt_chars": 2140,
                        "keywords_generated": 5,
                    },
                    "failure_stage": None,
                    "failure_reason": None,
                    "created_at": "2026-03-09T10:31:00Z",
                    "updated_at": "2026-03-09T10:31:10Z",
                }
            ]
        },
    )

    id: uuid.UUID
    resume_document_id: uuid.UUID
    job_description_id: uuid.UUID
    status: RunStatus
    idempotency_key: str
    model_name: str | None
    prompt_version: str | None
    run_attempt_count: int
    ats_keyword_alignment: dict | None
    model_trace_metadata: dict | None
    failure_stage: str | None
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime


class TailorRunAnalyticsResponse(StrictModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "run_id": "a662fced-56b5-4888-8f8f-1f4f4839f9a2",
                    "status": "SUCCEEDED",
                    "alignment_score": 83,
                    "missing_keywords_count": 1,
                    "attempts": 1,
                    "latency_ms": 2150,
                }
            ]
        },
    )

    run_id: uuid.UUID
    status: RunStatus
    alignment_score: int
    missing_keywords_count: int
    attempts: int
    latency_ms: int | None


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


class UploadUrlResponse(StrictModel):
    upload_url: str
    file_url: str
    expires_in_seconds: int


class ResumePatchRequest(StrictModel):
    source_file_url: str | None = Field(default=None, max_length=2048)
    canonical_json: dict | None = None


class JobStatusResponse(StrictModel):
    id: uuid.UUID
    status: ExportStatus
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime


class AtsScoreResponse(StrictModel):
    score: int
    breakdown: dict


class SkillsGapResponse(StrictModel):
    critical_missing: list[str]
    nice_to_have_missing: list[str]


class DriveExportCreateRequest(StrictModel):
    resume_version_id: uuid.UUID


class DriveExportResponse(StrictModel):
    id: uuid.UUID
    resume_version_id: uuid.UUID
    status: ExportStatus
    failure_reason: str | None
    drive_file_id: str | None
    drive_share_url: str | None
    exported_at: datetime | None
    created_at: datetime
