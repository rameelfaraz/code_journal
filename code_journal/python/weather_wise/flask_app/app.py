"""Flask app with single-city weather search (Jinja)."""
import os
import sys

from flask import Flask, render_template, request

BASE_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
STATIC_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "static"))

sys.path.insert(0, PROJECT_ROOT)
from weather_core import fetch_weather_for_city  

app = Flask(__name__, template_folder="templates", static_folder=STATIC_DIR)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        city = (request.form.get("city") or "").strip()
        if city:
            result = fetch_weather_for_city(city)
        else:
            result = {"error": "Please enter a city name."}
    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
