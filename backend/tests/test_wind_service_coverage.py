from datetime import date

from app import create_app
from app.config import TestConfig


def test_january_30min_coverage_and_granularity_gaps():
    app = create_app(TestConfig)
    with app.app_context():
        svc = app.extensions["wind_service"]
        repo = app.extensions["wind_repo"]
        from datetime import datetime, timezone

        repo.upsert_actuals(
            [
                {
                    "start_time": datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc),
                    "generation_mw": 1000.0,
                },
                {
                    "start_time": datetime(2026, 1, 1, 0, 30, tzinfo=timezone.utc),
                    "generation_mw": 1100.0,
                },
            ]
        )
        repo.upsert_forecasts(
            [
                {
                    "start_time": datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc),
                    "publish_time": datetime(2025, 12, 31, 10, 0, tzinfo=timezone.utc),
                    "generation_mw": 900.0,
                }
            ]
        )
        rows, quality = svc.build_compare(date(2026, 1, 1), date(2026, 1, 1), "30min")
        assert quality["expected_count"] == 48
        assert quality["matched_for_metrics"] == 1
        assert quality["gaps_hourly_granularity"] == 1
        assert any(r["gap_reason"] == "hourly_forecast_granularity" for r in rows)

        metrics = svc.build_metrics(date(2026, 1, 1), date(2026, 1, 1), resolution="30min")
        assert metrics["n_points"] == 1
        assert metrics["expected_intervals"] == 48
        assert metrics["matched_intervals"] == 1


def test_hourly_aggregation_keeps_publish_time():
    app = create_app(TestConfig)
    with app.app_context():
        svc = app.extensions["wind_service"]
        repo = app.extensions["wind_repo"]
        from datetime import datetime, timezone

        pub = datetime(2025, 12, 31, 10, 0, tzinfo=timezone.utc)
        for minute in (0, 30):
            repo.upsert_actuals(
                [
                    {
                        "start_time": datetime(2026, 1, 1, 0, minute, tzinfo=timezone.utc),
                        "generation_mw": 1000.0 + minute,
                    }
                ]
            )
        repo.upsert_forecasts(
            [
                {
                    "start_time": datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc),
                    "publish_time": pub,
                    "generation_mw": 900.0,
                }
            ]
        )
        rows, _ = svc.build_compare(date(2026, 1, 1), date(2026, 1, 1), "hourly")
        assert len(rows) == 1
        assert rows[0]["publish_time"] is not None
        assert "2025-12-31" in rows[0]["publish_time"]
