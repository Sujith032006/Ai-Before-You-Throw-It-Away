from typing import List, Optional
from pydantic import BaseModel

class ActivityItem(BaseModel):
    scan_id: Optional[str] = None
    object_name: str
    project_name: str
    project_id: str
    match_score: int
    status: str
    date: str

class DashboardResponse(BaseModel):
    success: bool = True
    total_scans: int
    total_projects: int
    completed_projects: int
    recent_activity: List[ActivityItem] = []

class HistoryItem(BaseModel):
    id: str
    object_name: str
    date: str
    recommended_project: str
    project_id: str
    match_score: int
    status: str

class HistoryResponse(BaseModel):
    success: bool = True
    history: List[HistoryItem] = []

class ProjectCompleteResponse(BaseModel):
    success: bool
    message: str
    project_id: Optional[str] = None
    warning: Optional[str] = None
