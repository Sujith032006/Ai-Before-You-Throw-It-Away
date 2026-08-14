export interface BBoxNormalized {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface NormalizedObject {
  name: string;
  display_name: string;
  base_object?: string;
  material: string;
  condition?: string;
  category: string;
  supported?: boolean;
  confidence?: number;
  confidence_level?: 'high' | 'medium' | 'low' | 'none' | string;
}

export interface AnalyzerResult {
  object: NormalizedObject;
  supported: boolean;
  confidence: number;
  confidence_level: 'high' | 'medium' | 'low' | 'none' | string;
  source: 'rf_detr' | 'vision_ai' | 'hybrid' | 'quality_check' | string;
  status: 'identified' | 'identified_but_unsupported' | 'multiple_objects' | 'ambiguous' | 'poor_image_quality' | string;
  verification: 'consistent' | 'conflict_resolved' | 'vision_ai_primary' | 'rf_detr_primary' | 'conflict_unresolved' | string;
  bbox?: BBoxNormalized;
  detected_objects?: NormalizedObject[];
  suggestions?: string[];
  debug_info?: Record<string, any>;
}

export interface DetectionResult {
  object: string;
  displayName: string;
  baseObject?: string;
  supported: boolean;
  confidence: number | null;
  confidenceText?: string;
  confidenceLevel?: string;
  material: string;
  category: string;
  image?: string;
  analysis?: AnalyzerResult;
  source?: string;
  status?: string;
  verification?: string;
  suggestions?: string[];
  detectedObjects?: NormalizedObject[];
  debugInfo?: Record<string, any>;
}

export interface AvailableObject {
  object: string;
  displayName: string;
  material: string;
  category: string;
}
