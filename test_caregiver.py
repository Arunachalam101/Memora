#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

print("Testing Caregiver Dashboard Flow:\n")

# Step 1: Login as caregiver
print("1. Login as Anil Sharma (caregiver)...")
response = session.post(f"{BASE_URL}/login", data={"name": "Anil Sharma", "pin": "5678"})
print(f"   Status: {response.status_code}")
print(f"   Redirected to: {response.url}")

# Step 2: Test /api/users/patients endpoint
print("\n2. Test /api/users/patients endpoint...")
response = session.get(f"{BASE_URL}/api/users/patients")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Patients: {json.dumps(data, indent=2)}")
else:
    print(f"   Response: {response.text}")

# Step 3: Test /api/progress/1 endpoint
print("\n3. Test /api/progress/1 endpoint (get patient activity)...")
response = session.get(f"{BASE_URL}/api/progress/1")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Activity count: {len(data) if isinstance(data, list) else 'Error'}")
    if isinstance(data, list) and len(data) > 0:
        print(f"   First entry: {json.dumps(data[0], indent=2)}")
else:
    print(f"   Response: {response.text}")

# Step 4: Access caregiver_dashboard page
print("\n4. Access caregiver_dashboard page...")
response = session.get(f"{BASE_URL}/caregiver_dashboard")
print(f"   Status: {response.status_code}")
if response.status_code == 200 and 'Caregiver' in response.text:
    print("   ✅ Caregiver dashboard loads successfully")
else:
    print(f"   ❌ Issue loading dashboard")

print("\nAll tests completed!")
