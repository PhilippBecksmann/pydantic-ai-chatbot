# Pydantic AI Chatbot

Ein einfacher lokaler KI-Chatbot mit Python, Pydantic AI, OpenAI GPT-5 mini und Gradio.

Die App laeuft lokal im Browser. Deine Nachrichten werden zur Beantwortung an den konfigurierten OpenAI-Dienst uebertragen.

## Voraussetzungen

- Windows mit PowerShell oder Eingabeaufforderung
- Python `3.14.6`
- Ein OpenAI-API-Key
- Internetverbindung fuer Modellanfragen

## Installation unter Windows

Wechsle in den Projektordner:

```powershell
cd pydantic-gradio-chatbot
```

Erstelle eine virtuelle Umgebung:

```powershell
python -m venv .venv
```

Aktiviere sie:

```powershell
.venv\Scripts\activate
```

Installiere die App und ihre Abhaengigkeiten:

```powershell
pip install -e .
```

Fuer Tests installierst du zusaetzlich die Development-Abhaengigkeiten:

```powershell
pip install -e ".[dev]"
```

## API-Key einrichten

Kopiere `.env.example` zu `.env`:

```powershell
copy .env.example .env
```

Oeffne `.env` und trage deinen API-Key ein:

```env
OPENAI_API_KEY=dein_api_key
```

Wichtig: `.env` enthaelt ein Geheimnis und darf nicht in Git eingecheckt werden. Die Datei ist deshalb in `.gitignore` eingetragen.

## App starten

Starte die Anwendung:

```powershell
python app.py
```

Gradio zeigt danach eine lokale URL an, normalerweise:

```text
http://127.0.0.1:7860
```

Oeffne diese Adresse im Browser.

## App verwenden

Du kannst im Textfeld eine Nachricht eingeben und mit **Absenden** senden. Die Antwort wird gestreamt, also schrittweise im Chatfenster angezeigt.

Du kannst Folgefragen stellen. Die App merkt sich den bisherigen Verlauf der aktuellen Browser-Sitzung und uebergibt ihn an Pydantic AI ueber `message_history`.

Mit **Stoppen** kannst du eine laufende Antwort abbrechen. Mit **Chat zuruecksetzen** loeschst du den sichtbaren Chat und die Pydantic-AI-Historie der aktuellen Sitzung.

Beispielanfragen:

- `Erklaere mir Pydantic AI einfach.`
- `Erstelle eine Python-Funktion fuer eine Einkaufsliste.`
- `Was ist der Unterschied zwischen einem Chatbot und einem KI-Agenten?`

## Tests ausfuehren

Die Tests verwenden gemockte Agenten und fuehren keine echten OpenAI-Aufrufe aus.

```powershell
python -m pytest
```

## Projektstruktur

```text
pydantic-gradio-chatbot/
├── app.py
├── src/
│   ├── __init__.py
│   ├── agent.py
│   ├── chat_service.py
│   ├── config.py
│   └── ui.py
├── tests/
│   ├── test_config.py
│   └── test_chat_service.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## API-Kosten

Jede echte Chatnachricht kann OpenAI-API-Kosten verursachen. Die genaue Hoehe haengt vom Modell, der Laenge deiner Eingaben, der Laenge der Antworten und dem Kontextverlauf ab.

Das verwendete Modell ist:

```text
openai:gpt-5-mini
```

## Datenschutz und Sicherheit

- Der API-Key wird aus `.env` geladen und nicht protokolliert.
- Chatverlaeufe werden in Version 1 nicht dauerhaft gespeichert.
- Vollstaendige Chatverlaeufe und sensible Eingaben werden nicht geloggt.
- Vom Modell erzeugter Code wird nicht automatisch ausgefuehrt.
- Die App verwendet kein `eval` und kein `exec`.
- Benutzereingaben werden nicht als Systemanweisung behandelt.

## Bekannte Einschraenkungen

- Die Historie ist einfach auf die letzten 20 Pydantic-AI-Nachrichten begrenzt.
- Eine Produktionsversion sollte tokenbasierte Begrenzung oder Kompaktierung verwenden.
- Es gibt keine Benutzerverwaltung.
- Chatverlaeufe werden nach einem Reset oder Neustart nicht wiederhergestellt.
- Ohne gueltigen OpenAI-API-Key kann die App keine Modellantworten erzeugen.

## Moegliche spaetere Erweiterungen

- Tokenbasierte Historienkompaktierung
- Persistente Chat-Sitzungen
- Auswahl mehrerer Modelle in der UI
- Export von Chatverlaeufen
- Authentifizierung fuer mehrere Benutzer
- Erweiterte Observability mit Pydantic Logfire
