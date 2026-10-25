"""Forecast accuracy metrics — pure functions."""

from __future__ import annotations

import math
from dataclasses import dataclass

# Intervals with actual generation below this floor are excluded from MAPE/SMAPE
# (documented in API responses and UI).
MAPE_ACTUAL_FLOOR_MW = 50.0


@dataclass
class MetricsResult:
    mae: float | None
    rmse: float | None
    mape: float | None
    smape: float | None
    bias: float | None
    n_points: int
    mape_excluded_count: int
    mape_floor_mw: float


def compute_metrics(
    actuals: list[float],
    forecasts: list[float],
    *,
    mape_floor_mw: float = MAPE_ACTUAL_FLOOR_MW,
) -> MetricsResult:
    if len(actuals) != len(forecasts):
        raise ValueError("actuals and forecasts must have the same length")
    n = len(actuals)
    if n == 0:
        return MetricsResult(
            mae=None,
            rmse=None,
            mape=None,
            smape=None,
            bias=None,
            n_points=0,
            mape_excluded_count=0,
            mape_floor_mw=mape_floor_mw,
        )

    errors = [a - f for a, f in zip(actuals, forecasts, strict=True)]
    abs_errors = [abs(e) for e in errors]

    mae = sum(abs_errors) / n
    rmse = math.sqrt(sum(e * e for e in errors) / n)
    bias = sum(errors) / n

    pct_pairs = [
        (a, f)
        for a, f in zip(actuals, forecasts, strict=True)
        if abs(a) >= mape_floor_mw
    ]
    mape_excluded = n - len(pct_pairs)

    mape = None
    smape = None
    if pct_pairs:
        mape_vals = [abs(a - f) / abs(a) * 100 for a, f in pct_pairs]
        mape = sum(mape_vals) / len(mape_vals)
        smape_vals = [
            abs(a - f) / (abs(a) + abs(f)) * 200 for a, f in pct_pairs
        ]
        smape = sum(smape_vals) / len(smape_vals)

    return MetricsResult(
        mae=mae,
        rmse=rmse,
        mape=mape,
        smape=smape,
        bias=bias,
        n_points=n,
        mape_excluded_count=mape_excluded,
        mape_floor_mw=mape_floor_mw,
    )
