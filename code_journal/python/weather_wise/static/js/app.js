const searchForm = document.getElementById("searchForm");
const searchInput = document.getElementById("searchInput");
const searchCountryInput = document.getElementById("searchCountryInput");
const searchBtn = document.getElementById("searchBtn");
const resultCard = document.getElementById("resultCard");

const compareForm = document.getElementById("compareForm");
const compareInput = document.getElementById("compareInput");
const compareBtn = document.getElementById("compareBtn");
const compareResults = document.getElementById("compareResults");

const historyBody = document.getElementById("historyBody");
const historyBadge = document.getElementById("historyBadge");
const downloadCsvBtn = document.getElementById("downloadCsvBtn");

const CITY_MAX_LENGTH = 80;
const COUNTRY_MAX_LENGTH = 60;
const COMPARE_MAX_PAIRS = 5;

let sessionHistory = [];

function normalizeText(value) {
	return String(value || "").trim().replace(/\s+/g, " ");
}

/** Letters (incl. accents), spaces, and light punctuation; optionally commas for region detail. */
function validateTextInput(value, { allowComma = false, maxLength = CITY_MAX_LENGTH } = {}) {
	const normalized = normalizeText(value);
	if (!normalized || normalized.length < 2 || normalized.length > maxLength) {
		return false;
	}

	const pattern = allowComma
		? /^\p{L}[\p{L}\s.',-]*$/u
		: /^\p{L}[\p{L}\s.'-]*$/u;

	return pattern.test(normalized) && /\p{L}{2,}/u.test(normalized);
}

function isValidCityInput(value) {
	return validateTextInput(value, { allowComma: true, maxLength: CITY_MAX_LENGTH });
}

function isValidCountryInput(value) {
	return validateTextInput(value, { allowComma: false, maxLength: COUNTRY_MAX_LENGTH });
}

/**
 * Parse compare input like "Lahore,Pakistan & Springfield, IL, USA".
 * Country is the last comma-separated part; everything before is the city.
 */
function parseComparePairs(value) {
	const rawEntries = String(value || "").split("&");
	if (rawEntries.some((entry) => entry.trim() === "")) {
		return { error: "Please remove extra ampersands and use City,Country & City,Country format.", pairs: [] };
	}

	if (rawEntries.length > COMPARE_MAX_PAIRS) {
		return { error: `Please compare at most ${COMPARE_MAX_PAIRS} cities at a time.`, pairs: [] };
	}

	const pairs = [];
	for (const entry of rawEntries) {
		const parts = entry.split(",");
		if (parts.length < 2) {
			return { error: "Use format: City,Country & City,Country.", pairs: [] };
		}

		const country = normalizeText(parts.pop());
		const city = normalizeText(parts.join(","));
		if (!isValidCityInput(city) || !isValidCountryInput(country)) {
			return { error: "Please enter valid City,Country pairs.", pairs: [] };
		}

		pairs.push({ city, country, label: `${city},${country}` });
	}

	return { error: null, pairs };
}

function escapeHtml(value) {
	return String(value)
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#39;");
}

function escapeCsvValue(value) {
	const text = String(value ?? "");
	if (/[",\n\r]/.test(text)) {
		return `"${text.replace(/"/g, '""')}"`;
	}
	return text;
}

function getRecommendationClass(recommendation) {
	const text = String(recommendation || "").toLowerCase();
	if (text.includes("umbrella")) return "rec-rain";
	if (text.includes("jacket")) return "rec-cool";
	if (text.includes("hydrated")) return "rec-hot";
	return "rec-sun";
}

function showLoadingState() {
	if (!resultCard) return;

	resultCard.classList.remove("hidden");
	resultCard.innerHTML = `
		<div class="loading-state-container">
			<div class="loading-main-body">
				<div class="loading-group-1">
					<div class="stacked-bones">
						<div class="skeleton-bone skeleton-w-140 skeleton-h-18"></div>
						<div class="skeleton-bone skeleton-w-90 skeleton-h-12"></div>
					</div>
				</div>
				<div class="loading-group-2">
					<div class="skeleton-bone skeleton-w-100 skeleton-h-56"></div>
				</div>
				<div class="loading-group-3">
					<div class="skeleton-bone skeleton-h-48"></div>
					<div class="skeleton-bone skeleton-h-48"></div>
					<div class="skeleton-bone skeleton-h-48"></div>
				</div>
			</div>
			<div class="loading-footer-strip">
				<div class="skeleton-bone skeleton-w-220 skeleton-h-14"></div>
			</div>
		</div>
	`;
}

function showSuccessState(data) {
	if (!resultCard) return;

	const bannerClass = getRecommendationClass(data.recommendation);

	resultCard.classList.remove("hidden");
	resultCard.innerHTML = `
		<div class="success-state-container">
			<div class="success-main-body">
				<div class="success-header-row">
					<div class="city-info-left">
						<div class="city-name-wrapper">
							<span>${escapeHtml(data.city)}, ${escapeHtml(data.country)}</span>
						</div>
						<div class="country-update-text">Updated just now</div>
					</div>
				</div>

				<div class="temp-row">
					<div class="temp-large">${Math.round(Number(data.temperature))}</div>
					<div class="temp-unit-condition">
						<div class="temp-unit">°C</div>
						<div class="condition-text">${escapeHtml(data.condition)}</div>
					</div>
				</div>

				<div class="stats-row">
					<div class="stat-pill">
						<div class="stat-content">
							<div class="stat-label">Wind Speed</div>
							<div class="stat-value">${escapeHtml(data.windspeed)} km/h</div>
						</div>
					</div>
					<div class="stat-pill">
						<div class="stat-content">
							<div class="stat-label">Condition</div>
							<div class="stat-value">${escapeHtml(data.condition)}</div>
						</div>
					</div>
					<div class="stat-pill">
						<div class="stat-content">
							<div class="stat-label">Country</div>
							<div class="stat-value">${escapeHtml(data.country)}</div>
						</div>
					</div>
				</div>
			</div>

			<div class="recommendation-banner ${bannerClass}">
				<span>${escapeHtml(data.recommendation)}</span>
			</div>
		</div>
	`;
}

function showErrorState(message) {
	if (!resultCard) return;

	resultCard.classList.remove("hidden");
	resultCard.innerHTML = `
		<div class="error-state-container">
			<div class="error-icon-circle">
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
					<circle cx="12" cy="12" r="10"></circle>
					<line x1="12" y1="8" x2="12" y2="12"></line>
					<line x1="12" y1="16" x2="12.01" y2="16"></line>
				</svg>
			</div>
			<div class="error-heading">${escapeHtml(message)}</div>
			<div class="error-subtext">Check the spelling or try a different city.</div>
		</div>
	`;
}

function showAmbiguityState(data) {
	if (!resultCard) return;

	const matchesHtml = Array.isArray(data.matches) && data.matches.length > 0
		? `<div class="ambiguity-matches-title">Suggested places:</div>
		   <div class="ambiguity-matches-list">
			   ${data.matches
					.map(
						(match) => `
					<button type="button" class="ambiguity-match-pill" data-match="${escapeHtml(match)}">
						<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
							<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
							<circle cx="12" cy="10" r="3"></circle>
						</svg>
						<span>${escapeHtml(match)}</span>
					</button>
				`
					)
					.join("")}
		   </div>`
		: "";

	resultCard.classList.remove("hidden");
	resultCard.innerHTML = `
		<div class="ambiguity-state-container">
			<div class="ambiguity-icon-circle">
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#F6AD55" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
					<circle cx="12" cy="12" r="10"></circle>
					<path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
					<line x1="12" y1="17" x2="12.01" y2="17"></line>
				</svg>
			</div>
			<div class="ambiguity-heading">Multiple Locations Found</div>
			<div class="ambiguity-subtext">
				Multiple exact matches were found for your query. Please select one of the suggestions below or refine your search by adding state/region details to the City field.
			</div>
			${matchesHtml}
		</div>
	`;
}

function selectAmbiguousMatch(matchName) {
	if (!searchInput || !searchForm) return;
	searchInput.value = matchName;
	searchForm.dispatchEvent(new Event("submit"));
}

function showCompareErrorState(message) {
	if (!compareResults) return;

	compareResults.innerHTML = `
		<div class="error-state-container">
			<div class="error-icon-circle">
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
					<circle cx="12" cy="12" r="10"></circle>
					<line x1="12" y1="8" x2="12" y2="12"></line>
					<line x1="12" y1="16" x2="12.01" y2="16"></line>
				</svg>
			</div>
			<div class="error-heading">${escapeHtml(message)}</div>
			<div class="error-subtext">Check the spelling or try a different city.</div>
		</div>
	`;
}

function setButtonLoading(button, isLoading, iconSelector) {
	if (!button) return;

	button.disabled = isLoading;

	const actionIcon = button.querySelector(iconSelector);
	const spinnerIcon = button.querySelector(".spinner-icon");

	if (actionIcon) actionIcon.classList.toggle("hidden", isLoading);
	if (spinnerIcon) spinnerIcon.classList.toggle("hidden", !isLoading);
}

function showCompareLoading() {
	if (!compareResults) return;

	compareResults.innerHTML = `
		<div class="compare-skeleton-wrapper">
			<div class="compare-skeleton-header">
				<div class="skeleton-bone skeleton-h-12"></div>
				<div class="skeleton-bone skeleton-h-12"></div>
				<div class="skeleton-bone skeleton-h-12"></div>
				<div class="skeleton-bone skeleton-h-12"></div>
				<div class="skeleton-bone skeleton-h-12"></div>
			</div>
			${[1, 2, 3]
				.map(
					() => `
				<div class="compare-skeleton-row">
					<div class="skeleton-bone skeleton-h-14"></div>
					<div class="skeleton-bone skeleton-h-14"></div>
					<div class="skeleton-bone skeleton-h-14"></div>
					<div class="skeleton-bone skeleton-h-14"></div>
					<div class="skeleton-bone skeleton-h-14"></div>
				</div>
			`
				)
				.join("")}
		</div>
	`;
}

function renderCompareResults(responses) {
	if (!compareResults) return;

	const valid = responses.filter((response) => !response.error);
	const errors = responses.filter((response) => response.error);

	let html = "";

	if (errors.length > 0 && valid.length > 0) {
		html += `<div class="compare-mixed-note">Some cities could not be found.</div>`;
	}

	errors.forEach((errorItem) => {
		html += `<div class="compare-error-line">${escapeHtml(errorItem.error)}</div>`;
	});

	if (valid.length > 0) {
		html += `
			<div class="table-wrapper">
				<table class="custom-table">
					<thead>
						<tr>
							<th>City</th>
							<th>Country</th>
							<th>Temperature</th>
							<th>Wind Speed</th>
							<th>Condition</th>
						</tr>
					</thead>
					<tbody>
						${valid
							.map(
								(row) => `
							<tr>
								<td class="city-cell"><span class="city-cell-name">${escapeHtml(row.city)}</span></td>
								<td class="country-code-cell">${escapeHtml(row.country)}</td>
								<td class="temp-cell">${Math.round(Number(row.temperature))}°C</td>
								<td>${escapeHtml(row.windspeed)} km/h</td>
								<td>${escapeHtml(row.condition)}</td>
							</tr>
						`
							)
							.join("")}
					</tbody>
				</table>
			</div>
		`;
	}

	compareResults.innerHTML = html || '<div class="error-subtext">No weather results available.</div>';
}

async function fetchJson(url) {
	const response = await fetch(url);
	const data = await response.json();
	return data;
}

function emptyHistoryMarkup() {
	return `
		<div class="empty-history">
			<div class="empty-icon-circle">
				<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<circle cx="12" cy="12" r="10"></circle>
					<polyline points="12 6 12 12 16 14"></polyline>
				</svg>
			</div>
			<div class="empty-title">No searches yet</div>
			<div class="empty-subtext">Your weather lookups will appear here automatically</div>
		</div>
	`;
}

function loadHistory() {
	if (!historyBody || !historyBadge || !downloadCsvBtn) return;

	if (sessionHistory.length === 0) {
		historyBadge.classList.add("hidden");
		downloadCsvBtn.classList.add("hidden");
		historyBody.innerHTML = emptyHistoryMarkup();
		return;
	}

	historyBadge.textContent = String(sessionHistory.length);
	historyBadge.classList.remove("hidden");
	downloadCsvBtn.classList.remove("hidden");

	const sorted = [...sessionHistory].reverse();

	historyBody.innerHTML = `
		<div class="table-wrapper">
			<table class="custom-table">
				<thead>
					<tr>
						<th>Timestamp</th>
						<th>City</th>
						<th>Country</th>
						<th>Temperature</th>
						<th>Wind Speed</th>
						<th>Condition</th>
					</tr>
				</thead>
				<tbody>
					${sorted
						.map(
							(row) => `
						<tr>
							<td class="timestamp-cell">${escapeHtml(row.Timestamp)}</td>
							<td class="city-cell"><span class="city-cell-name">${escapeHtml(row.City)}</span></td>
							<td class="country-code-cell">${escapeHtml(row.Country)}</td>
							<td class="temp-cell">${Math.round(Number(row.Temperature))}°C</td>
							<td>${escapeHtml(row.WindSpeed)} km/h</td>
							<td>${escapeHtml(row.Condition)}</td>
						</tr>
					`
						)
						.join("")}
				</tbody>
			</table>
		</div>
	`;
}

function addToSessionHistory(row) {
	sessionHistory.push(row);
}

function downloadHistoryAsCsv(history) {
	if (!history || history.length === 0) return;

	const headers = Object.keys(history[0]);
	const csvRows = [
		headers.map(escapeCsvValue).join(","),
		...history.map((row) => headers.map((header) => escapeCsvValue(row[header])).join(",")),
	];

	const blob = new Blob([csvRows.join("\n")], { type: "text/csv;charset=utf-8;" });
	const url = URL.createObjectURL(blob);
	const link = document.createElement("a");

	link.href = url;
	link.download = "weather_log.csv";
	link.click();

	URL.revokeObjectURL(url);
}

function historyRowFromWeather(data) {
	return {
		Timestamp: new Date().toISOString().replace("T", " ").slice(0, 19),
		City: data.city,
		Country: data.country,
		Temperature: data.temperature,
		WindSpeed: data.windspeed,
		Condition: data.condition,
	};
}

if (resultCard) {
	resultCard.addEventListener("click", (event) => {
		const pill = event.target.closest(".ambiguity-match-pill");
		if (!pill) return;
		selectAmbiguousMatch(pill.dataset.match || "");
	});
}

if (searchForm && searchInput && searchCountryInput && searchBtn && resultCard) {
	searchForm.addEventListener("submit", async (event) => {
		event.preventDefault();

		const city = normalizeText(searchInput.value);
		const country = normalizeText(searchCountryInput.value);
		if (!isValidCityInput(city) || !isValidCountryInput(country)) {
			showErrorState("Please enter a valid city and country.");
			return;
		}

		setButtonLoading(searchBtn, true, ".search-icon");
		showLoadingState();

		try {
			const data = await fetchJson(
				`/api/weather?city=${encodeURIComponent(city)}&country=${encodeURIComponent(country)}`
			);

			if (data && data.error) {
				if (data.ambiguous) {
					showAmbiguityState(data);
				} else {
					showErrorState(data.error);
				}
			} else {
				showSuccessState(data);
				addToSessionHistory(historyRowFromWeather(data));
				loadHistory();
			}
		} catch (error) {
			showErrorState("Something went wrong. Please try again.");
		} finally {
			setButtonLoading(searchBtn, false, ".search-icon");
		}
	});
}

if (compareForm && compareInput && compareBtn && compareResults) {
	compareForm.addEventListener("submit", async (event) => {
		event.preventDefault();

		const parsed = parseComparePairs(compareInput.value);
		if (parsed.error) {
			showCompareErrorState(parsed.error);
			return;
		}

		setButtonLoading(compareBtn, true, ".compare-icon");
		showCompareLoading();

		try {
			const responses = await Promise.all(
				parsed.pairs.map((pair) =>
					fetchJson(
						`/api/weather?city=${encodeURIComponent(pair.city)}&country=${encodeURIComponent(pair.country)}`
					).catch(() => ({ error: `Could not fetch weather for ${pair.label}.` }))
				)
			);

			renderCompareResults(responses);

			responses.forEach((res) => {
				if (res && !res.error) {
					addToSessionHistory(historyRowFromWeather(res));
				}
			});

			loadHistory();
		} catch (error) {
			compareResults.innerHTML = '<div class="error-subtext">Something went wrong. Please try again.</div>';
		} finally {
			setButtonLoading(compareBtn, false, ".compare-icon");
		}
	});
}

if (downloadCsvBtn) {
	downloadCsvBtn.addEventListener("click", () => {
		if (sessionHistory.length === 0) return;
		downloadHistoryAsCsv(sessionHistory);
	});
}

document.addEventListener("DOMContentLoaded", () => {
	loadHistory();
});
