from __future__ import annotations

from flask import Flask

from backend.config import Config


def register_blueprints(app: Flask) -> None:
    """Register application blueprints."""



def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(Config)

    register_blueprints(app)

    return app


if __name__ == "__main__":
    from waitress import serve

    application = create_app()
    serve(application, host="0.0.0.0", port=application.config["PORT"])
