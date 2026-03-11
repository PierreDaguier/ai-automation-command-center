from datetime import datetime

from pydantic import BaseModel

from app.db.models import RunStatus


class WorkflowRunResponse(BaseModel):
    run_id: str
    workflow_slug: str
    status: RunStatus
    idempotency_key: str
    queued: bool
    duplicate: bool = False
    created_at: datetime
