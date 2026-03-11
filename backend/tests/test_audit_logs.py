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


def _sign(payload_raw: bytes) -> str:
    return hmac.new(WEBHOOK_SECRET.encode("utf-8"), payload_raw, hashlib.sha256).hexdigest()


def test_audit_and_logs_are_available_with_redaction() -> None:
    payload = {
        "customer_email": "buyer@example.com",
        "password": "super-secret",
        "amount": 4200,
    }
    raw_payload = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

    with TestClient(app) as client:
        trigger = client.post(
            "/api/v1/triggers/webhook/invoice-dispute-triage",
            content=raw_payload,
            headers={
                "Content-Type": "application/json",
                "X-Signature": _sign(raw_payload),
                "X-Idempotency-Key": "audit-log-redaction-1",
            },
        )
        assert trigger.status_code == 200
        run_id = trigger.json()["run_id"]
        token = _token(client)

        logs = client.get(
            f"/api/v1/logs/actions?run_id={run_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert logs.status_code == 200
        items = logs.json()["items"]
        assert len(items) >= 1
        serialized = json.dumps(items[0]["details_json"])
        assert "super-secret" not in serialized
        assert "buyer@example.com" not in serialized
        assert "[REDACTED]" in serialized

        timeline = client.get(
            "/api/v1/audit/timeline",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert timeline.status_code == 200
        timeline_items = timeline.json()["items"]
        assert len(timeline_items) >= 1
        assert any(item["action"].startswith("workflow.run") for item in timeline_items)
