# PHASE 10D IMPLEMENTATION PLAN
## Mood Tracking + Enhanced Reminders
**Status:** PLAN REVIEW - REVISED FOR IMPLEMENTATION  
**Date:** January 17, 2025 (Revised September 23, 2026)

---

## TABLE OF CONTENTS
1. Current Architecture Audit
2. Proposed MoodEntry Model
3. API Endpoints
4. Routes & Pages
5. Frontend Changes (Patient UI)
6. Frontend Changes (Caregiver UI)
7. Voice Assistant Changes
8. i18n Changes
9. Database Initialization Approach
10. Security & Authorization
11. Testing Strategy
12. Exact Files to Create
13. Exact Files to Modify
14. Dependencies
15. Implementation Order
16. Risks & Edge Cases
17. Scope Boundaries
18. Expected Patient Workflow
19. Expected Caregiver Workflow
20. Regression Testing Strategy

---

## 1. CURRENT ARCHITECTURE AUDIT

### 1.1 Reminder System (Existing)

**Model:** `models/models.py` - `Reminder` class
```
├─ id (PK)
├─ user_id (FK → User)
├─ title (String 255)
├─ type (String 50) → "medicine", "appointment", "activity"
├─ time (String 5) → "HH:MM" format
├─ is_done (Boolean, default=False)
└─ created_at (DateTime)
```

**Current Types (hardcoded in reminders.js):**
- 💊 Medicine
- 📅 Appointment  
- 🎯 Activity

**Routes:** `routes/reminders.py`
- `GET /api/reminders` — Fetch user's reminders (requires login)
- `POST /api/reminders` — Create reminder (user_id from session)
- `PUT /api/reminders/<id>` — Update reminder (ownership check)
- `DELETE /api/reminders/<id>` — Delete reminder (ownership check)

**Authorization Pattern:**
- `require_login()` function checks session['user_id']
- Ownership check: `reminder.user_id != user_id` → 403 Forbidden
- No user_id trusted from client (always from session)

**Frontend UI:** `static/js/reminders.js`
- `REMINDER_TYPES` constant with icon/label/color per type
- `renderPatientReminders()` — Displays on patient_home.html
- `renderCaregiverReminders()` — Displays on caregiver_dashboard.html
- `markReminderDone()` — Updates is_done field
- Form submission for create: title, type, time → POST /api/reminders

**Voice Integration:** `static/js/voice_assistant.js`
- `processVoiceQuery()` checks: `if (query.includes('reminder')...`
- Calls `respondToReminderQuery()` (not shown in excerpt, but exists)
- Reminders data exposed via `VoiceAssistant.remindersData`

**Patient Home Display:** `templates/patient_home.html`
```html
<div class="reminders-section">
    <h2>📋 Today's Reminders</h2>
    <div id="reminders-container">
        (populated by renderPatientReminders())
    </div>
</div>
```

### 1.2 Authorization Architecture

**Pattern (from routes/memory.py):**
```python
def check_memory_authorization(patient_id, can_edit=False):
    # 1. Get user_id from session
    # 2. Fetch User from database
    # 3. Patient: can view own (patient_id == user_id), no edit
    # 4. Caregiver: can view/edit all patients
    # 5. Others: forbidden
```

**User Model Fields:**
- `id` (PK)
- `name` (String)
- `pin` (String, optional)
- `role` (String) → "patient" or "caregiver"
- `preferred_language` (String, default='en')
- `created_at` (DateTime)
- Relationships: activity_logs, reminders, memory_people, memory_places, memory_items

**Login Pattern (routes/users.py):**
```python
session['user_id'] = user.id
session['user_name'] = user.name
session['user_role'] = user.role
```

**Role-based Access:**
- Patient: can access own data only, limited actions
- Caregiver: can access all patient data (no formal mapping yet, all patients)

### 1.3 UI/UX Patterns

**Patient Home:**
- Welcome card
- Voice assistant section (2 buttons: "Ask Memora", "Read reminders")
- Reminders section
- Games section
- Memory section (Phase 10A/10C)

**Caregiver Dashboard:**
- Patient selector dropdown
- Patient overview cards (name, difficulty, games played, avg accuracy)
- Progress charts (2 Chart.js canvases: accuracy, score)
- Recent activity table
- Reminder management section

**Chart Library:** Chart.js (already in use)
- CHART_OPTIONS defined in static/js/dashboard_chart.js
- Colors: #4A90D9 (blue), #27AE60 (green), #E0E0E0 (grid)
- Responsive, maintainAspectRatio: true

### 1.4 i18n System

**Supported Languages:**
- English (en.json) — 200+ keys
- Assamese (as.json) — 200+ keys
- Tamil (NOT in Phase 10D - Phase 10E scope)

**Translation Keys for Reminders (existing):**
- reminders_section_title
- reminders_loading
- reminders_empty
- voice_read_reminders
- voice_hint

**Pattern:** HTML elements use `data-i18n-key="key_name"` → i18n.js translates on load

**Implementation:** static/js/i18n.js
- Loads JSON from static/i18n/{lang}.json
- Replaces textContent of elements with matching data-i18n-key
- localStorage caches language preference

### 1.5 Testing Architecture

**Framework:** pytest with Flask test client
**Database:** In-memory SQLite (`:memory:`) in tests
**Fixtures:** client, users, db fixtures with pre-populated data

**Test Pattern:**
```python
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        # Create test users/data
        yield app.test_client()
        db.drop_all()
```

**Existing Test Files:**
- test_phase10a_memory.py (35+ tests)
- test_phase10b_memory_games.py (30+ tests)
- test_phase10c_memory_assistance.py (26 tests)
- test_phase7_voice.py (e2e voice tests)

**Authorization Tests Pattern:**
- test_unauthenticated_access (no session → 401)
- test_patient_can_view_own_data (patient access own)
- test_patient_cannot_edit (patient view-only)
- test_caregiver_can_view_all_data (caregiver access)
- test_caregiver_can_edit (caregiver modify)

### 1.6 Database & Config

**Database:** SQLite at `data/memora.sqlite`
**Configuration:** config.py
```python
SQLALCHEMY_DATABASE_URI = "sqlite:///{BASE_DIR}/data/memora.sqlite"
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

**Current Models:** User, ActivityLog, Reminder, MemoryPerson, MemoryPlace, MemoryItem

**No Active Migrations:** Tables created via `db.create_all()` on app startup

---

## 2. PROPOSED MOODENTRY MODEL

### 2.1 Schema

**Table:** `mood_entries`

```python
class MoodEntry(db.Model):
    """Patient mood tracking entries (Phase 10D)"""
    __tablename__ = 'mood_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), 
                           nullable=False, index=True)
    mood = db.Column(db.String(20), nullable=False)  
        # Stored values: "very_happy", "happy", "okay", "sad", "very_sad"
    note = db.Column(db.Text, nullable=True)  
        # Optional patient/caregiver note (max 500 chars)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
        # When mood was recorded (UTC)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
        # When record was created
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                           onupdate=datetime.utcnow)
        # When record was last modified
    
    user = db.relationship('User', backref='mood_entries')
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'mood': self.mood,
            'note': self.note,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<MoodEntry {self.id}: {self.mood} at {self.timestamp}>"
```

### 2.2 Mood Values (Database Storage)

**STORED IN DATABASE AS STRING VALUES (not emoji):**
- `very_happy` — Stored as string "very_happy"
- `happy` — Stored as string "happy"
- `okay` — Stored as string "okay"
- `sad` — Stored as string "sad"
- `very_sad` — Stored as string "very_sad"

**DISPLAYED IN UI WITH EMOJI + LABELS:**
| Database Value | UI Display | Emoji | Color |
|---|---|---|---|
| very_happy | Very Happy | 😊 | #27AE60 (green) |
| happy | Happy | 🙂 | #4A90D9 (blue) |
| okay | Okay | 😐 | #F39C12 (orange) |
| sad | Sad | 😟 | #E74C3C (light red) |
| very_sad | Very Sad | 😔 | #C0392B (dark red) |

**Rationale for 5-Option Mood Set:**
- Simple, finite set (not continuous scale or slider)
- Elderly-friendly with clear emoji mapping
- Paired opposites (happy/very happy, sad/very_sad) for nuance without complexity
- Consistent with MEMORA's visual language (emoji-first, elderly-focused)
- NOT intended for medical diagnosis or mental health assessment

### 2.3 Constraints & Validations

**Database Constraints:**
- patient_id NOT NULL and FK to users(id)
- mood NOT NULL, valid string values only
- timestamp indexed for efficient historical queries
- Multiple entries per day allowed (one per timestamp)

**Application-Level Validations (all endpoints):**
- mood must be exactly one of: `["very_happy", "happy", "okay", "sad", "very_sad"]`
- note (if provided): max 500 characters, HTML escaped on display
- timestamp: validated server-side (must be within last 30 days to prevent backdating)
- patient_id: ALWAYS derived from session['user_id'], NEVER trusted from client
- Caregiver creating entry: Not allowed in Phase 10D (patients only)

### 2.4 Existing Reminder Model — NO CHANGES

**Current Reminder structure remains intact:**
```python
class Reminder(db.Model):
    __tablename__ = 'reminders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # "medicine", "appointment", "activity"
    time = db.Column(db.String(5), nullable=False)  # "HH:MM" format
    is_done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Why NO Changes:**
- `is_done` boolean field is sufficient for Phase 10D reminder tracking
- No category/status fields needed yet (defer to later phase if required)
- Existing API fully functional and tested
- Adding unnecessary fields risks breaking existing code

---

## 3. API ENDPOINTS

### 3.1 Mood Endpoints (NEW)

**Route Prefix:** `/api/mood`  
**Authorization:** Session-based (require_login)  
**Patient Operations:** Create entries (own only), read own history  
**Caregiver Operations (Phase 10D):** View patient mood data (read-only, no create/edit)

#### Endpoint 1: Create Mood Entry (PATIENT ONLY)
```
POST /api/mood/entries
Content-Type: application/json

{
    "mood": "very_happy",
    "note": "Had a good day with family"  // optional, max 500 chars
}

Response (201):
{
    "id": 1,
    "patient_id": 5,
    "mood": "very_happy",
    "note": "Had a good day with family",
    "timestamp": "2025-01-17T14:30:00.000000",
    "created_at": "2025-01-17T14:30:00.000000"
}

Errors:
- 401: Not authenticated
- 400: Invalid mood value, missing fields, or request body error
- 500: Server error
```

**Logic:**
- Get user_id from session['user_id']
- Validate mood in VALID_MOODS list: ["very_happy", "happy", "okay", "sad", "very_sad"]
- Validate note length (max 500 chars if provided)
- Validate timestamp is within last 30 days
- Create MoodEntry with patient_id = user_id (ALWAYS from session, never client)
- Return created entry with 201

#### Endpoint 2: Get Today's Mood (PATIENT & CAREGIVER)
```
GET /api/mood/today?patient_id=5

Response (200):
{
    "has_entry": true,
    "entry": {
        "id": 1,
        "mood": "very_happy",
        "note": "Had a good day",
        "timestamp": "2025-01-17T14:30:00.000000"
    }
}
OR
{
    "has_entry": false,
    "entry": null
}

Errors:
- 401: Not authenticated
- 403: Not authorized to view this patient's mood
- 400: Invalid query params
- 500: Server error
```

**Logic:**
- Get user_id from session['user_id']
- If patient: patient_id in query must equal user_id (patient can only view own)
- If caregiver: can view any patient (for now)
- Query MoodEntry for patient_id = requested_patient_id, date = today
- Return latest entry for today if exists, with has_entry flag
- Return 403 if patient tries to view another patient's mood

#### Endpoint 3: Get Mood History (PATIENT & CAREGIVER)
```
GET /api/mood/history?patient_id=5&limit=30&offset=0

Response (200):
{
    "total": 47,
    "entries": [
        {
            "id": 1,
            "mood": "very_happy",
            "note": "Good day",
            "timestamp": "2025-01-17T14:30:00.000000"
        },
        ...
    ]
}

Errors:
- 401: Not authenticated
- 403: Not authorized to view this patient's history
- 400: Invalid query params
- 500: Server error
```

**Logic:**
- Get user_id from session['user_id']
- Check authorization: patient can only view own, caregiver can view any
- Query MoodEntry for patient_id = requested_patient_id
- Order by timestamp DESC (most recent first)
- Apply limit (default 30, max 100) and offset for pagination
- Return list with total count

#### Endpoint 4: Get Mood Statistics (CAREGIVER ONLY - Phase 10D)
```
GET /api/mood/stats?patient_id=5&days=7

Response (200):
{
    "patient_id": 5,
    "period_days": 7,
    "total_entries": 5,
    "mood_distribution": {
        "very_happy": 1,
        "happy": 2,
        "okay": 1,
        "sad": 1,
        "very_sad": 0
    },
    "most_recent": {
        "mood": "happy",
        "timestamp": "2025-01-16T10:00:00.000000"
    }
}

Errors:
- 401: Not authenticated
- 403: User is not a caregiver
- 400: Invalid patient_id or days param
- 500: Server error
```

**Logic:**
- Get user_id from session['user_id']
- Check: user.role == 'caregiver' (only caregivers can access stats)
- Query MoodEntry for patient_id = requested_patient_id, last N days
- Calculate mood_distribution: count of each mood value
- Return factual statistics (NO medical interpretation)
- Return 403 if patient tries to access (patient must use /history instead)

**CRITICAL: Statistics are FACTUAL ONLY**
- ✅ Acceptable: "Sad recorded 3 times in last 7 days"
- ❌ NOT acceptable: "Patient shows signs of depression", "Recommend mental health intervention"
- ❌ NOT acceptable: Any medical diagnosis, anxiety detection, or clinical assessment

### 3.2 Reminder Endpoints (EXISTING — NO NEW ENDPOINTS)

**Current endpoints remain fully functional:**
- `GET /api/reminders` — Fetch user's reminders
- `POST /api/reminders` — Create reminder
- `PUT /api/reminders/<id>` — Update reminder
- `DELETE /api/reminders/<id>` — Delete reminder

**No changes to reminder endpoints in Phase 10D**
- Reminder model unchanged (is_done field sufficient)
- Authorization pattern unchanged
- All existing tests remain valid

## 4. ROUTES & PAGES

### 4.1 New Route

#### Route: Mood Page (Patient)
```
URL: /mood
Method: GET
Decorator: @login_required
Template: templates/mood.html
Blueprint: routes/users.py
```

**Purpose:** Patient records mood and views history  
**Content:**
- Welcome message
- Today's Mood section (5 large emoji buttons)
- Optional note textarea
- Mood confirmation message (hidden until submit)
- Recent mood history (last 7-14 days as cards or timeline)
- Help/guidance section
- Navigation back to home

**Backend Implementation (routes/users.py):**
```python
@users_bp.route('/mood')
@login_required
def mood():
    """Mood tracking page - Phase 10D"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('mood.html', user=user)
```

### 4.2 New API Routes

**Blueprint:** `routes/mood.py` (NEW FILE)  
**Prefix:** `/api/mood`

**Endpoints:**
1. POST /api/mood/entries — Create mood (patient only)
2. GET /api/mood/today — Get today's mood (patient & caregiver)
3. GET /api/mood/history — Get mood history (patient & caregiver)
4. GET /api/mood/stats — Get mood statistics (caregiver only)

### 4.3 Modified Routes

**routes/users.py:**
- Add /mood route (new route above)

**app.py:**
- Import mood blueprint
- Register mood blueprint

**No changes to existing routes** (reminders, games, memory, progress remain identical)

---

## 5. FRONTEND CHANGES (PATIENT UI)

### 5.1 New Files

#### File 1: templates/mood.html (NEW)
**Size:** ~200-250 lines  
**Purpose:** Patient mood recording and history page  
**Extends:** base.html

**Sections:**
1. Page header with welcome message
2. "Today's Mood" section with 5 emoji buttons (large, elderly-friendly)
3. Optional note textarea (after mood selected)
4. Submit button
5. Confirmation message (hidden until submit)
6. Recent mood history (last 7-14 days as cards)
7. Help/guidance section ("How to Use")
8. Navigation buttons (Back to Home, etc.)

**Styling:**
- Large buttons (100px+) for elderly touch targets
- Color-coded per mood value
- Visual feedback on selected state (border, highlight)
- Emoji prominently displayed
- Responsive design (mobile + tablet + desktop)
- Bootstrap 5 classes for consistency

**i18n Keys Used:**
- mood_title, mood_subtitle, mood_heading
- mood_label_very_happy, mood_label_happy, etc.
- mood_note_label, mood_note_placeholder, mood_note_hint
- mood_saved, mood_saved_with_note, mood_error, mood_loading
- mood_history_title, mood_history_label, mood_no_history, mood_today_label
- btn_back_to_home, btn_check_mood

**Why This File Needs to Change:**
- New feature (mood tracking) requires new page UI
- Must be separate from home page for focused interaction
- Elderly users need large, uncluttered interface

#### File 2: static/js/mood.js (NEW)
**Size:** ~350-400 lines  
**Purpose:** Mood page state management, API integration, UI updates

**Key Objects & Functions:**
```javascript
const MoodState = {
    currentMood: null,
    currentNote: '',
    todayEntry: null,
    historyEntries: [],
    isSubmitting: false
};

// Initialization & page load
async function initMoodPage() { }

// Handle mood button clicks
function handleMoodSelect(mood) { }

// Submit mood to API
async function submitMood(mood, note) { }

// Load today's mood entry
async function loadTodaysMood() { }

// Load mood history
async function loadMoodHistory() { }

// Display today's mood
function displayTodaysMood(entry) { }

// Render mood history timeline/cards
function renderMoodHistory(entries) { }

// Error/success handling
function showMoodError(message) { }
function showMoodSuccess(message) { }
```

**Error Handling:**
- Network errors: graceful fallback message
- Invalid mood: client-side validation before submit
- Auth failure: redirect to login
- Server errors: show user-friendly message + retry option

**Why This File Needs to Change:**
- New mood recording UI requires JavaScript state management
- API calls to /api/mood/* endpoints must be handled
- History display and user interaction need event handlers

### 5.2 Modified Files

#### File 1: templates/patient_home.html (MODIFIED)
**What:** Add "🎭 Mood Tracker" section

**Where:** After Memory section (before closing div.container)

**Lines to Add:** ~10-12 lines

**Change Type:** ADDITION (no deletion)

**Exact Addition:**
```html
<!-- Mood Tracker Section (Phase 10D) -->
<div class="placeholder-section">
    <h2>🎭 Mood Tracker</h2>
    <p data-i18n-key="mood_section_subtitle">Record how you're feeling today</p>
    <a href="{{ url_for('users.mood') }}" class="btn btn-secondary" data-i18n-key="btn_check_mood">Check Your Mood</a>
</div>
```

**Why This File Needs to Change:**
- Navigation to mood page must be accessible from home
- Patients need easy access to new mood feature
- Consistent UI pattern with existing sections (games, memory, reminders)

#### File 2: static/js/reminders.js (NOT MODIFIED)
**Status:** NO CHANGES  
**Reason:** Reminder functionality is independent of mood tracking
**Verification:** All existing reminder code remains valid

#### File 3: static/js/voice_assistant.js (MODIFIED - see section 7)
**Covered in:** Section 7 - Voice Assistant Changes

---

## 6. FRONTEND CHANGES (CAREGIVER UI)

### 6.1 Modified Files

#### File 1: templates/caregiver_dashboard.html (MODIFIED)
**What:** Add mood overview section to patient overview stats

**Where:** In patient overview stats section (after avg_accuracy stat card, ~line 30-35)

**Lines to Add:** ~15-20 lines

**Change Type:** ADDITION (no deletion)

**Exact Addition:**
```html
<!-- Mood Overview (Phase 10D) -->
<div class="stat-card">
    <span class="stat-label" data-i18n-key="stat_current_mood">Current Mood</span>
    <span class="stat-value" id="overview-mood">-</span>
</div>
<div class="stat-card">
    <span class="stat-label" data-i18n-key="mood_last_recorded">Last Recorded</span>
    <span class="stat-value" id="overview-mood-time">-</span>
</div>
```

**Why This File Needs to Change:**
- Caregivers need quick access to patient's current mood
- Factual information (latest mood + timestamp) supports caregiver awareness
- Integrated into existing patient overview dashboard
- Minimal visual footprint (2 stat cards following existing pattern)

#### File 2: static/js/dashboard_chart.js (MODIFIED)
**What:** Add function to fetch and display patient mood in overview section

**Where:** After existing fetchPatientProgress() function (~line 120)

**Lines to Add:** ~50-60 lines

**Change Type:** ADDITION (no deletion)

**New Functions:**
```javascript
async function fetchPatientMood(patientId) {
    // Fetch /api/mood/today?patient_id=patientId
    // Update #overview-mood and #overview-mood-time DOM elements
    // Handle 403 (no permission), 404 (no mood), and other errors
    // Return mood data or null
}

function displayMoodEmoji(moodValue) {
    // Map "very_happy" → "😊", "happy" → "🙂", etc.
    // Return emoji string with label
}

function updateMoodDisplay(moodData) {
    // Update DOM with mood value and timestamp
    // Format timestamp as human-readable (e.g., "Today at 2:30 PM")
}
```

**Why This File Needs to Change:**
- Dashboard must query and display patient mood
- Existing chartjs code is separate from mood display
- Mood data must update when patient selector changes
- Factual display (no interpretation or medical assessment)

---

## 7. VOICE ASSISTANT CHANGES

### 7.1 Extend Existing Voice System (Do Not Replace)

**Current Implementation:**
- `static/js/voice_assistant.js` contains VoiceAssistant object
- `processVoiceQuery()` decision tree routes intents
- Existing intents: time, date, reminders, greetings, memory rescue (Phase 10C)

**Phase 10D Additions:**
- Extend `processVoiceQuery()` decision tree with mood intent
- Add new `isMemoryMoodQuery()` detection function
- Add new `handleMoodQuery()` handler function
- Add new `getMoodLabel()` helper function
- All existing intents remain unchanged

### 7.2 New Intent: Mood Query (READ-ONLY)

**Supported Queries:**
- "How am I feeling?"
- "What's my mood?"
- "What was my mood today?"

**NOT Supported (Write Operations Deferred):**
- "I'm very happy" (requires confirmation, too risky for voice)
- "Record my mood as happy" (patients use UI, safer)

**Voice Response Examples:**
- "Your mood today is very happy, recorded at 2:30 PM."
- "You haven't recorded your mood yet today."
- "I couldn't access your mood data. Please check back later."

### 7.3 Implementation in voice_assistant.js

**Location:** After memory companion query handling in `processVoiceQuery()`

**Decision Tree Order (Updated):**
1. Memory Companion Query (Phase 10C) — "Who is...", "Tell me about..."
2. **Mood Query (Phase 10D NEW)** — "How am I feeling?", "What's my mood?"
3. Time query — "What time is it?"
4. Date query — "What's today's date?"
5. Reminder query — "What reminders do I have?"
6. Greeting — "Hello", "How are you?"
7. No match — "Sorry, I didn't understand"

**Code Addition (40-50 lines):**
```javascript
// Phase 10D: Mood query detection & handling
function isMoodQuery(query) {
    // Keywords: "mood", "feeling", "how am i", "my mood"
    // Return true if any keyword detected
}

async function handleMoodQuery(query) {
    try {
        // Call GET /api/mood/today
        // If mood exists: speak "Your mood today is [label]..."
        // If no mood: speak "You haven't recorded your mood yet..."
        // On error: speak "I couldn't access your mood data..."
    } catch (error) {
        // Log error, speak generic error message
    }
}

function getMoodLabel(moodValue) {
    // Map database values to readable labels
    // "very_happy" → "very happy"
    // "happy" → "happy"
    // etc.
}
```

**Why This File Needs to Change:**
- Extend voice capability to support mood queries
- Patients can ask about their mood without leaving page
- Read-only operation (no unsafe write commands)
- Consistent with existing voice assistant pattern

**Critical Constraint:**
- Do NOT replace existing voice_assistant.js
- Do NOT modify existing intent handlers (time, date, reminders, memory, greetings)
- Only ADD new mood query detection + handler
- All tests for existing voice intents must still pass

---

## 8. I18N CHANGES

### 8.1 Supported Languages (Phase 10D)

**Phase 10D Supports:**
- ✅ English (en.json)
- ✅ Assamese (as.json)

**NOT Supported in Phase 10D:**
- ❌ Tamil (deferred to later phase)

### 8.2 New Translation Keys

**Total New Keys: 30** (identical structure in both en.json and as.json)

**Mood Selection Labels:**
- `mood_label_very_happy` — "😊 Very Happy"
- `mood_label_happy` — "🙂 Happy"
- `mood_label_okay` — "😐 Okay"
- `mood_label_sad` — "😟 Sad"
- `mood_label_very_sad` — "😔 Very Sad"

**Mood Page Headers & Labels:**
- `mood_title` — "Mood Tracker"
- `mood_subtitle` — "How are you feeling today?"
- `mood_heading` — "🎭 Check Your Mood"
- `mood_section_subtitle` — "Record how you're feeling today"
- `mood_note_label` — "Add a note (optional)"
- `mood_note_placeholder` — "What happened today?"
- `mood_note_hint` — "Share what made you feel this way"

**Mood Messages:**
- `mood_saved` — "Your mood has been saved"
- `mood_saved_with_note` — "Your mood and note have been saved"
- `mood_error` — "Could not save your mood. Please try again."
- `mood_loading` — "Loading your mood..."
- `mood_empty` — "You haven't recorded a mood yet"

**Mood History:**
- `mood_history_title` — "Your Mood This Week"
- `mood_history_label` — "Mood History"
- `mood_no_history` — "No mood records yet"
- `mood_today_label` — "Today"
- `mood_days_ago` — "{n} days ago"

**Dashboard (Caregiver):**
- `stat_current_mood` — "Current Mood"
- `mood_last_recorded` — "Last Recorded"

**Navigation:**
- `btn_check_mood` — "Check Your Mood"

**Voice:**
- `voice_mood_query_greeting` — "What would you like to know about your mood?"

### 8.3 File Updates

#### File: static/i18n/en.json (MODIFIED)
**What:** Add 30 mood-related translation keys

**Where:** After existing memory_rescue keys (around line 200-210)

**Format:** JSON object with key-value pairs
```json
{
  "existing_keys": "remain unchanged",
  "mood_title": "Mood Tracker",
  "mood_subtitle": "How are you feeling today?",
  ...
  "mood_days_ago": "{n} days ago"
}
```

**Lines to Add:** ~40 lines

**Why:** Support English UI text for mood feature

#### File: static/i18n/as.json (MODIFIED)
**What:** Add 30 mood-related translation keys (Assamese)

**Where:** After existing memory_rescue keys (around line 200-210)

**Format:** Identical key structure to en.json, with Assamese translations

**Lines to Add:** ~40 lines

**Why:** Support Assamese UI text for mood feature

### 8.4 Key Structure Requirements

**Consistency Check:**
- en.json and as.json must have IDENTICAL key names
- Each key in en.json must exist in as.json
- Values differ (English vs Assamese), but keys are exactly the same
- No emoji in JSON values (emoji in UI only)

**Validation Before Implementation:**
- Script to compare en.json and as.json key sets
- Error if keys don't match between languages
- Ensure no orphaned keys

---

## 9. DATABASE INITIALIZATION APPROACH

### 9.1 Current Mechanism (Existing Project)

**Project Uses: SQLAlchemy with Automatic Table Creation**

**Current Flow:**
1. `app.py` imports models from `models/models.py`
2. `models/models.py` defines SQLAlchemy models (User, ActivityLog, Reminder, etc.)
3. `app.py` calls `db.init_app(app)` to initialize SQLAlchemy
4. On app startup (`if __name__ == '__main__'`), `db.create_all()` is called in app context
5. SQLAlchemy examines all model classes and creates missing tables in SQLite

**Code in app.py (lines 90-92):**
```python
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
```

**No Migration Tool Used:**
- Project does NOT use Alembic, Flask-Migrate, or Flyway
- No migrations/ folder or version control for schema changes
- Each environment creates tables directly from models

### 9.2 Phase 10D Approach: Follow Existing Mechanism

**Step 1: Add MoodEntry Model to models/models.py**
- Place after MemoryItem class (around line 250)
- Define with all fields: id, patient_id, mood, note, timestamp, created_at, updated_at
- Include relationship: `user = db.relationship('User', backref='mood_entries')`
- Include to_dict() and __repr__() methods

**Step 2: No Additional Database Setup Required**
- When app.py runs `db.create_all()`, SQLAlchemy automatically creates mood_entries table
- Existing tables (users, reminders, memory_people, memory_places, memory_items) remain intact
- Process is idempotent (safe to run multiple times)

**Step 3: Verify Table Creation**
- Check data/memora.sqlite after first run
- Confirm mood_entries table exists with correct schema
- Verify existing data in other tables is untouched

### 9.3 CRITICAL CONSTRAINTS

**MUST NOT:**
- ❌ Delete existing database
- ❌ Drop existing tables
- ❌ Reset user data
- ❌ Reset memory data
- ❌ Reset game activity logs
- ❌ Reset reminders
- ❌ Modify existing data
- ❌ Run db.drop_all() in production

**MUST:**
- ✅ Preserve all existing tables and data
- ✅ Only add new mood_entries table
- ✅ Maintain backward compatibility with Phase 10A/B/C
- ✅ Test in dev environment first
- ✅ Backup data/memora.sqlite before first run

### 9.4 Testing Database Initialization

**In Test Environment:**
- Tests use in-memory SQLite (`:memory:`)
- Each test fixture calls `db.create_all()` to create all tables including mood_entries
- Tests populate with demo data and run
- After tests, tables are dropped (in-memory, so no cleanup needed)

**Test Fixture Pattern (existing):**
```python
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()  # Creates all tables including new mood_entries
        # Populate test data...
        yield app.test_client()
        db.drop_all()  # Clean up after test
```

**No Changes Needed to Test Fixtures:**
- Existing fixtures will automatically create mood_entries table
- MoodEntry model is imported in test files, so table is recognized
- All Phase 10A/B/C tests continue to work

---

## 10. SECURITY & AUTHORIZATION

### 10.1 Session-Based Authentication

**Existing Pattern (Unchanged):**
- Login stores `session['user_id']`, `session['user_name']`, `session['user_role']`
- All API endpoints check `session.get('user_id')` to verify authentication
- Missing session['user_id'] → 401 Unauthorized

**Phase 10D Security: Follows Existing Pattern**

### 10.2 Patient (role='patient') Authorization

**Patient CAN:**
- ✅ Create own mood entries (patient_id = session['user_id'])
- ✅ View own mood history
- ✅ View own today's mood
- ✅ Create, update, delete own reminders
- ✅ Access own activity logs and memory data

**Patient CANNOT:**
- ❌ View another patient's mood
- ❌ View another patient's reminders
- ❌ Modify another patient's data
- ❌ Access caregiver dashboard
- ❌ Create mood entries for other patients
- ❌ Call /api/mood/stats endpoint

**Implementation:**
```python
@mood_bp.route('/entries', methods=['POST'])
def create_mood_entry():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # patient_id ALWAYS = user_id (from session, never from client)
    patient_id = user_id
    
    data = request.get_json()
    mood_entry = MoodEntry(patient_id=patient_id, mood=data['mood'], note=data.get('note'))
    db.session.add(mood_entry)
    db.session.commit()
    return jsonify(mood_entry.to_dict()), 201
```

### 10.3 Caregiver (role='caregiver') Authorization

**Caregiver CAN (Phase 10D):**
- ✅ View patient's latest mood (today's mood)
- ✅ View patient's mood history
- ✅ View patient's mood statistics (factual only: distribution, trend)
- ✅ View patient's reminders (existing)
- ✅ Manage patient reminders (existing)
- ✅ View patient activity logs (existing)
- ✅ View patient memory data (existing)
- ✅ Access caregiver dashboard

**Caregiver CANNOT:**
- ❌ Create mood entries for patients (patients record own moods)
- ❌ Edit mood entries
- ❌ Delete mood entries
- ❌ Access another caregiver's data
- ❌ Create diagnostic/medical assessments
- ❌ Generate clinical recommendations

**Implementation:**
```python
@mood_bp.route('/stats', methods=['GET'])
def get_mood_stats():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_id)
    if user.role != 'caregiver':
        return jsonify({'error': 'Forbidden'}), 403
    
    patient_id = request.args.get('patient_id', type=int)
    # ... return factual mood statistics only
    return jsonify({'mood_distribution': {...}})
```

### 10.4 Patient ID Validation

**CRITICAL RULE: Never Trust Client-Supplied patient_id**

**Pattern:**
1. Get user_id from session['user_id']
2. Get patient_id from request (query param or body)
3. ALWAYS validate:
   - If patient: patient_id must equal user_id
   - If caregiver: patient_id check depends on caregiver-patient mapping (TBD in later phase)
4. Return 403 Forbidden if validation fails

**Example:**
```python
# Patient requesting own mood history
def get_mood_history():
    user_id = session.get('user_id')
    patient_id = request.args.get('patient_id', type=int)
    
    # Validate: patient can only view own
    if patient_id != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    
    # Proceed with query
    entries = MoodEntry.query.filter_by(patient_id=patient_id).all()
    return jsonify([e.to_dict() for e in entries])
```

### 10.5 Input Validation

**Mood Creation Validation:**
- mood: must be exactly one of ["very_happy", "happy", "okay", "sad", "very_sad"]
- note (optional): max 500 characters
- HTML escape note text before display (prevent XSS)
- timestamp: validated server-side (must be within last 30 days)

**Reminder Operations (Existing - No Changes):**
- type: must be in ["medicine", "appointment", "activity"]
- time: valid "HH:MM" format
- title: max 255 characters

### 10.6 Data Privacy Notes

**Mood Data Considerations:**
- Mood is recorded as factual information, not medical assessment
- Caregivers see factual mood values (very_happy, happy, okay, sad, very_sad)
- No clinical interpretation or diagnosis
- No automatic alerts or recommendations
- Patient owns mood data and can view own mood history

---

## 11. TESTING STRATEGY

### 11.1 Test Scope

**Testing will focus on:**
- Phase 10D mood functionality (new)
- Reminder functionality (existing, verify no regression)
- Voice assistant (existing intents + new mood intent)
- i18n (new mood keys)
- Database (mood_entries table creation)
- Security/authorization (patient isolation, caregiver access)
- Integration tests (end-to-end workflows)

**The final test count will reflect the actual tests implemented for the Phase 10D functionality.**

**DO NOT create unnecessary tests just to reach a target number.**

### 11.2 Test Categories

**1. Authentication & Authorization (Estimated 5-8 tests)**
- [ ] test_mood_requires_login
- [ ] test_mood_patient_can_create_own
- [ ] test_mood_patient_cannot_create_for_other
- [ ] test_mood_caregiver_can_view_stats
- [ ] test_mood_caregiver_cannot_write
- [ ] test_patient_cannot_access_stats
- [ ] test_authorization_header_missing_401
- [ ] test_session_expired_401

**2. Mood Creation (Estimated 6-8 tests)**
- [ ] test_create_mood_very_happy
- [ ] test_create_mood_all_five_values
- [ ] test_create_mood_with_note
- [ ] test_create_mood_invalid_value_400
- [ ] test_create_mood_missing_mood_field_400
- [ ] test_create_mood_note_too_long_400
- [ ] test_create_mood_stores_timestamp
- [ ] test_create_mood_stores_patient_id_from_session

**3. Mood History Queries (Estimated 4-6 tests)**
- [ ] test_get_today_mood_exists
- [ ] test_get_today_mood_not_exists
- [ ] test_get_mood_history_list
- [ ] test_get_mood_history_pagination_limit
- [ ] test_get_mood_history_pagination_offset
- [ ] test_get_mood_history_ordered_descending

**4. Mood Statistics (Estimated 3-5 tests)**
- [ ] test_get_mood_stats_caregiver_only
- [ ] test_get_mood_stats_distribution
- [ ] test_get_mood_stats_time_period
- [ ] test_get_mood_stats_recent_entry
- [ ] test_mood_stats_no_medical_interpretation

**5. Patient Isolation (Estimated 4-5 tests)**
- [ ] test_patient_only_sees_own_mood
- [ ] test_patient_cannot_see_other_patient_mood
- [ ] test_patient_cannot_edit_other_mood
- [ ] test_patient_isolation_across_endpoints
- [ ] test_caregiver_can_see_all_patients

**6. Database & Model (Estimated 3-4 tests)**
- [ ] test_mood_entry_model_creation
- [ ] test_mood_entry_relationships
- [ ] test_mood_entry_to_dict()
- [ ] test_mood_table_created_automatically

**7. Voice Integration (Estimated 3-4 tests)**
- [ ] test_voice_detects_mood_query
- [ ] test_voice_mood_response_speaks
- [ ] test_voice_mood_no_entry_fallback
- [ ] test_voice_mood_error_handling

**8. i18n Consistency (Estimated 2-3 tests)**
- [ ] test_all_mood_keys_in_en
- [ ] test_all_mood_keys_in_as
- [ ] test_mood_keys_synchronized_en_as

**9. UI/Frontend (Estimated 2-3 tests)**
- [ ] test_mood_page_loads_for_patient
- [ ] test_mood_page_requires_login
- [ ] test_mood_buttons_functional

**10. Integration & End-to-End (Estimated 3-5 tests)**
- [ ] test_patient_records_mood_and_views_history
- [ ] test_patient_records_mood_with_note
- [ ] test_mood_reflected_on_caregiver_dashboard
- [ ] test_voice_query_mood_after_recording
- [ ] test_multiple_moods_same_day_timestamps

**ESTIMATED TOTAL: 35-55 tests** (actual count will depend on implementation)

### 11.3 Regression Testing

**Critical: Verify All Existing Functionality Still Works**

**Phase 10A Tests (Memory Foundation):**
- Run: `pytest test_phase10a_memory.py -v`
- All 35+ tests must pass
- MemoryPerson, MemoryPlace, MemoryItem still work

**Phase 10B Tests (Memory Games):**
- Run: `pytest test_phase10b_memory_games.py -v`
- All 30+ tests must pass
- Photo/name match games functional
- Who is this game functional

**Phase 10C Tests (Memory Rescue):**
- Run: `pytest test_phase10c_memory_assistance.py -v`
- All 26+ tests must pass
- Voice memory query still works

**Phase 7 Tests (Voice Assistant):**
- Run: `pytest test_phase7_voice.py -v`
- All voice intent tests must pass
- Time, date, reminder, greeting, memory queries work
- New mood intent doesn't break existing intents

**Reminder Tests:**
- CRUD operations still work (existing tests)
- Reminders API fully functional

**I18n Tests:**
- All keys in en.json accessible
- All keys in as.json accessible
- No missing translations

**Final Verification Command:**
```bash
pytest test_phase10a_memory.py test_phase10b_memory_games.py test_phase10c_memory_assistance.py test_phase7_voice.py -v --tb=short
```

**Expected Result:** All existing tests pass + new Phase 10D tests pass = comprehensive coverage

---

## 11. FILES TO CREATE/MODIFY

### 11.1 FILES TO CREATE (4 new)

#### 1. models/models.py → Add MoodEntry class
- Location: After MemoryItem class
- Lines: ~60 lines
- Content: MoodEntry model with all fields, relationships, methods
- Impact: No changes to existing models

#### 2. routes/mood.py (NEW FILE)
- Size: ~150 lines
- Purpose: All mood-related API endpoints
- Content:
  - Import statements
  - Authorization helper (reuse check_memory_authorization or create mood_check_auth)
  - POST /api/mood/entries
  - GET /api/mood/today
  - GET /api/mood/history
  - GET /api/mood/stats (with caregiver check)
- No breaking changes to other routes

#### 3. templates/mood.html (NEW FILE)
- Size: ~200 lines
- Purpose: Patient mood recording UI
- Content:
  - Welcome section
  - 5 emoji mood buttons
  - Optional note textarea
  - Recent history display
  - Navigation
- Extends base.html
- Uses data-i18n-key for translations

#### 4. static/js/mood.js (NEW FILE)
- Size: ~300 lines
- Purpose: Mood page state management and API
- Content:
  - MoodState object
  - initMoodPage()
  - handleMoodSelect(mood)
  - submitMood()
  - loadMoodHistory()
  - displayTodaysMood()
  - Error handling

### 11.2 FILES TO MODIFY (8 existing)

#### 1. models/models.py
- **What:** Add MoodEntry class and relationship to User
- **Where:** After MemoryItem class definition (~line 240)
- **Lines:** Add ~60 lines
- **Change Type:** ADDITION (no deletion, no breaking changes)
- **Why:** Define mood data model

#### 2. app.py
- **What:** Import and register mood blueprint
- **Where:** With other blueprint imports (~line 10-15)
- **Lines:** Add 2 lines
- **Change Type:** ADDITION
  ```python
  from routes.mood import mood_bp
  app.register_blueprint(mood_bp)
  ```
- **Why:** Register new mood API route handler

#### 3. routes/users.py
- **What:** Add /mood route
- **Where:** After @users_bp.route('/memory-rescue') (~line 100)
- **Lines:** Add ~8 lines
- **Change Type:** ADDITION
  ```python
  @users_bp.route('/mood')
  @login_required
  def mood():
      user_id = session.get('user_id')
      user = User.query.get(user_id)
      return render_template('mood.html', user=user)
  ```
- **Why:** Patient can navigate to mood page

#### 4. templates/patient_home.html
- **What:** Add Mood section with button
- **Where:** After Memory section (~line 60)
- **Lines:** Add ~12 lines
- **Change Type:** ADDITION
  ```html
  <div class="placeholder-section">
      <h2>🎭 Mood Tracker</h2>
      <p data-i18n-key="mood_section_subtitle">...</p>
      <a href="{{ url_for('users.mood') }}" class="btn btn-secondary">...</a>
  </div>
  ```
- **Why:** Navigate to mood page from home

#### 5. templates/caregiver_dashboard.html
- **What:** Add mood overview section
- **Where:** In patient overview stats (after avg_accuracy stat card, ~line 30)
- **Lines:** Add ~10 lines
- **Change Type:** ADDITION
  ```html
  <div class="stat-card">
      <span class="stat-label" data-i18n-key="stat_current_mood">Current Mood</span>
      <span class="stat-value" id="overview-mood">-</span>
  </div>
  ```
- **Why:** Caregivers see patient mood overview

#### 6. static/js/voice_assistant.js
- **What:** Add mood query detection and handling
- **Where:** In processVoiceQuery() decision tree (~line 150-160)
- **Lines:** Add ~50 lines
- **Change Type:** ADDITION
  - Add mood intent check (after memory queries)
  - Add getMoodLabel() helper function
  - Add handleMoodQuery() function
- **Why:** Support voice mood queries (read-only)

#### 7. static/i18n/en.json
- **What:** Add 30 mood-related translation keys
- **Where:** After memory_rescue keys (~line 200)
- **Lines:** Add ~40 lines (keys + values)
- **Change Type:** ADDITION
  - No modification of existing keys
  - Just add new keys at end of object (before closing })
- **Why:** Support English mood UI text

#### 8. static/i18n/as.json
- **What:** Add 30 mood-related translation keys (Assamese)
- **Where:** After memory_rescue keys (~line 200)
- **Lines:** Add ~40 lines
- **Change Type:** ADDITION
  - Parallel structure to en.json
  - Assamese translations
- **Why:** Support Assamese mood UI text

### 11.3 FILES THAT MUST NOT CHANGE

**These files MUST remain UNTOUCHED:**
- static/js/reminders.js (existing reminder logic)
- routes/reminders.py (existing reminder endpoints)
- models/models.py Reminder class (existing reminder model)
- config.py (database config)
- requirements.txt (no new dependencies)

---

## 12. DEPENDENCIES

### 12.1 Python Dependencies

**Current requirements.txt (NO NEW PACKAGES):**
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Werkzeug==3.0.1
... (others unchanged)
```

**Phase 10D:** ZERO new Python packages required

**Why:**
- SQLAlchemy handles ORM (no new ORM needed)
- Flask handles routing (no new web framework)
- No mood analysis libraries (deterministic only)
- No external APIs (browser-native voice)

### 12.2 JavaScript Dependencies

**Current static/js (NO NEW PACKAGES):**
- voice_assistant.js (browser Web Speech API)
- reminders.js (no external libs)
- dashboard_chart.js (Chart.js already included in caregiver_dashboard.html)
- i18n.js (custom implementation)

**Phase 10D:** ZERO new JavaScript packages required

**Why:**
- HTML5 buttons/inputs sufficient for mood UI
- Web Speech API for voice (browser native)
- Chart.js already used (if mood chart added later)
- No frontend framework required

### 12.3 Browser Requirements

**Minimum Versions:**
- Chrome 60+ (Web Speech API)
- Firefox 25+ (Web Speech API)
- Safari 14.1+ (Web Speech API)
- Edge 79+ (Web Speech API)
- Mobile browsers (iOS Safari 14.5+, Android Chrome 60+)

**No New Requirements for Phase 10D**

---

## 13. IMPLEMENTATION ORDER

### Phase 10D Implementation Sequence (Recommended)

**Step 1: Backend Model & DB (1-2 hours)**
1. Add MoodEntry class to models/models.py
2. Test model creation (pytest fixture)
3. Verify mood_entries table will be created

**Step 2: API Endpoints (2-3 hours)**
1. Create routes/mood.py with all 4 endpoints
2. Implement authorization checks
3. Test each endpoint with pytest (authentication, validation, isolation)

**Step 3: I18n Setup (0.5 hours)**
1. Add 30 keys to en.json
2. Add 30 keys to as.json
3. Verify key consistency between files

**Step 4: Frontend - Mood Page (2-3 hours)**
1. Create templates/mood.html
2. Create static/js/mood.js
3. Test button clicks, form submission, API integration

**Step 5: Navigation & Integration (1 hour)**
1. Add /mood route to users.py
2. Add mood section to patient_home.html
3. Add mood card to caregiver_dashboard.html

**Step 6: Voice Integration (1-2 hours)**
1. Extend voice_assistant.js with mood queries
2. Implement handleMoodQuery() and getMoodLabel()
3. Test voice commands

**Step 7: Testing (3-4 hours)**
1. Write 25 mood endpoint tests
2. Write 8 reminder regression tests
3. Write 6 voice integration tests
4. Write 4 i18n tests
5. Run full suite: verify 30 Phase 10B tests still pass, Phase 10C tests still pass

**Step 8: Documentation & Cleanup (1 hour)**
1. Update README with mood feature
2. Add deployment notes
3. Create PHASE_10D_COMPLETE.md
4. Clean up console logs

**Total Estimated Time: 12-18 hours**

---

## 14. RISKS & EDGE CASES

### 14.1 Identified Risks

| Risk | Likelihood | Severity | Mitigation |
|------|-----------|----------|-----------|
| Database migration failure | Low | High | Backup before deploy, test in dev |
| Patient timezone confusion | Medium | Medium | Always store UTC, convert on display |
| Multiple moods in one day | Medium | Low | Allow; use latest for "today" |
| Caregiver sees sensitive mood data | Low | High | Document: mood is not mental health diagnosis |
| Voice mood commands misheard | Medium | Low | Voice is read-only, no accidental changes |
| Missing i18n keys | Low | Medium | Script to validate key consistency |
| Mood dropdown too small for elderly | Low | Medium | Buttons not dropdown; large touch targets |

### 14.2 Edge Cases

**Edge Case 1: Patient Records Mood After Midnight**
- **Scenario:** Patient records mood at 11:58 PM, then again at 12:02 AM
- **Expected:** Two separate daily entries (not one "today")
- **Implementation:** timestamp filters by date range, not day-of-week

**Edge Case 2: Caregiver Views Patient Without Permission**
- **Scenario:** Caregiver tries to fetch /api/mood/stats?patient_id=999
- **Expected:** 403 Forbidden (no patient mapping yet)
- **Implementation:** Check user role and patient relationship (Phase 10E)

**Edge Case 3: Patient Deletes Note After Saving**
- **Scenario:** Patient saves mood with note, then wants to remove note
- **Expected:** Edit endpoint (not yet planned for Phase 10D)
- **Implementation:** PUT /api/mood/entries/{id} for Phase 10E

**Edge Case 4: Voice Mishears "Mood" as "Move" or "Mute"**
- **Scenario:** User says something unclear, voice thinks it's mood query
- **Expected:** Safe fallback to no-op or help message
- **Implementation:** Voice query detection uses exact keyword match, not fuzzy

**Edge Case 5: Patient Records Mood at 3 AM (Insomnia)**
- **Scenario:** Mood timestamp is 3:00 AM, displayed as "today" or "yesterday"?
- **Expected:** 3:00 AM is still "today" until 11:59 PM
- **Implementation:** Use date-only comparison, not full 24-hour window

---

## 15. EXPECTED USER WORKFLOWS

### 15.1 Patient Workflow: Record & View Mood

```
1. Patient logs in
2. See patient_home.html with "🎭 Mood Tracker" section
3. Click "Check Your Mood" button
4. Navigate to /mood page
5. See 5 large emoji buttons
6. Click preferred mood (e.g., 😊 Very Happy)
7. Optional: Add text note ("Had lunch with family")
8. See confirmation: "Your mood has been saved"
9. See recent mood history (last 7 days)
10. Each past mood shows date + mood emoji
11. Click "Back to Home" or "View More History"
```

### 15.2 Caregiver Workflow: Monitor Mood

```
1. Caregiver logs in
2. Navigate to /caregiver-dashboard
3. Select patient from dropdown
4. See patient overview with "Current Mood" stat
5. See mood emoji (e.g., 🙂 Happy)
6. See "Last Recorded: Today at 2:30 PM"
7. Optional: Click for mood trend/history (Phase 10E)
8. Caregiver notes patient mood in their own workflow
```

### 15.3 Voice Workflow: Query Mood

```
1. Patient on any page with voice assistant
2. Click "Ask Memora" button
3. Say: "How am I feeling?" or "What's my mood?"
4. Memora speaks: "Your mood today is very happy, recorded at 2:30 PM"
5. If no mood recorded: "You haven't recorded your mood yet"
```

### 15.4 Caregiver Reminder Workflow (Existing, Unchanged)

```
1. Caregiver on dashboard
2. See reminder management section (existing)
3. Add new reminder: title, type, time
4. Patient sees on home page under "Today's Reminders"
5. Patient clicks "Mark Done"
6. Caregiver sees updated reminder status
```

---

## 12. EXACT FILES TO CREATE (4 Files)

### 12.1 File: routes/mood.py (NEW FILE)
**Location:** `c:\Users\chala\Memora\routes\mood.py`
**Purpose:** RESTful API for mood recording, retrieval, and statistics  
**Estimated Size:** 250-300 lines

### 12.2 File: templates/mood.html (NEW FILE)
**Location:** `c:\Users\chala\Memora\templates\mood.html`
**Purpose:** Patient mood recording and history page  
**Estimated Size:** 220-280 lines

### 12.3 File: static/js/mood.js (NEW FILE)
**Location:** `c:\Users\chala\Memora\static\js\mood.js`
**Purpose:** Mood page state management and API calls  
**Estimated Size:** 350-420 lines

### 12.4 File: test_phase10d_mood.py (NEW FILE)
**Location:** `c:\Users\chala\Memora\test_phase10d_mood.py`
**Purpose:** Comprehensive test suite for Phase 10D mood functionality  
**Estimated Size:** 500-650 lines

---

## 13. EXACT FILES TO MODIFY (8 Files)

### 13.1 models/models.py (MODIFIED)
**What:** Add MoodEntry model class
**Where:** After MemoryItem class (around line 250)
**Lines to Add:** ~30 lines

### 13.2 app.py (MODIFIED)
**What:** Register mood blueprint
**Where:** In blueprint registration section (around line 26-31)
**Lines to Change:** 2 lines total (1 import + 1 registration)

### 13.3 routes/users.py (MODIFIED)
**What:** Add /mood route
**Where:** After existing routes (around line 80)
**Lines to Add:** 8-10 lines

### 13.4 templates/patient_home.html (MODIFIED)
**What:** Add Mood Tracker section
**Where:** After Memory section
**Lines to Add:** 6-8 lines

### 13.5 templates/caregiver_dashboard.html (MODIFIED)
**What:** Add mood overview to patient stats section
**Where:** In patient overview stats section (after accuracy stat)
**Lines to Add:** 8-10 lines

### 13.6 static/i18n/en.json (MODIFIED)
**What:** Add 30 mood translation keys
**Where:** After existing memory_rescue keys
**Lines to Add:** ~40 lines

### 13.7 static/i18n/as.json (MODIFIED)
**What:** Add 30 mood translation keys (Assamese)
**Where:** After existing memory_rescue keys
**Lines to Add:** ~40 lines

### 13.8 static/js/voice_assistant.js (MODIFIED)
**What:** Extend voice system with mood query support
**Where:** In processVoiceQuery() function
**Lines to Add:** ~45-50 lines

---

## 14. DEPENDENCIES

**New Python Packages Required:** ZERO (0)
**New JavaScript Libraries:** ZERO (0)
**New Database Drivers:** ZERO (0)
**Build Tools Changes:** ZERO (0)

All Phase 10D functionality uses existing Flask, SQLAlchemy, and browser APIs.

---

## 15. IMPLEMENTATION ORDER (8 Steps)

**Sequential Implementation (Estimated 14-22 hours):**

1. **Step 1: Database Model** (1-2 hours) — Add MoodEntry to models/models.py
2. **Step 2: API Routes** (2-3 hours) — Create routes/mood.py with 4 endpoints
3. **Step 3: Internationalization** (1-2 hours) — Add 30 keys to en.json and as.json
4. **Step 4: Frontend Page** (2-3 hours) — Create mood.html and add /mood route
5. **Step 5: Frontend JavaScript** (2-3 hours) — Create mood.js with state management
6. **Step 6: Dashboard Integration** (1-2 hours) — Update caregiver dashboard
7. **Step 7: Voice Integration** (1-2 hours) — Extend voice_assistant.js with mood queries
8. **Step 8: Comprehensive Testing** (3-4 hours) — Create test suite, run regression tests

---

## 16. RISKS & EDGE CASES

### 16.1 Technical Risks (7 Risks)

| Risk | Mitigation |
|------|-----------|
| SQLAlchemy table creation timing | Always call db.create_all() in app_context() |
| Patient ID override via client | ALWAYS use session['user_id'], never trust client |
| Invalid mood value stored | Validate mood in POST: must be one of 5 values |
| Timestamp precision for sorting | Use db.DateTime with microseconds, server-side timestamp |
| Unbounded note field size | Validate max 500 chars on client + server |
| Voice query performance | Index patient_id and timestamp in mood_entries table |
| i18n key mismatch between en/as | Script to compare keys before deployment |

### 16.2 Edge Cases (5 Edge Cases)

| Edge Case | Expected Behavior | Test |
|-----------|------------------|------|
| Multiple moods same day | Both stored, ordered by timestamp | test_multiple_moods_per_day |
| Caregiver requests non-assigned patient (Phase 10E) | 403 Forbidden | Placeholder for Phase 10E |
| No mood recorded, voice query | Graceful message | test_voice_mood_no_entry_fallback |
| Network failure during submit | Error shown, allow retry | Manual browser test |
| Old browser without Fetch API | Graceful degradation | Note in risk log |

---

## 17. SCOPE BOUNDARIES

### 17.1 INCLUDED in Phase 10D (✅)
- Record mood as 5 values (very_happy, happy, okay, sad, very_sad)
- View mood history (7-14 days)
- Voice mood queries (read-only)
- Caregiver sees patient's latest mood on dashboard
- 30 i18n keys (EN + AS)

### 17.2 EXCLUDED from Phase 10D (❌ Deferred)
- Medical diagnosis or clinical interpretation
- Automated alerts based on mood
- Caregiver can write mood entries
- Mood calendar/heatmap visualization
- Voice command to record mood ("I'm happy")
- Tamil translations (Phase 10E)
- Advanced analytics/trends

---

## 18. EXPECTED PATIENT WORKFLOW

**Daily Mood Check-In:**
1. Patient logs in, sees home page
2. Clicks "Check Your Mood" button (under Mood Tracker section)
3. Navigates to /mood page
4. Sees 5 large emoji buttons
5. Clicks one (e.g., 🙂 Happy)
6. Optional: adds note ("Had lunch with family")
7. Clicks "Save Mood"
8. Sees success message + timestamp
9. Views mood history (last 7 days as cards)

**Voice Query:**
1. Patient says: "What's my mood?"
2. Voice responds: "Your mood today is happy, recorded at 2:30 PM"
3. If no mood: "You haven't recorded your mood yet"

---

## 19. EXPECTED CAREGIVER WORKFLOW

**Dashboard Monitoring:**
1. Caregiver logs in, navigates to dashboard
2. Selects patient from dropdown
3. Sees "Current Mood" stat: 🙂 Happy
4. Sees "Last Recorded": Today at 2:30 PM
5. Quick glance at patient well-being

**Detailed Mood Review (Phase 10E, NOT Phase 10D):**
- Full mood history access deferred
- Mood statistics deferred
- Trend analysis deferred

---

## 20. REGRESSION TESTING STRATEGY

**Before Implementation, Run Baseline:**
```bash
pytest test_phase10a_memory.py test_phase10b_memory_games.py test_phase10c_memory_assistance.py test_phase7_voice.py -v
```

**After Implementation, Run Full Suite:**
```bash
pytest test_phase10a_memory.py test_phase10b_memory_games.py test_phase10c_memory_assistance.py test_phase7_voice.py test_phase10d_mood.py -v
```

**Critical Regression Tests:**
- test_patient_home_still_loads
- test_caregiver_dashboard_loads
- test_voice_time_query_still_works
- test_voice_date_query_still_works
- test_voice_reminder_query_still_works
- test_voice_memory_query_still_works
- test_reminders_crud_still_works
- test_user_table_unchanged
- test_no_data_loss_after_migration

**Final Sign-Off Checklist:**
- [ ] All 35-55 Phase 10D tests pass
- [ ] All Phase 10A/B/C tests pass (regression)
- [ ] All Phase 7 voice tests pass (regression)
- [ ] mood_entries table created automatically
- [ ] Patient home displays Mood Tracker section
- [ ] Patient can record and view mood
- [ ] Caregiver dashboard displays mood overview
- [ ] Voice responds to "What's my mood?" correctly
- [ ] i18n keys present in en.json and as.json
- [ ] No console errors in browser DevTools

---

## SUMMARY

**Phase 10D Implementation Plan** provides:
- ✅ Complete database schema (MoodEntry model)
- ✅ 4 RESTful API endpoints
- ✅ Patient UI for mood recording and history
- ✅ Caregiver dashboard integration
- ✅ Voice assistant extension for mood queries
- ✅ 30 internationalization keys (EN + AS)
- ✅ 35-55 comprehensive tests
- ✅ Security & authorization patterns
- ✅ Regression testing strategy
- ✅ Scope boundaries (what's in/out)
- ✅ Implementation order (8 sequential steps)
- ✅ Risk mitigation strategies
- ✅ Zero new dependencies

---

**PHASE 10D PLAN STATUS: READY FOR IMPLEMENTATION REVIEW**

All 20 plan sections are complete with detailed specifications for:
- Database schema and API design
- Frontend UI/UX for patients and caregivers
- Voice assistant integration
- Internationalization strategy
- Security model and authorization
- Testing approach with regression validation
- Implementation roadmap
- Risk assessment and edge case handling
- Scope boundaries and future phases

**Implementation can proceed once this plan receives approval.**
