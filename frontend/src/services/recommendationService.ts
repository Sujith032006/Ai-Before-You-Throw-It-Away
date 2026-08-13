import type { RecommendationRequest, RecommendationResponse, ProjectDetails } from '../types/recommendation';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function fetchRecommendations(req: RecommendationRequest): Promise<RecommendationResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/recommendations`, {
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

export async function fetchProjectDetails(projectId: string): Promise<ProjectDetails> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}`);
    
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Project not found (${response.status})`);
    }

    return await response.json();
  } catch (err: any) {
    if (err.name === 'TypeError' || err.message.includes('Failed to fetch')) {
      throw new Error('Unable to connect to backend server on ' + API_BASE_URL);
    }
    throw err;
  }
}
