from pydantic import BaseModel


class KpiResponse(BaseModel):
    success_rate: float
    p95_latency_ms: float
    cost_per_run_usd: float
    failed_runs: int
    total_runs: int
