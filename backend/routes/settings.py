from __future__ import annotations

import logging

from flask import Blueprint, current_app, redirect, render_template, request, url_for

from backend.emailer import send_email
from backend.models import UserConfig, db
from backend.routes.utils import clean_str, to_int, validate_email


logger = logging.getLogger(__name__)

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


def _get_user_config() -> UserConfig | None:
    try:
        return UserConfig.query.first()
    except Exception:
        logger.exception("Failed to load UserConfig")
        return None


def _build_form_data(user_config: UserConfig | None) -> dict[str, str | bool]:
    config = current_app.config

    return {
        "mail_server": user_config.mail_server if user_config else config.get("MAIL_SERVER", ""),
        "mail_port": str(
            user_config.mail_port if user_config and user_config.mail_port is not None else config.get("MAIL_PORT", "")
        ),
        "mail_use_tls": user_config.mail_use_tls
        if user_config and user_config.mail_use_tls is not None
        else bool(config.get("MAIL_USE_TLS", True)),
        "mail_username": user_config.mail_username if user_config else config.get("MAIL_USERNAME", ""),
        "mail_password": "",
        "notification_email": user_config.email if user_config else "",
        "send_hour": str(user_config.send_hour if user_config else 8),
    }


def _reschedule_daily_job(send_hour: int) -> None:
    scheduler = getattr(current_app, "scheduler", None)
    if not scheduler:
        return
    try:
        scheduler.reschedule_job(
            "daily_reminder_sender",
            trigger="cron",
            hour=send_hour,
            minute=0,
        )
    except Exception:
        logger.exception("Failed to reschedule daily reminder sender")


@settings_bp.route("/", methods=["GET", "POST"])
def settings_view() -> str:
    errors: dict[str, str] = {}
    message = ""
    message_type = ""

    user_config = _get_user_config()
    form_data = _build_form_data(user_config)

    status = request.args.get("status")
    if status == "sent":
        message = "Wysłano wiadomość testową."
        message_type = "success"
    elif status == "failed":
        message = "Nie udało się wysłać wiadomości testowej."
        message_type = "error"
    elif status == "missing":
        message = "Uzupełnij adres e-mail do wysyłki testu."
        message_type = "error"

    if request.method == "POST":
        form_data = {
            "mail_server": clean_str(request.form.get("mail_server")),
            "mail_port": clean_str(request.form.get("mail_port")),
            "mail_use_tls": bool(request.form.get("mail_use_tls")),
            "mail_username": clean_str(request.form.get("mail_username")),
            "mail_password": clean_str(request.form.get("mail_password")),
            "notification_email": clean_str(request.form.get("notification_email")),
            "send_hour": clean_str(request.form.get("send_hour")),
        }

        if not form_data["notification_email"]:
            errors["notification_email"] = "Adres e-mail jest wymagany."
        elif not validate_email(form_data["notification_email"]):
            errors["notification_email"] = "Podaj poprawny adres e-mail."

        send_hour = None
        if form_data["send_hour"]:
            try:
                send_hour = to_int(form_data["send_hour"])
            except ValueError:
                errors["send_hour"] = "Podaj poprawną godzinę."
        else:
            errors["send_hour"] = "Godzina wysyłki jest wymagana."

        if send_hour is not None and not 0 <= send_hour <= 23:
            errors["send_hour"] = "Godzina wysyłki musi być między 0 a 23."

        mail_port = None
        if form_data["mail_port"]:
            try:
                mail_port = to_int(form_data["mail_port"])
            except ValueError:
                errors["mail_port"] = "Podaj poprawny port."

        if not errors:
            if not user_config:
                user_config = UserConfig(email=form_data["notification_email"])
                db.session.add(user_config)

            user_config.email = form_data["notification_email"]
            user_config.mail_server = form_data["mail_server"] or None
            user_config.mail_port = mail_port
            user_config.mail_use_tls = bool(form_data["mail_use_tls"])
            user_config.mail_username = form_data["mail_username"] or None
            if form_data["mail_password"]:
                user_config.mail_password = form_data["mail_password"]
            if send_hour is not None:
                user_config.send_hour = send_hour

            db.session.commit()
            _reschedule_daily_job(user_config.send_hour)
            message = "Zapisano ustawienia."
            message_type = "success"
            form_data = _build_form_data(user_config)

    return render_template(
        "settings.html",
        form_data=form_data,
        errors=errors,
        message=message,
        message_type=message_type,
    )


@settings_bp.post("/test-email")
def send_test_email() -> str:
    user_config = _get_user_config()
    if not user_config or not user_config.email:
        return redirect(url_for("settings.settings_view", status="missing"))

    subject = "Test konfiguracji SMTP"
    body = "To jest testowa wiadomość z CRM."
    sent = send_email(subject, body, user_config.email)

    status = "sent" if sent else "failed"
    return redirect(url_for("settings.settings_view", status=status))
