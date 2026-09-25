"""
MEMORA Memory Foundation Routes - Phase 10A
Handles Memory Album CRUD operations (People, Places, Memories)
"""

from flask import Blueprint, request, session, jsonify
from models.models import db, User, MemoryPerson, MemoryPlace, MemoryItem
from utils.upload_handler import UploadHandler
from datetime import datetime

memory_bp = Blueprint('memory', __name__, url_prefix='/api/memory')


# ============================================================
# AUTHORIZATION HELPERS
# ============================================================

def check_memory_authorization(patient_id, can_edit=False):
    """
    Verify authorization for memory operations.
    
    Returns: (is_authorized, error_response_tuple)
    
    Authorization rules:
    - Patient (role='patient'): can view own data only
    - Caregiver (role='caregiver'): can view/edit all patient data
    """
    
    # Check: user is logged in
    user_id = session.get('user_id')
    if not user_id:
        return False, ({"error": "Unauthorized"}, 401)
    
    # Validate patient_id is integer
    try:
        patient_id = int(patient_id)
    except (ValueError, TypeError):
        return False, ({"error": "Invalid patient ID"}, 400)
    
    # Get requesting user
    user = User.query.get(user_id)
    if not user:
        return False, ({"error": "Unauthorized"}, 401)
    
    # Case 1: Patient accessing their own memories (can view AND edit their own)
    if user.role == 'patient' and patient_id == user_id:
        return True, None
    
    # Case 2: Caregiver accessing patient's memories (full access)
    if user.role == 'caregiver':
        # Note: Future phase could add formal caregiver-patient mapping here
        # For now: caregivers can access all patients
        return True, None
    
    # All other cases: forbidden
    return False, ({"error": "Forbidden"}, 403)


# ============================================================
# PEOPLE ENDPOINTS (4)
# ============================================================

@memory_bp.route('/people', methods=['GET'])
def get_people():
    """
    Get all people for a patient.
    
    Query params: patient_id (required)
    """
    patient_id = request.args.get('patient_id', type=int)
    
    if patient_id is None:
        return jsonify({'error': 'patient_id parameter required'}), 400
    
    is_authorized, error = check_memory_authorization(patient_id, can_edit=False)
    if error:
        return error
    
    try:
        people = MemoryPerson.query.filter_by(
            patient_id=patient_id, 
            is_active=True
        ).all()
        
        return jsonify([p.to_dict() for p in people]), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to fetch people: {str(e)}'}), 500


@memory_bp.route('/people', methods=['POST'])
def create_person():
    """
    Create a new person record with optional photo.
    
    Expects: multipart/form-data with:
        - patient_id: int (required)
        - name: str (required)
        - relationship: str (required)
        - description: str (optional)
        - photo: file (optional, jpg/png/gif/webp, max 5MB)
    """
    
    patient_id = request.form.get('patient_id', type=int)
    
    if patient_id is None:
        return jsonify({'error': 'patient_id is required'}), 400
    
    is_authorized, error = check_memory_authorization(patient_id, can_edit=True)
    if error:
        return error
    
    # Extract form data
    name = request.form.get('name', '').strip()
    relationship = request.form.get('relationship', '').strip()
    description = request.form.get('description', '').strip()
    
    # Validate required fields
    if not name or not relationship:
        return jsonify({'error': 'Name and relationship are required'}), 400
    
    photo_path = None
    
    # Handle optional photo
    if 'photo' in request.files:
        file = request.files['photo']
        if file.filename:
            success, result = UploadHandler.save_file(file, patient_id, 'person')
            if not success:
                return jsonify({'error': f'Photo upload failed: {result}'}), 400
            photo_path = result
    
    try:
        person = MemoryPerson(
            patient_id=patient_id,
            name=name,
            relationship=relationship,
            description=description if description else None,
            photo=photo_path,
            is_active=True
        )
        db.session.add(person)
        db.session.commit()
        
        return jsonify(person.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create person: {str(e)}'}), 500


@memory_bp.route('/people/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    """
    Update a person record with optional photo replacement.
    
    Expects: multipart/form-data with:
        - patient_id: int (required)
        - name: str (optional)
        - relationship: str (optional)
        - description: str (optional)
        - photo: file (optional, replaces old photo)
    """
    
    patient_id = request.form.get('patient_id', type=int)
    
    if patient_id is None:
        return jsonify({'error': 'patient_id is required'}), 400
    
    is_authorized, error = check_memory_authorization(patient_id, can_edit=True)
    if error:
        return error
    
    person = MemoryPerson.query.get(person_id)
    if not person:
        return jsonify({'error': 'Person not found'}), 404
    
    # Verify ownership
    if person.patient_id != patient_id:
        return jsonify({'error': 'Forbidden'}), 403
    
    try:
        # Update fields if provided
        if 'name' in request.form:
            name = request.form.get('name', '').strip()
            if name:
                person.name = name
        
        if 'relationship' in request.form:
            relationship = request.form.get('relationship', '').strip()
            if relationship:
                person.relationship = relationship
        
        if 'description' in request.form:
            person.description = request.form.get('description', '').strip() or None
        
        # Handle photo replacement
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename:
                # Delete old photo if exists
                if person.photo:
                    UploadHandler.delete_file(person.photo)
                
                # Upload new photo
                success, result = UploadHandler.save_file(file, patient_id, 'person')
                if not success:
                    return jsonify({'error': f'Photo upload failed: {result}'}), 400
                person.photo = result
        
        person.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(person.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update person: {str(e)}'}), 500


@memory_bp.route('/people/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    """
    Delete/deactivate a person record.
    
    Query params: patient_id (required)
    """
    
    patient_id = request.args.get('patient_id', type=int)
    
    if patient_id is None:
        return jsonify({'error': 'patient_id parameter required'}), 400
    
    is_authorized, error = check_memory_authorization(patient_id, can_edit=True)
    if error:
        return error
    
    person = MemoryPerson.query.get(person_id)
    if not person:
        return jsonify({'error': 'Person not found'}), 404
    
    # Verify ownership
    if person.patient_id != patient_id:
        return jsonify({'error': 'Forbidden'}), 403
    
    try:
        # Delete photo if exists
        if person.photo:
            UploadHandler.delete_file(person.photo)
        
        db.session.delete(person)
        db.session.commit()
        
        return jsonify({'success': True}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete person: {str(e)}'}), 500


# ============================================================
# PLACES ENDPOINTS (4)
# ============================================================

@memory_bp.route('/places', methods=['GET'])
def get_places():
    """Get all places for a patient."""
    patient_id = request.args.get('patient_id', type=int)
    
    if patient_id is None:
        return jsonify({'error': 'patient_id parameter required'}), 400
    
    is_authorized, error = check_memory_authorization(patient_id, can_edit=False)
    if error:
        return error
    
    try:
        places = MemoryPlace.query.filter_by(
            patient_id=patient_id, 
            is_active=True
        ).all()
        
        return jsonify([p.to_dict() for p in places]), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to fetch places: {str(e)}'}), 500


@memory_bp.route('/places', methods=['POST'])
def create_place():
    """Create a new place record with optional photo."""
    
    patient_id = request.form.get('patient_id', type=int)
    
    if patient_id is None:
        return jsonify({'error': 'patient_id is required'}), 400
    
    is_authorized, error = check_memory_authorization(patient_id, can_edit=True)
    if error:
        return error
    
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not name:
        return jsonify({'error': 'Place name is required'}), 400
    
    photo_path = None
    
    if 'photo' in request.files:
        file = request.files['photo']
        if file.filename:
            success, result = UploadHandler.save_file(file, patient_id, 'place')
            if not success:
                return jsonify({'error': f'Photo upload failed: {result}'}), 400
            photo_path = result
    
    try:
        place = MemoryPlace(
            patient_id=patient_id,
            name=name,
            description=description if description else None,
            photo=photo_path,
            is_active=True
        )
        db.session.add(place)
        db.session.commit()
        
        return jsonify(place.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create place: {str(e)}'}), 500


@memory_bp.route('/places/<int:place_id>', methods=['PUT'])
def update_place(place_id):
    """Update a place record with optional photo replacement."""
    
    patient_id = request.form.get('patient_id', type=int)
    
    if patient_id is None:
        return jsonify({'error': 'patient_id is required'}), 400
    
    is_authorized, error = check_memory_authorization(patient_id, can_edit=True)
    if error:
        return error
    
    place = MemoryPlace.query.get(place_id)
    if not place:
        return jsonify({'error': 'Place not found'}), 404
    
    if place.patient_id != patient_id:
        return jsonify({'error': 'Forbidden'}), 403
    
    try:
        if 'name' in request.form:
            name = request.form.get('name', '').strip()
            if name:
                place.name = name
        
        if 'description' in request.form:
            place.description = request.form.get('description', '').strip() or None
        
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename:
                if place.photo:
                    UploadHandler.delete_file(place.photo)
                
                success, result = UploadHandler.save_file(file, patient_id, 'place')
                if not success:
                    return jsonify({'error': f'Photo upload failed: {result}'}), 400
                place.photo = result
        
        place.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(place.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update place: {str(e)}'}), 500


@memory_bp.route('/places/<int:place_id>', methods=['DELETE'])
def delete_place(place_id):
    """Delete/deactivate a place record."""
    
    patient_id = request.args.get('patient_id', type=int)
    
    if patient_id is None:
        return jsonify({'error': 'patient_id parameter required'}), 400
    
    is_authorized, error = check_memory_authorization(patient_id, can_edit=True)
    if error:
        return error
    
    place = MemoryPlace.query.get(place_id)
    if not place:
        return jsonify({'error': 'Place not found'}), 404
    
    if place.patient_id != patient_id:
        return jsonify({'error': 'Forbidden'}), 403
    
    try:
        if place.photo:
            UploadHandler.delete_file(place.photo)
        
        db.session.delete(place)
        db.session.commit()
        
        return jsonify({'success': True}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete place: {str(e)}'}), 500


# ============================================================
# MEMORIES ENDPOINTS (4)
# ============================================================

@memory_bp.route('/memories', methods=['GET'])
def get_memories():
    """Get all memories for a patient."""
    patient_id = request.args.get('patient_id', type=int)
    
    if patient_id is None:
        return jsonify({'error': 'patient_id parameter required'}), 400
    
    is_authorized, error = check_memory_authorization(patient_id, can_edit=False)
    if error:
        return error
    
    try:
        memories = MemoryItem.query.filter_by(
            patient_id=patient_id, 
            is_active=True
        ).all()
        
        return jsonify([m.to_dict() for m in memories]), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to fetch memories: {str(e)}'}), 500


@memory_bp.route('/memories', methods=['POST'])
def create_memory():
    """Create a new memory record with optional photo."""
    
    patient_id = request.form.get('patient_id', type=int)
    
    if patient_id is None:
        return jsonify({'error': 'patient_id is required'}), 400
    
    is_authorized, error = check_memory_authorization(patient_id, can_edit=True)
    if error:
        return error
    
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    memory_date_str = request.form.get('memory_date', '').strip()
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    memory_date = None
    if memory_date_str:
        try:
            from datetime import datetime as dt
            memory_date = dt.strptime(memory_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    photo_path = None
    
    if 'photo' in request.files:
        file = request.files['photo']
        if file.filename:
            success, result = UploadHandler.save_file(file, patient_id, 'memory')
            if not success:
                return jsonify({'error': f'Photo upload failed: {result}'}), 400
            photo_path = result
    
    try:
        memory = MemoryItem(
            patient_id=patient_id,
            title=title,
            description=description if description else None,
            photo=photo_path,
            memory_date=memory_date,
            is_active=True
        )
        db.session.add(memory)
        db.session.commit()
        
        return jsonify(memory.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create memory: {str(e)}'}), 500


@memory_bp.route('/memories/<int:memory_id>', methods=['PUT'])
def update_memory(memory_id):
    """Update a memory record with optional photo replacement."""
    
    patient_id = request.form.get('patient_id', type=int)
    
    if patient_id is None:
        return jsonify({'error': 'patient_id is required'}), 400
    
    is_authorized, error = check_memory_authorization(patient_id, can_edit=True)
    if error:
        return error
    
    memory = MemoryItem.query.get(memory_id)
    if not memory:
        return jsonify({'error': 'Memory not found'}), 404
    
    if memory.patient_id != patient_id:
        return jsonify({'error': 'Forbidden'}), 403
    
    try:
        if 'title' in request.form:
            title = request.form.get('title', '').strip()
            if title:
                memory.title = title
        
        if 'description' in request.form:
            memory.description = request.form.get('description', '').strip() or None
        
        if 'memory_date' in request.form:
            memory_date_str = request.form.get('memory_date', '').strip()
            if memory_date_str:
                try:
                    from datetime import datetime as dt
                    memory.memory_date = dt.strptime(memory_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
            else:
                memory.memory_date = None
        
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename:
                if memory.photo:
                    UploadHandler.delete_file(memory.photo)
                
                success, result = UploadHandler.save_file(file, patient_id, 'memory')
                if not success:
                    return jsonify({'error': f'Photo upload failed: {result}'}), 400
                memory.photo = result
        
        memory.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(memory.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update memory: {str(e)}'}), 500


@memory_bp.route('/memories/<int:memory_id>', methods=['DELETE'])
def delete_memory(memory_id):
    """Delete/deactivate a memory record."""
    
    patient_id = request.args.get('patient_id', type=int)
    
    if patient_id is None:
        return jsonify({'error': 'patient_id parameter required'}), 400
    
    is_authorized, error = check_memory_authorization(patient_id, can_edit=True)
    if error:
        return error
    
    memory = MemoryItem.query.get(memory_id)
    if not memory:
        return jsonify({'error': 'Memory not found'}), 404
    
    if memory.patient_id != patient_id:
        return jsonify({'error': 'Forbidden'}), 403
    
    try:
        if memory.photo:
            UploadHandler.delete_file(memory.photo)
        
        db.session.delete(memory)
        db.session.commit()
        
        return jsonify({'success': True}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete memory: {str(e)}'}), 500
