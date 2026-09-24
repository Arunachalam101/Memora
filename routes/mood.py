"""
Phase 10D: Mood Tracking API Routes
Endpoints for mood entry creation, retrieval, and statistics
"""

from flask import Blueprint, request, session, jsonify
from datetime import datetime, timedelta
from models.models import db, MoodEntry, User

# Create mood blueprint
mood_bp = Blueprint('mood', __name__, url_prefix='/api/mood')

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def check_mood_authorization(patient_id, required_role=None):
    """
    Verify user is authorized to access mood data.
    
    Args:
        patient_id: The patient whose mood data is being accessed
        required_role: Optional role to check ("patient" or "caregiver")
    
    Returns:
        tuple: (user, error_response) or (user, None) if authorized
    """
    user_id = session.get('user_id')
    if not user_id:
        return None, {'error': 'Unauthorized'}, 401
    
    user = User.query.get(user_id)
    if not user:
        return None, {'error': 'User not found'}, 404
    
    # Check role constraint if specified
    if required_role and user.role != required_role:
        return None, {'error': 'Forbidden'}, 403
    
    # Patient can only view own mood
    if user.role == 'patient' and patient_id != user_id:
        return None, {'error': 'Forbidden'}, 403
    
    # Caregiver can view any patient (Phase 10D - basic access)
    # Phase 10E will add caregiver-patient relationship mapping
    if user.role not in ['patient', 'caregiver']:
        return None, {'error': 'Forbidden'}, 403
    
    return user, None, None


def validate_mood_value(mood):
    """Validate mood is one of the allowed values."""
    allowed_moods = ['very_happy', 'happy', 'okay', 'sad', 'very_sad']
    return mood in allowed_moods


# ============================================================
# ENDPOINTS
# ============================================================

@mood_bp.route('/entries', methods=['POST'])
def create_mood_entry():
    """
    Create a new mood entry for the patient.
    
    Request JSON:
    {
        "mood": "happy|very_happy|okay|sad|very_sad",
        "note": "optional text note"
    }
    
    Returns: MoodEntry object or error
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_id)
    if not user or user.role != 'patient':
        return jsonify({'error': 'Only patients can create mood entries'}), 403
    
    data = request.get_json()
    
    # Validate mood field exists
    if 'mood' not in data or not data['mood']:
        return jsonify({'error': 'Mood field is required'}), 400
    
    mood = data['mood'].strip()
    
    # Validate mood value
    if not validate_mood_value(mood):
        return jsonify({'error': 'Invalid mood value. Must be one of: very_happy, happy, okay, sad, very_sad'}), 400
    
    # Validate note if provided
    note = data.get('note', '').strip() if data.get('note') else None
    if note and len(note) > 500:
        return jsonify({'error': 'Note cannot exceed 500 characters'}), 400
    
    # Create and save mood entry
    mood_entry = MoodEntry(
        patient_id=user_id,
        mood=mood,
        note=note if note else None
    )
    
    try:
        db.session.add(mood_entry)
        db.session.commit()
        return jsonify(mood_entry.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create mood entry: {str(e)}'}), 500


@mood_bp.route('/today', methods=['GET'])
def get_today_mood():
    """
    Get today's mood entry for the requesting patient.
    
    Returns:
    {
        "has_entry": true/false,
        "entry": {mood entry object} or null
    }
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Patient sees own mood, caregiver can request specific patient via query param
    patient_id = user_id
    if user.role == 'caregiver':
        # Caregiver can request a specific patient's mood
        patient_id = request.args.get('patient_id', type=int)
        if not patient_id:
            return jsonify({'error': 'Caregiver must provide patient_id query parameter'}), 400
    
    # Get today's date range (midnight to 23:59:59)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    # Query today's mood entries, ordered by timestamp descending
    mood_entry = MoodEntry.query.filter(
        MoodEntry.patient_id == patient_id,
        MoodEntry.timestamp >= today_start,
        MoodEntry.timestamp < today_end
    ).order_by(MoodEntry.timestamp.desc()).first()
    
    return jsonify({
        'has_entry': mood_entry is not None,
        'entry': mood_entry.to_dict() if mood_entry else None
    }), 200


@mood_bp.route('/history', methods=['GET'])
def get_mood_history():
    """
    Get mood history for a patient.
    
    Query Parameters:
        days: Number of days to retrieve (default: 14)
        limit: Number of entries to return (default: 50)
        offset: Offset for pagination (default: 0)
    
    Returns:
    {
        "entries": [list of mood entry objects],
        "total": total count of entries in date range,
        "limit": limit used,
        "offset": offset used
    }
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Patient sees own history, caregiver can request specific patient
    patient_id = user_id
    if user.role == 'caregiver':
        patient_id = request.args.get('patient_id', type=int)
        if not patient_id:
            return jsonify({'error': 'Caregiver must provide patient_id query parameter'}), 400
    
    # Get query parameters
    days = request.args.get('days', default=14, type=int)
    limit = request.args.get('limit', default=50, type=int)
    offset = request.args.get('offset', default=0, type=int)
    
    # Validate parameters
    if days < 1 or days > 365:
        days = 14
    if limit < 1 or limit > 100:
        limit = 50
    if offset < 0:
        offset = 0
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Query mood entries
    query = MoodEntry.query.filter(
        MoodEntry.patient_id == patient_id,
        MoodEntry.timestamp >= start_date,
        MoodEntry.timestamp <= end_date
    )
    
    # Get total count
    total = query.count()
    
    # Get paginated results, ordered by timestamp descending
    entries = query.order_by(MoodEntry.timestamp.desc()).limit(limit).offset(offset).all()
    
    return jsonify({
        'entries': [entry.to_dict() for entry in entries],
        'total': total,
        'limit': limit,
        'offset': offset
    }), 200


@mood_bp.route('/stats', methods=['GET'])
def get_mood_stats():
    """
    Get mood statistics (caregiver only for Phase 10D).
    
    Query Parameters:
        patient_id: Required for caregivers, ignored for patients
        days: Number of days to analyze (default: 14)
    
    Returns:
    {
        "patient_id": patient_id,
        "period_days": days analyzed,
        "total_entries": total mood entries in period,
        "mood_distribution": {
            "very_happy": count,
            "happy": count,
            "okay": count,
            "sad": count,
            "very_sad": count
        },
        "latest_entry": {mood entry object} or null
    }
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Phase 10D: Only caregivers can access stats
    if user.role != 'caregiver':
        return jsonify({'error': 'Only caregivers can access mood statistics'}), 403
    
    # Get patient_id from query parameter
    patient_id = request.args.get('patient_id', type=int)
    if not patient_id:
        return jsonify({'error': 'patient_id query parameter is required'}), 400
    
    # Verify patient exists (optional validation)
    patient = User.query.get(patient_id)
    if not patient or patient.role != 'patient':
        return jsonify({'error': 'Patient not found'}), 404
    
    # Get days parameter
    days = request.args.get('days', default=14, type=int)
    if days < 1 or days > 365:
        days = 14
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Query mood entries for this patient
    entries = MoodEntry.query.filter(
        MoodEntry.patient_id == patient_id,
        MoodEntry.timestamp >= start_date,
        MoodEntry.timestamp <= end_date
    ).all()
    
    # Calculate mood distribution
    mood_distribution = {
        'very_happy': 0,
        'happy': 0,
        'okay': 0,
        'sad': 0,
        'very_sad': 0
    }
    
    for entry in entries:
        if entry.mood in mood_distribution:
            mood_distribution[entry.mood] += 1
    
    # Get latest entry
    latest_entry = MoodEntry.query.filter(
        MoodEntry.patient_id == patient_id
    ).order_by(MoodEntry.timestamp.desc()).first()
    
    return jsonify({
        'patient_id': patient_id,
        'period_days': days,
        'total_entries': len(entries),
        'mood_distribution': mood_distribution,
        'latest_entry': latest_entry.to_dict() if latest_entry else None
    }), 200
