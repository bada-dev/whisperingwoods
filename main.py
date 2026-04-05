import json
import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "fallback123")  # Change this
DATA_FILE = "updates.json"

def load_updates():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_updates(updates):
    with open(DATA_FILE, "w") as f:
        json.dump(updates, f, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/updates", methods=["GET"])
def get_updates():
    return jsonify(load_updates())

@app.route("/api/login", methods=["POST"])
def login():
    if request.headers.get("X-Admin-Password") == ADMIN_PASSWORD:
        return jsonify({"ok": True})
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/api/updates", methods=["POST"])
def post_update():
    if request.headers.get("X-Admin-Password") != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    updates = load_updates()
    updates.append({
        "id": str(uuid.uuid4()),
        "title": data.get("title", ""),
        "body": data.get("body", ""),
        "images": data.get("images", []),
        "imgPos": data.get("imgPos", "bottom"),
        "date": datetime.now().strftime("%d %B %Y")
    })
    save_updates(updates)
    return jsonify({"ok": True})

@app.route("/api/updates/<update_id>", methods=["DELETE"])
def delete_update(update_id):
    if request.headers.get("X-Admin-Password") != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized"}), 401
    updates = load_updates()
    updates = [u for u in updates if u["id"] != update_id]
    save_updates(updates)
    return jsonify({"ok": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
