from __future__ import annotations

from backend.routes.clients import clients_bp
from backend.routes.events import events_bp
from backend.routes.policies import policies_bp
from backend.routes.reminders import reminders_bp

__all__ = ["clients_bp", "events_bp", "policies_bp", "reminders_bp"]
