"""
Simple test to verify login persistence
"""
import requests

BASE_URL = 'http://localhost:5000'

# Use requests.Session which should handle cookies
session = requests.Session()

print("=== TEST 1: Login ===")
# Login with allow_redirects to follow the redirect
r = session.post(f'{BASE_URL}/login', data={'pin': '1234'}, allow_redirects=True)
print(f"Status: {r.status_code}")
print(f"Final URL: {r.url}")
print(f"Cookies in session: {dict(session.cookies)}")

# Check if we're on patient home
if 'Welcome back' in r.text or 'patient_home_subtitle' in r.text:
    print("✓ Successfully logged in and redirected to patient home")
else:
    print("✗ Not on patient home page")
    print(f"First 300 chars: {r.text[:300]}")

print("\n=== TEST 2: Access Mood Page ===")
r = session.get(f'{BASE_URL}/mood', allow_redirects=True)
print(f"Status: {r.status_code}")
print(f"Final URL: {r.url}")

if 'mood_heading' in r.text or 'Check Your Mood' in r.text:
    print("✓ Mood page loaded successfully")
    if 'mood-button' in r.text:
        print("✓ Mood buttons found")
else:
    print("✗ Mood page not loaded")
    print(f"Title: {r.text[r.text.find('<title>')+7:r.text.find('</title>')]}")

print("\n=== TEST 3: Create Mood Entry ===")
r = session.post(
    f'{BASE_URL}/api/mood/entries',
    json={'mood': 'happy', 'note': 'Test mood'},
    headers={'Content-Type': 'application/json'}
)
print(f"Status: {r.status_code}")
if r.status_code == 201:
    print("✓ Mood created successfully")
    data = r.json()
    print(f"  Mood: {data.get('entry', {}).get('mood')}")
else:
    print(f"✗ Failed to create mood: {r.text[:100]}")

print("\n=== TEST 4: Access Safety Page ===")
r = session.get(f'{BASE_URL}/safety', allow_redirects=True)
print(f"Status: {r.status_code}")

if 'safety_title' in r.text or 'Safety' in r.text:
    print("✓ Safety page loaded successfully")
    if 'sos-button' in r.text or 'emergency-button' in r.text:
        print("✓ SOS button found")
else:
    print("✗ Safety page not loaded")

print("\n=== TEST 5: Access Games Hub ===")
r = session.get(f'{BASE_URL}/games', allow_redirects=True)
print(f"Status: {r.status_code}")

if 'game-card' in r.text or 'games_hub_title' in r.text:
    print("✓ Games hub loaded successfully")
    
    # Check for specific games
    games = ['Memory Match', 'Attention Test', 'Photo / Name Match', 'Who Is This']
    for game in games:
        if game in r.text:
            print(f"  ✓ {game} found")

print("\n=== TEST 6: Access Game Pages ===")
games_routes = [
    ('/game/memory-match', 'Memory Match'),
    ('/game/attention-test', 'Attention Test'),
    ('/game/photo-name-match', 'Photo/Name Match'),
    ('/game/who-is-this', 'Who Is This'),
]

for route, name in games_routes:
    r = session.get(f'{BASE_URL}{route}', allow_redirects=True)
    print(f"{name}: {r.status_code}", end='')
    if r.status_code == 200:
        print(" ✓")
    else:
        print(" ✗")
