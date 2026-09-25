"""Android-specific launcher for the real MEMORA Flask application.

Called from FlaskService via Chaquopy with the app's writable
internal-storage directory (Context.getFilesDir()).
"""
import os


def start(app_data_dir):
    data_dir = os.path.join(app_data_dir, "data")
    uploads_dir = os.path.join(app_data_dir, "uploads")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(uploads_dir, exist_ok=True)

    # Config.SQLALCHEMY_DATABASE_URI already honors DATABASE_URL if set.
    db_path = os.path.join(data_dir, "memora.sqlite")
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    from app import app, db
    from utils.upload_handler import UploadHandler

    # Writable directory for uploaded photos (bundled app.root_path is read-only on Android).
    app.config["UPLOAD_ROOT"] = uploads_dir
    app.config["DEBUG"] = False
    UploadHandler.init_app(app)  # re-run now that UPLOAD_ROOT is set, so the dir actually exists

    with app.app_context():
        db.create_all()
        _seed_default_accounts(db)

    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False, threaded=True)


def _seed_default_accounts(db):
    """Seed a built-in caregiver + demo patient on first run, so a fresh
    Android install always has a caregiver account to log into."""
    from models.models import User

    if User.query.filter_by(role="caregiver").first() is None:
        db.session.add(User(name="Caregiver", pin="0000", role="caregiver"))
    if User.query.filter_by(role="patient").first() is None:
        db.session.add(User(name="Demo Patient", pin="1234", role="patient"))
    db.session.commit()
