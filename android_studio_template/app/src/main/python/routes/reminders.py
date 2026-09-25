from flask import Blueprint, request, session, jsonify
from models.models import db, Reminder

reminders_bp = Blueprint('reminders', __name__, url_prefix='/api')

def require_login():
    """Check if user is logged in, return 401 error if not"""
    if 'user_id' not in session:
        return None
    return session.get('user_id')


@reminders_bp.route('/reminders', methods=['GET'])
def get_reminders():
    """Get all reminders for the logged-in user"""
    user_id = require_login()
    if user_id is None:
        return jsonify({'error': 'Unauthorized'}), 401
    
    reminders = Reminder.query.filter_by(user_id=user_id).order_by(Reminder.time).all()
    return jsonify([r.to_dict() for r in reminders]), 200


@reminders_bp.route('/reminders', methods=['POST'])
def create_reminder():
    """Create a new reminder for the logged-in user"""
    user_id = require_login()
    if user_id is None:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    # Validate required fields
    if not data or 'title' not in data or 'type' not in data or 'time' not in data:
        return jsonify({'error': 'Missing required fields: title, type, time'}), 400
    
    try:
        reminder = Reminder(
            user_id=user_id,
            title=data['title'],
            type=data['type'],
            time=data['time'],
            is_done=False
        )
        db.session.add(reminder)
        db.session.commit()
        return jsonify(reminder.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@reminders_bp.route('/reminders/<int:reminder_id>', methods=['PUT'])
def update_reminder(reminder_id):
    """Update a reminder (only if owned by the logged-in user)"""
    user_id = require_login()
    if user_id is None:
        return jsonify({'error': 'Unauthorized'}), 401
    
    reminder = Reminder.query.get(reminder_id)
    if not reminder:
        return jsonify({'error': 'Reminder not found'}), 404
    
    # Check ownership
    if reminder.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    try:
        if 'title' in data:
            reminder.title = data['title']
        if 'type' in data:
            reminder.type = data['type']
        if 'time' in data:
            reminder.time = data['time']
        if 'is_done' in data:
            reminder.is_done = data['is_done']
        
        db.session.commit()
        return jsonify(reminder.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@reminders_bp.route('/reminders/<int:reminder_id>', methods=['DELETE'])
def delete_reminder(reminder_id):
    """Delete a reminder (only if owned by the logged-in user)"""
    user_id = require_login()
    if user_id is None:
        return jsonify({'error': 'Unauthorized'}), 401
    
    reminder = Reminder.query.get(reminder_id)
    if not reminder:
        return jsonify({'error': 'Reminder not found'}), 404
    
    # Check ownership
    if reminder.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        db.session.delete(reminder)
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
