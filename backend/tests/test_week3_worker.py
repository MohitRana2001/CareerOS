import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.ai.contracts import TailorOutput
from app.models import JobDescription, ResumeDocument, ResumeVersion, TailorRun, User
from app.workers import tasks


def test_tailor_worker_creates_version_and_is_idempotent(
    db_session: Session,
    testing_session_factory: sessionmaker,
    monkeypatch,
) -> None:
    now = datetime.now(UTC)

    user = User(
        id=uuid.uuid4(),
        google_sub="sub-week3",
        email="week3@example.com",
        full_name="Week Three",
        created_at=now,
        updated_at=now,
    )
    db_session.add(user)

    resume = ResumeDocument(
        id=uuid.uuid4(),
        user_id=user.id,
        source_file_url="https://example.com/resume.pdf",
        source_file_type="pdf",
        canonical_json={"experience": []},
        created_at=now,
        updated_at=now,
    )
    db_session.add(resume)

    jd = JobDescription(
        id=uuid.uuid4(),
        user_id=user.id,
        company_name="Acme",
        position_title="Backend Engineer",
        source_url=None,
        raw_text="Need Python, FastAPI, PostgreSQL, Redis, Docker, AWS and system design.",
        extracted_requirements={"keywords": ["python", "fastapi"]},
        created_at=now,
    )
    db_session.add(jd)

    run = TailorRun(
        id=uuid.uuid4(),
        user_id=user.id,
        resume_document_id=resume.id,
        job_description_id=jd.id,
        output_resume_version_id=None,
        status="PENDING",
        idempotency_key="week3-worker-idem-key",
        model_name="gemini-2.5-pro",
        prompt_version="v1",
        failure_stage=None,
        failure_reason=None,
        created_at=now,
        updated_at=now,
    )
    db_session.add(run)
    db_session.commit()

    monkeypatch.setattr(tasks, "SessionLocal", testing_session_factory)
    monkeypatch.setattr(
        tasks,
        "generate_tailored_content",
        lambda _prompt, _model: TailorOutput(
            tailored_summary="Backend engineer with strong API and distributed systems experience.",
            rewritten_bullets=[
                "Built FastAPI microservices with Redis caching and PostgreSQL persistence.",
                "Improved API latency by optimizing SQL queries and async endpoints.",
                "Deployed containerized services with Docker and CI workflows.",
            ],
            keywords_used=["python", "fastapi", "postgresql", "redis", "docker"],
        ),
    )

    first = tasks.tailor_resume.run(str(run.id))
    assert first["status"] == "SUCCEEDED"

    db_session.expire_all()
    refreshed_run = db_session.get(TailorRun, run.id)
    assert refreshed_run is not None
    assert refreshed_run.status == "SUCCEEDED"
    assert refreshed_run.output_resume_version_id is not None
    assert refreshed_run.run_attempt_count == 1
    assert refreshed_run.ats_keyword_alignment is not None
    assert refreshed_run.ats_keyword_alignment["alignment_score"] == 100
    assert refreshed_run.model_trace_metadata is not None
    assert refreshed_run.model_trace_metadata["provider"] == "gemini"

    versions = list(db_session.execute(select(ResumeVersion).where(ResumeVersion.resume_document_id == resume.id)).scalars())
    assert len(versions) == 1

    second = tasks.tailor_resume.run(str(run.id))
    assert second["status"] == "SUCCEEDED"

    versions_after = list(
        db_session.execute(select(ResumeVersion).where(ResumeVersion.resume_document_id == resume.id)).scalars()
    )
    assert len(versions_after) == 1


def test_openapi_contains_week2_examples(client) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schemas = response.json()["components"]["schemas"]

    assert schemas["TailorRunCreateRequest"]["examples"]
    assert schemas["TailorRunResponse"]["examples"]
    assert schemas["JobDescriptionCreateRequest"]["examples"]
    assert schemas["ResumeVersionCreateRequest"]["examples"]


def test_tailor_run_analytics_endpoint_returns_frontend_metrics(
    client,
    db_session: Session,
    testing_session_factory: sessionmaker,
    monkeypatch,
) -> None:
    now = datetime.now(UTC)

    user = User(
        id=uuid.uuid4(),
        google_sub="sub-analytics",
        email="analytics@example.com",
        full_name="Analytics User",
        created_at=now,
        updated_at=now,
    )
    db_session.add(user)

    resume = ResumeDocument(
        id=uuid.uuid4(),
        user_id=user.id,
        source_file_url="https://example.com/resume.pdf",
        source_file_type="pdf",
        canonical_json={"experience": []},
        created_at=now,
        updated_at=now,
    )
    db_session.add(resume)

    jd = JobDescription(
        id=uuid.uuid4(),
        user_id=user.id,
        company_name="Acme",
        position_title="Backend Engineer",
        source_url=None,
        raw_text="Need Python, FastAPI, PostgreSQL, Redis, Docker, AWS and system design.",
        extracted_requirements={"keywords": ["python", "fastapi", "postgresql", "redis", "docker", "aws"]},
        created_at=now,
    )
    db_session.add(jd)

    run = TailorRun(
        id=uuid.uuid4(),
        user_id=user.id,
        resume_document_id=resume.id,
        job_description_id=jd.id,
        output_resume_version_id=None,
        status="PENDING",
        idempotency_key="analytics-idem-key",
        model_name="gemini-2.5-pro",
        prompt_version="v1",
        run_attempt_count=0,
        ats_keyword_alignment=None,
        model_trace_metadata=None,
        failure_stage=None,
        failure_reason=None,
        created_at=now,
        updated_at=now,
    )
    db_session.add(run)
    db_session.commit()

    monkeypatch.setattr(tasks, "SessionLocal", testing_session_factory)
    monkeypatch.setattr(
        tasks,
        "generate_tailored_content",
        lambda _prompt, _model: TailorOutput(
            tailored_summary="Backend engineer with strong API and distributed systems experience.",
            rewritten_bullets=[
                "Built FastAPI microservices with Redis caching and PostgreSQL persistence.",
                "Improved API latency by optimizing SQL queries and async endpoints.",
                "Deployed containerized services with Docker and CI workflows.",
            ],
            keywords_used=["python", "fastapi", "postgresql", "redis", "docker"],
        ),
    )
    tasks.tailor_resume.run(str(run.id))
    db_session.expire_all()

    response = client.get(
        f"/api/v1/tailor-runs/{run.id}/analytics",
        headers={"X-Dev-User-Email": "analytics@example.com"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["attempts"] == 1
    assert payload["alignment_score"] == 83
    assert payload["missing_keywords_count"] == 1
    assert payload["latency_ms"] is not None
