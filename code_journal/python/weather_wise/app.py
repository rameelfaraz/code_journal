"""
app.py

Streamlit GUI for the Weather app. Contains ONLY UI code — all
actual logic lives in weather_core.py and is imported here.
"""

import streamlit as st
from weather_core import fetch_weather_for_city

st.set_page_config(page_title="Weather Wise", page_icon="🌤️")

st.title("🌤️ Weather Lookup")
st.write("Enter a city to see its current weather.")

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