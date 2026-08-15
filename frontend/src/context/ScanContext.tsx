import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { DetectionResult } from '../types/detection';
import type { RecommendationResponse, RecommendationRequest } from '../types/recommendation';
import type { ActivityItem } from '../types/dashboard';
import { deleteScanHistoryItem, clearAllUserHistory } from '../services/dashboardService';

export interface ChatTurn {
  role: 'user' | 'assistant';
  message: string;
  timestamp?: string;
  updated_project?: any;
}

interface ScanContextType {
  selectedImage: string | null;
  setSelectedImage: (image: string | null) => void;
  detectionResult: DetectionResult | null;
  setDetectionResult: (result: DetectionResult | null) => void;
  recommendations: RecommendationResponse | null;
  setRecommendations: (recs: RecommendationResponse | null) => void;
  lastPreferences: RecommendationRequest | null;
  setLastPreferences: (prefs: RecommendationRequest | null) => void;

  // Central User Preferences State
  goals: string[];
  setGoals: (goals: string[] | ((prev: string[]) => string[])) => void;
  tools: string[];
  setTools: (tools: string[] | ((prev: string[]) => string[])) => void;
  materials: string[];
  setMaterials: (materials: string[] | ((prev: string[]) => string[])) => void;
  budget: string;
  setBudget: (budget: string) => void;
  difficulty: string;
  setDifficulty: (difficulty: string) => void;
  timeAvailable: string;
  setTimeAvailable: (time: string) => void;

  // Central Reactive AI Assistant Chat Context
  chatHistory: ChatTurn[];
  setChatHistory: (history: ChatTurn[] | ((prev: ChatTurn[]) => ChatTurn[])) => void;
  addChatMessage: (turn: ChatTurn) => void;

  activityList: ActivityItem[];
  deletedIds: string[];
  recordScanActivity: (objectName: string, projectId: string, projectName: string, score: number) => void;
  recordProjectCompletion: (projectId: string) => void;
  deleteScanItem: (scanId: string) => Promise<void>;
  clearAllScans: () => Promise<void>;
  resetScan: () => void;
}

const ScanContext = createContext<ScanContextType | undefined>(undefined);

const STORAGE_KEY = 'byt_user_activities';
const DELETED_KEY = 'byt_deleted_ids';

export function ScanProvider({ children }: { children: ReactNode }) {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [detectionResult, setDetectionResult] = useState<DetectionResult | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null);
  const [lastPreferences, setLastPreferences] = useState<RecommendationRequest | null>(null);

  // Central Multi-Select Preferences State
  const [goals, setGoals] = useState<string[]>(['gardening']);
  const [tools, setTools] = useState<string[]>(['scissors']);
  const [materials, setMaterials] = useState<string[]>([]);
  const [budget, setBudget] = useState<string>('0-50');
  const [difficulty, setDifficulty] = useState<string>('easy');
  const [timeAvailable, setTimeAvailable] = useState<string>('30m');

  // Chat Context State
  const [chatHistory, setChatHistory] = useState<ChatTurn[]>([]);

  const [deletedIds, setDeletedIds] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem(DELETED_KEY);
      if (saved) return JSON.parse(saved);
    } catch {}
    return [];
  });

  const [activityList, setActivityList] = useState<ActivityItem[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      const del = localStorage.getItem(DELETED_KEY);
      const delArray: string[] = del ? JSON.parse(del) : [];
      if (saved !== null) {
        const parsed: ActivityItem[] = JSON.parse(saved);
        return parsed.filter(item => !(item.scan_id && delArray.includes(item.scan_id)) && !(item.project_id && delArray.includes(item.project_id)));
      }
    } catch {}
    return [];
  });

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(activityList));
    } catch {}
  }, [activityList]);

  useEffect(() => {
    try {
      localStorage.setItem(DELETED_KEY, JSON.stringify(deletedIds));
    } catch {}
  }, [deletedIds]);

  const addChatMessage = (turn: ChatTurn) => {
    setChatHistory(prev => [...prev, turn]);
  };

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
    setDeletedIds(prev => [...new Set([...prev, scanId])]);
    setActivityList(prev => {
      const updated = prev.filter(item => item.scan_id !== scanId && item.project_id !== scanId);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
    try {
      await deleteScanHistoryItem(scanId);
    } catch {}
  };

  const clearAllScans = async () => {
    setActivityList([]);
    setDeletedIds([]);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify([]));
      localStorage.setItem(DELETED_KEY, JSON.stringify([]));
      await clearAllUserHistory();
    } catch {}
  };

  const resetScan = () => {
    setSelectedImage(null);
    setDetectionResult(null);
    setRecommendations(null);
    setLastPreferences(null);
    setGoals(['gardening']);
    setTools(['scissors']);
    setMaterials([]);
    setBudget('0-50');
    setDifficulty('easy');
    setTimeAvailable('30m');
    setChatHistory([]);
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
        goals,
        setGoals,
        tools,
        setTools,
        materials,
        setMaterials,
        budget,
        setBudget,
        difficulty,
        setDifficulty,
        timeAvailable,
        setTimeAvailable,
        chatHistory,
        setChatHistory,
        addChatMessage,
        activityList,
        deletedIds,
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
