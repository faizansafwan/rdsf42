"""Orchestration: match forecasts, compute compare series and metrics."""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date, datetime, timezone

import pandas as pd

from app.data.repository import WindRepository
from app.services.forecast_matching import (
    ForecastCandidate,
    select_forecast,
    validate_interval_count,
)
from app.services.metrics import compute_metrics

logger = logging.getLogger(__name__)


def _utc_day_bounds(start: date, end: date) -> tuple[datetime, datetime]:
    start_dt = datetime(start.year, start.month, start.day, 0, 0, tzinfo=timezone.utc)
    end_dt = datetime(end.year, end.month, end.day, 23, 30, tzinfo=timezone.utc)
    return start_dt, end_dt


class WindService:
    def __init__(
        self,
        repo: WindRepository,
        *,
        cutoff_local: str,
        day_offset: int,
        mape_floor_mw: float,
    ):
        self.repo = repo
        self.cutoff_local = cutoff_local
        self.day_offset = day_offset
        self.mape_floor_mw = mape_floor_mw

    def build_compare(
        self,
        start: date,
        end: date,
        resolution: str = "30min",
    ) -> tuple[list[dict], dict]:
        start_dt, end_dt = _utc_day_bounds(start, end)
        actuals = self.repo.get_actuals(start_dt, end_dt)
        forecasts = self.repo.get_forecasts(start_dt, end_dt)

        by_start: dict[datetime, list[ForecastCandidate]] = defaultdict(list)
        for f in forecasts:
            by_start[f["start_time"]].append(
                ForecastCandidate(
                    publish_time=f["publish_time"],
                    generation_mw=f["generation_mw"],
                )
            )

        rows: list[dict] = []
        actual_map = {a["start_time"]: a["generation_mw"] for a in actuals}
        all_starts = sorted(set(actual_map.keys()) | set(by_start.keys()))

        for st in all_starts:
            if st < start_dt or st > end_dt:
                continue
            matched = select_forecast(
                st,
                by_start.get(st, []),
                cutoff_local=self.cutoff_local,
                day_offset=self.day_offset,
            )
            actual = actual_map.get(st)
            forecast_mw = matched.generation_mw if matched else None
            publish_time = matched.publish_time if matched else None
            error = None
            if actual is not None and forecast_mw is not None:
                error = actual - forecast_mw
            rows.append(
                {
                    "start_time": st.isoformat().replace("+00:00", "Z"),
                    "actual_mw": actual,
                    "forecast_mw": forecast_mw,
                    "publish_time": (
                        publish_time.isoformat().replace("+00:00", "Z")
                        if publish_time
                        else None
                    ),
                    "error_mw": error,
                    "missing_actual": actual is None,
                    "missing_forecast": matched is None,
                }
            )

        if resolution == "hourly":
            rows = _aggregate_hourly(rows)

        step_minutes = 60 if resolution == "hourly" else 30
        quality = validate_interval_count(
            [datetime.fromisoformat(r["start_time"].replace("Z", "+00:00")) for r in rows if not r["missing_actual"]],
            range_start=start,
            range_end=end,
            expected=_expected_intervals_for_resolution(start, end, resolution),
            step_minutes=step_minutes,
        )
        quality["forecast_granularity_note"] = (
            "Elexon WINDFOR start times are hourly in this dataset; :30 settlement "
            "periods have no native forecast row (shown as gaps at 30-minute resolution)."
            if resolution == "30min"
            else None
        )
        quality["intervals_with_missing_forecast"] = sum(
            1 for r in rows if r["missing_forecast"]
        )
        quality["intervals_with_missing_actual"] = sum(
            1 for r in rows if r["missing_actual"]
        )
        return rows, quality

    def build_metrics(self, start: date, end: date, *, resolution: str = "30min") -> dict:
        rows, _ = self.build_compare(start, end, resolution=resolution)
        pairs = [
            (r["actual_mw"], r["forecast_mw"])
            for r in rows
            if r["actual_mw"] is not None and r["forecast_mw"] is not None
        ]
        actuals = [p[0] for p in pairs]
        forecasts = [p[1] for p in pairs]
        m = compute_metrics(actuals, forecasts, mape_floor_mw=self.mape_floor_mw)
        return {
            "mae": m.mae,
            "rmse": m.rmse,
            "mape": m.mape,
            "smape": m.smape,
            "bias": m.bias,
            "n_points": m.n_points,
            "mape_excluded_count": m.mape_excluded_count,
            "mape_floor_mw": m.mape_floor_mw,
            "error_convention": "actual_minus_forecast",
        }

    def publish_time_distribution(self, delivery_date: date) -> dict:
        from collections import Counter
        from zoneinfo import ZoneInfo

        from app.services.forecast_matching import (
            TZ,
            TZ_NAME,
            ForecastCandidate,
            decision_cutoff_utc,
            select_forecast,
        )

        start_dt, end_dt = _utc_day_bounds(delivery_date, delivery_date)
        forecasts = self.repo.get_forecasts(start_dt, end_dt)
        empty = {
            "delivery_date": delivery_date.isoformat(),
            "decision_cutoff_local_time": self.cutoff_local,
            "decision_timezone": TZ_NAME,
            "decision_day_offset": self.day_offset,
            "cutoff_utc": None,
            "cutoff_chart_label": None,
            "selected_publish_time_utc": None,
            "x_axis_caption": "Distinct publish times observed (local clock)",
            "buckets": [],
        }
        if not forecasts:
            return empty

        by_start: dict[datetime, list[ForecastCandidate]] = defaultdict(list)
        for f in forecasts:
            by_start[f["start_time"]].append(
                ForecastCandidate(
                    publish_time=f["publish_time"],
                    generation_mw=f["generation_mw"],
                )
            )

        selected_publish_times: set[datetime] = set()
        for st, candidates in by_start.items():
            matched = select_forecast(
                st,
                candidates,
                cutoff_local=self.cutoff_local,
                day_offset=self.day_offset,
            )
            if matched:
                selected_publish_times.add(matched.publish_time)

        sample_start = datetime(
            delivery_date.year,
            delivery_date.month,
            delivery_date.day,
            12,
            0,
            tzinfo=timezone.utc,
        )
        cutoff_utc = decision_cutoff_utc(
            sample_start,
            cutoff_local=self.cutoff_local,
            day_offset=self.day_offset,
        )
        tz = TZ if isinstance(TZ, ZoneInfo) else ZoneInfo(TZ_NAME)
        cutoff_chart_label = cutoff_utc.astimezone(tz).strftime("%H:%M %Z")

        pub_counter = Counter(f["publish_time"] for f in forecasts)
        buckets: list[dict] = []
        for pub_time, count in sorted(pub_counter.items(), key=lambda x: x[0]):
            if pub_time in selected_publish_times:
                role = "selected"
            elif pub_time <= cutoff_utc:
                role = "eligible_not_selected"
            else:
                role = "after_cutoff"
            buckets.append(
                {
                    "publish_time_utc": pub_time.isoformat().replace("+00:00", "Z"),
                    "label": pub_time.astimezone(tz).strftime("%H:%M %Z"),
                    "count": count,
                    "role": role,
                }
            )

        primary_selected = max(selected_publish_times) if selected_publish_times else None
        return {
            **empty,
            "cutoff_utc": cutoff_utc.isoformat().replace("+00:00", "Z"),
            "cutoff_chart_label": cutoff_chart_label,
            "selected_publish_time_utc": (
                primary_selected.isoformat().replace("+00:00", "Z")
                if primary_selected
                else None
            ),
            "buckets": buckets,
        }


def _expected_intervals_for_resolution(start: date, end: date, resolution: str) -> int:
    days = (end - start).days + 1
    return days * 24 if resolution == "hourly" else days * 48


def _aggregate_hourly(rows: list[dict]) -> list[dict]:
    if not rows:
        return []
    df = pd.DataFrame(rows)
    df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
    df = df.set_index("start_time").sort_index()
    out = []
    for ts, group in df.resample("1h"):
        actual_vals = group["actual_mw"].dropna()
        forecast_vals = group["forecast_mw"].dropna()
        missing_actual = bool(group["missing_actual"].any())
        has_any_forecast = len(forecast_vals) > 0

        actual_mw = float(actual_vals.mean()) if len(actual_vals) else None
        forecast_mw = float(forecast_vals.mean()) if has_any_forecast else None

        error_mw = None
        if actual_mw is not None and forecast_mw is not None:
            error_mw = actual_mw - forecast_mw

        out.append(
            {
                "start_time": ts.isoformat().replace("+00:00", "Z"),
                "actual_mw": actual_mw,
                "forecast_mw": forecast_mw,
                "publish_time": None,
                "error_mw": error_mw,
                "missing_actual": missing_actual,
                "missing_forecast": not has_any_forecast,
            }
        )
    return out
