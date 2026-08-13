export interface GuideItemStatus {
  name: string;
  available: boolean;
  required: boolean;
}

export interface GuideStep {
  step_number: number;
  title: string;
  description: string;
  tip?: string;
}

export interface PersonalizedGuideRequest {
  project_id: string;
  object_name: string;
  goal: string;
  available_tools: string[];
  available_materials: string[];
  budget_min: number;
  budget_max: number;
  difficulty: string;
  max_time_minutes: number;
}

export interface PersonalizedGuideResponse {
  success: boolean;
  project_id: string;
  title: string;
  summary: string;
  estimated_time_minutes: number;
  estimated_cost: string;
  difficulty: string;
  materials: GuideItemStatus[];
  tools: GuideItemStatus[];
  steps: GuideStep[];
  missing_items: string[];
  tips: string[];
  safety_notes: string[];
  is_ai_generated: boolean;
  message?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  project_id: string;
  object_name: string;
  user_context: Record<string, any>;
  conversation: ChatMessage[];
}

export interface ChatResponse {
  success: boolean;
  message: string;
  error?: string;
}
