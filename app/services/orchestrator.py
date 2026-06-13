import time
import uuid
import re
import json
import logging
import asyncio
import httpx
from datetime import datetime
from typing import Dict, Any, List, Generator, AsyncGenerator
from app.config import settings
from app.core.models import Agent, Session, Log, LogStep, Tool
from app.infrastructure.database import get_db, BaseDatabase
from app.infrastructure.vectordb import get_vector_db, BaseVectorDB
from app.services.sandbox import get_sandbox, BaseSandbox
from app.services.telemetry import telemetry_manager

logger = logging.getLogger("orchestrator")

REACT_PROMPT_TEMPLATE = """You are an AI Agent operating within the Hermes Agent OS.
You have access to the following tools:
{tools_description}

Use the following format:
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Always start your responses with "Thought:".

Begin!
User Query: {query}
"""

class AgentOrchestrator:
    def __init__(self):
        self.db: BaseDatabase = get_db()
        self.vector_db: BaseVectorDB = get_vector_db()
        self.sandbox: BaseSandbox = get_sandbox()

    async def _mock_llm_react(self, query: str, session_id: str) -> AsyncGenerator[str, None]:
        """A simulated ReAct agent execution loop when Ollama is offline."""
        steps = [
            ("Thought: I need to analyze the user request and check local system status or files.", LogStep.PLANNING),
            ("Action: terminal\nAction Input: echo 'Hermes Agent OS Local Sandbox Active'", LogStep.EXECUTION),
            ("Observation: Hermes Agent OS Local Sandbox Active\n", LogStep.OUTPUT),
            ("Thought: The terminal is working correctly inside the sandbox. I can now provide the final answer.", LogStep.PLANNING),
            ("Final Answer: Local-first Agent OS Backend is successfully configured and running. Subprocesses, databases, and WebSockets are active.", LogStep.OUTPUT)
        ]

        for content, step_type in steps:
            # Simulate latency
            await asyncio.sleep(1.0)
            
            # Start step
            log_id = str(uuid.uuid4())
            log = Log(
                id=log_id,
                session_id=session_id,
                step=step_type,
                message=content,
                tokens_consumed=len(content.split()),
                latency_ms=1000,
                timestamp=datetime.utcnow()
            )
            await self.db.save_log(log)
            
            # Stream tokens word by word
            words = content.split(" ")
            for word in words:
                token = word + " "
                await telemetry_manager.stream_agent_event(session_id, "token", token)
                yield token
                await asyncio.sleep(0.05)
            
            # Stream step updates to frontend
            await telemetry_manager.stream_agent_event(
                session_id, 
                step_type.value, 
                content, 
                {"latency_ms": 1000, "tokens": len(words)}
            )

    async def run_tool(self, tool_id: str, tool_input: str) -> str:
        """Executes a tool within the safe local sandbox or fetches mock results."""
        try:
            tool = await self.db.get_tool(tool_id)
            if not tool.is_active:
                return f"Error: Tool '{tool_id}' is currently disabled."
        except Exception:
            return f"Error: Tool '{tool_id}' not found in registry."

        if tool_id == "code_execution":
            res = self.sandbox.execute_code(tool_input, language="python")
            return f"Exit Code: {res['exit_code']}\nStdout:\n{res['stdout']}\nStderr:\n{res['stderr']}"
        
        elif tool_id == "terminal":
            res = self.sandbox.execute_command(tool_input)
            return f"Exit Code: {res['exit_code']}\nStdout:\n{res['stdout']}\nStderr:\n{res['stderr']}"
        
        elif tool_id == "file_operations":
            # Simple wrapper to run safe python commands or parse files
            # For robustness, we will let it execute a shell command to list files or list it via Python
            cmd = f"python -c \"import os; print(os.listdir('.'))\""
            res = self.sandbox.execute_command(cmd)
            return res["stdout"]
        
        elif tool_id == "web_search":
            return f"Web Search Result for '{tool_input}': [Local Mock] Found Hermes OS repository and local-first FastAPI backend boilerplate setup guidelines."
        
        return f"Unknown tool execution: {tool_id}"

    async def orchestrate(self, agent_id: str, query: str, workspace_id: str) -> AsyncGenerator[str, None]:
        """Main ReAct reasoning and tool execution loop."""
        # 1. Fetch agent and create session
        agent = await self.db.get_agent(agent_id)
        session_id = str(uuid.uuid4())
        session = Session(
            id=session_id,
            agent_id=agent_id,
            workspace_id=workspace_id,
            status="running",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await self.db.save_session(session)

        # Notify start
        await telemetry_manager.stream_agent_event(session_id, "start", f"Orchestrating agent {agent.name}")

        # 2. Check if local Ollama service is reachable
        async with httpx.AsyncClient() as client:
            ollama_active = False
            try:
                resp = await client.get(settings.OLLAMA_URL)
                if resp.status_code == 200:
                    ollama_active = True
            except Exception:
                pass

        if not ollama_active:
            logger.warning("Local Ollama endpoint not reachable. Running ReAct loop simulation.")
            async for token in self._mock_llm_react(query, session_id):
                yield token
            
            # Update session status
            session.status = "completed"
            session.updated_at = datetime.utcnow()
            await self.db.save_session(session)
            return

        # 3. Real Ollama ReAct Execution Loop
        tools = []
        for t_id in agent.tool_ids:
            try:
                tools.append(await self.db.get_tool(t_id))
            except Exception:
                pass

        tools_description = "\n".join([f"- {t.id}: {t.description}" for t in tools])
        tool_names = ", ".join([t.id for t in tools])
        
        prompt = REACT_PROMPT_TEMPLATE.format(
            tools_description=tools_description,
            tool_names=tool_names,
            query=query
        )

        max_turns = 5
        turn = 0
        current_prompt = prompt

        while turn < max_turns:
            turn += 1
            start_time = time.time()
            llm_output = ""
            
            # Request token streaming from local Ollama
            try:
                payload = {
                    "model": agent.model_name,
                    "prompt": current_prompt,
                    "stream": True,
                    "options": {
                        "temperature": agent.temperature,
                        "stop": ["Observation:"]
                    }
                }
                
                # Stream logs
                await telemetry_manager.stream_agent_event(session_id, "thinking_start", f"Reasoning turn {turn}...")
                
                async with httpx.AsyncClient() as run_client:
                    async with run_client.stream(
                        "POST", 
                        f"{settings.OLLAMA_URL}/api/generate", 
                        json=payload,
                        timeout=httpx.Timeout(60.0)
                    ) as response:
                        if response.status_code != 200:
                            raise Exception(f"Ollama returned status {response.status_code}. Model '{agent.model_name}' may not be installed. Run 'ollama pull {agent.model_name}'.")
                        async for chunk in response.aiter_lines():
                            if not chunk:
                                continue
                            data = json.loads(chunk)
                            token = data.get("response", "")
                            llm_output += token
                            await telemetry_manager.stream_agent_event(session_id, "token", token)
                            yield token
                
            except Exception as e:
                err_msg = f"Ollama execution failed ({str(e)}). Falling back to ReAct loop simulation."
                logger.warning(err_msg)
                await telemetry_manager.stream_agent_event(session_id, "warning", err_msg)
                async for token in self._mock_llm_react(query, session_id):
                    yield token
                break

            latency_ms = int((time.time() - start_time) * 1000)
            tokens_count = len(llm_output.split())

            # Save planning trace
            log_id = str(uuid.uuid4())
            await self.db.save_log(Log(
                id=log_id,
                session_id=session_id,
                step=LogStep.PLANNING,
                message=llm_output,
                tokens_consumed=tokens_count,
                latency_ms=latency_ms,
                timestamp=datetime.utcnow()
            ))

            # Parse Action
            action_match = re.search(r"Action:\s*(.*)", llm_output)
            action_input_match = re.search(r"Action Input:\s*(.*)", llm_output)

            if action_match and action_input_match:
                tool_id = action_match.group(1).strip()
                tool_input = action_input_match.group(1).strip()

                await telemetry_manager.stream_agent_event(
                    session_id, 
                    "execution", 
                    f"Executing tool {tool_id} with input: {tool_input}"
                )

                # Run tool
                tool_start_time = time.time()
                observation = await self.run_tool(tool_id, tool_input)
                tool_latency = int((time.time() - tool_start_time) * 1000)

                # Save tool observation log
                await self.db.save_log(Log(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    step=LogStep.OUTPUT,
                    message=f"Tool: {tool_id}\nObservation:\n{observation}",
                    tokens_consumed=0,
                    latency_ms=tool_latency,
                    timestamp=datetime.utcnow()
                ))

                await telemetry_manager.stream_agent_event(
                    session_id, 
                    "waiting", 
                    observation,
                    {"latency_ms": tool_latency}
                )

                # Feed observation back to LLM context
                current_prompt += f"\n{llm_output}\nObservation: {observation}\n"

            elif "Final Answer:" in llm_output:
                final_answer = llm_output.split("Final Answer:")[-1].strip()
                await telemetry_manager.stream_agent_event(session_id, "output", final_answer)
                break
            else:
                # LLM finished without structured ReAct output
                await telemetry_manager.stream_agent_event(session_id, "output", llm_output)
                break

        # Update session status
        session.status = "completed"
        session.updated_at = datetime.utcnow()
        await self.db.save_session(session)
        await telemetry_manager.stream_agent_event(session_id, "end", "Execution complete.")


# Singleton orchestrator
_orchestrator = AgentOrchestrator()

def get_orchestrator() -> AgentOrchestrator:
    return _orchestrator
