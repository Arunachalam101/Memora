#!/usr/bin/env python3
"""
MEMORA EXTENDED STABILIZATION TEST
Tests all 14 features including Places and Memories CRUD
"""

import requests
import json

BASE_URL = "http://localhost:5000"
PATIENT_ID = 1

results = {'passed': [], 'failed': [], 'errors': []}

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
print("MEMORA EXTENDED STABILIZATION TEST")
print("=" * 70)

patient_session = requests.Session()

# Login
patient_session.post(f"{BASE_URL}/login", data={'name': 'Priya Devi', 'pin': '1234'})

# ============================================================
# TEST 1: MEMORY ALBUM - PLACES
# ============================================================
print("\n[TEST 1] MEMORY ALBUM - PLACES")
print("-" * 70)

place_id = None

try:
    resp = patient_session.post(
        f"{BASE_URL}/api/memory/places",
        data={
            'patient_id': PATIENT_ID,
            'name': 'Home',
            'description': 'My home'
        }
    )
    if resp.status_code == 201:
        place_id = resp.json().get('id')
        log_pass("Create place", f"ID={place_id}")
    else:
        log_fail("Create place", f"Status {resp.status_code}")
except Exception as e:
    log_error("Create place", str(e))

try:
    resp = patient_session.get(f"{BASE_URL}/api/memory/places",
        params={'patient_id': PATIENT_ID})
    if resp.status_code == 200 and isinstance(resp.json(), list):
        log_pass("Get places", f"Found {len(resp.json())} places")
    else:
        log_fail("Get places", f"Status {resp.status_code}")
except Exception as e:
    log_error("Get places", str(e))

try:
    if place_id:
        resp = patient_session.put(
            f"{BASE_URL}/api/memory/places/{place_id}",
            data={
                'patient_id': PATIENT_ID,
                'name': 'Updated Home',
                'description': 'Updated my home'
            }
        )
        if resp.status_code == 200:
            log_pass("Update place", f"ID={place_id}")
        else:
            log_fail("Update place", f"Status {resp.status_code}")
except Exception as e:
    log_error("Update place", str(e))

try:
    if place_id:
        resp = patient_session.delete(
            f"{BASE_URL}/api/memory/places/{place_id}",
            params={'patient_id': PATIENT_ID}
        )
        if resp.status_code == 200:
            log_pass("Delete place", f"ID={place_id}")
        else:
            log_fail("Delete place", f"Status {resp.status_code}")
except Exception as e:
    log_error("Delete place", str(e))

# ============================================================
# TEST 2: MEMORY ALBUM - MEMORIES
# ============================================================
print("\n[TEST 2] MEMORY ALBUM - MEMORIES")
print("-" * 70)

memory_id = None

try:
    resp = patient_session.post(
        f"{BASE_URL}/api/memory/memories",
        data={
            'patient_id': PATIENT_ID,
            'title': 'Wedding Day',
            'description': 'My wedding day memory'
        }
    )
    if resp.status_code == 201:
        memory_id = resp.json().get('id')
        log_pass("Create memory", f"ID={memory_id}")
    else:
        log_fail("Create memory", f"Status {resp.status_code}")
except Exception as e:
    log_error("Create memory", str(e))

try:
    resp = patient_session.get(f"{BASE_URL}/api/memory/memories",
        params={'patient_id': PATIENT_ID})
    if resp.status_code == 200 and isinstance(resp.json(), list):
        log_pass("Get memories", f"Found {len(resp.json())} memories")
    else:
        log_fail("Get memories", f"Status {resp.status_code}")
except Exception as e:
    log_error("Get memories", str(e))

try:
    if memory_id:
        resp = patient_session.put(
            f"{BASE_URL}/api/memory/memories/{memory_id}",
            data={
                'patient_id': PATIENT_ID,
                'title': 'Updated Wedding',
                'description': 'Updated memory'
            }
        )
        if resp.status_code == 200:
            log_pass("Update memory", f"ID={memory_id}")
        else:
            log_fail("Update memory", f"Status {resp.status_code}")
except Exception as e:
    log_error("Update memory", str(e))

try:
    if memory_id:
        resp = patient_session.delete(
            f"{BASE_URL}/api/memory/memories/{memory_id}",
            params={'patient_id': PATIENT_ID}
        )
        if resp.status_code == 200:
            log_pass("Delete memory", f"ID={memory_id}")
        else:
            log_fail("Delete memory", f"Status {resp.status_code}")
except Exception as e:
    log_error("Delete memory", str(e))

# ============================================================
# TEST 3: MEMORY RESCUE / SEARCH
# ============================================================
print("\n[TEST 3] MEMORY RESCUE / SEARCH")
print("-" * 70)

try:
    resp = patient_session.post(
        f"{BASE_URL}/api/memory/search",
        json={'query': 'home'}
    )
    if resp.status_code == 200:
        log_pass("Memory search", "Query executed")
    else:
        log_fail("Memory search", f"Status {resp.status_code}")
except Exception as e:
    log_error("Memory search", str(e))

# ============================================================
# TEST 4: GAMES - VERIFY ALL GAMES CAN LOG
# ============================================================
print("\n[TEST 4] GAMES - LOG ALL GAME TYPES")
print("-" * 70)

games = [
    ('memory_match', 'Memory Match'),
    ('attention_test', 'Attention Test'),
    ('photo_name_match', 'Photo/Name Match'),
    ('who_is_this', 'Who Is This')
]

for game_type, game_name in games:
    try:
        resp = patient_session.post(
            f"{BASE_URL}/api/games/log",
            json={
                'game_type': game_type,
                'score': 80,
                'accuracy': 85.0,
                'time_taken': 120.0,
                'difficulty': 'medium'
            }
        )
        if resp.status_code in [200, 201]:
            log_pass(f"Log {game_name}", "Score recorded")
        else:
            log_fail(f"Log {game_name}", f"Status {resp.status_code}")
    except Exception as e:
        log_error(f"Log {game_name}", str(e))

# ============================================================
# TEST 5: DATABASE PERSISTENCE - REFRESH AND VERIFY
# ============================================================
print("\n[TEST 5] DATABASE PERSISTENCE - REFRESH VERIFICATION")
print("-" * 70)

try:
    # Create a test item
    resp = patient_session.post(
        f"{BASE_URL}/api/memory/people",
        data={
            'patient_id': PATIENT_ID,
            'name': 'Persistence Test',
            'relationship': 'Test'
        }
    )
    if resp.status_code == 201:
        test_person_id = resp.json().get('id')
        
        # Immediately fetch to verify it exists
        resp2 = patient_session.get(
            f"{BASE_URL}/api/memory/people",
            params={'patient_id': PATIENT_ID}
        )
        people = resp2.json()
        if any(p['id'] == test_person_id for p in people):
            log_pass("Database persistence", "Data committed immediately after create")
        else:
            log_fail("Database persistence", "Created item not found in list")
    else:
        log_fail("Database persistence", "Could not create test item")
except Exception as e:
    log_error("Database persistence", str(e))

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"✅ Passed: {len(results['passed'])}")
print(f"❌ Failed: {len(results['failed'])}")
print(f"⚠️ Errors: {len(results['errors'])}")
total = len(results['passed']) + len(results['failed']) + len(results['errors'])
pass_rate = len(results['passed']) / total * 100 if total > 0 else 0
print(f"\nTOTAL: {total} tests")
print(f"PASS RATE: {pass_rate:.1f}%")

if len(results['failed']) == 0 and len(results['errors']) == 0:
    print("\n✅ ALL EXTENDED TESTS PASSED")
else:
    print("\n❌ SOME TESTS FAILED")
    if results['failed']:
        print("\nFailed tests:")
        for item in results['failed']:
            print(f"  - {item}")
    if results['errors']:
        print("\nErrors:")
        for feature, error in results['errors']:
            print(f"  - {feature}: {error}")
