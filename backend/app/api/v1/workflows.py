from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import User, Workflow
from app.db.session import get_db
from app.schemas.workflow import WorkflowCatalogItem, WorkflowCatalogResponse

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/catalog", response_model=WorkflowCatalogResponse)
def workflow_catalog(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkflowCatalogResponse:
    del current_user
    rows = db.scalars(select(Workflow).order_by(Workflow.category, Workflow.name)).all()
    return WorkflowCatalogResponse(items=[WorkflowCatalogItem.model_validate(row) for row in rows])
