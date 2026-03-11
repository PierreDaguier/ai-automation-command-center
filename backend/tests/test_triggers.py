import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from app.main import app

WEBHOOK_SECRET = "replace-webhook-secret"


def _raw_payload(payload: dict) -> bytes:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _signature(raw_payload: bytes) -> str:
    return hmac.new(WEBHOOK_SECRET.encode("utf-8"), raw_payload, hashlib.sha256).hexdigest()


def _token(client: TestClient) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "operator@command-center.io", "password": "ChangeMe!123"},
    )
    return response.json()["access_token"]


def test_webhook_rejects_invalid_signature() -> None:
    payload = {"case_id": "INV-1001"}
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/triggers/webhook/invoice-dispute-triage",
            json=payload,
            headers={"X-Signature": "invalid"},
        )
        assert response.status_code == 401


def test_webhook_accepts_valid_signature_and_idempotency() -> None:
    payload = {"case_id": "INV-1002", "amount": 8920}
    raw_payload = _raw_payload(payload)
    signature = _signature(raw_payload)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/triggers/webhook/invoice-dispute-triage",
            content=raw_payload,
            headers={
                "Content-Type": "application/json",
                "X-Signature": signature,
                "X-Idempotency-Key": "event-abc-1002",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["duplicate"] is False

        duplicate = client.post(
            "/api/v1/triggers/webhook/invoice-dispute-triage",
            content=raw_payload,
            headers={
                "Content-Type": "application/json",
                "X-Signature": signature,
                "X-Idempotency-Key": "event-abc-1002",
            },
        )
        assert duplicate.status_code == 200
        dup_body = duplicate.json()
        assert dup_body["duplicate"] is True
        assert dup_body["run_id"] == body["run_id"]


def test_scheduler_trigger_requires_auth() -> None:
    with TestClient(app) as client:
        response = client.post("/api/v1/triggers/scheduler/run", json={})
        assert response.status_code == 401


def test_scheduler_trigger_runs_when_authenticated() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/triggers/scheduler/run",
            json={"workflow_slug": "invoice-dispute-triage"},
            headers={"Authorization": f"Bearer {_token(client)}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["workflow_slug"] == "invoice-dispute-triage"
