import re
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.core.exceptions import SandboxViolationError

# List of blocked system commands/imports for quick local validation
BLOCKED_KEYWORDS = [
    r"__subclasses__",
    r"eval\(",
    r"exec\(",
    r"os\.system",
    r"os\.popen",
    r"subprocess\.",
    r"shutil\.",
    r"rm\s+-rf",
    r"mv\s+.*",
    r"chmod\s+",
    r"chown\s+",
    r"kill\s+-9",
    r"/etc/passwd",
    r"/etc/shadow",
    r"/dev/sda"
]

def validate_code_safety(code: str) -> None:
    """Performs static analysis on python code/commands to filter simple unsafe commands."""
    for pattern in BLOCKED_KEYWORDS:
        if re.search(pattern, code, re.IGNORECASE):
            raise SandboxViolationError(
                f"Blocked execution due to potentially malicious pattern matching: '{pattern}'"
            )

class BaseSandbox(ABC):
    """Abstract interface for executing code in a sandboxed environment."""

    @abstractmethod
    def execute_code(self, code: str, language: str = "python", timeout_sec: Optional[int] = None) -> Dict[str, Any]:
        """
        Executes a script and returns a dictionary with stdout, stderr, execution time, and exit code.
        """
        pass

    @abstractmethod
    def execute_command(self, command: str, timeout_sec: Optional[int] = None) -> Dict[str, Any]:
        """
        Executes a terminal/shell command and returns stdout, stderr, and exit code.
        """
        pass
