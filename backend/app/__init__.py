import logging
import os

from flask import Flask
from flask_talisman import Talisman

from app.api.admin_routes import bp as admin_bp
from app.api.routes import bp as wind_bp
from app.config import DevConfig, ProdConfig, TestConfig
from app.data.repository import WindRepository
from app.errors import register_error_handlers
from app.extensions import init_extensions
from app.jobs.scheduler import start_scheduler
from app.services.elexon_client import ElexonClient
from app.services.wind_service import WindService

logging.basicConfig(level=logging.INFO)


def create_app(config_object=None):
    app = Flask(__name__)

    if config_object is None:
        env = os.environ.get("FLASK_ENV", "development")
        config_object = ProdConfig if env == "production" else DevConfig
        if os.environ.get("PYTEST_CURRENT_TEST"):
            config_object = TestConfig

    app.config.from_object(config_object)

    init_extensions(app)
    register_error_handlers(app)

    if not app.config["TESTING"]:
        Talisman(
            app,
            force_https=False,
            content_security_policy=False,
            frame_options="SAMEORIGIN",
        )

    repo = WindRepository(app.config["DATABASE_PATH"])
    repo.init_schema()
    client = ElexonClient(base_url=app.config["ELEXON_API_BASE_URL"])
    wind_service = WindService(
        repo,
        cutoff_local=app.config["DECISION_CUTOFF_LOCAL_TIME"],
        day_offset=app.config["DECISION_DAY_OFFSET"],
        mape_floor_mw=app.config["MAPE_ACTUAL_FLOOR_MW"],
    )

    app.extensions["wind_repo"] = repo
    app.extensions["elexon_client"] = client
    app.extensions["wind_service"] = wind_service

    app.register_blueprint(wind_bp)
    app.register_blueprint(admin_bp)

    if not app.config["TESTING"]:
        start_scheduler(app)
        _maybe_bootstrap_cache(app, repo, client)

    return app


def _maybe_bootstrap_cache(app, repo, client):
    conn = repo.connect()
    row = conn.execute("SELECT COUNT(*) AS c FROM actuals").fetchone()
    if row and row["c"] == 0:
        from app.services.refresh_service import refresh_wind_cache

        try:
            with app.app_context():
                refresh_wind_cache(repo, client)
        except Exception:
            logging.getLogger(__name__).warning(
                "Initial Elexon refresh failed; API will serve empty/stale cache until refresh succeeds"
            )
