from pydantic import BaseModel, Field


class WebhookTriggerRequest(BaseModel):
    payload: dict = Field(default_factory=dict)


class SchedulerTriggerRequest(BaseModel):
    workflow_slug: str | None = None
