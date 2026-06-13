from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.api.deps import get_db_dep
from app.infrastructure.database import BaseDatabase
from app.core.models import Tool
from app.core.exceptions import EntityNotFoundError

router = APIRouter()

class ToggleResponse(BaseModel):
    tool_id: str
    is_active: bool
    message: str

@router.put("/{tool_id}/toggle", response_model=Tool)
async def toggle_tool(
    tool_id: str,
    db: BaseDatabase = Depends(get_db_dep)
):
    """
    Toggles the active state of a tool 'in-flight' in the database registry.
    """
    try:
        tool = await db.get_tool(tool_id)
        # Toggle state
        tool.is_active = not tool.is_active
        await db.save_tool(tool)
        return tool
    except EntityNotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database update failed: {str(e)}")
