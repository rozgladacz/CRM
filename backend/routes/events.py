from __future__ import annotations

from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for

from backend.auth import auth_required
from backend.models import Client, Event, Policy, db
from backend.routes.utils import clean_str, parse_datetime, to_int

events_bp = Blueprint("events", __name__, url_prefix="/events")


@events_bp.get("/")
@auth_required
def list_events() -> str:
    events = Event.query.order_by(Event.data_wydarzenia.desc()).all()
    return render_template("events/list.html", events=events)


@events_bp.get("/<int:event_id>")
@auth_required
def event_detail(event_id: int) -> str:
    event = Event.query.get_or_404(event_id)
    return render_template("events/detail.html", event=event)


@events_bp.route("/new", methods=["GET", "POST"])
@auth_required
def create_event() -> str:
    errors: dict[str, str] = {}
    clients = Client.query.order_by(Client.nazwisko.asc(), Client.imie.asc()).all()
    policies = Policy.query.order_by(Policy.numer_polisy.asc()).all()

    form_data = {
        "tytul": "",
        "opis": "",
        "data_wydarzenia": "",
        "client_id": "",
        "policy_id": "",
    }

    if request.method == "POST":
        form_data = {
            "tytul": clean_str(request.form.get("tytul")),
            "opis": clean_str(request.form.get("opis")),
            "data_wydarzenia": clean_str(request.form.get("data_wydarzenia")),
            "client_id": clean_str(request.form.get("client_id")),
            "policy_id": clean_str(request.form.get("policy_id")),
        }

        if not form_data["tytul"]:
            errors["tytul"] = "Tytuł jest wymagany."
        if not form_data["data_wydarzenia"]:
            errors["data_wydarzenia"] = "Data wydarzenia jest wymagana."
        if not form_data["client_id"]:
            errors["client_id"] = "Wybierz klienta."

        data_wydarzenia: datetime | None = None
        client_id = None
        policy_id = None

        if form_data["data_wydarzenia"]:
            try:
                data_wydarzenia = parse_datetime(form_data["data_wydarzenia"])
            except ValueError:
                errors["data_wydarzenia"] = "Podaj poprawną datę i godzinę."

        if form_data["client_id"]:
            try:
                client_id = to_int(form_data["client_id"])
            except ValueError:
                errors["client_id"] = "Wybierz poprawnego klienta."

        if form_data["policy_id"]:
            try:
                policy_id = to_int(form_data["policy_id"])
            except ValueError:
                errors["policy_id"] = "Wybierz poprawną polisę."

        client = Client.query.get(client_id) if client_id else None
        policy = Policy.query.get(policy_id) if policy_id else None

        if client_id and not client:
            errors["client_id"] = "Wybrany klient nie istnieje."
        if policy_id and not policy:
            errors["policy_id"] = "Wybrana polisa nie istnieje."
        if client and policy and policy.client_id != client.id:
            errors["policy_id"] = "Polisa nie należy do wybranego klienta."

        if not errors:
            event = Event(
                tytul=form_data["tytul"],
                opis=form_data["opis"] or None,
                data_wydarzenia=data_wydarzenia,
                client_id=client_id,
                policy_id=policy_id,
            )
            db.session.add(event)
            db.session.commit()
            return redirect(url_for("events.event_detail", event_id=event.id))

    return render_template(
        "events/form.html",
        form_data=form_data,
        errors=errors,
        clients=clients,
        policies=policies,
        mode="create",
    )


@events_bp.route("/<int:event_id>/edit", methods=["GET", "POST"])
@auth_required
def edit_event(event_id: int) -> str:
    event = Event.query.get_or_404(event_id)
    errors: dict[str, str] = {}
    clients = Client.query.order_by(Client.nazwisko.asc(), Client.imie.asc()).all()
    policies = Policy.query.order_by(Policy.numer_polisy.asc()).all()

    form_data = {
        "tytul": event.tytul,
        "opis": event.opis or "",
        "data_wydarzenia": event.data_wydarzenia.strftime("%Y-%m-%dT%H:%M"),
        "client_id": str(event.client_id),
        "policy_id": str(event.policy_id) if event.policy_id else "",
    }

    if request.method == "POST":
        form_data = {
            "tytul": clean_str(request.form.get("tytul")),
            "opis": clean_str(request.form.get("opis")),
            "data_wydarzenia": clean_str(request.form.get("data_wydarzenia")),
            "client_id": clean_str(request.form.get("client_id")),
            "policy_id": clean_str(request.form.get("policy_id")),
        }

        if not form_data["tytul"]:
            errors["tytul"] = "Tytuł jest wymagany."
        if not form_data["data_wydarzenia"]:
            errors["data_wydarzenia"] = "Data wydarzenia jest wymagana."
        if not form_data["client_id"]:
            errors["client_id"] = "Wybierz klienta."

        data_wydarzenia: datetime | None = None
        client_id = None
        policy_id = None

        if form_data["data_wydarzenia"]:
            try:
                data_wydarzenia = parse_datetime(form_data["data_wydarzenia"])
            except ValueError:
                errors["data_wydarzenia"] = "Podaj poprawną datę i godzinę."

        if form_data["client_id"]:
            try:
                client_id = to_int(form_data["client_id"])
            except ValueError:
                errors["client_id"] = "Wybierz poprawnego klienta."

        if form_data["policy_id"]:
            try:
                policy_id = to_int(form_data["policy_id"])
            except ValueError:
                errors["policy_id"] = "Wybierz poprawną polisę."

        client = Client.query.get(client_id) if client_id else None
        policy = Policy.query.get(policy_id) if policy_id else None

        if client_id and not client:
            errors["client_id"] = "Wybrany klient nie istnieje."
        if policy_id and not policy:
            errors["policy_id"] = "Wybrana polisa nie istnieje."
        if client and policy and policy.client_id != client.id:
            errors["policy_id"] = "Polisa nie należy do wybranego klienta."

        if not errors:
            event.tytul = form_data["tytul"]
            event.opis = form_data["opis"] or None
            event.data_wydarzenia = data_wydarzenia
            event.client_id = client_id
            event.policy_id = policy_id
            db.session.commit()
            return redirect(url_for("events.event_detail", event_id=event.id))

    return render_template(
        "events/form.html",
        form_data=form_data,
        errors=errors,
        clients=clients,
        policies=policies,
        mode="edit",
        event=event,
    )


@events_bp.post("/<int:event_id>/delete")
@auth_required
def delete_event(event_id: int) -> str:
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for("events.list_events"))
