"""
Phase 1 Test Script: Create and verify sample database entries
Run this script to test that the database models work correctly.
"""

from app import app, db
from models.models import User, ActivityLog, Reminder

def seed_database():
    """Create sample data and verify it works"""
    with app.app_context():
        # Clear existing data (optional, for testing)
        # db.drop_all()
        # db.create_all()
        
        print("=" * 60)
        print("MEMORA Phase 1 Database Test")
        print("=" * 60)
        
        # 1. Create a sample User
        print("\n[1] Creating sample User...")
        user = User(
            name="Test Patient",
            role="patient",
            pin="1234",
            preferred_language="en"
        )
        db.session.add(user)
        db.session.flush()  # Get the user ID without committing yet
        print(f"✓ Created: {user}")
        
        # 2. Create a sample Reminder for the user
        print("\n[2] Creating sample Reminder...")
        reminder = Reminder(
            user_id=user.id,
            title="Take medicine",
            type="medicine",
            time="09:00",
            is_done=False
        )
        db.session.add(reminder)
        db.session.flush()
        print(f"✓ Created: {reminder}")
        
        # 3. Create a sample ActivityLog for the user
        print("\n[3] Creating sample ActivityLog...")
        activity_log = ActivityLog(
            user_id=user.id,
            game_type="memory_match",
            score=80,
            accuracy=75.5,
            time_taken=45.2,
            difficulty="medium"
        )
        db.session.add(activity_log)
        db.session.flush()
        print(f"✓ Created: {activity_log}")
        
        # Commit all changes
        print("\n[4] Committing to database...")
        db.session.commit()
        print("✓ All changes committed!")
        
        # 5. Query and display all data
        print("\n" + "=" * 60)
        print("QUERY RESULTS")
        print("=" * 60)
        
        # Query all users
        print("\n[Users]")
        users = User.query.all()
        for u in users:
            print(f"  {u} -> {u.to_dict()}")
        
        # Query all reminders
        print("\n[Reminders]")
        reminders = Reminder.query.all()
        for r in reminders:
            print(f"  {r} -> {r.to_dict()}")
        
        # Query all activity logs
        print("\n[Activity Logs]")
        logs = ActivityLog.query.all()
        for log in logs:
            print(f"  {log} -> {log.to_dict()}")
        
        # Query reminders for the specific user
        print(f"\n[Reminders for User {user.id}]")
        user_reminders = user.reminders
        for r in user_reminders:
            print(f"  {r}")
        
        # Query activity logs for the specific user
        print(f"\n[Activity Logs for User {user.id}]")
        user_logs = user.activity_logs
        for log in user_logs:
            print(f"  {log}")
        
        print("\n" + "=" * 60)
        print("✅ Phase 1 Database Test Complete!")
        print("=" * 60)

if __name__ == '__main__':
    seed_database()
