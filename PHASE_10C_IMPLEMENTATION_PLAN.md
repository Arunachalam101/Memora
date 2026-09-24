# PHASE 10C IMPLEMENTATION PLAN
## Memory Assistance & AI Voice Companion

**Date:** 2026-09-23  
**Status:** PLAN ONLY - Awaiting Approval  
**Scope:** Memory Rescue + Memory Lookup + AI Voice Companion

---

## A. CURRENT ARCHITECTURE FINDINGS

### A1. Memory Foundation (Phase 10A)

**Models:**
- `MemoryPerson`: id, patient_id, name, relationship, description, photo, is_active
- `MemoryPlace`: id, patient_id, name, description, photo, is_active
- `MemoryItem`: id, patient_id, title, description, photo, memory_date, is_active

**APIs Available:**
```
GET    /api/memory/people?patient_id=<id>     → List people (filtered by is_active)
POST   /api/memory/people                      → Create person
PUT    /api/memory/people/<id>                 → Update person
DELETE /api/memory/people/<id>                 → Delete person

GET    /api/memory/places?patient_id=<id>     → List places
POST   /api/memory/places                      → Create place
PUT    /api/memory/places/<id>                 → Update place
DELETE /api/memory/places/<id>                 → Delete place

GET    /api/memory/memories?patient_id=<id>   → List memories
POST   /api/memory/memories                    → Create memory
PUT    /api/memory/memories/<id>               → Update memory
DELETE /api/memory/memories/<id>               → Delete memory
```

**Authorization Model:**
- `check_memory_authorization(patient_id, can_edit=False)` enforces:
  - Patients can view own data only (patient_id == user_id from session)
  - Caregivers can access any patient's data
  - Session-based user_id (server-side, not client-supplied)

**Serialization:**
- Each model has `.to_dict()` method returning JSON-compatible dict

**Patient Isolation:**
- Enforced at backend via authorization checks
- Query parameters are validated against session user
- All queries filter by patient_id and is_active=True

### A2. Existing Voice Assistant (Phase 7)

**Technology:**
- Web Speech API (browser built-in, no external dependencies)
- SpeechRecognition: speech-to-text (Chrome, Edge, Safari)
- SpeechSynthesis: text-to-speech (all modern browsers)

**Current Capabilities:**
- Time queries ("What's the time?")
- Date queries ("What's today's date?")
- Reminder queries ("What's my next reminder?")
- Greetings ("Hello", "Hi there")
- Rule-based intent matching (string.includes())

**Architecture:**
- `VoiceAssistant` object manages state (isListening, isSpeaking, recognition)
- `speak(text)` → returns Promise, speaks text and updates UI
- `listenForQuery()` → starts speech recognition, calls `processVoiceQuery()`
- `processVoiceQuery(query)` → rule-based matching, calls appropriate handler
- UI state updates reflect listening/speaking state
- Error handling for: no-speech, unsupported browsers, API failures

**Limitations:**
- Rule-based only (no NLP, no semantics)
- Only handles reminders from ActivityLog
- No patient memory data integration
- No backend processing (client-side only)
- Only English language support currently

**Integration Points:**
- Loaded in `templates/patient_home.html`
- Uses global `USER_ID` variable (injected from template)
- Fetches `/api/reminders/{USER_ID}` for reminder data
- Responds via speak() function

### A3. AI Infrastructure

**Current Status:**
- NO LLM integration exists
- NO external AI provider configured
- NO API keys defined in config.py or environment
- Only rule-based adaptive difficulty system in `ai/adaptive_difficulty.py`

**Dependencies:**
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
```
No NLP, ML, or AI packages installed.

**Configuration:**
- `config.py` has only SECRET_KEY and database URI
- No environment variable setup for AI provider credentials

### A4. i18n System

**Languages Supported:**
- English (en) → static/i18n/en.json
- Assamese (as) → static/i18n/as.json
- Tamil belongs to Phase 10E

**Architecture:**
- `i18n.js` loads language JSON files dynamically
- Elements use `data-i18n-key` attributes
- `applyTranslations()` replaces text content
- Language choice persisted to localStorage
- User.preferred_language column stores user preference

**Key Names:**
- Kebab-case convention: `game_photo_name_match_title`
- Keys grouped by feature

### A5. Authentication & Session

**Model:**
- User: id, name, pin, role (patient/caregiver), preferred_language
- Session stores: user_id, user_name, user_role
- @login_required decorator enforces authentication

**API Authorization Pattern:**
- Routes check `session.get('user_id')`
- Reject if not authenticated (return 401)
- Patient ID from request validated against session user_id
- Cross-patient access returns 403 Forbidden

### A6. Existing Pages & Routes

**Patient Pages:**
- `/` → redirects to patient-home or login
- `/login` → login page
- `/patient-home` → patient dashboard
- `/games` → games hub
- `/memory-album` → Memory Album (Phase 10A)

**Caregiver Pages:**
- `/caregiver-dashboard` → progress tracking

**Game Routes:**
- `/game/memory-match`
- `/game/attention-test`
- `/game/photo-name-match` (Phase 10B)
- `/game/who-is-this` (Phase 10B)

---

## B. PROPOSED ARCHITECTURE

### B1. Phase 10C Features

```
Patient Home
    ↓
Memory Rescue (new page)
    ├── View People (with photos, names, relationships, descriptions)
    ├── View Places (with photos, names, descriptions)
    └── View Memories (with photos, titles, descriptions, dates)
    ↓
Memory Search / Lookup (new API endpoint)
    ├── Search patient's people by name/keyword
    ├── Search patient's places by name/keyword
    └── Search patient's memories by title/keyword
    ↓
AI Voice Companion (enhanced voice assistant)
    ├── Listens to patient questions via Web Speech API
    ├── Retrieves relevant memory records via backend lookup
    ├── Generates contextual response (deterministic + optional AI)
    ├── Speaks response via SpeechSynthesis
    └── Falls back to text if voice unavailable
```

### B2. Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Patient Session                                             │
│ (session.user_id from backend, authenticated)              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Memory Rescue Page                                          │
│ (View-only interface, large text, large buttons)           │
│ - Displays People Tab                                       │
│ - Displays Places Tab                                       │
│ - Displays Memories Tab                                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Frontend JavaScript (memory_rescue.js)                      │
│ - Calls /api/memory/people?patient_id=USER_ID              │
│ - Calls /api/memory/places?patient_id=USER_ID              │
│ - Calls /api/memory/memories?patient_id=USER_ID            │
│ - Displays formatted cards with photos/text                │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Backend Authorization                                       │
│ - check_memory_authorization(patient_id=USER_ID)           │
│ - Verify session user_id matches requested patient_id      │
│ - Return patient's memory records (filtered by is_active)   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ AI Voice Companion (new)                                    │
│ - Mic button to start listening                            │
│ - Web Speech API captures user question                    │
│ - Question sent to /api/memory/search                      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Memory Search Engine (new backend)                          │
│ - Receive: user_id (from session), query text              │
│ - Search patient's MemoryPerson/Place/Item by name/title   │
│ - Return: matched records + metadata                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Response Generation (new)                                   │
│ - Option A: Deterministic templates (no AI)                │
│ - Option B: Optional LLM (configurable, Phase 10C final)   │
│ - Always ground in patient's actual memory data            │
│ - Never invent facts                                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Text Response                                               │
│ - Displayed to patient                                      │
│ - Spoken via SpeechSynthesis                               │
│ - Falls back to text-only if speech unavailable            │
└─────────────────────────────────────────────────────────────┘
```

### B3. Patient Isolation Model

**Frontend:**
- USER_ID injected into page via template: `const USER_ID = {{ session.get('user_id') }}`
- Frontend sends USER_ID as query parameter
- Frontend cannot change session user_id

**Backend:**
- Retrieve authenticated user_id from session: `user_id = session.get('user_id')`
- Validate query parameter matches session user_id
- Return 403 Forbidden if mismatch
- Query database only for patient_id == session user_id

**API Signature:**
```python
@app.route('/api/memory/search', methods=['POST'])
def search_memory():
    # NEVER use patient_id from request
    user_id = session.get('user_id')  # ← FROM SESSION ONLY
    if not user_id:
        return {"error": "Unauthorized"}, 401
    
    query = request.json.get('query', '')
    
    # Search only this patient's records
    results = search_patient_records(user_id, query)
    
    return jsonify(results), 200
```

---

## C. FILES TO CREATE

### C1. Frontend
1. **`templates/memory_rescue.html`** (new page)
   - Three tabs: People, Places, Memories
   - Large readable cards with photos
   - Photo fallback for missing images
   - Simple navigation
   - Mic button for voice companion
   - Text response area for voice/companion answers
   - Empty state messages
   - i18n support
   - View-only interface (no editing)

2. **`static/js/memory_rescue.js`** (new)
   - Load and display memory data from /api/memory/* endpoints
   - Handle empty states
   - Tab switching (People, Places, Memories)
   - Integration point for voice companion
   - Display voice response text
   - Patient isolation enforced by backend (user_id from session)

3. **`static/js/voice_assistant.js`** (modify—extend existing)
   - Add new memory-related intent handler
   - Detect memory companion queries (e.g., "Who is...", "Where is...")
   - Call `/api/memory/search` with normalized query
   - Generate response from search results
   - Speak response via existing SpeechSynthesis
   - Keep existing time/date/reminder handlers unchanged

### C2. Backend
1. **`routes/memory_assistance.py`** (new blueprint)
   - `POST /api/memory/search` → search patient's records by query
     - Frontend sends only: `{"query": "Who is Anil?"}`
     - Backend retrieves user_id from session (NOT from request)
     - Authorization via session user_id

2. **`utils/memory_search.py`** (new utility)
   - `search_patient_memory(user_id, query)` → search patient's records
   - Search across multiple fields:
     - MemoryPerson: name, relationship, description
     - MemoryPlace: name, description
     - MemoryItem: title, description
   - Case-insensitive, partial matching (LIKE queries)
   - Query normalization (strip punctuation, handle "Who is", "Tell me about", etc.)
   - Return: dict with 'people', 'places', 'memories' lists

3. **`utils/response_generator.py`** (new utility)
   - `generate_response(query, search_results)` → text response
   - Deterministic template-based generation (no ML, no LLM)
   - No external API calls or AI provider
   - Examples:
     ```
     Query: "Who is Anil?"
     Match: MemoryPerson with name="Anil Sharma", relationship="Son"
     Response: "Anil Sharma is your son. Lives in Delhi, works in IT."
     ```
   - Handle no-match case:
     ```
     Query: "Who is X?"
     Match: None
     Response: "I don't have that information saved. You can ask your caregiver to add it."
     ```

### C3. Database & Models
- NO database changes needed
- Existing MemoryPerson, MemoryPlace, MemoryItem models sufficient

### C4. Testing
1. **`test_phase10c_memory_assistance.py`** (new)
   - ~200-300 lines
   - Tests for Memory Rescue, Lookup, Voice Companion

---

## D. FILES TO MODIFY

### D1. `app.py`
- Register new `memory_assistance_bp` blueprint

### D2. `routes/users.py`
- Add route for Memory Rescue page: `@users_bp.route('/memory-rescue')`
- Redirect to template with USER_ID injection

### D3. `templates/base.html` or `templates/patient_home.html`
- Add navigation link to Memory Rescue
- Add to patient sidebar/menu

### D4. `static/i18n/en.json`
- Add Phase 10C i18n keys (see section J below)

### D5. `static/i18n/as.json`
- Add Phase 10C i18n keys (Assamese translations)

### D6. `static/js/voice_assistant.js` (extend, NOT replace)
- Add new case in `processVoiceQuery()` for memory-related queries
- Detect memory companion intent: "Who is", "Where is", "Tell me about", etc.
- Add handler: `handleMemoryCompanionQuery(query)`
- Integrate with `/api/memory/search` endpoint
- Reuse existing `speak()` function for text-to-speech
- Reuse existing `updateVoiceUI()` for button state
- Keep existing reminder/time/date handlers completely unchanged
- No breaking changes to existing voice assistant logic

### D7. `config.py`
- Optional: Add AI_ENABLED and AI_PROVIDER environment variables
- Default to deterministic mode (no AI)

---

## E. API ENDPOINTS

### E1. New Endpoints (Phase 10C)

**Memory Search** (PRIMARY NEW ENDPOINT)
```
POST /api/memory/search
Authorization: Session-based (user_id retrieved from session)

Request:
{
    "query": "Who is Anil?"
}

Response:
{
    "query": "Who is Anil?",
    "results": {
        "people": [
            {
                "id": 5,
                "name": "Anil Sharma",
                "relationship": "Son",
                "description": "Lives in Delhi, works in IT",
                "photo": "uploads/p_5.jpg",
                "is_active": true,
                "created_at": "2026-01-15T10:30:00"
            }
        ],
        "places": [],
        "memories": []
    },
    "match_found": true
}
```

**CRITICAL SECURITY NOTE:**
- Backend retrieves `user_id = session.get('user_id')`
- Search is restricted to authenticated user's records only
- Frontend does NOT send patient_id
- No lookup endpoint needed for Phase 10C

### E2. Reused Endpoints
- GET /api/memory/people?patient_id=USER_ID
- GET /api/memory/places?patient_id=USER_ID
- GET /api/memory/memories?patient_id=USER_ID

---

## F. DATABASE CHANGES

**NONE REQUIRED**

Existing models are sufficient:
- MemoryPerson has all needed fields
- MemoryPlace has all needed fields
- MemoryItem has all needed fields
- is_active field already supported
- to_dict() serialization already implemented

---

## G. RESPONSE GENERATION STRATEGY (DETERMINISTIC ONLY)

### Phase 10C Implementation: NO AI, NO LLM, NO API KEYS

**Technology Stack:**
- Web Speech API (browser native)
- Memory Retrieval (SQL LIKE queries)
- Deterministic Response Generation (template-based)
- **NO external AI provider**
- **NO LLM integration**
- **NO API keys**
- **NO additional package dependencies**

**Deterministic Response Generation:**
- Query normalization: strip punctuation, lowercase, handle variations
- Search patient's memory records (name, relationship, description, etc.)
- Generate response from matching records using templates
- Examples:
  ```
  Query: "Who is Anil?" or "who's anil" or "tell me about anil"
  Normalized: "anil"
  Search: MemoryPerson.name LIKE "%anil%" OR .relationship LIKE "%anil%" OR .description LIKE "%anil%"
  Match: Anil Sharma (Son, "Lives in Delhi, works in IT")
  Response: "Anil Sharma is your son. He lives in Delhi, works in IT."
  
  Query: "Where is hospital?" or "hospital" or "my hospital"
  Normalized: "hospital"
  Search: MemoryPlace.name LIKE "%hospital%" OR .description LIKE "%hospital%"
  Match: City Hospital ("Main cardiac center, 10km from home")
  Response: "City Hospital is one of your saved places. Main cardiac center, 10km from home."
  ```

**No LLM Ever for Phase 10C:**
- Do NOT install openai, anthropic, or any AI library
- Do NOT add API keys to config.py
- Do NOT add environment variables for AI providers
- Do NOT modify requirements.txt
- Deterministic templates + keyword matching only

---

## H. SECURITY MODEL

### H1. Patient Isolation (Backend-Enforced)

**Frontend:**
- Does NOT send patient_id to `/api/memory/search`
- Sends only: `{"query": "Who is Anil?"}`
- Cannot manipulate session user_id from client

**Backend (CRITICAL):**
```python
@memory_assistance_bp.route('/search', methods=['POST'])
def search_memory():
    # STEP 1: Get user_id from session (server-side only)
    user_id = session.get('user_id')
    if not user_id:
        return {"error": "Unauthorized"}, 401
    
    # STEP 2: Get query from request (and only the query)
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if not query:
        return {"error": "Query cannot be empty"}, 400
    
    # STEP 3: Search ONLY this user's records (patient_id == session user_id)
    results = search_patient_memory(user_id, query)
    # search_patient_memory() searches across:
    # - MemoryPerson.name, .relationship, .description (LIKE, case-insensitive)
    # - MemoryPlace.name, .description (LIKE, case-insensitive)
    # - MemoryItem.title, .description (LIKE, case-insensitive)
    # ONLY for patient_id == user_id and is_active == True
    
    return jsonify(results), 200
```

**Why This Is Secure:**
- user_id comes from Flask session (signed, server-only)
- Patient cannot send a different user_id in the request
- Query parameter is just a string (no authorization scope)
- Backend enforces `patient_id == session.get('user_id')` at query time
```

### H2. Authorization Checks
- All Memory Rescue API calls use check_memory_authorization()
- Session-based user_id validation
- 401 for unauthenticated requests
- 403 for cross-patient access attempts

### H3. Data Privacy
- Memory data never logged unnecessarily
- API responses contain only requested patient's data
- No memory data in error messages
- File uploads remain scoped to patient

### H4. Voice Data
- Speech Recognition handled client-side (no recording sent)
- Query text sent to backend (normal text, no audio)
- Response generated and sent back
- TTS handled client-side (no voice data stored)

---

## I. VOICE ARCHITECTURE

### I1. Extend Existing Web Speech API (Do Not Replace)

**Existing Implementation (Keep Unchanged):**
- `VoiceAssistant` object with recognition + synthesis
- `speak(text)` → returns Promise, speaks text
- `listenForQuery()` → starts speech recognition
- `processVoiceQuery(query)` → rule-based intent matching
- `updateVoiceUI()` → reflects listening/speaking state
- Error handling for unsupported browsers
- Existing intents: time, date, reminders, greetings

**Phase 10C Extension (Add to Existing processVoiceQuery):**
```javascript
async function processVoiceQuery(query) {
    // EXISTING handlers first (do not break them)
    if (query.includes('time') && !query.includes('reminder')) {
        // ... existing time handler
        return;
    }
    if (query.includes('date') || query.includes('today')) {
        // ... existing date handler
        return;
    }
    if (query.includes('reminder')) {
        // ... existing reminder handler
        return;
    }
    
    // NEW: Memory companion handler
    if (isMemoryCompanionQuery(query)) {
        handleMemoryCompanionQuery(query);
        return;
    }
    
    // Fallback
    await speak('Sorry, I did not understand. ...');
}

function isMemoryCompanionQuery(query) {
    // Detect memory-related keywords
    const keywords = ['who is', "who's", 'where is', 'tell me about', 
                      'describe', 'about', 'how is', 'what about'];
    return keywords.some(kw => query.includes(kw));
}

async function handleMemoryCompanionQuery(query) {
    try {
        // POST to backend search
        const response = await fetch('/api/memory/search', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query})
        });
        
        if (response.status === 401) {
            await speak('Please log in to use the memory assistant.');
            return;
        }
        
        const data = await response.json();
        const responseText = generateMemoryResponse(query, data.results);
        
        // Display text
        displayMemoryResponseText(responseText);
        
        // Speak response (reuse existing speak function)
        await speak(responseText);
    } catch (err) {
        console.error(err);
        const fallback = 'I\'m having trouble responding right now. You can still use your Memory Album.';
        displayMemoryResponseText(fallback);
        await speak(fallback);
    }
}
```

### I2. Error Handling

```javascript
handleMemoryCompanionQuery(query) {
    fetch('/api/memory/search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query})
    })
    .then(r => {
        if (r.status === 401) {
            speak("Please log in to use the memory assistant.");
            return null;
        }
        return r.json();
    })
    .then(data => {
        if (!data) return;
        
        const response = generateResponse(query, data.results);
        displayMemoryResponse(response);
        speak(response);
    })
    .catch(err => {
        console.error(err);
        const fallback = "I'm having trouble responding right now. You can still use your Memory Album.";
        displayMemoryResponse(fallback);
        speak(fallback);
    });
}
```

### I3. Microphone Permission
- Handled by browser (Web Speech API)
- User grants permission first time
- Browser remembers preference
- Graceful degradation if denied

### I4. Text Fallback
- Voice response displayed as text
- If browser lacks SpeechSynthesis, show text only
- Text response always readable on screen

---

## J. i18n KEYS (Phase 10C)

### English (en.json) - 30 new keys

```json
"memory_rescue_title": "Memory Rescue",
"memory_rescue_subtitle": "Ask for help remembering important people, places, and memories",
"memory_rescue_heading": "💡 Memory Rescue",

"people_section_title": "People",
"places_section_title": "Places",
"memories_section_title": "Memories",

"voice_companion_button": "🎤 Ask Memora",
"voice_companion_placeholder": "Speak your question...",
"voice_companion_help": "You can ask things like: Who is Anil? Where is my hospital? Tell me about my birthday.",

"no_people_yet": "No people have been added to your Memory Album yet.",
"no_places_yet": "No places have been added to your Memory Album yet.",
"no_memories_yet": "No personal memories have been added to your Memory Album yet.",

"memory_response_error": "I'm having trouble responding right now. You can still use your Memory Album.",
"memory_response_not_found": "I don't have that information saved yet. You can ask your caregiver to add it to your Memory Album.",
"memory_response_empty_query": "Please ask a question or say a person's name.",

"companion_greeting": "I'm here to help you remember. Ask me about anyone in your Memory Album.",
"companion_suggestion_person": "You can ask me about any of these people:",
"companion_suggestion_place": "You can ask me about any of these places:",
"companion_suggestion_memory": "You can ask me about any of these memories:",

"person_detail_relationship": "Relationship",
"person_detail_description": "About",
"place_detail_description": "About",
"memory_detail_title": "Title",
"memory_detail_date": "Date"
```

### Assamese (as.json) - 30 new keys

```json
"memory_rescue_title": "স্মৃতি সহায়তা",
"memory_rescue_subtitle": "গুরুত্বপূর্ণ লোক, স্থান এবং স্মৃতি মনে রাখতে সাহায্যের জন্য জিজ্ঞাসা করুন",
"memory_rescue_heading": "💡 স্মৃতি সহায়তা",

"people_section_title": "মানুহ",
"places_section_title": "স্থান",
"memories_section_title": "স্মৃতি",

"voice_companion_button": "🎤 মেমোরাক সোধক",
"voice_companion_placeholder": "আপোনাৰ প্রশ্ন কওক...",
"voice_companion_help": "আপুনি সুধিব পাৰে: অনিল কোন? মোৰ হস্পিটাল ক'ত? মোৰ জন্মদিন সম্পর্কে কওক।",

[... etc for all 30 keys in Assamese]
```

---

## K. TESTING PLAN

### File: `test_phase10c_memory_assistance.py`
**Note:** Actual test count will be reported upon implementation, not pre-estimated.

**Test Coverage Areas:**

#### Memory Rescue Page & Display
- Authenticated access to /memory-rescue route
- Unauthenticated redirect to login
- People tab loads and displays active records only
- Places tab loads and displays active records only
- Memories tab loads and displays active records only
- Empty state messages when no records exist
- Photo display with fallback for missing images
- Inactive records are filtered out
- Tab switching works

#### Memory Search API (`POST /api/memory/search`)
- Endpoint requires authentication (401 if not logged in)
- Patient isolation (search only user's own records)
- Case-insensitive search works
- Partial name matching works
- Partial relationship matching works (for people)
- Partial description matching works (for all types)
- Empty query rejection (400)
- Query normalization (\"Who is Anil?\" == \"anil\")
- Multiple word queries (\"Tell me about Anil Sharma\")
- No match returns appropriate message
- Match returns correct record type

#### Deterministic Response Generation
- Template generation for person matches
- Template generation for place matches
- Template generation for memory matches
- Priority ordering (people > places > memories)
- No-match fallback message
- Description field included when available
- No invented information in responses

#### Voice Companion Integration
- Memory companion queries detected (\"Who is\", \"Where is\", etc.)
- Non-memory queries routed to existing handlers
- API call includes only query (no patient_id)
- Response spoken via existing speak() function
- Response text displayed on page
- Error handling for API failures
- Existing voice handlers (time, date, reminders) still work

#### Patient Isolation & Security
- Cross-patient search returns 403 (if query uses wrong patient_id)
- Session-based user_id enforcement
- Frontend cannot supply patient_id in search
- Unauthenticated search blocked

#### Regression Testing
- Memory Album (Phase 10A) still works
- Photo name match game (Phase 10B) still works
- Who is this game (Phase 10B) still works
- Voice assistant time query still works
- Voice assistant date query still works
- Voice assistant reminder query still works
- Existing test suite (Phase 1-10B) passes

---

## L. PHASE 10C SCOPE BOUNDARY

### ✅ INCLUDED in Phase 10C

1. **Memory Rescue Feature**
   - Patient-facing view-only interface
   - Three tabs: People, Places, Memories
   - Large readable text
   - Large click/touch targets
   - Card-based layout with photos
   - Photo fallback for missing images
   - Empty state messages
   - NO editing controls

2. **Memory Search**
   - POST `/api/memory/search` endpoint
   - Search across multiple fields:
     - People: name, relationship, description
     - Places: name, description
     - Memories: title, description
   - Case-insensitive partial matching (LIKE queries)
   - Query normalization (\"Who is Anil?\" == \"anil\")
   - Simple keyword string processing
   - Backend enforced patient isolation

3. **AI Voice Companion (Web Speech + Deterministic)**
   - Extend existing voice_assistant.js
   - Detect memory queries (\"Who is\", \"Where is\", etc.)
   - Call /api/memory/search with query
   - Generate deterministic template responses
   - Speak response via SpeechSynthesis
   - Display text response on page
   - Text fallback if voice unavailable
   - Keep existing voice features (time, date, reminders) working

4. **Patient Isolation & Security**
   - Backend retrieves user_id from session
   - Search restricted to authenticated patient's records
   - Frontend does NOT send patient_id to search endpoint
   - 401 for unauthenticated, 400 for empty query

5. **Deterministic Response Generation**
   - Template-based text generation
   - No ML, no LLM, no external AI provider
   - No API keys or credentials
   - Query normalization and keyword matching
   - No invented information (grounded in records)

6. **i18n Support**
   - English (en) translation keys
   - Assamese (as) translation keys
   - 30 new keys minimum
   - Language switching via existing system

### ❌ EXPLICITLY NOT INCLUDED in Phase 10C

1. **Tamil Language**
   - Reserved for Phase 10E
   - No Tamil translations
   - No multilingual speech recognition
   - No multilingual TTS

2. **AI/LLM Integration**
   - NO OpenAI, Anthropic, Ollama, or any AI SDK
   - NO API keys in config.py or environment
   - NO modifications to requirements.txt for AI packages
   - Deterministic templates ONLY

3. **Advanced NLP & Search**
   - NO semantic search
   - NO vector embeddings or vector database
   - NO word embeddings (word2vec, GloVe, etc.)
   - NO NLP frameworks (NLTK, spaCy, etc.)
   - NO complex intent classification models
   - Simple keyword string processing only

4. **Caregiver Intelligence Features**
   - NO caregiver usage analytics
   - NO pattern detection in queries
   - NO recommendations for caregivers
   - Caregivers can view Memory Album (existing), not Memory Rescue insights

5. **Memory Rescue Editing**
   - Memory Rescue is view-only
   - All editing remains in Memory Album (Phase 10A)
   - NO add/edit/delete in Memory Rescue UI

6. **Mood & Emotion Tracking**
   - NO mood logging
   - NO sentiment analysis
   - NO emotion detection
   - NO daily mood checkins
   - Reserved for Phase 10D

7. **Enhanced Reminders**
   - NO new reminder types
   - NO reminder integration with Memory Rescue
   - Existing reminders (Phase 6) unmodified
   - Reserved for Phase 10D enhancement

8. **Safety & Geofencing**
   - NO location tracking
   - NO safe-zone geofencing
   - NO wandering alerts
   - NO location-based reminders
   - NO emergency contact features
   - Reserved for Phase 10E

9. **Cognitive Games**
   - Memory Rescue is NOT a game
   - NO ActivityLog entries from Memory Rescue
   - NO scoring in Memory Rescue
   - NO difficulty adaptation for Memory Rescue
   - NO game progression tracking

10. **Database Changes**
    - NO new tables
    - NO schema migrations
    - NO MemoryRecue model (use existing models)
    - Existing MemoryPerson, MemoryPlace, MemoryItem fully sufficient

---

## M. EXAMPLE USER FLOWS

### Flow 1: Memory Rescue - Viewing People

```
Patient opens /memory-rescue
  ↓
Backend serves memory_rescue.html with USER_ID injected
  ↓
JavaScript loads and calls GET /api/memory/people?patient_id=USER_ID
  ↓
Backend returns [MemoryPerson objects] for this patient
  ↓
JavaScript displays cards:
  [Photo] [Name] [Relationship] [Description]
  ↓
Patient views people, read descriptions
  ↓
Patient can click on person card (optional: show details modal)
```

### Flow 2: Memory Rescue - Voice Companion Query

```
Patient clicks "🎤 Ask Memora" button
  ↓
Browser requests microphone permission (first time)
  ↓
Patient speaks: "Who is Anil?"
  ↓
Speech Recognition converts to text: "Who is Anil?"
  ↓
JavaScript detects memory companion query (contains "Who is")
  ↓
POST /api/memory/search with query="Who is Anil?"
  ↓
Backend searches MemoryPerson.name LIKE "%Anil%"
  ↓
Returns:
{
    "people": [
        {
            "id": 5,
            "name": "Anil Sharma",
            "relationship": "Son",
            "description": "Lives in Delhi, works in IT"
        }
    ]
}
  ↓
Frontend generates response: "Anil Sharma is your son. He lives in Delhi, works in IT."
  ↓
Displays text on page: "Anil Sharma is your son. He lives in Delhi, works in IT."
  ↓
Speaks via SpeechSynthesis
  ↓
Patient hears response
```

### Flow 3: Memory Companion - No Match

```
Patient asks: "Who is Alex?"
  ↓
Search returns empty (no person named "Alex")
  ↓
Frontend generates response: "I don't have that information saved yet. You can ask your caregiver to add it to your Memory Album."
  ↓
Displays and speaks response
  ↓
Patient knows to ask caregiver
```

---

## N. TECHNICAL IMPLEMENTATION NOTES

### N1. Frontend Files
- **Extend** `static/js/voice_assistant.js` (do not replace)
  - Add `isMemoryCompanionQuery()` detection
  - Add `handleMemoryCompanionQuery()` handler
  - Keep existing time/date/reminder logic intact
- **Create** `templates/memory_rescue.html` (new page, view-only)
- **Create** `static/js/memory_rescue.js` (tab switching, display)
- Reuse existing `speak()` and `updateVoiceUI()` functions

### N2. Backend Files
- **Create** `routes/memory_assistance.py` (new blueprint)
  - POST `/api/memory/search` endpoint
  - Get user_id from session (never from request)
  - Search patient's records via `search_patient_memory()`
- **Create** `utils/memory_search.py` (search logic)
  - `search_patient_memory(user_id, query)` function
  - Search multiple fields per type
  - Case-insensitive LIKE queries
  - Query normalization (optional helper)
- **Create** `utils/response_generator.py` (response generation)
  - `generate_response(query, search_results)` function
  - Deterministic templates only
  - No AI, no LLM, no external calls

### N3. Search Implementation (Multi-Field)
```python
from sqlalchemy import or_

def search_patient_memory(user_id, query):
    """
    Search patient's memory records across all types.
    Searches multiple fields per type.
    """
    results = {
        'people': [],
        'places': [],
        'memories': []
    }
    
    query_pattern = f"%{query}%"
    
    # Search people: name, relationship, description
    people = MemoryPerson.query.filter_by(
        patient_id=user_id, 
        is_active=True
    ).filter(
        or_(
            MemoryPerson.name.ilike(query_pattern),
            MemoryPerson.relationship.ilike(query_pattern),
            MemoryPerson.description.ilike(query_pattern)
        )
    ).all()
    results['people'] = [p.to_dict() for p in people]
    
    # Search places: name, description
    places = MemoryPlace.query.filter_by(
        patient_id=user_id, 
        is_active=True
    ).filter(
        or_(
            MemoryPlace.name.ilike(query_pattern),
            MemoryPlace.description.ilike(query_pattern)
        )
    ).all()
    results['places'] = [pl.to_dict() for pl in places]
    
    # Search memories: title, description
    memories = MemoryItem.query.filter_by(
        patient_id=user_id, 
        is_active=True
    ).filter(
        or_(
            MemoryItem.title.ilike(query_pattern),
            MemoryItem.description.ilike(query_pattern)
        )
    ).all()
    results['memories'] = [m.to_dict() for m in memories]
    
    return results
```

### N4. Response Generation (Deterministic, No AI)
```python
def generate_response(query, results):
    """
    Generate response from search results.
    Deterministic templates only, no ML/AI/LLM.
    
    Args:
        query: original query string
        results: dict with 'people', 'places', 'memories' lists
    
    Returns:
        response_text: str (always a response, never None)
    """
    
    if not any(results.values()):
        # No matches found
        return "I don't have that information saved yet. You can ask your caregiver to add it to your Memory Album."
    
    # Prioritize: people > places > memories
    if results['people']:
        p = results['people'][0]  # First match only
        name = p.get('name', 'Someone')
        relationship = p.get('relationship', 'a person')
        desc = p.get('description', '').strip()
        if desc:
            return f"{name} is your {relationship}. {desc}"
        else:
            return f"{name} is your {relationship}."
    
    if results['places']:
        pl = results['places'][0]
        name = pl.get('name', 'A place')
        desc = pl.get('description', '').strip()
        if desc:
            return f"{name} is one of your saved places. {desc}"
        else:
            return f"{name} is one of your saved places."
    
    if results['memories']:
        m = results['memories'][0]
        title = m.get('title', 'Something')
        desc = m.get('description', '').strip()
        if desc:
            return f"You have a memory about {title}. {desc}"
        else:
            return f"You have a memory about {title}."
    
    # Should not reach here, but safety fallback
    return "I'm not sure how to answer that. Please try asking about a person, place, or memory."
```
        m = results['memories'][0]
        desc = m.get('description', '')
        return f"You have a memory about {m['title']}. {desc}".strip()
    
    return "I'm not sure how to answer that."
```

---

## O. DEPLOYMENT CONSIDERATIONS

### O1. Dependencies
**ZERO new package requirements for Phase 10C**
- requirements.txt remains: Flask==3.0.0, Flask-SQLAlchemy==3.1.1
- Web Speech API is browser built-in (no npm packages needed)
- Deterministic response generation requires no AI library
- No external API clients (openai, anthropic, etc.)
- No NLP frameworks (spaCy, NLTK, etc.)
- SQLAlchemy's `.ilike()` method available for case-insensitive search

### O2. Configuration Changes
**NO new environment variables or config needed for Phase 10C**
- config.py remains unchanged
- No AI_ENABLED flag needed
- No AI_PROVIDER configuration needed
- No API keys to manage

### O3. Database Changes
- NO migrations required
- Existing schema fully supports Phase 10C
- MemoryPerson, MemoryPlace, MemoryItem models already built
- is_active field already present
- to_dict() serialization already implemented

### O4. Browser Compatibility
- Memory Rescue page: All modern browsers (HTML/CSS/JS)
- Voice companion: Chrome, Edge, Safari, Firefox (Web Speech API support varies)
- Text fallback: Always available if voice unavailable
- No polyfills or shims required

---

## P. QUALITY ASSURANCE

### P1. Testing Coverage
- 30+ unit tests in test_phase10c_memory_assistance.py
- Test Memory Rescue display
- Test Memory Search API
- Test Voice Companion integration
- Test Patient Isolation
- Test Regression (Phase 1-10B still works)

### P2. Security Verification
- Patient isolation enforced at backend
- No cross-patient data leakage
- Session-based authorization
- No hard-coded credentials

### P3. Accessibility
- Large fonts in Memory Rescue
- High contrast design
- Large click targets
- Keyboard navigation support
- Screen reader friendly (semantic HTML)

### P4. Performance
- Memory search optimized with LIKE queries
- Pagination if >10 records (optional)
- Caching disabled (always fresh data)
- Response times < 1 second typical

---

## Q. APPROVAL CHECKLIST

Before implementing, confirm:

- [ ] Memory Rescue feature understood (view people/places/memories)
- [ ] Memory Search API design approved (POST /api/memory/search)
- [ ] Deterministic response generation acceptable (no AI in Phase 10C)
- [ ] Web Speech API reuse strategy approved
- [ ] i18n keys (30 EN + 30 AS) approved
- [ ] Patient isolation model verified
- [ ] Test plan coverage sufficient
- [ ] Scope boundaries clear (no Tamil, no AI LLM, no games)
- [ ] File list complete (7 create, 7 modify)
- [ ] Ready to implement

---

## IMPLEMENTATION READINESS

This plan is ready for review and approval. Upon approval:

1. Will create 7 new files (templates, JS, routes, utils, tests)
2. Will modify 7 existing files (app, routes, i18n, voice assistant)
3. Will implement 2 main features: Memory Rescue + AI Voice Companion
4. Will add 60 i18n keys (30 EN, 30 AS)
5. Will add ~35 unit tests covering all functionality
6. Will maintain 100% patient isolation and security

**NO CODE WILL BE WRITTEN** until this plan receives explicit approval.

---

**Plan prepared:** 2026-09-23  
**Status:** AWAITING APPROVAL  
**Ready to proceed:** Upon confirmation
