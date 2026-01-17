# Przewodnik dewelopera

## Struktura kodu

- `backend/` — główna aplikacja Flask.
  - `app.py` — fabryka aplikacji, rejestracja blueprintów i uruchomienie harmonogramu.
  - `auth.py` — logowanie i wylogowanie przez Flask-Login.
  - `config.py` — konfiguracja (baza danych, SMTP, bezpieczeństwo).
  - `models.py` — modele SQLAlchemy.
  - `scheduler.py` — harmonogram wysyłki przypomnień (APScheduler).
  - `emailer.py` — logika wysyłki e-maili przez SMTP.
  - `routes/` — blueprinty widoków (klienci, polisy, przypomnienia, ustawienia itd.).
  - `templates/` i `static/` — szablony HTML oraz zasoby statyczne.
- `frontend/` — alternatywny katalog szablonów i zasobów (obecnie duplikujący strukturę backendu).
- `docs/` — dokumentacja użytkownika i deweloperska.

## Modele danych

W `backend/models.py` zdefiniowane są modele SQLAlchemy:

- `Client` — klient (imie, nazwisko, email, telefon, adres).
- `Policy` — polisa (numer, produkt, daty, składka, status) powiązana z klientem.
- `Event` — wydarzenie dla klienta i opcjonalnie polisy.
- `Reminder` — przypomnienie z datą wysyłki, statusem wysłania i powiązaniami.
- `UserConfig` — ustawienia użytkownika (SMTP, godzina wysyłki, e-mail do powiadomień).
- `User` — konto do logowania (email, hasło zahashowane, aktywność).

Relacje są zdefiniowane przez `db.relationship`, a w większości przypadków używany jest `cascade="all, delete-orphan"`.

## Scheduler (APScheduler)

Harmonogram uruchamia się w `backend/app.py` przez `init_scheduler(app)`.
W `backend/scheduler.py` ustawiany jest job `daily_reminder_sender`, który:

1. Ładuje godzinę wysyłki z `UserConfig.send_hour` (domyślnie 8:00).
2. Wysyła przypomnienia, których `data_przypomnienia` jest w przeszłości i nie zostały jeszcze wysłane.
3. Aktualizuje pole `wyslano` po udanym wysłaniu.

Zmiana godziny w ustawieniach (`/settings/`) powoduje reschedule joba bez restartu aplikacji.

## SMTP i wysyłka e-maili

Wysyłka e-maili realizowana jest w `backend/emailer.py`:

- Konfiguracja jest pobierana z `Config` (zmienne środowiskowe) i może być nadpisana przez `UserConfig`.
- Wspierane pola to m.in. `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`.
- Dodatkowo w `/settings/` można ustawić adres docelowy dla testowych wiadomości i godzinę wysyłki.

W przypadku braku `MAIL_SERVER` wysyłka jest blokowana i logowany jest błąd.
