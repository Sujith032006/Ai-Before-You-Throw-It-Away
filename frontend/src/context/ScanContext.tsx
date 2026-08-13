import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { DetectionResult } from '../types/detection';
import type { RecommendationResponse, RecommendationRequest } from '../types/recommendation';
import type { ActivityItem } from '../types/dashboard';
import { deleteScanHistoryItem, clearAllUserHistory } from '../services/dashboardService';

interface ScanContextType {
  selectedImage: string | null;
  setSelectedImage: (image: string | null) => void;
  detectionResult: DetectionResult | null;
  setDetectionResult: (result: DetectionResult | null) => void;
  recommendations: RecommendationResponse | null;
  setRecommendations: (recs: RecommendationResponse | null) => void;
  lastPreferences: RecommendationRequest | null;
  setLastPreferences: (prefs: RecommendationRequest | null) => void;
  activityList: ActivityItem[];
  recordScanActivity: (objectName: string, projectId: string, projectName: string, score: number) => void;
  recordProjectCompletion: (projectId: string) => void;
  deleteScanItem: (scanId: string) => Promise<void>;
  clearAllScans: () => Promise<void>;
  resetScan: () => void;
}

const ScanContext = createContext<ScanContextType | undefined>(undefined);

const STORAGE_KEY = 'byt_user_activities';

export function ScanProvider({ children }: { children: ReactNode }) {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [detectionResult, setDetectionResult] = useState<DetectionResult | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null);
  const [lastPreferences, setLastPreferences] = useState<RecommendationRequest | null>(null);

  const [activityList, setActivityList] = useState<ActivityItem[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved !== null) return JSON.parse(saved);
    } catch {}
    return [];
  });

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(activityList));
    } catch {}
  }, [activityList]);

  const recordScanActivity = (objectName: string, projectId: string, projectName: string, score: number) => {
    const today = new Date().toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' });
    const newItem: ActivityItem = {
      scan_id: `scan-${Date.now()}`,
      object_name: objectName,
      project_name: projectName,
      project_id: projectId,
      match_score: score,
      status: 'in_progress',
      date: today
    };

    setActivityList(prev => {
      const exists = prev.some(item => item.project_id === projectId && item.date === today);
      if (exists) return prev;
      return [newItem, ...prev];
    });
  };

  const recordProjectCompletion = (projectId: string) => {
    setActivityList(prev =>
      prev.map(item =>
        item.project_id === projectId ? { ...item, status: 'completed' } : item
      )
    );
  };

  const deleteScanItem = async (scanId: string) => {
    setActivityList(prev => prev.filter(item => item.scan_id !== scanId && item.project_id !== scanId));
    try {
      await deleteScanHistoryItem(scanId);
    } catch {}
  };

  const clearAllScans = async () => {
    setActivityList([]);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify([]));
      await clearAllUserHistory();
    } catch {}
  };

  const resetScan = () => {
    setSelectedImage(null);
    setDetectionResult(null);
    setRecommendations(null);
    setLastPreferences(null);
  };

  return (
    <ScanContext.Provider
      value={{
        selectedImage,
        setSelectedImage,
        detectionResult,
        setDetectionResult,
        recommendations,
        setRecommendations,
        lastPreferences,
        setLastPreferences,
        activityList,
        recordScanActivity,
        recordProjectCompletion,
        deleteScanItem,
        clearAllScans,
        resetScan,
      }}
    >
      {children}
    </ScanContext.Provider>
  );
}

export function useScan() {
  const context = useContext(ScanContext);
  if (!context) {
    throw new Error('useScan must be used within a ScanProvider');
  }
  return context;
}
