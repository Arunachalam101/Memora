"""Debug script to check HTML responses"""
import requests

# Login
session = requests.Session()
r = session.post('http://localhost:5000/login', data={'pin': '1234'})
print(f'Login: {r.status_code}')

# Get mood page
print("\n=== MOOD PAGE ===")
r = session.get('http://localhost:5000/mood')
print(f'Status: {r.status_code}')
print(f'Content length: {len(r.text)} bytes')
print('\nFirst 1000 chars:')
print(r.text[:1000])

# Check for key elements
elements = [
    'mood-button',
    'save-mood-btn',
    'clear-mood-btn',
    'mood-selector',
]
print('\nElements found:')
for elem in elements:
    found = elem in r.text
    status = '✓' if found else '✗'
    print(f"{status} {elem}")

# Get safety page
print("\n=== SAFETY PAGE ===")
r = session.get('http://localhost:5000/safety')
print(f'Status: {r.status_code}')
print(f'Content length: {len(r.text)} bytes')
print('\nFirst 1000 chars:')
print(r.text[:1000])

elements = [
    'sos-button',
    'safety-status-card',
    'emergency-button-container',
]
print('\nElements found:')
for elem in elements:
    found = elem in r.text
    status = '✓' if found else '✗'
    print(f"{status} {elem}")

# Get games page
print("\n=== GAMES PAGE ===")
r = session.get('http://localhost:5000/games')
print(f'Status: {r.status_code}')
print(f'Content length: {len(r.text)} bytes')
print('\nFirst 1000 chars:')
print(r.text[:1000])

# Check routes
print("\n=== TESTING GAME ROUTES ===")
games = [
    '/games/memory-match',
    '/games/attention-test',
    '/games/photo-name-match',
    '/games/who-is-this',
]

for game_path in games:
    r = session.get(f'http://localhost:5000{game_path}')
    print(f"{game_path}: {r.status_code}")
