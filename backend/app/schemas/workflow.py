from pydantic import BaseModel


class WorkflowCatalogItem(BaseModel):
    id: str
    slug: str
    name: str
    description: str
    category: str
    risk_level: str
    enabled: bool
    requires_approval: bool

    model_config = {"from_attributes": True}


class WorkflowCatalogResponse(BaseModel):
    items: list[WorkflowCatalogItem]
