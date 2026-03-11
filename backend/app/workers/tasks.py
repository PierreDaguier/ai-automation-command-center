from datetime import datetime, timezone

from sqlalchemy import select

from app.core.config import settings
from app.db.models import ActionLog, AgentTask, AuditEvent, RunStatus, Workflow, WorkflowRun
from app.db.session import SessionLocal
from app.schemas.agent import AgentExecutionRequest, ToolContract, ToolParameter
from app.services.agents.manager import AgentService
from app.services.n8n_client import N8NClient


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

            n8n_client = N8NClient()
            orchestration_payload = {
                "run_id": run.id,
                "workflow_slug": run.workflow.slug,
                "input": run.input_payload,
                "agent": agent_result.output,
                "tool_calls": agent_result.tool_calls,
            }
            n8n_result = n8n_client.trigger_workflow(run.workflow.slug, orchestration_payload)

            action_status = "success" if n8n_result.get("status") in {"triggered", "simulated"} else "warning"

            db.add(
                ActionLog(
                    run_id=run.id,
                    action_type="n8n.workflow.trigger",
                    target=run.workflow.slug,
                    status=action_status,
                    details_json={
                        "agent_provider": agent_result.provider,
                        "agent_cost_usd": agent_result.cost_usd,
                        "n8n": n8n_result,
                    },
                )
            )

            run.output_payload = {
                "agent": agent_result.model_dump(),
                "n8n": n8n_result,
            }
            run.status = RunStatus.success if action_status == "success" else RunStatus.failed
            run.estimated_cost_usd = agent_result.cost_usd
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
                        "agent_provider": agent_result.provider,
                    },
                )
            )

        except Exception as exc:
            agent_task.status = RunStatus.failed
            agent_task.error_message = str(exc)
            run.status = RunStatus.failed
            run.error_message = str(exc)
            run.completed_at = datetime.now(timezone.utc)
            db.add(
                AuditEvent(
                    actor="system",
                    actor_role="service",
                    action="workflow.run.failed",
                    entity_type="workflow_run",
                    entity_id=run.id,
                    metadata_json={"error": str(exc)},
                )
            )

        db.commit()
