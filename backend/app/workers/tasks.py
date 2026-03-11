from datetime import datetime, timezone

from sqlalchemy import select

from app.db.models import ActionLog, AuditEvent, RunStatus, WorkflowRun
from app.db.session import SessionLocal
from app.services.n8n_client import N8NClient


def _to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def process_workflow_run(run_id: str) -> None:
    with SessionLocal() as db:
        run = db.scalar(select(WorkflowRun).where(WorkflowRun.id == run_id))
        if not run:
            return

        run.status = RunStatus.running
        run.started_at = datetime.now(timezone.utc)
        db.commit()

        n8n_client = N8NClient()
        result = n8n_client.trigger_workflow(run.workflow.slug, run.input_payload)

        action_status = "success" if result.get("status") in {"triggered", "simulated"} else "warning"

        db.add(
            ActionLog(
                run_id=run.id,
                action_type="n8n.workflow.trigger",
                target=run.workflow.slug,
                status=action_status,
                details_json=result,
            )
        )

        run.output_payload = result
        run.status = RunStatus.success if action_status == "success" else RunStatus.failed
        run.completed_at = datetime.now(timezone.utc)
        if run.started_at and run.completed_at:
            delta = _to_utc(run.completed_at) - _to_utc(run.started_at)
            run.latency_ms = int(delta.total_seconds() * 1000)

        db.add(
            AuditEvent(
                actor="system",
                actor_role="service",
                action="workflow.run.executed",
                entity_type="workflow_run",
                entity_id=run.id,
                metadata_json={"status": run.status.value},
            )
        )

        db.commit()
