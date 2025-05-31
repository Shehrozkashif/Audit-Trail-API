# client_app/client.py
import requests

BASE_URL = "http://127.0.0.1:5000"

def log_action(user, action):
    res = requests.post(f"{BASE_URL}/log", json={"user": user, "action": action})
    print(res.json())

def view_logs():
    res = requests.get(f"{BASE_URL}/logs")
    for log in res.json():
        print(f"{log['timestamp']} - {log['user']}: {log['action']}")

# Example usage
log_action("admin", "logged in")
log_action("admin", "uploaded a file")
view_logs()
