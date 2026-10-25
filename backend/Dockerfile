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
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
