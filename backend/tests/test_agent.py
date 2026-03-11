from fastapi.testclient import TestClient

from app.main import app


def _token(client: TestClient) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "operator@command-center.io", "password": "ChangeMe!123"},
    )
    return response.json()["access_token"]


def test_agent_execute_requires_auth() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/agent/execute",
            json={"prompt": "Classify this request", "input_payload": {"amount": 2000}},
        )
        assert response.status_code == 401


def test_agent_execute_with_mock_provider() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/agent/execute",
            json={
                "prompt": "Assess operational risk",
                "provider": "mock",
                "input_payload": {"amount": 9200, "vendor": "Acme"},
                "tools": [
                    {
                        "name": "route_operational_action",
                        "description": "Route to owner",
                        "parameters": [
                            {
                                "name": "team",
                                "type": "string",
                                "description": "Owning team",
                                "required": True,
                            }
                        ],
                    }
                ],
            },
            headers={"Authorization": f"Bearer {_token(client)}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert body["result"]["provider"] == "mock"
        assert "suggested_actions" in body["result"]["output"]
