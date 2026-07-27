# Weather Wise

Weather Wise is a lightweight web app for looking up live weather by **city and country**, comparing conditions across multiple places, and keeping a searchable session history you can export as CSV. It solves the everyday problem of quickly checking accurate, location-specific weather without opening several tabs or guessing which "Paris" or "Springfield" an API returned.

---

## Live Demo

**Demo link:** https://weather-wise-uf86.onrender.com

> Free-tier hosts sleep after inactivity; the first load can take 30–60 seconds.

---

## Key Features

- **City + country search** — Look up current weather with explicit location matching (not just city name alone)
- **Country aliases** — Supports shortcuts like `USA`, `UK`, `PK`, `UAE`, and more
- **Ambiguity handling** — Suggests places when multiple exact matches exist (e.g. add state/region to narrow results)
- **Compare cities** — Side-by-side table for up to 5 `City,Country` pairs using `City,Country & City,Country` format
- **Outfit / preparedness tips** — Simple recommendations based on temperature and conditions (rain, heat, cold)
- **Session search history** — Recent lookups shown in-app with a count badge
- **CSV export** — Download your session history as `weather_log.csv`
- **Responsive UI** — Usable on desktop, tablet, and mobile
- **Input validation** — Client- and server-side checks for safe, readable place names

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Flask |
| HTTP client | `requests` (Open-Meteo geocoding + forecast APIs) |
| Frontend | HTML, CSS, vanilla JavaScript |
| Templates | Jinja2 (page shell + static asset URLs) |
| Data logging | CSV (server-side `weather_log.csv`) |
| APIs | [Open-Meteo Geocoding](https://open-meteo.com/en/docs/geocoding-api), [Open-Meteo Forecast](https://open-meteo.com/en/docs) |

---

## Run Locally

### Prerequisites

- Python 3.10+ recommended
- `pip`

### Steps

1. **Clone the repository** (or navigate to this folder if you already have it):

   ```bash
   git clone https://github.com/rameelfaraz/code_journal.git
   cd code_journal/python/weather_wise
   ```

2. **Create and activate a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   ```

   Windows:

   ```bash
   venv\Scripts\activate
   ```

   macOS / Linux:

   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Flask app**:

   ```bash
   python flask_app/app.py
   ```

5. **Open in your browser**:

   ```
   http://127.0.0.1:5000
   ```

6. **Try a search** — e.g. City: `Lahore`, Country: `Pakistan`

---

## Project Structure

```
weather_wise/
├── .gitignore                 # Ignores venv, bytecode, local weather_log.csv
├── LICENSE                    # MIT License
├── README.md
├── requirements.txt           # flask, requests
├── weather_core.py            # Geocoding, weather fetch, CSV logging, recommendations
├── flask_app/
│   ├── app.py                 # Flask routes, validation, /api/weather JSON endpoint
│   └── templates/
│       └── index.html         # HTML page shell (Jinja2 url_for for static assets)
├── static/
│   ├── css/
│   │   └── style.css          # Layout, cards, responsive styles, state UI
│   └── js/
│       └── app.js             # Search, compare, history, fetch API calls
└── screenshots/               # README demo images
    ├── home-desktop.png
    ├── result-success.png
    ├── compare-cities.png
    ├── ambiguity.png
    ├── history.png
    └── mobile-home.png
```

**Runtime file (not committed):** `weather_log.csv` — created in the project root when you run a search.

---

## How It Works

### Request flow

1. The browser loads `index.html` from Flask (`GET /`).
2. CSS and JavaScript are served from `static/`.
3. When you search or compare, JavaScript calls `GET /api/weather?city=...&country=...`.
4. Flask validates the input, then calls `fetch_weather_for_city()` in `weather_core.py`.
5. `weather_core.py` geocodes the place via Open-Meteo, fetches current weather, logs the lookup to CSV, and returns JSON.
6. JavaScript renders the result card, compare table, or error/ambiguity state without a full page reload.
7. Successful lookups are added to **session history** in the browser; you can download that list as CSV.

### Geocoding logic (summary)

- City and country are normalized and matched against Open-Meteo results.
- Country aliases map common abbreviations to full country names.
- US state hints (e.g. `Springfield, IL`) help disambiguate cities.
- If several exact matches remain, the app returns suggestions instead of guessing.

### Limitations

- **No API key / no auth** — Relies on free Open-Meteo endpoints; subject to their availability and rate limits.
- **Current weather only** — No hourly or multi-day forecast in the UI.
- **Session-only history in the browser** — Refreshing the page clears the in-app history table (server CSV logging still runs per lookup).
- **Exact-match geocoding** — Misspellings or vague names may return “not found”; ambiguous names require you to pick or refine the query.
- **Compare cap** — At most 5 city pairs per compare request.
- **No user accounts** — No saved preferences or cross-device history.
- **Free hosting sleep** — If deployed on a free tier, the app may spin down when idle and wake slowly on first visit.

---

## Screenshots


### Home — search & layout (desktop)

<img src="screenshots/home-desktop.png" alt="Home desktop — search, compare, and history sections" width="800">

### Weather result — success state

<img src="screenshots/result-success.png" alt="Weather result card with temperature and recommendation" width="800">

### Compare cities

<img src="screenshots/compare-cities.png" alt="Compare cities table" width="800">

### Ambiguous location suggestions

<img src="screenshots/ambiguity.png" alt="Ambiguous location suggestions" width="800">

### Search history & CSV download

<img src="screenshots/history.png" alt="Search history table and CSV download" width="800">

### Mobile view

<img src="screenshots/mobile-home.png" alt="Mobile layout">

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
