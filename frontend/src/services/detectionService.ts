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
    // 1. Try POST /api/analyze
    let response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      body: formData,
    });

    // 2. Fallback to POST /api/scan if /api/analyze is 404 (mid-deployment on Render)
    if (response.status === 404) {
      const formDataScan = new FormData();
      formDataScan.append('file', fileToUpload);
      response = await fetch(`${API_BASE_URL}/api/scan`, {
        method: 'POST',
        body: formDataScan,
      });
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Server error (${response.status})`);
    }

    const data: BackendScanResponse = await response.json();

    // Check normalized analysis from two-stage analyzer
    if (data.analysis) {
      const normObj = data.analysis.object;
      const confLevel = data.analysis.confidence_level || (data.analysis.confidence >= 0.85 ? 'high' : data.analysis.confidence >= 0.65 ? 'medium' : 'low');
      const confText = `${confLevel.toUpperCase()} Confidence`;

      return {
        object: normObj.name,
        displayName: normObj.display_name,
        baseObject: normObj.base_object,
        supported: data.analysis.supported ?? normObj.supported ?? false,
        confidence: data.analysis.confidence,
        confidenceText: confText,
        confidenceLevel: confLevel,
        material: normObj.material || 'unknown',
        category: normObj.category || 'Household Object',
        image: typeof imageInput === 'string' ? imageInput : URL.createObjectURL(imageInput),
        analysis: data.analysis,
        source: data.analysis.source,
        status: data.analysis.status,
        verification: data.analysis.verification,
        suggestions: data.analysis.suggestions,
        detectedObjects: data.analysis.detected_objects,
        debugInfo: data.analysis.debug_info
      };
    }

    if (!data.primary_detection) {
      throw new Error(data.message || "We couldn't identify this item confidently. Please try a clearer photo.");
    }

    const primary = data.primary_detection;

    return {
      object: primary.object,
      displayName: primary.display_name,
      supported: true,
      confidence: primary.confidence,
      confidenceText: 'HIGH Confidence',
      confidenceLevel: 'high',
      material: primary.material || 'unknown',
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

/**
 * Calls POST /api/general-ideas for unsupported objects
 */
export async function fetchGeneralIdeas(objectName: string, material: string = 'unknown'): Promise<string[]> {
  try {
    const resp = await fetch(`${API_BASE_URL}/api/general-ideas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ object_name: objectName, material: material }),
    });
    if (!resp.ok) return [];
    const data = await resp.json();
    return data.ideas || [];
  } catch {
    return [
      `Repaint or refinish the ${objectName} surface for a fresh look.`,
      `Repurpose as an outdoor planter or garden centerpiece.`,
      `Convert into a unique storage or organizational rack.`,
      `Donate to a local community recycling center or repair workshop.`
    ];
  }
}
