"""
Shared pytest configuration for MEMORA.

1. DATABASE ISOLATION
   The test fixtures call ``db.drop_all()``.  Flask-SQLAlchemy 3.x creates the
   engine inside ``db.init_app(app)``, so overriding SQLALCHEMY_DATABASE_URI
   *afterwards* has no effect and the tests used to wipe the real
   ``data/memora.sqlite``.  DATABASE_URL is now pointed at a throw-away file
   BEFORE the application is imported, so the real database is never touched.

2. LIVE-SERVER TESTS
   Several legacy scripts (test_e2e.py, test_requirements.py, ...) talk to a
   running server on http://127.0.0.1:5000 using ``requests`` (some at import
   time).  They are skipped automatically when no server is reachable.
"""
import os
import socket
import tempfile

_TMP_DIR = tempfile.mkdtemp(prefix="memora_tests_")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{os.path.join(_TMP_DIR, 'test.sqlite')}")

LIVE_SERVER = ("127.0.0.1", 5000)


def _server_running():
    try:
        with socket.create_connection(LIVE_SERVER, timeout=0.5):
            return True
    except OSError:
        return False


def pytest_ignore_collect(collection_path, config):
    """Skip live-server scripts (they call the server at import time) if it is down."""
    path = str(collection_path)
    if not path.endswith(".py") or os.path.basename(path) == "conftest.py" or _server_running():
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            source = fh.read()
    except OSError:
        return None
    if "127.0.0.1:5000" in source or "localhost:5000" in source:
        return True
    return None