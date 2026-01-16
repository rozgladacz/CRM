from __future__ import annotations

import csv
from io import StringIO

from flask import Blueprint, Response

from backend.models import Client, Policy

export_bp = Blueprint("export", __name__, url_prefix="/export")


def _csv_response(filename: str, rows: list[list[str]]) -> Response:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerows(rows)
    csv_data = buffer.getvalue()
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return Response(csv_data, mimetype="text/csv", headers=headers)


def _format_value(value: object | None) -> str:
    if value is None:
        return ""
    return str(value)


@export_bp.get("/clients.csv")
def export_clients() -> Response:
    clients = Client.query.order_by(Client.nazwisko.asc(), Client.imie.asc()).all()
    rows = [
        [
            "id",
            "imie",
            "nazwisko",
            "email",
            "telefon",
            "adres",
            "data_utworzenia",
        ]
    ]
    for client in clients:
        rows.append(
            [
                _format_value(client.id),
                _format_value(client.imie),
                _format_value(client.nazwisko),
                _format_value(client.email),
                _format_value(client.telefon),
                _format_value(client.adres),
                _format_value(client.data_utworzenia),
            ]
        )
    return _csv_response("clients.csv", rows)


@export_bp.get("/policies.csv")
def export_policies() -> Response:
    policies = (
        Policy.query.join(Client)
        .order_by(Policy.data_poczatku.desc(), Policy.numer_polisy.asc())
        .all()
    )
    rows = [
        [
            "id",
            "numer_polisy",
            "produkt",
            "data_poczatku",
            "data_konca",
            "skladka",
            "status",
            "client_id",
            "client_imie",
            "client_nazwisko",
        ]
    ]
    for policy in policies:
        rows.append(
            [
                _format_value(policy.id),
                _format_value(policy.numer_polisy),
                _format_value(policy.produkt),
                _format_value(policy.data_poczatku),
                _format_value(policy.data_konca),
                _format_value(policy.skladka),
                _format_value(policy.status),
                _format_value(policy.client_id),
                _format_value(policy.client.imie if policy.client else None),
                _format_value(policy.client.nazwisko if policy.client else None),
            ]
        )
    return _csv_response("policies.csv", rows)
