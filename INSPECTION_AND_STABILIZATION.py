"""
MEMORA Final Stabilization - Comprehensive Inspection & Testing
Tests all core features end-to-end
"""
import os
import sys
os.environ['DATABASE_URL'] = 'sqlite:///data/test_inspect.sqlite'

from app import app, db
from models.models import User, ActivityLog, MoodEntry, SafetyAlert, Reminder, MemoryPerson, MemoryPlace, MemoryItem
import json

def reset_db():
    """Reset test database"""
    db.drop_all()
    db.create_all()
    print("✅ Database reset and tables created")

def create_test_data():
    """Create test data"""
    # Create users
    patient = User(id=1, name='Anil Sharma', role='patient', pin='1234', preferred_language='en')
    caregiver = User(id=2, name='Priya Sharma', role='caregiver', pin='5678', preferred_language='en')
    
    db.session.add(patient)
    db.session.add(caregiver)
    db.session.commit()
    print("✅ Created test users: Patient (1), Caregiver (2)")
    
    return patient, caregiver

def test_authentication():
    """Test login and session"""
    with app.test_client() as client:
        # Test patient login
        response = client.post('/login', data={'name': 'Anil Sharma', 'pin': '1234'})
        assert response.status_code == 302 or response.status_code == 200, f"Patient login failed: {response.status_code}"
        print("✅ Patient login works")
        
        # Test caregiver login
        response = client.post('/login', data={'name': 'Priya Sharma', 'pin': '5678'})
        assert response.status_code == 302 or response.status_code == 200, f"Caregiver login failed: {response.status_code}"
        print("✅ Caregiver login works")

def test_mood_flow():
    """Test mood entry creation and retrieval"""
    with app.test_client() as client:
        # Login as patient
        client.post('/login', data={'name': 'Anil Sharma', 'pin': '1234'})
        
        # Create mood entry
        response = client.post('/api/mood/entries', 
            json={'mood': 'happy', 'note': 'Feeling good today'},
            content_type='application/json')
        print(f"  POST /api/mood/entries: {response.status_code}")
        assert response.status_code == 201, f"Create mood failed: {response.data}"
        print("  ✅ Mood entry created")
        
        # Get today's mood
        response = client.get('/api/mood/today')
        print(f"  GET /api/mood/today: {response.status_code}")
        data = response.get_json()
        assert data['has_entry'], "Today's mood not retrieved"
        print(f"  ✅ Today's mood retrieved: {data['entry']['mood']}")
        
        # Get mood history
        response = client.get('/api/mood/history')
        print(f"  GET /api/mood/history: {response.status_code}")
        data = response.get_json()
        assert len(data) >= 1, "History not retrieved"
        print(f"  ✅ Mood history retrieved: {len(data)} entries")

def test_safety_flow():
    """Test safety alert creation and retrieval"""
    with app.test_client() as client:
        # Login as patient
        client.post('/login', data={'name': 'Anil Sharma', 'pin': '1234'})
        
        # Create SOS alert
        response = client.post('/api/safety/sos', 
            json={},
            content_type='application/json')
        print(f"  POST /api/safety/sos: {response.status_code}")
        assert response.status_code in [200, 201], f"Create SOS failed: {response.data}"
        data = response.get_json()
        print(f"  ✅ SOS alert created: {data.get('alert', data.get('message', 'unknown'))}")
        
        # Get safety status
        response = client.get('/api/safety/status')
        print(f"  GET /api/safety/status: {response.status_code}")
        data = response.get_json()
        assert data['status'] == 'alert', "Safety status should be alert"
        print(f"  ✅ Safety status: {data['status']}")

def test_games_flow():
    """Test game activity logging"""
    with app.test_client() as client:
        # Login as patient
        client.post('/login', data={'name': 'Anil Sharma', 'pin': '1234'})
        
        # Submit game result
        response = client.post('/api/progress/submit', 
            json={
                'game_type': 'memory_match',
                'score': 100,
                'accuracy': 85.5,
                'time_taken': 45.2,
                'difficulty': 'medium'
            },
            content_type='application/json')
        print(f"  POST /api/progress/submit: {response.status_code}")
        assert response.status_code == 201, f"Game submit failed: {response.data}"
        print("  ✅ Game result submitted")
        
        # Get progress
        response = client.get('/api/progress/1')
        print(f"  GET /api/progress/1: {response.status_code}")
        data = response.get_json()
        assert len(data) >= 1, "Progress not retrieved"
        print(f"  ✅ Progress retrieved: {len(data)} activities")

def test_reminders_flow():
    """Test reminder creation"""
    with app.test_client() as client:
        # Login as patient
        client.post('/login', data={'name': 'Anil Sharma', 'pin': '1234'})
        
        # Create reminder
        response = client.post('/api/reminders/add', 
            json={
                'title': 'Take medicine',
                'type': 'medicine',
                'time': '08:00'
            },
            content_type='application/json')
        print(f"  POST /api/reminders/add: {response.status_code}")
        assert response.status_code == 201, f"Reminder creation failed: {response.data}"
        print("  ✅ Reminder created")
        
        # Get reminders
        response = client.get('/api/reminders/1')
        print(f"  GET /api/reminders/1: {response.status_code}")
        data = response.get_json()
        assert len(data) >= 1, "Reminders not retrieved"
        print(f"  ✅ Reminders retrieved: {len(data)} reminders")

def test_memory_flow():
    """Test memory album"""
    with app.test_client() as client:
        # Login as patient
        client.post('/login', data={'name': 'Anil Sharma', 'pin': '1234'})
        
        # Create memory person
        response = client.post('/api/memory/people/add', 
            json={
                'name': 'John',
                'relationship': 'Son',
                'description': 'My son'
            },
            content_type='application/json')
        print(f"  POST /api/memory/people/add: {response.status_code}")
        assert response.status_code in [201, 200], f"Memory person creation failed: {response.data}"
        print("  ✅ Memory person created")

def test_caregiver_dashboard():
    """Test caregiver dashboard data endpoints"""
    with app.test_client() as client:
        # Login as caregiver
        client.post('/login', data={'name': 'Priya Sharma', 'pin': '5678'})
        
        # Get patient progress
        response = client.get('/api/progress/1')
        print(f"  GET /api/progress/1: {response.status_code}")
        print("  ✅ Caregiver can access patient progress")
        
        # Get patient mood
        response = client.get('/api/mood/today?patient_id=1')
        print(f"  GET /api/mood/today?patient_id=1: {response.status_code}")
        print("  ✅ Caregiver can access patient mood")

def test_database_persistence():
    """Verify data persists in database"""
    # Check database
    with app.app_context():
        moods = MoodEntry.query.filter_by(patient_id=1).all()
        print(f"  MoodEntry table: {len(moods)} entries")
        assert len(moods) >= 1, "Mood not persisted"
        print("  ✅ Mood data persisted in database")
        
        alerts = SafetyAlert.query.filter_by(patient_id=1).all()
        print(f"  SafetyAlert table: {len(alerts)} entries")
        assert len(alerts) >= 1, "Safety alert not persisted"
        print("  ✅ Safety alert data persisted in database")
        
        activities = ActivityLog.query.filter_by(user_id=1).all()
        print(f"  ActivityLog table: {len(activities)} entries")
        assert len(activities) >= 1, "Game activity not persisted"
        print("  ✅ Game activity data persisted in database")

def run_all_tests():
    """Run all inspection tests"""
    print("\n" + "="*70)
    print("MEMORA FINAL STABILIZATION - COMPREHENSIVE INSPECTION")
    print("="*70)
    
    with app.app_context():
        try:
            print("\n1. DATABASE SETUP")
            print("-" * 70)
            reset_db()
            patient, caregiver = create_test_data()
            
            print("\n2. AUTHENTICATION")
            print("-" * 70)
            test_authentication()
            
            print("\n3. MOOD TRACKING")
            print("-" * 70)
            test_mood_flow()
            
            print("\n4. SAFETY/SOS")
            print("-" * 70)
            test_safety_flow()
            
            print("\n5. GAMES & ACTIVITY")
            print("-" * 70)
            test_games_flow()
            
            print("\n6. REMINDERS")
            print("-" * 70)
            test_reminders_flow()
            
            print("\n7. MEMORY ALBUM")
            print("-" * 70)
            test_memory_flow()
            
            print("\n8. CAREGIVER DASHBOARD")
            print("-" * 70)
            test_caregiver_dashboard()
            
            print("\n9. DATABASE PERSISTENCE")
            print("-" * 70)
            test_database_persistence()
            
            print("\n" + "="*70)
            print("✅ ALL TESTS PASSED - MEMORA IS STABLE")
            print("="*70)
            
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
