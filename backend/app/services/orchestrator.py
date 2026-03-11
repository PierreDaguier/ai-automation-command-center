from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AuditEvent, InboundEvent, RunStatus, User, Workflow, WorkflowRun
from app.schemas.run import WorkflowRunResponse
from app.services.signing import payload_hash
from app.workers.queue import get_queue
from app.workers.tasks import process_workflow_run


def _resolve_idempotency_key(request_key: str | None, payload_raw: bytes) -> str:
    if request_key:
        return request_key
    return payload_hash(payload_raw)


def enqueue(run: WorkflowRun) -> tuple[bool, str | None]:
    queue = get_queue()
    if queue is None:
        return False, None

    job = queue.enqueue("app.workers.tasks.process_workflow_run", run.id)
    return True, job.id


def create_run_from_event(
    db: Session,
    workflow: Workflow,
    payload: dict,
    payload_raw: bytes,
    source: str,
    actor: User | None,
    idempotency_header: str | None,
) -> WorkflowRunResponse:
    idempotency_key = _resolve_idempotency_key(idempotency_header, payload_raw)

    existing_event = db.scalar(
        select(InboundEvent).where(InboundEvent.idempotency_key == idempotency_key)
    )
    if existing_event:
        existing_run = db.scalar(select(WorkflowRun).where(WorkflowRun.id == existing_event.run_id))
        if not existing_run:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Idempotency key collision without run",
            )
        return WorkflowRunResponse(
            run_id=existing_run.id,
            workflow_slug=workflow.slug,
            status=existing_run.status,
            idempotency_key=idempotency_key,
            queued=bool(existing_run.queue_job_id),
            duplicate=True,
            created_at=existing_run.created_at,
        )

    run = WorkflowRun(
        workflow_id=workflow.id,
        triggered_by=actor.id if actor else None,
        trigger_type=source,
        status=RunStatus.queued,
        idempotency_key=idempotency_key,
        input_payload=payload,
        started_at=datetime.now(timezone.utc),
    )
    db.add(run)
    db.flush()

    db.add(
        InboundEvent(
            source=source,
            idempotency_key=idempotency_key,
            payload_hash=payload_hash(payload_raw),
            run_id=run.id,
        )
    )

    db.add(
        AuditEvent(
            actor=actor.email if actor else "system",
            actor_role=actor.role.value if actor else "service",
            action="workflow.run.created",
            entity_type="workflow_run",
            entity_id=run.id,
            metadata_json={
                "workflow_slug": workflow.slug,
                "source": source,
                "queued": False,
            },
        )
    )

    db.commit()
    queued, job_id = enqueue(run)
    if queued:
        run.queue_job_id = job_id
        db.add(
            AuditEvent(
                actor="system",
                actor_role="service",
                action="workflow.run.enqueued",
                entity_type="workflow_run",
                entity_id=run.id,
                metadata_json={"queue_job_id": job_id},
            )
        )
        db.commit()
    else:
        process_workflow_run(run.id)

    db.refresh(run)

    return WorkflowRunResponse(
        run_id=run.id,
        workflow_slug=workflow.slug,
        status=run.status,
        idempotency_key=idempotency_key,
        queued=queued,
        duplicate=False,
        created_at=run.created_at,
    )
