from fastapi.testclient import TestClient


def test_application_create_update_note_flow(client: TestClient) -> None:
    headers = {"X-Dev-User-Email": "apps-user@example.com"}
    create_response = client.post(
        "/api/v1/applications",
        json={
            "company_name": "Acme",
            "position_title": "Backend Engineer",
            "status": "APPLIED",
        },
        headers=headers,
    )
    assert create_response.status_code == 200
    app_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/applications/{app_id}",
        json={"status": "INTERVIEW"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "INTERVIEW"

    note_response = client.post(
        f"/api/v1/applications/{app_id}/notes",
        json={"note": "Recruiter replied"},
        headers=headers,
    )
    assert note_response.status_code == 200
    assert note_response.json()["message"] == "Note added"


def test_application_status_validation(client: TestClient) -> None:
    headers = {"X-Dev-User-Email": "apps-user@example.com"}
    response = client.post(
        "/api/v1/applications",
        json={
            "company_name": "Acme",
            "position_title": "Backend Engineer",
            "status": "UNKNOWN",
        },
        headers=headers,
    )
    assert response.status_code == 422
