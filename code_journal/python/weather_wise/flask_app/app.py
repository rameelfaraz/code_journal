"""Flask app with city+country search, compare, and history (Jinja)."""
import os
import sys

from flask import Flask, render_template, request

BASE_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
STATIC_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "static"))

sys.path.insert(0, PROJECT_ROOT)
from weather_core import fetch_weather_for_city, get_search_history  

app = Flask(__name__, template_folder="templates", static_folder=STATIC_DIR)


def _parse_compare_pairs(raw):
    """Parse 'City,Country & City,Country' into list of (city, country)."""
    pairs = []
    for entry in (raw or "").split("&"):
        entry = entry.strip()
        if not entry:
            continue
        parts = [p.strip() for p in entry.split(",")]
        if len(parts) < 2:
            return None, "Use format: City,Country & City,Country"
        country = parts[-1]
        city = ",".join(parts[:-1]).strip()
        if not city or not country:
            return None, "Use format: City,Country & City,Country"
        pairs.append((city, country))
    return pairs, None


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    compare_results = None

    if request.method == "POST":
        form_type = request.form.get("form_type", "search")

        if form_type == "search":
            city = (request.form.get("city") or "").strip()
            country = (request.form.get("country") or "").strip()
            if city and country:
                result = fetch_weather_for_city(city, country)
            else:
                result = {"error": "Please enter both city and country."}

        elif form_type == "compare":
            pairs, err = _parse_compare_pairs(request.form.get("cities") or "")
            if err:
                compare_results = [{"error": err}]
            elif len(pairs) < 2:
                compare_results = [{"error": "Enter at least two City,Country pairs separated by &."}]
            else:
                compare_results = [fetch_weather_for_city(city, country) for city, country in pairs]

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
