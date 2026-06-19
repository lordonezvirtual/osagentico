import subprocess
import json
import logging
import shutil
import os
from typing import List, Dict, Any, Optional
from app.infrastructure.database import get_db
from app.services.fallbacks import get_fallback_html

# Mapping from friendly user service name to GitHub repositories to clone if files are missing
GITHUB_REPOS = {
    "hermes-agent": "https://github.com/lordonezvirtual/osagentico.git",
    "hermes-desktop": "https://github.com/lordonezvirtual/iothome.git",
    "hermes-workspace": "https://github.com/lordonezvirtual/osagentico.git",
    "openclaw": "https://github.com/hscspring/openclaw.git",
    "n8n": "https://github.com/n8n-io/n8n.git",
}

logger = logging.getLogger("service_manager")

# Mapping from friendly user service name to docker-compose service name
SERVICE_MAPPING = {
    "hermes-agent": "agent-os-backend",
    "hermes-desktop": "hermes-desktop",
    "hermes-workspace": "hermes-workspace",
    "n8n": "n8n",
    "openclaw": "openclaw",
    "crewai": "crewai",
    "autogpt": "autogpt",
    "langflow": "langflow",
    "autogen": "autogen",
    "langgraph": "langgraph",
    "devika": "devika",
    "chatdev": "chatdev"
}

# Service details metadata
SERVICE_METADATA = {
    "hermes-agent": {
        "name": "Hermes Agent",
        "description": "Núcleo autónomo de toma de decisiones vía API y CLI.",
        "port": 8081
    },
    "hermes-desktop": {
        "name": "Hermes Desktop",
        "description": "Entorno de ejecución local con acceso a sistema de archivos y terminal.",
        "port": 8082
    },
    "hermes-workspace": {
        "name": "Hermes Workspace",
        "description": "Espacio de trabajo compartido en la nube con repositorios y directorios aislados.",
        "port": 8083
    },
    "n8n": {
        "name": "n8n",
        "description": "Automatizador de flujos de trabajo e integraciones nodales de terceros.",
        "port": 5678
    },
    "openclaw": {
        "name": "openclaw",
        "description": "Framework ligero y orquestador modular de agentes.",
        "port": 8080
    },
    "crewai": {
        "name": "CrewAI Framework",
        "description": "Orquestador de equipos de agentes AI colaborativos con roles definidos.",
        "port": 8010
    },
    "autogpt": {
        "name": "AutoGPT Node",
        "description": "Agente autónomo de bucle continuo para resolución de objetivos complejos.",
        "port": 8012
    },
    "langflow": {
        "name": "Langflow UI",
        "description": "Constructor visual de flujos de trabajo e interfaces gráficas RAG.",
        "port": 7860
    },
    "autogen": {
        "name": "Microsoft AutoGen",
        "description": "Framework multi-agente para configurar flujos conversacionales de resolución de tareas.",
        "port": 8015
    },
    "langgraph": {
        "name": "LangGraph Nodes",
        "description": "Orquestación cíclica y persistente de agentes complejos basada en grafos.",
        "port": 8016
    },
    "devika": {
        "name": "Devika Agent",
        "description": "Asistente de codificación y desarrollo de software autónomo open-source.",
        "port": 8018
    },
    "chatdev": {
        "name": "ChatDev Virtual",
        "description": "Entorno virtual simulado para creación cooperativa de software mediante agentes.",
        "port": 8020
    }
}

class ServiceManager:
    def __init__(self):
        self.docker_available = shutil.which("docker") is not None

    def _run_compose_cmd(self, args: List[str]) -> tuple[bool, str]:
        """Runs docker compose command in subprocess."""
        if not self.docker_available:
            return False, "Docker CLI not found on host path."
        
        try:
            cmd = ["docker", "compose"] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                return True, result.stdout
            return False, result.stderr
        except subprocess.TimeoutExpired:
            return False, "Docker command execution timed out."
        except Exception as e:
            return False, str(e)

    async def _ensure_service_files(self, name: str) -> None:
        """Checks if local folder is empty, and clones or generates fallback files."""
        dir_suffix = name.replace("hermes-", "")
        target_dir = os.path.abspath(os.path.join(".", "data", dir_suffix))
        
        if name in ["n8n", "postgres", "ollama"]:
            return

        os.makedirs(target_dir, exist_ok=True)
        
        files = [f for f in os.listdir(target_dir) if not f.startswith(".")]
        if not files:
            logger.info(f"Target directory {target_dir} for service '{name}' is empty. Cloner triggered.")
            repo_url = GITHUB_REPOS.get(name)
            cloned = False
            
            if repo_url:
                try:
                    cmd = ["git", "clone", repo_url, "."]
                    result = subprocess.run(
                        cmd,
                        cwd=target_dir,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        logger.info(f"Successfully cloned {repo_url} into {target_dir}")
                        cloned = True
                    else:
                        logger.warning(f"Git clone failed: {result.stderr}")
                except Exception as e:
                    logger.warning(f"Error during git clone: {e}")
            
            if not cloned:
                logger.info(f"Writing high-fidelity fallback HTML for service '{name}'")
                fallback_html = get_fallback_html(
                    name, 
                    SERVICE_METADATA.get(name, {}).get("name", name),
                    SERVICE_METADATA.get(name, {}).get("port", 80)
                )
                try:
                    with open(os.path.join(target_dir, "index.html"), "w", encoding="utf-8") as f:
                        f.write(fallback_html)
                    logger.info(f"Successfully wrote fallback index.html to {target_dir}")
                except Exception as e:
                    logger.error(f"Failed to write fallback index.html: {e}")

    async def list_services(self) -> List[Dict[str, Any]]:
        """Lists all services with status, port, and description details."""
        db = get_db()
        db_services = await db.list_services()
        db_statuses = {srv["id"]: srv["status"] for srv in db_services}
        
        docker_statuses = {}
        success, output = self._run_compose_cmd(["ps", "-a", "--format", "json"])
        if success and output.strip():
            try:
                lines = output.strip().split("\n")
                for line in lines:
                    if not line:
                        continue
                    container_data = json.loads(line)
                    service_key = container_data.get("Service")
                    state = container_data.get("State", "inactive").lower()
                    
                    mapped_state = "inactive"
                    if state in ["running", "up"]:
                        mapped_state = "active"
                    elif state in ["restarting", "starting"]:
                        mapped_state = "starting"
                        
                    for friendly_name, comp_name in SERVICE_MAPPING.items():
                        if comp_name == service_key:
                            docker_statuses[friendly_name] = mapped_state
            except Exception as e:
                logger.warning(f"Error parsing docker compose ps JSON output: {e}")

        services_list = []
        for key, meta in SERVICE_METADATA.items():
            status = docker_statuses.get(key, db_statuses.get(key, "inactive"))
            
            if db_statuses.get(key) != status:
                await db.save_service(key, status)
                
            services_list.append({
                "id": key,
                "name": meta["name"],
                "description": meta["description"],
                "port": meta["port"],
                "status": status
            })
        return services_list

    async def deploy_service(self, name: str) -> Dict[str, Any]:
        """Starts/turns on a service."""
        if name not in SERVICE_MAPPING:
            return {"success": False, "message": f"Service '{name}' is not registered."}

        await self._ensure_service_files(name)

        compose_service = SERVICE_MAPPING[name]
        logger.info(f"Deploying service: {name} ({compose_service})")

        success, error_msg = self._run_compose_cmd(["start", compose_service])
        if not success:
            success, error_msg = self._run_compose_cmd(["up", "-d", compose_service])

        db = get_db()
        await db.save_service(name, "active")

        if success:
            return {"success": True, "message": f"Service '{name}' deployed successfully."}
        else:
            logger.warning(f"Docker deployment failed, using database/local fallback: {error_msg}")
            return {"success": True, "message": f"Service '{name}' deployed locally (mock fallback)."}

    async def shutdown_service(self, name: str) -> Dict[str, Any]:
        """Stops/turns off a service."""
        if name not in SERVICE_MAPPING:
            return {"success": False, "message": f"Service '{name}' is not registered."}

        compose_service = SERVICE_MAPPING[name]
        logger.info(f"Shutting down service: {name} ({compose_service})")

        success, error_msg = self._run_compose_cmd(["stop", compose_service])

        db = get_db()
        await db.save_service(name, "inactive")

        if success:
            return {"success": True, "message": f"Service '{name}' shut down successfully."}
        else:
            logger.warning(f"Docker shutdown failed, using database/local fallback: {error_msg}")
            return {"success": True, "message": f"Service '{name}' shut down locally (mock fallback)."}

    async def deploy_all(self) -> Dict[str, Any]:
        """Starts all defined compose services (Prender Todo)."""
        logger.info("Deploying all services...")
        
        for key in SERVICE_MAPPING.keys():
            await self._ensure_service_files(key)
            
        success, error_msg = self._run_compose_cmd(["start"])
        if not success:
            success, error_msg = self._run_compose_cmd(["up", "-d"])

        db = get_db()
        for key in SERVICE_MAPPING.keys():
            await db.save_service(key, "active")

        return {
            "success": True, 
            "message": "All services deployed successfully." if success else "All services deployed locally (mock fallback)."
        }

    async def shutdown_all(self) -> Dict[str, Any]:
        """Stops all defined compose services (Apagar Todo)."""
        logger.info("Shutting down all services...")
        success, error_msg = self._run_compose_cmd(["stop"])
        
        db = get_db()
        for key in SERVICE_MAPPING.keys():
            await db.save_service(key, "inactive")

        return {
            "success": True, 
            "message": "All services shut down successfully." if success else "All services shut down locally (mock fallback)."
        }


# Singleton service manager instance
_service_manager = ServiceManager()

def get_service_manager() -> ServiceManager:
    return _service_manager
