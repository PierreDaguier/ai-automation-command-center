from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.db.models import ApprovalStatus, RunStatus


class ApprovalQueueItem(BaseModel):
    approval_id: str
    run_id: str
    workflow_slug: str
    action_label: str
    requested_by: str
    status: ApprovalStatus
    created_at: datetime


class ApprovalQueueResponse(BaseModel):
    items: list[ApprovalQueueItem]


class ApprovalDecisionRequest(BaseModel):
    decision: Literal["approve", "reject"]
    reason: str = Field(min_length=3, max_length=500)


class ApprovalDecisionResponse(BaseModel):
    approval_id: str
    run_id: str
    approval_status: ApprovalStatus
    run_status: RunStatus
    decided_by: str
    reason: str
    decided_at: datetime
