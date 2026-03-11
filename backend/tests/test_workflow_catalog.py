from fastapi.testclient import TestClient

from app.main import app


def _token(client: TestClient) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "operator@command-center.io", "password": "ChangeMe!123"},
    )
    return response.json()["access_token"]


def test_workflow_catalog_authenticated() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/workflows/catalog",
            headers={"Authorization": f"Bearer {_token(client)}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body["items"]) >= 4
