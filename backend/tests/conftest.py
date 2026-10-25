from datetime import datetime, timezone

import pytest

from app import create_app
from app.config import TestConfig
from app.data.repository import WindRepository


@pytest.fixture
def app():
    application = create_app(TestConfig)
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seeded_repo(app):
    repo: WindRepository = app.extensions["wind_repo"]
    repo.upsert_actuals(
        [
            {
                "start_time": datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc),
                "generation_mw": 5000.0,
            },
            {
                "start_time": datetime(2026, 1, 1, 0, 30, tzinfo=timezone.utc),
                "generation_mw": 5100.0,
            },
        ]
    )
    repo.upsert_forecasts(
        [
            {
                "start_time": datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc),
                "publish_time": datetime(2025, 12, 31, 10, 0, tzinfo=timezone.utc),
                "generation_mw": 4800.0,
            },
            {
                "start_time": datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc),
                "publish_time": datetime(2025, 12, 31, 12, 0, tzinfo=timezone.utc),
                "generation_mw": 4900.0,
            },
            {
                "start_time": datetime(2026, 1, 1, 0, 30, tzinfo=timezone.utc),
                "publish_time": datetime(2025, 12, 31, 10, 30, tzinfo=timezone.utc),
                "generation_mw": 5000.0,
            },
        ]
    )
    repo.set_meta("last_updated", "2026-01-02T00:00:00Z")
    repo.set_meta("stale", "false")
    return repo
