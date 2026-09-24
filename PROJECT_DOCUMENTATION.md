# 🧠 MEMORA — Project Documentation

**Smart India Hackathon 2026 · Problem SIH26003**
Branch documented: `development` · Last verified: 178 automated tests passing

---

## Table of Contents

1. [Overview](#1-overview)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [Setup & Running](#4-setup--running)
5. [Configuration](#5-configuration)
6. [Database Models](#6-database-models)
7. [Feature Modules](#7-feature-modules)
8. [API Reference](#8-api-reference)
9. [Frontend](#9-frontend)
10. [Adaptive Difficulty](#10-adaptive-difficulty)
11. [Internationalization](#11-internationalization)
12. [Testing](#12-testing)
13. [Development Phases](#13-development-phases)
14. [Bug Fixes in This Revision](#14-bug-fixes-in-this-revision)
15. [Known Issues & Security Notes](#15-known-issues--security-notes)
16. [Future Work](#16-future-work)

---

## 1. Overview

**MEMORA** is a cognitive-support web app for people living with dementia and their caregivers. It combines cognitive games, reminders, a photo-based memory album, mood tracking, an SOS safety feature and a voice assistant, with English and Assamese (অসমীয়া) interfaces.

| User | What they do |
|------|--------------|
| **Patient** | Plays games, sees reminders, browses the Memory Album, logs mood, asks "who is this?" via Memory Rescue, presses SOS |
| **Caregiver** | Manages a patient's people/places/memories and reminders, views progress charts and mood trends, resolves SOS alerts |

Design goals: large elder-friendly UI, minimal typing, no external AI services (all "AI" is deterministic and rule-based).

---

## 2. Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask 3.0.0, Flask-SQLAlchemy 3.1.1 |
| Database | SQLite (`data/memora.sqlite`) |
| Frontend | Jinja2 templates, vanilla CSS/JavaScript, Chart.js-style dashboard chart |
| Auth | Flask cookie session (`user_id`, `user_name`, `user_role`) |
| Voice | Browser Web Speech API |
| Tests | pytest (+ `requests`, `beautifulsoup4` for live-server tests) |

`requirements.txt` — runtime. `requirements-dev.txt` — runtime + test tools.

---

## 3. Project Structure

```
Memora/
├── app.py                  # Flask app, blueprint registration, error handlers
├── config.py               # Config (SECRET_KEY, DATABASE_URL override)
├── conftest.py             # pytest: isolates DB, skips live-server tests if server is down
├── requirements.txt / requirements-dev.txt
├── seed_demo_data.py       # Resets DB and loads demo patient/caregiver data (DESTRUCTIVE)
├── models/models.py        # All SQLAlchemy models
├── routes/
│   ├── users.py            # Login/logout, page routes, language PATCH
│   ├── games.py            # Game pages + activity logging
│   ├── progress.py         # Progress & difficulty APIs
│   ├── reminders.py        # Reminder CRUD
│   ├── memory.py           # People / Places / Memories CRUD + photo upload
│   ├── memory_assistance.py# Memory Rescue search
│   ├── mood.py             # Mood entries & stats
│   └── safety.py           # SOS alerts
├── ai/adaptive_difficulty.py   # Rule-based difficulty engine
├── utils/
│   ├── upload_handler.py   # Validated image uploads
│   ├── memory_search.py    # Query normalization + patient memory search
│   └── response_generator.py   # Template-based spoken/text answers
├── templates/              # 14 Jinja2 pages (base, login, patient_home, games, memory_*, mood, safety, ...)
├── static/
│   ├── css/style.css
│   ├── js/                 # 13 modules (see §9)
│   ├── i18n/{en,as}.json   # 219 translation keys each
│   └── uploads/memory/     # Uploaded photos (created at startup)
├── tests/ + test_*.py      # Test suites and verification scripts
└── PHASE_*.md, AUDIT_*.md  # Per-phase completion / audit reports
```

---

## 4. Setup & Running

### Prerequisites
Python 3.10+ and `pip`.

### Install
```bash
git clone https://github.com/Arunachalam101/Memora.git
cd Memora
git checkout development

python -m venv venv
# Windows:  venv\Scripts\activate        macOS/Linux:  source venv/bin/activate

pip install -r requirements.txt          # app only
pip install -r requirements-dev.txt      # app + test tools
```

### (Optional) Load demo data
```bash
python seed_demo_data.py
```
> ⚠️ Drops and recreates every table. Only run it on a database you are happy to lose.

Demo accounts: patient **Priya Devi** (PIN `1234`), caregiver **Anil Sharma** (PIN `5678`).

### Run
```bash
python app.py
```
Open <http://127.0.0.1:5000>. Tables are created automatically on start.

---

## 5. Configuration

| Setting | Source | Default |
|---------|--------|---------|
| `SECRET_KEY` | env `SECRET_KEY` | `dev-secret-key-change-in-production` |
| Database | env `DATABASE_URL` | `sqlite:///<project>/data/memora.sqlite` |
| `DEBUG` | `config.py` | `True` |

Set `SECRET_KEY` and turn off `DEBUG` before any real deployment.

---

## 6. Database Models

All in `models/models.py`.

| Table | Key columns | Notes |
|-------|-------------|-------|
| `users` | `id, name, pin, role, preferred_language, created_at` | `role` = `patient`/`caregiver`; language `en`/`as` |
| `activity_logs` | `user_id, game_type, score, accuracy, time_taken, difficulty, timestamp` | One row per finished game |
| `reminders` | `user_id, title, type, time("HH:MM"), is_done` | `type`: medicine / appointment / activity |
| `memory_people` | `patient_id, name, relationship, description, photo, is_active` | Soft-delete via `is_active` |
| `memory_places` | `patient_id, name, description, photo, is_active` | Soft-delete |
| `memory_items` | `patient_id, title, description, photo, memory_date, is_active` | Soft-delete |
| `mood_entries` | `patient_id, mood, note, timestamp` | mood ∈ `very_happy, happy, okay, sad, very_sad` |
| `safety_alerts` | `patient_id, alert_type, status, message, created_at, resolved_at` | status `active`/`resolved` |

`User` cascades deletes to its logs and reminders. Photo columns store a **relative path only**.

---

## 7. Feature Modules

### Games (Phases 4–5, 10B)
Four games, all logging to `activity_logs`:
- **Memory Match** — flip cards to match pairs.
- **Attention Test** — react to targets in a grid.
- **Photo–Name Match** — match a person's photo to their name (uses the patient's own album).
- **Who Is This?** — identify a person from their photo.

### Reminders (Phase 3)
Caregiver/patient create timed reminders; patients tick them off.

### Memory Album (Phase 10A)
Caregivers add **people, places and memories** with optional photos. Uploads are validated by `UploadHandler`: extensions `jpg/jpeg/png/gif/webp`, MIME-type check, max **5 MB**, stored under `static/uploads/memory/`.

### Memory Rescue (Phase 10C)
Patient types or speaks a question ("Who is Ravi?"). `memory_search` normalizes it and searches that patient's album; `response_generator` builds a **deterministic template answer** (priority: people › places › memories). No LLM or external API is used. If nothing matches it says the info isn't saved and suggests asking a caregiver.

### Mood Tracking (Phase 10D)
Patient logs a mood + optional note; caregivers see today's mood, history and aggregate stats.

### Safety / SOS (Phase 10E)
Patient presses SOS → an `emergency` alert is created (duplicate active alerts are prevented; `patient_id` always comes from the session). Caregivers list alerts and resolve them.

### Voice Assistant (Phase 7)
`voice_assistant.js` uses the browser speech API for voice commands and read-aloud.

### Caregiver Dashboard (Phase 6)
Patient selector, progress chart, difficulty level, reminders and safety/mood overview.

---

## 8. API Reference

Authorization rule of thumb: a **patient** may only access their own data; a **caregiver** may access any patient. Unauthenticated → `401`, wrong role/patient → `403`.

### Pages (HTML)
| Route | Purpose |
|-------|---------|
| `GET /` | Redirects to `/patient-home` or `/login` |
| `GET/POST /login`, `GET /logout` | Login (creates the user on first login) / logout |
| `GET /patient-home`, `/games`, `/caregiver-dashboard`, `/memory-album`, `/memory-rescue`, `/mood`, `/safety` | Main pages (login required) |
| `GET /game/memory-match`, `/game/attention-test`, `/game/photo-name-match`, `/game/who-is-this` | Game pages |

### Users
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/users/patients` | List patients (caregiver) |
| PATCH | `/api/user/language` | Body `{"language":"en"|"as"}`; `400` on any other code |

### Games & Progress
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/games/log` | Save a finished game |
| GET | `/api/progress/<user_id>` | History for charts |
| GET | `/api/difficulty/<user_id>` | Recommended next difficulty |

### Reminders (`/api`)
| Method | Route |
|--------|-------|
| GET / POST | `/api/reminders` |
| PUT / DELETE | `/api/reminders/<id>` |

### Memory (`/api/memory`)
| Resource | Routes |
|----------|--------|
| People | `GET/POST /people`, `PUT/DELETE /people/<id>` |
| Places | `GET/POST /places`, `PUT/DELETE /places/<id>` |
| Memories | `GET/POST /memories`, `PUT/DELETE /memories/<id>` |
| Rescue | `POST /search` |

### Mood (`/api/mood`)
`POST /entries` · `GET /today` · `GET /history` · `GET /stats`

### Safety (`/api/safety`)
`POST /sos` · `GET /status` · `GET /alerts` · `POST /alerts/<id>/resolve`

### Errors
`404`, `500` and uncaught exceptions render `error.html`; paths starting with `/api/` get JSON `{"error": ...}` instead.

---

## 9. Frontend

`templates/base.html` provides the navbar (with EN/AS toggle), flash area and script includes; every page extends it.

| JS module | Role |
|-----------|------|
| `i18n.js` | Loads `en.json`/`as.json`, applies `data-i18n` keys, saves choice to localStorage + DB |
| `error_handler.js` | Global fetch/UI error display |
| `memory_match.js`, `attention_test.js`, `photo_name_match.js`, `who_is_this.js` | Game logic |
| `reminders.js` | Reminder UI |
| `dashboard_chart.js` | Caregiver progress chart |
| `memory_album.js` | Album CRUD + uploads |
| `memory_rescue.js` | Rescue search UI |
| `mood.js` | Mood picker & history |
| `safety.js` | SOS button & alert list |
| `voice_assistant.js` | Speech input/output |

---

## 10. Adaptive Difficulty

`ai/adaptive_difficulty.py` — transparent rule-based logic (a stand-in for a future ML model):

- Fewer than 3 sessions → `easy`
- Otherwise average accuracy of the last 3 sessions: **≥ 80 % → hard**, **≥ 50 % → medium**, else **easy**

| Difficulty | Memory Match | Attention Test |
|-----------|--------------|----------------|
| easy | 4 pairs | 6 rounds, grid 4 |
| medium | 6 pairs | 8 rounds, grid 6 |
| hard | 8 pairs | 10 rounds, grid 9 |

---

## 11. Internationalization

Languages: **English (`en`)** and **Assamese (`as`)**, 219 keys each. Choice is stored in `localStorage` and in `users.preferred_language`, and restored at login. To add a string: add the same key to both JSON files and use `data-i18n="key"` in the template (`test_i18n_coverage.py` checks parity).

---

## 12. Testing

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

- **Without a server:** ~169 tests run in seconds. They use an isolated temporary database (see `conftest.py`) — your real `data/memora.sqlite` is never touched.
- **Live-server tests** (`test_e2e.py`, `test_requirements.py`, `test_caregiver.py`, `test_page_load.py`, `test_patch_*.py`, …) need `python app.py` running on port 5000 and are **skipped automatically** if it isn't. To run everything, start the server on its own database so the two don't interfere:

```bash
# terminal 1
DATABASE_URL=sqlite:////tmp/live.sqlite python app.py
# terminal 2
python -m pytest -q          # 178 passed
```
(Windows PowerShell: `$env:DATABASE_URL="sqlite:///C:/temp/live.sqlite"`.)

Main suites: `test_phase10a_memory.py`, `test_phase10b_memory_games.py`, `test_phase10c_memory_assistance.py`, `test_phase10d_mood.py`, `tests/test_phase10e_safety.py`, `test_authorization_audit.py`, `test_i18n*.py`.

---

## 13. Development Phases

| Phase | Deliverable |
|-------|-------------|
| 0–2 | Environment, models, login & navigation |
| 3 | Reminders |
| 4 | Games (Memory Match, Attention Test) |
| 5 | Adaptive difficulty |
| 6 | Caregiver dashboard |
| 7 | Voice assistant |
| 8 | English/Assamese toggle |
| 9 | Demo polish, error handling |
| 10A | Memory Album + photo uploads |
| 10B | Memory-based games (Photo–Name Match, Who Is This?) |
| 10C | Memory Rescue search |
| 10D | Mood tracking |
| 10E | Safety / SOS |
| 10F | Audit (`AUDIT_PHASE_10F_REPORT.md`) |

---

## 14. Bug Fixes in This Revision

**Problem:** running the test-suite destroyed the real database. Symptoms: `sqlite3.OperationalError: no such table: users`, `POST /login → 500`, and `test_requirements.py` failing with a JSON decode error.

**Root cause:** the test fixtures set `SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'` *after* `app.py` had already called `db.init_app(app)`. Flask-SQLAlchemy 3.x builds the engine inside `init_app`, so the override was ignored and the fixtures' `db.drop_all()` ran against `data/memora.sqlite`. `test_phase10b_memory_games.py` did not attempt isolation at all.

**Fix:**
| File | Change |
|------|--------|
| `config.py` | Database URI now read from `DATABASE_URL` (falls back to the old path) |
| `conftest.py` (new) | Sets `DATABASE_URL` to a temp file **before** the app is imported; skips live-server scripts when no server is running |
| `requirements-dev.txt` (new) | Adds `pytest`, `requests`, `beautifulsoup4`, which the tests import but `requirements.txt` lacked |

**Result:** 177 pass / 1 fail / server errors → **178 passed, 0 failed, 0 server tracebacks**; the real database is no longer modified by tests.

---

## 15. Known Issues & Security Notes

Not changed in this revision (behavior decisions for the project owner):

1. **PIN is never verified.** `POST /login` looks a user up by name only; the PIN is stored at first login but ignored afterwards, so anyone who knows a name can log in as that user (including a caregiver). PINs are also stored in plain text. *Recommendation:* hash PINs (`werkzeug.security`) and check them on login.
2. **Login auto-creates accounts** for unknown names.
3. `DEBUG = True` and a default `SECRET_KEY` — fine for demos, unsafe in production.
4. No CSRF protection on form/JSON endpoints.
5. Deprecation warnings: `Query.get()` (use `db.session.get()`) and `datetime.utcnow()` (use `datetime.now(timezone.utc)`).
6. Unused imports in `routes/memory_assistance.py`, `progress.py`, `games.py`, `safety.py`.
7. `seed_demo_data.py` wipes all tables without confirmation.

---

## 16. Future Work

- Fix the authentication issues in §15.
- Replace rule-based difficulty with a trained model once enough data exists.
- Push notifications / SMS for reminders and SOS.
- Add more regional languages.
- Alembic migrations, Docker image, production WSGI server (gunicorn) and PostgreSQL.