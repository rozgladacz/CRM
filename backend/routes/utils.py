from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import re
from typing import Any

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%dT%H:%M")


def parse_decimal(value: str | None) -> Decimal | None:
    if not value:
        return None
    try:
        return Decimal(value.replace(",", "."))
    except InvalidOperation as exc:
        raise ValueError("Nieprawidłowa wartość liczbowa.") from exc


def clean_str(value: str | None) -> str:
    return (value or "").strip()


def validate_email(value: str | None) -> bool:
    if not value:
        return True
    return bool(EMAIL_REGEX.match(value))


def to_int(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError("Nieprawidłowa wartość numeryczna.") from exc


def checkbox_value(value: Any) -> bool:
    return bool(value)
