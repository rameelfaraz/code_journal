"""
Personal Finance Tracker — Iteration 1
Load and clean raw transaction data.
"""

import pandas as pd

DATA_FILE = "transactions.csv"


def load_and_clean(filepath):
    df = pd.read_csv(filepath)

    # Standardize the description text: strip whitespace, uppercase
    df["Description"] = df["Description"].str.strip().str.upper()

    # Parse dates despite mixed formats 
    def parse_date(value):
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"):
            try:
                return pd.to_datetime(value, format=fmt)
            except (ValueError, TypeError):
                continue
        return pd.NaT

    df["Date"] = df["Date"].apply(parse_date)

    # Drop rows where the date couldn't be parsed at all
    df = df.dropna(subset=["Date"])

    # Remove exact duplicate transactions 
    before = len(df)
    df = df.drop_duplicates(subset=["Date", "Description", "Amount"])
    print(f"Removed {before - len(df)} duplicate transaction(s).")

    # Sort chronologically
    df = df.sort_values("Date").reset_index(drop=True)

    return df


if __name__ == "__main__":
    df = load_and_clean(DATA_FILE)
    print(df.head(10))
    print("\nShape:", df.shape)
    print("\nData types:\n", df.dtypes)