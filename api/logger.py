import json
import os
from datetime import datetime
from typing import Optional, List, Dict
from threading import Lock
from pydantic import BaseModel, validator

class LogEntry(BaseModel):
    user: str
    action: str
    timestamp: str
    type: str = "info"  # info/warning/error

    @validator('type')
    def validate_type(cls, v):
        if v not in ("info", "warning", "error"):
            raise ValueError("Type must be info, warning, or error")
        return v

class AuditLogger:
    _instance = None
    _lock = Lock()

    def __new__(cls, storage_path="api/db.json"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(storage_path)
        return cls._instance

    def _initialize(self, storage_path):
        """Initialize the logger with thread-safe file handling"""
        self.storage_path = storage_path
        self._ensure_storage()
        
    def _ensure_storage(self):
        """Ensure storage file exists with proper permissions"""
        with self._lock:
            if not os.path.exists(self.storage_path):
                with open(self.storage_path, 'w') as f:
                    json.dump([], f)
                os.chmod(self.storage_path, 0o600)  # Secure file permissions

    def _read_logs(self) -> List[Dict]:
        """Thread-safe log reading"""
        with self._lock:
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []

    def _write_logs(self, logs: List[Dict]):
        """Thread-safe log writing"""
        with self._lock:
            with open(self.storage_path, 'w') as f:
                json.dump(logs, f, indent=2)

    def log_action(self, entry: LogEntry) -> Optional[LogEntry]:
        """Add a new log entry with validation"""
        try:
            logs = self._read_logs()
            logs.append(entry.dict())
            self._write_logs(logs)
            return entry
        except Exception as e:
            print(f"Logging failed: {str(e)}")
            return None

    def get_logs(self, 
                user: Optional[str] = None,
                action: Optional[str] = None,
                log_type: Optional[str] = None,
                start_date: Optional[str] = None,
                end_date: Optional[str] = None) -> List[LogEntry]:
        
        logs = self._read_logs()
        
        # Apply filters
        filtered = []
        for log in logs:
            if user and log['user'] != user:
                continue
            if action and action.lower() not in log['action'].lower():
                continue
            if log_type and log['type'] != log_type:
                continue
            if start_date and log['timestamp'] < start_date:
                continue
            if end_date and log['timestamp'] > end_date:
                continue
            filtered.append(LogEntry(**log))
            
        return filtered

    def clear_logs(self):
        """Clear all logs (with confirmation in calling code)"""
        self._write_logs([])