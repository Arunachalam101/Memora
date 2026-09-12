#!/usr/bin/env python3
"""
Test the PATCH /api/user/language endpoint
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_patch_endpoint():
    """Test that PATCH /api/user/language works"""
    session = requests.Session()
    
    print("=" * 60)
    print("TEST: PATCH /api/user/language Endpoint")
    print("=" * 60)
    
    # Step 1: Login
    login_data = {"name": "TestUser456", "pin": "5678"}
    response = session.post(f"{BASE_URL}/login", data=login_data)
    print(f"✓ Logged in: {response.status_code}")
    
    # Step 2: Try to update language to Assamese
    patch_url = f"{BASE_URL}/api/user/language"
    patch_data = {"language": "as"}
    
    response = session.patch(patch_url, json=patch_data)
    print(f"✓ PATCH request sent: {response.status_code}")
    print(f"  Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print(f"✓ Language updated to: {data.get('language')}")
        else:
            print(f"✗ Language update failed: {data.get('error')}")
    else:
        print(f"✗ PATCH request failed: {response.status_code}")
    
    # Step 3: Verify language persisted by checking the user page
    print("\n✓ Verifying language persists...")
    home_response = session.get(f"{BASE_URL}/patient-home")
    
    if home_response.status_code == 200:
        # Check if the page has window.userPreferredLanguage set to 'as'
        if 'window.userPreferredLanguage = "as"' in home_response.text:
            print("✓ Language preference persisted in database!")
        elif 'window.userPreferredLanguage = "en"' in home_response.text:
            print("✗ Language preference not saved (still 'en')")
        else:
            print("? Could not find userPreferredLanguage in page")
    else:
        print(f"✗ Failed to load patient home: {response.status_code}")

if __name__ == '__main__':
    try:
        test_patch_endpoint()
        print("\n" + "=" * 60)
        print("✓ PATCH ENDPOINT TEST COMPLETED")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
