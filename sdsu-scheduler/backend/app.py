"""
Flask app entry point.

Run locally with:
    python3 backend/app.py

Then open http://localhost:5000 in a browser. The frontend/ folder is
served directly by Flask (static_folder below), so there's only one
server to run for local dev.
"""

import os
import sys

# allow "from backend.models..." imports to work when running this file
# directly (python3 backend/app.py) from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, send_from_directory

from backend.routes.sections import sections_bp
from backend.routes.schedule import schedule_bp

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

app.register_blueprint(sections_bp)
app.register_blueprint(schedule_bp)


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/api/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True, port=5000)
