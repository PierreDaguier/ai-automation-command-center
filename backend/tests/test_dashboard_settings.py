import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from app.main import app

WEBHOOK_SECRET = "replace-webhook-secret"


def _token(client: TestClient) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "operator@command-center.io", "password": "ChangeMe!123"},
    )
    return response.json()["access_token"]


def _signature(raw_payload: bytes) -> str:
    return hmac.new(WEBHOOK_SECRET.encode("utf-8"), raw_payload, hashlib.sha256).hexdigest()


def test_dashboard_and_settings_endpoints() -> None:
    payload = {"event": "kpi-seed", "amount": 1000}
    raw_payload = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

    with TestClient(app) as client:
        trigger = client.post(
            "/api/v1/triggers/webhook/invoice-dispute-triage",
            content=raw_payload,
            headers={
                "Content-Type": "application/json",
                "X-Signature": _signature(raw_payload),
                "X-Idempotency-Key": "kpi-seed-001",
            },
        )
        assert trigger.status_code == 200

        token = _token(client)

        kpi_response = client.get(
            "/api/v1/dashboard/kpis",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert kpi_response.status_code == 200
        kpis = kpi_response.json()
        assert "success_rate" in kpis
        assert "p95_latency_ms" in kpis

        settings_response = client.get(
            "/api/v1/settings",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert settings_response.status_code == 200
        settings = settings_response.json()
        assert "safety_controls" in settings
        assert "environment" in settings
