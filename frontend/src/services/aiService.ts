import type { PersonalizedGuideRequest, PersonalizedGuideResponse, ChatRequest, ChatResponse } from '../types/ai';
import { API_BASE_URL } from './config';

export interface ProjectContextPayload {
  object: {
    name: string;
    material?: string;
    condition?: string;
  };
  selected_project: {
    title: string;
    difficulty?: string;
    estimated_time_minutes?: number;
    estimated_cost?: {
      min?: number;
      max?: number;
      currency?: string;
    };
  };
  user_preferences: {
    goal?: string;
    custom_goal?: string;
    budget?: number;
    time_minutes?: number;
    difficulty?: string;
  };
  tools: string[];
  materials: string[];
  current_step: number;
}

export interface ProjectChatPayload {
  project_context: ProjectContextPayload;
  conversation: Array<{ role: string; content: string }>;
  message: string;
}

export interface ProjectChatResult {
  success: boolean;
  message: string;
  action: string;
  updated_project?: any;
  suggestions: string[];
}

export async function sendProjectChatMessage(payload: ProjectChatPayload): Promise<ProjectChatResult> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/project-chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Server error (${response.status})`);
    }

    return await response.json();
  } catch (err: any) {
    if (err.name === 'TypeError' || err.message.includes('Failed to fetch')) {
      throw new Error('Unable to connect to backend server on ' + API_BASE_URL);
    }
    throw err;
  }
}

export async function fetchPersonalizedGuide(req: PersonalizedGuideRequest): Promise<PersonalizedGuideResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/projects/personalized-guide`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Server error (${response.status})`);
    }

    return await response.json();
  } catch (err: any) {
    if (err.name === 'TypeError' || err.message.includes('Failed to fetch')) {
      throw new Error('Unable to connect to backend server on ' + API_BASE_URL);
    }
    throw err;
  }
}

export async function sendChatMessage(req: ChatRequest): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Server error (${response.status})`);
    }

    return await response.json();
  } catch (err: any) {
    if (err.name === 'TypeError' || err.message.includes('Failed to fetch')) {
      throw new Error('Unable to connect to backend server on ' + API_BASE_URL);
    }
    throw err;
  }
}
