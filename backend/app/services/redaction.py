from collections.abc import Mapping
from typing import Any

SENSITIVE_PATTERNS = {
    "password",
    "secret",
    "token",
    "api_key",
    "authorization",
    "credit_card",
    "card_number",
    "ssn",
    "email",
    "phone",
}


def _looks_sensitive(key: str) -> bool:
    normalized = key.strip().lower()
    return any(pattern in normalized for pattern in SENSITIVE_PATTERNS)


def redact_payload(payload: Any) -> Any:
    if isinstance(payload, Mapping):
        redacted: dict[str, Any] = {}
        for key, value in payload.items():
            if _looks_sensitive(str(key)):
                redacted[str(key)] = "[REDACTED]"
            else:
                redacted[str(key)] = redact_payload(value)
        return redacted

    if isinstance(payload, list):
        return [redact_payload(item) for item in payload]

    return payload
