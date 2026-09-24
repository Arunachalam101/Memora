#!/usr/bin/env python3
"""
Seed Demo Data for MEMORA
Generates clean demo database with sample patient/caregiver data
and demo activity logs showing improvement trend
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app import app, db
from models.models import User, ActivityLog, Reminder, MemoryPerson, MemoryPlace, MemoryItem

DB_PATH = Path(__file__).parent / 'data' / 'memora.sqlite'


def clean_database():
    """Drop all tables and recreate them"""
    print("🔄 Cleaning database...")
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✓ Database cleaned and recreated")


def create_demo_users():
    """Create patient and caregiver users"""
    print("\n👥 Creating demo users...")
    with app.app_context():
        # Create patient user
        patient = User(
            name="Priya Devi",
            role="patient",
            pin="1234",
            preferred_language="en"
        )
        db.session.add(patient)
        
        # Create caregiver user
        caregiver = User(
            name="Anil Sharma",
            role="caregiver",
            pin="5678",
            preferred_language="en"
        )
        db.session.add(caregiver)
        
        db.session.commit()
        
        print(f"✓ Patient created: {patient.name} (ID: {patient.id})")
        print(f"✓ Caregiver created: {caregiver.name} (ID: {caregiver.id})")
        
        return patient, caregiver


def create_reminders(patient):
    """Create demo reminders for the patient"""
    print("\n🔔 Creating demo reminders...")
    with app.app_context():
        reminders = [
            Reminder(
                user_id=patient.id,
                title="Take Morning Medication",
                type="medicine",
                time="08:30",
                is_done=True
            ),
            Reminder(
                user_id=patient.id,
                title="Doctor's Appointment",
                type="appointment",
                time="14:00",
                is_done=True
            ),
            Reminder(
                user_id=patient.id,
                title="Afternoon Walk",
                type="activity",
                time="15:30",
                is_done=False
            ),
            Reminder(
                user_id=patient.id,
                title="Take Evening Medication",
                type="medicine",
                time="19:00",
                is_done=False
            ),
            Reminder(
                user_id=patient.id,
                title="Family Video Call",
                type="activity",
                time="20:00",
                is_done=False
            ),
        ]
        
        for reminder in reminders:
            db.session.add(reminder)
        
        db.session.commit()
        print(f"✓ Created {len(reminders)} reminders")


def create_activity_logs(patient):
    """Create demo activity logs with upward trending scores"""
    print("\n🎮 Creating demo activity logs...")
    with app.app_context():
        now = datetime.utcnow()
        activities = []
        
        # Generate 15 activity logs over the last 9 days
        # with upward trending scores and progressive difficulty
        game_types = ["memory_match", "attention_test"]
        difficulties = ["easy", "medium", "hard"]
        
        base_scores = {
            "memory_match": [45, 52, 58, 65, 72, 78, 85],
            "attention_test": [50, 56, 62, 70, 76, 82, 88]
        }
        
        for day_offset in range(9, 0, -1):
            timestamp = now - timedelta(days=day_offset)
            
            for game_idx, game_type in enumerate(game_types):
                # Alternate games across days for variety
                if (day_offset + game_idx) % 2 == 0:
                    continue
                
                # Calculate score based on progression
                progression_step = (9 - day_offset)
                if progression_step < 3:
                    base_score = base_scores[game_type][0]
                    difficulty = "easy"
                    accuracy_offset = 2
                elif progression_step < 6:
                    base_score = base_scores[game_type][3]
                    difficulty = "medium"
                    accuracy_offset = 4
                else:
                    base_score = base_scores[game_type][6]
                    difficulty = "hard"
                    accuracy_offset = 6
                
                # Add some randomness to make it realistic
                import random
                score = base_score + random.randint(-5, 8)
                accuracy = min(95, 60 + progression_step * 3 + random.randint(-3, 5))
                time_taken = random.uniform(20, 90)
                
                activity = ActivityLog(
                    user_id=patient.id,
                    game_type=game_type,
                    score=score,
                    accuracy=accuracy,
                    time_taken=time_taken,
                    difficulty=difficulty,
                    timestamp=timestamp
                )
                activities.append(activity)
        
        # Sort by timestamp to ensure chronological order
        activities.sort(key=lambda x: x.timestamp)
        
        for activity in activities:
            db.session.add(activity)
        
        db.session.commit()
        
        print(f"✓ Created {len(activities)} activity logs with upward trending data")
        print("  • Difficulty progression: easy → medium → hard")
        print("  • Accuracy trend: 60-95%")
        print("  • Score trend: +30-40 points over 9 days")


def create_demo_memories(patient):
    """Create demo memory records for the patient - Phase 10A"""
    print("\n📸 Creating demo memory records...")
    with app.app_context():
        # Demo people
        people = [
            MemoryPerson(
                patient_id=patient.id,
                name="Anil Sharma",
                relationship="Son",
                description="Lives in Delhi, works in software engineering. Loves gardening and cooking."
            ),
            MemoryPerson(
                patient_id=patient.id,
                name="Lakshmi Devi",
                relationship="Mother",
                description="Lives in Punjab. Enjoys reading and playing with grandchildren."
            ),
            MemoryPerson(
                patient_id=patient.id,
                name="Ravi Kumar",
                relationship="Brother",
                description="Lives in Mumbai. Retired from banking. Likes playing cricket."
            ),
        ]
        
        # Demo places
        places = [
            MemoryPlace(
                patient_id=patient.id,
                name="Home",
                description="3-room apartment in New Delhi. Where family gathers during festivals."
            ),
            MemoryPlace(
                patient_id=patient.id,
                name="Local Hospital",
                description="Apollo Hospital, Sector 5. Regular check-ups every 3 months."
            ),
            MemoryPlace(
                patient_id=patient.id,
                name="Temple",
                description="Sri Veerabhadreshwara Temple nearby. Visits every Sunday morning."
            ),
        ]
        
        # Demo memories
        from datetime import datetime
        memories = [
            MemoryItem(
                patient_id=patient.id,
                title="Family Function",
                description="Memorable reunion with all family members. Everyone gathered at home for Diwali celebration.",
                memory_date=datetime(2024, 11, 1).date()
            ),
            MemoryItem(
                patient_id=patient.id,
                title="Birthday Party",
                description="Grandchildren came over and sang birthday songs. Had delicious homemade kheer.",
                memory_date=datetime(2024, 9, 15).date()
            ),
            MemoryItem(
                patient_id=patient.id,
                title="Festival Celebration",
                description="Celebrated Holi with colors and traditional food. The whole neighborhood joined in the festivities.",
                memory_date=datetime(2024, 3, 25).date()
            ),
        ]
        
        # Add all records to database
        for person in people:
            db.session.add(person)
        
        for place in places:
            db.session.add(place)
        
        for memory in memories:
            db.session.add(memory)
        
        db.session.commit()
        
        print(f"✓ Created {len(people)} people records")
        print(f"✓ Created {len(places)} place records")
        print(f"✓ Created {len(memories)} memory records")


def main():
    """Main function to seed database"""
    print("=" * 70)
    print("🧠 MEMORA DEMO DATA SEEDER")
    print("=" * 70)
    
    # Check if database exists
    if DB_PATH.exists():
        print(f"\n📁 Existing database found at: {DB_PATH}")
        response = input("Delete and recreate? (y/n): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return
    
    # Clean and recreate database
    clean_database()
    
    # Create demo data
    patient, caregiver = create_demo_users()
    create_reminders(patient)
    create_activity_logs(patient)
    create_demo_memories(patient)
    
    # Print summary
    print("\n" + "=" * 70)
    print("✅ DEMO DATA SEEDING COMPLETE")
    print("=" * 70)
    print("\n📊 Demo Account Information:")
    print(f"  Patient: {patient.name} (ID: {patient.id}, PIN: 1234)")
    print(f"  Caregiver: {caregiver.name} (ID: {caregiver.id}, PIN: 5678)")
    print("\n🎮 Demo includes:")
    print("  • 5 reminders (mix of done/pending)")
    print("  • 15 activity logs (7-10 days, upward trending)")
    print("  • Score progression: showing improvement story")
    print("  • Difficulty: easy → medium → hard")
    print("  • Phase 10A Memory Album:")
    print("    - 3 people (family members)")
    print("    - 3 places (important locations)")
    print("    - 3 memories (important events with dates)")
    print("\n🚀 Next steps:")
    print("  1. Run: python app.py")
    print("  2. Login as 'Priya Devi' (patient)")
    print("  3. Or login as 'Anil Sharma' (caregiver)")
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
