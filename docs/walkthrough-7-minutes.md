# 7-Minute Client Walkthrough

## Goal
Show a non-technical buyer that the platform can execute operations workflows safely, with AI assistance and human governance.

## Minute 0-1: Frame the Value
- Open `/login`.
- Explain that this is a production-grade demo, not a mock dashboard.
- Mention the control loop: trigger -> agent -> approval (if needed) -> execution -> audit.

## Minute 1-2: Dashboard KPI Story
- Open `/dashboard`.
- Highlight:
  - success rate
  - p95 latency
  - cost per run
  - failed runs
- Explain that these KPIs come from actual run records, not hardcoded metrics.

## Minute 2-3: Workflow Catalog + Trigger Ingestion
- Open `/workflows`.
- Show business-friendly catalog entries and risk labels.
- Point to webhook and scheduler ingestion endpoints.

## Minute 3-4: Run a High-Risk Workflow
- Call signed webhook endpoint for a high-risk workflow (`vendor-risk-escalation`).
- Explain idempotency key handling and signature verification.
- Show that the run pauses in approval queue.

## Minute 4-5: Human-in-the-Loop Decision
- Open `/approvals`.
- Approve one request with a reason.
- Reject another with a reason.
- Explain that decision metadata is audited and non-silent.

## Minute 5-6: Show Operational Evidence
- Open `/logs` and `/audit`.
- Show redacted fields in logs and chronological audit events.
- Explain dead-letter + retry controls for reliability.

## Minute 6-7: Settings and Deployment Confidence
- Open `/settings`.
- Show secret status, environment checks, and safety controls.
- Close with Docker Compose + CI + PR workflow and observability stack.

## Demo Script Snippets
```bash
# login token
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"operator@command-center.io","password":"ChangeMe!123"}'

# trigger high-risk workflow
curl -s -X POST http://localhost:8000/api/v1/triggers/webhook/vendor-risk-escalation \
  -H 'Content-Type: application/json' \
  -H 'X-Signature: <hmac_sha256_payload>' \
  -H 'X-Idempotency-Key: demo-risk-001' \
  -d '{"vendor":"ACME","amount":9800}'
```
