from pydantic import BaseModel


class SafetyControls(BaseModel):
    max_retries: int
    timeout_seconds: float
    max_budget_per_run_usd: float


class SecretStatus(BaseModel):
    openai_api_key_set: bool
    n8n_api_key_set: bool


class EnvironmentStatus(BaseModel):
    database: str
    redis: str
    n8n: str


class SettingsOverviewResponse(BaseModel):
    secrets: SecretStatus
    environment: EnvironmentStatus
    safety_controls: SafetyControls
