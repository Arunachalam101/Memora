# 🧠 MEMORA - Cognitive Support for Dementia Care

**Smart Hackathon India 2026 (SIH26003)**

MEMORA is an AI-powered cognitive support system designed for dementia patients and their caregivers. It combines cognitive games, reminders, and voice assistance to provide a holistic care experience with regional language support and adaptive difficulty levels.

---

## 🎯 Features

### For Patients
- **Cognitive Games**: Memory Match and Attention Test games with adaptive difficulty
- **Smart Reminders**: Personalized reminders for medicines, appointments, and activities
- **Voice Assistant**: Hands-free voice interaction for game guidance
- **Progress Tracking**: Visual dashboard showing cognitive improvements
- **Regional Language Support**: Full interface support for English and Assamese
- **Session Persistence**: Secure login system with PIN-based authentication

### For Caregivers
- **Patient Dashboard**: Monitor multiple patients' cognitive progress
- **Progress Charts**: Visual trend analysis of accuracy, scores, and difficulty levels
- **Activity Logs**: Comprehensive record of all patient activities
- **Easy Patient Selection**: Dropdown menu to quickly switch between patients

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.13.7** (or higher)
- **pip** (Python package manager)
- **Git** (optional, for cloning the repository)

### 1. **Setup Virtual Environment**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On Windows (Command Prompt):
.\venv\Scripts\activate.bat

# On macOS/Linux:
source venv/bin/activate
```

### 2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 3. **Create Demo Database**

Generate sample data for demo purposes:

```bash
# On Windows:
.\venv\Scripts\python.exe seed_demo_data.py

# On macOS/Linux:
python seed_demo_data.py
```

This will:
- Create a fresh SQLite database (`data/memora.sqlite`)
- Add 2 demo users (patient and caregiver)
- Generate 5 sample reminders
- Create 15 activity logs showing cognitive improvement trends

### 4. **Start the Application**

```bash
# On Windows:
.\venv\Scripts\python.exe app.py

# On macOS/Linux:
python app.py
```

The application will start at: **http://localhost:5000**

---

## 👥 Demo Credentials

After running `seed_demo_data.py`, use these credentials to explore the application:

### Patient Account
- **Name**: Priya Devi
- **PIN**: `1234`
- **Role**: Patient
- **Access**: Home page, games, reminders, voice assistant

### Caregiver Account
- **Name**: Anil Sharma
- **PIN**: `5678`
- **Role**: Caregiver
- **Access**: Caregiver dashboard, patient progress tracking

---

## 📋 Demo Walkthrough

### 1. **Login Screen** (0 min)
```
→ Navigate to http://localhost:5000
→ You'll be redirected to the login page
```

### 2. **Patient Flow** (5 mins)
```
1. Login as Priya Devi (PIN: 1234)
2. View patient home page with:
   - 5 reminders (medicines, appointments, activities)
   - Quick access to games
   - Voice assistant button
3. Click "Play Games" → Games Hub
4. Choose:
   - 🎮 Memory Match: Flip cards to find matching pairs
   - 👁️ Attention Test: Find the odd one out
5. Play a game → See your score and progress
6. Return to home → View updated reminders
7. Toggle language: EN / องส (top-right navbar)
8. Logout
```

### 3. **Caregiver Flow** (3 mins)
```
1. Login as Anil Sharma (PIN: 5678)
2. View Caregiver Dashboard with:
   - Patient selector dropdown
   - Accuracy trend chart (60% → 95%)
   - Score trend chart (45 → 88)
   - Full activity log table
3. Click on patient dropdown → See all available patients
4. Observe upward trending data (showing improvement)
5. Check individual activity records
6. Logout
```

### 4. **Language Toggle** (1 min)
```
1. From any logged-in page
2. Click "EN" or "องස" in top-right navbar
3. Observe all UI text changes
4. Check that preference persists (reload page)
```

### 5. **Error Handling** (Optional)
```
1. Try accessing /invalid-page → See friendly 404 error page
2. Network error (if possible) → See inline error message
3. Language loading failure → See graceful fallback to English
```

---

## 🏗️ Project Structure

```
memora/
├── app.py                    # Flask application entry point
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── seed_demo_data.py         # Demo data generation script
├── README.md                 # This file
│
├── models/
│   └── models.py            # SQLAlchemy database models
│
├── routes/
│   ├── users.py             # Authentication and user routes
│   ├── reminders.py         # Reminder API endpoints
│   ├── games.py             # Game endpoints
│   └── progress.py          # Progress tracking endpoints
│
├── data/
│   └── memora.sqlite        # SQLite database (created at runtime)
│
├── templates/
│   ├── base.html            # Base layout template
│   ├── login.html           # Login page
│   ├── patient_home.html    # Patient dashboard
│   ├── games_hub.html       # Game selection page
│   ├── game_memory_match.html # Memory game
│   ├── game_attention_test.html # Attention game
│   ├── caregiver_dashboard.html # Caregiver monitoring
│   └── error.html           # Error pages (404, 500)
│
├── static/
│   ├── css/
│   │   └── style.css        # All styling
│   ├── js/
│   │   ├── error_handler.js    # Error and loading state management
│   │   ├── reminders.js        # Reminder functionality
│   │   ├── games.js            # Game utilities
│   │   ├── memory_match.js     # Memory game logic
│   │   ├── attention_test.js   # Attention game logic
│   │   ├── dashboard_chart.js  # Caregiver dashboard charts
│   │   ├── voice_assistant.js  # Voice interaction
│   │   └── i18n.js             # Internationalization
│   └── images/              # Image assets (if needed)
│
└── instance/                # Flask instance folder (created at runtime)
```

---

## 🗄️ Database Schema

### Users Table
```sql
id (Primary Key)
name (String) - User's full name
pin (String, nullable) - PIN for login
role (String) - 'patient' or 'caregiver'
preferred_language (String) - 'en' or 'as'
created_at (DateTime)
```

### Reminders Table
```sql
id (Primary Key)
user_id (Foreign Key)
title (String) - Reminder text
type (String) - 'medicine' | 'appointment' | 'activity'
time (String) - HH:MM format
is_done (Boolean)
created_at (DateTime)
```

### ActivityLog Table
```sql
id (Primary Key)
user_id (Foreign Key)
game_type (String) - 'memory_match' | 'attention_test'
score (Integer) - 0-100
accuracy (Float) - 0-100%
time_taken (Integer) - seconds
difficulty (String) - 'easy' | 'medium' | 'hard'
timestamp (DateTime)
```

---

## 🔧 API Endpoints

### Authentication
- `POST /login` - User login
- `GET /logout` - User logout
- `GET /patient_home` - Patient dashboard
- `GET /caregiver_dashboard` - Caregiver dashboard

### Reminders
- `GET /api/reminders` - Fetch user's reminders
- `POST /api/reminders` - Create reminder
- `PUT /api/reminders/<id>` - Update reminder
- `DELETE /api/reminders/<id>` - Delete reminder

### Games
- `POST /api/games/log` - Log game result
- `GET /api/difficulty/<user_id>` - Get adaptive difficulty

### Progress
- `GET /api/progress/<patient_id>` - Get patient activity logs
- `GET /api/users/patients` - Get list of all patients

### Settings
- `PATCH /api/user/language` - Update language preference

---

## 🌍 Supported Languages

| Language | Code | Status |
|----------|------|--------|
| English | `en` | ✅ Full Support |
| Assamese | `as` | ✅ Full Support (84 keys) |

Language preference is saved to:
- LocalStorage (browser)
- Database (user account)

---

## 🎮 Game Details

### Memory Match
- **Objective**: Flip cards to find matching emoji pairs
- **Scoring**: Based on accuracy and speed
- **Difficulty Levels**:
  - 🟢 Easy (4 pairs, 8 cards)
  - 🟡 Medium (6 pairs, 12 cards)
  - 🔴 Hard (8 pairs, 16 cards)

### Attention Test
- **Objective**: Find the odd one out among shapes
- **Scoring**: Based on reaction time and accuracy
- **Difficulty Levels**:
  - 🟢 Easy (6 rounds, 8 shapes)
  - 🟡 Medium (8 rounds, 12 shapes)
  - 🔴 Hard (10 rounds, 16 shapes)

---

## 🔐 Security Features

- **PIN-Based Authentication**: Secure login system
- **Session Management**: Flask session-based authentication
- **Role-Based Access**: Patient vs Caregiver routes
- **CSRF Protection**: Ready for production deployment
- **Input Validation**: All user inputs validated

---

## 📈 Technology Stack

### Backend
- **Flask 3.0.0** - Web framework
- **Flask-SQLAlchemy 3.1.1** - ORM
- **SQLite** - Database
- **Python 3.13.7** - Runtime

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Styling with CSS variables
- **Vanilla JavaScript** - No dependencies
- **Chart.js** - Data visualization
- **Fetch API** - AJAX calls
- **Web Speech API** - Voice interaction

### DevOps
- **No external APIs required** - All services self-contained
- **Single database file** - Easy backup and deployment
- **No authentication services** - PIN-based login built-in

---

## 🛠️ Development Commands

### Run with Debug Mode
```bash
python app.py
```
Starts server at `http://localhost:5000` with auto-reload

### Run Tests (if added)
```bash
python -m pytest
```

### Reset Database
```bash
# Remove old database
rm data/memora.sqlite

# Regenerate
python seed_demo_data.py
```

### Lint & Format (optional)
```bash
pip install black pylint
black *.py
```

---

## 📱 Device Compatibility

MEMORA is tested and optimized for:
- 🖥️ **Desktop**: 1920px, 1440px, 1024px width
- 📱 **Tablet**: 768px width
- 📱 **Mobile**: 375px-480px width
- **Browsers**: Chrome, Edge, Firefox, Safari (latest versions)

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'flask'"
**Solution**: Ensure virtual environment is activated and dependencies installed
```bash
.\venv\Scripts\activate.bat  # Windows
pip install -r requirements.txt
```

### Issue: "Port 5000 already in use"
**Solution**: Change port in `app.py`
```python
app.run(debug=True, port=5001)  # Use different port
```

### Issue: "database is locked"
**Solution**: Close other connections and try again
```bash
# On Windows: restart Python
# Or delete and regenerate
rm data/memora.sqlite
python seed_demo_data.py
```

### Issue: "Language file not found"
**Solution**: Ensure `static/i18n/en.json` and `static/i18n/as.json` exist
```bash
ls static/i18n/  # Verify files
```

---

## 📊 Demo Data Characteristics

The seed data is specifically designed to tell a compelling "improvement story" for judges:

- **Score Progression**: 45 → 88 (96% improvement)
- **Accuracy Trend**: 60% → 95% (58% improvement)
- **Difficulty Adaptation**: easy → medium → hard
- **Timeline**: 9 days of daily entries
- **Game Variety**: Alternating memory_match and attention_test
- **Realistic Variance**: Random ±5% for authenticity

---

## 🎓 Educational Purpose

This project is built for the Smart Hackathon India 2026 competition and demonstrates:
- ✅ Full-stack web development
- ✅ Database design and ORM
- ✅ User authentication
- ✅ RESTful API design
- ✅ Frontend accessibility
- ✅ Internationalization (i18n)
- ✅ Responsive design
- ✅ Error handling
- ✅ Adaptive algorithms (difficulty)
- ✅ Real-time data visualization

---

## 📝 License

This project is submitted to Smart Hackathon India 2026 (SIH26003).

---

## 👥 Team

**MEMORA** is developed as part of the Smart Hackathon India 2026 initiative to leverage technology for elder care and cognitive support in dementia management.

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review console logs (Press F12 in browser)
3. Check server terminal output
4. Verify database exists: `data/memora.sqlite`

---

**Last Updated**: Phase 9 (Final Polish for Demo)
**Status**: Ready for SIH26003 Judge Presentation ✅
