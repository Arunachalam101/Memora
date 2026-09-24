#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

print("Testing Caregiver Dashboard Page Load:\n")

# Step 1: Login as caregiver
print("1. Login as Anil Sharma (caregiver)...")
response = session.post(f"{BASE_URL}/login", data={"name": "Anil Sharma", "pin": "5678"})
print(f"   Status: {response.status_code}")

# Step 2: Load caregiver dashboard page
print("\n2. Load caregiver-dashboard page...")
response = session.get(f"{BASE_URL}/caregiver-dashboard")
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for patient-select element
    patient_select = soup.find('select', {'id': 'patient-select'})
    if patient_select:
        print("   ✅ Patient selector element found")
        option = patient_select.find('option')
        if option:
            print(f"   Default option text: {option.get_text()}")
    
    # Check for script tags
    scripts = soup.find_all('script', {'src': True})
    script_files = [s['src'] for s in scripts]
    print(f"\n   Loaded scripts:")
    for script in script_files:
        if 'dashboard_chart' in script or 'reminders' in script or 'error_handler' in script:
            print(f"   ✅ {script}")
        else:
            print(f"      {script}")
    
    # Check for sessionStorage or session variables
    inline_scripts = soup.find_all('script')
    print(f"\n   Checking inline scripts:")
    for script in inline_scripts:
        if script.string and 'currentUserId' in script.string:
            print(f"   ✅ currentUserId variable found: {script.string[:100]}")
        if script.string and 'currentUserRole' in script.string:
            print(f"   ✅ currentUserRole variable found: {script.string[:100]}")
    
    # Check page elements
    print(f"\n   Page elements:")
    overview = soup.find('div', {'class': 'patient-overview-section'})
    if overview:
        print("   ✅ Patient overview section found")
    
    activity = soup.find('div', {'class': 'activity-logs-section'})
    if activity:
        print("   ✅ Activity logs section found")
else:
    print(f"   ❌ Failed to load page")

print("\nPage load test completed!")
