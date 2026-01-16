from __future__ import annotations

from functools import wraps
from typing import Callable, TypeVar

from flask import Blueprint, jsonify, request
from flask_login import LoginManager, login_required, login_user, logout_user

from backend.models import User

auth_bp = Blueprint("auth", __name__)
login_manager = LoginManager()

F = TypeVar("F", bound=Callable[..., object])


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return User.query.get(int(user_id))


def init_auth(app) -> None:
    login_manager.init_app(app)
    app.register_blueprint(auth_bp)


def auth_required(view: F) -> F:
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        return view(*args, **kwargs)

    return wrapped


@auth_bp.post("/login")
def login() -> tuple:
    payload = request.get_json(silent=True) or request.form
    email = payload.get("email") if payload else None
    password = payload.get("password") if payload else None
    remember = bool(payload.get("remember")) if payload else False

    if not email or not password:
        return jsonify({"error": "Email i hasło są wymagane."}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Nieprawidłowe dane logowania."}), 401

    login_user(user, remember=remember)
    return jsonify({"message": "Zalogowano pomyślnie.", "user_id": user.id}), 200


@auth_bp.post("/logout")
@login_required
def logout() -> tuple:
    logout_user()
    return jsonify({"message": "Wylogowano pomyślnie."}), 200
