from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.db.models import AuditEvent, User
from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse, UserSummary

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("20/minute")
def login(
    request: Request,
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    token = create_access_token(subject=user.email, role=user.role.value, expires_delta=expires_delta)

    db.add(
        AuditEvent(
            actor=user.email,
            actor_role=user.role.value,
            action="auth.login",
            entity_type="user",
            entity_id=user.id,
            metadata_json={"method": "password"},
        )
    )
    db.commit()

    return TokenResponse(
        access_token=token,
        expires_in_seconds=int(expires_delta.total_seconds()),
    )


@router.get("/me", response_model=UserSummary)
def me(current_user: User = Depends(get_current_user)) -> UserSummary:
    return UserSummary.model_validate(current_user)
