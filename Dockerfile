# EzClass production image: Flask app served by gunicorn.
# Works the same on Render, Fly or AWS (ECS / App Runner): they all
# set $PORT and run this image. See README "Deploying it".
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# install dependencies first so code changes don't redo this layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY frontend ./frontend
COPY data ./data

# Bake the class database into the image. The app only reads it, so a
# redeploy just ships a fresh copy. (Visit counts are different: they need a
# volume, see ANALYTICS_DB_PATH in .env.example.)
RUN python -m backend.models.db data/cleaned

# non-root user that owns /app, so it can write analytics.db and lock files.
# /data is where a volume for visit counts gets mounted (ANALYTICS_DB_PATH=/data/analytics.db);
# creating it here means a Docker named volume starts out owned by that user too.
RUN useradd --create-home --uid 1000 ezclass \
    && mkdir -p /data \
    && chown -R ezclass:ezclass /app /data
USER ezclass

EXPOSE 8000
# sh -c so ${PORT} gets filled in; exec so gunicorn (not sh) receives the stop signal.
# The access log format leaves out the client IP, user agent and query string
# (search boxes put typed professor/keyword text in the URL), per the privacy rules.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 4 --access-logfile - --access-logformat '%(t)s \"%(m)s %(U)s\" %(s)s %(b)s %(M)sms' backend.app:app"]
