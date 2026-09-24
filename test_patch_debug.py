#!/usr/bin/env python3
import requests

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

# Step 1: Login
print("Step 1: Login")
login_resp = session.post(f"{BASE_URL}/login", data={"name": "TestUser", "pin": "1"})
print(f"  Status: {login_resp.status_code}")
print(f"  URL after redirect: {login_resp.url}")
print(f"  Cookies: {session.cookies}")

# Step 2: Try PATCH
print("\nStep 2: Try PATCH /api/user/language")
patch_resp = session.patch(f"{BASE_URL}/api/user/language", json={"language": "as"})
print(f"  Status: {patch_resp.status_code}")
print(f"  Content-Type: {patch_resp.headers.get('Content-Type')}")

# Check if response is JSON or HTML
if patch_resp.status_code == 200:
    try:
        data = patch_resp.json()
        print(f"  JSON response: {data}")
    except:
        print(f"  Response is NOT JSON. First 200 chars: {patch_resp.text[:200]}")
