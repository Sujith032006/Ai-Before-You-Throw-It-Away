export interface RecommendationRequest {
  object_name: string;
  goal: string;
  tools: string[];
  materials: string[];
  budget_min: number;
  budget_max: number;
  difficulty: string;
  max_time_minutes: number;
}

export interface RecommendationItem {
  project_id: string;
  name: string;
  description: string;
  match_score: number;
  difficulty: string;
  estimated_time_minutes: number;
  estimated_cost_min: number;
  estimated_cost_max: number;
  matched_factors: string[];
  missing_requirements: string[];
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
