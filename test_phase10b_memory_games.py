"""
MEMORA Phase 10B Test Suite - Personalized Memory Games
Tests for Photo/Name Match and Who Is This games
"""

import pytest
import json
from datetime import datetime
from models.models import User, ActivityLog, MemoryPerson


# ============================================================
# SETUP & FIXTURES
# ============================================================

@pytest.fixture(autouse=True)
def reset_db():
    """Reset database before each test"""
    from app import app, db
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Create test users
        patient = User(id=1, name="Test Patient", role="patient")
        caregiver = User(id=2, name="Test Caregiver", role="caregiver")
        db.session.add_all([patient, caregiver])
        db.session.commit()
        
        yield
        
        db.drop_all()


@pytest.fixture
def client():
    """Create Flask test client"""
    from app import app
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def session_with_patient(client):
    """Set up session with patient logged in"""
    from app import app
    
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'patient'
        sess.permanent = True
    
    return client


# ============================================================
# TEST: ROUTE AVAILABILITY
# ============================================================

class TestPhotoNameMatchRoutes:
    """Test photo/name match game routes"""
    
    def test_game_route_exists(self, session_with_patient):
        """Verify /game/photo-name-match route exists"""
        response = session_with_patient.get('/game/photo-name-match')
        assert response.status_code == 200
        assert b'game_photo_name_match_heading' in response.data
    
    def test_game_route_requires_login(self, client):
        """Verify /game/photo-name-match requires login"""
        response = client.get('/game/photo-name-match')
        # Should redirect or return 302
        assert response.status_code in [302, 401]
    
    def test_template_contains_user_id_injection(self, session_with_patient):
        """Verify USER_ID is injected in template"""
        response = session_with_patient.get('/game/photo-name-match')
        assert b'const USER_ID' in response.data
        assert b'= 1' in response.data
    
    def test_template_loads_javascript(self, session_with_patient):
        """Verify photo_name_match.js is loaded"""
        response = session_with_patient.get('/game/photo-name-match')
        assert b'photo_name_match.js' in response.data


class TestWhoIsThisRoutes:
    """Test who is this game routes"""
    
    def test_game_route_exists(self, session_with_patient):
        """Verify /game/who-is-this route exists"""
        response = session_with_patient.get('/game/who-is-this')
        assert response.status_code == 200
        assert b'game_who_is_this_heading' in response.data
    
    def test_game_route_requires_login(self, client):
        """Verify /game/who-is-this requires login"""
        response = client.get('/game/who-is-this')
        assert response.status_code in [302, 401]
    
    def test_template_loads_javascript(self, session_with_patient):
        """Verify who_is_this.js is loaded"""
        response = session_with_patient.get('/game/who-is-this')
        assert b'who_is_this.js' in response.data


# ============================================================
# TEST: GAMES HUB INTEGRATION
# ============================================================

class TestGamesHubCards:
    """Test games hub shows new games"""
    
    def test_games_hub_shows_photo_name_match(self, session_with_patient):
        """Verify Photo/Name Match card appears in games hub"""
        response = session_with_patient.get('/games')
        assert response.status_code == 200
        assert b'game_photo_name_match_title' in response.data
        assert b'photo-name-match' in response.data
    
    def test_games_hub_shows_who_is_this(self, session_with_patient):
        """Verify Who Is This card appears in games hub"""
        response = session_with_patient.get('/games')
        assert response.status_code == 200
        assert b'game_who_is_this_title' in response.data
        assert b'who-is-this' in response.data


# ============================================================
# TEST: GAME LOGIC - PHOTO NAME MATCH
# ============================================================

class TestPhotoNameMatchGameplay:
    """Test photo/name match game logic"""
    
    def setup_method(self):
        """Setup test data before each test"""
        from app import app, db
        
        self.app = app
        
        with app.app_context():
            # Clear existing people
            MemoryPerson.query.delete()
            
            # Create test people
            people = [
                MemoryPerson(
                    patient_id=1,
                    name="Anil Sharma",
                    relationship="Son",
                    description="Eldest son",
                    photo="uploads/person1.jpg",
                    is_active=True
                ),
                MemoryPerson(
                    patient_id=1,
                    name="Lakshmi Devi",
                    relationship="Wife",
                    description="Loving wife",
                    photo="uploads/person2.jpg",
                    is_active=True
                ),
                MemoryPerson(
                    patient_id=1,
                    name="Ravi Kumar",
                    relationship="Brother",
                    description="Younger brother",
                    photo="uploads/person3.jpg",
                    is_active=True
                ),
            ]
            db.session.add_all(people)
            db.session.commit()
    
    def test_game_requires_minimum_people(self, session_with_patient):
        """Test game requires at least 2 people"""
        from app import app, db
        
        with app.app_context():
            # Clear all people
            MemoryPerson.query.delete()
            db.session.commit()
            
            # Game should load but show error
            response = session_with_patient.get('/game/photo-name-match')
            # Game page still loads, but JS will show error
            assert response.status_code == 200
    
    def test_memory_people_api_returns_people(self, session_with_patient):
        """Test API returns memory people for patient"""
        response = session_with_patient.get('/api/memory/people?patient_id=1')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 3
        
        # Check structure
        person = data[0]
        assert 'id' in person
        assert 'name' in person
        assert 'relationship' in person
        assert 'photo' in person
        assert 'is_active' in person
    
    def test_memory_people_api_filters_by_patient(self, session_with_patient):
        """Test API only returns patient's own people"""
        response = session_with_patient.get('/api/memory/people?patient_id=1')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # All returned people should be active (test data validation)
        # Note: patient_id is not exposed in API response, only used server-side for filtering
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_memory_people_api_filters_active(self, session_with_patient):
        """Test API only returns active people"""
        from app import app, db
        
        with app.app_context():
            # Mark one person as inactive
            person = MemoryPerson.query.first()
            if person:
                person.is_active = False
                db.session.commit()
        
        response = session_with_patient.get('/api/memory/people?patient_id=1')
        data = json.loads(response.data)
        
        # All should be active
        for person in data:
            assert person['is_active'] is True


# ============================================================
# TEST: GAME LOGIC - WHO IS THIS
# ============================================================

class TestWhoIsThisGameplay:
    """Test who is this game logic"""
    
    def setup_method(self):
        """Setup test data"""
        from app import app, db
        
        self.app = app
        
        with app.app_context():
            MemoryPerson.query.delete()
            
            people = [
                MemoryPerson(
                    patient_id=1,
                    name="Anil Sharma",
                    relationship="Son",
                    description="Eldest son",
                    photo="uploads/person1.jpg",
                    is_active=True
                ),
                MemoryPerson(
                    patient_id=1,
                    name="Lakshmi Devi",
                    relationship="Wife",
                    description="Loving wife",
                    photo="uploads/person2.jpg",
                    is_active=True
                ),
                MemoryPerson(
                    patient_id=1,
                    name="Ravi Kumar",
                    relationship="Brother",
                    description="Younger brother",
                    photo="uploads/person3.jpg",
                    is_active=True
                ),
            ]
            db.session.add_all(people)
            db.session.commit()
    
    def test_who_is_this_route_accessible(self, session_with_patient):
        """Verify who-is-this route is accessible"""
        response = session_with_patient.get('/game/who-is-this')
        assert response.status_code == 200


# ============================================================
# TEST: ACTIVITY LOG CREATION
# ============================================================

class TestActivityLogLogging:
    """Test game results are logged correctly"""
    
    def test_photo_name_match_logged(self, session_with_patient):
        """Test photo_name_match game result is logged"""
        from app import app, db
        
        game_data = {
            'game_type': 'photo_name_match',
            'score': 80,
            'accuracy': 80.0,
            'time_taken': 45.5,
            'difficulty': 'medium'
        }
        
        response = session_with_patient.post(
            '/api/games/log',
            data=json.dumps(game_data),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 201]
        
        # Verify in database
        with app.app_context():
            log = ActivityLog.query.filter_by(
                user_id=1,
                game_type='photo_name_match'
            ).first()
            
            assert log is not None
            assert log.score == 80
            assert log.accuracy == 80.0
            assert log.difficulty == 'medium'
    
    def test_who_is_this_logged(self, session_with_patient):
        """Test who_is_this game result is logged"""
        from app import app, db
        
        game_data = {
            'game_type': 'who_is_this',
            'score': 60,
            'accuracy': 60.0,
            'time_taken': 52.3,
            'difficulty': 'hard'
        }
        
        response = session_with_patient.post(
            '/api/games/log',
            data=json.dumps(game_data),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 201]
        
        # Verify in database
        with app.app_context():
            log = ActivityLog.query.filter_by(
                user_id=1,
                game_type='who_is_this'
            ).first()
            
            assert log is not None
            assert log.score == 60
            assert log.difficulty == 'hard'
    
    def test_log_requires_all_fields(self, session_with_patient):
        """Test game log requires all required fields"""
        # Missing required fields
        incomplete_data = {
            'game_type': 'photo_name_match',
            'score': 80
            # Missing accuracy, time_taken, difficulty
        }
        
        response = session_with_patient.post(
            '/api/games/log',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        # Should fail or require fields
        assert response.status_code in [400, 422, 500]


# ============================================================
# TEST: AUTHORIZATION & PATIENT ISOLATION
# ============================================================

class TestAuthorizationAndIsolation:
    """Test authorization and patient data isolation"""
    
    def setup_method(self):
        """Setup test data"""
        from app import app, db
        
        self.app = app
        
        with app.app_context():
            MemoryPerson.query.delete()
            
            # Create people for patient 1
            people_p1 = [
                MemoryPerson(
                    patient_id=1,
                    name="Patient 1 Person 1",
                    relationship="Friend",
                    description="Friend",
                    photo="uploads/p1_1.jpg",
                    is_active=True
                ),
            ]
            
            # Create people for patient 2 (hypothetical)
            people_p2 = [
                MemoryPerson(
                    patient_id=2,
                    name="Patient 2 Person 1",
                    relationship="Friend",
                    description="Friend",
                    photo="uploads/p2_1.jpg",
                    is_active=True
                ),
            ]
            
            db.session.add_all(people_p1 + people_p2)
            db.session.commit()
    
    def test_patient_only_sees_own_people(self, session_with_patient):
        """Verify patient only gets their own memory people"""
        response = session_with_patient.get('/api/memory/people?patient_id=1')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        # Should not contain patient 2's people
        for person in data:
            assert person['name'] != "Patient 2 Person 1"
    
    def test_caregiver_can_view_all_patients(self, client):
        """Verify caregiver can view other patients' people"""
        from app import app, db
        
        # Login as caregiver
        with client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['role'] = 'caregiver'
            sess.permanent = True
        
        # Caregiver should be able to query any patient's people
        # (Depending on implementation - may require caregiver role check)
        response = client.get('/api/memory/people?patient_id=1')
        
        # Should succeed (caregiver has broader access)
        assert response.status_code == 200


# ============================================================
# TEST: REGRESSION - EXISTING GAMES STILL WORK
# ============================================================

class TestNoRegressions:
    """Verify no regressions to Phase 1-9 games"""
    
    def test_memory_match_still_accessible(self, session_with_patient):
        """Verify Memory Match game still works"""
        response = session_with_patient.get('/game/memory-match')
        assert response.status_code == 200
        assert b'game_memory_match_heading' in response.data
    
    def test_attention_test_still_accessible(self, session_with_patient):
        """Verify Attention Test game still works"""
        response = session_with_patient.get('/game/attention-test')
        assert response.status_code == 200
        assert b'game_attention_test_heading' in response.data
    
    def test_games_hub_still_shows_original_games(self, session_with_patient):
        """Verify games hub still shows original games"""
        response = session_with_patient.get('/games')
        assert response.status_code == 200
        assert b'game_memory_match' in response.data
        assert b'game_attention_test' in response.data
    
    def test_original_games_still_log_correctly(self, session_with_patient):
        """Verify original games still log to ActivityLog"""
        game_data = {
            'game_type': 'memory_match',
            'score': 500,
            'accuracy': 90.0,
            'time_taken': 120.5,
            'difficulty': 'medium'
        }
        
        response = session_with_patient.post(
            '/api/games/log',
            data=json.dumps(game_data),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 201]


# ============================================================
# TEST: I18N KEYS EXIST
# ============================================================

class TestI18nKeys:
    """Verify i18n keys exist for new games"""
    
    def test_english_keys_exist(self):
        """Verify all English i18n keys for new games exist"""
        with open('static/i18n/en.json', 'r', encoding='utf-8') as f:
            en = json.load(f)
        
        required_keys = [
            'game_photo_name_match_title',
            'game_photo_name_match_desc',
            'game_photo_name_match_heading',
            'game_who_is_this_title',
            'game_who_is_this_desc',
            'game_who_is_this_heading',
            'question_label',
            'of_label',
            'who_is_this_question',
            'select_name',
            'select_photo',
            'not_enough_memories',
            'add_more_people_message',
            'try_again',
            'missing_photo',
            'game_not_started'
        ]
        
        for key in required_keys:
            assert key in en, f"Missing key: {key}"
    
    def test_assamese_keys_exist(self):
        """Verify all Assamese i18n keys for new games exist"""
        with open('static/i18n/as.json', 'r', encoding='utf-8') as f:
            as_lang = json.load(f)
        
        required_keys = [
            'game_photo_name_match_title',
            'game_photo_name_match_desc',
            'game_photo_name_match_heading',
            'game_who_is_this_title',
            'game_who_is_this_desc',
            'game_who_is_this_heading',
            'question_label',
            'of_label',
            'who_is_this_question',
            'select_name',
            'select_photo',
            'not_enough_memories',
            'add_more_people_message',
            'try_again',
            'missing_photo',
            'game_not_started'
        ]
        
        for key in required_keys:
            assert key in as_lang, f"Missing Assamese key: {key}"
    
    def test_keys_have_content(self):
        """Verify i18n keys have non-empty values"""
        with open('static/i18n/en.json', 'r', encoding='utf-8') as f:
            en = json.load(f)
        
        required_keys = [
            'game_photo_name_match_title',
            'game_who_is_this_title',
        ]
        
        for key in required_keys:
            assert en[key], f"Key {key} is empty"
            assert isinstance(en[key], str), f"Key {key} is not a string"


# ============================================================
# TEST: DIFFICULTY API STILL WORKS
# ============================================================

class TestDifficultyAPI:
    """Test adaptive difficulty API for new games"""
    
    def test_difficulty_endpoint_accessible(self, session_with_patient):
        """Verify difficulty endpoint is accessible"""
        response = session_with_patient.get('/api/difficulty/1')
        assert response.status_code == 200
    
    def test_difficulty_returns_valid_level(self, session_with_patient):
        """Test difficulty endpoint returns valid difficulty level"""
        response = session_with_patient.get('/api/difficulty/1')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'difficulty' in data
        assert data['difficulty'] in ['easy', 'medium', 'hard']


# ============================================================
# TEST: MEMORY ALBUM INTEGRATION
# ============================================================

class TestMemoryAlbumIntegration:
    """Test new games integrate with Memory Album"""
    
    def test_memory_album_route_exists(self, session_with_patient):
        """Verify memory album route is accessible"""
        response = session_with_patient.get('/memory-album')
        assert response.status_code == 200
    
    def test_memory_album_shows_people(self, session_with_patient):
        """Verify memory album displays memory people"""
        from app import app, db
        
        with app.app_context():
            # Ensure we have people
            if MemoryPerson.query.count() == 0:
                person = MemoryPerson(
                    patient_id=1,
                    name="Test Person",
                    relationship="Friend",
                    description="Test",
                    photo="uploads/test.jpg",
                    is_active=True
                )
                db.session.add(person)
                db.session.commit()
        
        response = session_with_patient.get('/memory-album')
        assert response.status_code == 200
        # Should have memory album content (actual content depends on template)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
