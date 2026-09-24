#!/usr/bin/env python3
from app import app
from models.models import User, db

with app.app_context():
    # Verify data exists
    patient = User.query.filter_by(name='Priya Devi').first()
    print(f'Patient found: {patient.name if patient else "NOT FOUND"} (ID: {patient.id if patient else "N/A"})')
    
    # Now test with test client
    with app.test_client() as client:
        # Login via POST
        response = client.post('/login', data={'name': 'Priya Devi', 'pin': '1234'})
        print(f'Login status: {response.status_code}')
        
        # Check if session is set
        with client.session_transaction() as sess:
            print(f'Session user_id: {sess.get("user_id")}')
        
        # Test fetching memory people
        response = client.get('/api/memory/people?patient_id=1')
        data = response.get_json()
        
        print('\n=== API TEST RESULTS ===\n')
        print(f'Status: {response.status_code}')
        
        if isinstance(data, list):
            print(f'Memory People: {len(data)} records')
            for person in data:
                print(f'  - {person["name"]} ({person["relationship"]})')
        else:
            print(f'Response: {data}')
        
        # Test memory places
        response = client.get('/api/memory/places?patient_id=1')
        data = response.get_json()
        
        if isinstance(data, list):
            print(f'\nMemory Places: {len(data)} records')
            for place in data:
                print(f'  - {place["name"]}')
        else:
            print(f'Places error: {data}')
        
        # Test memory items
        response = client.get('/api/memory/memories?patient_id=1')
        data = response.get_json()
        
        if isinstance(data, list):
            print(f'\nMemory Items: {len(data)} records')
            for item in data:
                print(f'  - {item["title"]}')
        else:
            print(f'Items error: {data}')
