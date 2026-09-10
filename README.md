# Expedia Lite — Part 1

A small city-search application built with Vue 3, FastAPI, and the supplied fictional Expedia Lite CSV data.

## Structure

- `frontend/`: Vue/Vite browser interface
- `backend/`: FastAPI service, CSV data, and backend tests
- `docs/design.md`: concise design decisions
- `prompts/`: selected implementation prompts
- `handoffs/current.md`: current implementation and verification status

## Setup

Requirements: Python 3.11+ and Node.js 20+.

```sh
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
cd frontend
npm install
```

No environment variables are required. By default the frontend calls `/api`, which Vite proxies to `http://127.0.0.1:8000` during development.
Set `VITE_API_TARGET` only when the backend must use a different local port.

## Run

From the repository root, start the backend:

```sh
backend/.venv/bin/python -m uvicorn backend.app.main:app --reload --port 8000
```

In a second terminal, start the frontend:

```sh
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173`.

## Checks

```sh
backend/.venv/bin/python -m pytest backend/tests
cd frontend
npm run test
npm run build
```

Expected sample checks: `Boston` returns 4 stays (`T001`, `T002`, `T009`, `T010`); `Miami` returns none.
