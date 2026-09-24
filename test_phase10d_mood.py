"""
Phase 10D: Mood Tracking - Comprehensive Test Suite
Tests mood tracking feature with focus on patient isolation and data integrity
"""

import pytest
import json
import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Import models first
from models.models import db, User, MoodEntry

# Create Flask app for testing
from flask import Flask
from config import Config

def create_test_app():
    """Create Flask app with test database"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.secret_key = 'test-secret-key'
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    from routes.users import users_bp
    from routes.reminders import reminders_bp
    from routes.games import games_bp
    from routes.progress import progress_bp
    from routes.memory import memory_bp
    from routes.memory_assistance import memory_assistance_bp
    from routes.mood import mood_bp
    
    app.register_blueprint(users_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(memory_bp)
    app.register_blueprint(memory_assistance_bp)
    app.register_blueprint(mood_bp)
    
    # Add index route
    @app.route('/')
    def index():
        from flask import session, redirect, url_for
        if 'user_id' in session:
            return redirect(url_for('users.patient_home'))
        return redirect(url_for('users.login'))
    
    return app


@pytest.fixture
def app():
    """Create Flask app with test database"""
    app = create_test_app()
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def patient_user(app):
    """Create test patient user"""
    with app.app_context():
        user = User(name='Test Patient', role='patient')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        return user_id


@pytest.fixture
def caregiver_user(app):
    """Create test caregiver user"""
    with app.app_context():
        user = User(name='Test Caregiver', role='caregiver')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        return user_id


@pytest.fixture
def patient_session(client, app, patient_user):
    """Create authenticated patient session"""
    with client.session_transaction() as session:
        session['user_id'] = patient_user
        session['user_name'] = 'Test Patient'
        session['user_role'] = 'patient'
    return client


@pytest.fixture
def caregiver_session(client, app, caregiver_user):
    """Create authenticated caregiver session"""
    with client.session_transaction() as session:
        session['user_id'] = caregiver_user
        session['user_name'] = 'Test Caregiver'
        session['user_role'] = 'caregiver'
    return client


# ============================================================
# TEST 1: AUTHENTICATION & AUTHORIZATION (5 tests)
# ============================================================

class TestMoodAuthentication:
    """Test authentication requirements for mood endpoints"""

    def test_mood_post_requires_login(self, client):
        """Test that POST /api/mood/entries requires authentication"""
        response = client.post('/api/mood/entries', json={'mood': 'happy'})
        assert response.status_code == 401

    def test_mood_get_today_requires_login(self, client):
        """Test that GET /api/mood/today requires authentication"""
        response = client.get('/api/mood/today')
        assert response.status_code == 401

    def test_mood_get_history_requires_login(self, client):
        """Test that GET /api/mood/history requires authentication"""
        response = client.get('/api/mood/history')
        assert response.status_code == 401

    def test_mood_stats_requires_login(self, client):
        """Test that GET /api/mood/stats requires authentication"""
        response = client.get('/api/mood/stats?patient_id=1')
        assert response.status_code == 401

    def test_mood_template_requires_login(self, client):
        """Test that /mood route requires authentication"""
        response = client.get('/mood')
        assert response.status_code == 302  # Redirect to login


# ============================================================
# TEST 2: MOOD CREATION & CRUD (8 tests)
# ============================================================

class TestMoodCreation:
    """Test mood entry creation and basic CRUD operations"""

    def test_create_mood_with_note(self, patient_session, patient_user, app):
        """Test creating a mood entry with a note"""
        with app.app_context():
            response = patient_session.post('/api/mood/entries', json={
                'mood': 'happy',
                'note': 'Had a great day with family'
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['mood'] == 'happy'
            assert data['note'] == 'Had a great day with family'
            assert 'timestamp' in data
            
            # Verify in database
            mood = MoodEntry.query.filter_by(patient_id=patient_user).first()
            assert mood is not None
            assert mood.mood == 'happy'

    def test_create_mood_without_note(self, patient_session, patient_user, app):
        """Test creating a mood entry without a note"""
        with app.app_context():
            response = patient_session.post('/api/mood/entries', json={
                'mood': 'okay'
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['mood'] == 'okay'
            assert data.get('note') is None

    def test_create_mood_invalid_value(self, patient_session):
        """Test that invalid mood values are rejected"""
        response = patient_session.post('/api/mood/entries', json={
            'mood': 'invalid_mood'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_create_mood_missing_mood_field(self, patient_session):
        """Test that missing mood field is rejected"""
        response = patient_session.post('/api/mood/entries', json={
            'note': 'Just a note'
        })
        
        assert response.status_code == 400

    def test_create_mood_note_too_long(self, patient_session):
        """Test that overly long notes are rejected"""
        long_note = 'x' * 501  # Exceeds 500 character limit
        response = patient_session.post('/api/mood/entries', json={
            'mood': 'happy',
            'note': long_note
        })
        
        assert response.status_code == 400

    def test_create_all_mood_values(self, patient_session, app):
        """Test creating mood entries for all valid mood values"""
        moods = ['very_happy', 'happy', 'okay', 'sad', 'very_sad']
        
        for mood in moods:
            response = patient_session.post('/api/mood/entries', json={'mood': mood})
            assert response.status_code == 201
            data = response.get_json()
            assert data['mood'] == mood

    def test_mood_timestamp_is_set(self, patient_session, app):
        """Test that mood entry has a timestamp"""
        with app.app_context():
            before = datetime.utcnow()
            response = patient_session.post('/api/mood/entries', json={'mood': 'happy'})
            after = datetime.utcnow()
            
            assert response.status_code == 201
            data = response.get_json()
            
            timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            assert before <= timestamp <= after

    def test_mood_created_at_set(self, patient_session, patient_user, app):
        """Test that created_at timestamp is set"""
        with app.app_context():
            patient_session.post('/api/mood/entries', json={'mood': 'happy'})
            
            mood = MoodEntry.query.filter_by(patient_id=patient_user).first()
            assert mood.created_at is not None


# ============================================================
# TEST 3: MOOD HISTORY & PAGINATION (6 tests)
# ============================================================

class TestMoodHistory:
    """Test mood history retrieval with pagination"""

    def test_get_empty_history(self, patient_session):
        """Test getting history when no moods are recorded"""
        response = patient_session.get('/api/mood/history')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['entries'] == []

    def test_get_history_single_entry(self, patient_session, patient_user, app):
        """Test getting history with a single mood entry"""
        with app.app_context():
            patient_session.post('/api/mood/entries', json={'mood': 'happy', 'note': 'Great!'})
            
            response = patient_session.get('/api/mood/history')
            assert response.status_code == 200
            data = response.get_json()
            
            assert len(data['entries']) == 1
            assert data['entries'][0]['mood'] == 'happy'

    def test_history_pagination_limit(self, patient_session, app):
        """Test that history respects limit parameter"""
        with app.app_context():
            # Create 10 mood entries
            for i in range(10):
                patient_session.post('/api/mood/entries', json={'mood': 'happy'})
            
            # Request with limit of 3
            response = patient_session.get('/api/mood/history?limit=3')
            assert response.status_code == 200
            data = response.get_json()
            
            assert len(data['entries']) == 3

    def test_history_pagination_offset(self, patient_session, app):
        """Test that history respects offset parameter"""
        with app.app_context():
            # Create 5 mood entries
            for i in range(5):
                patient_session.post('/api/mood/entries', json={'mood': 'happy'})
            
            # Get first 2
            response1 = patient_session.get('/api/mood/history?limit=2&offset=0')
            data1 = response1.get_json()
            ids1 = [e['id'] for e in data1['entries']]
            
            # Get next 2
            response2 = patient_session.get('/api/mood/history?limit=2&offset=2')
            data2 = response2.get_json()
            ids2 = [e['id'] for e in data2['entries']]
            
            # Should be different entries
            assert ids1 != ids2

    def test_history_days_filter(self, patient_session, patient_user, app):
        """Test that history respects days parameter"""
        with app.app_context():
            # Create mood entry
            patient_session.post('/api/mood/entries', json={'mood': 'happy'})
            
            # Request last 7 days
            response = patient_session.get('/api/mood/history?days=7')
            assert response.status_code == 200
            data = response.get_json()
            
            assert len(data['entries']) >= 1

    def test_history_ordered_by_timestamp(self, patient_session, app):
        """Test that history entries are ordered by timestamp descending"""
        with app.app_context():
            # Create 3 mood entries
            for i in range(3):
                patient_session.post('/api/mood/entries', json={'mood': 'happy'})
            
            response = patient_session.get('/api/mood/history')
            data = response.get_json()
            
            # Verify descending order
            timestamps = [datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00')) 
                         for e in data['entries']]
            assert timestamps == sorted(timestamps, reverse=True)


# ============================================================
# TEST 4: MOOD STATISTICS (5 tests)
# ============================================================

class TestMoodStats:
    """Test mood statistics endpoint and access control"""

    def test_stats_patient_denied(self, patient_session, patient_user):
        """Test that patients cannot access stats endpoint"""
        response = patient_session.get(f'/api/mood/stats?patient_id={patient_user}')
        assert response.status_code == 403

    def test_stats_caregiver_allowed(self, caregiver_session, patient_user, app):
        """Test that caregivers can access stats endpoint"""
        with app.app_context():
            # Create mood entries for patient
            for _ in range(3):
                patient = User.query.get(patient_user)
                mood = MoodEntry(patient_id=patient.id, mood='happy')
                db.session.add(mood)
                db.session.commit()
            
            response = caregiver_session.get(f'/api/mood/stats?patient_id={patient_user}')
            assert response.status_code == 200

    def test_stats_response_format(self, caregiver_session, patient_user, app):
        """Test that stats endpoint returns correct format"""
        with app.app_context():
            # Create various mood entries
            moods = ['very_happy', 'happy', 'okay', 'sad', 'very_sad']
            for mood in moods:
                patient = User.query.get(patient_user)
                entry = MoodEntry(patient_id=patient.id, mood=mood)
                db.session.add(entry)
                db.session.commit()
            
            response = caregiver_session.get(f'/api/mood/stats?patient_id={patient_user}')
            assert response.status_code == 200
            data = response.get_json()
            
            # Verify response structure
            assert 'total_entries' in data
            assert 'mood_distribution' in data
            assert 'latest_entry' in data

    def test_stats_mood_distribution(self, caregiver_session, patient_user, app):
        """Test that mood distribution is calculated correctly"""
        with app.app_context():
            # Create 2 happy and 1 sad
            for mood in ['happy', 'happy', 'sad']:
                patient = User.query.get(patient_user)
                entry = MoodEntry(patient_id=patient.id, mood=mood)
                db.session.add(entry)
                db.session.commit()
            
            response = caregiver_session.get(f'/api/mood/stats?patient_id={patient_user}')
            data = response.get_json()
            
            assert data['mood_distribution']['happy'] == 2
            assert data['mood_distribution']['sad'] == 1
            assert data['total_entries'] == 3


# ============================================================
# TEST 5: PATIENT DATA ISOLATION (CRITICAL - 5 tests)
# ============================================================

class TestPatientDataIsolation:
    """Test that patients can only see their own mood data"""

    def test_patient_cannot_create_mood_for_other_patient(self, app):
        """Test that patient cannot create mood for another patient"""
        with app.app_context():
            patient1 = User(name='Patient 1', role='patient')
            patient2 = User(name='Patient 2', role='patient')
            db.session.add_all([patient1, patient2])
            db.session.commit()
            
            # Login as patient1
            client = app.test_client()
            with client.session_transaction() as session:
                session['user_id'] = patient1.id
                session['user_role'] = 'patient'
            
            # Try to create mood with patient2's ID
            response = client.post('/api/mood/entries', json={
                'mood': 'happy',
                'patient_id': patient2.id
            })
            
            # Should create for authenticated patient (patient1), not patient2
            assert response.status_code == 201
            
            # Verify mood belongs to patient1, not patient2
            mood = MoodEntry.query.first()
            assert mood.patient_id == patient1.id

    def test_patient_cannot_view_other_moods(self, app):
        """Test that patient cannot view other patient's moods"""
        with app.app_context():
            patient1 = User(name='Patient 1', role='patient')
            patient2 = User(name='Patient 2', role='patient')
            db.session.add_all([patient1, patient2])
            db.session.commit()
            
            # Create mood for patient2
            mood = MoodEntry(patient_id=patient2.id, mood='happy')
            db.session.add(mood)
            db.session.commit()
            
            # Login as patient1
            client = app.test_client()
            with client.session_transaction() as session:
                session['user_id'] = patient1.id
                session['user_role'] = 'patient'
            
            # Try to get history - should only see own moods
            response = client.get('/api/mood/history')
            data = response.get_json()
            
            assert len(data['entries']) == 0  # Should not see patient2's mood

    def test_patient_cannot_access_other_today_moods(self, app):
        """Test that patient cannot access other patient's today mood"""
        with app.app_context():
            patient1 = User(name='Patient 1', role='patient')
            patient2 = User(name='Patient 2', role='patient')
            db.session.add_all([patient1, patient2])
            db.session.commit()
            
            # Create today's mood for patient2
            mood = MoodEntry(patient_id=patient2.id, mood='happy')
            db.session.add(mood)
            db.session.commit()
            
            # Login as patient1
            client = app.test_client()
            with client.session_transaction() as session:
                session['user_id'] = patient1.id
                session['user_role'] = 'patient'
            
            # Get today's mood - should return no entry
            response = client.get('/api/mood/today')
            data = response.get_json()
            
            assert data['has_entry'] == False

    def test_caregiver_can_view_all_patient_moods(self, app):
        """Test that caregiver can view any patient's moods"""
        with app.app_context():
            patient = User(name='Patient', role='patient')
            caregiver = User(name='Caregiver', role='caregiver')
            db.session.add_all([patient, caregiver])
            db.session.commit()
            
            # Create mood for patient
            mood = MoodEntry(patient_id=patient.id, mood='happy')
            db.session.add(mood)
            db.session.commit()
            
            # Login as caregiver
            client = app.test_client()
            with client.session_transaction() as session:
                session['user_id'] = caregiver.id
                session['user_role'] = 'caregiver'
            
            # Should be able to access patient's stats
            response = client.get(f'/api/mood/stats?patient_id={patient.id}')
            assert response.status_code == 200

    def test_mood_patient_id_not_trusted_from_client(self, app):
        """Test that patient_id from client is not trusted"""
        with app.app_context():
            patient1 = User(name='Patient 1', role='patient')
            patient2 = User(name='Patient 2', role='patient')
            db.session.add_all([patient1, patient2])
            db.session.commit()
            
            # Login as patient1
            client = app.test_client()
            with client.session_transaction() as session:
                session['user_id'] = patient1.id
                session['user_role'] = 'patient'
            
            # Try to create mood with patient2_id in body
            response = client.post('/api/mood/entries', json={
                'mood': 'happy',
                'patient_id': patient2.id  # Attempt to spoof
            })
            
            # Verify mood belongs to patient1 (session user), not patient2
            mood = MoodEntry.query.first()
            assert mood.patient_id == patient1.id


# ============================================================
# TEST 6: DATABASE MODEL VALIDATION (4 tests)
# ============================================================

class TestMoodModel:
    """Test MoodEntry model validation and relationships"""

    def test_mood_model_has_required_fields(self, app):
        """Test that MoodEntry has all required fields"""
        with app.app_context():
            patient = User(name='Test Patient', role='patient')
            db.session.add(patient)
            db.session.commit()
            
            mood = MoodEntry(patient_id=patient.id, mood='happy')
            db.session.add(mood)
            db.session.commit()
            
            assert mood.patient_id == patient.id
            assert mood.mood == 'happy'
            assert mood.timestamp is not None
            assert mood.created_at is not None

    def test_mood_model_relationship_to_user(self, app):
        """Test MoodEntry relationship to User"""
        with app.app_context():
            patient = User(name='Test Patient', role='patient')
            db.session.add(patient)
            db.session.commit()
            
            mood = MoodEntry(patient_id=patient.id, mood='happy')
            db.session.add(mood)
            db.session.commit()
            
            # Test relationship
            assert mood.user.id == patient.id
            assert mood in patient.mood_entries

    def test_mood_to_dict_serialization(self, app):
        """Test MoodEntry.to_dict() method"""
        with app.app_context():
            patient = User(name='Test Patient', role='patient')
            db.session.add(patient)
            db.session.commit()
            
            mood = MoodEntry(patient_id=patient.id, mood='happy', note='Great day!')
            db.session.add(mood)
            db.session.commit()
            
            mood_dict = mood.to_dict()
            
            assert 'id' in mood_dict
            assert mood_dict['mood'] == 'happy'
            assert mood_dict['note'] == 'Great day!'
            assert 'timestamp' in mood_dict

    def test_mood_note_nullable(self, app):
        """Test that mood note field is nullable"""
        with app.app_context():
            patient = User(name='Test Patient', role='patient')
            db.session.add(patient)
            db.session.commit()
            
            mood = MoodEntry(patient_id=patient.id, mood='happy', note=None)
            db.session.add(mood)
            db.session.commit()
            
            mood_dict = mood.to_dict()
            assert mood_dict.get('note') is None


# ============================================================
# TEST 7: VOICE ASSISTANT INTEGRATION (4 tests)
# ============================================================

class TestVoiceIntegration:
    """Test voice assistant integration with mood tracking"""

    def test_voice_can_query_mood(self, patient_session, patient_user, app):
        """Test that voice assistant can retrieve mood via API"""
        with app.app_context():
            # Create mood
            patient_session.post('/api/mood/entries', json={'mood': 'happy', 'note': 'Good day'})
            
            # Voice would call this API
            response = patient_session.get('/api/mood/today')
            assert response.status_code == 200
            data = response.get_json()
            
            assert data['has_entry'] == True
            assert data['entry']['mood'] == 'happy'

    def test_voice_mood_response_format(self, patient_session, patient_user, app):
        """Test that mood response is in correct format for voice"""
        with app.app_context():
            patient_session.post('/api/mood/entries', json={'mood': 'very_happy'})
            
            response = patient_session.get('/api/mood/today')
            data = response.get_json()
            
            # Voice needs these fields to form a response
            assert 'mood' in data['entry']
            assert 'timestamp' in data['entry']

    def test_voice_handles_no_mood_recorded(self, patient_session):
        """Test that voice gets proper response when no mood recorded"""
        response = patient_session.get('/api/mood/today')
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['has_entry'] == False

    def test_voice_mood_with_note(self, patient_session, patient_user, app):
        """Test that voice can get mood with note"""
        with app.app_context():
            patient_session.post('/api/mood/entries', json={
                'mood': 'happy',
                'note': 'Had coffee with friends'
            })
            
            response = patient_session.get('/api/mood/today')
            data = response.get_json()
            
            assert data['entry']['note'] == 'Had coffee with friends'


# ============================================================
# TEST 8: INTERNATIONALIZATION (i18n) (3 tests)
# ============================================================

class TestMoodI18n:
    """Test internationalization key consistency"""

    def test_mood_keys_in_english(self):
        """Test that all mood i18n keys exist in English"""
        with open('static/i18n/en.json', 'r', encoding='utf-8') as f:
            en = json.load(f)
        
        required_keys = [
            'mood_title', 'mood_subtitle', 'mood_heading',
            'mood_label_very_happy', 'mood_label_happy', 'mood_label_okay',
            'mood_label_sad', 'mood_label_very_sad',
            'mood_note_label', 'mood_note_placeholder', 'mood_note_hint',
            'mood_saved', 'mood_saved_with_note', 'mood_error', 'mood_loading',
            'mood_empty', 'mood_history_title', 'mood_history_label',
            'mood_no_history', 'mood_today_label', 'mood_days_ago',
            'stat_current_mood', 'mood_last_recorded', 'mood_section_subtitle',
            'btn_check_mood', 'voice_mood_query_greeting'
        ]
        
        for key in required_keys:
            assert key in en, f"Missing English translation key: {key}"

    def test_mood_keys_in_assamese(self):
        """Test that all mood i18n keys exist in Assamese"""
        with open('static/i18n/as.json', 'r', encoding='utf-8') as f:
            as_json = json.load(f)
        
        with open('static/i18n/en.json', 'r', encoding='utf-8') as f:
            en = json.load(f)
        
        # All English mood keys should exist in Assamese
        mood_keys = [k for k in en.keys() if 'mood' in k.lower()]
        
        for key in mood_keys:
            assert key in as_json, f"Missing Assamese translation key: {key}"

    def test_mood_keys_are_non_empty(self):
        """Test that mood translation values are non-empty"""
        with open('static/i18n/en.json', 'r', encoding='utf-8') as f:
            en = json.load(f)
        
        mood_keys = [k for k in en.keys() if 'mood' in k.lower()]
        
        for key in mood_keys:
            value = en[key]
            assert value and len(str(value).strip()) > 0, f"Empty translation for key: {key}"


# ============================================================
# TEST 9: INTEGRATION & END-TO-END (5 tests)
# ============================================================

class TestMoodIntegration:
    """Test end-to-end mood tracking workflows"""

    def test_full_mood_workflow(self, patient_session, patient_user, app):
        """Test complete mood tracking workflow"""
        with app.app_context():
            # 1. Create mood
            response = patient_session.post('/api/mood/entries', json={
                'mood': 'happy',
                'note': 'Had a good meeting'
            })
            assert response.status_code == 201
            
            # 2. Get today's mood
            response = patient_session.get('/api/mood/today')
            assert response.status_code == 200
            data = response.get_json()
            assert data['has_entry'] == True
            
            # 3. Get history
            response = patient_session.get('/api/mood/history')
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['entries']) == 1

    def test_multiple_moods_in_day(self, patient_session, patient_user, app):
        """Test recording multiple moods in one day"""
        with app.app_context():
            # Create multiple moods
            moods = ['very_happy', 'happy', 'okay']
            
            for mood in moods:
                response = patient_session.post('/api/mood/entries', json={'mood': mood})
                assert response.status_code == 201
            
            # Get history - should have all 3
            response = patient_session.get('/api/mood/history')
            data = response.get_json()
            assert len(data['entries']) == 3
            
            # Today's mood should return the latest
            response = patient_session.get('/api/mood/today')
            data = response.get_json()
            assert data['entry']['mood'] == 'okay'  # Last one recorded

    def test_caregiver_views_patient_moods(self, app, patient_user):
        """Test caregiver viewing patient mood dashboard"""
        with app.app_context():
            caregiver = User(name='Caregiver', role='caregiver')
            db.session.add(caregiver)
            db.session.commit()
            
            # Create moods for patient
            for mood in ['happy', 'sad', 'okay']:
                entry = MoodEntry(patient_id=patient_user, mood=mood)
                db.session.add(entry)
                db.session.commit()
            
            # Login as caregiver
            client = app.test_client()
            with client.session_transaction() as session:
                session['user_id'] = caregiver.id
                session['user_role'] = 'caregiver'
            
            # Get patient stats
            response = client.get(f'/api/mood/stats?patient_id={patient_user}')
            assert response.status_code == 200
            data = response.get_json()
            
            assert data['total_entries'] == 3

    def test_mood_persistence_across_sessions(self, app, patient_user):
        """Test that moods persist across login sessions"""
        with app.app_context():
            # First session - create mood
            client1 = app.test_client()
            with client1.session_transaction() as session:
                session['user_id'] = patient_user
                session['user_role'] = 'patient'
            
            response = client1.post('/api/mood/entries', json={'mood': 'happy'})
            assert response.status_code == 201
            
            # Second session - retrieve mood
            client2 = app.test_client()
            with client2.session_transaction() as session:
                session['user_id'] = patient_user
                session['user_role'] = 'patient'
            
            response = client2.get('/api/mood/today')
            assert response.status_code == 200
            data = response.get_json()
            assert data['has_entry'] == True
            assert data['entry']['mood'] == 'happy'

    def test_mood_page_loads(self, patient_session):
        """Test that mood.html page loads successfully"""
        response = patient_session.get('/mood')
        assert response.status_code == 200
        assert b'Check Your Mood' in response.data or b'mood' in response.data.lower()


# ============================================================
# TEST 10: REGRESSION VALIDATION (Phases 10A/B/C/7)
# ============================================================

class TestPhaseRegression:
    """Test that existing functionality still works after mood tracking"""

    def test_memory_entries_unaffected(self, app):
        """Test that memory entries still work"""
        with app.app_context():
            patient = User(name='Test Patient', role='patient')
            db.session.add(patient)
            db.session.commit()
            
            from models.models import MemoryItem
            memory = MemoryItem(patient_id=patient.id, title='Test Memory', description='Test content')
            db.session.add(memory)
            db.session.commit()
            
            retrieved = MemoryItem.query.filter_by(patient_id=patient.id).first()
            assert retrieved is not None

    def test_user_authentication_unaffected(self, app):
        """Test that user authentication still works"""
        with app.app_context():
            user = User(name='Test User', role='patient')
            db.session.add(user)
            db.session.commit()
            
            retrieved = User.query.filter_by(name='Test User').first()
            assert retrieved is not None
            assert retrieved.role == 'patient'

    def test_games_routes_unaffected(self, patient_session):
        """Test that games routes still work"""
        response = patient_session.get('/games')
        # Should not error - whether it exists or redirects is okay
        assert response.status_code in [200, 302]

    def test_dashboard_loads(self, caregiver_session):
        """Test that caregiver dashboard still loads"""
        response = caregiver_session.get('/caregiver-dashboard')
        assert response.status_code in [200, 302]

    def test_patient_home_loads(self, patient_session):
        """Test that patient home page still loads with mood section"""
        response = patient_session.get('/patient-home')
        assert response.status_code == 200
        # Should mention mood tracker
        assert b'mood' in response.data.lower() or b'Mood' in response.data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
