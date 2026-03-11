from datetime import datetime

from pydantic import BaseModel


class ActionLogItem(BaseModel):
    id: str
    run_id: str
    action_type: str
    target: str
    status: str
    details_json: dict
    created_at: datetime


class ActionLogResponse(BaseModel):
    items: list[ActionLogItem]
