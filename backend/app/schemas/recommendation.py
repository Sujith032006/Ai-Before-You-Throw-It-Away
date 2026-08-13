from typing import List, Optional
from pydantic import BaseModel

class RecommendationRequest(BaseModel):
    object_name: str
    goal: str = "gardening"  # gardening, storage, decoration, organization, useful_item, craft, gift, surprise_me
    tools: List[str] = []    # e.g., ["scissors", "glue"]
    materials: List[str] = [] # e.g., ["soil", "cotton"]
    budget_min: float = 0
    budget_max: float = 50
    difficulty: str = "easy"  # easy, medium, hard
    max_time_minutes: int = 30

class RecommendationItem(BaseModel):
    project_id: str
    name: str
    description: str
    match_score: int          # 0 - 100
    difficulty: str
    estimated_time_minutes: int
    estimated_cost_min: float
    estimated_cost_max: float
    matched_factors: List[str]
    missing_requirements: List[str]
    is_top_match: bool = False
    image_color: str = "bg-green-100"

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
    supported_objects: List[str]
    goals: List[str]
    required_tools: List[str]
    optional_tools: List[str]
    required_materials: List[str]
    optional_materials: List[str]
    difficulty: str
    estimated_time_minutes: int
    estimated_cost_min: float
    estimated_cost_max: float
    safety_notes: List[str]
    steps: List[str]
