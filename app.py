from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from flask import Flask, render_template

# Initialize Flask application
application = Flask(__name__)
CORS(application)  # Enable CORS for all routes

# Configuration
API_KEY = os.getenv("API_KEY", "default-secure-key")

# In-memory storage
logs = []

@application.route('/api/log', methods=['POST'])
def add_log():
    try:
        # Check API key
        if request.headers.get('X-API-KEY') != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
            
        data = request.json
        required_fields = ['user', 'action', 'type']
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
            
        new_log = {
            'user': data['user'],
            'action': data['action'],
            'type': data['type'],
            'timestamp': datetime.now().isoformat(),
            'details': data.get('details', '')
        }
        
        logs.append(new_log)
        return jsonify(new_log), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        # Get query parameters
        user = request.args.get('user')
        action = request.args.get('action')
        log_type = request.args.get('type')
        date_from = request.args.get('from')
        date_to = request.args.get('to')
        
        # Filter logs
        filtered_logs = logs
        if user:
            filtered_logs = [log for log in filtered_logs if log['user'] == user]
        if action:
            filtered_logs = [log for log in filtered_logs if action.lower() in log['action'].lower()]
        if log_type:
            filtered_logs = [log for log in filtered_logs if log['type'] == log_type]
        if date_from:
            filtered_logs = [log for log in filtered_logs if log['timestamp'].split('T')[0] >= date_from]
        if date_to:
            filtered_logs = [log for log in filtered_logs if log['timestamp'].split('T')[0] <= date_to]
            
        return jsonify(filtered_logs)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route('/api/clear', methods=['POST'])
def clear_logs():
    try:
        # Check API key
        if request.headers.get('X-API-KEY') != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
            
        logs.clear()
        return jsonify({"message": "All logs cleared"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        stats = {
            'total': len(logs),
            'info': len([log for log in logs if log['type'] == 'info']),
            'warning': len([log for log in logs if log['type'] == 'warning']),
            'error': len([log for log in logs if log['type'] == 'error'])
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route('/')
def home():
    return "Audit Trail API is running. Use /api endpoints to interact with the system."

if __name__ == '__main__':
    application.run(debug=True, port=5000, host='0.0.0.0')

