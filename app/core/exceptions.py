class AgentOSException(Exception):
    """Base exception class for all Agent OS custom exceptions."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class EntityNotFoundError(AgentOSException):
    """Raised when a requested resource (Agent, Tool, Workspace, Session) is not found."""
    def __init__(self, entity_type: str, entity_id: str):
        super().__init__(f"{entity_type} with ID '{entity_id}' not found.", status_code=404)

class ToolExecutionError(AgentOSException):
    """Raised when a tool fails to execute or returns an error."""
    def __init__(self, tool_name: str, reason: str):
        super().__init__(f"Tool '{tool_name}' execution failed: {reason}", status_code=422)

class SandboxViolationError(AgentOSException):
    """Raised when code execution violates security, sandboxing, or resource limits."""
    def __init__(self, reason: str):
        super().__init__(f"Sandbox violation: {reason}", status_code=403)

class OrchestrationError(AgentOSException):
    """Raised when the ReAct loop or Ollama connection fails."""
    def __init__(self, reason: str):
        super().__init__(f"Orchestration failure: {reason}", status_code=500)
