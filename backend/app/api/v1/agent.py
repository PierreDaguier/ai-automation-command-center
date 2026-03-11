from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.models import AgentTask, AuditEvent, RunStatus, User, UserRole, WorkflowRun
from app.db.session import get_db
from app.schemas.agent import AgentExecutionRequest, AgentTaskResponse
from app.services.agents.manager import AgentService

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/execute", response_model=AgentTaskResponse)
def execute_agent_task(
    payload: AgentExecutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.operator)),
) -> AgentTaskResponse:
    run = None
    run_id = payload.input_payload.get("run_id")
    if run_id:
        run = db.scalar(select(WorkflowRun).where(WorkflowRun.id == run_id))
        if not run:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")

    service = AgentService(provider_hint=payload.provider)

    task = AgentTask(
        run_id=run.id if run else None,
        status=RunStatus.running,
        provider=service.provider_name,
        model=payload.model or "auto",
        structured_input=payload.model_dump(),
        attempts=1,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    result = service.execute(payload)

    task.status = RunStatus.success
    task.structured_output = result.model_dump()
    task.model = result.model

    db.add(
        AuditEvent(
            actor=current_user.email,
            actor_role=current_user.role.value,
            action="agent.task.executed",
            entity_type="agent_task",
            entity_id=task.id,
            metadata_json={
                "provider": result.provider,
                "run_id": run.id if run else None,
            },
        )
    )
    db.commit()

    return AgentTaskResponse(
        task_id=task.id,
        run_id=run.id if run else None,
        status=task.status.value,
        result=result,
    )
