from fastapi.testclient import TestClient


def test_auth_me_requires_token(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_google_callback_and_me_flow(client: TestClient, monkeypatch) -> None:
    from app.services.auth_service import GoogleIdentity

    def fake_verify_google_id_token(_: str) -> GoogleIdentity:
        return GoogleIdentity(sub="google-sub-123", email="user@example.com", full_name="Demo User")

    monkeypatch.setattr("app.routers.auth.verify_google_id_token", fake_verify_google_id_token)

    callback_response = client.post(
        "/api/v1/auth/google/callback",
        json={"id_token": "x" * 24},
    )
    assert callback_response.status_code == 200
    access_token = callback_response.json()["access_token"]

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "user@example.com"
