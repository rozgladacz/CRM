from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from typing import Any, Mapping

from flask import current_app, has_app_context

from backend.config import Config
from backend.models import UserConfig


logger = logging.getLogger(__name__)


def _get_config_value(
    user_config: UserConfig | None,
    app_config: Mapping[str, Any] | Config,
    app_key: str,
    user_key: str | None = None,
    default: Any | None = None,
) -> Any:
    if user_config is not None and user_key:
        value = getattr(user_config, user_key, None)
        if value not in (None, ""):
            return value

    if isinstance(app_config, Mapping):
        value = app_config.get(app_key)
    else:
        value = getattr(app_config, app_key, None)

    if value not in (None, ""):
        return value

    return default


def _load_smtp_settings() -> dict[str, Any]:
    app_config: Mapping[str, Any] | Config
    if has_app_context():
        app_config = current_app.config
        try:
            user_config = UserConfig.query.first()
        except Exception:
            logger.exception("Failed to load UserConfig for SMTP settings")
            user_config = None
    else:
        app_config = Config
        user_config = None

    mail_server = _get_config_value(user_config, app_config, "MAIL_SERVER", "mail_server")
    mail_port = int(
        _get_config_value(user_config, app_config, "MAIL_PORT", "mail_port", Config.MAIL_PORT)
    )
    mail_use_tls = bool(
        _get_config_value(
            user_config, app_config, "MAIL_USE_TLS", "mail_use_tls", Config.MAIL_USE_TLS
        )
    )
    mail_username = _get_config_value(
        user_config, app_config, "MAIL_USERNAME", "mail_username", Config.MAIL_USERNAME
    )
    mail_password = _get_config_value(
        user_config, app_config, "MAIL_PASSWORD", "mail_password", Config.MAIL_PASSWORD
    )
    default_sender = _get_config_value(
        user_config,
        app_config,
        "MAIL_DEFAULT_SENDER",
        "email",
        Config.MAIL_DEFAULT_SENDER,
    )

    return {
        "server": mail_server,
        "port": mail_port,
        "use_tls": mail_use_tls,
        "username": mail_username,
        "password": mail_password,
        "default_sender": default_sender,
    }


def send_email(subject: str, body: str, to_addr: str) -> bool:
    settings = _load_smtp_settings()
    server = settings["server"]
    port = settings["port"]
    use_tls = settings["use_tls"]
    username = settings["username"]
    password = settings["password"]
    default_sender = settings["default_sender"]

    if not server:
        logger.error("SMTP server is not configured; cannot send email to %s", to_addr)
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = default_sender
    message["To"] = to_addr
    message.set_content(body)

    try:
        with smtplib.SMTP(server, port, timeout=10) as smtp:
            smtp.ehlo()
            if use_tls or port == 587:
                smtp.starttls()
                smtp.ehlo()
            if username and password:
                smtp.login(username, password)
            smtp.send_message(message)
        return True
    except (smtplib.SMTPException, OSError):
        logger.exception("Failed to send email to %s via %s:%s", to_addr, server, port)
        return False
