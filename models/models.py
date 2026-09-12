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
