"""Ingest Elexon data into SQLite with stale-cache metadata."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.data.repository import META_LAST_UPDATED, META_STALE, WindRepository
from app.services.elexon_client import ElexonClient

logger = logging.getLogger(__name__)

ACTUALS_FROM = "2026-01-01"
ACTUALS_TO = "2026-01-31"
FORECASTS_PUBLISH_FROM = "2025-12-31T00:00:00Z"
FORECASTS_PUBLISH_TO = "2026-01-31T23:59:59Z"


def refresh_wind_cache(
    repo: WindRepository,
    client: ElexonClient,
    *,
    mark_stale_on_failure: bool = True,
) -> dict:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        actuals = client.fetch_wind_actuals(ACTUALS_FROM, ACTUALS_TO)
        forecasts = client.fetch_wind_forecasts(
            FORECASTS_PUBLISH_FROM, FORECASTS_PUBLISH_TO
        )
        n_a = repo.upsert_actuals(actuals)
        n_f = repo.upsert_forecasts(forecasts)
        repo.set_meta(META_LAST_UPDATED, now)
        repo.set_meta(META_STALE, "false")
        logger.info("Refresh OK: %s actuals, %s forecast rows", n_a, n_f)
        return {
            "ok": True,
            "actuals_upserted": n_a,
            "forecasts_upserted": n_f,
            "last_updated": now,
            "stale": False,
        }
    except Exception as exc:
        logger.exception("Refresh failed: %s", exc)
        if mark_stale_on_failure:
            repo.set_meta(META_STALE, "true")
            if not repo.get_meta(META_LAST_UPDATED):
                repo.set_meta(META_LAST_UPDATED, now)
        raise
