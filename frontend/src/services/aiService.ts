import type { PersonalizedGuideRequest, PersonalizedGuideResponse, ChatRequest, ChatResponse } from '../types/ai';

import { API_BASE_URL } from './config';

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
