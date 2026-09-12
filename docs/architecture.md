## Development Phases

**Phase 0 — Environment setup**
- Create venv, install Flask + Flask-SQLAlchemy
- Basic `app.py` that runs a "Hello Memora" route to confirm Flask works

**Phase 1 — Database & models**
- Define `User`, `ActivityLog`, `Reminder` models in `models/models.py`
- Initialize SQLite DB, create tables
- Test with a simple script that adds/reads a dummy user

**Phase 2 — Auth & navigation skeleton**
- `login.html` + `/login` route (name + optional PIN, session-based)
- `base.html` layout (nav, elder-friendly styling)
- `patient_home.html` with placeholder sections (reminders, games button)

**Phase 3 — Reminders module**
- CRUD routes in `routes/reminders.py`
- Reminders shown on `patient_home.html`
- Simple add/edit form (can live on caregiver dashboard later)

**Phase 4 — Games (core feature)**
- Memory Match game (HTML + `memory_match.js`)
- Attention Test game (HTML + `attention_test.js`)
- POST results to `/api/games/log`

**Phase 5 — Adaptive difficulty (the "AI" piece)**
- `ai/adaptive_difficulty.py` logic
- Wire it to update after each game session
- Reflect current difficulty back to the patient/caregiver

**Phase 6 — Caregiver dashboard**
- `/api/progress/<user_id>` endpoint
- Chart.js line chart of scores/accuracy over time
- Show difficulty level + reminders list

**Phase 7 — Voice assistant**
- `voice_assistant.js` using Web Speech API
- Text-to-speech for reminders
- Speech-to-text for simple queries

**Phase 8 — Regional language toggle**
- `en.json` / `as.json` dictionaries
- JS function to swap `data-i18n-key` text on toggle

**Phase 9 — Polish for demo**
- Consistent elder-friendly styling across all pages
- Error handling, loading states
- Seed some dummy data so the dashboard looks good in the demo
- Rehearse the end-to-end flow: login → play game → difficulty adapts → dashboard updates → voice reads a reminder

