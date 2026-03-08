from fastapi.testclient import TestClient


def test_create_and_list_resumes(client: TestClient) -> None:
    headers = {"X-Dev-User-Email": "resume-user@example.com"}
    create_response = client.post(
        "/api/v1/resumes",
        json={"source_file_url": "https://example.com/resume.pdf", "source_file_type": "pdf"},
        headers=headers,
    )
    assert create_response.status_code == 200
    created = create_response.json()
    assert created["source_file_type"] == "pdf"

    list_response = client.get("/api/v1/resumes", headers=headers)
    assert list_response.status_code == 200
    rows = list_response.json()
    assert len(rows) == 1
    assert rows[0]["id"] == created["id"]


def test_resume_validation_rejects_invalid_type(client: TestClient) -> None:
    headers = {"X-Dev-User-Email": "resume-user@example.com"}
    response = client.post(
        "/api/v1/resumes",
        json={"source_file_url": "https://example.com/resume.txt", "source_file_type": "txt"},
        headers=headers,
    )
    assert response.status_code == 422
