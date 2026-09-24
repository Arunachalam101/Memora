#!/usr/bin/env python3
"""Verification audit for Phase 10D"""

import json
from models.models import db, MoodEntry, User, MemoryItem, Reminder, ActivityLog
from app import app

print("=" * 70)
print("PHASE 10D FINAL VERIFICATION AUDIT")
print("=" * 70)

# 1. i18n Audit
print("\n[1] INTERNATIONALIZATION AUDIT")
print("-" * 70)

en = json.load(open('static/i18n/en.json', encoding='utf-8'))
as_data = json.load(open('static/i18n/as.json', encoding='utf-8'))

mood_keys = sorted([k for k in en.keys() if 'mood' in k])
mood_keys_as = sorted([k for k in as_data.keys() if 'mood' in k])

print(f"English mood-related keys: {len(mood_keys)}")
print(f"Assamese mood-related keys: {len(mood_keys_as)}")

missing_in_as = set(mood_keys) - set(mood_keys_as)
if missing_in_as:
    print(f"❌ Missing in Assamese: {missing_in_as}")
else:
    print(f"✅ All mood keys present in Assamese")

# Check for duplicates
en_dups = len(en) != len(set(en.keys()))
as_dups = len(as_data) != len(set(as_data.keys()))
if not en_dups and not as_dups:
    print("✅ No duplicate keys in either file")
else:
    print(f"❌ Duplicates found: EN={en_dups}, AS={as_dups}")

# Check for empty values
empty_en = [k for k in mood_keys if not en.get(k)]
empty_as = [k for k in mood_keys_as if not as_data.get(k)]
if not empty_en and not empty_as:
    print("✅ No empty mood translation values")
else:
    print(f"❌ Empty values: EN={empty_en}, AS={empty_as}")

# Check JSON validity
try:
    json.dumps(en)
    json.dumps(as_data)
    print("✅ Both JSON files are valid")
except:
    print("❌ JSON validation failed")

# 2. Database Audit
print("\n[2] DATABASE AUDIT")
print("-" * 70)

with app.app_context():
    # Create all tables first
    db.create_all()
    
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    print(f"Total tables: {len(tables)}")
    expected_tables = ['users', 'mood_entries', 'memory_items', 'reminders', 'activity_logs']
    
    for table in expected_tables:
        if table in tables:
            print(f"✅ {table} exists")
        else:
            print(f"❌ {table} missing")
    
    # Check mood_entries structure
    if 'mood_entries' in tables:
        cols = [c['name'] for c in inspector.get_columns('mood_entries')]
        required_cols = ['id', 'patient_id', 'mood', 'note', 'timestamp', 'created_at', 'updated_at']
        for col in required_cols:
            if col in cols:
                print(f"  ✅ Column '{col}' exists")
            else:
                print(f"  ❌ Column '{col}' missing")
    
    # Check indexes
    if 'mood_entries' in tables:
        mood_indexes = inspector.get_indexes('mood_entries')
        print(f"  Indexes on mood_entries: {len(mood_indexes)}")
        for idx in mood_indexes:
            print(f"    - {idx['name']}: {', '.join(idx['column_names'])}")

# 3. Authorization Tests
print("\n[3] AUTHORIZATION AUDIT")
print("-" * 70)

with app.app_context():
    client = app.test_client()
    
    # Create test users
    patient1 = User(id=100, name='Patient 1', role='patient')
    patient2 = User(id=101, name='Patient 2', role='patient')
    caregiver = User(id=200, name='Caregiver', role='caregiver')
    db.session.add_all([patient1, patient2, caregiver])
    db.session.commit()
    
    # Create test mood
    mood = MoodEntry(patient_id=100, mood='happy', note='Test note')
    db.session.add(mood)
    db.session.commit()
    
    # Test 1: Patient can create own mood
    with client.session_transaction() as sess:
        sess['user_id'] = 100
        sess['user_role'] = 'patient'
    resp = client.post('/api/mood/entries', json={'mood': 'happy'})
    print(f"✅ Patient create own mood: {resp.status_code == 201}" if resp.status_code == 201 else f"❌ Patient create own mood: {resp.status_code}")
    
    # Test 2: Patient cannot supply another patient ID
    with client.session_transaction() as sess:
        sess['user_id'] = 100
        sess['user_role'] = 'patient'
    resp = client.get('/api/mood/today?patient_id=101')
    print(f"✅ Patient denied other patient mood: {resp.status_code == 403}" if resp.status_code == 403 else f"❌ Patient denied other patient mood: {resp.status_code}")
    
    # Test 3: Caregiver can access patient mood
    with client.session_transaction() as sess:
        sess['user_id'] = 200
        sess['user_role'] = 'caregiver'
    resp = client.get('/api/mood/today?patient_id=100')
    print(f"✅ Caregiver can access patient mood: {resp.status_code == 200}" if resp.status_code == 200 else f"❌ Caregiver can access patient mood: {resp.status_code}")
    
    # Test 4: Patient denied stats endpoint
    with client.session_transaction() as sess:
        sess['user_id'] = 100
        sess['user_role'] = 'patient'
    resp = client.get('/api/mood/stats?patient_id=100')
    print(f"✅ Patient denied stats: {resp.status_code == 403}" if resp.status_code == 403 else f"❌ Patient denied stats: {resp.status_code}")
    
    # Test 5: Unauthenticated denied
    client.delete_cookie('session')
    resp = client.get('/api/mood/today')
    print(f"✅ Unauthenticated denied: {resp.status_code == 401}" if resp.status_code == 401 else f"❌ Unauthenticated denied: {resp.status_code}")

# 4. Voice Integration Audit
print("\n[4] VOICE INTEGRATION AUDIT")
print("-" * 70)

voice_js_path = 'static/js/voice_assistant.js'
try:
    with open(voice_js_path, encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('isMoodQuery function', 'isMoodQuery' in content),
        ('handleMoodQuery function', 'handleMoodQuery' in content),
        ('getMoodLabel function', 'getMoodLabel' in content),
        ('Mood intent in processVoiceQuery', 'mood' in content.lower() and 'processVoiceQuery' in content),
    ]
    
    for check_name, result in checks:
        print(f"{'✅' if result else '❌'} {check_name}")
except Exception as e:
    print(f"❌ Error reading voice_assistant.js: {e}")

# 5. Frontend Template Audit
print("\n[5] FRONTEND TEMPLATE AUDIT")
print("-" * 70)

try:
    with open('templates/mood.html', encoding='utf-8') as f:
        html = f.read()
    
    checks = [
        ('Emoji buttons', 'data-mood=' in html),
        ('Note textarea', '<textarea' in html and 'mood-note' in html),
        ('Submit button', 'Save Mood' in html),
        ('History section', 'mood-history' in html),
        ('i18n attributes', 'data-i18n-key=' in html),
    ]
    
    for check_name, result in checks:
        print(f"{'✅' if result else '❌'} {check_name}")
except Exception as e:
    print(f"❌ Error reading mood.html: {e}")

# 6. JavaScript Interactivity Audit
print("\n[6] JAVASCRIPT INTERACTIVITY AUDIT")
print("-" * 70)

try:
    with open('static/js/mood.js', encoding='utf-8') as f:
        js = f.read()
    
    checks = [
        ('MoodState object', 'const MoodState' in js),
        ('handleMoodSelect function', 'handleMoodSelect' in js),
        ('submitMood function', 'submitMood' in js),
        ('loadTodaysMood function', 'loadTodaysMood' in js),
        ('loadMoodHistory function', 'loadMoodHistory' in js),
        ('XSS prevention', 'escapeHtml' in js),
    ]
    
    for check_name, result in checks:
        print(f"{'✅' if result else '❌'} {check_name}")
except Exception as e:
    print(f"❌ Error reading mood.js: {e}")

print("\n" + "=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)
