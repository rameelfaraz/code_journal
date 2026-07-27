"""Weather lookup helpers backed by Open-Meteo's free geocoding and forecast APIs."""

import csv
import os
from datetime import datetime

import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weather_log.csv")
LOG_HEADERS = ["Timestamp", "City", "Country", "Temperature", "WindSpeed", "Condition"]

COUNTRY_ALIASES = {
    "usa": "united states",
    "u.s.a": "united states",
    "us": "united states",
    "u.s": "united states",
    "united states of america": "united states",
    "uk": "united kingdom",
    "u.k": "united kingdom",
    "gb": "united kingdom",
    "great britain": "united kingdom",
    "uae": "united arab emirates",
    "u.a.e": "united arab emirates",
    "pk": "pakistan",
    "pak": "pakistan",
    "in": "india",
    "ind": "india",
    "ca": "canada",
    "can": "canada",
    "au": "australia",
    "aus": "australia",
    "nz": "new zealand",
    "nzl": "new zealand",
    "de": "germany",
    "deu": "germany",
    "fr": "france",
    "fra": "france",
    "jp": "japan",
    "jpn": "japan",
    "cn": "china",
    "chn": "china",
    "prc": "china",
    "ksa": "saudi arabia",
    "k.s.a": "saudi arabia",
    "sa": "saudi arabia",
    "ch": "switzerland",
    "che": "switzerland",
    "nl": "netherlands",
    "nld": "netherlands",
    "br": "brazil",
    "bra": "brazil",
    "mx": "mexico",
    "mex": "mexico",
    "ru": "russia",
    "rus": "russia",
    "eg": "egypt",
    "egy": "egypt",
    "kr": "south korea",
    "kor": "south korea",
    "tr": "turkey",
    "tur": "turkey",
    "sg": "singapore",
    "sgp": "singapore",
    "es": "spain",
    "esp": "spain",
    "it": "italy",
    "ita": "italy",
}

US_STATES = {
    "al": "alabama", "ak": "alaska", "az": "arizona", "ar": "arkansas", "ca": "california",
    "co": "colorado", "ct": "connecticut", "de": "delaware", "fl": "florida", "ga": "georgia",
    "hi": "hawaii", "id": "idaho", "il": "illinois", "in": "indiana", "ia": "iowa",
    "ks": "kansas", "ky": "kentucky", "la": "louisiana", "me": "maine", "md": "maryland",
    "ma": "massachusetts", "mi": "michigan", "mn": "minnesota", "ms": "mississippi", "mo": "missouri",
    "mt": "montana", "ne": "nebraska", "nv": "nevada", "nh": "new hampshire", "nj": "new jersey",
    "nm": "new mexico", "ny": "new york", "nc": "north carolina", "nd": "north dakota", "oh": "ohio",
    "ok": "oklahoma", "or": "oregon", "pa": "pennsylvania", "ri": "rhode island", "sc": "south carolina",
    "sd": "south dakota", "tn": "tennessee", "tx": "texas", "ut": "utah", "vt": "vermont",
    "va": "virginia", "wa": "washington", "wv": "west virginia", "wi": "wisconsin", "wy": "wyoming",
}

WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Foggy",
    51: "Light Drizzle",
    61: "Light Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Light Snow",
    80: "Rain Showers",
    95: "Thunderstorm",
}


def _normalize_text(value):
    return " ".join(str(value or "").strip().lower().split())


def _normalize_country_name(country_name):
    normalized = _normalize_text(country_name)
    return COUNTRY_ALIASES.get(normalized, normalized)


def _format_city_label(location):
    """Prefer 'City, Region' when the admin region adds useful detail."""
    name = location.get("name", "")
    admin1 = location.get("admin1")
    if admin1 and _normalize_text(admin1) != _normalize_text(name):
        return f"{name}, {admin1}"
    return name


def get_coordinates(city_name, country_name):
    """
    Resolve a city to coordinates via Open-Meteo geocoding.

    Returns {name, country, admin1, latitude, longitude} on success,
    {ambiguous, error, matches} when several exact matches exist,
    or None when nothing is found / the request fails.
    """
    try:
        target_country = _normalize_country_name(country_name)
        raw_city = str(city_name or "").strip()

        parts = [p.strip() for p in raw_city.split(",") if p.strip()]
        if len(parts) > 1:
            base_city = parts[0]
            region_detail = _normalize_text(parts[1])
        else:
            words = raw_city.split()
            if len(words) > 1 and (_normalize_text(words[-1]) in US_STATES or len(words[-1]) == 2):
                base_city = " ".join(words[:-1])
                region_detail = _normalize_text(words[-1])
            else:
                base_city = raw_city
                region_detail = None

        target_city = _normalize_text(base_city)

        params = {"name": base_city, "count": 20}
        response = requests.get(GEOCODING_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if "results" not in data or len(data["results"]) == 0:
            if base_city != raw_city:
                params = {"name": raw_city, "count": 20}
                response = requests.get(GEOCODING_URL, params=params, timeout=5)
                response.raise_for_status()
                data = response.json()
                if "results" not in data or len(data["results"]) == 0:
                    return None
            else:
                return None

        candidates = []
        for result in data["results"]:
            result_city = _normalize_text(result.get("name", ""))
            result_country = _normalize_country_name(result.get("country", ""))
            if result_city == target_city and result_country == target_country:
                if region_detail:
                    admin1 = _normalize_text(result.get("admin1", ""))
                    admin2 = _normalize_text(result.get("admin2", ""))
                    admin3 = _normalize_text(result.get("admin3", ""))
                    norm_region = US_STATES.get(region_detail, region_detail)
                    if (
                        norm_region in admin1
                        or norm_region in admin2
                        or norm_region in admin3
                        or region_detail in admin1
                    ):
                        candidates.append(result)
                else:
                    candidates.append(result)

        if len(candidates) == 0:
            return None

        if len(candidates) > 1:
            options = []
            for entry in candidates:
                admin = entry.get("admin1") or entry.get("admin2") or entry.get("country")
                options.append(f"{entry.get('name', base_city)}, {admin}")

            unique_options = list(dict.fromkeys(options))[:3]
            options_text = "; ".join(unique_options)
            return {
                "ambiguous": True,
                "error": (
                    f"Multiple exact matches found for '{city_name}, {country_name}'. "
                    f"Try adding state/region details. Possible matches: {options_text}."
                ),
                "matches": unique_options,
            }

        result = candidates[0]
        return {
            "name": result["name"],
            "country": result.get("country", "Unknown"),
            "admin1": result.get("admin1"),
            "latitude": result["latitude"],
            "longitude": result["longitude"],
        }

    except requests.exceptions.RequestException:
        return None


def get_current_weather(latitude, longitude):
    """
    Fetch current weather for a coordinate pair.

    Returns {temperature, windspeed, weathercode} on success, or None on failure.
    """
    try:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True,
        }
        response = requests.get(WEATHER_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        current = data["current_weather"]
        return {
            "temperature": current["temperature"],
            "windspeed": current["windspeed"],
            "weathercode": current["weathercode"],
        }

    except (requests.exceptions.RequestException, KeyError):
        return None


def describe_weather_code(code):
    """Map an Open-Meteo weather code to a short label."""
    return WEATHER_CODES.get(code, "Unknown Conditions")


def get_recommendation(temperature, weathercode):
    """Build a short clothing / preparedness tip from conditions."""
    condition = describe_weather_code(weathercode)
    messages = []

    if "Rain" in condition or "Drizzle" in condition or "Thunderstorm" in condition:
        messages.append("Bring an umbrella.")
    if temperature < 15:
        messages.append("Wear a jacket — it's chilly.")
    elif temperature > 35:
        messages.append("Stay hydrated — it's very hot.")
    if not messages:
        messages.append("Great day to be outside — light clothing recommended.")

    return " ".join(messages)


def log_search(location, weather):
    """Append one lookup to the local CSV history file."""
    entry = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "City": _format_city_label(location),
        "Country": location["country"],
        "Temperature": weather["temperature"],
        "WindSpeed": weather["windspeed"],
        "Condition": describe_weather_code(weather["weathercode"]),
    }

    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=LOG_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)


def fetch_weather_for_city(city_name, country_name):
    """
    Geocode, fetch weather, and log one city+country lookup.

    Returns a display-ready dict, or a dict with an "error" key on failure.
    """
    location = get_coordinates(city_name, country_name)
    if location is None:
        return {"error": f"Could not find an exact match for '{city_name}, {country_name}'."}

    if location.get("ambiguous"):
        return {
            "error": location["error"],
            "ambiguous": True,
            "matches": location.get("matches", []),
        }

    weather = get_current_weather(location["latitude"], location["longitude"])
    if weather is None:
        return {"error": "Could not fetch weather data. Try again."}

    log_search(location, weather)

    return {
        "city": _format_city_label(location),
        "country": location["country"],
        "temperature": weather["temperature"],
        "windspeed": weather["windspeed"],
        "condition": describe_weather_code(weather["weathercode"]),
        "recommendation": get_recommendation(weather["temperature"], weather["weathercode"]),
    }
