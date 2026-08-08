import os
from pathlib import Path

import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

API_URL = os.getenv("API_URL", "http://localhost:8000/profile")
API_KEY = os.getenv("API_KEY", "")

st.set_page_config(page_title="Data Quality Profiler", layout="centered")

st.title("Data Quality & Profiling Tool")
st.write("Upload a CSV and get an instant data quality report.")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
include_outliers = st.checkbox("Include outlier detection", value=True)

if uploaded_file is not None:
    if st.button("Analyze"):
        with st.spinner("Analyzing..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
            headers = {"x-api-key": API_KEY}
            params = {"include_outliers": include_outliers}

            if not API_KEY:
                st.error("Missing API_KEY. Create a .env file from .env.example before running the app.")
                st.stop()

            try:
                response = requests.post(API_URL, files=files, headers=headers, params=params)
            except requests.exceptions.ConnectionError:
                st.error("Could not reach the API. Is it running?")
                st.stop()

            if response.status_code != 200:
                try:
                    error_detail = response.json().get("detail", "Something went wrong.")
                except ValueError:
                    error_detail = response.text or "Something went wrong."

                st.error(error_detail)
                st.stop()

            data = response.json()

        col1, col2, col3 = st.columns(3)
        col1.metric("Rows", data["rows"])
        col2.metric("Columns", data["columns"])
        col3.metric("Duplicate Rows", data["duplicate_rows"])

        st.subheader("Column Details")
        col_df = pd.DataFrame(data["column_profiles"])
        col_df["has_whitespace_issues"] = col_df["has_whitespace_issues"].map({True: "Yes", False: "No"})
        col_df["outlier_count"] = col_df["outlier_count"].fillna("N/A")
        st.dataframe(col_df, use_container_width=True)
