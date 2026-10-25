from flask import Blueprint, current_app, jsonify, request

from app.api.validation import parse_date_param, parse_date_range, parse_resolution
from app.extensions import limiter

bp = Blueprint("wind_api", __name__, url_prefix="/api")


def _envelope(payload: dict) -> dict:
    repo = current_app.extensions["wind_repo"]
    stale, last_updated = repo.cache_status()
    return {"stale": stale, "last_updated": last_updated, **payload}


@bp.get("/health")
@limiter.limit("300 per minute")
def health():
    return jsonify({"status": "ok"})


@bp.get("/wind/compare")
@limiter.limit("120 per minute")
def wind_compare():
    try:
        start, end = parse_date_range(request.args.get("start"), request.args.get("end"))
        resolution = parse_resolution(request.args.get("resolution"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    svc = current_app.extensions["wind_service"]
    rows, quality = svc.build_compare(start, end, resolution=resolution)
    return jsonify(_envelope({"data": rows, "quality": quality}))


@bp.get("/wind/metrics")
@limiter.limit("120 per minute")
def wind_metrics():
    try:
        start, end = parse_date_range(request.args.get("start"), request.args.get("end"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    svc = current_app.extensions["wind_service"]
    metrics = svc.build_metrics(start, end)
    return jsonify(_envelope({"metrics": metrics}))


@bp.get("/wind/publish-time-distribution")
@limiter.limit("120 per minute")
def publish_time_distribution():
    try:
        d = parse_date_param("date", request.args.get("date"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    svc = current_app.extensions["wind_service"]
    histogram = svc.publish_time_distribution(d)
    return jsonify(_envelope({"histogram": histogram, "date": d.isoformat()}))
