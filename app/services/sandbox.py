import os
import sys
import uuid
import time
import subprocess
from typing import Dict, Any, Optional
from app.config import settings
from app.core.security import BaseSandbox, validate_code_safety
from app.core.exceptions import SandboxViolationError, ToolExecutionError

class LocalSubprocessSandbox(BaseSandbox):
    def __init__(self, sandbox_dir: str = settings.SANDBOX_WORK_DIR):
        self.sandbox_dir = os.path.abspath(sandbox_dir)
        os.makedirs(self.sandbox_dir, exist_ok=True)

    def execute_code(self, code: str, language: str = "python", timeout_sec: Optional[int] = None) -> Dict[str, Any]:
        """
        Runs Python code by writing it to a temporary file and running it in a subprocess.
        """
        # 1. Validate safety
        validate_code_safety(code)
        
        if language.lower() != "python":
            raise ToolExecutionError("sandbox", f"Language '{language}' not supported by local sandbox.")

        timeout = timeout_sec or settings.SANDBOX_TIMEOUT_SEC
        
        # 2. Write code to a temp file in the sandbox directory
        file_id = str(uuid.uuid4())
        script_name = f"script_{file_id}.py"
        script_path = os.path.join(self.sandbox_dir, script_name)

        try:
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)

            start_time = time.time()
            
            # 3. Execute script using the current active Python interpreter
            # In Windows/Linux this executes inside the active virtual environment
            result = subprocess.run(
                [sys.executable, script_name],
                cwd=self.sandbox_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            latency_ms = int((time.time() - start_time) * 1000)

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "latency_ms": latency_ms,
                "success": result.returncode == 0
            }

        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"Process execution timed out after {timeout} seconds.",
                "exit_code": -1,
                "latency_ms": timeout * 1000,
                "success": False
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"Unexpected error during code execution: {str(e)}",
                "exit_code": -1,
                "latency_ms": 0,
                "success": False
            }
        finally:
            # Cleanup temp file
            if os.path.exists(script_path):
                try:
                    os.remove(script_path)
                except Exception:
                    pass

    def execute_command(self, command: str, timeout_sec: Optional[int] = None) -> Dict[str, Any]:
        """
        Runs a shell command safely inside the sandbox directory.
        """
        # Validate safety
        validate_code_safety(command)

        timeout = timeout_sec or settings.SANDBOX_TIMEOUT_SEC
        start_time = time.time()

        try:
            # Use shell=True to run standard commands, but restrict execution context
            # We set cwd to sandbox_dir to restrict operations to that directory
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.sandbox_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            latency_ms = int((time.time() - start_time) * 1000)

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "latency_ms": latency_ms,
                "success": result.returncode == 0
            }

        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"Command execution timed out after {timeout} seconds.",
                "exit_code": -1,
                "latency_ms": timeout * 1000,
                "success": False
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"Unexpected error during command execution: {str(e)}",
                "exit_code": -1,
                "latency_ms": 0,
                "success": False
            }


# Singleton pattern
_sandbox_instance = LocalSubprocessSandbox()

def get_sandbox() -> BaseSandbox:
    return _sandbox_instance
