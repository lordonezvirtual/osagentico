from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
from app.services.manager import get_service_manager, ServiceManager

router = APIRouter()

class ServiceStatusResponse(BaseModel):
    id: str
    name: str
    description: str
    port: int
    status: str  # active, inactive, starting

class ActionResponse(BaseModel):
    success: bool
    message: str

@router.get("", response_model=List[ServiceStatusResponse])
async def list_services(
    manager: ServiceManager = Depends(get_service_manager)
):
    """
    Lists the status of all managed services (Desktop, Workspace, Agent, n8n, etc.).
    """
    try:
        return manager.list_services()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query service statuses: {str(e)}")

@router.post("/{service_name}/deploy", response_model=ActionResponse)
async def deploy_service(
    service_name: str,
    manager: ServiceManager = Depends(get_service_manager)
):
    """
    Deploys (starts) a specific service by name.
    """
    res = manager.deploy_service(service_name)
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["message"])
    return res

@router.post("/{service_name}/shutdown", response_model=ActionResponse)
async def shutdown_service(
    service_name: str,
    manager: ServiceManager = Depends(get_service_manager)
):
    """
    Shuts down (stops) a specific service by name.
    """
    res = manager.shutdown_service(service_name)
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["message"])
    return res

@router.post("/deploy-all", response_model=ActionResponse)
async def deploy_all_services(
    manager: ServiceManager = Depends(get_service_manager)
):
    """
    Global start action: Starts all docker compose services (Prender Todo).
    """
    return manager.deploy_all()

@router.post("/shutdown-all", response_model=ActionResponse)
async def shutdown_all_services(
    manager: ServiceManager = Depends(get_service_manager)
):
    """
    Global stop action: Stops all docker compose services (Apagar Todo).
    """
    return manager.shutdown_all()
