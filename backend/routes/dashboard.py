from __future__ import annotations

from datetime import datetime, time, timedelta
import logging
from zoneinfo import ZoneInfo

from flask import Blueprint, render_template

from backend.auth import auth_required
from backend.config import Config
from backend.models import Reminder

dashboard_bp = Blueprint("dashboard", __name__)
logger = logging.getLogger(__name__)


def _get_timezone() -> ZoneInfo:
    try:
        return ZoneInfo(Config.TIMEZONE)
    except Exception:
        logger.exception("Invalid TIMEZONE configuration: %s", Config.TIMEZONE)
        return ZoneInfo("UTC")


def _local_now_naive() -> datetime:
    return datetime.now(_get_timezone()).replace(tzinfo=None)


def _serialize_reminder(reminder: Reminder, status_label: str, status_class: str) -> dict:
    return {
        "reminder": reminder,
        "status_label": status_label,
        "status_class": status_class,
    }


@dashboard_bp.get("/dashboard")
@auth_required
def dashboard() -> str:
    now = _local_now_naive()
    today = now.date()
    start_today = datetime.combine(today, time.min)
    end_today = datetime.combine(today, time.max)
    tomorrow_start = datetime.combine(today + timedelta(days=1), time.min)
    next_seven_end = datetime.combine(today + timedelta(days=7), time.max)

    overdue = (
        Reminder.query.filter(Reminder.data_przypomnienia < start_today)
        .filter_by(wyslano=False)
        .order_by(Reminder.data_przypomnienia.asc())
        .all()
    )
    today_reminders = (
        Reminder.query.filter(Reminder.data_przypomnienia.between(start_today, end_today))
        .filter_by(wyslano=False)
        .order_by(Reminder.data_przypomnienia.asc())
        .all()
    )
    next_seven = (
        Reminder.query.filter(Reminder.data_przypomnienia.between(tomorrow_start, next_seven_end))
        .filter_by(wyslano=False)
        .order_by(Reminder.data_przypomnienia.asc())
        .all()
    )

    return render_template(
        "dashboard.html",
        overdue=[_serialize_reminder(reminder, "Zaległe", "status-overdue") for reminder in overdue],
        today=[
            _serialize_reminder(reminder, "Dziś", "status-today")
            for reminder in today_reminders
        ],
        upcoming=[
            _serialize_reminder(reminder, "Następne 7 dni", "status-upcoming")
            for reminder in next_seven
        ],
    )
