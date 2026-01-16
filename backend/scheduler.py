from __future__ import annotations

from datetime import datetime
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

from backend.emailer import send_email
from backend.models import Reminder, db


logger = logging.getLogger(__name__)


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
        now = datetime.utcnow()
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
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        send_due_reminders,
        "cron",
        hour=8,
        minute=0,
        args=[app],
        id="daily_reminder_sender",
        replace_existing=True,
    )
    scheduler.start()
    return scheduler
