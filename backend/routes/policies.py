from __future__ import annotations

from datetime import date

from flask import Blueprint, redirect, render_template, request, url_for

from backend.models import Client, Policy, db
from backend.routes.utils import clean_str, parse_date, parse_decimal, to_int

policies_bp = Blueprint("policies", __name__, url_prefix="/policies")


@policies_bp.get("/")
def list_policies() -> str:
    policies = Policy.query.order_by(Policy.data_poczatku.desc()).all()
    return render_template("policies/list.html", policies=policies)


@policies_bp.get("/<int:policy_id>")
def policy_detail(policy_id: int) -> str:
    policy = Policy.query.get_or_404(policy_id)
    return render_template("policies/detail.html", policy=policy)


@policies_bp.route("/new", methods=["GET", "POST"])
def create_policy() -> str:
    errors: dict[str, str] = {}
    clients = Client.query.order_by(Client.nazwisko.asc(), Client.imie.asc()).all()
    form_data = {
        "numer_polisy": "",
        "produkt": "",
        "data_poczatku": "",
        "data_konca": "",
        "skladka": "",
        "status": "",
        "client_id": "",
    }

    if request.method == "POST":
        form_data = {
            "numer_polisy": clean_str(request.form.get("numer_polisy")),
            "produkt": clean_str(request.form.get("produkt")),
            "data_poczatku": clean_str(request.form.get("data_poczatku")),
            "data_konca": clean_str(request.form.get("data_konca")),
            "skladka": clean_str(request.form.get("skladka")),
            "status": clean_str(request.form.get("status")),
            "client_id": clean_str(request.form.get("client_id")),
        }

        if not form_data["numer_polisy"]:
            errors["numer_polisy"] = "Numer polisy jest wymagany."
        if not form_data["data_poczatku"]:
            errors["data_poczatku"] = "Data początku jest wymagana."
        if not form_data["client_id"]:
            errors["client_id"] = "Wybierz klienta."

        data_poczatku: date | None = None
        data_konca: date | None = None
        skladka = None
        client_id = None

        if form_data["data_poczatku"]:
            try:
                data_poczatku = parse_date(form_data["data_poczatku"])
            except ValueError:
                errors["data_poczatku"] = "Podaj poprawną datę początku."

        if form_data["data_konca"]:
            try:
                data_konca = parse_date(form_data["data_konca"])
            except ValueError:
                errors["data_konca"] = "Podaj poprawną datę końca."

        if data_poczatku and data_konca and data_konca < data_poczatku:
            errors["data_konca"] = "Data końca nie może być wcześniejsza niż początek."

        if form_data["skladka"]:
            try:
                skladka = parse_decimal(form_data["skladka"])
            except ValueError:
                errors["skladka"] = "Podaj poprawną składkę."

        if form_data["client_id"]:
            try:
                client_id = to_int(form_data["client_id"])
            except ValueError:
                errors["client_id"] = "Wybierz poprawnego klienta."

        if form_data["numer_polisy"]:
            existing = Policy.query.filter_by(numer_polisy=form_data["numer_polisy"]).first()
            if existing:
                errors["numer_polisy"] = "Taki numer polisy już istnieje."

        if client_id and not Client.query.get(client_id):
            errors["client_id"] = "Wybrany klient nie istnieje."

        if not errors:
            policy = Policy(
                numer_polisy=form_data["numer_polisy"],
                produkt=form_data["produkt"] or None,
                data_poczatku=data_poczatku,
                data_konca=data_konca,
                skladka=skladka,
                status=form_data["status"] or None,
                client_id=client_id,
            )
            db.session.add(policy)
            db.session.commit()
            return redirect(url_for("policies.policy_detail", policy_id=policy.id))

    return render_template(
        "policies/form.html", form_data=form_data, errors=errors, clients=clients, mode="create"
    )


@policies_bp.route("/<int:policy_id>/edit", methods=["GET", "POST"])
def edit_policy(policy_id: int) -> str:
    policy = Policy.query.get_or_404(policy_id)
    errors: dict[str, str] = {}
    clients = Client.query.order_by(Client.nazwisko.asc(), Client.imie.asc()).all()

    form_data = {
        "numer_polisy": policy.numer_polisy,
        "produkt": policy.produkt or "",
        "data_poczatku": policy.data_poczatku.isoformat() if policy.data_poczatku else "",
        "data_konca": policy.data_konca.isoformat() if policy.data_konca else "",
        "skladka": str(policy.skladka) if policy.skladka is not None else "",
        "status": policy.status or "",
        "client_id": str(policy.client_id),
    }

    if request.method == "POST":
        form_data = {
            "numer_polisy": clean_str(request.form.get("numer_polisy")),
            "produkt": clean_str(request.form.get("produkt")),
            "data_poczatku": clean_str(request.form.get("data_poczatku")),
            "data_konca": clean_str(request.form.get("data_konca")),
            "skladka": clean_str(request.form.get("skladka")),
            "status": clean_str(request.form.get("status")),
            "client_id": clean_str(request.form.get("client_id")),
        }

        if not form_data["numer_polisy"]:
            errors["numer_polisy"] = "Numer polisy jest wymagany."
        if not form_data["data_poczatku"]:
            errors["data_poczatku"] = "Data początku jest wymagana."
        if not form_data["client_id"]:
            errors["client_id"] = "Wybierz klienta."

        data_poczatku: date | None = None
        data_konca: date | None = None
        skladka = None
        client_id = None

        if form_data["data_poczatku"]:
            try:
                data_poczatku = parse_date(form_data["data_poczatku"])
            except ValueError:
                errors["data_poczatku"] = "Podaj poprawną datę początku."

        if form_data["data_konca"]:
            try:
                data_konca = parse_date(form_data["data_konca"])
            except ValueError:
                errors["data_konca"] = "Podaj poprawną datę końca."

        if data_poczatku and data_konca and data_konca < data_poczatku:
            errors["data_konca"] = "Data końca nie może być wcześniejsza niż początek."

        if form_data["skladka"]:
            try:
                skladka = parse_decimal(form_data["skladka"])
            except ValueError:
                errors["skladka"] = "Podaj poprawną składkę."

        if form_data["client_id"]:
            try:
                client_id = to_int(form_data["client_id"])
            except ValueError:
                errors["client_id"] = "Wybierz poprawnego klienta."

        if form_data["numer_polisy"]:
            existing = Policy.query.filter_by(numer_polisy=form_data["numer_polisy"]).first()
            if existing and existing.id != policy.id:
                errors["numer_polisy"] = "Taki numer polisy już istnieje."

        if client_id and not Client.query.get(client_id):
            errors["client_id"] = "Wybrany klient nie istnieje."

        if not errors:
            policy.numer_polisy = form_data["numer_polisy"]
            policy.produkt = form_data["produkt"] or None
            policy.data_poczatku = data_poczatku
            policy.data_konca = data_konca
            policy.skladka = skladka
            policy.status = form_data["status"] or None
            policy.client_id = client_id
            db.session.commit()
            return redirect(url_for("policies.policy_detail", policy_id=policy.id))

    return render_template(
        "policies/form.html",
        form_data=form_data,
        errors=errors,
        clients=clients,
        mode="edit",
        policy=policy,
    )


@policies_bp.post("/<int:policy_id>/delete")
def delete_policy(policy_id: int) -> str:
    policy = Policy.query.get_or_404(policy_id)
    db.session.delete(policy)
    db.session.commit()
    return redirect(url_for("policies.list_policies"))
