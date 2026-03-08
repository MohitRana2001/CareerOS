from fastapi.testclient import TestClient


def _create_resume(client: TestClient, headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/resumes",
        json={"source_file_url": "https://example.com/base.pdf", "source_file_type": "pdf"},
        headers=headers,
    )
    assert response.status_code == 200
    return response.json()["id"]


def _create_jd(client: TestClient, headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/job-descriptions",
        json={
            "company_name": "Acme",
            "position_title": "Backend Engineer",
            "raw_text": "We need Python, FastAPI, PostgreSQL, Redis, Docker and strong system design skills.",
        },
        headers=headers,
    )
    assert response.status_code == 200
    return response.json()["id"]


def test_job_description_parsing_and_read(client: TestClient) -> None:
    headers = {"X-Dev-User-Email": "week2-jd@example.com"}
    jd_id = _create_jd(client, headers)

    get_response = client.get(f"/api/v1/job-descriptions/{jd_id}", headers=headers)
    assert get_response.status_code == 200
    payload = get_response.json()
    assert "keywords" in payload["extracted_requirements"]
    assert "python" in payload["extracted_requirements"]["keywords"]


def test_resume_versions_increment_and_ownership(client: TestClient) -> None:
    owner_headers = {"X-Dev-User-Email": "week2-resume-owner@example.com"}
    other_headers = {"X-Dev-User-Email": "week2-resume-other@example.com"}

    resume_id = _create_resume(client, owner_headers)
    jd_id = _create_jd(client, owner_headers)

    v1_response = client.post(
        f"/api/v1/resumes/{resume_id}/versions",
        json={"latex_source": "v1 content", "created_by": "USER"},
        headers=owner_headers,
    )
    assert v1_response.status_code == 200
    v1 = v1_response.json()
    assert v1["version_no"] == 1

    v2_response = client.post(
        f"/api/v1/resumes/{resume_id}/versions",
        json={
            "based_on_version_id": v1["id"],
            "job_description_id": jd_id,
            "latex_source": "v2 tailored content",
            "created_by": "SYSTEM",
        },
        headers=owner_headers,
    )
    assert v2_response.status_code == 200
    v2 = v2_response.json()
    assert v2["version_no"] == 2
    assert v2["based_on_version_id"] == v1["id"]

    list_response = client.get(f"/api/v1/resumes/{resume_id}/versions", headers=owner_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2

    forbidden_response = client.get(f"/api/v1/resumes/{resume_id}/versions/{v1['id']}", headers=other_headers)
    assert forbidden_response.status_code == 404


def test_tailor_run_orchestration_and_idempotency(client: TestClient, monkeypatch) -> None:
    headers = {"X-Dev-User-Email": "week2-tailor@example.com"}
    resume_id = _create_resume(client, headers)
    jd_id = _create_jd(client, headers)

    class _DummyAsyncResult:
        id = "dummy-task-id"

    def _fake_delay(_: str) -> _DummyAsyncResult:
        return _DummyAsyncResult()

    monkeypatch.setattr("app.services.tailor_service.tailor_resume.delay", _fake_delay)

    payload = {
        "resume_document_id": resume_id,
        "job_description_id": jd_id,
        "idempotency_key": "abc123xyz",
    }
    create_response = client.post("/api/v1/tailor-runs", json=payload, headers=headers)
    assert create_response.status_code == 200
    run = create_response.json()
    assert run["status"] == "PENDING"

    second_response = client.post("/api/v1/tailor-runs", json=payload, headers=headers)
    assert second_response.status_code == 200
    assert second_response.json()["id"] == run["id"]

    get_response = client.get(f"/api/v1/tailor-runs/{run['id']}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == run["id"]
