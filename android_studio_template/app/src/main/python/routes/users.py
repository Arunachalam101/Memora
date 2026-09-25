from flask import Blueprint, render_template, request, redirect, session, url_for, jsonify
from models.models import db, User

users_bp = Blueprint('users', __name__)

def login_required(f):
    """Decorator to check if user is logged in"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('users.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


@users_bp.route('/login', methods=['GET'])
def login():
    """Render login page"""
    return render_template('login.html')


@users_bp.route('/login', methods=['POST'])
def login_post():
    """Handle login form submission"""
    name = request.form.get('name', '').strip()
    pin = request.form.get('pin', '').strip()
    
    if not name:
        return redirect(url_for('users.login'))
    
    # Check if user exists
    user = User.query.filter_by(name=name).first()
    
    if not user:
        # Create new user with patient role
        user = User(name=name, pin=pin if pin else None, role='patient')
        db.session.add(user)
        db.session.commit()
    
    # Store in session
    session['user_id'] = user.id
    session['user_name'] = user.name
    session['user_role'] = user.role
    
    return redirect(url_for('users.patient_home'))


@users_bp.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('users.login'))


@users_bp.route('/patient-home')
@login_required
def patient_home():
    """Patient home page"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('patient_home.html', user=user)


@users_bp.route('/games')
@login_required
def games():
    """Games hub page"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('games_hub.html', user=user)


@users_bp.route('/caregiver-dashboard')
@login_required
def caregiver_dashboard():
    """Caregiver dashboard page"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('caregiver_dashboard.html', user=user)


@users_bp.route('/memory-album')
@login_required
def memory_album():
    """Memory Album page - Phase 10A"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('memory_album.html', user=user)


@users_bp.route('/memory-rescue')
@login_required
def memory_rescue():
    """Memory Rescue page - Phase 10C"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('memory_rescue.html', user=user)


@users_bp.route('/mood')
@login_required
def mood():
    """Mood Tracker page - Phase 10D"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('mood.html', user=user)


@users_bp.route('/safety')
@login_required
def safety():
    """Safety page - Phase 10E"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('safety.html', user=user)


# ============================================================
# API ENDPOINTS FOR DASHBOARD (Phase 6)
# ============================================================

@users_bp.route('/api/users/patients', methods=['GET'])
def get_patients():
    """
    Get all patients in the system.
    Returns JSON list of patients: {id, name, role}
    """
    try:
        patients = User.query.filter_by(role='patient').all()
        
        patients_data = [
            {
                'id': p.id,
                'name': p.name,
                'role': p.role
            }
            for p in patients
        ]
        
        return jsonify(patients_data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch patients: {str(e)}"}), 500


# ============================================================
# API ENDPOINTS FOR i18n (Phase 8)
# ============================================================

@users_bp.route('/api/user/language', methods=['PATCH'])
@login_required
def update_user_language():
    """
    Update user's preferred language.
    Accepts JSON: {"language": "en"} or {"language": "as"}
    Returns JSON: {"success": true}
    """
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return {"error": "User not found"}, 404
        
        data = request.get_json() or {}
        language = data.get('language', 'en').strip()
        
        # Validate language code
        if language not in ['en', 'as']:
            return {"error": f"Invalid language code: {language}"}, 400
        
        # Update user's preferred language
        user.preferred_language = language
        db.session.commit()
        
        return {"success": True, "language": language}, 200
    except Exception as e:
        return {"error": f"Failed to update language: {str(e)}"}, 500
