#!/usr/bin/env python3
"""
Test script for Phase 8: Regional Language Toggle
Verifies i18n implementation with login and language switching
"""

import sys
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"

def test_login_and_navbar():
    """Test that language toggle appears in navbar after login"""
    session = requests.Session()
    
    print("=" * 60)
    print("TEST 1: Login and Check Navbar")
    print("=" * 60)
    
    # Step 1: Login
    login_data = {"name": "TestUser123", "pin": "1234"}
    response = session.post(f"{BASE_URL}/login", data=login_data)
    
    print(f"✓ Login request sent: {response.status_code}")
    
    # Step 2: Follow redirect to patient home
    if response.status_code == 200:
        print("✓ Logged in successfully, loading patient_home")
        # The response should be the patient_home page after redirect
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for navbar
        navbar = soup.find('nav', class_='navbar')
        if navbar:
            print("✓ Navbar found on page")
            
            # Check for language toggle buttons
            lang_buttons = navbar.find_all(attrs={'data-language-toggle': True})
            print(f"✓ Found {len(lang_buttons)} language toggle buttons")
            
            for btn in lang_buttons:
                lang = btn.get('data-language-toggle')
                text = btn.get_text(strip=True)
                print(f"  - Button: {text} (data-language-toggle={lang})")
            
            # Check for i18n keys
            i18n_elements = navbar.find_all(attrs={'data-i18n-key': True})
            print(f"✓ Found {len(i18n_elements)} elements with i18n-key in navbar")
            
            for elem in i18n_elements[:5]:  # Show first 5
                key = elem.get('data-i18n-key')
                text = elem.get_text(strip=True)
                print(f"  - {key}: {text}")
        else:
            print("✗ Navbar NOT found on page")
            print("Page content preview:")
            print(response.text[:500])
    else:
        print(f"✗ Login failed with status code: {response.status_code}")
        print("Response:")
        print(response.text[:500])

def test_i18n_files():
    """Test that translation JSON files are accessible"""
    print("\n" + "=" * 60)
    print("TEST 2: Check Translation Files")
    print("=" * 60)
    
    for lang in ['en', 'as']:
        url = f"{BASE_URL}/static/i18n/{lang}.json"
        response = requests.get(url)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✓ {lang}.json loaded successfully")
                print(f"  - Total keys: {len(data)}")
                print(f"  - Sample keys: {list(data.keys())[:5]}")
            except:
                print(f"✗ {lang}.json is not valid JSON")
        else:
            print(f"✗ {lang}.json not found (status: {response.status_code})")

def test_i18n_js():
    """Test that i18n.js script is loadable"""
    print("\n" + "=" * 60)
    print("TEST 3: Check i18n.js Script")
    print("=" * 60)
    
    url = f"{BASE_URL}/static/js/i18n.js"
    response = requests.get(url)
    
    if response.status_code == 200:
        print("✓ i18n.js loaded successfully")
        if "loadLanguage" in response.text:
            print("✓ loadLanguage function found")
        if "I18N =" in response.text or "window.I18N" in response.text:
            print("✓ window.I18N API found")
        if "localStorage" in response.text:
            print("✓ localStorage implementation found")
    else:
        print(f"✗ i18n.js not found (status: {response.status_code})")

if __name__ == '__main__':
    try:
        test_i18n_files()
        test_i18n_js()
        test_login_and_navbar()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS COMPLETED")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
