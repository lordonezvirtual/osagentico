import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.v1.agent import router as agent_router
from app.api.v1.tools import router as tools_router
from app.api.v1.services import router as services_router
from app.api.v1.telemetry import router as telemetry_router
from app.services.telemetry import telemetry_manager
from app.infrastructure.database import get_db
from app.core.models import Agent, Workspace
from app.core.exceptions import AgentOSException

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Actions ---
    logger.info("Starting Hermes Agent OS Core Backend...")
    
    # 1. Start Telemetry hardware polling
    await telemetry_manager.start_metrics_loop()
    
    # 2. Bootstrapping Default Agent and Workspace for instant local development
    try:
        db = get_db()
        
        # Check and seed default workspace
        try:
            await db.get_workspace("default_workspace")
            logger.info("Default workspace already exists.")
        except Exception:
            logger.info("Seeding default workspace...")
            await db.save_workspace(Workspace(
                id="default_workspace",
                name="Hermes Default Workspace",
                config={}
            ))

        # Check and seed default agent
        try:
            await db.get_agent("hermes_coder")
            logger.info("Default agent 'hermes_coder' already exists.")
        except Exception:
            logger.info("Seeding default agent 'hermes_coder'...")
            await db.save_agent(Agent(
                id="hermes_coder",
                name="Hermes Coder Agent",
                system_prompt=(
                    "You are a helpful coding assistant. You use the code_execution "
                    "tool to run Python scripts, and terminal to execute shell commands "
                    "when needed to solve code problems. Always think step by step."
                ),
                model_name=settings.DEFAULT_MODEL,
                provider="ollama",
                temperature=0.1,
                tool_ids=["code_execution", "terminal", "file_operations", "web_search"],
                is_active=True
            ))
            
    except Exception as e:
        logger.error(f"Error bootstrapping default database entities: {e}")

    yield
    
    # --- Shutdown Actions ---
    logger.info("Shutting down Hermes Agent OS Core Backend...")
    telemetry_manager.stop_metrics_loop()


# Initialize FastAPI app with lifespan
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Custom Exception Handler
@app.exception_handler(AgentOSException)
async def agent_os_exception_handler(request: Request, exc: AgentOSException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.__class__.__name__,
            "message": exc.message
        }
    )

# Register HTTP routers
app.include_router(agent_router, prefix=f"{settings.API_V1_STR}/agent", tags=["agent"])
app.include_router(tools_router, prefix=f"{settings.API_V1_STR}/tools", tags=["tools"])
app.include_router(services_router, prefix=f"{settings.API_V1_STR}/services", tags=["services"])

# Register WebSocket routers (usually separate prefix)
app.include_router(telemetry_router, prefix="/ws", tags=["websocket"])

@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "db_mode": settings.DB_MODE,
        "ollama_endpoint": settings.OLLAMA_URL
    }

# Mount static files to serve the frontend
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/", StaticFiles(directory=base_dir, html=True), name="static")
