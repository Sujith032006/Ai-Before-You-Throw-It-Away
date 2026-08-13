from fastapi import APIRouter, status, Path
from app.schemas.dashboard import HistoryResponse, ProjectCompleteResponse
from app.services.persistence_service import get_user_history, mark_project_complete, delete_user_scan, delete_all_user_history

router = APIRouter(prefix="/api", tags=["History & Projects"])

@router.get("/history", response_model=HistoryResponse, status_code=status.HTTP_200_OK)
async def get_history():
    items = get_user_history()
    return HistoryResponse(success=True, history=items)

@router.delete("/history/{scan_id}", status_code=status.HTTP_200_OK)
async def delete_history_item(scan_id: str = Path(..., description="ID of scan to delete")):
    res = delete_user_scan(scan_id)
    return {"success": res, "message": f"Scan item {scan_id} deleted."}

@router.delete("/history", status_code=status.HTTP_200_OK)
async def clear_all_history():
    res = delete_all_user_history()
    return {"success": res, "message": "All scan history cleared."}

@router.post("/projects/{project_id}/complete", response_model=ProjectCompleteResponse, status_code=status.HTTP_200_OK)
async def complete_project(project_id: str = Path(..., description="ID of project to mark completed")):
    res = mark_project_complete(project_id)
    return ProjectCompleteResponse(
        success=res.get("success", True),
        message=res.get("message", "Project marked completed"),
        project_id=project_id,
        warning=res.get("warning")
    )
