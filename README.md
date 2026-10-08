# Expedia Lite — Assignment 2, Part 1

Live U.S. ZIP hotel discovery using Vue, FastAPI, Geoapify and Leaflet. Search resolves the requested U.S. postcode, then retrieves up to 50 hotel records within 5 km of its returned point. List and map selections stay synchronized. No hotel inventory, prices, ratings, booking, or shortlist is inferred from the provider data.

The original CSV/SQLite sample-stay application is preserved at `/sample-stays`. Its header includes “← ZIP hotel search” to return to the new discovery page. Its existing booking functionality is a classroom simulation and is separate from Assignment 2. Assignment 2 Part 2 now adds local saving and simulated dated rates/availability; it does not add booking for provider hotels.

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

The student completed manual review and authorized commit and push. The assessed implementation commit is `92b910b`; [report.md](report.md) includes public submission links. Future changes still require the review workflow in AGENTS.md.

## Part 2 preflight observations

The October 1 database/API comparison and captured evidence are in [schema comparison](docs/assignment-2-part-2/schema-comparison.md). The student reports completing that DB Explorer checkpoint. The additive saved-hotel and daily-demo schema is now implemented; see [migration details and verification](docs/assignment-2-part-2/schema-migration.md). Local storage is now connected through Add/Remove controls and local-first ZIP lookup; see [local storage behavior and verification](docs/assignment-2-part-2/local-storage.md). Explicit saves create October 10–14, 2026 demo nights using fictional defaults of 10000 cents and 20 rooms. Repeated saves preserve edited values. The Part 1 API remains unchanged. Manual browser/database review is pending.

Agent-assisted verification on October 1 confirmed that committed edits for Nittany Lion Inn, October 10, 2026, appear after repeating ZIP 16802: $5.00/night and 10 rooms. See the [before/after evidence](docs/assignment-2-part-2/local-storage.md). These remain fictional classroom values.

## Assignment 2 Part 2 — SQL RAG and saved conversations

The discovery page includes **Ask about saved hotels**, saved user/assistant messages, follow-ups, and a durable trace of SQL, parameters, retrieval, answers and errors. The backend loads `prompts/hotel-assistant.md` on startup and uses **OpenAI gpt-5.6-luna** for query proposals and grounded answers. Model queries are restricted to bounded read-only local hotel retrieval; separate application-owned operations save conversation history. Demo rates/rooms are simulated course data, checkout is excluded and missing nights cannot imply availability.

No dependency installation is needed in the existing environment. Privately set `OPEN_AI` in the ignored root `.env`; `OPENAI_MODEL=gpt-5.6-luna` is the class default. Restart the backend after changing `.env` or the prompt. Run `backend/.venv/bin/python -m backend.app.model_preflight` to check configured model access without generation; API credit/spend limits are checked in your OpenAI account. Credentials never reach Vue. The previous provisional OpenRouter setup has been replaced by the supplied OpenAI activity.

[Current RAG-context instructions, schema/JOINs, API contract, research and verification](docs/rag-context.md), [draft Part 2 report](docs/assignment-2-part-2/report.md), [early mockup](docs/assignment-2-part-2/chatbot-mockup.svg), [fixed JSON sample](docs/assignment-2-part-2/chat-fixture.json), [persisted mocked evidence](docs/assignment-2-part-2/rag-conversation-evidence.json), and [demo script](docs/assignment-2-part-2/demo-script.md). Root report.md remains Part 1. Part 2 is due **October 8, 2026, at 11:59 PM Eastern**.

Current checkpoint: **132 backend tests / 37 frontend tests pass; lint/build pass**. Browser mocks verify greeting, both hotel JOINs, a dated follow-up, no matches, rejection, and refresh/backend restart persistence. No personal API key is configured, so successful live model calls and the recorded live demo remain pending. No changes were committed or pushed; active branch is rag_integration.


Live OpenAI verification completed October 6: the two-night $105 result, $100 follow-up, no-match answer and refresh/restart persistence passed. See [live verification](docs/rag-context.md) and the [Part 2 report](docs/assignment-2-part-2/report.md). Final live recording and student review remain pending.


## October 6 — student empty-storage retest correction

Student screenshots at 20:48–20:51 UTC showed empty results for the first two questions. Direct read-only inspection found saved_hotels, saved_hotel_zips and demo_hotel_nights all empty. Saved proposal logs use the correct ZIP, cents budget and dates; empty results are genuine, not a retrieval regression. Prior expected $105/$100 values were conditional on the saved hotel and manual $5 nightly edit remaining. No deleted hotel/rates were restored. Re-saving provider hotel seeds default $100 nightly rates for Oct10–14: two-night expected $200, Oct12 expected $100, Oct14–16 incomplete because Oct15 missing.

Adjustment: second LLM receives saved_hotel_count, with instructions to distinguish empty storage from filtered no-match; frontend shows explicit Add to Local guidance for zero saved hotels. General empty-filter feedback no longer implies all dated records are absent. Regression tests prove the count reaches the second call and empty inventory is not mutated, and verify frontend guidance. Verification: 133 backend / 38 frontend tests, lint/build pass. Live empty-storage evidence in docs/assignment-2-part-2/rag-empty-storage-live.json. Historical successful traces remain labeled with their earlier data state. No dependency change, commits or pushes.


October 8 presentation/manual-review update: assistant display removes Markdown bold/backticks, replaces long provider IDs and wraps long text; raw saved messages and workflow evidence remain intact and HTML stays escaped. Runtime answer prompt requests plain text and names instead of provider IDs. Added docs/assignment-2-part-2/manual-review.md with unfilled student observations, report review and labeled student-run rejection checks. Student manual verification is pending; agent cannot certify it on the student’s behalf. No dependencies installed or commits/pushes.


October8 demo/report packaging: docs/assignment-2-part-2/part-2-rag-demo.webm (81sec edited silent browser screen capture at about1fps; LIVE/MOCK footer); live trace demo-live-trace-oct8.json and isolated rejected DELETE/before-after trace demo-rejection-trace-oct8.json. Student confirmed GPT-6.1 Sol and that ZIP/chat questions were performed; copied supplied screenshots into student-{success,followup,insufficient-data}.png. manual-review.md records only confirmed observations and leaves other checks pending. Report reviewed before these final edits; new video/report review needed. Assessed commit/public links remain pending; no commit/push. No dependencies installed; existing bundled Pillow and previously approved FFmpeg used to encode actual CUA browser captures.
