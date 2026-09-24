import os
from flask import Flask
from config import Config

# Create data/ folder FIRST, before anything else
os.makedirs('data', exist_ok=True)

from models.models import db
from routes.users import users_bp
from routes.reminders import reminders_bp
from routes.games import games_bp
from routes.progress import progress_bp
from routes.memory import memory_bp
from routes.memory_assistance import memory_assistance_bp
from routes.mood import mood_bp
from routes.safety import safety_bp
from utils.upload_handler import UploadHandler

app = Flask(__name__)
app.config.from_object(Config)

# Set secret key for session management
app.secret_key = Config.SECRET_KEY

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(users_bp)
app.register_blueprint(reminders_bp)
app.register_blueprint(games_bp)
app.register_blueprint(progress_bp)
app.register_blueprint(memory_bp)
app.register_blueprint(memory_assistance_bp)
app.register_blueprint(mood_bp)
app.register_blueprint(safety_bp)

# Initialize upload handler
UploadHandler.init_app(app)

@app.route('/')
def index():
    from flask import session, redirect, url_for
    # If user is logged in, redirect to patient home
    if 'user_id' in session:
        return redirect(url_for('users.patient_home'))
    # Otherwise, redirect to login
    return redirect(url_for('users.login'))

# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors (page not found)"""
    from flask import render_template
    return render_template('error.html',
                         error_code=404,
                         error_title='Page Not Found',
                         error_message='The page you are looking for does not exist.',
                         error_details='Try going to the home page or logging in again.'), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors (server errors)"""
    from flask import render_template
    return render_template('error.html',
                         error_code=500,
                         error_title='Server Error',
                         error_message='Something went wrong on our end.',
                         error_details='Our team has been notified. Please try again later.'), 500

@app.errorhandler(Exception)
def handle_exception(error):
    """Catch any unhandled exceptions"""
    import traceback
    traceback.print_exc()
    
    from flask import render_template, request, jsonify
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': 'An unexpected error occurred'}), 500
    
    # For regular pages, show error template
    return render_template('error.html',
                         error_code=500,
                         error_title='Unexpected Error',
                         error_message='An unexpected error occurred.',
                         error_details='Please refresh the page or contact support if the problem persists.'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
