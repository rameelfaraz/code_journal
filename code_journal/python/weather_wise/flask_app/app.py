"""Flask entry point for Weather Wise."""

import os
import sys

from flask import Flask, jsonify, render_template, request

BASE_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
STATIC_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "static"))

sys.path.insert(0, PROJECT_ROOT)
from weather_core import fetch_weather_for_city  

app = Flask(__name__, template_folder="templates", static_folder=STATIC_DIR)

CITY_MAX_LENGTH = 80
COUNTRY_MAX_LENGTH = 60
CITY_EXTRA_CHARS = ".'-,"
COUNTRY_EXTRA_CHARS = ".'-"


def _is_valid_name(value, extra_chars, max_length):
    """Letters (any language), spaces, and a small set of punctuation; at least 2 letters."""
    cleaned = " ".join(str(value or "").strip().split())
    if not cleaned or len(cleaned) > max_length:
        return False

    letter_count = 0
    for character in cleaned:
        if character.isalpha():
            letter_count += 1
        elif character.isspace() or character in extra_chars:
            continue
        else:
            return False

    return letter_count >= 2


def is_valid_city_name(city_name):
    return _is_valid_name(city_name, CITY_EXTRA_CHARS, CITY_MAX_LENGTH)


def is_valid_country_name(country_name):
    return _is_valid_name(country_name, COUNTRY_EXTRA_CHARS, COUNTRY_MAX_LENGTH)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/weather")
def api_weather():
    city = request.args.get("city", "")
    country = request.args.get("country", "")

    if not is_valid_city_name(city) or not is_valid_country_name(country):
        return jsonify({
            "error": "Please enter a valid city and country name."
        }), 400

    return jsonify(fetch_weather_for_city(city, country))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = "PORT" not in os.environ
    app.run(host="0.0.0.0", port=port, debug=debug)
