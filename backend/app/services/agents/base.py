from abc import ABC, abstractmethod

from app.schemas.agent import AgentExecutionRequest, AgentExecutionResult


class AgentProvider(ABC):
    name: str

    @abstractmethod
    def execute(self, request: AgentExecutionRequest) -> AgentExecutionResult:
        raise NotImplementedError
