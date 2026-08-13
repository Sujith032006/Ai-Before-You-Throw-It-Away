import type { DetectionResult } from '../types/detection';

import { API_BASE_URL } from './config';

/**
 * Helper function to convert base64/data URL into a Blob File
 */
function dataURLtoFile(dataurl: string, filename: string): File {
  const arr = dataurl.split(',');
  const mimeMatch = arr[0].match(/:(.*?);/);
  const mime = mimeMatch ? mimeMatch[1] : 'image/jpeg';
  const bstr = atob(arr[1]);
  let n = bstr.length;
  const u8arr = new Uint8Array(n);
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n);
  }
  return new File([u8arr], filename, { type: mime });
}

export interface BackendScanResponse {
  success: boolean;
  primary_detection: {
    object: string;
    display_name: string;
    confidence: number;
    bounding_box?: { x1: number; y1: number; x2: number; y2: number };
  } | null;
  detections: Array<{
    object: string;
    display_name: string;
    confidence: number;
    bounding_box?: { x1: number; y1: number; x2: number; y2: number };
  }>;
  message?: string;
  mode?: string;
}

/**
 * Calls FastAPI POST /api/scan endpoint with multipart/form-data
 */
export async function analyzeImageWithBackend(imageInput: string | File): Promise<DetectionResult> {
  let fileToUpload: File;

  if (typeof imageInput === 'string') {
    if (imageInput.startsWith('data:')) {
      fileToUpload = dataURLtoFile(imageInput, 'scanned_item.jpg');
    } else {
      throw new Error('Invalid image data format.');
    }
  } else {
    fileToUpload = imageInput;
  }

  const formData = new FormData();
  formData.append('file', fileToUpload);

  try {
    const response = await fetch(`${API_BASE_URL}/api/scan`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Server error (${response.status})`);
    }

    const data: BackendScanResponse = await response.json();

    if (!data.primary_detection) {
      throw new Error(data.message || "We couldn't identify this item confidently. Please try a clearer photo.");
    }

    const primary = data.primary_detection;

    return {
      object: primary.object,
      displayName: primary.display_name,
      confidence: primary.confidence,
      confidenceText: `${Math.round(primary.confidence * 100)}%`,
      material: 'Detected Item', // Real material mapping will be enhanced in later stage
      category: 'Scanned Object',
      image: typeof imageInput === 'string' ? imageInput : URL.createObjectURL(imageInput),
    };
  } catch (err: any) {
    if (err.name === 'TypeError' || err.message.includes('Failed to fetch')) {
      throw new Error('Unable to connect to the AI service. Please make sure the backend server is running on ' + API_BASE_URL);
    }
    throw err;
  }
}
