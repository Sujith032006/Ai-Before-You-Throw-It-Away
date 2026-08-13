export interface ActivityItem {
  scan_id?: string;
  object_name: string;
  project_name: string;
  project_id: string;
  match_score: number;
  status: string;
  date: string;
}

export interface DashboardResponse {
  success: boolean;
  total_scans: number;
  total_projects: number;
  completed_projects: number;
  recent_activity: ActivityItem[];
}

export interface HistoryItem {
  id: string;
  object_name: string;
  date: string;
  recommended_project: string;
  project_id: string;
  match_score: number;
  status: string;
}

export interface HistoryResponse {
  success: boolean;
  history: HistoryItem[];
}

export interface ProjectCompleteResponse {
  success: boolean;
  message: string;
  project_id?: string;
  warning?: string;
}
