from __future__ import annotations

from flask import Flask

from backend.config import Config
from backend.models import db
from backend.routes import clients_bp, events_bp, policies_bp, reminders_bp


def register_blueprints(app: Flask) -> None:
    """Register application blueprints."""
    app.register_blueprint(clients_bp)
    app.register_blueprint(policies_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(reminders_bp)



def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    register_blueprints(app)

    return app


if __name__ == "__main__":
    from waitress import serve

    application = create_app()
    serve(application, host="0.0.0.0", port=application.config["PORT"])
