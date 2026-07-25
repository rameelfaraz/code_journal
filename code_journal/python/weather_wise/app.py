"""
app.py

Streamlit GUI for the Weather app. Contains ONLY UI code — all
actual logic lives in weather_core.py and is imported here.
"""

import streamlit as st
import pandas as pd
from weather_core import fetch_weather_for_city

st.set_page_config(page_title="Weather Wise", page_icon="🌤️")

st.title("🌤️ Weather Lookup")

mode = st.radio("Mode", ["Single City", "Compare Cities"], horizontal=True)

if mode == "Single City":
    city = st.text_input("City name")

    if st.button("Get Weather"):
        if not city.strip():
            st.warning("Please enter a city name.")
        else:
            result = fetch_weather_for_city(city)

            if "error" in result:
                st.error(result["error"])
            else:
                st.subheader(f"📍 {result['city']}, {result['country']}")

                col1, col2 = st.columns(2)
                col1.metric("Temperature", f"{result['temperature']}°C")
                col2.metric("Wind Speed", f"{result['windspeed']} km/h")

                st.write(f"**Condition:** {result['condition']}")
                st.info(result["recommendation"])

else:  # Compare Cities
    cities_input = st.text_input("Enter city names separated by commas", placeholder="Lahore, Karachi, Islamabad")

    if st.button("Compare"):
        city_list = [c.strip() for c in cities_input.split(",") if c.strip()]

        if not city_list:
            st.warning("Please enter at least one city.")
        else:
            results = []
            errors = []

            for city in city_list:
                result = fetch_weather_for_city(city)
                if "error" in result:
                    errors.append(result["error"])
                else:
                    results.append({
                        "City": result["city"],
                        "Temp (°C)": result["temperature"],
                        "Wind (km/h)": result["windspeed"],
                        "Condition": result["condition"],
                    })

            for err in errors:
                st.error(err)

            if results:
                comparison_df = pd.DataFrame(results)
                st.subheader("Comparison")
                st.dataframe(comparison_df, use_container_width=True)

