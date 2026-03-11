import hashlib
import hmac

from fastapi import HTTPException, status

from app.core.config import settings


def payload_hash(payload_raw: bytes) -> str:
    return hashlib.sha256(payload_raw).hexdigest()


def verify_webhook_signature(payload_raw: bytes, signature: str | None) -> None:
    if not signature:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing signature")

    expected = hmac.new(
        settings.webhook_signing_secret.encode("utf-8"),
        payload_raw,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")
