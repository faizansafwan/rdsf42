"""Fetch and parse Elexon BMRS FUELHH / WINDFOR stream endpoints."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"


class ElexonClientError(Exception):
    pass


def _parse_iso(ts: str) -> datetime:
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_fuelhh_rows(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in raw:
        if item.get("fuelType") != "WIND":
            continue
        rows.append(
            {
                "start_time": _parse_iso(item["startTime"]),
                "generation_mw": float(item["generation"]),
            }
        )
    return rows


def parse_windfor_rows(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in raw:
        rows.append(
            {
                "start_time": _parse_iso(item["startTime"]),
                "publish_time": _parse_iso(item["publishTime"]),
                "generation_mw": float(item["generation"]),
            }
        )
    return rows


class ElexonClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL, session: requests.Session | None = None):
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()

    @retry(
        retry=retry_if_exception_type((requests.RequestException, ElexonClientError)),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=8),
        stop=stop_after_attempt(4),
        reraise=True,
    )
    def _get_json_array(self, path: str, params: dict[str, str]) -> list[dict[str, Any]]:
        url = f"{self.base_url}{path}"
        resp = self.session.get(url, params=params, timeout=60)
        if resp.status_code >= 400:
            raise ElexonClientError(f"Elexon HTTP {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        if not isinstance(data, list):
            raise ElexonClientError("Expected bare JSON array from Elexon stream endpoint")
        return data

    def fetch_wind_actuals(
        self,
        settlement_date_from: str,
        settlement_date_to: str,
    ) -> list[dict[str, Any]]:
        raw = self._get_json_array(
            "/datasets/FUELHH/stream",
            {
                "fuelType": "WIND",
                "settlementDateFrom": settlement_date_from,
                "settlementDateTo": settlement_date_to,
            },
        )
        return parse_fuelhh_rows(raw)

    def fetch_wind_forecasts(
        self,
        publish_datetime_from: str,
        publish_datetime_to: str,
    ) -> list[dict[str, Any]]:
        raw = self._get_json_array(
            "/datasets/WINDFOR/stream",
            {
                "publishDateTimeFrom": publish_datetime_from,
                "publishDateTimeTo": publish_datetime_to,
            },
        )
        return parse_windfor_rows(raw)
