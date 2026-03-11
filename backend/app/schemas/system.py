from pydantic import BaseModel


class EnvironmentStatusResponse(BaseModel):
    database: str
    redis: str
    n8n: str
