from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.models import ApprovalRequest, ApprovalStatus, AuditEvent, RunStatus, User, UserRole, Workflow, WorkflowRun
from app.db.session import get_db
from app.schemas.approval import (
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    ApprovalQueueItem,
    ApprovalQueueResponse,
)
from app.workers.tasks import finalize_approved_run

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/queue", response_model=ApprovalQueueResponse)
def approval_queue(
    state: ApprovalStatus = Query(default=ApprovalStatus.pending),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.operator)),
) -> ApprovalQueueResponse:
    rows = db.execute(
        select(ApprovalRequest, WorkflowRun, Workflow)
        .join(WorkflowRun, WorkflowRun.id == ApprovalRequest.run_id)
        .join(Workflow, Workflow.id == WorkflowRun.workflow_id)
        .where(ApprovalRequest.status == state)
        .order_by(ApprovalRequest.created_at.asc())
    ).all()

    items = [
        ApprovalQueueItem(
            approval_id=approval.id,
            run_id=run.id,
            workflow_slug=workflow.slug,
            action_label=approval.action_label,
            requested_by=approval.requested_by,
            status=approval.status,
            created_at=approval.created_at,
        )
        for approval, run, workflow in rows
    ]
    return ApprovalQueueResponse(items=items)


@router.post("/{approval_id}/decision", response_model=ApprovalDecisionResponse)
def approval_decision(
    approval_id: str,
    payload: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.operator)),
) -> ApprovalDecisionResponse:
    approval = db.scalar(select(ApprovalRequest).where(ApprovalRequest.id == approval_id))
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")
    if approval.status != ApprovalStatus.pending:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Approval is not pending")

    run = db.scalar(select(WorkflowRun).where(WorkflowRun.id == approval.run_id))
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")

    approval.status = ApprovalStatus.approved if payload.decision == "approve" else ApprovalStatus.rejected
    approval.decided_by = current_user.email
    approval.reason = payload.reason
    approval.decided_at = datetime.now(timezone.utc)

    if payload.decision == "approve":
        run.status = RunStatus.approved
        db.commit()
        final_status = finalize_approved_run(run.id)
    else:
        run.status = RunStatus.rejected
        run.error_message = payload.reason
        run.completed_at = datetime.now(timezone.utc)
        final_status = run.status
        db.add(
            AuditEvent(
                actor=current_user.email,
                actor_role=current_user.role.value,
                action="approval.rejected",
                entity_type="workflow_run",
                entity_id=run.id,
                metadata_json={"reason": payload.reason},
            )
        )
        db.commit()

    db.add(
        AuditEvent(
            actor=current_user.email,
            actor_role=current_user.role.value,
            action=f"approval.{payload.decision}",
            entity_type="approval_request",
            entity_id=approval.id,
            metadata_json={"run_id": run.id, "reason": payload.reason},
        )
    )
    db.commit()

    return ApprovalDecisionResponse(
        approval_id=approval.id,
        run_id=run.id,
        approval_status=approval.status,
        run_status=final_status,
        decided_by=current_user.email,
        reason=payload.reason,
        decided_at=approval.decided_at or datetime.now(timezone.utc),
    )
