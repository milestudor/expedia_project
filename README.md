# Expedia Lite — Assignment 2, Part 1

Live U.S. ZIP hotel discovery using Vue, FastAPI, Geoapify and Leaflet. Search resolves the requested U.S. postcode, then retrieves up to 50 hotel records within 5 km of its returned point. List and map selections stay synchronized. No hotel inventory, prices, ratings, booking, or shortlist is inferred from the provider data.

The original CSV/SQLite sample-stay application is preserved at `/sample-stays`. Its header includes “← ZIP hotel search” to return to the new discovery page. Its existing booking functionality is a classroom simulation and is separate from Assignment 2. No Assignment 2 Part 2 shortlist was added.

## Setup

Requirements: Python 3.11+ and Node.js 20.19+ or 22.12+.

```sh
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
cd frontend
npm ci
cd ..
cp .env.example .env
```

Do not overwrite an existing `.env`. Put your own Geoapify key in the project-root `.env`:

```dotenv
GEOAPIFY_API_KEY=your_backend_geoapify_key_here
```

The root file is loaded by explicit path; process environment values take precedence. Restart the backend after editing it. `.env` is ignored and must never be committed. There is no frontend API key or tile key. `GET /api/health` reports configuration presence without exposing the key or calling the provider.

## Run

From the repository root:

```sh
backend/.venv/bin/python -m uvicorn backend.app.main:app --reload --port 8000
```

In another terminal:

```sh
cd frontend
npm run dev
```

Open [the application](http://127.0.0.1:5173). Vite proxies `/api` to port 8000. The backend needs internet access to Geoapify; the browser needs access to OpenStreetMap tiles. Public tiles are appropriate for modest classroom use, subject to their usage policy.

## Behavior and limits

- ZIPs remain strings, preserving leading zeros. Trimmed input must be five ASCII digits.
- Exact postcode and U.S. country must match before the hotel request. The circle is around the returned point, not the ZIP boundary or traveler.
- `GET /api/hotels?postcode=02108` returns center, hotels, radius, limit and limit flag. Hotels use provider IDs and nullable text fields with valid coordinates.
- Loading, invalid input, unresolved ZIP, empty results and request failure have distinct feedback. Missing hotel names/addresses receive honest labels.
- Results are limited to 50; coverage varies and is not exhaustive. Each submission makes at most two provider calls, with no automatic retries or polling.
- Hotel list buttons and map markers support keyboard selection. OSM and Geoapify attribution remain visible.

## Verification and submission

```sh
backend/.venv/bin/python -m pytest backend/tests -q
cd frontend
npm test
npm run lint
npm run build
npm ls leaflet
```

See [report.md](report.md) for the Part 1 report, [research](docs/assignment-2-part-1/research.md), [early mockup](docs/assignment-2-part-1/mockup.svg), [verification](docs/assignment-2-part-1/verification.md) and [AI evidence](prompts/selected.md). Prior assignment report: [archive](docs/assignment-1-report.md).

Architecture and verification rules are in [AGENTS.md](AGENTS.md) and [docs/design.md](docs/design.md). Original sample hotels/trips remain joined by `hotel_id` with case-insensitive trimmed city matching. The existing database is ignored and retained; live discovery does not write hotel records into it.

Do not commit or push until manual review of changes and browser results. The report's assessed commit and instructor-accessible artifact URLs must be finalized after that review.
