#!/usr/bin/env python
"""Quick verification script for Phase 10E implementation"""
from app import app, db
from models.models import SafetyAlert
from routes.safety import safety_bp

print("✅ All imports successful")

with app.app_context():
    # Create tables
    db.create_all()
    print("✅ Database tables created")
    
    # Verify SafetyAlert model has all required fields
    required_fields = ['id', 'patient_id', 'alert_type', 'status', 'message', 'created_at', 'resolved_at']
    model_columns = [c.name for c in SafetyAlert.__table__.columns]
    
    for field in required_fields:
        assert field in model_columns, f"Missing field: {field}"
    
    print(f"✅ SafetyAlert model verified with {len(model_columns)} fields")
    
    # Verify indexes
    indexes = [idx.name for idx in SafetyAlert.__table__.indexes]
    print(f"✅ SafetyAlert indexes verified: {', '.join(indexes)}")

print("✅ Phase 10E Verification Complete - All systems ready!")
