"""D-1 day-ahead forecast selection — pure functions, no I/O."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, time, timezone
from zoneinfo import ZoneInfo

DECISION_CUTOFF_LOCAL_TIME = "11:00"
DECISION_DAY_OFFSET = -1
TZ_NAME = "Europe/London"
TZ = ZoneInfo(TZ_NAME)

JANUARY_2026_INTERVALS = 31 * 48  # 1,488 half-hour periods


@dataclass(frozen=True)
class ForecastCandidate:
    publish_time: datetime
    generation_mw: float


def _parse_cutoff_time(cutoff_str: str) -> time:
    parts = cutoff_str.strip().split(":")
    return time(int(parts[0]), int(parts[1]))


def decision_cutoff_utc(
    start_time_utc: datetime,
    *,
    cutoff_local: str = DECISION_CUTOFF_LOCAL_TIME,
    day_offset: int = DECISION_DAY_OFFSET,
    tz: ZoneInfo = TZ,
) -> datetime:
    if start_time_utc.tzinfo is None:
        raise ValueError("start_time_utc must be timezone-aware UTC")
    local_start = start_time_utc.astimezone(tz)
    decision_day = local_start.date() + timedelta(days=day_offset)
    cutoff_t = _parse_cutoff_time(cutoff_local)
    cutoff_local_dt = datetime.combine(decision_day, cutoff_t, tzinfo=tz)
    return cutoff_local_dt.astimezone(timezone.utc)


def select_forecast(
    start_time_utc: datetime,
    forecasts_for_interval: list[ForecastCandidate],
    *,
    cutoff_local: str = DECISION_CUTOFF_LOCAL_TIME,
    day_offset: int = DECISION_DAY_OFFSET,
) -> ForecastCandidate | None:
    cutoff_utc = decision_cutoff_utc(
        start_time_utc, cutoff_local=cutoff_local, day_offset=day_offset
    )
    candidates = [f for f in forecasts_for_interval if f.publish_time <= cutoff_utc]
    if not candidates:
        return None
    return max(candidates, key=lambda f: f.publish_time)


def validate_interval_count(
    start_times: list[datetime],
    *,
    expected: int | None = None,
    range_start: date | None = None,
    range_end: date | None = None,
    step_minutes: int = 30,
) -> dict:
    """Report gaps and duplicates for a set of settlement intervals."""
    if range_start and range_end:
        if expected is None:
            expected = _expected_intervals_in_range(range_start, range_end, step_minutes)
    elif expected is None:
        expected = JANUARY_2026_INTERVALS

    normalized = []
    for t in start_times:
        if t.tzinfo is None:
            normalized.append(t.replace(tzinfo=timezone.utc))
        else:
            normalized.append(t.astimezone(timezone.utc))

    unique = sorted(set(normalized))
    duplicates = len(normalized) - len(unique)
    missing: list[str] = []
    if range_start and range_end:
        expected_set = _generate_expected_starts(range_start, range_end, step_minutes)
        present = set(unique)
        for exp in expected_set:
            if exp not in present:
                missing.append(exp.isoformat())

    return {
        "expected_count": expected,
        "actual_count": len(unique),
        "duplicate_count": duplicates,
        "missing_count": len(missing),
        "missing_intervals": missing[:20],
    }


def _expected_intervals_in_range(start: date, end: date, step_minutes: int = 30) -> int:
    days = (end - start).days + 1
    periods_per_day = (24 * 60) // step_minutes
    return days * periods_per_day


def _generate_expected_starts(
    start: date, end: date, step_minutes: int = 30
) -> list[datetime]:
    out: list[datetime] = []
    periods_per_day = (24 * 60) // step_minutes
    d = start
    while d <= end:
        for period in range(periods_per_day):
            minutes = period * step_minutes
            hour, minute = divmod(minutes, 60)
            ts = datetime(d.year, d.month, d.day, hour, minute, tzinfo=timezone.utc)
            out.append(ts)
        d += timedelta(days=1)
    return out
