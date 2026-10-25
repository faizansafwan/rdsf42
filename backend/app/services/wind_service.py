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

        quality = validate_interval_count(
            [datetime.fromisoformat(r["start_time"].replace("Z", "+00:00")) for r in rows if not r["missing_actual"]],
            range_start=start,
            range_end=end,
        )
        quality["intervals_with_missing_forecast"] = sum(
            1 for r in rows if r["missing_forecast"]
        )
        quality["intervals_with_missing_actual"] = sum(
            1 for r in rows if r["missing_actual"]
        )
        return rows, quality

    def build_metrics(self, start: date, end: date) -> dict:
        rows, _ = self.build_compare(start, end, resolution="30min")
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

    def publish_time_distribution(self, delivery_date: date) -> list[dict]:
        start_dt = datetime(
            delivery_date.year,
            delivery_date.month,
            delivery_date.day,
            0,
            0,
            tzinfo=timezone.utc,
        )
        end_dt = datetime(
            delivery_date.year,
            delivery_date.month,
            delivery_date.day,
            23,
            30,
            tzinfo=timezone.utc,
        )
        forecasts = self.repo.get_forecasts(start_dt, end_dt)
        if not forecasts:
            return []
        df = pd.DataFrame(forecasts)
        df["hour"] = df["publish_time"].dt.hour
        counts = df.groupby("hour").size().reset_index(name="count")
        return [{"hour_utc": int(r.hour), "count": int(r.count)} for r in counts.itertuples()]


def _aggregate_hourly(rows: list[dict]) -> list[dict]:
    if not rows:
        return []
    df = pd.DataFrame(rows)
    df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
    df = df.set_index("start_time").sort_index()
    agg = df.resample("1h").agg(
        {
            "actual_mw": "mean",
            "forecast_mw": "mean",
            "error_mw": "mean",
            "missing_actual": "max",
            "missing_forecast": "max",
        }
    )
    out = []
    for ts, row in agg.iterrows():
        out.append(
            {
                "start_time": ts.isoformat().replace("+00:00", "Z"),
                "actual_mw": None if pd.isna(row["actual_mw"]) else float(row["actual_mw"]),
                "forecast_mw": None if pd.isna(row["forecast_mw"]) else float(row["forecast_mw"]),
                "publish_time": None,
                "error_mw": None if pd.isna(row["error_mw"]) else float(row["error_mw"]),
                "missing_actual": bool(row["missing_actual"]),
                "missing_forecast": bool(row["missing_forecast"]),
            }
        )
    return out
