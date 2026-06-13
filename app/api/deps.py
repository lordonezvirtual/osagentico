from app.infrastructure.database import get_db, BaseDatabase
from app.infrastructure.vectordb import get_vector_db, BaseVectorDB
from app.services.sandbox import get_sandbox, BaseSandbox
from app.services.orchestrator import get_orchestrator, AgentOrchestrator

def get_db_dep() -> BaseDatabase:
    return get_db()

def get_vector_db_dep() -> BaseVectorDB:
    return get_vector_db()

def get_sandbox_dep() -> BaseSandbox:
    return get_sandbox()

def get_orchestrator_dep() -> AgentOrchestrator:
    return get_orchestrator()
