from __future__ import annotations

from datetime import datetime
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

from backend.emailer import send_email
from backend.models import Reminder, UserConfig, db


logger = logging.getLogger(__name__)


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
    if reminder.client:
        client = reminder.client
        lines.append("Dane klienta:")
        lines.append(f" - Imię i nazwisko: {client.imie} {client.nazwisko}")
        if client.email:
            lines.append(f" - Email: {client.email}")
        if client.telefon:
            lines.append(f" - Telefon: {client.telefon}")
        if client.adres:
            lines.append(f" - Adres: {client.adres}")
    if reminder.policy:
        policy = reminder.policy
        lines.append("Dane polisy:")
        lines.append(f" - Numer polisy: {policy.numer_polisy}")
        if policy.produkt:
            lines.append(f" - Produkt: {policy.produkt}")
        if policy.data_poczatku:
            lines.append(f" - Data początku: {policy.data_poczatku:%Y-%m-%d}")
        if policy.data_konca:
            lines.append(f" - Data końca: {policy.data_konca:%Y-%m-%d}")
        if policy.skladka is not None:
            lines.append(f" - Składka: {policy.skladka}")
        if policy.status:
            lines.append(f" - Status: {policy.status}")
    return "\n".join(lines)


def _get_agent_recipient(app: Flask) -> str | None:
    with app.app_context():
        try:
            user_config = UserConfig.query.first()
        except Exception:
            logger.exception("Failed to load UserConfig for reminder recipient")
            user_config = None

        recipient = user_config.email if user_config and user_config.email else None
        if recipient:
            return recipient

        return app.config.get("MAIL_DEFAULT_SENDER")


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

        recipient = _get_agent_recipient(app)
        if not recipient:
            logger.warning("No agent email configured for reminders")
            return

        for reminder in reminders:

            subject = "Przypomnienie"
            body = _build_reminder_body(reminder)
            sent = send_email(subject, body, recipient)
            if sent:
                reminder.wyslano = True

        db.session.commit()


def init_scheduler(app: Flask) -> BackgroundScheduler:
    send_hour = _get_send_hour(app)
    scheduler = BackgroundScheduler()
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
