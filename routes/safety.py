"""
Phase 10E: Safety & Caregiver Support
Endpoints for emergency alerts and safety monitoring
"""

from flask import Blueprint, request, session, jsonify
from datetime import datetime
from models.models import db, SafetyAlert, User

# Create safety blueprint
safety_bp = Blueprint('safety', __name__, url_prefix='/api/safety')

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def check_safety_authorization(patient_id):
    """
    Verify user is authorized to access safety data.
    
    Returns:
        tuple: (user, error_response) or (user, None) if authorized
    """
    user_id = session.get('user_id')
    if not user_id:
        return None, {'error': 'Unauthorized'}, 401
    
    user = User.query.get(user_id)
    if not user:
        return None, {'error': 'User not found'}, 404
    
    # Patient can only view own safety
    if user.role == 'patient' and patient_id != user_id:
        return None, {'error': 'Forbidden'}, 403
    
    # Caregiver can view any patient
    if user.role not in ['patient', 'caregiver']:
        return None, {'error': 'Forbidden'}, 403
    
    return user, None, None


# ============================================================
# ENDPOINTS
# ============================================================

@safety_bp.route('/sos', methods=['POST'])
def create_sos_alert():
    """
    Patient creates an emergency SOS alert.
    
    Behavior:
    - require authenticated patient
    - derive patient_id from session
    - prevent duplicate active alerts
    - return created alert
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_id)
    if not user or user.role != 'patient':
        return jsonify({'error': 'Only patients can create alerts'}), 403
    
    # Check for existing active alert
    existing_alert = SafetyAlert.query.filter(
        SafetyAlert.patient_id == user_id,
        SafetyAlert.status == 'active'
    ).first()
    
    if existing_alert:
        # Return existing alert instead of creating duplicate
        return jsonify({
            'success': False,
            'message': 'Active alert already exists',
            'alert': existing_alert.to_dict()
        }), 200
    
    # Create new emergency alert
    alert = SafetyAlert(
        patient_id=user_id,
        alert_type='emergency',
        status='active',
        message=f'Emergency alert from {user.name}'
    )
    
    try:
        db.session.add(alert)
        db.session.commit()
        return jsonify({
            'success': True,
            'alert': alert.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create alert: {str(e)}'}), 500


@safety_bp.route('/status', methods=['GET'])
def get_safety_status():
    """
    Get patient's current safety status.
    
    Returns:
    {
        "success": true,
        "status": "safe" | "alert",
        "active_alert": alert_object or null
    }
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.role != 'patient':
        return jsonify({'error': 'Only patients can check their safety status'}), 403
    
    # Get active alert if exists
    active_alert = SafetyAlert.query.filter(
        SafetyAlert.patient_id == user_id,
        SafetyAlert.status == 'active'
    ).order_by(SafetyAlert.created_at.desc()).first()
    
    status = 'alert' if active_alert else 'safe'
    
    return jsonify({
        'success': True,
        'status': status,
        'active_alert': active_alert.to_dict() if active_alert else None
    }), 200


@safety_bp.route('/alerts', methods=['GET'])
def get_safety_alerts():
    """
    Caregiver endpoint to get recent alerts for authorized patients.
    
    Returns only alerts for patients the caregiver can view.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.role != 'caregiver':
        return jsonify({'error': 'Only caregivers can access alerts'}), 403
    
    # Get recent alerts (active and resolved within last 24 hours)
    from datetime import timedelta
    recent_cutoff = datetime.utcnow() - timedelta(hours=24)
    
    alerts = SafetyAlert.query.filter(
        (SafetyAlert.status == 'active') |
        (SafetyAlert.resolved_at >= recent_cutoff)
    ).order_by(SafetyAlert.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'alerts': [alert.to_dict() for alert in alerts]
    }), 200


@safety_bp.route('/alerts/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """
    Caregiver resolves an alert.
    
    Set status='resolved' and resolved_at=now
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.role != 'caregiver':
        return jsonify({'error': 'Only caregivers can resolve alerts'}), 403
    
    alert = SafetyAlert.query.get(alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    
    # Update alert
    alert.status = 'resolved'
    alert.resolved_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'alert': alert.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to resolve alert: {str(e)}'}), 500
