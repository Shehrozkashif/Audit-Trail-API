import json
import os
from datetime import datetime
from typing import Optional, List, Dict


class AuditLogger:
    def __init__(self, storage_path="api/db.json"):
        self.storage_path = storage_path
        self._initialize_storage()

    def _initialize_storage(self):
        """Ensure the log file exists and contains valid JSON."""
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump([], f)
        else:
            try:
                with open(self.storage_path, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError:
                with open(self.storage_path, 'w') as f:
                    json.dump([], f)

    def log_action(self, user: str, action: str) -> Optional[Dict]:
        """Logs a user action with timestamp."""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "user": user,
            "action": action,
            "timestamp": timestamp
        }

        try:
            with open(self.storage_path, 'r+') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []

                logs.append(log_entry)
                f.seek(0)
                f.truncate()
                json.dump(logs, f, indent=4)

            return log_entry
        except Exception as e:
            print(f"[ERROR] Failed to log action: {e}")
            return None

    def get_logs(self, user: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Dict]:
        """Returns logs, optionally filtered by user and/or time range."""
        try:
            with open(self.storage_path, 'r') as f:
                logs = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to read logs: {e}")
            return []

        if user:
            logs = [log for log in logs if log.get("user") == user]

        if start_time:
            logs = [log for log in logs if log.get("timestamp") >= start_time]

        if end_time:
            logs = [log for log in logs if log.get("timestamp") <= end_time]

        return logs
