from fastapi import APIRouter, Depends
from redis import Redis
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.config import settings
from app.db.models import UserRole
from app.db.session import get_db
from app.schemas.system import EnvironmentStatusResponse

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/environment-status", response_model=EnvironmentStatusResponse)
def environment_status(
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.admin, UserRole.operator)),
) -> EnvironmentStatusResponse:
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

    return EnvironmentStatusResponse(database=db_status, redis=redis_status, n8n=n8n_status)
