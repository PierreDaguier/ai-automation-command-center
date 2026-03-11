from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.models import User, UserRole, Workflow
from app.db.session import get_db
from app.schemas.run import WorkflowRunResponse
from app.schemas.trigger import SchedulerTriggerRequest
from app.services.orchestrator import create_run_from_event
from app.services.signing import verify_webhook_signature

router = APIRouter(prefix="/triggers", tags=["triggers"])


@router.post("/webhook/{workflow_slug}", response_model=WorkflowRunResponse)
async def webhook_trigger(
    workflow_slug: str,
    request: Request,
    db: Session = Depends(get_db),
    x_signature: str | None = Header(default=None, alias="X-Signature"),
    x_idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key"),
) -> WorkflowRunResponse:
    payload_raw = await request.body()
    verify_webhook_signature(payload_raw, x_signature)

    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body") from exc

    workflow = db.scalar(
        select(Workflow).where(Workflow.slug == workflow_slug, Workflow.enabled.is_(True))
    )
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    return create_run_from_event(
        db=db,
        workflow=workflow,
        payload=payload,
        payload_raw=payload_raw,
        source="webhook",
        actor=None,
        idempotency_header=x_idempotency_key,
    )


@router.post("/scheduler/run", response_model=list[WorkflowRunResponse])
def scheduler_trigger(
    payload: SchedulerTriggerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.operator)),
) -> list[WorkflowRunResponse]:
    query = select(Workflow).where(Workflow.enabled.is_(True))
    if payload.workflow_slug:
        query = query.where(Workflow.slug == payload.workflow_slug)
    else:
        query = query.where(Workflow.schedule_cron.is_not(None))

    workflows = db.scalars(query).all()
    if not workflows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matching workflows")

    responses: list[WorkflowRunResponse] = []
    for workflow in workflows:
        event_payload = {
            "source": "scheduler",
            "workflow_slug": workflow.slug,
            "initiator": current_user.email,
        }
        payload_raw = str(event_payload).encode("utf-8")
        response = create_run_from_event(
            db=db,
            workflow=workflow,
            payload=event_payload,
            payload_raw=payload_raw,
            source="scheduler",
            actor=current_user,
            idempotency_header=None,
        )
        responses.append(response)

    return responses
