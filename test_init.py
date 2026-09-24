#!/usr/bin/env python
"""Quick app initialization test"""
from app import app, db

try:
    print("✅ App imported successfully")
    with app.app_context():
        db.create_all()
        print("✅ Database initialized successfully")
    print("✅ All systems ready!")
except Exception as e:
    print(f"❌ Error: {e}")
    raise
