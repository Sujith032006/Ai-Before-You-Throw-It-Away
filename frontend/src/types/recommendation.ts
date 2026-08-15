export interface ObjectProfile {
  object_name: string;
  display_name?: string;
  material?: string;
  condition?: string;
  confidence?: number;
}

export interface BudgetConstraint {
  min: number;
  max: number;
  currency?: string;
}

export interface RecommendationRequest {
  object_name: string;
  object?: ObjectProfile;
  goal: string;
  custom_goal?: string;
  tools: string[];
  materials: string[];
  budget_min: number;
  budget_max: number;
  budget?: BudgetConstraint;
  difficulty: string;
  max_time_minutes: number;
  time_minutes?: number;
}

export interface EstimatedCost {
  min: number;
  max: number;
  currency?: string;
}

export interface RecommendationItem {
  project_id: string;
  name: string;
  title?: string;
  description: string;
  match_score: number;
  why_it_matches?: string[];
  difficulty: string;
  estimated_time_minutes: number;
  estimated_cost_min: number;
  estimated_cost_max: number;
  estimated_cost?: EstimatedCost;
  matched_factors: string[];
  missing_requirements: string[];
  tools_needed?: string[];
  materials_needed?: string[];
  steps?: string[];
  is_top_match?: boolean;
  image_color?: string;
}

export interface RecommendationResponse {
  success: boolean;
  object_name: string;
  top_recommendation: RecommendationItem | null;
  recommendations: RecommendationItem[];
  message?: string;
}

export interface ProjectDetails {
  success: boolean;
  project_id: string;
  name: string;
  description: string;
  supported_objects: string[];
  goals: string[];
  required_tools: string[];
  optional_tools: string[];
  required_materials: string[];
  optional_materials: string[];
  difficulty: string;
  estimated_time_minutes: number;
  estimated_cost_min: number;
  estimated_cost_max: number;
  safety_notes: string[];
  steps: string[];
}
