# 🧰 TBC Lagerverwaltung (Flask App)

Dies ist eine webbasierte Lagerverwaltungsanwendung, entwickelt mit **Python**, **Flask**, **MariaDB** und einer **RESTful API**.  
Sie erlaubt das Verwalten von Artikeln, Benutzeraccounts und bietet sowohl ein Webinterface als auch gesicherte API-Zugriffe.

---

## 🔧 Technologien

| Komponente     | Beschreibung                         |
|----------------|--------------------------------------|
| Backend        | Python 3.11, Flask, SQLAlchemy       |
| Datenbank      | MariaDB (extern gehostet via Plesk)  |
| API-Schutz     | Token-basierte Authentifizierung     |
| Authentifizierung | Flask-Login, bcrypt                |
| UI             | Bootstrap 5                          |
| Server         | Entwickelt für Gunicorn / PythonAnywhere |
| API-Tests      | Postman / curl-ready                 |

---

## ✅ Features

- Registrierung & Login mit sicheren Passwörtern
- Benutzerprofil mit Passwortänderung & Accountlöschung
- Artikelverwaltung: Hinzufügen, Bearbeiten, Löschen
- Gültigkeitsprüfung: Keine doppelten Artikelnamen
- Globale Bearbeitung durch alle Nutzer erlaubt
- Admin-Bereich (für spätere Erweiterung)
- Vollständige API-Schnittstelle mit Token-Zugriff
- Lokale Entwicklung und extern gehostete Datenbank

---

- Die Applikation ist online zugänglich unter:

  ➤ **Frontend (Browser):** https://<dein-benutzername>.pythonanywhere.com  
  ➤ **API (GET):** `https://<dein-benutzername>.pythonanywhere.com/api/artikel`

- Die API erfordert Token-basierte Authentifizierung (`Authorization` Header)
- Die Datenbank ist weiterhin extern gehostet (nicht auf PythonAnywhere)

---

## 🚀 Lokale Entwicklung starten

```bash
# 1. Virtual Environment aktivieren (Windows PowerShell)
.\venv\bin\Activate.ps1

# 2. Flask-App definieren
$env:FLASK_APP = "app.py"

# 3. App starten
python app.py