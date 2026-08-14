export interface BBoxNormalized {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface NormalizedObject {
  name: string;
  display_name: string;
  material: string;
  condition: string;
  category: string;
}

export interface AnalyzerResult {
  object: NormalizedObject;
  confidence: number;
  source: 'rf_detr' | 'vision_ai' | 'hybrid' | 'quality_check' | string;
  status: 'high_confidence' | 'verified' | 'uncertain' | 'unknown' | 'poor_image_quality' | string;
  bbox?: BBoxNormalized;
  suggestions?: string[];
}

export interface DetectionResult {
  object: string;
  displayName: string;
  confidence: number | null; // e.g., 0.96 for 96%, or null if manually selected
  confidenceText?: string;   // e.g., "96%" or "Manually selected"
  material: string;
  category: string;
  image?: string; // base64 or object URL string
  analysis?: AnalyzerResult;
  source?: string;
  status?: string;
  suggestions?: string[];
}

export interface AvailableObject {
  object: string;
  displayName: string;
  material: string;
  category: string;
}
