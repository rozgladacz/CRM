# Podręcznik użytkownika

## Logowanie

Aplikacja udostępnia logowanie przez endpoint HTTP `POST /login`. Dane można przekazać jako JSON lub formularz.

Przykład żądania (JSON):

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "haslo", "remember": true}'
```

W odpowiedzi otrzymasz komunikat o sukcesie oraz `user_id`. Jeśli w bazie nie ma użytkownika z danym e-mailem, logowanie zostanie odrzucone.

> **Wskazówka:** obecnie aplikacja nie ma formularza rejestracji. Konto użytkownika należy dodać bezpośrednio w bazie danych lub przygotować je w migracji startowej.

## Dodawanie klientów

1. Wejdź na listę klientów pod adresem `/clients/`.
2. Kliknij przycisk dodawania nowego klienta (`/clients/new`).
3. Wypełnij wymagane pola:
   - **Imię**
   - **Nazwisko**
4. Opcjonalnie uzupełnij: e-mail, telefon i adres.
5. Zapisz formularz — zostaniesz przekierowany do szczegółów klienta.

> **Walidacja:** adres e-mail jest opcjonalny, ale jeśli go podasz, musi mieć poprawny format.

## Przypomnienia

1. Wejdź na listę przypomnień pod adresem `/reminders/`.
2. Kliknij dodawanie nowego przypomnienia (`/reminders/new`).
3. Wprowadź:
   - **Treść przypomnienia** (wymagana)
   - **Data i godzina przypomnienia** (wymagana)
   - **Klient** (wymagany)
   - **Polisa** (opcjonalna — musi należeć do wybranego klienta)
4. Zapisz formularz, aby przypomnienie pojawiło się na liście.

> **Status wysyłki:** pole „Wysłano” odzwierciedla, czy przypomnienie zostało już wysłane przez harmonogram.
