from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import (
    ActionLog,
    AgentTask,
    ApprovalRequest,
    ApprovalStatus,
    AuditEvent,
    DeadLetterEvent,
    RunStatus,
    Workflow,
    WorkflowRun,
)
from app.db.session import SessionLocal
from app.schemas.agent import AgentExecutionRequest, ToolContract, ToolParameter
from app.services.agents.manager import AgentService
from app.services.n8n_client import N8NClient
from app.services.redaction import redact_payload


def _to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _default_tools() -> list[ToolContract]:
    return [
        ToolContract(
            name="route_operational_action",
            description="Route action payload to the right execution lane.",
            parameters=[
                ToolParameter(name="team", type="string", description="Target team", required=True),
                ToolParameter(name="priority", type="string", description="Priority level", required=True),
                ToolParameter(name="reason", type="string", description="Routing reason", required=False),
            ],
        )
    ]


def _tool_contracts_for(workflow: Workflow) -> list[ToolContract]:
    contracts = workflow.metadata_json.get("tool_contracts") if workflow.metadata_json else None
    if not contracts:
        return _default_tools()
    return [ToolContract.model_validate(item) for item in contracts]


def _requires_approval(run: WorkflowRun) -> bool:
    return bool(run.workflow.requires_approval or run.workflow.risk_level.lower() == "high")


def _request_human_approval(db: Session, run: WorkflowRun) -> None:
    approval = ApprovalRequest(
        run_id=run.id,
        action_label=f"Authorize execution for workflow {run.workflow.slug}",
        status=ApprovalStatus.pending,
        requested_by="system",
    )
    run.status = RunStatus.waiting_approval
    db.add(approval)
    db.add(
        AuditEvent(
            actor="system",
            actor_role="service",
            action="approval.requested",
            entity_type="workflow_run",
            entity_id=run.id,
            metadata_json={"workflow_slug": run.workflow.slug},
        )
    )


def _mark_dead_letter(db: Session, run: WorkflowRun, reason: str, payload: dict[str, Any]) -> None:
    db.add(
        DeadLetterEvent(
            run_id=run.id,
            reason=reason,
            payload_json=redact_payload(payload),
        )
    )
    run.status = RunStatus.failed
    run.error_message = reason
    run.completed_at = datetime.now(timezone.utc)
    db.add(
        AuditEvent(
            actor="system",
            actor_role="service",
            action="workflow.run.dead_lettered",
            entity_type="workflow_run",
            entity_id=run.id,
            metadata_json={"reason": reason},
        )
    )


def _execute_operational_action(db: Session, run: WorkflowRun, agent_payload: dict[str, Any]) -> RunStatus:
    n8n_client = N8NClient()
    orchestration_payload = {
        "run_id": run.id,
        "workflow_slug": run.workflow.slug,
        "input": run.input_payload,
        "agent": agent_payload.get("output", {}),
        "tool_calls": agent_payload.get("tool_calls", []),
    }
    n8n_result = n8n_client.trigger_workflow(run.workflow.slug, orchestration_payload)

    action_status = "success" if n8n_result.get("status") in {"triggered", "simulated"} else "warning"

    db.add(
        ActionLog(
            run_id=run.id,
            action_type="n8n.workflow.trigger",
            target=run.workflow.slug,
            status=action_status,
            details_json=redact_payload(
                {
                    "agent_provider": agent_payload.get("provider", "unknown"),
                    "agent_cost_usd": agent_payload.get("cost_usd", 0.0),
                    "n8n": n8n_result,
                }
            ),
        )
    )

    run.output_payload = redact_payload(
        {
        "agent": agent_payload,
        "n8n": n8n_result,
        }
    )
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
            metadata_json={
                "status": run.status.value,
                "agent_provider": agent_payload.get("provider", "unknown"),
            },
        )
    )
    return run.status


def process_workflow_run(run_id: str) -> None:
    with SessionLocal() as db:
        run = db.scalar(select(WorkflowRun).where(WorkflowRun.id == run_id))
        if not run:
            return

        run.status = RunStatus.running
        run.started_at = datetime.now(timezone.utc)
        db.commit()

        agent_service = AgentService()
        agent_request = AgentExecutionRequest(
            prompt=f"Analyze workflow run for {run.workflow.slug} and produce actionable structured output.",
            input_payload={"run_id": run.id, "workflow_slug": run.workflow.slug, **run.input_payload},
            tools=_tool_contracts_for(run.workflow),
            model=settings.openai_model,
            provider=agent_service.provider_name,
        )

        agent_task = AgentTask(
            run_id=run.id,
            status=RunStatus.running,
            provider=agent_service.provider_name,
            model=agent_request.model or settings.openai_model,
            structured_input=agent_request.model_dump(),
            attempts=1,
        )
        db.add(agent_task)
        db.commit()
        db.refresh(agent_task)

        try:
            agent_result = agent_service.execute(agent_request)

            agent_task.status = RunStatus.success
            agent_task.provider = agent_result.provider
            agent_task.model = agent_result.model
            agent_task.structured_output = agent_result.model_dump()

            run.output_payload = {"agent": agent_result.model_dump()}
            run.estimated_cost_usd = agent_result.cost_usd

            if float(agent_result.cost_usd) > settings.max_budget_per_run_usd:
                _mark_dead_letter(
                    db,
                    run,
                    f"Budget guardrail exceeded ({agent_result.cost_usd} > {settings.max_budget_per_run_usd})",
                    {"agent_result": agent_result.model_dump()},
                )
                db.commit()
                return

            if _requires_approval(run):
                _request_human_approval(db, run)
            else:
                _execute_operational_action(db, run, agent_result.model_dump())

        except Exception as exc:
            agent_task.status = RunStatus.failed
            agent_task.error_message = str(exc)
            _mark_dead_letter(
                db,
                run,
                str(exc),
                {"run_input": run.input_payload, "workflow_slug": run.workflow.slug},
            )

        db.commit()


def finalize_approved_run(run_id: str) -> RunStatus:
    with SessionLocal() as db:
        run = db.scalar(select(WorkflowRun).where(WorkflowRun.id == run_id))
        if not run:
            return RunStatus.failed

        if run.started_at is None:
            run.started_at = datetime.now(timezone.utc)

        agent_payload = {}
        if isinstance(run.output_payload, dict):
            maybe_agent = run.output_payload.get("agent")
            if isinstance(maybe_agent, dict):
                agent_payload = maybe_agent

        status = _execute_operational_action(db, run, agent_payload)
        db.add(
            AuditEvent(
                actor="system",
                actor_role="service",
                action="workflow.run.approved_execution",
                entity_type="workflow_run",
                entity_id=run.id,
                metadata_json={"status": status.value},
            )
        )
        db.commit()
        return status
