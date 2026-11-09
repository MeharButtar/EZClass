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

import datetime
import gzip
import json
import os
import sys

# allow "from backend.models..." imports to work when running this file
# directly (python3 backend/app.py) from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, Response, jsonify, redirect, request, send_from_directory

from backend.models.db import CLEANED_DIR, ensure_database, get_connection
from backend.routes.analytics import analytics_bp
from backend.routes.feedback import feedback_bp
from backend.routes.majors import majors_bp
from backend.routes.sections import sections_bp
from backend.routes.schedule import schedule_bp

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

# build the class database if this is a fresh machine/container (never wipes existing data)
ensure_database()

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

app.register_blueprint(sections_bp)
app.register_blueprint(schedule_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(majors_bp)
app.register_blueprint(feedback_bp)

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


# Text answers (the section list is 1.6 MB of JSON) are gzipped for browsers that
# accept it; that's most of the download on a phone.
COMPRESSIBLE = ("application/json", "text/html", "text/css", "text/javascript", "application/javascript",
                "image/svg+xml", "text/plain", "application/xml")
MIN_COMPRESS_BYTES = 1024


@app.after_request
def compress(response):
    if ("gzip" not in request.headers.get("Accept-Encoding", "").lower() or response.status_code != 200
            or response.mimetype not in COMPRESSIBLE or "Content-Encoding" in response.headers):
        return response
    if response.direct_passthrough:              # a static file: read it so it can be compressed
        response.direct_passthrough = False
    elif response.is_streamed:                   # a real stream: leave it alone
        return response
    data = response.get_data()
    if len(data) < MIN_COMPRESS_BYTES:
        return response
    response.set_data(gzip.compress(data, compresslevel=6))
    response.headers["Content-Encoding"] = "gzip"
    response.headers.add("Vary", "Accept-Encoding")
    etag, weak = response.get_etag()
    if etag:
        response.set_etag(etag, weak=True)       # same content, different bytes
    return response


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


# Pages, so /search, /major and so on open the right page (shared links, typed URLs).
PAGES = ("major", "ge", "search", "schedule", "reviews", "support")


@app.route("/<any(major, ge, search, schedule, reviews, support):page>")
@app.route("/<any(major, ge, search, schedule, reviews, support):page>/")
def clean_url(page):
    query = request.query_string.decode("utf-8", "ignore")
    return redirect(f"/{page}.html" + (f"?{query}" if query else ""), code=301)


@app.errorhandler(404)
def not_found(error):
    # the API answers in JSON; everything else gets a page with a way back
    if request.path.startswith("/api/"):
        return jsonify({"error": "not found"}), 404
    return send_from_directory(FRONTEND_DIR, "404.html"), 404


@app.errorhandler(405)
def wrong_method(error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "method not allowed"}), 405
    return error


# ---------- search engines ----------

def site_url():
    """https://<host>/ as the visitor sees it (Render ends HTTPS in front of the app). SITE_URL wins if set."""
    configured = os.environ.get("SITE_URL", "").strip().rstrip("/")
    if configured:
        return configured + "/"
    scheme = request.headers.get("X-Forwarded-Proto", request.scheme).split(",")[0].strip() or "https"
    return f"{scheme}://{request.host}/"


@app.route("/robots.txt")
def robots():
    body = f"User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {site_url()}sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    base = site_url()
    urls = [base] + [f"{base}{page}.html" for page in PAGES]
    body = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls)
            + "</urlset>\n")
    return Response(body, mimetype="application/xml")


@app.route("/favicon.ico")
def favicon():
    return redirect("/favicon.svg", code=301)


@app.route("/api/health")
def health():
    try:
        conn = get_connection()
        conn.execute("SELECT 1").fetchone()
        conn.close()
    except Exception:
        return {"status": "error"}, 503
    return {"status": "ok"}


# The importer writes the day it ran into data/cleaned/data_info.json, so the
# site can say how current the class data is. Missing or odd file -> null.
DATA_INFO_PATH = os.path.join(CLEANED_DIR, "data_info.json")


@app.route("/api/info")
def info():
    updated = None
    try:
        with open(DATA_INFO_PATH, encoding="utf-8") as f:
            value = json.load(f).get("updated")
        updated = datetime.date.fromisoformat(value).isoformat()
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    return {"data_updated": updated}


if __name__ == "__main__":
    app.run(
        debug=os.environ.get("FLASK_DEBUG") == "1",
        port=int(os.environ.get("PORT", "5000")),
    )
