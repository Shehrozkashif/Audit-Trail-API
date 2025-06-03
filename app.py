from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from api.logger import AuditLogger, LogEntry  # <-- import your logger

# Initialize Flask application
application = Flask(__name__)
CORS(application)

API_KEY = os.getenv("API_KEY", "default-secure-key")

logger = AuditLogger("api/db.json")  # <-- use your logger

@application.route('/api/log', methods=['POST'])
def add_log():
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    try:
        entry = LogEntry(
            user=data['user'],
            action=data['action'],
            type=data['type'],
            timestamp=datetime.now().isoformat()
        )
        logger.log_action(entry)
        return jsonify(entry.dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@application.route('/api/logs', methods=['GET'])
def get_logs():
    user = request.args.get('user')
    action = request.args.get('action')
    log_type = request.args.get('type')
    date_from = request.args.get('from')
    date_to = request.args.get('to')

    try:
        logs = logger.get_logs(
            user=user,
            action=action,
            log_type=log_type,
            start_date=date_from,
            end_date=date_to
        )
        return jsonify([log.dict() for log in logs]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route('/api/clear', methods=['POST'])
def clear_logs():
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        logger.clear_logs()
        return jsonify({"message": "All logs cleared"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        logs = logger.get_logs()
        stats = {
            'total': len(logs),
            'info': len([log for log in logs if log.type == 'info']),
            'warning': len([log for log in logs if log.type == 'warning']),
            'error': len([log for log in logs if log.type == 'error']),
        }
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route('/')
def home():
    return "Audit Trail API is running with persistent logger."

if __name__ == '__main__':
    application.run(debug=True, port=5000, host='0.0.0.0')
