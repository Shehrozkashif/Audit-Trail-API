import requests
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"
API_KEY = "default-secure-key"  # Should be in environment variables

def log_action(user: str, action: str, log_type: str = "info"):
    """Log a new action to the audit trail"""
    try:
        res = requests.post(
            f"{BASE_URL}/log",
            json={
                "user": user,
                "action": action,
                "type": log_type
            },
            headers={"X-API-KEY": API_KEY}
        )
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error logging action: {str(e)}")
        return None

def view_logs(days: int = 7):
    """View recent logs (default: last 7 days)"""
    try:
        end_date = datetime.now().isoformat()
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        res = requests.get(
            f"{BASE_URL}/logs",
            params={
                "from": start_date,
                "to": end_date
            }
        )
        res.raise_for_status()
        
        logs = res.json()
        for log in logs:
            print(f"{log['timestamp']} [{log['type'].upper()}] {log['user']}: {log['action']}")
        return logs
    except Exception as e:
        print(f"Error fetching logs: {str(e)}")
        return None

if __name__ == '__main__':
    # Example usage
    log_action("admin", "system maintenance", "warning")
    log_action("user1", "logged in")
    view_logs(1)  # Show last day's logs