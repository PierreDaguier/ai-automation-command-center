from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.models import ActionLog, User, UserRole
from app.db.session import get_db
from app.schemas.logs import ActionLogItem, ActionLogResponse
from app.services.redaction import redact_payload

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/actions", response_model=ActionLogResponse)
def action_logs(
    run_id: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.operator)),
) -> ActionLogResponse:
    query = select(ActionLog).order_by(ActionLog.created_at.desc()).limit(limit)
    if run_id:
        query = query.where(ActionLog.run_id == run_id)

    rows = db.scalars(query).all()
    items = [
        ActionLogItem(
            id=row.id,
            run_id=row.run_id,
            action_type=row.action_type,
            target=row.target,
            status=row.status,
            details_json=redact_payload(row.details_json),
            created_at=row.created_at,
        )
        for row in rows
    ]
    return ActionLogResponse(items=items)
