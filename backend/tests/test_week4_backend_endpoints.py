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
            "raw_text": "Need Python, FastAPI, PostgreSQL, Redis, Docker and AWS skills for backend role.",
        },
        headers=headers,
    )
    assert response.status_code == 200
    return response.json()["id"]


def test_upload_url_and_patch_resume(client: TestClient) -> None:
    headers = {"X-Dev-User-Email": "week4-upload@example.com"}

    upload_response = client.post("/api/v1/resumes/upload-url", headers=headers)
    assert upload_response.status_code == 200
    upload = upload_response.json()
    assert upload["upload_url"]
    assert upload["file_url"]

    resume_id = _create_resume(client, headers)
    patch_response = client.patch(
        f"/api/v1/resumes/{resume_id}",
        json={"canonical_json": {"summary": "Backend Engineer"}},
        headers=headers,
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["canonical_json"]["summary"] == "Backend Engineer"


def test_compile_ats_skills_and_drive_export(client: TestClient, monkeypatch) -> None:
    headers = {"X-Dev-User-Email": "week4-flow@example.com"}

    resume_id = _create_resume(client, headers)
    jd_id = _create_jd(client, headers)

    version_response = client.post(
        f"/api/v1/resumes/{resume_id}/versions",
        json={
            "job_description_id": jd_id,
            "latex_source": "\\\\item Built FastAPI APIs with PostgreSQL and Redis",
            "created_by": "SYSTEM",
        },
        headers=headers,
    )
    assert version_response.status_code == 200
    version_id = version_response.json()["id"]

    monkeypatch.setattr("app.services.resume_service.compile_pdf.delay", lambda _id: None)
    compile_response = client.post(f"/api/v1/resumes/{resume_id}/versions/{version_id}/compile", headers=headers)
    assert compile_response.status_code == 200
    assert compile_response.json()["status"] == "RUNNING"

    ats_response = client.get(f"/api/v1/resumes/{resume_id}/versions/{version_id}/ats", headers=headers)
    assert ats_response.status_code == 200
    assert 0 <= ats_response.json()["score"] <= 100

    skills_response = client.get(f"/api/v1/resumes/{resume_id}/versions/{version_id}/skills-gap", headers=headers)
    assert skills_response.status_code == 200
    assert "critical_missing" in skills_response.json()

    monkeypatch.setattr("app.services.drive_service.export_drive.delay", lambda _version_id, _export_id: None)
    export_response = client.post("/api/v1/drive/exports", json={"resume_version_id": version_id}, headers=headers)
    assert export_response.status_code == 200
    export = export_response.json()
    assert export["status"] == "PENDING"

    get_export_response = client.get(f"/api/v1/drive/exports/{export['id']}", headers=headers)
    assert get_export_response.status_code == 200
    assert get_export_response.json()["id"] == export["id"]
