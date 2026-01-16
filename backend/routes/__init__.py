from __future__ import annotations

from backend.routes.clients import clients_bp
from backend.routes.events import events_bp
from backend.routes.policies import policies_bp
from backend.routes.reminders import reminders_bp
from backend.routes.dashboard import dashboard_bp
from backend.routes.settings import settings_bp
from backend.routes.export import export_bp

__all__ = [
    "clients_bp",
    "events_bp",
    "policies_bp",
    "reminders_bp",
    "dashboard_bp",
    "settings_bp",
    "export_bp",
]
