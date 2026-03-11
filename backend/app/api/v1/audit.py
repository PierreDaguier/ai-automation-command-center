from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.models import AuditEvent, User, UserRole
from app.db.session import get_db
from app.schemas.audit import AuditTimelineItem, AuditTimelineResponse
from app.services.redaction import redact_payload

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/timeline", response_model=AuditTimelineResponse)
def timeline(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.operator)),
) -> AuditTimelineResponse:
    rows = db.scalars(select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit)).all()
    return AuditTimelineResponse(
        items=[
            AuditTimelineItem(
                id=row.id,
                actor=row.actor,
                actor_role=row.actor_role,
                action=row.action,
                entity_type=row.entity_type,
                entity_id=row.entity_id,
                metadata_json=redact_payload(row.metadata_json),
                created_at=row.created_at,
            )
            for row in rows
        ]
    )
