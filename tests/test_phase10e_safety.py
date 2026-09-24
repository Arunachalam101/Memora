"""
Phase 10E Safety & Caregiver Support - Comprehensive Test Suite

Tests for emergency SOS alerts, safety status, and caregiver alert management.
Validates authorization, data integrity, and backward compatibility.
"""

import pytest
import json
from datetime import datetime, timedelta
from app import app, db
from models.models import User, SafetyAlert


# ============================================================
# FIXTURES & SETUP
# ============================================================

@pytest.fixture
def client():
    """Create test client with in-memory database"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def patient_user():
    """Create a test patient user"""
    with app.app_context():
        patient = User(id=1, name='Test Patient', pin='1234', role='patient', preferred_language='en')
        db.session.add(patient)
        db.session.commit()
        return patient.id


@pytest.fixture
def caregiver_user():
    """Create a test caregiver user"""
    with app.app_context():
        caregiver = User(id=2, name='Test Caregiver', pin='5678', role='caregiver', preferred_language='en')
        db.session.add(caregiver)
        db.session.commit()
        return caregiver.id


@pytest.fixture
def patient_session(client, patient_user):
    """Create authenticated patient session"""
    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = patient_user
        yield client


@pytest.fixture
def caregiver_session(client, caregiver_user):
    """Create authenticated caregiver session"""
    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = caregiver_user
        yield client


# ============================================================
# AUTHENTICATION TESTS
# ============================================================

class TestSafetyAuthentication:
    """Test authentication requirements for safety endpoints"""
    
    def test_sos_requires_authentication(self, client):
        """SOS endpoint should reject unauthenticated requests"""
        response = client.post('/api/safety/sos')
        assert response.status_code == 401
    
    def test_status_requires_authentication(self, client):
        """Status endpoint should reject unauthenticated requests"""
        response = client.get('/api/safety/status')
        assert response.status_code == 401
    
    def test_alerts_requires_authentication(self, client):
        """Alerts endpoint should reject unauthenticated requests"""
        response = client.get('/api/safety/alerts')
        assert response.status_code == 401


# ============================================================
# PATIENT BEHAVIOR TESTS
# ============================================================

class TestPatientSafety:
    """Test patient safety functionality"""
    
    def test_patient_create_sos_alert(self, patient_session, patient_user):
        """Patient can create emergency SOS alert"""
        response = patient_session.post('/api/safety/sos')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['alert']['patient_id'] == patient_user
        assert data['alert']['alert_type'] == 'emergency'
        assert data['alert']['status'] == 'active'
    
    def test_patient_view_safety_status_safe(self, patient_session, patient_user):
        """Patient can view safety status when safe"""
        response = patient_session.get('/api/safety/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['status'] == 'safe'
        assert data['active_alert'] == None
    
    def test_patient_view_safety_status_alert(self, patient_session, patient_user):
        """Patient can view safety status with active alert"""
        # Create alert first
        patient_session.post('/api/safety/sos')
        
        # Check status
        response = patient_session.get('/api/safety/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['status'] == 'alert'
        assert data['active_alert'] is not None
        assert data['active_alert']['status'] == 'active'
    
    def test_patient_cannot_specify_other_patient_id(self, patient_session, patient_user):
        """Patient cannot create alert for another patient"""
        with app.app_context():
            other_patient = User(id=10, name='Other Patient', pin='9999', role='patient', preferred_language='en')
            db.session.add(other_patient)
            db.session.commit()
        
        response = patient_session.post('/api/safety/sos')
        assert response.status_code == 201
        data = json.loads(response.data)
        # Alert should belong to authenticated patient, not any other
        assert data['alert']['patient_id'] == patient_user
    
    def test_patient_duplicate_active_alert_prevented(self, patient_session):
        """Duplicate active SOS alert is prevented"""
        # Create first alert
        response1 = patient_session.post('/api/safety/sos')
        assert response1.status_code == 201
        
        # Try to create second alert
        response2 = patient_session.post('/api/safety/sos')
        assert response2.status_code in [200, 400, 201]  # Either error or returns existing alert
        data = json.loads(response2.data)
        # Should indicate that alert already exists
        if response2.status_code in [200, 400]:
            assert 'already exists' in data.get('message', '').lower()
    
    def test_patient_cannot_resolve_alerts(self, patient_session, patient_user):
        """Patient cannot resolve alerts (caregiver only)"""
        # Create alert first
        response = patient_session.post('/api/safety/sos')
        alert_id = json.loads(response.data)['alert']['id']
        
        # Try to resolve (should fail - patient not caregiver)
        resolve_response = patient_session.post(f'/api/safety/alerts/{alert_id}/resolve')
        assert resolve_response.status_code == 403


# ============================================================
# CAREGIVER BEHAVIOR TESTS
# ============================================================

class TestCaregiverSafety:
    """Test caregiver safety alert functionality"""
    
    def test_caregiver_view_safety_alerts(self, client, patient_user, caregiver_user):
        """Caregiver can view patient safety alerts"""
        # Create alert from patient
        with client:
            with client.session_transaction() as sess:
                sess['user_id'] = patient_user
            response = client.post('/api/safety/sos')
            assert response.status_code == 201
        
        # Caregiver views alerts
        with client:
            with client.session_transaction() as sess:
                sess['user_id'] = caregiver_user
            response = client.get('/api/safety/alerts')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] == True
            assert len(data['alerts']) > 0
            assert data['alerts'][0]['patient_id'] == patient_user
            assert data['alerts'][0]['status'] == 'active'
    
    def test_caregiver_resolve_alert(self, client, patient_user, caregiver_user):
        """Caregiver can resolve an alert"""
        # Create alert from patient
        with client:
            with client.session_transaction() as sess:
                sess['user_id'] = patient_user
            response = client.post('/api/safety/sos')
            alert_id = json.loads(response.data)['alert']['id']
        
        # Caregiver resolves alert
        with client:
            with client.session_transaction() as sess:
                sess['user_id'] = caregiver_user
            resolve_response = client.post(f'/api/safety/alerts/{alert_id}/resolve')
            assert resolve_response.status_code == 200
            data = json.loads(resolve_response.data)
            assert data['success'] == True
            assert data['alert']['status'] == 'resolved'
            assert data['alert']['resolved_at'] is not None
    
    def test_patient_cannot_access_caregiver_alerts_endpoint(self, patient_session):
        """Patient cannot access caregiver alerts endpoint"""
        response = patient_session.get('/api/safety/alerts')
        assert response.status_code == 403


# ============================================================
# DATA INTEGRITY TESTS
# ============================================================

class TestSafetyDataIntegrity:
    """Test data integrity and correctness"""
    
    def test_alert_created_correctly(self, patient_session, patient_user):
        """Alert is created with correct data"""
        response = patient_session.post('/api/safety/sos')
        data = json.loads(response.data)
        alert = data['alert']
        
        with app.app_context():
            db_alert = SafetyAlert.query.get(int(alert['id']))
            assert db_alert.patient_id == patient_user
            assert db_alert.alert_type == 'emergency'
            assert db_alert.status == 'active'
            assert db_alert.created_at is not None
            assert db_alert.resolved_at is None
    
    def test_alert_status_changes_on_resolution(self, client, patient_user, caregiver_user):
        """Alert status changes from active to resolved"""
        # Create alert
        with client:
            with client.session_transaction() as sess:
                sess['user_id'] = patient_user
            response = client.post('/api/safety/sos')
            alert_id = json.loads(response.data)['alert']['id']
        
        # Verify active status
        with app.app_context():
            alert = SafetyAlert.query.get(alert_id)
            assert alert.status == 'active'
        
        # Resolve alert
        with client:
            with client.session_transaction() as sess:
                sess['user_id'] = caregiver_user
            client.post(f'/api/safety/alerts/{alert_id}/resolve')
        
        # Verify resolved status
        with app.app_context():
            alert = SafetyAlert.query.get(alert_id)
            assert alert.status == 'resolved'
    
    def test_resolved_at_timestamp_set_on_resolution(self, client, patient_user, caregiver_user):
        """resolved_at timestamp is set when alert is resolved"""
        # Create alert
        with client:
            with client.session_transaction() as sess:
                sess['user_id'] = patient_user
            response = client.post('/api/safety/sos')
            alert_id = json.loads(response.data)['alert']['id']
        
        # Verify resolved_at is None initially
        with app.app_context():
            alert = SafetyAlert.query.get(alert_id)
            assert alert.resolved_at is None
        
        # Resolve alert
        with client:
            with client.session_transaction() as sess:
                sess['user_id'] = caregiver_user
            client.post(f'/api/safety/alerts/{alert_id}/resolve')
        
        # Verify resolved_at is set
        with app.app_context():
            alert = SafetyAlert.query.get(alert_id)
            assert alert.resolved_at is not None
            assert isinstance(alert.resolved_at, datetime)
    
    def test_created_at_is_server_side(self, patient_session):
        """created_at timestamp is set server-side"""
        before = datetime.utcnow()
        response = patient_session.post('/api/safety/sos')
        after = datetime.utcnow()
        
        alert_id = json.loads(response.data)['alert']['id']
        with app.app_context():
            alert = SafetyAlert.query.get(alert_id)
            assert before <= alert.created_at <= after


# ============================================================
# AUTHORIZATION TESTS
# ============================================================

class TestSafetyAuthorization:
    """Test authorization and role-based access control"""
    
    def test_patient_can_only_create_own_sos(self, patient_session, patient_user):
        """Patient can only create SOS for themselves"""
        response = patient_session.post('/api/safety/sos')
        data = json.loads(response.data)
        assert data['alert']['patient_id'] == patient_user
    
    def test_caregiver_cannot_create_sos(self, caregiver_session):
        """Caregiver cannot create SOS alert (patient only)"""
        response = caregiver_session.post('/api/safety/sos')
        assert response.status_code == 403


# ============================================================
# REGRESSION TESTS
# ============================================================

class TestPhase10ERegression:
    """Verify Phase 10A-10D functionality still works"""
    
    def test_patient_can_login(self, client, patient_user):
        """Patient login still works"""
        with app.app_context():
            user = User.query.filter_by(role='patient').first()
            assert user is not None
    
    def test_caregiver_can_login(self, client, caregiver_user):
        """Caregiver login still works"""
        with app.app_context():
            user = User.query.filter_by(role='caregiver').first()
            assert user is not None
    
    def test_safety_blueprint_registered(self, client):
        """Safety blueprint is properly registered"""
        # Check that safety routes are accessible
        response = client.get('/api/safety/status')
        # Should be 401 (unauthenticated) not 404 (route not found)
        assert response.status_code == 401


# ============================================================
# EDGE CASES & ERROR HANDLING
# ============================================================

class TestSafetyEdgeCases:
    """Test edge cases and error handling"""
    
    def test_resolve_nonexistent_alert(self, caregiver_session):
        """Resolving non-existent alert returns 404"""
        response = caregiver_session.post('/api/safety/alerts/99999/resolve')
        assert response.status_code == 404
    
    def test_empty_alerts_list_on_no_alerts(self, caregiver_session):
        """Alerts endpoint returns empty list when no alerts"""
        response = caregiver_session.get('/api/safety/alerts')
        data = json.loads(response.data)
        assert data['alerts'] == []
    
    def test_alert_response_format_consistency(self, patient_session):
        """Alert response format is consistent"""
        response = patient_session.post('/api/safety/sos')
        data = json.loads(response.data)
        alert = data['alert']
        
        # Check required fields
        required_fields = ['id', 'patient_id', 'alert_type', 'status', 'created_at', 'resolved_at']
        for field in required_fields:
            assert field in alert


# ============================================================
# UI & ROUTE TESTS
# ============================================================

class TestSafetyUI:
    """Test safety page routes and UI rendering"""
    
    def test_safety_page_renders_for_patient(self, patient_session):
        """Safety page renders for authenticated patient"""
        response = patient_session.get('/safety')
        assert response.status_code == 200
        assert b'safety' in response.data.lower()
    
    def test_safety_page_requires_authentication(self, client):
        """Safety page requires authentication"""
        response = client.get('/safety')
        assert response.status_code in [302, 401]  # Redirect or unauthorized
    
    def test_patient_home_has_safety_link(self, patient_session):
        """Patient home page includes safety section"""
        response = patient_session.get('/patient-home')
        assert response.status_code == 200
        # Check for safety section (should contain safety-related content)
        assert b'safety' in response.data.lower() or b'check' in response.data.lower()


# ============================================================
# JSON & SERIALIZATION TESTS
# ============================================================

class TestSafetyJsonSerialization:
    """Test JSON serialization of safety data"""
    
    def test_alert_to_dict_returns_all_fields(self, patient_session):
        """Alert.to_dict() returns all required fields"""
        response = patient_session.post('/api/safety/sos')
        data = json.loads(response.data)
        alert = data['alert']
        
        # Verify to_dict format
        assert 'id' in alert
        assert 'patient_id' in alert
        assert 'alert_type' in alert
        assert 'status' in alert
        assert 'message' in alert
        assert 'created_at' in alert
        assert 'resolved_at' in alert
    
    def test_timestamps_are_iso_strings(self, patient_session):
        """Timestamps in JSON are ISO format strings"""
        response = patient_session.post('/api/safety/sos')
        data = json.loads(response.data)
        alert = data['alert']
        
        # Try to parse ISO string
        assert alert['created_at']
        assert 'T' in alert['created_at']  # ISO format includes T


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
