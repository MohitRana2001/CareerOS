import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import JobDescription, ResumeDocument, TailorRun
from app.schemas import RunStatus, TailorRunAnalyticsResponse, TailorRunCreateRequest
from app.workers.tasks import tailor_resume


class TailorService:
    def __init__(self, db: Session):
        self.db = db

    def create_or_get_run(self, user_id: uuid.UUID, payload: TailorRunCreateRequest) -> TailorRun:
        existing = self.db.execute(
            select(TailorRun).where(
                TailorRun.user_id == user_id,
                TailorRun.idempotency_key == payload.idempotency_key,
            )
        ).scalar_one_or_none()
        if existing is not None:
            return existing

        self._assert_resources_belong_to_user(user_id, payload.resume_document_id, payload.job_description_id)
        now = datetime.now(UTC)

        run = TailorRun(
            id=uuid.uuid4(),
            user_id=user_id,
            resume_document_id=payload.resume_document_id,
            job_description_id=payload.job_description_id,
            output_resume_version_id=None,
            status=RunStatus.PENDING.value,
            idempotency_key=payload.idempotency_key,
            model_name=payload.model_name,
            prompt_version=payload.prompt_version,
            run_attempt_count=0,
            ats_keyword_alignment=None,
            model_trace_metadata=None,
            failure_stage=None,
            failure_reason=None,
            created_at=now,
            updated_at=now,
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        try:
            tailor_resume.delay(str(run.id))
        except Exception as exc:  # pragma: no cover
            run.status = RunStatus.FAILED.value
            run.failure_stage = "QUEUE"
            run.failure_reason = str(exc)
            run.updated_at = datetime.now(UTC)
            self.db.add(run)
            self.db.commit()
            self.db.refresh(run)

        return run

    def get_run(self, user_id: uuid.UUID, run_id: uuid.UUID) -> TailorRun:
        run = self.db.execute(
            select(TailorRun).where(
                TailorRun.id == run_id,
                TailorRun.user_id == user_id,
            )
        ).scalar_one_or_none()
        if run is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tailor run not found")
        return run

    def get_run_analytics(self, user_id: uuid.UUID, run_id: uuid.UUID) -> TailorRunAnalyticsResponse:
        run = self.get_run(user_id, run_id)
        alignment = run.ats_keyword_alignment or {}
        missing_keywords = alignment.get("missing_keywords") or []
        trace = run.model_trace_metadata or {}

        return TailorRunAnalyticsResponse(
            run_id=run.id,
            status=run.status,
            alignment_score=int(alignment.get("alignment_score") or 0),
            missing_keywords_count=len(missing_keywords),
            attempts=int(run.run_attempt_count or 0),
            latency_ms=_extract_latency_ms(trace, run.created_at, run.updated_at),
        )

    def _assert_resources_belong_to_user(
        self,
        user_id: uuid.UUID,
        resume_document_id: uuid.UUID,
        job_description_id: uuid.UUID,
    ) -> None:
        resume = self.db.execute(
            select(ResumeDocument).where(
                ResumeDocument.id == resume_document_id,
                ResumeDocument.user_id == user_id,
            )
        ).scalar_one_or_none()
        if resume is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

        jd = self.db.execute(
            select(JobDescription).where(
                JobDescription.id == job_description_id,
                JobDescription.user_id == user_id,
            )
        ).scalar_one_or_none()
        if jd is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")


def _extract_latency_ms(trace: dict, created_at: datetime, updated_at: datetime) -> int | None:
    started_raw = trace.get("started_at")
    completed_raw = trace.get("completed_at")
    if isinstance(started_raw, str) and isinstance(completed_raw, str):
        started = _parse_iso_datetime(started_raw)
        completed = _parse_iso_datetime(completed_raw)
        if started is not None and completed is not None:
            return max(0, int((completed - started).total_seconds() * 1000))

    if updated_at and created_at:
        return max(0, int((updated_at - created_at).total_seconds() * 1000))
    return None


def _parse_iso_datetime(value: str) -> datetime | None:
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed
