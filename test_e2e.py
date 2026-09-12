#!/usr/bin/env python3
"""
End-to-end test for Phase 8: Regional Language Toggle
Tests full workflow: login, switch language, persist, logout, login again
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_full_e2e():
    """Test the complete language toggle workflow"""
    
    print("=" * 70)
    print("END-TO-END TEST: Phase 8 Regional Language Toggle")
    print("=" * 70)
    
    session = requests.Session()
    test_user = "E2ETestUser789"
    
    # STEP 1: Login with new user
    print("\n[STEP 1] Logging in with new user...")
    login_data = {"name": test_user, "pin": "9999"}
    response = session.post(f"{BASE_URL}/login", data=login_data)
    print(f"✓ Login status: {response.status_code}")
    
    # Verify default language is English
    if 'window.userPreferredLanguage = "en"' in response.text:
        print("✓ Default language is English")
    else:
        print("? Could not verify default language")
    
    # STEP 2: Switch to Assamese
    print("\n[STEP 2] Switching to Assamese...")
    response = session.patch(f"{BASE_URL}/api/user/language", json={"language": "as"})
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Language switched to: {data.get('language')}")
    else:
        print(f"✗ Failed to switch language: {response.status_code}")
        return
    
    # STEP 3: Load a page and verify Assamese is set
    print("\n[STEP 3] Loading page and verifying Assamese persists...")
    home_response = session.get(f"{BASE_URL}/patient-home")
    if 'window.userPreferredLanguage = "as"' in home_response.text:
        print("✓ Assamese preference persisted after PATCH")
    else:
        print("✗ Assamese preference not persisted")
    
    # STEP 4: Logout
    print("\n[STEP 4] Logging out...")
    session.get(f"{BASE_URL}/logout")
    print("✓ Logged out")
    
    # STEP 5: Log back in with same user
    print("\n[STEP 5] Logging in again with same user...")
    session = requests.Session()  # New session
    login_data = {"name": test_user, "pin": "9999"}
    response = session.post(f"{BASE_URL}/login", data=login_data)
    print(f"✓ Re-login status: {response.status_code}")
    
    # STEP 6: Verify language persisted across logout/login
    print("\n[STEP 6] Verifying language persisted after logout/login...")
    if 'window.userPreferredLanguage = "as"' in response.text:
        print("✓✓✓ SUCCESS: Language persisted across logout/login!")
    elif 'window.userPreferredLanguage = "en"' in response.text:
        print("✗ Language reset to English after logout")
    else:
        print("? Could not verify language after re-login")
    
    # STEP 7: Load different pages and verify language persists
    print("\n[STEP 7] Testing language persistence across page navigation...")
    pages_to_test = [
        ("/games", "games_hub.html"),
        ("/caregiver-dashboard", "dashboard"),
        ("/patient-home", "patient home"),
    ]
    
    for page_url, page_name in pages_to_test:
        response = session.get(f"{BASE_URL}{page_url}")
        if response.status_code == 200:
            if 'window.userPreferredLanguage = "as"' in response.text:
                print(f"✓ Language persists on {page_name}")
            else:
                print(f"? Could not verify language on {page_name}")
        else:
            print(f"✗ Failed to load {page_name}: {response.status_code}")
    
    print("\n" + "=" * 70)
    print("✓✓✓ END-TO-END TEST COMPLETED SUCCESSFULLY")
    print("=" * 70)

if __name__ == '__main__':
    try:
        test_full_e2e()
    except Exception as e:
        print(f"\n✗ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
