"""
Personal Finance Tracker 

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

def add_month_column(df):
    # Extract "2025-07" style month labels for grouping
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    return df


def monthly_summary(df):
    # Total income, total spend, and net savings per month.
    income = df[df["Amount"] > 0].groupby("Month")["Amount"].sum()
    spend = df[df["Amount"] < 0].groupby("Month")["Amount"].sum().abs()

    summary = pd.DataFrame({"Income": income, "Spending": spend}).fillna(0)
    summary["Net Savings"] = summary["Income"] - summary["Spending"]
    return summary


def category_breakdown(df, month=None):
    # Spending total per category, optionally filtered to one month.
    spend_df = df[df["Amount"] < 0].copy()
    if month:
        spend_df = spend_df[spend_df["Month"] == month]

    breakdown = spend_df.groupby("Category")["Amount"].sum().abs()
    breakdown = breakdown.sort_values(ascending=False)
    return breakdown


def top_merchants(df, month=None, n=5):
    # Top N merchants by total spend.
    spend_df = df[df["Amount"] < 0].copy()
    if month:
        spend_df = spend_df[spend_df["Month"] == month]

    totals = spend_df.groupby("Description")["Amount"].sum().abs()
    return totals.sort_values(ascending=False).head(n)


def month_over_month_change(summary):
    # Percentage change in spending compared to the previous month.
    summary = summary.copy()
    summary["Spending Change %"] = summary["Spending"].pct_change() * 100
    return summary


if __name__ == "__main__":
    df = load_and_clean(DATA_FILE)
    df = add_categories(df)
    df = add_month_column(df)

    print("\n=== Monthly Summary ===")
    summary = monthly_summary(df)
    print(summary)

    print("\n=== Month-over-Month Spending Change ===")
    print(month_over_month_change(summary))

    latest_month = df["Month"].max()
    print(f"\n=== Category Breakdown for {latest_month} ===")
    print(category_breakdown(df, month=latest_month))

    print(f"\n=== Top 5 Merchants for {latest_month} ===")
    print(top_merchants(df, month=latest_month))