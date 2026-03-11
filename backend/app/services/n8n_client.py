import httpx

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

        try:
            response = httpx.post(
                f"{self.base_url}/webhook/{workflow_slug}",
                json=payload,
                headers=headers,
                timeout=10.0,
            )
            response.raise_for_status()
            return {"status": "triggered", "result": response.json()}
        except Exception as exc:
            return {
                "status": "simulated",
                "provider": "n8n",
                "workflow_slug": workflow_slug,
                "fallback_reason": str(exc),
                "payload": payload,
            }
