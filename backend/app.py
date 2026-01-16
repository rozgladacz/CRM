from __future__ import annotations

from flask import Flask

from backend.auth import init_auth
from backend.config import Config
from backend.models import db
from backend.routes import (
    clients_bp,
    dashboard_bp,
    events_bp,
    export_bp,
    policies_bp,
    reminders_bp,
    settings_bp,
)
from backend.scheduler import init_scheduler


def register_blueprints(app: Flask) -> None:
    """Register application blueprints."""
    app.register_blueprint(clients_bp)
    app.register_blueprint(policies_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(export_bp)



def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    init_auth(app)
    register_blueprints(app)
    app.scheduler = init_scheduler(app)

    return app


if __name__ == "__main__":
    from waitress import serve

    application = create_app()
    serve(application, host="0.0.0.0", port=application.config["PORT"])
