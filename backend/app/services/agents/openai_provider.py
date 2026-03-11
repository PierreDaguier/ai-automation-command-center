import json
from typing import Any

from openai import OpenAI

from app.core.config import settings
from app.schemas.agent import AgentExecutionRequest, AgentExecutionResult
from app.services.agents.base import AgentProvider


class OpenAIResponsesProvider(AgentProvider):
    name = "openai"

    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        self.client = OpenAI(api_key=settings.openai_api_key)

    @staticmethod
    def _to_openai_tools(request: AgentExecutionRequest) -> list[dict[str, Any]]:
        tools: list[dict[str, Any]] = []
        for tool in request.tools:
            properties: dict[str, Any] = {}
            required: list[str] = []
            for parameter in tool.parameters:
                properties[parameter.name] = {
                    "type": parameter.type,
                    "description": parameter.description,
                }
                if parameter.required:
                    required.append(parameter.name)

            tools.append(
                {
                    "type": "function",
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                }
            )
        return tools

    def execute(self, request: AgentExecutionRequest) -> AgentExecutionResult:
        tools = self._to_openai_tools(request)
        input_payload = {
            "prompt": request.prompt,
            "input": request.input_payload,
            "instructions": "Return structured JSON with summary and suggested_actions.",
        }

        request_payload: dict[str, Any] = {
            "model": request.model or settings.openai_model,
            "input": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "You are an enterprise operations agent. Prefer precise, auditable actions.",
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": json.dumps(input_payload)}],
                },
            ],
            "temperature": 0.2,
        }
        if tools:
            request_payload["tools"] = tools
            request_payload["tool_choice"] = "auto"

        responses_client: Any = self.client.responses
        response = responses_client.create(**request_payload)

        response_data = response.model_dump()
        tool_calls: list[dict[str, Any]] = []
        for item in response_data.get("output", []):
            if item.get("type") == "function_call":
                tool_calls.append(
                    {
                        "tool_name": item.get("name"),
                        "arguments": item.get("arguments"),
                    }
                )

        output_text = response_data.get("output_text") or ""
        parsed_output: dict[str, Any]
        try:
            parsed_output = json.loads(output_text) if output_text else {}
        except json.JSONDecodeError:
            parsed_output = {
                "summary": output_text,
                "suggested_actions": ["manual_review"],
            }

        usage = response_data.get("usage", {})
        input_tokens = int(usage.get("input_tokens", 0) or 0)
        output_tokens = int(usage.get("output_tokens", 0) or 0)

        # Conservative demo estimation; configurable at deployment time.
        estimated_cost = (input_tokens * 0.15 + output_tokens * 0.60) / 1_000_000

        return AgentExecutionResult(
            provider=self.name,
            model=request.model or settings.openai_model,
            output=parsed_output,
            tool_calls=tool_calls,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=round(estimated_cost, 6),
        )
