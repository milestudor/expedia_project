# Expedia Lite — Part 2

A Vue 3 and FastAPI travel app with durable SQLite hotel search and booking CRUD.

## Structure

- `frontend/`: search, simulated booking, booking history, cancellation, and test deletion
- `backend/`: FastAPI routes, SQLite data access, seed CSVs, and backend tests
- `backend/data/`: original hotels/trips plus starter users/bookings; the generated database is ignored by Git
- `docs/design.md`, `prompts/selected.md`, and `handoffs/current.md`: concise project context

## Setup

Requirements: Python 3.11+ and Node.js 20+.

```sh
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
cd frontend
npm install
```

SQLite is included with Python, so Part 2 adds no dependency. The frontend uses Vite's `/api` proxy to `http://127.0.0.1:8000` by default.

## Run

Start the backend from the repository root:

```sh
backend/.venv/bin/python -m uvicorn backend.app.main:app --reload --port 8000
```

In a second terminal:

```sh
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173`. The first backend start creates `backend/data/expedia_lite.db` and seeds empty tables. Later starts retain saved changes. For an intentional reset, stop the backend, delete only that database file, and restart.

## Checks

```sh
backend/.venv/bin/python -m pytest backend/tests
cd frontend
npm run test
npm run lint
npm run build
```

The backend tests create, read, cancel, delete, and reopen a temporary database to verify persistence and non-duplicating seeds.
