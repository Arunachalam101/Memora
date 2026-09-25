#!/usr/bin/env python3
"""
MEMORA - Comprehensive Feature Verification Script
Tests all major features end-to-end using HTTP requests
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"
SESSION = requests.Session()

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'

# Test counters
tests_passed = 0
tests_failed = 0

def print_header(text):
    print(f"\n{BLUE}{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}{END}\n")

def print_test(name):
    print(f"  > Testing: {name}...", end=" ", flush=True)

def print_pass(message=""):
    global tests_passed
    tests_passed += 1
    print(f"{GREEN}PASS{END}" + (f" - {message}" if message else ""))

def print_fail(message=""):
    global tests_failed
    tests_failed += 1
    print(f"{RED}FAIL{END}" + (f" - {message}" if message else ""))

def print_info(text):
    print(f"  i {text}")

def test_endpoint(method, path, expected_status=200, data=None, headers=None, description=""):
    """Test an API endpoint"""
    url = BASE_URL + path
    
    try:
        if method == 'GET':
            resp = SESSION.get(url, headers=headers)
        elif method == 'POST':
            resp = SESSION.post(url, json=data, headers=headers)
        elif method == 'PATCH':
            resp = SESSION.patch(url, json=data, headers=headers)
        elif method == 'PUT':
            resp = SESSION.put(url, json=data, headers=headers)
        else:
            return False, "Unknown method"
        
        if resp.status_code == expected_status:
            return True, resp.json() if resp.text else {}
        else:
            return False, f"Status {resp.status_code}, expected {expected_status}: {resp.text[:100]}"
    except Exception as e:
        return False, str(e)

# ========================================
# TEST SUITE
# ========================================

def test_database_connection():
    """Test if database is accessible"""
    print_header("DATABASE CONNECTION")
    
    print_test("Checking if data/memora.sqlite exists")
    import os
    if os.path.exists("data/memora.sqlite"):
        size = os.path.getsize("data/memora.sqlite")
        print_pass(f"Database file exists ({size} bytes)")
        return True
    else:
        print_fail("Database file not found")
        return False


def test_authentication():
    """Test login/logout flow"""
    print_header("AUTHENTICATION")
    
    # Test login with existing user
    print_test("Login with existing user (Priya Devi, PIN: 1234)")
    success, resp = test_endpoint('POST', '/login', 302, 
                                 data={'name': 'Priya Devi', 'pin': '1234'})
    if not success or SESSION.cookies.get('session') is None:
        print_fail("Session not created")
        return False
    else:
        print_pass("Session created")
    
    # Test patient home access
    print_test("Access /patient-home after login")
    success, resp = test_endpoint('GET', '/patient-home', 200)
    print_pass() if success else print_fail(resp)
    
    # Test logout
    print_test("Logout")
    success, resp = test_endpoint('GET', '/logout', 302)
    print_pass() if success else print_fail(resp)
    
    return True


def test_games():
    """Test all 4 games"""
    print_header("GAMES (4 GAMES TOTAL)")
    
    # Re-login
    SESSION.post(f"{BASE_URL}/login", data={'name': 'Priya Devi', 'pin': '1234'})
    
    games = [
        ('memory-match', 'Memory Match'),
        ('attention-test', 'Attention Test'),
        ('photo-name-match', 'Photo/Name Match'),
        ('who-is-this', 'Who Is This'),
    ]
    
    for game_id, game_name in games:
        print_test(f"Load {game_name} game")
        success, resp = test_endpoint('GET', f'/game/{game_id}', 200)
        print_pass() if success else print_fail(resp)
    
    # Test game logging
    print_test("Submit game result (Memory Match)")
    success, resp = test_endpoint('POST', '/api/games/log', 201,
                                 data={
                                     'game_type': 'memory_match',
                                     'score': 850,
                                     'accuracy': 91.5,
                                     'time_taken': 45.2,
                                     'difficulty': 'medium'
                                 })
    if success:
        print_pass(f"Game result logged (ID: {resp.get('id', '?')})")
    else:
        print_fail(resp)
    
    return True


def test_mood():
    """Test mood tracking"""
    print_header("MOOD TRACKING")
    
    # Re-login if needed
    if not SESSION.cookies.get('session'):
        SESSION.post(f"{BASE_URL}/login", data={'name': 'Priya Devi', 'pin': '1234'})
    
    user_id = 1
    
    # Create mood entry
    print_test("Create mood entry")
    success, resp = test_endpoint('POST', '/api/mood/entries', 201,
                                 data={
                                     'patient_id': user_id,
                                     'mood': 'very_happy',
                                     'note': 'Had a great day with family!'
                                 })
    if success:
        print_pass(f"Mood saved")
    else:
        print_fail(resp)
    
    # Get today's mood
    print_test("Get today's mood")
    success, resp = test_endpoint('GET', f'/api/mood/today?patient_id={user_id}', 200)
    if success:
        has_entry = resp.get('has_entry', False)
        if has_entry:
            mood = resp.get('entry', {}).get('mood', 'unknown')
            print_pass(f"Today's mood: {mood}")
        else:
            print_info("No mood entry for today")
    else:
        print_fail(resp)
    
    # Get mood history
    print_test("Get mood history (14 days)")
    success, resp = test_endpoint('GET', f'/api/mood/history?patient_id={user_id}&days=14', 200)
    if success:
        count = len(resp.get('entries', []))
        print_pass(f"Retrieved {count} mood entries")
    else:
        print_fail(resp)
    
    return True


def test_safety():
    """Test safety/SOS alerts"""
    print_header("SAFETY / SOS ALERTS")
    
    # Re-login if needed
    if not SESSION.cookies.get('session'):
        SESSION.post(f"{BASE_URL}/login", data={'name': 'Priya Devi', 'pin': '1234'})
    
    user_id = 1
    
    # Create SOS alert
    print_test("Create SOS alert")
    success, resp = test_endpoint('POST', '/api/safety/sos', 200,
                                 data={'patient_id': user_id})
    if success:
        print_pass(f"SOS alert created")
    else:
        print_fail(resp)
    
    # Get safety status
    print_test("Get safety status")
    success, resp = test_endpoint('GET', f'/api/safety/status?patient_id={user_id}', 200)
    if success:
        status = resp.get('status', 'unknown')
        alert = resp.get('active_alert')
        print_pass(f"Status: {status}, Alert: {'Active' if alert else 'None'}")
    else:
        print_fail(resp)
    
    # Get safety alerts (caregiver view)
    print_test("Get safety alerts (caregiver view)")
    success, resp = test_endpoint('GET', f'/api/safety/alerts?patient_id={user_id}', 200)
    if success:
        count = len(resp.get('alerts', []))
        print_pass(f"Retrieved {count} alert(s)")
    else:
        print_fail(resp)
    
    return True


def test_reminders():
    """Test reminder functionality"""
    print_header("REMINDERS")
    
    # Re-login if needed
    if not SESSION.cookies.get('session'):
        SESSION.post(f"{BASE_URL}/login", data={'name': 'Priya Devi', 'pin': '1234'})
    
    # Get reminders
    print_test("Get reminders for user")
    success, resp = test_endpoint('GET', '/api/reminders', 200)
    if success:
        count = len(resp)
        print_pass(f"Retrieved {count} reminder(s)")
    else:
        print_fail(resp)
    
    # Create reminder
    print_test("Create new reminder")
    success, resp = test_endpoint('POST', '/api/reminders', 201,
                                 data={
                                     'title': 'Take Medication',
                                     'type': 'medicine',
                                     'time': '14:30'
                                 })
    if success:
        reminder_id = resp.get('id')
        print_pass(f"Reminder created (ID: {reminder_id})")
    else:
        print_fail(resp)
    
    return True


def test_memory():
    """Test memory album"""
    print_header("MEMORY ALBUM")
    
    # Re-login if needed
    if not SESSION.cookies.get('session'):
        SESSION.post(f"{BASE_URL}/login", data={'name': 'Priya Devi', 'pin': '1234'})
    
    patient_id = 1
    
    # Get people
    print_test("Get memory people")
    success, resp = test_endpoint('GET', f'/api/memory/people?patient_id={patient_id}', 200)
    if success:
        count = len(resp)
        print_pass(f"Retrieved {count} people")
    else:
        print_fail(resp)
    
    # Get places
    print_test("Get memory places")
    success, resp = test_endpoint('GET', f'/api/memory/places?patient_id={patient_id}', 200)
    if success:
        count = len(resp)
        print_pass(f"Retrieved {count} places")
    else:
        print_fail(resp)
    
    # Get memories
    print_test("Get memory items")
    success, resp = test_endpoint('GET', f'/api/memory/items?patient_id={patient_id}', 200)
    if success:
        count = len(resp)
        print_pass(f"Retrieved {count} memories")
    else:
        print_fail(resp)
    
    return True


def test_progress():
    """Test progress tracking and difficulty"""
    print_header("PROGRESS TRACKING & ADAPTIVE DIFFICULTY")
    
    user_id = 1
    
    # Get progress
    print_test("Get user progress (all games)")
    success, resp = test_endpoint('GET', f'/api/progress/{user_id}', 200)
    if success:
        count = len(resp)
        print_pass(f"Retrieved {count} game session(s)")
    else:
        print_fail(resp)
    
    # Get difficulty
    print_test("Get recommended difficulty")
    success, resp = test_endpoint('GET', f'/api/difficulty/{user_id}', 200)
    if success:
        difficulty = resp.get('difficulty')
        print_pass(f"Difficulty: {difficulty}")
    else:
        print_fail(resp)
    
    return True


def test_caregiver_dashboard():
    """Test caregiver dashboard data endpoints"""
    print_header("CAREGIVER DASHBOARD")
    
    # Login as caregiver
    SESSION.post(f"{BASE_URL}/login", data={'name': 'Anil Sharma', 'pin': '5678'})
    
    # Get all patients
    print_test("Get all patients")
    success, resp = test_endpoint('GET', '/api/users/patients', 200)
    if success:
        count = len(resp)
        print_pass(f"Retrieved {count} patient(s)")
        if count > 0:
            print_info(f"First patient: {resp[0].get('name', '?')} (ID: {resp[0].get('id', '?')})")
    else:
        print_fail(resp)
    
    # Get patient progress
    patient_id = 1
    print_test(f"Get patient {patient_id} progress")
    success, resp = test_endpoint('GET', f'/api/progress/{patient_id}', 200)
    if success:
        count = len(resp)
        print_pass(f"Retrieved {count} game session(s)")
    else:
        print_fail(resp)
    
    # Get patient mood
    print_test(f"Get patient {patient_id} mood")
    success, resp = test_endpoint('GET', f'/api/mood/today?patient_id={patient_id}', 200)
    if success:
        has_entry = resp.get('has_entry', False)
        print_pass(f"Has mood entry: {has_entry}")
    else:
        print_fail(resp)
    
    # Get patient reminders
    print_test(f"Get patient {patient_id} reminders")
    success, resp = test_endpoint('GET', f'/api/reminders', 200)
    if success:
        count = len(resp)
        print_pass(f"Retrieved {count} reminder(s)")
    else:
        print_fail(resp)
    
    return True


def test_i18n():
    """Test internationalization"""
    print_header("INTERNATIONALIZATION (i18n)")
    
    # Check language files
    print_test("Check i18n language files")
    import os
    en_exists = os.path.exists("static/i18n/en.json")
    as_exists = os.path.exists("static/i18n/as.json")
    
    if en_exists and as_exists:
        # Load and verify content
        import json
        with open("static/i18n/en.json", encoding='utf-8') as f:
            en_data = json.load(f)
        with open("static/i18n/as.json", encoding='utf-8') as f:
            as_data = json.load(f)
        
        en_keys = len(en_data)
        as_keys = len(as_data)
        print_pass(f"EN: {en_keys} keys, AS: {as_keys} keys")
        
        # Check coverage
        missing = set(en_data.keys()) - set(as_data.keys())
        if missing:
            print_info(f"Assamese missing {len(missing)} key(s)")
        
        return True
    else:
        print_fail("Language files not found")
        return False


# ========================================
# MAIN EXECUTION
# ========================================

if __name__ == '__main__':
    print(f"\n{BLUE}{'='*70}{END}")
    print(f"{BLUE}MEMORA FEATURE VERIFICATION SUITE{END}".center(70))
    print(f"{BLUE}Comprehensive End-to-End Testing Framework{END}".center(70))
    print(f"{BLUE}{'='*70}{END}")
    
    print(f"\n{YELLOW}Prerequisites:{END}")
    print(f"  1. Flask server must be running: python app.py")
    print(f"  2. Database must exist at: data/memora.sqlite")
    print(f"  3. Server running on: {BASE_URL}")
    print(f"\n{YELLOW}Starting tests in 2 seconds...{END}")
    time.sleep(2)
    
    # Run all tests
    try:
        test_database_connection()
        test_authentication()
        test_games()
        test_mood()
        test_safety()
        test_reminders()
        test_memory()
        test_progress()
        test_caregiver_dashboard()
        test_i18n()
        
    except Exception as e:
        print(f"\n{RED}ERROR: Tests interrupted - {str(e)}{END}")
        import traceback
        traceback.print_exc()
    
    # Print summary
    print_header("TEST SUMMARY")
    
    total = tests_passed + tests_failed
    pass_rate = (tests_passed / total * 100) if total > 0 else 0
    
    print(f"  Total Tests: {total}")
    print(f"  {GREEN}Passed: {tests_passed}{END}")
    print(f"  {RED}Failed: {tests_failed}{END}")
    print(f"  Pass Rate: {pass_rate:.1f}%")
    
    if tests_failed == 0:
        print(f"\n{GREEN}ALL TESTS PASSED - MEMORA IS READY FOR DEPLOYMENT{END}\n")
    else:
        print(f"\n{RED}SOME TESTS FAILED - REVIEW RESULTS ABOVE{END}\n")
    
    exit(0 if tests_failed == 0 else 1)
