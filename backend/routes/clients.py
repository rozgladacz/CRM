from __future__ import annotations

from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy import or_

from backend.models import Client, db
from backend.routes.utils import clean_str, validate_email

clients_bp = Blueprint("clients", __name__, url_prefix="/clients")


@clients_bp.get("/")
def list_clients() -> str:
    search_query = clean_str(request.args.get("q"))
    query = Client.query
    if search_query:
        like_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                Client.imie.ilike(like_pattern),
                Client.nazwisko.ilike(like_pattern),
                Client.email.ilike(like_pattern),
                Client.telefon.ilike(like_pattern),
                Client.adres.ilike(like_pattern),
            )
        )
    clients = query.order_by(Client.nazwisko.asc(), Client.imie.asc()).all()
    return render_template("clients/list.html", clients=clients, search_query=search_query)


@clients_bp.get("/<int:client_id>")
def client_detail(client_id: int) -> str:
    client = Client.query.get_or_404(client_id)
    return render_template("clients/detail.html", client=client)


@clients_bp.route("/new", methods=["GET", "POST"])
def create_client() -> str:
    errors: dict[str, str] = {}
    form_data = {
        "imie": "",
        "nazwisko": "",
        "email": "",
        "telefon": "",
        "adres": "",
    }

    if request.method == "POST":
        form_data = {
            "imie": clean_str(request.form.get("imie")),
            "nazwisko": clean_str(request.form.get("nazwisko")),
            "email": clean_str(request.form.get("email")),
            "telefon": clean_str(request.form.get("telefon")),
            "adres": clean_str(request.form.get("adres")),
        }

        if not form_data["imie"]:
            errors["imie"] = "Imię jest wymagane."
        if not form_data["nazwisko"]:
            errors["nazwisko"] = "Nazwisko jest wymagane."
        if not validate_email(form_data["email"]):
            errors["email"] = "Podaj poprawny adres e-mail."

        if not errors:
            client = Client(**form_data)
            db.session.add(client)
            db.session.commit()
            return redirect(url_for("clients.client_detail", client_id=client.id))

    return render_template("clients/form.html", form_data=form_data, errors=errors, mode="create")


@clients_bp.route("/<int:client_id>/edit", methods=["GET", "POST"])
def edit_client(client_id: int) -> str:
    client = Client.query.get_or_404(client_id)
    errors: dict[str, str] = {}

    form_data = {
        "imie": client.imie,
        "nazwisko": client.nazwisko,
        "email": client.email or "",
        "telefon": client.telefon or "",
        "adres": client.adres or "",
    }

    if request.method == "POST":
        form_data = {
            "imie": clean_str(request.form.get("imie")),
            "nazwisko": clean_str(request.form.get("nazwisko")),
            "email": clean_str(request.form.get("email")),
            "telefon": clean_str(request.form.get("telefon")),
            "adres": clean_str(request.form.get("adres")),
        }

        if not form_data["imie"]:
            errors["imie"] = "Imię jest wymagane."
        if not form_data["nazwisko"]:
            errors["nazwisko"] = "Nazwisko jest wymagane."
        if not validate_email(form_data["email"]):
            errors["email"] = "Podaj poprawny adres e-mail."

        if not errors:
            client.imie = form_data["imie"]
            client.nazwisko = form_data["nazwisko"]
            client.email = form_data["email"] or None
            client.telefon = form_data["telefon"] or None
            client.adres = form_data["adres"] or None
            db.session.commit()
            return redirect(url_for("clients.client_detail", client_id=client.id))

    return render_template("clients/form.html", form_data=form_data, errors=errors, mode="edit", client=client)


@clients_bp.post("/<int:client_id>/delete")
def delete_client(client_id: int) -> str:
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    return redirect(url_for("clients.list_clients"))
