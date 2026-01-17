from __future__ import annotations

from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for

from backend.auth import auth_required
from backend.models import Client, Policy, Reminder, db
from backend.routes.utils import clean_str, parse_datetime, to_int

reminders_bp = Blueprint("reminders", __name__, url_prefix="/reminders")


@reminders_bp.get("/")
@auth_required
def list_reminders() -> str:
    reminders = Reminder.query.order_by(Reminder.data_przypomnienia.desc()).all()
    return render_template("reminders/list.html", reminders=reminders)


@reminders_bp.get("/<int:reminder_id>")
@auth_required
def reminder_detail(reminder_id: int) -> str:
    reminder = Reminder.query.get_or_404(reminder_id)
    return render_template("reminders/detail.html", reminder=reminder)


@reminders_bp.route("/new", methods=["GET", "POST"])
@auth_required
def create_reminder() -> str:
    errors: dict[str, str] = {}
    clients = Client.query.order_by(Client.nazwisko.asc(), Client.imie.asc()).all()
    policies = Policy.query.order_by(Policy.numer_polisy.asc()).all()

    form_data = {
        "tresc": "",
        "data_przypomnienia": "",
        "wyslano": False,
        "client_id": "",
        "policy_id": "",
    }

    if request.method == "POST":
        form_data = {
            "tresc": clean_str(request.form.get("tresc")),
            "data_przypomnienia": clean_str(request.form.get("data_przypomnienia")),
            "wyslano": bool(request.form.get("wyslano")),
            "client_id": clean_str(request.form.get("client_id")),
            "policy_id": clean_str(request.form.get("policy_id")),
        }

        if not form_data["tresc"]:
            errors["tresc"] = "Treść przypomnienia jest wymagana."
        if not form_data["data_przypomnienia"]:
            errors["data_przypomnienia"] = "Data przypomnienia jest wymagana."

        data_przypomnienia: datetime | None = None
        client_id = None
        policy_id = None

        if form_data["data_przypomnienia"]:
            try:
                data_przypomnienia = parse_datetime(form_data["data_przypomnienia"])
            except ValueError:
                errors["data_przypomnienia"] = "Podaj poprawną datę i godzinę."

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
            reminder = Reminder(
                tresc=form_data["tresc"],
                data_przypomnienia=data_przypomnienia,
                wyslano=form_data["wyslano"],
                client_id=client_id,
                policy_id=policy_id,
            )
            db.session.add(reminder)
            db.session.commit()
            return redirect(url_for("reminders.reminder_detail", reminder_id=reminder.id))

    return render_template(
        "reminders/form.html",
        form_data=form_data,
        errors=errors,
        clients=clients,
        policies=policies,
        mode="create",
    )


@reminders_bp.route("/<int:reminder_id>/edit", methods=["GET", "POST"])
@auth_required
def edit_reminder(reminder_id: int) -> str:
    reminder = Reminder.query.get_or_404(reminder_id)
    errors: dict[str, str] = {}
    clients = Client.query.order_by(Client.nazwisko.asc(), Client.imie.asc()).all()
    policies = Policy.query.order_by(Policy.numer_polisy.asc()).all()

    form_data = {
        "tresc": reminder.tresc,
        "data_przypomnienia": reminder.data_przypomnienia.strftime("%Y-%m-%dT%H:%M"),
        "wyslano": reminder.wyslano,
        "client_id": str(reminder.client_id) if reminder.client_id else "",
        "policy_id": str(reminder.policy_id) if reminder.policy_id else "",
    }

    if request.method == "POST":
        form_data = {
            "tresc": clean_str(request.form.get("tresc")),
            "data_przypomnienia": clean_str(request.form.get("data_przypomnienia")),
            "wyslano": bool(request.form.get("wyslano")),
            "client_id": clean_str(request.form.get("client_id")),
            "policy_id": clean_str(request.form.get("policy_id")),
        }

        if not form_data["tresc"]:
            errors["tresc"] = "Treść przypomnienia jest wymagana."
        if not form_data["data_przypomnienia"]:
            errors["data_przypomnienia"] = "Data przypomnienia jest wymagana."

        data_przypomnienia: datetime | None = None
        client_id = None
        policy_id = None

        if form_data["data_przypomnienia"]:
            try:
                data_przypomnienia = parse_datetime(form_data["data_przypomnienia"])
            except ValueError:
                errors["data_przypomnienia"] = "Podaj poprawną datę i godzinę."

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
            reminder.tresc = form_data["tresc"]
            reminder.data_przypomnienia = data_przypomnienia
            reminder.wyslano = form_data["wyslano"]
            reminder.client_id = client_id
            reminder.policy_id = policy_id
            db.session.commit()
            return redirect(url_for("reminders.reminder_detail", reminder_id=reminder.id))

    return render_template(
        "reminders/form.html",
        form_data=form_data,
        errors=errors,
        clients=clients,
        policies=policies,
        mode="edit",
        reminder=reminder,
    )


@reminders_bp.post("/<int:reminder_id>/delete")
@auth_required
def delete_reminder(reminder_id: int) -> str:
    reminder = Reminder.query.get_or_404(reminder_id)
    db.session.delete(reminder)
    db.session.commit()
    return redirect(url_for("reminders.list_reminders"))
