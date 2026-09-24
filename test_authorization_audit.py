#!/usr/bin/env python3
"""Detailed authorization vulnerability test"""

from app import app
from models.models import db, User, MoodEntry

with app.app_context():
    db.create_all()
    
    # Clean up old test data
    db.session.query(MoodEntry).delete()
    db.session.query(User).filter(User.id >= 100).delete()
    db.session.commit()
    
    # Create test users
    patient1 = User(id=100, name='Patient 1', role='patient')
    patient2 = User(id=101, name='Patient 2', role='patient')
    db.session.add_all([patient1, patient2])
    db.session.commit()
    
    # Create mood for patient2 (not patient1)
    mood = MoodEntry(patient_id=101, mood='happy', note='Patient 2 mood')
    db.session.add(mood)
    db.session.commit()
    
    client = app.test_client()
    
    print("=" * 70)
    print("AUTHORIZATION VULNERABILITY TEST")
    print("=" * 70)
    
    # Test: Patient 1 tries to access their own mood
    with client.session_transaction() as sess:
        sess['user_id'] = 100
        sess['user_role'] = 'patient'
    resp = client.get('/api/mood/today')
    print(f"\n[TEST 1] Patient accesses own mood (/api/mood/today)")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.get_json()}")
    
    # Test: Patient 1 tries to access patient 2's mood by supplying patient_id
    with client.session_transaction() as sess:
        sess['user_id'] = 100
        sess['user_role'] = 'patient'
    resp = client.get('/api/mood/today?patient_id=101')
    print(f"\n[TEST 2] Patient tries to access another patient's mood (/api/mood/today?patient_id=101)")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.get_json()}")
    print(f"⚠️  SECURITY ISSUE: Patient got status {resp.status_code}, should be 403")
    
    # Test: Patient 1 tries to access history with another patient_id
    with client.session_transaction() as sess:
        sess['user_id'] = 100
        sess['user_role'] = 'patient'
    resp = client.get('/api/mood/history?patient_id=101')
    print(f"\n[TEST 3] Patient tries to access another patient's history (/api/mood/history?patient_id=101)")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.get_json()}")
    
    # Test: Patient 1 tries to access stats for another patient
    with client.session_transaction() as sess:
        sess['user_id'] = 100
        sess['user_role'] = 'patient'
    resp = client.get('/api/mood/stats?patient_id=101')
    print(f"\n[TEST 4] Patient tries to access another patient's stats (/api/mood/stats?patient_id=101)")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.get_json()}")
