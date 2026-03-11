from fastapi import APIRouter, Depends
from redis import Redis
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.config import settings
from app.db.models import User, UserRole
from app.db.session import get_db
from app.schemas.settings import (
    EnvironmentStatus,
    SafetyControls,
    SecretStatus,
    SettingsOverviewResponse,
)

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsOverviewResponse)
def settings_overview(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.operator)),
) -> SettingsOverviewResponse:
    db_status = "connected"
    redis_status = "unreachable"
    n8n_status = "configured" if settings.n8n_base_url else "missing"

    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unreachable"

    try:
        redis = Redis.from_url(settings.redis_url, socket_connect_timeout=0.5)
        redis.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "unreachable"

    return SettingsOverviewResponse(
        secrets=SecretStatus(
            openai_api_key_set=bool(settings.openai_api_key),
            n8n_api_key_set=bool(settings.n8n_api_key),
        ),
        environment=EnvironmentStatus(
            database=db_status,
            redis=redis_status,
            n8n=n8n_status,
        ),
        safety_controls=SafetyControls(
            max_retries=settings.max_retries,
            timeout_seconds=settings.request_timeout_seconds,
            max_budget_per_run_usd=settings.max_budget_per_run_usd,
        ),
    )
