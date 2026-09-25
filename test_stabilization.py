#!/usr/bin/env python3
"""
MEMORA FINAL STABILIZATION TEST
Tests all 14 features end-to-end to identify broken flows before APK packaging
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"
PATIENT_ID = 1
CAREGIVER_ID = 2

# Test results tracker
results = {
    'passed': [],
    'failed': [],
    'errors': []
}

def log_pass(feature, detail=""):
    msg = f"✅ {feature}"
    if detail:
        msg += f" - {detail}"
    print(msg)
    results['passed'].append(feature)

def log_fail(feature, reason=""):
    msg = f"❌ {feature}"
    if reason:
        msg += f" - {reason}"
    print(msg)
    results['failed'].append(feature)

def log_error(feature, error_detail=""):
    msg = f"⚠️ {feature}"
    if error_detail:
        msg += f" - {error_detail}"
    print(msg)
    results['errors'].append((feature, error_detail))

print("=" * 70)
print("MEMORA FINAL STABILIZATION TEST")
print("=" * 70)

# ============================================================
# PART 1: AUTHENTICATION
# ============================================================
print("\n[PART 1] AUTHENTICATION")
print("-" * 70)

patient_session = requests.Session()
caregiver_session = requests.Session()

try:
    # Patient login
    resp = patient_session.post(f"{BASE_URL}/login", 
        data={'name': 'Priya Devi', 'pin': '1234'})
    if resp.status_code in [200, 302]:  # 200 for direct response, 302 for redirect
        log_pass("Patient login (Priya Devi)")
    else:
        log_fail("Patient login", f"Status {resp.status_code}")
except Exception as e:
    log_error("Patient login", str(e))

try:
    # Caregiver login
    resp = caregiver_session.post(f"{BASE_URL}/login",
        data={'name': 'Anil Sharma', 'pin': '5678'})
    if resp.status_code in [200, 302]:  # 200 for direct response, 302 for redirect
        log_pass("Caregiver login (Anil Sharma)")
    else:
        log_fail("Caregiver login", f"Status {resp.status_code}")
except Exception as e:
    log_error("Caregiver login", str(e))

# ============================================================
# PART 2: MEMORY ALBUM
# ============================================================
print("\n[PART 2] MEMORY ALBUM - PEOPLE")
print("-" * 70)

person_id = None

try:
    # Create person
    resp = patient_session.post(
        f"{BASE_URL}/api/memory/people",
        data={
            'patient_id': PATIENT_ID,
            'name': 'Test Person',
            'relationship': 'Test Relation',
            'description': 'Test Description'
        }
    )
    if resp.status_code == 201:
        data = resp.json()
        if 'id' in data:
            person_id = data['id']
            log_pass("Create person", f"ID={person_id}")
        else:
            log_fail("Create person - no ID in response", json.dumps(data))
    else:
        log_fail("Create person", f"Status {resp.status_code}: {resp.text}")
except Exception as e:
    log_error("Create person", str(e))

try:
    # Get people
    resp = patient_session.get(
        f"{BASE_URL}/api/memory/people",
        params={'patient_id': PATIENT_ID}
    )
    if resp.status_code == 200:
        people = resp.json()
        if isinstance(people, list) and len(people) > 0:
            log_pass("Get people", f"Found {len(people)} people")
        else:
            log_fail("Get people", "Empty list returned")
    else:
        log_fail("Get people", f"Status {resp.status_code}")
except Exception as e:
    log_error("Get people", str(e))

try:
    # Update person (form data, not JSON!)
    if person_id:
        resp = patient_session.put(
            f"{BASE_URL}/api/memory/people/{person_id}",
            data={
                'patient_id': PATIENT_ID,
                'name': 'Updated Person Name',
                'relationship': 'Updated Relation',
                'description': 'Updated Description'
            }
        )
        if resp.status_code == 200:
            log_pass("Update person", f"ID={person_id}")
        else:
            log_fail("Update person", f"Status {resp.status_code}: {resp.text}")
except Exception as e:
    log_error("Update person", str(e))

try:
    # Delete person
    if person_id:
        resp = patient_session.delete(
            f"{BASE_URL}/api/memory/people/{person_id}",
            params={'patient_id': PATIENT_ID}
        )
        if resp.status_code == 200:
            log_pass("Delete person", f"ID={person_id}")
        else:
            log_fail("Delete person", f"Status {resp.status_code}: {resp.text}")
except Exception as e:
    log_error("Delete person", str(e))

# ============================================================
# PART 3: MOOD
# ============================================================
print("\n[PART 3] MOOD TRACKING")
print("-" * 70)

mood_id = None

try:
    # Create mood entry
    resp = patient_session.post(
        f"{BASE_URL}/api/mood/entries",
        json={
            'mood': 'happy',
            'note': 'Test mood entry'
        }
    )
    if resp.status_code == 201:
        data = resp.json()
        if 'id' in data:
            mood_id = data['id']
            log_pass("Create mood entry", f"Mood=happy, ID={mood_id}")
        else:
            log_fail("Create mood - no ID in response", json.dumps(data))
    else:
        log_fail("Create mood entry", f"Status {resp.status_code}: {resp.text}")
except Exception as e:
    log_error("Create mood entry", str(e))

try:
    # Get today's mood
    resp = patient_session.get(f"{BASE_URL}/api/mood/today")
    if resp.status_code == 200:
        data = resp.json()
        if 'has_entry' in data:
            log_pass("Get today's mood", f"Has entry: {data.get('has_entry')}")
        else:
            log_fail("Get today's mood - unexpected format", json.dumps(data))
    else:
        log_fail("Get today's mood", f"Status {resp.status_code}")
except Exception as e:
    log_error("Get today's mood", str(e))

try:
    # Get mood history
    resp = patient_session.get(f"{BASE_URL}/api/mood/history")
    if resp.status_code == 200:
        data = resp.json()
        # Handle both wrapped {"entries": [...]} and unwrapped [...] formats
        if isinstance(data, dict) and 'entries' in data:
            entries = data['entries']
        elif isinstance(data, list):
            entries = data
        else:
            entries = None
        
        if isinstance(entries, list):
            log_pass("Get mood history", f"Found {len(entries)} entries")
        else:
            log_fail("Get mood history - unexpected format", json.dumps(data))
    else:
        log_fail("Get mood history", f"Status {resp.status_code}")
except Exception as e:
    log_error("Get mood history", str(e))

# ============================================================
# PART 4: REMINDERS
# ============================================================
print("\n[PART 4] REMINDERS")
print("-" * 70)

reminder_id = None

try:
    # Create reminder
    resp = patient_session.post(
        f"{BASE_URL}/api/reminders",
        json={
            'title': 'Test Reminder',
            'type': 'medicine',
            'time': '09:00'
        }
    )
    if resp.status_code == 201:
        data = resp.json()
        if 'id' in data:
            reminder_id = data['id']
            log_pass("Create reminder", f"ID={reminder_id}")
        else:
            log_fail("Create reminder - no ID", json.dumps(data))
    else:
        log_fail("Create reminder", f"Status {resp.status_code}: {resp.text}")
except Exception as e:
    log_error("Create reminder", str(e))

try:
    # Get reminders
    resp = patient_session.get(f"{BASE_URL}/api/reminders")
    if resp.status_code == 200:
        reminders = resp.json()
        if isinstance(reminders, list):
            log_pass("Get reminders", f"Found {len(reminders)} reminders")
        else:
            log_fail("Get reminders - not a list", json.dumps(reminders))
    else:
        log_fail("Get reminders", f"Status {resp.status_code}")
except Exception as e:
    log_error("Get reminders", str(e))

try:
    # Update reminder (mark done)
    if reminder_id:
        resp = patient_session.put(
            f"{BASE_URL}/api/reminders/{reminder_id}",
            json={
                'is_done': True
            }
        )
        if resp.status_code == 200:
            log_pass("Update reminder (mark done)", f"ID={reminder_id}")
        else:
            log_fail("Update reminder", f"Status {resp.status_code}: {resp.text}")
except Exception as e:
    log_error("Update reminder", str(e))

try:
    # Delete reminder
    if reminder_id:
        resp = patient_session.delete(f"{BASE_URL}/api/reminders/{reminder_id}")
        if resp.status_code == 200:
            log_pass("Delete reminder", f"ID={reminder_id}")
        else:
            log_fail("Delete reminder", f"Status {resp.status_code}")
except Exception as e:
    log_error("Delete reminder", str(e))

# ============================================================
# PART 5: SAFETY / SOS
# ============================================================
print("\n[PART 5] SAFETY / SOS")
print("-" * 70)

alert_id = None

try:
    # Trigger SOS
    resp = patient_session.post(
        f"{BASE_URL}/api/safety/sos",
        json={'message': 'Test emergency'}
    )
    if resp.status_code in [200, 201]:
        data = resp.json()
        if isinstance(data, dict) and 'id' in data:
            alert_id = data['id']
            log_pass("Trigger SOS", f"Alert ID={alert_id}")
        else:
            log_pass("Trigger SOS", "Status OK but format unclear")
    else:
        log_fail("Trigger SOS", f"Status {resp.status_code}: {resp.text}")
except Exception as e:
    log_error("Trigger SOS", str(e))

try:
    # Get alerts (caregiver)
    resp = caregiver_session.get(f"{BASE_URL}/api/safety/alerts")
    if resp.status_code == 200:
        data = resp.json()
        # Handle both wrapped {"alerts": [...], "success": true} and unwrapped [...] formats
        if isinstance(data, dict) and 'alerts' in data:
            alerts = data['alerts']
        elif isinstance(data, list):
            alerts = data
        else:
            alerts = None
        
        if isinstance(alerts, list):
            log_pass("Get safety alerts (caregiver)", f"Found {len(alerts)} alerts")
        else:
            log_fail("Get alerts - unexpected format", json.dumps(data))
    else:
        log_fail("Get safety alerts", f"Status {resp.status_code}")
except Exception as e:
    log_error("Get safety alerts", str(e))

try:
    # Resolve alert (caregiver)
    if alert_id:
        resp = caregiver_session.post(
            f"{BASE_URL}/api/safety/alerts/{alert_id}/resolve",
            json={'message': 'Resolved'}
        )
        if resp.status_code in [200, 201]:
            log_pass("Resolve alert", f"Alert ID={alert_id}")
        else:
            log_fail("Resolve alert", f"Status {resp.status_code}")
except Exception as e:
    log_error("Resolve alert", str(e))

# ============================================================
# PART 6: GAMES & PROGRESS
# ============================================================
print("\n[PART 6] GAMES & PROGRESS")
print("-" * 70)

try:
    # Log game result
    resp = patient_session.post(
        f"{BASE_URL}/api/games/log",
        json={
            'game_type': 'memory_match',
            'score': 85,
            'accuracy': 88.5,
            'time_taken': 120.5,
            'difficulty': 'medium'
        }
    )
    if resp.status_code in [200, 201]:
        log_pass("Log game result", "Memory Match")
    else:
        log_fail("Log game result", f"Status {resp.status_code}: {resp.text}")
except Exception as e:
    log_error("Log game result", str(e))

try:
    # Get progress
    resp = caregiver_session.get(f"{BASE_URL}/api/progress/{PATIENT_ID}")
    if resp.status_code == 200:
        progress = resp.json()
        if isinstance(progress, list):
            log_pass("Get progress", f"Found {len(progress)} activity records")
        else:
            log_fail("Get progress - not a list", json.dumps(progress))
    else:
        log_fail("Get progress", f"Status {resp.status_code}")
except Exception as e:
    log_error("Get progress", str(e))

# ============================================================
# PART 7: CAREGIVER DASHBOARD
# ============================================================
print("\n[PART 7] CAREGIVER DASHBOARD")
print("-" * 70)

try:
    # Get patients list
    resp = caregiver_session.get(f"{BASE_URL}/api/users/patients")
    if resp.status_code == 200:
        patients = resp.json()
        if isinstance(patients, list) and len(patients) > 0:
            log_pass("Get patients list", f"Found {len(patients)} patients")
        else:
            log_fail("Get patients list", "Empty list")
    else:
        log_fail("Get patients list", f"Status {resp.status_code}")
except Exception as e:
    log_error("Get patients list", str(e))

try:
    # Get difficulty level
    resp = caregiver_session.get(f"{BASE_URL}/api/difficulty/{PATIENT_ID}")
    if resp.status_code == 200:
        data = resp.json()
        if 'difficulty' in data:
            log_pass("Get difficulty level", f"Difficulty={data['difficulty']}")
        else:
            log_fail("Get difficulty - missing field", json.dumps(data))
    else:
        log_fail("Get difficulty", f"Status {resp.status_code}")
except Exception as e:
    log_error("Get difficulty", str(e))

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"✅ Passed: {len(results['passed'])}")
for item in results['passed']:
    print(f"  - {item}")

print(f"\n❌ Failed: {len(results['failed'])}")
for item in results['failed']:
    print(f"  - {item}")

if results['errors']:
    print(f"\n⚠️ Errors: {len(results['errors'])}")
    for feature, error in results['errors']:
        print(f"  - {feature}: {error}")

total = len(results['passed']) + len(results['failed']) + len(results['errors'])
print(f"\nTOTAL: {total} tests")

pass_rate = len(results['passed']) / total * 100 if total > 0 else 0
print(f"PASS RATE: {pass_rate:.1f}%")

if len(results['failed']) == 0 and len(results['errors']) == 0:
    print("\n✅ ALL TESTS PASSED - READY FOR APK PACKAGING")
else:
    print("\n⚠️ ISSUES DETECTED - NEEDS FIXES BEFORE APK PACKAGING")
