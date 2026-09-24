#!/usr/bin/env python3
import requests

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

print("Testing Login Flow:\n")

# Test 1: Login as Priya Devi (patient)
print("1. Attempting login as Priya Devi (patient)...")
response = session.post(f"{BASE_URL}/login", data={"name": "Priya Devi", "pin": "1234"})
print(f"   Status: {response.status_code}")
print(f"   Redirected to: {response.url}")

if response.status_code == 200:
    print("   ✅ Login successful!")
    
    # Verify we can access patient home
    if "patient-home" in response.url:
        print("   ✅ Redirected to patient home page")
    
    # Test fetching a protected page
    home_response = session.get(f"{BASE_URL}/patient-home")
    if home_response.status_code == 200:
        print("   ✅ Can access patient home page")
    else:
        print(f"   ❌ Cannot access patient home: {home_response.status_code}")
else:
    print(f"   ❌ Login failed with status {response.status_code}")

print("\n2. Attempting login as Anil Sharma (caregiver)...")
session2 = requests.Session()
response = session2.post(f"{BASE_URL}/login", data={"name": "Anil Sharma", "pin": "5678"})
print(f"   Status: {response.status_code}")
print(f"   Redirected to: {response.url}")

if response.status_code == 200:
    print("   ✅ Login successful!")
    if "patient-home" in response.url:
        print("   ✅ Redirected to patient home page")
else:
    print(f"   ❌ Login failed with status {response.status_code}")

print("\n3. Testing Memory Album API...")
response = session.get(f"{BASE_URL}/api/memory/people?patient_id=1")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ Memory API working - Found {len(data)} people")
else:
    print(f"   ❌ Memory API error: {response.status_code}")

print("\nAll tests completed!")
