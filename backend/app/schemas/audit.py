from datetime import datetime

from pydantic import BaseModel


class AuditTimelineItem(BaseModel):
    id: str
    actor: str
    actor_role: str
    action: str
    entity_type: str
    entity_id: str
    metadata_json: dict
    created_at: datetime


class AuditTimelineResponse(BaseModel):
    items: list[AuditTimelineItem]
