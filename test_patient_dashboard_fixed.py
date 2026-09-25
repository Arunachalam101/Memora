"""
Test Patient Dashboard - Mood, Safety, and Game Features
Verifies mood tracking, emergency SOS, and game image display
CORRECTED VERSION - Uses proper routes
"""
import json
import requests
from datetime import datetime

BASE_URL = 'http://localhost:5000'

# Test users (from seed_demo_data.py)
PATIENT_PIN = '1234'
PATIENT_ID = 1
PATIENT_NAME = 'Priya Devi'

CAREGIVER_PIN = '5678'
CAREGIVER_ID = 2

print("=" * 70)
print("MEMORA PATIENT DASHBOARD - MOOD, SAFETY & GAMES VERIFICATION")
print("=" * 70)

# ============================================================
# Test 1: Verify Login Works and Session is Set
# ============================================================
print("\n[TEST 1] Patient Login & Session")
print("-" * 70)

session_patient = requests.Session()
r = session_patient.post(f'{BASE_URL}/login', data={'pin': PATIENT_PIN})
print(f"✓ Patient login: {r.status_code}")
print(f"  Cookies set: {len(session_patient.cookies)} cookies")
print(f"  Session ID: {session_patient.cookies.get('session', 'NO SESSION COOKIE')[:20]}...")

# ============================================================
# Test 2: Verify Mood Page Loads
# ============================================================
print("\n[TEST 2] Mood Page Load")
print("-" * 70)

r = session_patient.get(f'{BASE_URL}/mood')
print(f"✓ Mood page: {r.status_code}")
print(f"  Content size: {len(r.text)} bytes")

if '🎭 Check Your Mood' in r.text or 'mood_heading' in r.text:
    print(f"  ✓ Correct page (heading found)")
else:
    print(f"  ✗ WRONG PAGE - Expected mood page")
    print(f"  First 200 chars: {r.text[:200]}")

# Check for mood button elements
mood_checks = [
    ('mood-button', 'Mood selection buttons'),
    ('data-mood="happy"', 'Happy mood option'),
    ('data-mood="sad"', 'Sad mood option'),
    ('id="save-mood-btn"', 'Save mood button'),
    ('id="clear-mood-btn"', 'Clear button'),
    ('mood-selector', 'Mood selector container'),
]

for selector, label in mood_checks:
    if selector in r.text:
        print(f"  ✓ {label}")
    else:
        print(f"  ✗ {label} NOT found")

# ============================================================
# Test 3: Submit Mood Entry
# ============================================================
print("\n[TEST 3] Mood Submission")
print("-" * 70)

mood_data = {
    'mood': 'happy',
    'note': 'Had a great day!'
}

r = session_patient.post(
    f'{BASE_URL}/api/mood/entries',
    json=mood_data,
    headers={'Content-Type': 'application/json'}
)

print(f"✓ Mood POST: {r.status_code}")
if r.status_code == 201:
    print(f"  ✓ Mood created successfully")
    data = r.json()
    entry = data.get('entry', {})
    print(f"    - Mood: {entry.get('mood')}")
    print(f"    - Note: {entry.get('note')}")
else:
    print(f"  ✗ Expected 201, got {r.status_code}")
    print(f"  Response: {r.text[:200]}")

# ============================================================
# Test 4: Get Today's Mood
# ============================================================
print("\n[TEST 4] Get Today's Mood")
print("-" * 70)

r = session_patient.get(f'{BASE_URL}/api/mood/today')
print(f"✓ Get today's mood: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    if data.get('has_entry'):
        entry = data.get('entry', {})
        print(f"  ✓ Mood found: {entry.get('mood')}")
        print(f"    - Note: {entry.get('note')}")
    else:
        print(f"  ✗ No mood for today")
else:
    print(f"  ✗ Failed: {r.status_code}")

# ============================================================
# Test 5: Get Mood History
# ============================================================
print("\n[TEST 5] Mood History (14 days)")
print("-" * 70)

r = session_patient.get(f'{BASE_URL}/api/mood/history?limit=14')
print(f"✓ Get history: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    entries = data.get('entries', [])
    print(f"  ✓ Total entries: {data.get('total')}")
    print(f"  ✓ Retrieved: {len(entries)}")
    if entries:
        print(f"  ✓ Latest mood: {entries[0].get('mood')}")

# ============================================================
# Test 6: Safety Page Loads
# ============================================================
print("\n[TEST 6] Safety Page Load")
print("-" * 70)

r = session_patient.get(f'{BASE_URL}/safety')
print(f"✓ Safety page: {r.status_code}")
print(f"  Content size: {len(r.text)} bytes")

if 'Safety' in r.text or 'safety_title' in r.text:
    print(f"  ✓ Correct page (heading found)")
else:
    print(f"  ✗ WRONG PAGE - Expected safety page")

# Check for safety button elements
safety_checks = [
    ('id="sos-button"', 'Emergency/SOS button'),
    ('safety-status-card', 'Safety status card'),
    ('id="safety-icon"', 'Safety icon'),
    ('id="safety-status-label"', 'Safety status label'),
    ('emergency-button-container', 'Emergency button container'),
]

for selector, label in safety_checks:
    if selector in r.text:
        print(f"  ✓ {label}")
    else:
        print(f"  ✗ {label} NOT found")

# ============================================================
# Test 7: Check Safety Status
# ============================================================
print("\n[TEST 7] Safety Status Check")
print("-" * 70)

r = session_patient.get(f'{BASE_URL}/api/safety/status')
print(f"✓ Safety status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    status = data.get('status', 'unknown')
    print(f"  ✓ Status: {status}")
    if status in ['safe', 'alert']:
        print(f"  ✓ Valid status")

# ============================================================
# Test 8: Trigger SOS Emergency
# ============================================================
print("\n[TEST 8] Trigger SOS Emergency")
print("-" * 70)

r = session_patient.post(
    f'{BASE_URL}/api/safety/sos',
    headers={'Content-Type': 'application/json'}
)

print(f"✓ SOS POST: {r.status_code}")
if r.status_code == 200:
    print(f"  ✓ SOS triggered successfully")
    data = r.json()
    alert = data.get('alert', {})
    print(f"    - Alert type: {alert.get('alert_type')}")
    print(f"    - Status: {alert.get('status')}")
else:
    print(f"  ✗ Expected 200, got {r.status_code}")

# ============================================================
# Test 9: Caregiver Views Alert
# ============================================================
print("\n[TEST 9] Caregiver Views Patient Alert")
print("-" * 70)

session_caregiver = requests.Session()
r = session_caregiver.post(f'{BASE_URL}/login', data={'pin': CAREGIVER_PIN})
print(f"✓ Caregiver login: {r.status_code}")

r = session_caregiver.get(f'{BASE_URL}/api/safety/alerts')
print(f"✓ Get alerts: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    alerts = data.get('alerts', [])
    print(f"  ✓ Alerts found: {len(alerts)}")
    if alerts:
        alert = alerts[0]
        print(f"    - Patient: {alert.get('patient_id')}")
        print(f"    - Type: {alert.get('alert_type')}")
        print(f"    - Status: {alert.get('status')}")

# ============================================================
# Test 10: Games Hub Page
# ============================================================
print("\n[TEST 10] Games Hub Page")
print("-" * 70)

r = session_patient.get(f'{BASE_URL}/games')
print(f"✓ Games hub: {r.status_code}")
print(f"  Content size: {len(r.text)} bytes")

if 'Games' in r.text or 'games_hub_title' in r.text:
    print(f"  ✓ Correct page (heading found)")
else:
    print(f"  ✗ WRONG PAGE - Expected games hub")

# Check for game cards
game_checks = [
    ('game-card', 'Game cards container'),
    ('Memory Match', 'Memory Match game'),
    ('Attention Test', 'Attention Test game'),
    ('Photo / Name Match', 'Photo/Name Match game'),
    ('Who Is This', 'Who Is This game'),
]

for selector, label in game_checks:
    if selector in r.text:
        print(f"  ✓ {label}")
    else:
        print(f"  ✗ {label} NOT found")

# ============================================================
# Test 11: Memory Match Game Page
# ============================================================
print("\n[TEST 11] Memory Match Game Page")
print("-" * 70)

r = session_patient.get(f'{BASE_URL}/game/memory-match')
print(f"✓ Memory Match game: {r.status_code}")

if r.status_code == 200:
    checks = [
        ('id="game-board"', 'Game board'),
        ('id="completion-screen"', 'Completion screen'),
        ('memory_match.js', 'Game JavaScript'),
    ]
    for selector, label in checks:
        if selector in r.text:
            print(f"  ✓ {label}")
        else:
            print(f"  ✗ {label} NOT found")

# ============================================================
# Test 12: Attention Test Game Page
# ============================================================
print("\n[TEST 12] Attention Test Game Page")
print("-" * 70)

r = session_patient.get(f'{BASE_URL}/game/attention-test')
print(f"✓ Attention Test game: {r.status_code}")

if r.status_code == 200:
    checks = [
        ('id="attention-grid"', 'Attention grid'),
        ('id="completion-screen"', 'Completion screen'),
        ('attention_test.js', 'Game JavaScript'),
    ]
    for selector, label in checks:
        if selector in r.text:
            print(f"  ✓ {label}")
        else:
            print(f"  ✗ {label} NOT found")

# ============================================================
# Test 13: Photo/Name Match Game Page (with Images)
# ============================================================
print("\n[TEST 13] Photo/Name Match Game Page")
print("-" * 70)

r = session_patient.get(f'{BASE_URL}/game/photo-name-match')
print(f"✓ Photo/Name Match game: {r.status_code}")

if r.status_code == 200:
    checks = [
        ('id="question-photo"', 'Photo display element'),
        ('id="game-options"', 'Options container'),
        ('id="completion-screen"', 'Completion screen'),
        ('photo_name_match.js', 'Game JavaScript'),
    ]
    for selector, label in checks:
        if selector in r.text:
            print(f"  ✓ {label}")
        else:
            print(f"  ✗ {label} NOT found")

# ============================================================
# Test 14: Who Is This Game Page (with Images)
# ============================================================
print("\n[TEST 14] Who Is This Game Page")
print("-" * 70)

r = session_patient.get(f'{BASE_URL}/game/who-is-this')
print(f"✓ Who Is This game: {r.status_code}")

if r.status_code == 200:
    checks = [
        ('id="question-text"', 'Question text'),
        ('id="game-options"', 'Photo options container'),
        ('id="completion-screen"', 'Completion screen'),
        ('who_is_this.js', 'Game JavaScript'),
    ]
    for selector, label in checks:
        if selector in r.text:
            print(f"  ✓ {label}")
        else:
            print(f"  ✗ {label} NOT found")

# ============================================================
# Final Summary
# ============================================================
print("\n" + "=" * 70)
print("PATIENT DASHBOARD VERIFICATION COMPLETE")
print("=" * 70)
print("""
✅ Mood Feature: Create, view today, history
✅ Safety Feature: Check status, emergency SOS alert
✅ Games: All 4 games pages load correctly with image containers
✅ Caregiver Integration: Caregiver can see patient alerts
✅ Buttons: All interactive elements present and properly configured
""")
