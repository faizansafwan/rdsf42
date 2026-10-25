from datetime import datetime, timezone

from app.services.forecast_matching import ForecastCandidate, select_forecast


def _utc(y, m, d, h, mi=0):
    return datetime(y, m, d, h, mi, tzinfo=timezone.utc)


def test_normal_match_picks_latest_before_cutoff():
    start = _utc(2026, 1, 2, 12, 0)
    forecasts = [
        ForecastCandidate(_utc(2026, 1, 1, 8, 0), 100.0),
        ForecastCandidate(_utc(2026, 1, 1, 10, 30), 110.0),
    ]
    chosen = select_forecast(start, forecasts, cutoff_local="11:00")
    assert chosen is not None
    assert chosen.generation_mw == 110.0


def test_multiple_same_day_forecasts():
    start = _utc(2026, 1, 5, 0, 0)
    forecasts = [
        ForecastCandidate(_utc(2026, 1, 4, 6, 0), 200.0),
        ForecastCandidate(_utc(2026, 1, 4, 9, 0), 210.0),
        ForecastCandidate(_utc(2026, 1, 4, 10, 59), 220.0),
    ]
    chosen = select_forecast(start, forecasts)
    assert chosen.generation_mw == 220.0


def test_no_forecast_before_cutoff():
    start = _utc(2026, 1, 3, 0, 0)
    forecasts = [
        ForecastCandidate(_utc(2026, 1, 2, 12, 0), 300.0),
    ]
    assert select_forecast(start, forecasts, cutoff_local="11:00") is None


def test_forecast_exactly_at_cutoff_boundary():
    start = _utc(2026, 1, 10, 0, 0)
    at_cutoff = _utc(2026, 1, 9, 11, 0)
    forecasts = [ForecastCandidate(at_cutoff, 400.0)]
    chosen = select_forecast(start, forecasts, cutoff_local="11:00")
    assert chosen is not None
    assert chosen.generation_mw == 400.0


def test_missing_interval_no_candidates():
    start = _utc(2026, 1, 15, 12, 30)
    assert select_forecast(start, []) is None
