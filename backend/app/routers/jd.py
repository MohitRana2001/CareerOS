import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import (
    JobDescriptionCreateRequest,
    JobDescriptionResponse,
    TailorRunCreateRequest,
    TailorRunResponse,
)
from app.services.jd_service import JobDescriptionService
from app.services.tailor_service import TailorService

router = APIRouter()


@router.post("/job-descriptions", response_model=JobDescriptionResponse)
def create_jd(
    payload: JobDescriptionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobDescriptionResponse:
    jd = JobDescriptionService(db).create_job_description(current_user.id, payload)
    return JobDescriptionResponse(
        id=jd.id,
        company_name=jd.company_name,
        position_title=jd.position_title,
        source_url=jd.source_url,
        raw_text=jd.raw_text,
        extracted_requirements=jd.extracted_requirements,
        created_at=jd.created_at,
    )


@router.get("/job-descriptions/{job_description_id}", response_model=JobDescriptionResponse)
def get_jd(
    job_description_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobDescriptionResponse:
    jd = JobDescriptionService(db).get_job_description(current_user.id, job_description_id)
    return JobDescriptionResponse(
        id=jd.id,
        company_name=jd.company_name,
        position_title=jd.position_title,
        source_url=jd.source_url,
        raw_text=jd.raw_text,
        extracted_requirements=jd.extracted_requirements,
        created_at=jd.created_at,
    )


@router.post("/tailor-runs", response_model=TailorRunResponse)
def create_tailor_run(
    payload: TailorRunCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TailorRunResponse:
    run = TailorService(db).create_or_get_run(current_user.id, payload)
    return TailorRunResponse(
        id=run.id,
        resume_document_id=run.resume_document_id,
        job_description_id=run.job_description_id,
        status=run.status,
        idempotency_key=run.idempotency_key,
        model_name=run.model_name,
        prompt_version=run.prompt_version,
        run_attempt_count=run.run_attempt_count,
        ats_keyword_alignment=run.ats_keyword_alignment,
        model_trace_metadata=run.model_trace_metadata,
        failure_stage=run.failure_stage,
        failure_reason=run.failure_reason,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )


@router.get("/tailor-runs/{run_id}", response_model=TailorRunResponse)
def get_tailor_run(
    run_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TailorRunResponse:
    run = TailorService(db).get_run(current_user.id, run_id)
    return TailorRunResponse(
        id=run.id,
        resume_document_id=run.resume_document_id,
        job_description_id=run.job_description_id,
        status=run.status,
        idempotency_key=run.idempotency_key,
        model_name=run.model_name,
        prompt_version=run.prompt_version,
        run_attempt_count=run.run_attempt_count,
        ats_keyword_alignment=run.ats_keyword_alignment,
        model_trace_metadata=run.model_trace_metadata,
        failure_stage=run.failure_stage,
        failure_reason=run.failure_reason,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )
