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


def _raw(payload: dict) -> bytes:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _signature(raw_payload: bytes) -> str:
    return hmac.new(WEBHOOK_SECRET.encode("utf-8"), raw_payload, hashlib.sha256).hexdigest()


def _create_pending_approval(client: TestClient, workflow_slug: str, key: str) -> str:
    payload = {"workflow_slug": workflow_slug, "case": key, "amount": 7300}
    raw_payload = _raw(payload)
    response = client.post(
        f"/api/v1/triggers/webhook/{workflow_slug}",
        content=raw_payload,
        headers={
            "Content-Type": "application/json",
            "X-Signature": _signature(raw_payload),
            "X-Idempotency-Key": key,
        },
    )
    assert response.status_code == 200
    return response.json()["run_id"]


def test_approval_queue_and_reject_flow() -> None:
    with TestClient(app) as client:
        token = _token(client)
        run_id = _create_pending_approval(client, "vendor-risk-escalation", "approval-reject-1")

        queue_response = client.get(
            "/api/v1/approvals/queue",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert queue_response.status_code == 200

        items = queue_response.json()["items"]
        target = next(item for item in items if item["run_id"] == run_id)

        decision_response = client.post(
            f"/api/v1/approvals/{target['approval_id']}/decision",
            json={"decision": "reject", "reason": "Policy threshold exceeded"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert decision_response.status_code == 200
        decision = decision_response.json()
        assert decision["approval_status"] == "rejected"
        assert decision["run_status"] == "rejected"


def test_approval_approve_executes_run() -> None:
    with TestClient(app) as client:
        token = _token(client)
        run_id = _create_pending_approval(client, "contract-renewal-safeguard", "approval-approve-1")

        queue_response = client.get(
            "/api/v1/approvals/queue",
            headers={"Authorization": f"Bearer {token}"},
        )
        items = queue_response.json()["items"]
        target = next(item for item in items if item["run_id"] == run_id)

        decision_response = client.post(
            f"/api/v1/approvals/{target['approval_id']}/decision",
            json={"decision": "approve", "reason": "Validated by operator"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert decision_response.status_code == 200
        decision = decision_response.json()
        assert decision["approval_status"] == "approved"
        assert decision["run_status"] in {"success", "failed"}
