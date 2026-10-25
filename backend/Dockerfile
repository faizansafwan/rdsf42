FROM python:3.12-slim

WORKDIR /app

RUN useradd --create-home appuser
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser
ENV FLASK_APP=wsgi:app
ENV FLASK_ENV=production
ENV DATABASE_PATH=/app/data/wind.db

EXPOSE 5000
# Render (and Heroku) set PORT; default 5000 for local Docker.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --threads 2 --timeout 120 wsgi:app"]
