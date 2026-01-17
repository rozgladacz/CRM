from __future__ import annotations

from functools import wraps
from typing import Callable, TypeVar

from flask import Blueprint, Response, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, login_required, login_user, logout_user

from backend.models import User

auth_bp = Blueprint("auth", __name__)
login_manager = LoginManager()
login_manager.login_view = "/login"

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
def login() -> Response | tuple:
    wants_html = not request.is_json and request.accept_mimetypes.accept_html
    payload = request.get_json(silent=True) or request.form
    email = payload.get("email") if payload else None
    password = payload.get("password") if payload else None
    remember = bool(payload.get("remember")) if payload else False
    next_url = request.form.get("next") if request.form else None
    next_url = next_url or request.args.get("next") or url_for("dashboard.dashboard")

    if not email or not password:
        if wants_html:
            return (
                render_template(
                    "login.html",
                    error="Email i hasło są wymagane.",
                    email=email or "",
                    next_url=next_url,
                ),
                400,
            )
        return jsonify({"error": "Email i hasło są wymagane."}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        if wants_html:
            return (
                render_template(
                    "login.html",
                    error="Nieprawidłowe dane logowania.",
                    email=email or "",
                    next_url=next_url,
                ),
                401,
            )
        return jsonify({"error": "Nieprawidłowe dane logowania."}), 401

    login_user(user, remember=remember)
    if wants_html:
        return redirect(next_url)
    return jsonify({"message": "Zalogowano pomyślnie.", "user_id": user.id}), 200


@auth_bp.get("/login")
def login_form() -> str:
    next_url = request.args.get("next") or url_for("dashboard.dashboard")
    return render_template("login.html", next_url=next_url)


@auth_bp.post("/logout")
@login_required
def logout() -> Response | tuple:
    logout_user()
    if not request.is_json and request.accept_mimetypes.accept_html:
        return redirect(url_for("auth.login_form"))
    return jsonify({"message": "Wylogowano pomyślnie."}), 200
