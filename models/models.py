from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    """User model for patients and caregivers"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    pin = db.Column(db.String(10), nullable=True)
    role = db.Column(db.String(20), default='patient')  # "patient" or "caregiver"
    preferred_language = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    activity_logs = db.relationship('ActivityLog', backref='user', lazy=True, cascade='all, delete-orphan')
    reminders = db.relationship('Reminder', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User {self.id}: {self.name} ({self.role})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'preferred_language': self.preferred_language,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ActivityLog(db.Model):
    """Game activity log for tracking user performance"""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_type = db.Column(db.String(50), nullable=False)  # "memory_match", "attention_test", etc.
    score = db.Column(db.Integer, nullable=False)
    accuracy = db.Column(db.Float, nullable=False)  # 0-100 percentage
    time_taken = db.Column(db.Float, nullable=False)  # seconds
    difficulty = db.Column(db.String(20), nullable=False)  # "easy", "medium", "hard"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ActivityLog {self.id}: {self.game_type} score={self.score}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'game_type': self.game_type,
            'score': self.score,
            'accuracy': self.accuracy,
            'time_taken': self.time_taken,
            'difficulty': self.difficulty,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class Reminder(db.Model):
    """Reminders for users (medicine, appointments, activities, etc.)"""
    __tablename__ = 'reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # "medicine", "appointment", "activity"
    time = db.Column(db.String(5), nullable=False)  # "HH:MM" format
    is_done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Reminder {self.id}: {self.title} at {self.time}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'type': self.type,
            'time': self.time,
            'is_done': self.is_done,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============================================================
# PHASE 10A - MEMORY FOUNDATION
# ============================================================

class MemoryPerson(db.Model):
    """Family members and important people in patient's life"""
    __tablename__ = 'memory_people'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), 
                           nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    relationship = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    photo = db.Column(db.String(500))  # Relative path only
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                           onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='memory_people')
    
    def __repr__(self):
        return f"<MemoryPerson {self.id}: {self.name}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'relationship': self.relationship,
            'description': self.description,
            'photo': self.photo,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class MemoryPlace(db.Model):
    """Important places in patient's life"""
    __tablename__ = 'memory_places'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), 
                           nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    photo = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                           onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='memory_places')
    
    def __repr__(self):
        return f"<MemoryPlace {self.id}: {self.name}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'photo': self.photo,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class MemoryItem(db.Model):
    """Important memories and events"""
    __tablename__ = 'memory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), 
                           nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    photo = db.Column(db.String(500))
    memory_date = db.Column(db.Date)  # Optional
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                           onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='memory_items')
    
    def __repr__(self):
        return f"<MemoryItem {self.id}: {self.title}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'photo': self.photo,
            'memory_date': self.memory_date.isoformat() if self.memory_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# ============================================================
# PHASE 10D - MOOD TRACKING
# ============================================================

class MoodEntry(db.Model):
    """Patient mood tracking entries"""
    __tablename__ = 'mood_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), 
                           nullable=False, index=True)
    mood = db.Column(db.String(20), nullable=False)
    # Values: "very_happy", "happy", "okay", "sad", "very_sad"
    note = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                           onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='mood_entries')
    
    def __repr__(self):
        return f"<MoodEntry {self.id}: patient_id={self.patient_id} mood={self.mood} at {self.timestamp}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'mood': self.mood,
            'note': self.note,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============================================================
# PHASE 10E - SAFETY & CAREGIVER SUPPORT
# ============================================================

class SafetyAlert(db.Model):
    """Safety alerts for emergency situations and patient monitoring"""
    __tablename__ = 'safety_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), 
                           nullable=False, index=True)
    alert_type = db.Column(db.String(50), nullable=False)  # "emergency"
    status = db.Column(db.String(20), nullable=False, default='active')  # "active" or "resolved"
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship('User', backref='safety_alerts')
    
    def __repr__(self):
        return f"<SafetyAlert {self.id}: patient_id={self.patient_id} type={self.alert_type} status={self.status}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'alert_type': self.alert_type,
            'status': self.status,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }
