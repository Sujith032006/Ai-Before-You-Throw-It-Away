from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ObjectProfile(BaseModel):
    object_name: str
    display_name: Optional[str] = None
    material: Optional[str] = "unknown"
    condition: Optional[str] = "used"
    confidence: Optional[float] = 0.95

class BudgetConstraint(BaseModel):
    min: float = 0
    max: float = 50
    currency: str = "INR"

class RecommendationRequest(BaseModel):
    object_name: str
    object: Optional[ObjectProfile] = None
    goal: str = "gardening"
    custom_goal: Optional[str] = None
    tools: List[str] = []
    materials: List[str] = []
    budget_min: float = 0
    budget_max: float = 50
    budget: Optional[BudgetConstraint] = None
    difficulty: str = "easy"
    max_time_minutes: int = 30
    time_minutes: Optional[int] = None

class EstimatedCost(BaseModel):
    min: float = 0
    max: float = 50
    currency: str = "INR"

class RecommendationItem(BaseModel):
    project_id: str
    name: str
    title: Optional[str] = None
    description: str
    match_score: int          # 0 - 100
    why_it_matches: List[str] = []
    difficulty: str
    estimated_time_minutes: int
    estimated_cost_min: float = 0
    estimated_cost_max: float = 50
    estimated_cost: Optional[EstimatedCost] = None
    matched_factors: List[str] = []
    missing_requirements: List[str] = []
    tools_needed: List[str] = []
    materials_needed: List[str] = []
    steps: List[str] = []
    is_top_match: bool = False
    image_color: str = "bg-emerald-100"

class RecommendationResponse(BaseModel):
    success: bool
    object_name: str
    top_recommendation: Optional[RecommendationItem] = None
    recommendations: List[RecommendationItem] = []
    message: Optional[str] = None

class ProjectDetailsResponse(BaseModel):
    success: bool
    project_id: str
    name: str
    description: str
    supported_objects: List[str] = []
    goals: List[str] = []
    required_tools: List[str] = []
    optional_tools: List[str] = []
    required_materials: List[str] = []
    optional_materials: List[str] = []
    difficulty: str
    estimated_time_minutes: int
    estimated_cost_min: float = 0
    estimated_cost_max: float = 50
    safety_notes: List[str] = []
    steps: List[str] = []
