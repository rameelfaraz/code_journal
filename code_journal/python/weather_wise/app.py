"""
app.py

Streamlit GUI for the Weather app. Contains ONLY UI code — all
actual logic lives in weather_core.py and is imported here.
"""

import streamlit as st
import pandas as pd
from weather_core import fetch_weather_for_city, get_search_history

st.set_page_config(page_title="Weather Wise", page_icon="🌤️", layout="centered")

st.title("🌤️ Weather Lookup")

tab1, tab2, tab3 = st.tabs(["Single City", "Compare Cities", "Search History"])

with tab1:
    city = st.text_input("City name", key="single_city_input")

    if st.button("Get Weather", key="single_city_button"):
        if not city.strip():
            st.warning("Please enter a city name.")
        else:
            with st.spinner("Fetching weather..."):
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

with tab2:
    cities_input = st.text_input(
        "Enter city names separated by commas",
        placeholder="Lahore, Karachi, Islamabad",
        key="compare_input",
    )

    if st.button("Compare", key="compare_button"):
        city_list = [c.strip() for c in cities_input.split(",") if c.strip()]

        if not city_list:
            st.warning("Please enter at least one city.")
        else:
            results = []
            errors = []

            with st.spinner("Fetching weather for all cities..."):
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


with tab3:
    history_df = get_search_history()

    if history_df.empty:
        st.write("No searches yet — try looking up a city first.")
    else:
        st.dataframe(history_df.sort_values("Timestamp", ascending=False), use_container_width=True)

        st.download_button(
            label="Download history as CSV",
            data=history_df.to_csv(index=False),
            file_name="weather_log.csv",
            mime="text/csv",
        )