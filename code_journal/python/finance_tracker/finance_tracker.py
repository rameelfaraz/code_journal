"""
Personal Finance Tracker — Iteration 1
Load and clean raw transaction data.
"""

import pandas as pd

DATA_FILE = "transactions.csv"

CATEGORY_KEYWORDS = {
    "FOODPANDA": "Food & Dining",
    "KFC": "Food & Dining",
    "CAREEM": "Transport",
    "TOTAL": "Transport",
    "PARCO": "Transport",
    "K-ELECTRIC": "Bills & Utilities",
    "KE BILL": "Bills & Utilities",
    "AMAZON": "Shopping",
    "DARAZ": "Shopping",
    "ELECTRONICS": "Shopping",
    "TECH WORLD": "Shopping",
    "NETFLIX": "Entertainment",
    "GYM": "Health & Fitness",
    "FITNESS": "Health & Fitness",
    "SUPERMARKET": "Groceries",
    "METRO CASH": "Groceries",
    "CARREFOUR": "Groceries",
    "SALARY": "Income",
    "FREELANCE": "Income",
    "PAYPAL": "Income",
    "RENT": "Housing",
    "JAZZ": "Mobile & Internet",
    "TELENOR": "Mobile & Internet",
    "ZONG": "Mobile & Internet",
}

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

def categorize(description):
    # Return the category for a transaction based on keyword matching.
    for keyword, category in CATEGORY_KEYWORDS.items():
        if keyword in description:
            return category
    return "Other"


def add_categories(df):
    df["Category"] = df["Description"].apply(categorize)
    return df

if __name__ == "__main__":
    df = load_and_clean(DATA_FILE)
    df = add_categories(df)

    print(df[["Date", "Description", "Amount", "Category"]].head(15))

    print("\nTransactions falling into 'Other' (may need new keywords):")
    print(df[df["Category"] == "Other"]["Description"].unique())