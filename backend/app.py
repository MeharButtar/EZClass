"""
Flask app entry point.

Run locally with:
    python3 backend/app.py

Then open http://localhost:5000 in a browser. The frontend/ folder is
served directly by Flask (static_folder below), so there's only one
server to run for local dev.

In production (Docker / Render) gunicorn imports `app` from this module
instead, see the Dockerfile. Settings come from environment variables,
see .env.example.
"""

import os
import sys

# allow "from backend.models..." imports to work when running this file
# directly (python3 backend/app.py) from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, send_from_directory

from backend.models.db import ensure_database, get_connection
from backend.routes.analytics import analytics_bp
from backend.routes.sections import sections_bp
from backend.routes.schedule import schedule_bp

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

# build the class database if this is a fresh machine/container (never wipes existing data)
ensure_database()

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

app.register_blueprint(sections_bp)
app.register_blueprint(schedule_bp)
app.register_blueprint(analytics_bp)

# The frontend has no inline scripts and loads nothing from other sites, so a
# strict policy costs nothing. Inline styles stay allowed so style="" attributes
# (and element.style in JS) keep working for whoever edits the frontend next.
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Content-Security-Policy": (
        "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
        "script-src 'self'; connect-src 'self'; frame-ancestors 'none'; "
        "base-uri 'self'; form-action 'self'"
    ),
}


@app.after_request
def add_security_headers(response):
    for name, value in SECURITY_HEADERS.items():
        response.headers.setdefault(name, value)
    return response


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/api/health")
def health():
    try:
        conn = get_connection()
        conn.execute("SELECT 1").fetchone()
        conn.close()
    except Exception:
        return {"status": "error"}, 503
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(
        debug=os.environ.get("FLASK_DEBUG") == "1",
        port=int(os.environ.get("PORT", "5000")),
    )
