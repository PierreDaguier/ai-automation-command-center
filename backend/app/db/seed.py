from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.models import AuditEvent, User, UserRole, Workflow

DEFAULT_WORKFLOWS = [
    {
        "slug": "invoice-dispute-triage",
        "name": "Invoice Dispute Triage",
        "description": "Ingest disputes, classify intent, and route to finance ops.",
        "category": "finance",
        "risk_level": "medium",
        "requires_approval": False,
    },
    {
        "slug": "vendor-risk-escalation",
        "name": "Vendor Risk Escalation",
        "description": "Correlate vendor alerts, propose mitigation plan, and notify owners.",
        "category": "procurement",
        "risk_level": "high",
        "requires_approval": True,
    },
    {
        "slug": "lead-enrichment-and-routing",
        "name": "Lead Enrichment and Routing",
        "description": "Enhance inbound leads and assign account owner using routing policy.",
        "category": "revenue",
        "risk_level": "low",
        "requires_approval": False,
    },
    {
        "slug": "contract-renewal-safeguard",
        "name": "Contract Renewal Safeguard",
        "description": "Detect renewal windows and prepare decision packs for legal review.",
        "category": "legal",
        "risk_level": "high",
        "requires_approval": True,
    },
]


def seed_defaults(db: Session) -> None:
    admin = db.scalar(select(User).where(User.email == settings.default_admin_email))
    if not admin:
        admin = User(
            email=settings.default_admin_email,
            full_name="System Administrator",
            role=UserRole.admin,
            hashed_password=get_password_hash(settings.default_admin_password),
            is_active=True,
        )
        db.add(admin)
    else:
        admin.full_name = "System Administrator"
        admin.role = UserRole.admin
        admin.hashed_password = get_password_hash(settings.default_admin_password)
        admin.is_active = True

    operator = db.scalar(select(User).where(User.email == settings.default_operator_email))
    if not operator:
        operator = User(
            email=settings.default_operator_email,
            full_name="Operations Specialist",
            role=UserRole.operator,
            hashed_password=get_password_hash(settings.default_operator_password),
            is_active=True,
        )
        db.add(operator)
    else:
        operator.full_name = "Operations Specialist"
        operator.role = UserRole.operator
        operator.hashed_password = get_password_hash(settings.default_operator_password)
        operator.is_active = True

    workflows_exist = db.scalar(select(Workflow.id).limit(1))
    if not workflows_exist:
        db.add_all(Workflow(**workflow) for workflow in DEFAULT_WORKFLOWS)

    audit_exists = db.scalar(select(AuditEvent.id).limit(1))
    if not audit_exists:
        db.add(
            AuditEvent(
                actor="system",
                actor_role="service",
                action="bootstrap.seeded",
                entity_type="environment",
                entity_id="default",
                metadata_json={"workflows": len(DEFAULT_WORKFLOWS)},
            )
        )

    db.commit()
