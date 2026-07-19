# 💰 Personal Finance Tracker

A command-line tool built with Python and Pandas that loads a bank
transaction export, cleans and categorizes every transaction
automatically, and generates a monthly spending report — including
category breakdowns, top merchants, spending trends, and detection of
unusually large transactions.

This project was built as a hands-on way to practice real-world data
cleaning with Pandas, going beyond textbook examples into the kind of
messy, inconsistent data you actually encounter outside a classroom.

---

## 📖 Table of Contents
- [About the Dataset](#-about-the-dataset)
- [Key Features](#-key-features)
- [What This Project Does](#-what-this-project-does)
- [The Problem This Solves](#-the-problem-this-solves)
- [How It Works (Behind the Scenes)](#-how-it-works-behind-the-scenes)
- [How to Run This on Your PC](#-how-to-run-this-on-your-pc)
- [Sample Output](#-sample-output)
- [What I Learned](#-what-i-learned)
- [License](#-license)

---

## 📊 About the Dataset

`transactions.csv` is a **synthetically generated (fake) dataset**
built to imitate a real bank/wallet statement export — it is not real
financial data. It was generated with a Python script that
deliberately injects the kind of messiness found in real exports,
including:

- **Mixed date formats** in the same file (`2025-07-15`, `7/15/2025`,
  and `15-07-2025` all appear)
- **Inconsistent merchant naming** for the same business (e.g.
  `"FOODPANDA*ORDER8821"` vs. `"Foodpanda Lahore"` vs.
  `"FOODPANDA ONLINE"`)
- **Duplicate transactions**, simulating pending/settled entries that
  sometimes both appear in a real export
- **Randomized but realistic transaction volume and amounts** across
  three months (May–July 2025), including fixed monthly costs
  (salary, rent, utilities, subscriptions) and variable spending
  (food, shopping, transport)
- **Deliberately injected large transactions** each month, to make
  sure the anomaly detection logic had something real to catch

### Why this mattered for how the script was written
Because the data was intentionally messy rather than clean, the
script couldn't just call `pd.read_csv()` and start analyzing. Every
cleaning step in `load_and_clean()` — the multi-format date parser,
the uppercase/strip normalization on merchant names, and
`drop_duplicates()` — exists specifically *because* the fake dataset
was built to require it. This was a deliberate choice: writing
against clean data would have skipped the most important and most
transferable skill in this project, which is handling data that
doesn't arrive in a tidy, analysis-ready shape.

**Note:** this script works the same way against a real exported bank
statement — you can drop in your own CSV as long as it has `Date`,
`Description`, and `Amount` columns.

---

## ✨ Key Features

- 🧹 Cleans messy real-world-style transaction data automatically
- 🏷️ Categorizes transactions using keyword matching (Food, Shopping,
  Bills, Transport, Housing, etc.)
- 📅 Monthly income, spending, and net savings summary
- 📈 Month-over-month spending trend (% change)
- 🏪 Top merchants by total spend, per month
- ⚠️ Anomaly detection for unusually large transactions
- 🎛️ Interactive command-line menu
- 🛡️ Graceful error handling for missing, empty, or malformed CSV files

---

## ✅ What This Project Does

- Loads a CSV of transactions and cleans it (dates, text formatting,
  duplicates)
- Automatically assigns each transaction a spending category based on
  keywords in its description
- Calculates monthly totals for income, spending, and net savings
- Breaks down spending by category, with percentages
- Identifies the top 5 merchants by spend for a given month
- Flags transactions that are significantly larger than that month's
  average transaction size
- Presents everything through a simple interactive menu in the
  terminal

---

## 🎯 The Problem This Solves

Most people (myself included) have no real visibility into where
their money actually goes each month beyond a vague sense of "I spent
too much." Bank statements are exportable but not readable —
hundreds of rows of inconsistent merchant codes with no categorization
or summary.

This tool takes that raw, unreadable export and turns it into an
actual answer to the question **"where did my money go this month,
and was anything unusual?"** — automatically, without manually
sorting transactions into a spreadsheet by hand every month.

---

## ⚙️ How It Works (Behind the Scenes)

1. **Load** — `load_and_clean()` reads the CSV with `pd.read_csv()`,
   wrapped in a try/except block to handle missing, empty, or
   malformed files without crashing.
2. **Clean** —
   - Merchant descriptions are stripped of whitespace and uppercased
     for consistent matching.
   - Dates are parsed by trying three known formats in turn
     (`%Y-%m-%d`, `%m/%d/%Y`, `%d-%m-%Y`); anything that still fails
     becomes `NaT` and is dropped.
   - Exact duplicate transactions (same date, description, and
     amount) are removed with `drop_duplicates()`.
3. **Categorize** — `categorize()` checks each transaction's
   description against a dictionary of keywords (`CATEGORY_KEYWORDS`)
   and assigns the first matching category, or `"Other"` if nothing
   matches.
4. **Aggregate** — using `groupby()` on the `Month` and `Category`
   columns, the script calculates:
   - Total income and spending per month (`monthly_summary()`)
   - Spending broken down by category (`category_breakdown()`)
   - Top merchants by total spend (`top_merchants()`)
   - Percentage change in spending month-over-month
     (`month_over_month_change()`, using `.pct_change()`)
5. **Detect anomalies** — `find_unusual_transactions()` calculates the
   average transaction size for the selected month, then flags any
   transaction more than 2x that average.
6. **Report** — `print_report()` formats all of the above into a
   readable terminal report, and `menu()` wraps everything in an
   interactive loop so you can choose what to view.

---

## 🚀 How to Run This on Your PC

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/code_journal/python/finance_tracker

cd finance_tracker
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/Scripts/activate    # Git Bash on Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Make sure the dataset is present
Confirm `transactions.csv` is in the same folder as `finance_tracker.py`.
(If you want to use your own real bank export instead, make sure it
has `Date`, `Description`, and `Amount` columns, and rename it to
`transactions.csv`, or update `DATA_FILE` in the script.)

### 5. Run the program
```bash
python finance_tracker.py
```

### 6. Use the interactive menu
- Choose **1** for a full monthly report (you'll be asked which
  month — options are shown at the top)
- Choose **2** for an all-months summary table
- Choose **3** for an all-time category breakdown
- Choose **4** to exit

---

## 📋 Sample Output

```
======================================
   MONTHLY SPENDING SUMMARY - 2025-07
======================================

Total Income     : Rs. 183,663
Total Spending   : Rs. 359,948
Net Savings      : Rs. -176,285

--------------------------------------
Spending by Category

Shopping           Rs.    282,679   (78.5%)
Housing            Rs.     35,000   ( 9.7%)
Groceries          Rs.     13,100   ( 3.6%)
Transport          Rs.     10,053   ( 2.8%)
Mobile & Internet  Rs.      5,618   ( 1.6%)
Health & Fitness   Rs.      5,000   ( 1.4%)
Bills & Utilities  Rs.      4,962   ( 1.4%)
Food & Dining      Rs.      2,036   ( 0.6%)
Entertainment      Rs.      1,500   ( 0.4%)

--------------------------------------
Top Merchants

ELECTRONICS STORE - MEGA MALL Rs.  154,454
TECH WORLD ELECTRONICS        Rs.   84,892
RENT PAYMENT - LANDLORD       Rs.   35,000
AMAZON MKTPL*2K3J9            Rs.   24,781
METRO CASH AND CARRY          Rs.   13,100

--------------------------------------
⚠️  Unusual Transactions Detected

Rs. 42,289 at "ELECTRONICS STORE - MEGA MALL" on July 08 (3.8x your average transaction)
Rs. 40,876 at "ELECTRONICS STORE - MEGA MALL" on July 14 (3.6x your average transaction)
Rs. 35,537 at "ELECTRONICS STORE - MEGA MALL" on July 12 (3.2x your average transaction)
Rs. 35,000 at "RENT PAYMENT - LANDLORD" on July 27 (3.1x your average transaction)
======================================
```

---

## 🎓 What I Learned

Practiced using Pandas to clean genuinely messy real-world-style
data — inconsistent date formats, duplicate records, and unnormalized
text all needed to be handled before any analysis could happen. Built
a keyword-based categorization system and used `groupby()`-based
aggregation to turn raw transactions into real financial insights.

Also learned that a simple threshold-based anomaly detector has real
limitations: a fixed, predictable expense like Rent still got flagged
as "unusual" in one month, because that month's *average* transaction
size happened to be pulled down by many small purchases, making the
Rent payment look disproportionately large by comparison. This wasn't
a bug — it was a useful, honest demonstration of why production
anomaly detection systems usually need smarter baselines, such as
comparing a transaction against its own category's average rather
than the overall average, or explicitly excluding known recurring
transactions.

---

## 📄 License
This project is licensed under the MIT License — see the
[LICENSE](LICENSE) file for details.