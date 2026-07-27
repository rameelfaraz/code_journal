import requests
import pandas as pd
from datetime import datetime

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
LOG_FILE = "weather_log.csv"

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


def get_coordinates(city_name, country_name):
    """
    Look up a city's latitude/longitude using Open-Meteo's free
    geocoding endpoint, filtered by exact country name match.

    Returns a dict {name, country, latitude, longitude} on success,
    or None if no match / network error.
    First exact match wins (no ambiguity handling yet).
    """
    try:
        target_country = _normalize_country_name(country_name)
        target_city = _normalize_text(city_name)

        params = {"name": city_name, "count": 10}
        response = requests.get(GEOCODING_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if "results" not in data or len(data["results"]) == 0:
            return None

        for result in data["results"]:
            result_city = _normalize_text(result.get("name", ""))
            result_country = _normalize_country_name(result.get("country", ""))
            if result_city == target_city and result_country == target_country:
                return {
                    "name": result["name"],
                    "country": result.get("country", "Unknown"),
                    "latitude": result["latitude"],
                    "longitude": result["longitude"],
                }

        return None

    except requests.exceptions.RequestException:
        return None


def get_current_weather(latitude, longitude):
    """
    Fetch current weather for a coordinate pair.

    Returns a dict {temperature, windspeed, weathercode} on success,
    or None on any network/parsing error.
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
    """Turn a numeric Open-Meteo weather code into a readable label."""
    return WEATHER_CODES.get(code, "Unknown Conditions")


def get_recommendation(temperature, weathercode):
    """Simple rule-based recommendation string based on conditions."""
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
    """Append a search result to the CSV history file with a timestamp."""
    entry = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "City": location["name"],
        "Country": location["country"],
        "Temperature": weather["temperature"],
        "WindSpeed": weather["windspeed"],
        "Condition": describe_weather_code(weather["weathercode"]),
    }
    df_entry = pd.DataFrame([entry])

    try:
        pd.read_csv(LOG_FILE)
        df_entry.to_csv(LOG_FILE, mode="a", header=False, index=False)
    except FileNotFoundError:
        df_entry.to_csv(LOG_FILE, mode="w", header=True, index=False)


def get_search_history():
    """Return the search history as a DataFrame, or an empty one if none exists."""
    try:
        return pd.read_csv(LOG_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Timestamp", "City", "Country", "Temperature", "WindSpeed", "Condition"])


def fetch_weather_for_city(city_name, country_name):
    """
    Full pipeline for one city+country: geocode -> fetch weather -> log.
    Returns a dict with everything a UI needs to display, or a dict
    with an "error" key if something failed.
    """
    location = get_coordinates(city_name, country_name)
    if location is None:
        return {"error": f"Could not find an exact match for '{city_name}, {country_name}'."}

    weather = get_current_weather(location["latitude"], location["longitude"])
    if weather is None:
        return {"error": "Could not fetch weather data. Try again."}

    log_search(location, weather)

    return {
        "city": location["name"],
        "country": location["country"],
        "temperature": weather["temperature"],
        "windspeed": weather["windspeed"],
        "condition": describe_weather_code(weather["weathercode"]),
        "recommendation": get_recommendation(weather["temperature"], weather["weathercode"]),
    }
