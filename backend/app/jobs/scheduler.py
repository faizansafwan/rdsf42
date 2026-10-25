import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.services.refresh_service import refresh_wind_cache

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def start_scheduler(app):
    if not app.config.get("SCHEDULER_ENABLED"):
        return

    def job():
        with app.app_context():
            repo = app.extensions["wind_repo"]
            client = app.extensions["elexon_client"]
            try:
                refresh_wind_cache(repo, client)
            except Exception:
                logger.exception("Scheduled refresh failed")

    hour = app.config["REFRESH_CRON_HOUR"]
    minute = app.config["REFRESH_CRON_MINUTE"]
    scheduler.add_job(job, "cron", hour=hour, minute=minute, id="daily_refresh")
    scheduler.start()
    logger.info("Scheduler started (daily refresh at %02d:%02d UTC)", hour, minute)
