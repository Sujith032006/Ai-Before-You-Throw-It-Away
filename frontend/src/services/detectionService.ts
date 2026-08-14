import type { DetectionResult, AnalyzerResult } from '../types/detection';
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
  scan_id?: string;
  analysis?: AnalyzerResult;
  primary_detection: {
    object: string;
    display_name: string;
    confidence: number;
    material?: string;
    category?: string;
    bounding_box?: { x1: number; y1: number; x2: number; y2: number };
  } | null;
  detections: Array<{
    object: string;
    display_name: string;
    confidence: number;
    material?: string;
    category?: string;
    bounding_box?: { x1: number; y1: number; x2: number; y2: number };
  }>;
  message?: string;
  mode?: string;
}

/**
 * Calls FastAPI POST /api/analyze endpoint with multipart/form-data
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
    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Server error (${response.status})`);
    }

    const data: BackendScanResponse = await response.json();

    // Check normalized analysis
    if (data.analysis) {
      const normObj = data.analysis.object;
      return {
        object: normObj.name,
        displayName: normObj.display_name,
        confidence: data.analysis.confidence,
        confidenceText: `${Math.round(data.analysis.confidence * 100)}%`,
        material: normObj.material || 'Reusable Material',
        category: normObj.category || 'Household Object',
        image: typeof imageInput === 'string' ? imageInput : URL.createObjectURL(imageInput),
        analysis: data.analysis,
        source: data.analysis.source,
        status: data.analysis.status,
        suggestions: data.analysis.suggestions
      };
    }

    if (!data.primary_detection) {
      throw new Error(data.message || "We couldn't identify this item confidently. Please try a clearer photo.");
    }

    const primary = data.primary_detection;

    return {
      object: primary.object,
      displayName: primary.display_name,
      confidence: primary.confidence,
      confidenceText: `${Math.round(primary.confidence * 100)}%`,
      material: primary.material || 'Reusable Material',
      category: primary.category || 'Household Object',
      image: typeof imageInput === 'string' ? imageInput : URL.createObjectURL(imageInput),
    };
  } catch (err: any) {
    if (err.name === 'TypeError' || err.message.includes('Failed to fetch')) {
      throw new Error('Unable to connect to the AI service. Please make sure the backend server is running on ' + API_BASE_URL);
    }
    throw err;
  }
}
