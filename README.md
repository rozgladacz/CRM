# CRM

## Opis
Prosty szkielet aplikacji CRM przygotowany do dalszego rozwoju (backend, frontend, dokumentacja i skrypty).

## Wymagania
- Python 3.10+

## Uruchomienie lokalne
1. Utwórz i aktywuj wirtualne środowisko:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Zainstaluj zależności:
   ```bash
   pip install -r requirements.txt
   ```
3. Uruchom aplikację zgodnie z przyszłą dokumentacją w katalogu `docs/`.
   Przykładowe uruchomienie:
   ```bash
   waitress-serve --host 0.0.0.0 --port 5000 app:app
   ```

## Backup bazy danych
Domyślnie aplikacja przechowuje dane w pliku SQLite `crm.sqlite3` w katalogu głównym repozytorium (możesz to zmienić przez zmienną `DATABASE_URL`).

Aby wykonać kopię zapasową, zatrzymaj aplikację i skopiuj plik bazy w bezpieczne miejsce:

```bash
cp crm.sqlite3 backups/crm.sqlite3.$(date +%Y%m%d_%H%M%S)
```

Przywracanie polega na podmianie pliku na kopię zapasową (upewnij się, że aplikacja jest wtedy wyłączona).
