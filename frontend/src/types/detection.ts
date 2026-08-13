export interface DetectionResult {
  object: string;
  displayName: string;
  confidence: number | null; // e.g., 0.96 for 96%, or null if manually selected
  confidenceText?: string;   // e.g., "96%" or "Manually selected"
  material: string;
  category: string;
  image?: string; // base64 or object URL string
}

export interface AvailableObject {
  object: string;
  displayName: string;
  material: string;
  category: string;
}
