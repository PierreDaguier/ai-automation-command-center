from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str


class MessageResponse(BaseModel):
    message: str


class Pagination(BaseModel):
    total: int
    page: int
    page_size: int


class TimestampedModel(BaseModel):
    created_at: datetime
    updated_at: datetime
