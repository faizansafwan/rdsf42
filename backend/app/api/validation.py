"""Query parameter validation for wind API routes."""

from __future__ import annotations

import re
from datetime import date, datetime

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MIN_DATE = date(2026, 1, 1)
MAX_DATE = date(2026, 1, 31)


def parse_date_param(name: str, value: str | None) -> date:
    if not value or not DATE_RE.match(value):
        raise ValueError(f"Invalid {name}: use YYYY-MM-DD")
    d = datetime.strptime(value, "%Y-%m-%d").date()
    if d < MIN_DATE or d > MAX_DATE:
        raise ValueError(f"{name} must be within January 2026")
    return d


def parse_date_range(start: str | None, end: str | None) -> tuple[date, date]:
    s = parse_date_param("start", start)
    e = parse_date_param("end", end)
    if e < s:
        raise ValueError("end must be on or after start")
    return s, e


def parse_resolution(value: str | None) -> str:
    r = (value or "30min").lower()
    if r not in ("30min", "hourly"):
        raise ValueError("resolution must be 30min or hourly")
    return r
