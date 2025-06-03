from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from .logger import AuditLogger, JSONFileStrategy, LogEntry
import os

app = Flask(__name__)
CORS(app)

# Initialize logger with JSON strategy
logger = AuditLogger(JSONFileStrategy("logs.json"))
API_KEY = os.getenv("API_KEY", "default-secure-key")

@app.route('/log', methods=['POST'])
def add_log():
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    try:
        log_entry = LogEntry(
            user=data['user'],
            action=data['action'],
            type=data.get('type', 'info'),
            timestamp=datetime.utcnow().isoformat()
        )
        result = logger.log_action(log_entry)
        return jsonify(result.dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        logs = logger.get_logs(
            user=request.args.get('user'),
            action=request.args.get('action'),
            log_type=request.args.get('type'),
            start_date=request.args.get('from'),
            end_date=request.args.get('to')
        )
        return jsonify([log.dict() for log in logs])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_logs():
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    logger.clear_logs()
    return jsonify({"message": "Logs cleared"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)