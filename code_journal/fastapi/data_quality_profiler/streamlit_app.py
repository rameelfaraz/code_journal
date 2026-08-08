import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

API_URL = os.getenv("API_URL", "http://localhost:8000/profile")
API_KEY = os.getenv("API_KEY", "")

st.title("Data Quality & Profiling Tool")
st.write("Upload a CSV and get a quick profile report.")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
include_outliers = st.checkbox("Include outlier detection", value=True)

if uploaded_file is not None and st.button("Analyze"):
    if not API_KEY:
        st.error("Missing API_KEY in environment.")
        st.stop()

    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
    headers = {"x-api-key": API_KEY}
    params = {"include_outliers": include_outliers}

    try:
        response = requests.post(API_URL, files=files, headers=headers, params=params)
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to backend API.")
        st.stop()

    if response.status_code != 200:
        st.error(response.text)
        st.stop()

    data = response.json()
    st.success("Report generated")
    st.write({
        "rows": data["rows"],
        "columns": data["columns"],
        "duplicate_rows": data["duplicate_rows"],
    })
    st.write("Columns", data["column_names"])
