from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    type: str = Field(default="string")
    description: str = Field(default="")
    required: bool = False


class ToolContract(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str
    parameters: list[ToolParameter] = Field(default_factory=list)


class AgentExecutionRequest(BaseModel):
    prompt: str = Field(min_length=5)
    input_payload: dict = Field(default_factory=dict)
    tools: list[ToolContract] = Field(default_factory=list)
    model: str | None = None
    provider: str | None = None


class AgentExecutionResult(BaseModel):
    provider: str
    model: str
    output: dict
    tool_calls: list[dict] = Field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0


class AgentTaskResponse(BaseModel):
    task_id: str
    run_id: str | None = None
    status: str
    result: AgentExecutionResult
