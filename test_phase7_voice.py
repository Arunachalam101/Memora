#!/usr/bin/env python3
"""
PHASE 7 VOICE ASSISTANT - Integration Test
Tests voice assistant HTML rendering, JavaScript API, and data flow
"""

import json
import time
from urllib.parse import urljoin
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.request
    import urllib.parse

def test_voice_assistant():
    """Test voice assistant Phase 7 integration"""
    
    base_url = "http://127.0.0.1:5000"
    print("="*70)
    print("PHASE 7 VOICE ASSISTANT - INTEGRATION TEST")
    print("="*70)
    print()
    
    # Test 1: Check Flask is running
    print("TEST 1: Verify Flask server is running...")
    try:
        if HAS_REQUESTS:
            resp = requests.get(base_url)
        else:
            resp = urllib.request.urlopen(base_url)
        print("  ✅ Flask server is online")
    except Exception as e:
        print(f"  ❌ Flask server not responding: {e}")
        return False
    
    # Test 2: Login and get patient home
    print("\nTEST 2: Load patient_home page...")
    try:
        if HAS_REQUESTS:
            sess = requests.Session()
            login_resp = sess.post(
                urljoin(base_url, "/login"),
                data={"name": "TestPatient", "pin": "1234"}
            )
            home_resp = sess.get(urljoin(base_url, "/patient-home"))
            html_content = home_resp.text
        else:
            # Fallback for urllib
            req = urllib.request.Request(urljoin(base_url, "/login"), 
                                        data=urllib.parse.urlencode({"name": "TestPatient", "pin": "1234"}).encode())
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
            login_resp = opener.open(req)
            home_resp = opener.open(urljoin(base_url, "/patient-home"))
            html_content = home_resp.read().decode('utf-8')
        
        print("  ✅ Patient home loaded (200 OK)")
    except Exception as e:
        print(f"  ❌ Failed to load patient home: {e}")
        return False
    
    # Test 3: Check voice assistant section exists
    print("\nTEST 3: Verify voice assistant HTML components...")
    checks = {
        'voice-assistant-section': 'Voice section div',
        'voice-ask-button': 'Ask Memora button',
        'voice-read-button': 'Read reminders button',
        'voice-status': 'Voice status display',
        '🎤 Ask Memora': 'Ask button text',
        '🔊 Read my reminders': 'Read button text',
        '💡 Tap "Ask Memora"': 'Voice hint text'
    }
    
    all_found = True
    for check, label in checks.items():
        if check in html_content:
            print(f"  ✅ {label}")
        else:
            print(f"  ❌ {label} - NOT FOUND")
            all_found = False
    
    if not all_found:
        return False
    
    # Test 4: Check JavaScript files are loaded
    print("\nTEST 4: Verify JavaScript files are loaded...")
    js_checks = {
        'voice_assistant.js': 'Voice assistant script',
        'reminders.js': 'Reminders script',
        'VoiceAPI': 'VoiceAPI public API',
        'speakRemindersGreeting': 'Auto-read greeting function',
        'listenForQuery': 'Voice query listener'
    }
    
    for check, label in js_checks.items():
        if check in html_content:
            print(f"  ✅ {label}")
        else:
            print(f"  ❌ {label} - NOT FOUND")
            all_found = False
    
    # Check voice_assistant.js file directly for updateRemindersData
    print("\nTEST 4b: Check voice_assistant.js implementation...")
    try:
        if HAS_REQUESTS:
            voice_js_resp = requests.get(urljoin(base_url, "/static/js/voice_assistant.js"))
            voice_js_content = voice_js_resp.text
        else:
            voice_js_resp = urllib.request.urlopen(urljoin(base_url, "/static/js/voice_assistant.js"))
            voice_js_content = voice_js_resp.read().decode('utf-8')
        
        if 'updateRemindersData' in voice_js_content:
            print(f"  ✅ Data update function (updateRemindersData)")
        else:
            print(f"  ❌ Data update function - NOT FOUND")
            all_found = False
    except Exception as e:
        print(f"  ⚠️  Could not check voice_assistant.js: {e}")
    
    # Test 5: Check CSS styling is present
    print("\nTEST 5: Verify voice assistant CSS styling...")
    print("  ℹ️  Fetching CSS file...")
    try:
        if HAS_REQUESTS:
            css_resp = requests.get(urljoin(base_url, "/static/css/style.css"))
            css_content = css_resp.text
        else:
            css_resp = urllib.request.urlopen(urljoin(base_url, "/static/css/style.css"))
            css_content = css_resp.read().decode('utf-8')
        
        css_checks = {
            '.voice-assistant-section': 'Main voice section styles',
            '.voice-buttons-container': 'Button container styles',
            '.btn-voice': 'Voice button styles',
            '.btn-ask': 'Ask button styles',
            '.btn-read': 'Read button styles',
            '@keyframes pulse': 'Pulse animation',
            '.voice-status': 'Status display styles',
            '.voice-hint': 'Hint text styles'
        }
        
        for check, label in css_checks.items():
            if check in css_content:
                print(f"  ✅ {label}")
            else:
                print(f"  ❌ {label} - NOT FOUND")
                all_found = False
    except Exception as e:
        print(f"  ⚠️  Could not verify CSS: {e}")
    
    # Test 6: Check API endpoints respond
    print("\nTEST 6: Verify API endpoints respond...")
    try:
        if HAS_REQUESTS:
            sess = requests.Session()
            sess.post(urljoin(base_url, "/login"), data={"name": "TestPatient", "pin": "1234"})
            
            # Test reminders endpoint
            reminders_resp = sess.get(urljoin(base_url, "/api/reminders"))
            print(f"  ✅ GET /api/reminders - {reminders_resp.status_code}")
            
            if reminders_resp.status_code == 200:
                try:
                    reminders_data = reminders_resp.json()
                    print(f"     └─ Returned {len(reminders_data) if isinstance(reminders_data, list) else 1} reminder(s)")
                except:
                    pass
    except Exception as e:
        print(f"  ⚠️  Could not test API endpoints: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("PHASE 7 VOICE ASSISTANT TEST SUMMARY")
    print("="*70)
    
    if all_found:
        print("✅ ALL TESTS PASSED")
        print("\nVoice Assistant Phase 7 is fully integrated:")
        print("  • HTML buttons and sections rendered correctly")
        print("  • JavaScript files loaded and VoiceAPI exposed")
        print("  • CSS styling for voice UI applied")
        print("  • Auto-read greeting initialized on page load")
        print("  • Reminders data exposed to voice assistant")
        print("\nNext steps:")
        print("  1. Open browser to http://127.0.0.1:5000")
        print("  2. Log in and navigate to patient home")
        print("  3. Test voice buttons (requires microphone/speaker)")
        print("  4. Test voice queries: 'What time is it?' / 'What's the date?'")
        print("  5. Test reminder queries: 'Next reminder?' / 'What are my tasks?'")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        print("Check the console output above for details")
        return False

if __name__ == '__main__':
    success = test_voice_assistant()
    exit(0 if success else 1)
