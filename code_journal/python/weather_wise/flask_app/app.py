"""Flask app with search, compare, and history — card layout UI."""
import os
import sys

from flask import Flask, render_template, request

BASE_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
STATIC_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "static"))

sys.path.insert(0, PROJECT_ROOT)
from weather_core import fetch_weather_for_city, get_search_history 

app = Flask(__name__, template_folder="templates", static_folder=STATIC_DIR)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    compare_results = None

    if request.method == "POST":
        form_type = request.form.get("form_type", "search")

        if form_type == "search":
            city = (request.form.get("city") or "").strip()
            if city:
                result = fetch_weather_for_city(city)
            else:
                result = {"error": "Please enter a city name."}

        elif form_type == "compare":
            cities_raw = request.form.get("cities") or ""
            city_list = [c.strip() for c in cities_raw.split(",") if c.strip()]
            if len(city_list) < 2:
                compare_results = [{"error": "Enter at least two cities, separated by commas."}]
            else:
                compare_results = [fetch_weather_for_city(city) for city in city_list]

    history_df = get_search_history()
    history = history_df.to_dict(orient="records") if not history_df.empty else []

    return render_template(
        "index.html",
        result=result,
        compare_results=compare_results,
        history=history,
    )


if __name__ == "__main__":
    app.run(debug=True)
