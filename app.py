from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from api.logger import AuditLogger
import os

app = Flask(__name__, static_folder="frontend")  # Your frontend folder
CORS(app)
logger = AuditLogger()

@app.route("/log", methods=["POST"])
def log_action():
    data = request.get_json()
    user = data.get("user")
    action = data.get("action")
    
    if not user or not action:
        return jsonify({"error": "user and action fields are required"}), 400

    entry = logger.log_action(user, action)
    return jsonify(entry), 201

@app.route("/logs", methods=["GET"])
def get_logs():
    logs = logger.get_logs()
    return jsonify(logs), 200

# New endpoint to clear logs
@app.route("/clear", methods=["POST"])
def clear_logs():
    # Clear the logs by overwriting with an empty list
    with open(logger.storage_path, 'w') as f:
        f.write("[]")
    return jsonify({"status": "cleared"}), 200

@app.route("/", methods=["GET"])
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    app.run(debug=True)
