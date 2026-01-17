from __future__ import annotations

from datetime import datetime
import logging
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

from backend.config import Config
from backend.emailer import send_email
from backend.models import Reminder, UserConfig, db


logger = logging.getLogger(__name__)


def _get_timezone() -> ZoneInfo:
    try:
        return ZoneInfo(Config.TIMEZONE)
    except Exception:
        logger.exception("Invalid TIMEZONE configuration: %s", Config.TIMEZONE)
        return ZoneInfo("UTC")


def _local_now_naive() -> datetime:
    return datetime.now(_get_timezone()).replace(tzinfo=None)


def _get_send_hour(app: Flask) -> int:
    with app.app_context():
        try:
            user_config = UserConfig.query.first()
        except Exception:
            logger.exception("Failed to load UserConfig for scheduler")
            user_config = None

    send_hour = user_config.send_hour if user_config and user_config.send_hour is not None else 8
    if not isinstance(send_hour, int) or not 0 <= send_hour <= 23:
        return 8
    return send_hour


def _build_reminder_body(reminder: Reminder) -> str:
    lines = [
        f"Przypomnienie: {reminder.tresc}",
        f"Data przypomnienia: {reminder.data_przypomnienia:%Y-%m-%d %H:%M}",
    ]
    if reminder.policy:
        lines.append(f"Polisa: {reminder.policy.numer_polisy}")
    return "\n".join(lines)


def send_due_reminders(app: Flask) -> None:
    with app.app_context():
        now = _local_now_naive()
        reminders = (
            Reminder.query.filter(
                Reminder.wyslano.is_(False),
                Reminder.data_przypomnienia <= now,
            )
            .order_by(Reminder.data_przypomnienia.asc())
            .all()
        )

        if not reminders:
            logger.info("No reminders to send")
            return

        for reminder in reminders:
            recipient = reminder.client.email if reminder.client else None
            if not recipient:
                logger.warning("Reminder %s has no recipient email", reminder.id)
                continue

            subject = "Przypomnienie"
            body = _build_reminder_body(reminder)
            sent = send_email(subject, body, recipient)
            if sent:
                reminder.wyslano = True

        db.session.commit()


def init_scheduler(app: Flask) -> BackgroundScheduler:
    send_hour = _get_send_hour(app)
    scheduler = BackgroundScheduler(timezone=_get_timezone())
    scheduler.add_job(
        send_due_reminders,
        "cron",
        hour=send_hour,
        minute=0,
        args=[app],
        id="daily_reminder_sender",
        replace_existing=True,
    )
    scheduler.start()
    return scheduler
