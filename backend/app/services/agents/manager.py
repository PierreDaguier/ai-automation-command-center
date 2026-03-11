from app.schemas.agent import AgentExecutionRequest, AgentExecutionResult
from app.services.agents.base import AgentProvider
from app.services.agents.mock_provider import MockAgentProvider
from app.services.agents.openai_provider import OpenAIResponsesProvider


class AgentService:
    def __init__(self, provider_hint: str | None = None) -> None:
        self.provider: AgentProvider

        if provider_hint == "mock":
            self.provider = MockAgentProvider()
        else:
            try:
                self.provider = OpenAIResponsesProvider()
            except Exception:
                self.provider = MockAgentProvider()

    @property
    def provider_name(self) -> str:
        return self.provider.name

    def execute(self, request: AgentExecutionRequest) -> AgentExecutionResult:
        return self.provider.execute(request)
