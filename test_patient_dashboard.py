"""
Test Patient Dashboard - Mood, Safety, and Game Features
Verifies mood tracking, emergency SOS, and game image display
"""
import json
import requests
import time
from datetime import datetime

BASE_URL = 'http://localhost:5000'
SESSION = requests.Session()

# Test users (from seed_demo_data.py)
PATIENT_PIN = '1234'
PATIENT_ID = 1
PATIENT_NAME = 'Priya Devi'

CAREGIVER_PIN = '5678'
CAREGIVER_ID = 2

def login_patient():
    """Login as patient"""
    response = SESSION.post(f'{BASE_URL}/login', data={'pin': PATIENT_PIN})
    if response.status_code in [200, 302]:
        print(f"✓ Patient login: {response.status_code} OK")
        return True
    print(f"✗ Patient login failed: {response.status_code}")
    return False

def login_caregiver():
    """Login as caregiver"""
    response = SESSION.post(f'{BASE_URL}/login', data={'pin': CAREGIVER_PIN})
    if response.status_code in [200, 302]:
        print(f"✓ Caregiver login: {response.status_code} OK")
        return True
    print(f"✗ Caregiver login failed: {response.status_code}")
    return False

def test_mood_page_loads():
    """Test 1: Mood page loads with all buttons"""
    print("\n[TEST 1] Mood Page Load")
    print("-" * 70)
    
    response = SESSION.get(f'{BASE_URL}/mood')
    if response.status_code != 200:
        print(f"✗ Mood page load failed: {response.status_code}")
        return False
    
    print(f"✓ Mood page loads: 200 OK")
    
    # Check for mood buttons
    checks = [
        ('mood selection buttons', 'mood-button'),
        ('save mood button', 'id="save-mood-btn"'),
        ('clear button', 'id="clear-mood-btn"'),
        ('note textarea', 'id="mood-note"'),
        ('mood history section', 'id="mood-history"'),
    ]
    
    for label, check_str in checks:
        if check_str in response.text:
            print(f"  ✓ {label}")
        else:
            print(f"  ✗ {label} NOT found")
            return False
    
    return True

def test_mood_submission():
    """Test 2: Create mood entry and verify response"""
    print("\n[TEST 2] Mood Submission")
    print("-" * 70)
    
    mood_data = {
        'mood': 'happy',
        'note': 'Had a good day with family'
    }
    
    response = SESSION.post(
        f'{BASE_URL}/api/mood/entries',
        json=mood_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 201:
        print(f"✗ Mood creation failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False
    
    print(f"✓ Mood entry created: 201 Created")
    
    data = response.json()
    entry = data.get('entry', {})
    
    checks = {
        'mood value': entry.get('mood') == 'happy',
        'note saved': entry.get('note') == 'Had a good day with family',
        'timestamp present': 'timestamp' in entry,
        'patient_id correct': entry.get('patient_id') == PATIENT_ID,
    }
    
    all_pass = True
    for label, result in checks.items():
        if result:
            print(f"  ✓ {label}")
        else:
            print(f"  ✗ {label}")
            all_pass = False
    
    return all_pass

def test_mood_retrieval():
    """Test 3: Retrieve today's mood"""
    print("\n[TEST 3] Mood Retrieval (Today)")
    print("-" * 70)
    
    response = SESSION.get(f'{BASE_URL}/api/mood/today')
    
    if response.status_code != 200:
        print(f"✗ Get today's mood failed: {response.status_code}")
        return False
    
    print(f"✓ Today's mood retrieved: 200 OK")
    
    data = response.json()
    if not data.get('has_entry'):
        print(f"✗ No mood entry for today")
        return False
    
    entry = data.get('entry', {})
    print(f"  ✓ Mood: {entry.get('mood')}")
    print(f"  ✓ Note: {entry.get('note')}")
    print(f"  ✓ Timestamp: {entry.get('timestamp')}")
    
    return True

def test_mood_history():
    """Test 4: Get mood history"""
    print("\n[TEST 4] Mood History (14 days)")
    print("-" * 70)
    
    response = SESSION.get(f'{BASE_URL}/api/mood/history?limit=14')
    
    if response.status_code != 200:
        print(f"✗ Get mood history failed: {response.status_code}")
        return False
    
    print(f"✓ Mood history retrieved: 200 OK")
    
    data = response.json()
    entries = data.get('entries', [])
    total = data.get('total', 0)
    
    print(f"  ✓ Total entries: {total}")
    print(f"  ✓ Retrieved entries: {len(entries)}")
    
    if entries:
        latest = entries[0]
        print(f"  ✓ Latest mood: {latest.get('mood')}")
        print(f"  ✓ Latest timestamp: {latest.get('timestamp')}")
    
    return True

def test_safety_page_loads():
    """Test 5: Safety page loads with emergency button"""
    print("\n[TEST 5] Safety Page Load")
    print("-" * 70)
    
    response = SESSION.get(f'{BASE_URL}/safety')
    if response.status_code != 200:
        print(f"✗ Safety page load failed: {response.status_code}")
        return False
    
    print(f"✓ Safety page loads: 200 OK")
    
    checks = [
        ('emergency button', 'id="sos-button"'),
        ('safety status card', 'safety-status-card'),
        ('safety icon', 'id="safety-icon"'),
        ('safety status label', 'id="safety-status-label"'),
        ('success message', 'id="success-message"'),
    ]
    
    for label, check_str in checks:
        if check_str in response.text:
            print(f"  ✓ {label}")
        else:
            print(f"  ✗ {label} NOT found")
            return False
    
    return True

def test_safety_status():
    """Test 6: Check safety status API"""
    print("\n[TEST 6] Safety Status Check")
    print("-" * 70)
    
    response = SESSION.get(f'{BASE_URL}/api/safety/status')
    
    if response.status_code != 200:
        print(f"✗ Get safety status failed: {response.status_code}")
        return False
    
    print(f"✓ Safety status retrieved: 200 OK")
    
    data = response.json()
    status = data.get('status', 'unknown')
    print(f"  ✓ Status: {status}")
    
    if status not in ['safe', 'alert']:
        print(f"  ✗ Invalid status value: {status}")
        return False
    
    return True

def test_sos_trigger():
    """Test 7: Trigger SOS emergency alert"""
    print("\n[TEST 7] SOS Emergency Alert Trigger")
    print("-" * 70)
    
    response = SESSION.post(
        f'{BASE_URL}/api/safety/sos',
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"✗ SOS trigger failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False
    
    print(f"✓ SOS alert triggered: 200 OK")
    
    data = response.json()
    alert = data.get('alert', {})
    
    checks = {
        'alert_type is emergency': alert.get('alert_type') == 'emergency',
        'status is active': alert.get('status') == 'active',
        'patient_id correct': alert.get('patient_id') == PATIENT_ID,
    }
    
    all_pass = True
    for label, result in checks.items():
        if result:
            print(f"  ✓ {label}")
        else:
            print(f"  ✗ {label}")
            all_pass = False
    
    return all_pass

def test_caregiver_sees_alert():
    """Test 8: Caregiver can see patient's alert"""
    print("\n[TEST 8] Caregiver Views Patient Alert")
    print("-" * 70)
    
    # First, logout patient and login as caregiver
    SESSION.get(f'{BASE_URL}/logout')
    
    if not login_caregiver():
        print("✗ Could not login as caregiver")
        return False
    
    response = SESSION.get(f'{BASE_URL}/api/safety/alerts')
    
    if response.status_code != 200:
        print(f"✗ Get alerts failed: {response.status_code}")
        return False
    
    print(f"✓ Caregiver retrieved alerts: 200 OK")
    
    data = response.json()
    alerts = data.get('alerts', [])
    
    if not alerts:
        print(f"✗ No alerts found")
        return False
    
    print(f"  ✓ Alerts found: {len(alerts)}")
    
    # Find the emergency alert we just created
    emergency_alert = next((a for a in alerts if a.get('alert_type') == 'emergency'), None)
    
    if not emergency_alert:
        print(f"✗ Emergency alert not found in caregiver view")
        return False
    
    print(f"  ✓ Emergency alert visible to caregiver")
    print(f"    - Patient ID: {emergency_alert.get('patient_id')}")
    print(f"    - Status: {emergency_alert.get('status')}")
    print(f"    - Message: {emergency_alert.get('message')}")
    
    return True

def test_game_hub_images():
    """Test 9: Game hub page loads with game cards"""
    print("\n[TEST 9] Game Hub - Images and Cards")
    print("-" * 70)
    
    # Login as patient first
    SESSION.get(f'{BASE_URL}/logout')
    login_patient()
    
    response = SESSION.get(f'{BASE_URL}/games')
    if response.status_code != 200:
        print(f"✗ Game hub page load failed: {response.status_code}")
        return False
    
    print(f"✓ Game hub page loads: 200 OK")
    
    checks = [
        ('Memory Match card', 'memory-match'),
        ('Attention Test card', 'attention-test'),
        ('Photo/Name Match card', 'photo-name-match'),
        ('Who Is This card', 'who-is-this'),
        ('Game icons (emojis)', '🧠'),
    ]
    
    all_pass = True
    for label, check_str in checks:
        if check_str in response.text:
            print(f"  ✓ {label}")
        else:
            print(f"  ✗ {label} NOT found")
            all_pass = False
    
    return all_pass

def test_photo_name_match_game_images():
    """Test 10: Photo/Name Match game loads and displays images"""
    print("\n[TEST 10] Photo/Name Match Game - Image Display")
    print("-" * 70)
    
    response = SESSION.get(f'{BASE_URL}/games/photo-name-match')
    if response.status_code != 200:
        print(f"✗ Game page load failed: {response.status_code}")
        return False
    
    print(f"✓ Photo/Name Match game page loads: 200 OK")
    
    checks = [
        ('question photo element', 'id="question-photo"'),
        ('game options container', 'id="game-options"'),
        ('completion screen', 'id="completion-screen"'),
    ]
    
    for label, check_str in checks:
        if check_str in response.text:
            print(f"  ✓ {label}")
        else:
            print(f"  ✗ {label} NOT found")
            return False
    
    # Check JavaScript for image loading
    if 'photo_name_match.js' in response.text:
        print(f"  ✓ Game JavaScript loaded")
    else:
        print(f"  ✗ Game JavaScript not found")
        return False
    
    return True

def test_who_is_this_game_images():
    """Test 11: Who Is This game loads and displays images"""
    print("\n[TEST 11] Who Is This Game - Image Display")
    print("-" * 70)
    
    response = SESSION.get(f'{BASE_URL}/games/who-is-this')
    if response.status_code != 200:
        print(f"✗ Game page load failed: {response.status_code}")
        return False
    
    print(f"✓ Who Is This game page loads: 200 OK")
    
    checks = [
        ('question text element', 'id="question-text"'),
        ('game photo options', 'id="game-options"'),
        ('completion screen', 'id="completion-screen"'),
    ]
    
    for label, check_str in checks:
        if check_str in response.text:
            print(f"  ✓ {label}")
        else:
            print(f"  ✗ {label} NOT found")
            return False
    
    # Check JavaScript for image loading
    if 'who_is_this.js' in response.text:
        print(f"  ✓ Game JavaScript loaded")
    else:
        print(f"  ✗ Game JavaScript not found")
        return False
    
    return True

def test_memory_match_game():
    """Test 12: Memory Match game loads"""
    print("\n[TEST 12] Memory Match Game - Display")
    print("-" * 70)
    
    response = SESSION.get(f'{BASE_URL}/games/memory-match')
    if response.status_code != 200:
        print(f"✗ Game page load failed: {response.status_code}")
        return False
    
    print(f"✓ Memory Match game page loads: 200 OK")
    
    checks = [
        ('game board', 'id="game-board"'),
        ('completion screen', 'id="completion-screen"'),
    ]
    
    for label, check_str in checks:
        if check_str in response.text:
            print(f"  ✓ {label}")
        else:
            print(f"  ✗ {label} NOT found")
            return False
    
    if 'memory_match.js' in response.text:
        print(f"  ✓ Game JavaScript loaded")
    else:
        print(f"  ✗ Game JavaScript not found")
        return False
    
    return True

def test_attention_test_game():
    """Test 13: Attention Test game loads"""
    print("\n[TEST 13] Attention Test Game - Display")
    print("-" * 70)
    
    response = SESSION.get(f'{BASE_URL}/games/attention-test')
    if response.status_code != 200:
        print(f"✗ Game page load failed: {response.status_code}")
        return False
    
    print(f"✓ Attention Test game page loads: 200 OK")
    
    checks = [
        ('attention grid', 'id="attention-grid"'),
        ('completion screen', 'id="completion-screen"'),
    ]
    
    for label, check_str in checks:
        if check_str in response.text:
            print(f"  ✓ {label}")
        else:
            print(f"  ✗ {label} NOT found")
            return False
    
    if 'attention_test.js' in response.text:
        print(f"  ✓ Game JavaScript loaded")
    else:
        print(f"  ✗ Game JavaScript not found")
        return False
    
    return True

def test_mood_button_states():
    """Test 14: Mood buttons show proper states"""
    print("\n[TEST 14] Mood Page - Button States & CSS")
    print("-" * 70)
    
    response = SESSION.get(f'{BASE_URL}/mood')
    
    # Check for CSS classes and states
    checks = [
        ('mood-button class', 'class="mood-button'),
        ('selected class definition', '.mood-button.selected'),
        ('btn-lg class', 'btn-lg'),
        ('data-mood attributes', 'data-mood='),
    ]
    
    all_pass = True
    for label, check_str in checks:
        if check_str in response.text:
            print(f"  ✓ {label}")
        else:
            print(f"  ✗ {label} NOT found")
            all_pass = False
    
    return all_pass

def test_safety_button_states():
    """Test 15: Safety button shows proper states and disabled state"""
    print("\n[TEST 15] Safety Page - Button States & CSS")
    print("-" * 70)
    
    response = SESSION.get(f'{BASE_URL}/safety')
    
    checks = [
        ('SOS button exists', 'id="sos-button"'),
        ('Emergency button class', 'btn-emergency'),
        ('Safety status card', 'safety-status-card'),
        ('Alert active class available', 'alert-active'),
    ]
    
    all_pass = True
    for label, check_str in checks:
        if check_str in response.text:
            print(f"  ✓ {label}")
        else:
            print(f"  ✗ {label} NOT found")
            all_pass = False
    
    return all_pass

def main():
    """Run all tests"""
    print("=" * 70)
    print("MEMORA PATIENT DASHBOARD - MOOD, SAFETY & GAMES VERIFICATION")
    print("=" * 70)
    
    tests = [
        ('Patient login', login_patient),
        ('Mood page loads', test_mood_page_loads),
        ('Mood submission', test_mood_submission),
        ('Mood retrieval', test_mood_retrieval),
        ('Mood history', test_mood_history),
        ('Safety page loads', test_safety_page_loads),
        ('Safety status', test_safety_status),
        ('SOS trigger', test_sos_trigger),
        ('Caregiver sees alert', test_caregiver_sees_alert),
        ('Game hub images', test_game_hub_images),
        ('Photo/Name Match images', test_photo_name_match_game_images),
        ('Who Is This images', test_who_is_this_game_images),
        ('Memory Match display', test_memory_match_game),
        ('Attention Test display', test_attention_test_game),
        ('Mood button states', test_mood_button_states),
        ('Safety button states', test_safety_button_states),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} - EXCEPTION: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed}/{total} tests passed ({int(passed*100/total)}%)")
    print("=" * 70)
    
    if passed == total:
        print("🎉 ALL PATIENT DASHBOARD FEATURES VERIFIED!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")

if __name__ == '__main__':
    main()
