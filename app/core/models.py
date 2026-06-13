from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class ToolType(str, Enum):
    WEB_SEARCH = "web_search"
    CODE_EXECUTION = "code_execution"
    TERMINAL = "terminal"
    FILE_OPERATIONS = "file_operations"

class LogStep(str, Enum):
    PLANNING = "planning"
    EXECUTION = "execution"
    WAITING = "waiting"
    OUTPUT = "output"
    ERROR = "error"

class Tool(BaseModel):
    id: str = Field(..., description="Unique ID of the tool")
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Function description of the tool")
    type: ToolType = Field(..., description="Category of the tool")
    is_active: bool = Field(True, description="Whether the tool is enabled")
    permissions: List[str] = Field(default_factory=list, description="Access permissions required")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Agent(BaseModel):
    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Display name of the agent")
    system_prompt: str = Field(..., description="System instructions guiding agent behavior")
    model_name: str = Field(..., description="Name of the LLM model to execute")
    provider: str = Field("ollama", description="LLM provider (e.g., ollama, openai, anthropic)")
    temperature: float = Field(0.2, description="Inference temperature")
    tool_ids: List[str] = Field(default_factory=list, description="List of tool IDs assigned to the agent")
    is_active: bool = Field(True, description="Is this agent enabled for execution")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Workspace(BaseModel):
    id: str = Field(..., description="Workspace ID")
    name: str = Field(..., description="Name of the workspace")
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuration parameters")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Session(BaseModel):
    id: str = Field(..., description="Session/Run identifier")
    agent_id: str = Field(..., description="ID of the executing agent")
    workspace_id: str = Field(..., description="ID of the active workspace")
    status: str = Field("running", description="Status of the session (running, completed, failed)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Log(BaseModel):
    id: str = Field(..., description="Unique log ID")
    session_id: str = Field(..., description="Session reference ID")
    step: LogStep = Field(..., description="Execution step phase (PLANNING, EXECUTION, etc.)")
    message: str = Field(..., description="Execution details or reasoning tokens")
    tokens_consumed: int = Field(0, description="Tokens consumed during this step")
    latency_ms: int = Field(0, description="Latency in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
