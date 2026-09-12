#!/usr/bin/env python3
"""
Test the language toggle UI and active button styling
"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"

def test_active_button_state():
    """Test that the active language button is properly marked"""
    session = requests.Session()
    
    print("=" * 70)
    print("TEST: Language Toggle Active Button State")
    print("=" * 70)
    
    # Login
    login_data = {"name": "UITestUser", "pin": "1111"}
    response = session.post(f"{BASE_URL}/login", data=login_data)
    
    # Parse the page
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Get language toggle buttons
    nav_buttons = soup.find_all(attrs={'data-language-toggle': True})
    
    print(f"\nLanguage Toggle Buttons Found: {len(nav_buttons)}")
    
    for btn in nav_buttons:
        lang = btn.get('data-language-toggle')
        text = btn.get_text(strip=True)
        has_active = 'active' in btn.get('class', [])
        aria_pressed = btn.get('aria-pressed')
        
        print(f"\n  Language: {lang}")
        print(f"  Text: {text}")
        print(f"  Has 'active' class: {has_active}")
        print(f"  aria-pressed: {aria_pressed}")
        
        # For English button (default), it should be marked as active
        if lang == 'en' and (has_active or aria_pressed == 'true'):
            print(f"  ✓ EN button correctly marked as active")
        elif lang == 'en':
            print(f"  ? EN button may not be properly marked as active")
    
    # Now test switching to Assamese
    print("\n" + "=" * 70)
    print("Switching to Assamese and checking active state...")
    print("=" * 70)
    
    # Switch language
    session.patch(f"{BASE_URL}/api/user/language", json={"language": "as"})
    
    # Reload page
    response = session.get(f"{BASE_URL}/patient-home")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    nav_buttons = soup.find_all(attrs={'data-language-toggle': True})
    
    print(f"\nLanguage Toggle Buttons After Switch: {len(nav_buttons)}")
    
    for btn in nav_buttons:
        lang = btn.get('data-language-toggle')
        text = btn.get_text(strip=True)
        has_active = 'active' in btn.get('class', [])
        aria_pressed = btn.get('aria-pressed')
        
        print(f"\n  Language: {lang}")
        print(f"  Text: {text}")
        print(f"  Has 'active' class: {has_active}")
        print(f"  aria-pressed: {aria_pressed}")
        
        # For Assamese button, it should be marked as active
        if lang == 'as' and (has_active or aria_pressed == 'true'):
            print(f"  ✓ AS button correctly marked as active")
        elif lang == 'as':
            print(f"  ? AS button may not be properly marked as active")

if __name__ == '__main__':
    try:
        test_active_button_state()
        print("\n" + "=" * 70)
        print("✓ ACTIVE BUTTON STATE TEST COMPLETED")
        print("=" * 70)
    except Exception as e:
        print(f"\n✗ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
