from fastapi import APIRouter

from app.api.v1 import auth, system, workflows

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(workflows.router)
api_router.include_router(system.router)
