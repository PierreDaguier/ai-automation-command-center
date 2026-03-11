import httpx
import time

from app.core.config import settings


class N8NClient:
    def __init__(self) -> None:
        self.base_url = settings.n8n_base_url.rstrip("/")
        self.api_key = settings.n8n_api_key

    def trigger_workflow(self, workflow_slug: str, payload: dict) -> dict:
        if not self.base_url:
            return {
                "status": "simulated",
                "provider": "n8n",
                "workflow_slug": workflow_slug,
                "payload": payload,
            }

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-N8N-API-KEY"] = self.api_key

        attempts = settings.max_retries + 1
        last_error = ""

        for attempt in range(1, attempts + 1):
            try:
                response = httpx.post(
                    f"{self.base_url}/webhook/{workflow_slug}",
                    json=payload,
                    headers=headers,
                    timeout=settings.request_timeout_seconds,
                )
                response.raise_for_status()
                return {
                    "status": "triggered",
                    "result": response.json(),
                    "attempts": attempt,
                }
            except Exception as exc:
                last_error = str(exc)
                if attempt < attempts:
                    delay = settings.retry_backoff_seconds * (2 ** (attempt - 1))
                    time.sleep(delay)

        if settings.n8n_simulation_mode:
            return {
                "status": "simulated",
                "provider": "n8n",
                "workflow_slug": workflow_slug,
                "fallback_reason": last_error,
                "payload": payload,
                "attempts": attempts,
            }

        raise RuntimeError(f"n8n trigger failed after {attempts} attempts: {last_error}")
