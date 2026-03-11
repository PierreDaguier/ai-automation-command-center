from fastapi import APIRouter

from app.api.v1 import agent, approvals, auth, system, triggers, workflows

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(workflows.router)
api_router.include_router(triggers.router)
api_router.include_router(agent.router)
api_router.include_router(approvals.router)
api_router.include_router(system.router)
