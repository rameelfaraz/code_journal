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
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Error: could not find '{filepath}'.")
        return None
    except pd.errors.EmptyDataError:
        print(f"Error: '{filepath}' is empty.")
        return None
    except pd.errors.ParserError:
        print(f"Error: '{filepath}' is not a valid CSV file.")
        return None

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


def find_unusual_transactions(df, month=None, threshold_multiplier=2.0):
    # Flag spending transactions that are unusually large compared to
    # the average spending transaction size (a simple anomaly detector).
    spend_df = df[df["Amount"] < 0].copy()
    if month:
        spend_df = spend_df[spend_df["Month"] == month]

    avg_transaction = spend_df["Amount"].abs().mean()
    threshold = avg_transaction * threshold_multiplier

    unusual = spend_df[spend_df["Amount"].abs() > threshold].copy()
    unusual["TimesAverage"] = (unusual["Amount"].abs() / avg_transaction).round(1)
    return unusual.sort_values("Amount")


def print_report(df, month):
    # Print the full formatted monthly report: summary, category
    # breakdown, top merchants, and any unusual transactions.
    summary = monthly_summary(df)
    breakdown = category_breakdown(df, month=month)
    merchants = top_merchants(df, month=month)
    unusual = find_unusual_transactions(df, month=month)

    print("=" * 38)
    print(f"   MONTHLY SPENDING SUMMARY - {month}")
    print("=" * 38)

    if month in summary.index:
        row = summary.loc[month]
        print(f"\nTotal Income     : Rs. {row['Income']:,.0f}")
        print(f"Total Spending   : Rs. {row['Spending']:,.0f}")
        print(f"Net Savings      : Rs. {row['Net Savings']:,.0f}")

    print("\n" + "-" * 38)
    print("Spending by Category\n")
    total_spend = breakdown.sum()
    for category, amount in breakdown.items():
        pct = (amount / total_spend * 100) if total_spend else 0
        print(f"{category:<18} Rs. {amount:>10,.0f}   ({pct:4.1f}%)")

    print("\n" + "-" * 38)
    print("Top Merchants\n")
    for merchant, amount in merchants.items():
        print(f"{merchant:<28} Rs. {amount:>8,.0f}")

    print("\n" + "-" * 38)
    if len(unusual) > 0:
        print("⚠️  Unusual Transactions Detected\n")
        for _, row in unusual.iterrows():
            print(
                f"Rs. {abs(row['Amount']):,.0f} at \"{row['Description']}\" "
                f"on {row['Date'].strftime('%B %d')} "
                f"({row['TimesAverage']}x your average transaction)"
            )
    else:
        print("No unusual transactions detected this month.")

    print("\n" + "=" * 38)


def menu():
    # Interactive CLI menu for exploring the transaction data.
    df = load_and_clean(DATA_FILE)
    if df is None:
        return

    df = add_categories(df)
    df = add_month_column(df)

    available_months = sorted(df["Month"].unique())

    while True:
        print("\nAvailable months:", ", ".join(available_months))
        print("1. Full Monthly Report")
        print("2. All Months Summary")
        print("3. Category Breakdown (all time)")
        print("4. Exit")

        choice = input("Choose an option: ").strip()

        if not choice:
            print("Invalid option, try again.")
            continue

        if choice == "1":
            month = input(f"Enter month ({available_months[-1]} is most recent): ").strip()
            if not month:
                print("Invalid month.")
                continue
            if month not in available_months:
                print("Invalid month.")
                continue
            print_report(df, month)
        elif choice == "2":
            print(monthly_summary(df))
        elif choice == "3":
            print(category_breakdown(df))
        elif choice == "4":
            break
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    menu()