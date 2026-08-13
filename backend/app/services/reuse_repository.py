import json
import os
from typing import List, Optional, Dict, Any

DATA_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "reuse_projects.json")

class ReuseRepository:
    def __init__(self, data_path: str = DATA_FILE_PATH):
        self.data_path = data_path
        self._projects: List[Dict[str, Any]] = []
        self._load_projects()

    def _load_projects(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as f:
                self._projects = json.load(f)
        else:
            self._projects = []

    def get_all_projects(self) -> List[Dict[str, Any]]:
        return self._projects

    def get_project_by_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        for proj in self._projects:
            if proj.get("id") == project_id:
                return proj
        return None

    def get_projects_by_object(self, object_name: str) -> List[Dict[str, Any]]:
        norm_name = object_name.lower().strip().replace(" ", "_")
        norm_title = object_name.lower().strip()
        
        matches = []
        for proj in self._projects:
            supported = [s.lower().strip() for s in proj.get("supported_objects", [])]
            if norm_name in supported or norm_title in supported:
                matches.append(proj)
        return matches

# Global singleton repository instance
reuse_repository = ReuseRepository()
