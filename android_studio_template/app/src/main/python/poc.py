"""Minimal Chaquopy + Flask proof-of-concept for MEMORA Android build."""
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


def start():
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False, threaded=True)
