from __future__ import annotations

from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(120), nullable=False)
    nazwisko = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    telefon = db.Column(db.String(50), nullable=True)
    adres = db.Column(db.String(255), nullable=True)
    data_utworzenia = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    policies = db.relationship("Policy", back_populates="client", cascade="all, delete-orphan")
    events = db.relationship("Event", back_populates="client", cascade="all, delete-orphan")
    reminders = db.relationship(
        "Reminder", back_populates="client", cascade="all, delete-orphan"
    )


class Policy(db.Model):
    __tablename__ = "policies"

    id = db.Column(db.Integer, primary_key=True)
    numer_polisy = db.Column(db.String(120), nullable=False, unique=True)
    produkt = db.Column(db.String(120), nullable=True)
    data_poczatku = db.Column(db.Date, nullable=False)
    data_konca = db.Column(db.Date, nullable=True)
    skladka = db.Column(db.Numeric(12, 2), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)

    client = db.relationship("Client", back_populates="policies")
    events = db.relationship("Event", back_populates="policy", cascade="all, delete-orphan")
    reminders = db.relationship(
        "Reminder", back_populates="policy", cascade="all, delete-orphan"
    )


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    tytul = db.Column(db.String(200), nullable=False)
    opis = db.Column(db.Text, nullable=True)
    data_wydarzenia = db.Column(db.DateTime, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    policy_id = db.Column(db.Integer, db.ForeignKey("policies.id"), nullable=True)

    client = db.relationship("Client", back_populates="events")
    policy = db.relationship("Policy", back_populates="events")


class Reminder(db.Model):
    __tablename__ = "reminders"

    id = db.Column(db.Integer, primary_key=True)
    tresc = db.Column(db.Text, nullable=False)
    data_przypomnienia = db.Column(db.DateTime, nullable=False)
    wyslano = db.Column(db.Boolean, default=False, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    policy_id = db.Column(db.Integer, db.ForeignKey("policies.id"), nullable=True)

    client = db.relationship("Client", back_populates="reminders")
    policy = db.relationship("Policy", back_populates="reminders")


class UserConfig(db.Model):
    __tablename__ = "user_configs"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    strefa_czasowa = db.Column(db.String(120), nullable=True)
    dni_przed_wygasnieciem = db.Column(db.Integer, default=30, nullable=False)
    aktywne_powiadomienia = db.Column(db.Boolean, default=True, nullable=False)
    data_utworzenia = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    aktywny = db.Column(db.Boolean, default=True, nullable=False)
    data_utworzenia = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
