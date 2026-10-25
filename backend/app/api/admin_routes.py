from flask import Blueprint, current_app, jsonify, request

from app.extensions import limiter
from app.services.refresh_service import refresh_wind_cache

bp = Blueprint("admin_api", __name__, url_prefix="/api/admin")


def _check_admin_secret() -> bool:
    expected = current_app.config.get("ADMIN_REFRESH_SECRET") or ""
    if not expected:
        return False
    provided = request.headers.get("X-Admin-Secret", "")
    return provided == expected


@bp.post("/refresh")
@limiter.limit("10 per hour")
def admin_refresh():
    if not _check_admin_secret():
        return jsonify({"error": "Unauthorized"}), 401

    repo = current_app.extensions["wind_repo"]
    client = current_app.extensions["elexon_client"]
    try:
        result = refresh_wind_cache(repo, client)
        return jsonify(result)
    except Exception:
        stale, last_updated = repo.cache_status()
        return (
            jsonify(
                {
                    "ok": False,
                    "stale": stale,
                    "last_updated": last_updated,
                    "error": "Refresh failed; serving cached data if available",
                }
            ),
            502,
        )
