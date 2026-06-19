import json
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.config import settings
from app.core.models import Workspace, Agent, Tool, Session, Log
from app.core.exceptions import EntityNotFoundError

# Check for Firestore availability
try:
    from google.cloud import firestore
    firestore_available = True
except ImportError:
    firestore_available = False

# Check for Postgres availability
try:
    import psycopg2
    import psycopg2.extras
    postgres_available = True
except ImportError:
    postgres_available = False

class BaseDatabase(ABC):
    @abstractmethod
    async def get_workspace(self, workspace_id: str) -> Workspace: pass
    @abstractmethod
    async def save_workspace(self, workspace: Workspace) -> None: pass

    @abstractmethod
    async def get_agent(self, agent_id: str) -> Agent: pass
    @abstractmethod
    async def save_agent(self, agent: Agent) -> None: pass
    @abstractmethod
    async def list_agents(self) -> List[Agent]: pass

    @abstractmethod
    async def get_tool(self, tool_id: str) -> Tool: pass
    @abstractmethod
    async def save_tool(self, tool: Tool) -> None: pass
    @abstractmethod
    async def list_tools(self) -> List[Tool]: pass

    @abstractmethod
    async def get_session(self, session_id: str) -> Session: pass
    @abstractmethod
    async def save_session(self, session: Session) -> None: pass

    @abstractmethod
    async def save_log(self, log: Log) -> None: pass
    @abstractmethod
    async def list_logs(self, session_id: str) -> List[Log]: pass

    @abstractmethod
    async def list_services(self) -> List[Dict[str, Any]]: pass
    @abstractmethod
    async def get_service(self, service_id: str) -> Optional[Dict[str, Any]]: pass
    @abstractmethod
    async def save_service(self, service_id: str, status: str) -> None: pass


class SQLiteDatabase(BaseDatabase):
    def __init__(self, db_url: str):
        # sqlite:///./agent_os_local.db -> ./agent_os_local.db
        self.db_path = db_url.replace("sqlite:///", "")
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workspaces (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    config TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    system_prompt TEXT,
                    model_name TEXT,
                    provider TEXT,
                    temperature REAL,
                    tool_ids TEXT,
                    is_active INTEGER,
                    created_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tools (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    type TEXT,
                    is_active INTEGER,
                    permissions TEXT,
                    created_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT,
                    workspace_id TEXT,
                    status TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    step TEXT,
                    message TEXT,
                    tokens_consumed INTEGER,
                    latency_ms INTEGER,
                    timestamp TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS services (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    port INTEGER,
                    status TEXT,
                    updated_at TEXT
                )
            """)
            conn.commit()

            # Seed default tools if empty
            cursor.execute("SELECT COUNT(*) FROM tools")
            if cursor.fetchone()[0] == 0:
                self._seed_default_tools(conn)

            # Seed default services if empty
            cursor.execute("SELECT COUNT(*) FROM services")
            if cursor.fetchone()[0] == 0:
                self._seed_default_services(conn)

    def _seed_default_tools(self, conn):
        default_tools = [
            ("web_search", "Web Search", "Search the web for up to date information", "web_search", 1, "[]", datetime.utcnow().isoformat()),
            ("code_execution", "Code Execution", "Run python scripts inside a safe sandbox environment", "code_execution", 1, "[]", datetime.utcnow().isoformat()),
            ("terminal", "Terminal Exec", "Execute commands in a sandboxed system shell", "terminal", 1, "[]", datetime.utcnow().isoformat()),
            ("file_operations", "File Operations", "Read, write, list files under the workspace directory", "file_operations", 1, "[]", datetime.utcnow().isoformat())
        ]
        conn.executemany(
            "INSERT INTO tools (id, name, description, type, is_active, permissions, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            default_tools
        )
        conn.commit()

    async def get_workspace(self, workspace_id: str) -> Workspace:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM workspaces WHERE id = ?", (workspace_id,)).fetchone()
            if not row:
                raise EntityNotFoundError("Workspace", workspace_id)
            return Workspace(
                id=row["id"],
                name=row["name"],
                config=json.loads(row["config"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"])
            )

    async def save_workspace(self, workspace: Workspace) -> None:
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO workspaces (id, name, config, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (workspace.id, workspace.name, json.dumps(workspace.config), workspace.created_at.isoformat(), workspace.updated_at.isoformat())
            )
            conn.commit()

    async def get_agent(self, agent_id: str) -> Agent:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM agents WHERE id = ?", (agent_id,)).fetchone()
            if not row:
                raise EntityNotFoundError("Agent", agent_id)
            return Agent(
                id=row["id"],
                name=row["name"],
                system_prompt=row["system_prompt"],
                model_name=row["model_name"],
                provider=row["provider"],
                temperature=row["temperature"],
                tool_ids=json.loads(row["tool_ids"]),
                is_active=bool(row["is_active"]),
                created_at=datetime.fromisoformat(row["created_at"])
            )

    async def save_agent(self, agent: Agent) -> None:
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO agents (id, name, system_prompt, model_name, provider, temperature, tool_ids, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (agent.id, agent.name, agent.system_prompt, agent.model_name, agent.provider, agent.temperature, json.dumps(agent.tool_ids), 1 if agent.is_active else 0, agent.created_at.isoformat())
            )
            conn.commit()

    async def list_agents(self) -> List[Agent]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM agents").fetchall()
            return [
                Agent(
                    id=row["id"],
                    name=row["name"],
                    system_prompt=row["system_prompt"],
                    model_name=row["model_name"],
                    provider=row["provider"],
                    temperature=row["temperature"],
                    tool_ids=json.loads(row["tool_ids"]),
                    is_active=bool(row["is_active"]),
                    created_at=datetime.fromisoformat(row["created_at"])
                ) for row in rows
            ]

    async def get_tool(self, tool_id: str) -> Tool:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM tools WHERE id = ?", (tool_id,)).fetchone()
            if not row:
                raise EntityNotFoundError("Tool", tool_id)
            return Tool(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                type=row["type"],
                is_active=bool(row["is_active"]),
                permissions=json.loads(row["permissions"]),
                created_at=datetime.fromisoformat(row["created_at"])
            )

    async def save_tool(self, tool: Tool) -> None:
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO tools (id, name, description, type, is_active, permissions, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (tool.id, tool.name, tool.description, tool.type, 1 if tool.is_active else 0, json.dumps(tool.permissions), tool.created_at.isoformat())
            )
            conn.commit()

    async def list_tools(self) -> List[Tool]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM tools").fetchall()
            return [
                Tool(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    type=row["type"],
                    is_active=bool(row["is_active"]),
                    permissions=json.loads(row["permissions"]),
                    created_at=datetime.fromisoformat(row["created_at"])
                ) for row in rows
            ]

    async def get_session(self, session_id: str) -> Session:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
            if not row:
                raise EntityNotFoundError("Session", session_id)
            return Session(
                id=row["id"],
                agent_id=row["agent_id"],
                workspace_id=row["workspace_id"],
                status=row["status"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"])
            )

    async def save_session(self, session: Session) -> None:
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO sessions (id, agent_id, workspace_id, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (session.id, session.agent_id, session.workspace_id, session.status, session.created_at.isoformat(), session.updated_at.isoformat())
            )
            conn.commit()

    async def save_log(self, log: Log) -> None:
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO logs (id, session_id, step, message, tokens_consumed, latency_ms, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (log.id, log.session_id, log.step.value, log.message, log.tokens_consumed, log.latency_ms, log.timestamp.isoformat())
            )
            conn.commit()

    async def list_logs(self, session_id: str) -> List[Log]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM logs WHERE session_id = ? ORDER BY timestamp ASC", (session_id,)).fetchall()
            return [
                Log(
                    id=row["id"],
                    session_id=row["session_id"],
                    step=row["step"],
                    message=row["message"],
                    tokens_consumed=row["tokens_consumed"],
                    latency_ms=row["latency_ms"],
                    timestamp=datetime.fromisoformat(row["timestamp"])
                ) for row in rows
            ]

    def _seed_default_services(self, conn):
        default_services = [
            ("hermes-agent", "Hermes Agent", "Núcleo autónomo de toma de decisiones vía API y CLI.", 8081, "inactive", datetime.utcnow().isoformat()),
            ("hermes-desktop", "Hermes Desktop", "Entorno de ejecución local con acceso a sistema de archivos y terminal.", 8082, "active", datetime.utcnow().isoformat()),
            ("hermes-workspace", "Hermes Workspace", "Espacio de trabajo compartido en la nube con repositorios y directorios aislados.", 8083, "inactive", datetime.utcnow().isoformat()),
            ("n8n", "n8n Automation", "Automatización de flujos de trabajo conectando nodos y APIs de terceros.", 5678, "inactive", datetime.utcnow().isoformat()),
            ("openclaw", "OpenClaw / OpenHands", "Agente desarrollador autónomo que escribe código y ejecuta comandos en sandbox.", 8080, "inactive", datetime.utcnow().isoformat()),
            ("crewai", "CrewAI Framework", "Orquestador de equipos de agentes AI colaborativos con roles definidos.", 8010, "inactive", datetime.utcnow().isoformat()),
            ("autogpt", "AutoGPT Node", "Agente autónomo de bucle continuo para resolución de objetivos complejos.", 8012, "inactive", datetime.utcnow().isoformat()),
            ("langflow", "Langflow UI", "Constructor visual de flujos de trabajo e interfaces gráficas RAG.", 7860, "inactive", datetime.utcnow().isoformat()),
            ("autogen", "Microsoft AutoGen", "Framework multi-agente para configurar flujos conversacionales de resolución de tareas.", 8015, "inactive", datetime.utcnow().isoformat()),
            ("langgraph", "LangGraph Nodes", "Orquestación cíclica y persistente de agentes complejos basada en grafos.", 8016, "inactive", datetime.utcnow().isoformat()),
            ("devika", "Devika Agent", "Asistente de codificación y desarrollo de software autónomo open-source.", 8018, "inactive", datetime.utcnow().isoformat()),
            ("chatdev", "ChatDev Virtual", "Entorno virtual simulado para creación cooperativa de software mediante agentes.", 8020, "inactive", datetime.utcnow().isoformat())
        ]
        conn.executemany(
            "INSERT INTO services (id, name, description, port, status, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            default_services
        )
        conn.commit()

    async def list_services(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM services").fetchall()
            return [dict(row) for row in rows]

    async def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM services WHERE id = ?", (service_id,)).fetchone()
            return dict(row) if row else None

    async def save_service(self, service_id: str, status: str) -> None:
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE services SET status = ?, updated_at = ? WHERE id = ?",
                (status, datetime.utcnow().isoformat(), service_id)
            )
            conn.commit()


class FirestoreDatabase(BaseDatabase):
    def __init__(self, project_id: Optional[str] = None, credentials_path: Optional[str] = None):
        if not firestore_available:
            raise ImportError("Firestore client library 'google-cloud-firestore' not installed.")
        
        # Initialize firestore client using ADC or explicit credentials
        if credentials_path:
            self.db = firestore.Client.from_service_account_json(credentials_path)
        else:
            self.db = firestore.Client(project=project_id)

    async def get_workspace(self, workspace_id: str) -> Workspace:
        doc = self.db.collection("workspaces").document(workspace_id).get()
        if not doc.exists:
            raise EntityNotFoundError("Workspace", workspace_id)
        data = doc.to_dict()
        return Workspace(**data)

    async def save_workspace(self, workspace: Workspace) -> None:
        # Pydantic serialization
        self.db.collection("workspaces").document(workspace.id).set(workspace.dict())

    async def get_agent(self, agent_id: str) -> Agent:
        doc = self.db.collection("agents").document(agent_id).get()
        if not doc.exists:
            raise EntityNotFoundError("Agent", agent_id)
        return Agent(**doc.to_dict())

    async def save_agent(self, agent: Agent) -> None:
        self.db.collection("agents").document(agent.id).set(agent.dict())

    async def list_agents(self) -> List[Agent]:
        docs = self.db.collection("agents").stream()
        return [Agent(**doc.to_dict()) for doc in docs]

    async def get_tool(self, tool_id: str) -> Tool:
        doc = self.db.collection("tools").document(tool_id).get()
        if not doc.exists:
            raise EntityNotFoundError("Tool", tool_id)
        return Tool(**doc.to_dict())

    async def save_tool(self, tool: Tool) -> None:
        self.db.collection("tools").document(tool.id).set(tool.dict())

    async def list_tools(self) -> List[Tool]:
        docs = self.db.collection("tools").stream()
        return [Tool(**doc.to_dict()) for doc in docs]

    async def get_session(self, session_id: str) -> Session:
        doc = self.db.collection("sessions").document(session_id).get()
        if not doc.exists:
            raise EntityNotFoundError("Session", session_id)
        return Session(**doc.to_dict())

    async def save_session(self, session: Session) -> None:
        self.db.collection("sessions").document(session.id).set(session.dict())

    async def save_log(self, log: Log) -> None:
        # Save nested or direct collections. Logs are nested under session documents for query optimization.
        self.db.collection("sessions").document(log.session_id).collection("logs").document(log.id).set(log.dict())

    async def list_logs(self, session_id: str) -> List[Log]:
        docs = self.db.collection("sessions").document(session_id).collection("logs").order_by("timestamp").stream()
        return [Log(**doc.to_dict()) for doc in docs]

    async def list_services(self) -> List[Dict[str, Any]]:
        docs = list(self.db.collection("services").stream())
        if not docs:
            # Seed default services
            default_services = [
                {"id": "hermes-agent", "name": "Hermes Agent", "description": "Núcleo autónomo de toma de decisiones vía API y CLI.", "port": 8081, "status": "inactive", "updated_at": datetime.utcnow().isoformat()},
                {"id": "hermes-desktop", "name": "Hermes Desktop", "description": "Entorno de ejecución local con acceso a sistema de archivos y terminal.", "port": 8082, "status": "active", "updated_at": datetime.utcnow().isoformat()},
                {"id": "hermes-workspace", "name": "Hermes Workspace", "description": "Espacio de trabajo compartido en la nube con repositorios y directorios aislados.", "port": 8083, "status": "inactive", "updated_at": datetime.utcnow().isoformat()},
                {"id": "n8n", "name": "n8n Automation", "description": "Automatización de flujos de trabajo conectando nodos y APIs de terceros.", "port": 5678, "status": "inactive", "updated_at": datetime.utcnow().isoformat()},
                {"id": "openclaw", "name": "OpenClaw / OpenHands", "description": "Agente desarrollador autónomo que escribe código y ejecuta comandos en sandbox.", "port": 8080, "status": "inactive", "updated_at": datetime.utcnow().isoformat()},
                {"id": "crewai", "name": "CrewAI Framework", "description": "Orquestador de equipos de agentes AI colaborativos con roles definidos.", "port": 8010, "status": "inactive", "updated_at": datetime.utcnow().isoformat()},
                {"id": "autogpt", "name": "AutoGPT Node", "description": "Agente autónomo de bucle continuo para resolución de objetivos complejos.", "port": 8012, "status": "inactive", "updated_at": datetime.utcnow().isoformat()},
                {"id": "langflow", "name": "Langflow UI", "description": "Constructor visual de flujos de trabajo e interfaces gráficas RAG.", "port": 7860, "status": "inactive", "updated_at": datetime.utcnow().isoformat()},
                {"id": "autogen", "name": "Microsoft AutoGen", "description": "Framework multi-agente para configurar flujos conversacionales de resolución de tareas.", "port": 8015, "status": "inactive", "updated_at": datetime.utcnow().isoformat()},
                {"id": "langgraph", "name": "LangGraph Nodes", "description": "Orquestación cíclica y persistente de agentes complejos basada en grafos.", "port": 8016, "status": "inactive", "updated_at": datetime.utcnow().isoformat()},
                {"id": "devika", "name": "Devika Agent", "description": "Asistente de codificación y desarrollo de software autónomo open-source.", "port": 8018, "status": "inactive", "updated_at": datetime.utcnow().isoformat()},
                {"id": "chatdev", "name": "ChatDev Virtual", "description": "Entorno virtual simulado para creación cooperativa de software mediante agentes.", "port": 8020, "status": "inactive", "updated_at": datetime.utcnow().isoformat()}
            ]
            for srv in default_services:
                self.db.collection("services").document(srv["id"]).set(srv)
            docs = list(self.db.collection("services").stream())
        return [doc.to_dict() for doc in docs]

    async def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        doc = self.db.collection("services").document(service_id).get()
        return doc.to_dict() if doc.exists else None

    async def save_service(self, service_id: str, status: str) -> None:
        self.db.collection("services").document(service_id).update({
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        })


# Singleton instance selector based on DB_MODE
_db_instance: Optional[BaseDatabase] = None

class PostgresDatabase(BaseDatabase):
    def __init__(self, db_url: str):
        if not postgres_available:
            raise ImportError("PostgreSQL client library 'psycopg2-binary' not installed.")
        self.db_url = db_url
        self._init_db()

    def _get_conn(self):
        return psycopg2.connect(self.db_url)

    def _init_db(self):
        with self._get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS workspaces (
                        id VARCHAR(255) PRIMARY KEY,
                        name VARCHAR(255),
                        config TEXT,
                        created_at VARCHAR(255),
                        updated_at VARCHAR(255)
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS agents (
                        id VARCHAR(255) PRIMARY KEY,
                        name VARCHAR(255),
                        system_prompt TEXT,
                        model_name VARCHAR(255),
                        provider VARCHAR(255),
                        temperature DOUBLE PRECISION,
                        tool_ids TEXT,
                        is_active BOOLEAN,
                        created_at VARCHAR(255)
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tools (
                        id VARCHAR(255) PRIMARY KEY,
                        name VARCHAR(255),
                        description TEXT,
                        type VARCHAR(255),
                        is_active BOOLEAN,
                        permissions TEXT,
                        created_at VARCHAR(255)
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id VARCHAR(255) PRIMARY KEY,
                        agent_id VARCHAR(255),
                        workspace_id VARCHAR(255),
                        status VARCHAR(255),
                        created_at VARCHAR(255),
                        updated_at VARCHAR(255)
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS logs (
                        id VARCHAR(255) PRIMARY KEY,
                        session_id VARCHAR(255),
                        step VARCHAR(255),
                        message TEXT,
                        tokens_consumed INTEGER,
                        latency_ms INTEGER,
                        timestamp VARCHAR(255)
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS services (
                        id VARCHAR(255) PRIMARY KEY,
                        name VARCHAR(255),
                        description TEXT,
                        port INTEGER,
                        status VARCHAR(255),
                        updated_at VARCHAR(255)
                    )
                """)
                conn.commit()

                # Seed default tools if empty
                cursor.execute("SELECT COUNT(*) FROM tools")
                if cursor.fetchone()[0] == 0:
                    self._seed_default_tools(conn)

                # Seed default services if empty
                cursor.execute("SELECT COUNT(*) FROM services")
                if cursor.fetchone()[0] == 0:
                    self._seed_default_services(conn)

    def _seed_default_tools(self, conn):
        default_tools = [
            ("web_search", "Web Search", "Search the web for up to date information", "web_search", True, "[]", datetime.utcnow().isoformat()),
            ("code_execution", "Code Execution", "Run python scripts inside a safe sandbox environment", "code_execution", True, "[]", datetime.utcnow().isoformat()),
            ("terminal", "Terminal Exec", "Execute commands in a sandboxed system shell", "terminal", True, "[]", datetime.utcnow().isoformat()),
            ("file_operations", "File Operations", "Read, write, list files under the workspace directory", "file_operations", True, "[]", datetime.utcnow().isoformat())
        ]
        with conn.cursor() as cursor:
            for tool_id, name, desc, t_type, is_active, perms, created in default_tools:
                cursor.execute(
                    """
                    INSERT INTO tools (id, name, description, type, is_active, permissions, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (tool_id, name, desc, t_type, is_active, perms, created)
                )
            conn.commit()

    async def get_workspace(self, workspace_id: str) -> Workspace:
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM workspaces WHERE id = %s", (workspace_id,))
                row = cursor.fetchone()
                if not row:
                    raise EntityNotFoundError("Workspace", workspace_id)
                return Workspace(
                    id=row["id"],
                    name=row["name"],
                    config=json.loads(row["config"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"])
                )

    async def save_workspace(self, workspace: Workspace) -> None:
        with self._get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO workspaces (id, name, config, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        config = EXCLUDED.config,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (workspace.id, workspace.name, json.dumps(workspace.config), workspace.created_at.isoformat(), workspace.updated_at.isoformat())
                )
                conn.commit()

    async def get_agent(self, agent_id: str) -> Agent:
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM agents WHERE id = %s", (agent_id,))
                row = cursor.fetchone()
                if not row:
                    raise EntityNotFoundError("Agent", agent_id)
                return Agent(
                    id=row["id"],
                    name=row["name"],
                    system_prompt=row["system_prompt"],
                    model_name=row["model_name"],
                    provider=row["provider"],
                    temperature=row["temperature"],
                    tool_ids=json.loads(row["tool_ids"]),
                    is_active=bool(row["is_active"]),
                    created_at=datetime.fromisoformat(row["created_at"])
                )

    async def save_agent(self, agent: Agent) -> None:
        with self._get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO agents (id, name, system_prompt, model_name, provider, temperature, tool_ids, is_active, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        system_prompt = EXCLUDED.system_prompt,
                        model_name = EXCLUDED.model_name,
                        provider = EXCLUDED.provider,
                        temperature = EXCLUDED.temperature,
                        tool_ids = EXCLUDED.tool_ids,
                        is_active = EXCLUDED.is_active
                    """,
                    (agent.id, agent.name, agent.system_prompt, agent.model_name, agent.provider, agent.temperature, json.dumps(agent.tool_ids), agent.is_active, agent.created_at.isoformat())
                )
                conn.commit()

    async def list_agents(self) -> List[Agent]:
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM agents")
                rows = cursor.fetchall()
                return [
                    Agent(
                        id=row["id"],
                        name=row["name"],
                        system_prompt=row["system_prompt"],
                        model_name=row["model_name"],
                        provider=row["provider"],
                        temperature=row["temperature"],
                        tool_ids=json.loads(row["tool_ids"]),
                        is_active=bool(row["is_active"]),
                        created_at=datetime.fromisoformat(row["created_at"])
                    ) for row in rows
                ]

    async def get_tool(self, tool_id: str) -> Tool:
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM tools WHERE id = %s", (tool_id,))
                row = cursor.fetchone()
                if not row:
                    raise EntityNotFoundError("Tool", tool_id)
                return Tool(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    type=row["type"],
                    is_active=bool(row["is_active"]),
                    permissions=json.loads(row["permissions"]),
                    created_at=datetime.fromisoformat(row["created_at"])
                )

    async def save_tool(self, tool: Tool) -> None:
        with self._get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO tools (id, name, description, type, is_active, permissions, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        type = EXCLUDED.type,
                        is_active = EXCLUDED.is_active,
                        permissions = EXCLUDED.permissions
                    """,
                    (tool.id, tool.name, tool.description, tool.type, tool.is_active, json.dumps(tool.permissions), tool.created_at.isoformat())
                )
                conn.commit()

    async def list_tools(self) -> List[Tool]:
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM tools")
                rows = cursor.fetchall()
                return [
                    Tool(
                        id=row["id"],
                        name=row["name"],
                        description=row["description"],
                        type=row["type"],
                        is_active=bool(row["is_active"]),
                        permissions=json.loads(row["permissions"]),
                        created_at=datetime.fromisoformat(row["created_at"])
                    ) for row in rows
                ]

    async def get_session(self, session_id: str) -> Session:
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM sessions WHERE id = %s", (session_id,))
                row = cursor.fetchone()
                if not row:
                    raise EntityNotFoundError("Session", session_id)
                return Session(
                    id=row["id"],
                    agent_id=row["agent_id"],
                    workspace_id=row["workspace_id"],
                    status=row["status"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"])
                )

    async def save_session(self, session: Session) -> None:
        with self._get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO sessions (id, agent_id, workspace_id, status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        status = EXCLUDED.status,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (session.id, session.agent_id, session.workspace_id, session.status, session.created_at.isoformat(), session.updated_at.isoformat())
                )
                conn.commit()

    async def save_log(self, log: Log) -> None:
        with self._get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO logs (id, session_id, step, message, tokens_consumed, latency_ms, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        message = EXCLUDED.message,
                        tokens_consumed = EXCLUDED.tokens_consumed,
                        latency_ms = EXCLUDED.latency_ms
                    """,
                    (log.id, log.session_id, log.step.value, log.message, log.tokens_consumed, log.latency_ms, log.timestamp.isoformat())
                )
                conn.commit()

    async def list_logs(self, session_id: str) -> List[Log]:
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM logs WHERE session_id = %s ORDER BY timestamp ASC", (session_id,))
                rows = cursor.fetchall()
                return [
                    Log(
                        id=row["id"],
                        session_id=row["session_id"],
                        step=row["step"],
                        message=row["message"],
                        tokens_consumed=row["tokens_consumed"],
                        latency_ms=row["latency_ms"],
                        timestamp=datetime.fromisoformat(row["timestamp"])
                    ) for row in rows
                ]

    def _seed_default_services(self, conn):
        default_services = [
            ("hermes-agent", "Hermes Agent", "Núcleo autónomo de toma de decisiones vía API y CLI.", 8081, "inactive", datetime.utcnow().isoformat()),
            ("hermes-desktop", "Hermes Desktop", "Entorno de ejecución local con acceso a sistema de archivos y terminal.", 8082, "active", datetime.utcnow().isoformat()),
            ("hermes-workspace", "Hermes Workspace", "Espacio de trabajo compartido en la nube con repositorios y directorios aislados.", 8083, "inactive", datetime.utcnow().isoformat()),
            ("n8n", "n8n Automation", "Automatización de flujos de trabajo conectando nodos y APIs de terceros.", 5678, "inactive", datetime.utcnow().isoformat()),
            ("openclaw", "OpenClaw / OpenHands", "Agente desarrollador autónomo que escribe código y ejecuta comandos en sandbox.", 8080, "inactive", datetime.utcnow().isoformat()),
            ("crewai", "CrewAI Framework", "Orquestador de equipos de agentes AI colaborativos con roles definidos.", 8010, "inactive", datetime.utcnow().isoformat()),
            ("autogpt", "AutoGPT Node", "Agente autónomo de bucle continuo para resolución de objetivos complejos.", 8012, "inactive", datetime.utcnow().isoformat()),
            ("langflow", "Langflow UI", "Constructor visual de flujos de trabajo e interfaces gráficas RAG.", 7860, "inactive", datetime.utcnow().isoformat()),
            ("autogen", "Microsoft AutoGen", "Framework multi-agente para configurar flujos conversacionales de resolución de tareas.", 8015, "inactive", datetime.utcnow().isoformat()),
            ("langgraph", "LangGraph Nodes", "Orquestación cíclica y persistente de agentes complejos basada en grafos.", 8016, "inactive", datetime.utcnow().isoformat()),
            ("devika", "Devika Agent", "Asistente de codificación y desarrollo de software autónomo open-source.", 8018, "inactive", datetime.utcnow().isoformat()),
            ("chatdev", "ChatDev Virtual", "Entorno virtual simulado para creación cooperativa de software mediante agentes.", 8020, "inactive", datetime.utcnow().isoformat())
        ]
        with conn.cursor() as cursor:
            for s_id, name, desc, port, status, updated in default_services:
                cursor.execute(
                    """
                    INSERT INTO services (id, name, description, port, status, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (s_id, name, desc, port, status, updated)
                )
            conn.commit()

    async def list_services(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM services")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM services WHERE id = %s", (service_id,))
                row = cursor.fetchone()
                return dict(row) if row else None

    async def save_service(self, service_id: str, status: str) -> None:
        with self._get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE services SET status = %s, updated_at = %s WHERE id = %s",
                    (status, datetime.utcnow().isoformat(), service_id)
                )
                conn.commit()

def get_db() -> BaseDatabase:
    global _db_instance
    if _db_instance is None:
        if settings.DB_MODE == "firebase":
            _db_instance = FirestoreDatabase(
                project_id=settings.FIREBASE_PROJECT_ID,
                credentials_path=settings.FIREBASE_CREDENTIALS_PATH
            )
        elif settings.DB_MODE == "postgres":
            _db_instance = PostgresDatabase(settings.POSTGRES_URL)
        else:
            _db_instance = SQLiteDatabase(settings.SQLITE_URL)
    return _db_instance
