"""Minimal Flask shell for Weather Wise."""
import os
import sys
from flask import Flask, render_template

BASE_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
STATIC_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "static"))
sys.path.insert(0, PROJECT_ROOT)

app = Flask(__name__, template_folder="templates", static_folder=STATIC_DIR)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
