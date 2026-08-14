from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class GuideItemStatus(BaseModel):
    name: str
    available: bool
    required: bool

class GuideStep(BaseModel):
    step_number: int
    title: str
    description: str
    tip: Optional[str] = None

class PersonalizedGuideRequest(BaseModel):
    project_id: str
    object_name: str
    goal: str = "gardening"
    available_tools: List[str] = []
    available_materials: List[str] = []
    budget_min: float = 0
    budget_max: float = 50
    difficulty: str = "easy"
    max_time_minutes: int = 30

class PersonalizedGuideResponse(BaseModel):
    success: bool
    project_id: str
    title: str
    summary: str
    estimated_time_minutes: int
    estimated_cost: str
    difficulty: str
    materials: List[GuideItemStatus] = []
    tools: List[GuideItemStatus] = []
    steps: List[GuideStep] = []
    missing_items: List[str] = []
    tips: List[str] = []
    safety_notes: List[str] = []
    is_ai_generated: bool = True
    message: Optional[str] = None

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    project_id: str
    object_name: str
    user_context: Dict[str, Any] = {}
    conversation: List[ChatMessage] = []

class ChatResponse(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None

class GeneralIdeasRequest(BaseModel):
    object_name: str
    material: Optional[str] = "unknown"

class GeneralIdeasResponse(BaseModel):
    success: bool
    object_name: str
    ideas: List[str] = []
    disclaimer: str = "These are general AI suggestions, not validated structured reuse projects."
    message: Optional[str] = None
