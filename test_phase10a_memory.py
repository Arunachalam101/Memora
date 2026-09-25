"""
Test Suite for MEMORA Phase 10A - Memory Foundation
Tests for Memory Album API, Authorization, Photo Uploads, and Database Models
"""

import pytest
import json
import os
from pathlib import Path
from datetime import datetime, date

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from app import app, db
from models.models import User, MemoryPerson, MemoryPlace, MemoryItem, ActivityLog, Reminder
from utils.upload_handler import UploadHandler


@pytest.fixture
def client():
    """Create a test client with a temporary database"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def users(client):
    """Create test users: patient and caregiver"""
    with app.app_context():
        patient = User(
            name="Test Patient",
            role="patient",
            pin="1234",
            preferred_language="en"
        )
        caregiver = User(
            name="Test Caregiver",
            role="caregiver",
            pin="5678",
            preferred_language="en"
        )
        db.session.add(patient)
        db.session.add(caregiver)
        db.session.commit()
        
        return {
            'patient': patient,
            'caregiver': caregiver,
            'patient_id': patient.id,
            'caregiver_id': caregiver.id
        }


# ============================================================
# TESTS FOR MODELS
# ============================================================

class TestMemoryModels:
    """Test memory model creation and methods"""
    
    def test_memory_person_creation(self, users):
        """Test creating a MemoryPerson record"""
        with app.app_context():
            person = MemoryPerson(
                patient_id=users['patient_id'],
                name="John Doe",
                relationship="Son",
                description="Works in tech",
                photo="/uploads/memory/person_1.jpg"
            )
            db.session.add(person)
            db.session.commit()
            
            retrieved = MemoryPerson.query.filter_by(
                patient_id=users['patient_id'],
                name="John Doe"
            ).first()
            assert retrieved is not None
            assert retrieved.name == "John Doe"
            assert retrieved.relationship == "Son"
            assert retrieved.is_active == True
    
    def test_memory_person_to_dict(self, users):
        """Test MemoryPerson.to_dict() method"""
        with app.app_context():
            person = MemoryPerson(
                patient_id=users['patient_id'],
                name="Jane Doe",
                relationship="Daughter",
                description="Doctor"
            )
            db.session.add(person)
            db.session.commit()
            
            data = person.to_dict()
            assert data['name'] == "Jane Doe"
            assert data['relationship'] == "Daughter"
            assert 'created_at' in data
            assert 'updated_at' in data
    
    def test_memory_place_creation(self, users):
        """Test creating a MemoryPlace record"""
        with app.app_context():
            place = MemoryPlace(
                patient_id=users['patient_id'],
                name="Home",
                description="3-room apartment",
                photo="/uploads/memory/place_1.jpg"
            )
            db.session.add(place)
            db.session.commit()
            
            retrieved = MemoryPlace.query.first()
            assert retrieved.name == "Home"
            assert retrieved.is_active == True
    
    def test_memory_item_creation(self, users):
        """Test creating a MemoryItem record"""
        with app.app_context():
            today = date.today()
            memory = MemoryItem(
                patient_id=users['patient_id'],
                title="Family Reunion",
                description="Everyone gathered",
                memory_date=today,
                photo="/uploads/memory/memory_1.jpg"
            )
            db.session.add(memory)
            db.session.commit()
            
            retrieved = MemoryItem.query.first()
            assert retrieved.title == "Family Reunion"
            assert retrieved.memory_date == today
            assert retrieved.is_active == True
    
    def test_memory_item_to_dict_with_date(self, users):
        """Test MemoryItem.to_dict() with date field"""
        with app.app_context():
            today = date.today()
            memory = MemoryItem(
                patient_id=users['patient_id'],
                title="Birthday",
                memory_date=today
            )
            db.session.add(memory)
            db.session.commit()
            
            data = memory.to_dict()
            assert data['memory_date'] == today.isoformat()


# ============================================================
# TESTS FOR AUTHORIZATION
# ============================================================

class TestMemoryAuthorization:
    """Test authorization for memory API endpoints"""
    
    def test_unauthenticated_access(self, client, users):
        """Test that unauthenticated users get 401"""
        response = client.get(f'/api/memory/people?patient_id={users["patient_id"]}')
        assert response.status_code == 401
    
    def test_patient_can_view_own_memories(self, client, users):
        """Test that patient can view own memory data"""
        with client.session_transaction() as sess:
            sess['user_id'] = users['patient_id']
            sess['user_role'] = 'patient'
        
        with app.app_context():
            person = MemoryPerson(
                patient_id=users['patient_id'],
                name="Test",
                relationship="Test"
            )
            db.session.add(person)
            db.session.commit()
        
        response = client.get(f'/api/memory/people?patient_id={users["patient_id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
    
    def test_patient_can_edit_own_memories(self, client, users):
        """Test that patient CAN edit own memories (fixed authorization)"""
        with client.session_transaction() as sess:
            sess['user_id'] = users['patient_id']
            sess['user_role'] = 'patient'
        
        response = client.post(
            '/api/memory/people',
            data={
                'patient_id': users['patient_id'],
                'name': 'Test Person',
                'relationship': 'Test'
            }
        )
        assert response.status_code == 201  # Patient can create (after authorization fix)
    
    def test_caregiver_can_view_all_memories(self, client, users):
        """Test that caregiver can view patient memories"""
        with client.session_transaction() as sess:
            sess['user_id'] = users['caregiver_id']
            sess['user_role'] = 'caregiver'
        
        with app.app_context():
            person = MemoryPerson(
                patient_id=users['patient_id'],
                name="Test",
                relationship="Test"
            )
            db.session.add(person)
            db.session.commit()
        
        response = client.get(f'/api/memory/people?patient_id={users["patient_id"]}')
        assert response.status_code == 200
    
    def test_caregiver_can_edit_all_memories(self, client, users):
        """Test that caregiver can edit patient memories"""
        with client.session_transaction() as sess:
            sess['user_id'] = users['caregiver_id']
            sess['user_role'] = 'caregiver'
        
        response = client.post(
            '/api/memory/people',
            data={
                'patient_id': users['patient_id'],
                'name': 'Test Person',
                'relationship': 'Test Relationship'
            }
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Test Person'
    
    def test_caregiver_cannot_access_invalid_patient(self, client, users):
        """Test accessing non-existent patient returns 400"""
        with client.session_transaction() as sess:
            sess['user_id'] = users['caregiver_id']
            sess['user_role'] = 'caregiver'
        
        response = client.get('/api/memory/people?patient_id=invalid')
        assert response.status_code == 400


# ============================================================
# TESTS FOR PEOPLE API
# ============================================================

class TestMemoryPeopleAPI:
    """Test People endpoint CRUD operations"""
    
    def test_get_people_empty(self, client, users):
        """Test getting people when list is empty"""
        with client.session_transaction() as sess:
            sess['user_id'] = users['patient_id']
            sess['user_role'] = 'patient'
        
        response = client.get(f'/api/memory/people?patient_id={users["patient_id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []
    
    def test_get_people_with_data(self, client, users):
        """Test getting people with existing records"""
        with app.app_context():
            person = MemoryPerson(
                patient_id=users['patient_id'],
                name="John",
                relationship="Son"
            )
            db.session.add(person)
            db.session.commit()
        
        with client.session_transaction() as sess:
            sess['user_id'] = users['patient_id']
            sess['user_role'] = 'patient'
        
        response = client.get(f'/api/memory/people?patient_id={users["patient_id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['name'] == 'John'
    
    def test_create_person_minimal(self, client, users):
        """Test creating person with minimal required fields"""
        with client.session_transaction() as sess:
            sess['user_id'] = users['caregiver_id']
            sess['user_role'] = 'caregiver'
        
        response = client.post(
            '/api/memory/people',
            data={
                'patient_id': users['patient_id'],
                'name': 'Alice',
                'relationship': 'Sister'
            }
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Alice'
        assert data['relationship'] == 'Sister'
        assert data['description'] is None
    
    def test_create_person_with_description(self, client, users):
        """Test creating person with all fields"""
        with client.session_transaction() as sess:
            sess['user_id'] = users['caregiver_id']
            sess['user_role'] = 'caregiver'
        
        response = client.post(
            '/api/memory/people',
            data={
                'patient_id': users['patient_id'],
                'name': 'Bob',
                'relationship': 'Brother',
                'description': 'Works in Mumbai'
            }
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['description'] == 'Works in Mumbai'
    
    def test_create_person_missing_name(self, client, users):
        """Test creating person without name fails"""
        with client.session_transaction() as sess:
            sess['user_id'] = users['caregiver_id']
            sess['user_role'] = 'caregiver'
        
        response = client.post(
            '/api/memory/people',
            data={
                'patient_id': users['patient_id'],
                'relationship': 'Sister'
            }
        )
        assert response.status_code == 400
    
    def test_update_person(self, client, users):
        """Test updating a person record"""
        with app.app_context():
            person = MemoryPerson(
                patient_id=users['patient_id'],
                name="Original Name",
                relationship="Original"
            )
            db.session.add(person)
            db.session.commit()
            person_id = person.id
        
        with client.session_transaction() as sess:
            sess['user_id'] = users['caregiver_id']
            sess['user_role'] = 'caregiver'
        
        response = client.put(
            f'/api/memory/people/{person_id}',
            data={
                'patient_id': users['patient_id'],
                'name': 'Updated Name'
            }
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Updated Name'
    
    def test_delete_person(self, client, users):
        """Test deleting a person record"""
        with app.app_context():
            person = MemoryPerson(
                patient_id=users['patient_id'],
                name="To Delete",
                relationship="Test"
            )
            db.session.add(person)
            db.session.commit()
            person_id = person.id
        
        with client.session_transaction() as sess:
            sess['user_id'] = users['caregiver_id']
            sess['user_role'] = 'caregiver'
        
        response = client.delete(
            f'/api/memory/people/{person_id}?patient_id={users["patient_id"]}'
        )
        assert response.status_code == 200
        
        # Verify it's deleted
        with app.app_context():
            deleted = MemoryPerson.query.get(person_id)
            assert deleted is None


# ============================================================
# TESTS FOR PLACES API
# ============================================================

class TestMemoryPlacesAPI:
    """Test Places endpoint CRUD operations"""
    
    def test_get_places_empty(self, client, users):
        """Test getting places when list is empty"""
        with client.session_transaction() as sess:
            sess['user_id'] = users['patient_id']
            sess['user_role'] = 'patient'
        
        response = client.get(f'/api/memory/places?patient_id={users["patient_id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []
    
    def test_create_place(self, client, users):
        """Test creating a place"""
        with client.session_transaction() as sess:
            sess['user_id'] = users['caregiver_id']
            sess['user_role'] = 'caregiver'
        
        response = client.post(
            '/api/memory/places',
            data={
                'patient_id': users['patient_id'],
                'name': 'Home',
                'description': 'My house'
            }
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Home'
    
    def test_create_place_missing_name(self, client, users):
        """Test creating place without name fails"""
        with client.session_transaction() as sess:
            sess['user_id'] = users['caregiver_id']
            sess['user_role'] = 'caregiver'
        
        response = client.post(
            '/api/memory/places',
            data={
                'patient_id': users['patient_id'],
                'description': 'Somewhere'
            }
        )
        assert response.status_code == 400
    
    def test_update_place(self, client, users):
        """Test updating a place"""
        with app.app_context():
            place = MemoryPlace(
                patient_id=users['patient_id'],
                name="Original"
            )
            db.session.add(place)
            db.session.commit()
            place_id = place.id
        
        with client.session_transaction() as sess:
            sess['user_id'] = users['caregiver_id']
            sess['user_role'] = 'caregiver'
        
        response = client.put(
            f'/api/memory/places/{place_id}',
            data={
                'patient_id': users['patient_id'],
                'name': 'Updated'
            }
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Updated'
    
    def test_delete_place(self, client, users):
        """Test deleting a place"""
        with app.app_context():
            place = MemoryPlace(
                patient_id=users['patient_id'],
                name="To Delete"
            )
            db.session.add(place)
            db.session.commit()
            place_id = place.id
        
        with client.session_transaction() as sess:
            sess['user_id'] = users['caregiver_id']
            sess['user_role'] = 'caregiver'
        
        response = client.delete(
            f'/api/memory/places/{place_id}?patient_id={users["patient_id"]}'
        )
        assert response.status_code == 200


# ============================================================
# TESTS FOR MEMORIES API
# ============================================================

class TestMemoryMemoriesAPI:
    """Test Memories endpoint CRUD operations"""
    
    def test_get_memories_empty(self, client, users):
        """Test getting memories when list is empty"""
        with client.session_transaction() as sess:
            sess['user_id'] = users['patient_id']
            sess['user_role'] = 'patient'
        
        response = client.get(f'/api/memory/memories?patient_id={users["patient_id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []
    
    def test_create_memory(self, client, users):
        """Test creating a memory"""
        with client.session_transaction() as sess:
            sess['user_id'] = users['caregiver_id']
            sess['user_role'] = 'caregiver'
        
        response = client.post(
            '/api/memory/memories',
            data={
                'patient_id': users['patient_id'],
                'title': 'Birthday Party',
                'description': 'Had a great time'
            }
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == 'Birthday Party'
    
    def test_create_memory_with_date(self, client, users):
        """Test creating memory with optional date"""
        with client.session_transaction() as sess:
            sess['user_id'] = users['caregiver_id']
            sess['user_role'] = 'caregiver'
        
        response = client.post(
            '/api/memory/memories',
            data={
                'patient_id': users['patient_id'],
                'title': 'Anniversary',
                'memory_date': '2024-05-15'
            }
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['memory_date'] == '2024-05-15'
    
    def test_create_memory_invalid_date(self, client, users):
        """Test creating memory with invalid date format"""
        with client.session_transaction() as sess:
            sess['user_id'] = users['caregiver_id']
            sess['user_role'] = 'caregiver'
        
        response = client.post(
            '/api/memory/memories',
            data={
                'patient_id': users['patient_id'],
                'title': 'Bad Date',
                'memory_date': 'invalid-date'
            }
        )
        assert response.status_code == 400
    
    def test_update_memory(self, client, users):
        """Test updating a memory"""
        with app.app_context():
            memory = MemoryItem(
                patient_id=users['patient_id'],
                title="Original Title"
            )
            db.session.add(memory)
            db.session.commit()
            memory_id = memory.id
        
        with client.session_transaction() as sess:
            sess['user_id'] = users['caregiver_id']
            sess['user_role'] = 'caregiver'
        
        response = client.put(
            f'/api/memory/memories/{memory_id}',
            data={
                'patient_id': users['patient_id'],
                'title': 'Updated Title'
            }
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == 'Updated Title'
    
    def test_delete_memory(self, client, users):
        """Test deleting a memory"""
        with app.app_context():
            memory = MemoryItem(
                patient_id=users['patient_id'],
                title="To Delete"
            )
            db.session.add(memory)
            db.session.commit()
            memory_id = memory.id
        
        with client.session_transaction() as sess:
            sess['user_id'] = users['caregiver_id']
            sess['user_role'] = 'caregiver'
        
        response = client.delete(
            f'/api/memory/memories/{memory_id}?patient_id={users["patient_id"]}'
        )
        assert response.status_code == 200


# ============================================================
# TESTS FOR UPLOAD HANDLER
# ============================================================

class TestUploadHandler:
    """Test file upload validation and storage"""
    
    def test_validate_file_empty_filename(self):
        """Test that empty filenames are rejected"""
        # Mock file object
        class MockFile:
            filename = ''
        
        is_valid, error = UploadHandler.validate_file(MockFile())
        assert is_valid == False
        assert 'No file selected' in error
    
    def test_validate_file_max_size(self):
        """Test file size validation"""
        class MockFile:
            filename = 'test.jpg'
            
            def seek(self, pos, whence=0):
                pass
            
            def tell(self):
                return 6 * 1024 * 1024  # 6MB - exceeds 5MB limit
        
        is_valid, error = UploadHandler.validate_file(MockFile())
        assert is_valid == False
        assert 'too large' in error.lower()
    
    def test_validate_file_invalid_extension(self):
        """Test file extension validation"""
        class MockFile:
            filename = 'test.exe'
            
            def seek(self, pos, whence=0):
                pass
            
            def tell(self):
                return 1024
        
        is_valid, error = UploadHandler.validate_file(MockFile())
        assert is_valid == False
        assert 'Invalid file type' in error


# ============================================================
# TESTS FOR REGRESSION
# ============================================================

class TestRegressionChecks:
    """Test that existing functionality is not broken"""
    
    def test_users_still_work(self, users):
        """Verify User model still works"""
        assert users['patient'].role == 'patient'
        assert users['caregiver'].role == 'caregiver'
    
    def test_reminders_still_work(self, client, users):
        """Verify Reminder model still works"""
        with app.app_context():
            reminder = Reminder(
                user_id=users['patient_id'],
                title="Test Reminder",
                type="medicine",
                time="10:00"
            )
            db.session.add(reminder)
            db.session.commit()
            
            retrieved = Reminder.query.first()
            assert retrieved.title == "Test Reminder"
    
    def test_activity_logs_still_work(self, users):
        """Verify ActivityLog model still works"""
        with app.app_context():
            activity = ActivityLog(
                user_id=users['patient_id'],
                game_type="memory_match",
                score=85,
                accuracy=90.5,
                difficulty="medium",
                time_taken=125.5  # Required field
            )
            db.session.add(activity)
            db.session.commit()
            
            retrieved = ActivityLog.query.first()
            assert retrieved.game_type == "memory_match"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
