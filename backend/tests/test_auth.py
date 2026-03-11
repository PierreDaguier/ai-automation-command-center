from fastapi.testclient import TestClient

from app.main import app


def test_login_success() -> None:
    payload = {
        "email": "admin@command-center.io",
        "password": "ChangeMe!123",
    }
    with TestClient(app) as client:
        response = client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"


def test_login_failure() -> None:
    payload = {
        "email": "admin@command-center.io",
        "password": "wrong-password",
    }
    with TestClient(app) as client:
        response = client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == 401


def test_workflow_catalog_requires_auth() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/workflows/catalog")
        assert response.status_code == 401
