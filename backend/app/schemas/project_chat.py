from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ProjectObjectContext(BaseModel):
    name: str = "item"
    material: str = "unknown"
    condition: str = "used"

class SelectedProjectContext(BaseModel):
    title: str = "Upcycling Project"
    difficulty: str = "easy"
    estimated_time_minutes: int = 30
    estimated_cost: Dict[str, Any] = {"min": 0, "max": 50, "currency": "INR"}

class UserPreferencesContext(BaseModel):
    goal: str = "gardening"
    custom_goal: Optional[str] = None
    budget: float = 50.0
    time_minutes: int = 30
    difficulty: str = "easy"

class ProjectContext(BaseModel):
    object: ProjectObjectContext = ProjectObjectContext()
    selected_project: SelectedProjectContext = SelectedProjectContext()
    user_preferences: UserPreferencesContext = UserPreferencesContext()
    tools: List[str] = []
    materials: List[str] = []
    current_step: int = 1

class ProjectChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str

class ProjectChatRequest(BaseModel):
    project_context: ProjectContext
    conversation: List[ProjectChatMessage] = []
    message: str

class ProjectChatResponse(BaseModel):
    success: bool = True
    message: str
    action: str = "answer_question"  # answer_question | modify_project | replace_material | replace_tool | reduce_budget | reduce_time | change_difficulty | generate_alternatives | explain_step | restart_project
    updated_project: Optional[Dict[str, Any]] = None
    suggestions: List[str] = []
