from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.auth import limiter
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.observability import setup_metrics, setup_tracing
from app.db.base import Base
from app.db.seed import seed_defaults
from app.db.session import SessionLocal, engine
from app.schemas.common import HealthResponse

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Production-grade demo API for AI automation orchestration, approvals, and auditability."
    ),
)


def _rate_limiter_exception_handler(request: Request, exc: Exception) -> Response:
    if isinstance(exc, RateLimitExceeded):
        return _rate_limit_exceeded_handler(request, exc)
    raise exc


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limiter_exception_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_defaults(db)


setup_metrics(app)
setup_tracing(app, engine)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["health"], response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=settings.app_version)
