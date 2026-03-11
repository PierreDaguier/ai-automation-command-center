from statistics import fmean

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.models import RunStatus, User, UserRole, WorkflowRun
from app.db.session import get_db
from app.schemas.dashboard import KpiResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/kpis", response_model=KpiResponse)
def kpis(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.operator)),
) -> KpiResponse:
    total_runs = db.scalar(select(func.count(WorkflowRun.id))) or 0

    if total_runs == 0:
        return KpiResponse(
            success_rate=0.0,
            p95_latency_ms=0.0,
            cost_per_run_usd=0.0,
            failed_runs=0,
            total_runs=0,
        )

    successful_runs = db.scalar(
        select(func.count(WorkflowRun.id)).where(WorkflowRun.status == RunStatus.success)
    ) or 0
    failed_runs = db.scalar(
        select(func.count(WorkflowRun.id)).where(
            WorkflowRun.status.in_([RunStatus.failed, RunStatus.rejected])
        )
    ) or 0

    latency_values = [
        row
        for row in db.scalars(
            select(WorkflowRun.latency_ms).where(WorkflowRun.latency_ms.is_not(None))
        ).all()
        if row is not None
    ]
    latency_values.sort()

    if latency_values:
        percentile_index = int(0.95 * (len(latency_values) - 1))
        p95_latency = float(latency_values[percentile_index])
    else:
        p95_latency = 0.0

    cost_values = [
        float(row)
        for row in db.scalars(
            select(WorkflowRun.estimated_cost_usd).where(WorkflowRun.estimated_cost_usd.is_not(None))
        ).all()
        if row is not None
    ]
    cost_per_run = float(fmean(cost_values)) if cost_values else 0.0

    return KpiResponse(
        success_rate=round((successful_runs / total_runs) * 100, 2),
        p95_latency_ms=round(p95_latency, 2),
        cost_per_run_usd=round(cost_per_run, 4),
        failed_runs=int(failed_runs),
        total_runs=int(total_runs),
    )
