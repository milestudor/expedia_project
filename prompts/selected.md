# Selected prompts

- Add a standalone backend ZIP lookup controller using Geoapify forward geocoding,
  existing HTTPX, and the configuration helper. Validate exact U.S. postcode and coordinates,
  distinguish unresolved results from safe provider failures, and verify with mocks.
  Keep routes and Vue unchanged; only `"16802"` is approved as a live demonstration input.

- Load the project-root `.env` in a separate backend helper using existing python-dotenv;
  extend health with only the key configuration status, preserve existing health information,
  treat absent/empty/whitespace values as unconfigured, and document backend restart requirements.
  Do not expose the key or call Geoapify.

- Implement Part 2 with SQLite-backed reads and writes after one-time seeding; preserve existing IDs and saved changes across restarts.
- Keep Vue in `frontend/` and FastAPI/Python in `backend/`; route every CRUD action through the frontend and API.
- Search by hotel name, simulate booking creation, read history, cancel by retaining and updating the record, and delete a test booking.
- Use a persistent sequence for unique new booking IDs and test CRUD plus restart persistence in a temporary database.
- Follow CHECK → TAKE ACTION → VERIFY for dependencies, update project context, and do not commit, merge, or push before manual review.

- Add the thin fixed-ZIP demo route, map configuration/unresolved/provider errors safely,
  test with a mocked controller, preserve unrelated processes, and make exactly one
  live request to the local route after checking project startup.

- Add a small ZIP lookup demonstration panel with one fixed-ZIP button, backend-proxy
  requests, loading/duplicate-click protection, cleared stale results, labeled location
  fields, and backend errors. Preserve hotel search; run frontend checks and stop for review.

- Verify the visible browser ZIP round trip against Chrome Network, check a quota-free
  mocked provider failure and hotel-name search, restore normal behavior, and document
  expected versus observed results and the responsible files without adding features.

- Replace the fixed ZIP demonstration with a text field that searches the entered U.S.
  ZIP, preserving leading zeros, validating input, and retaining backend-only credentials.

## Assignment 2 Part 1 — September 29, 2026

AI tool/model: OpenAI Codex desktop, GPT-6 (agent session). Used for assignment interpretation, repository inspection, primary-source research through web tools, the pre-implementation SVG mockup, Vue/FastAPI changes, tests, browser automation, documentation and report drafting. Playwright/Chrome are verification tools, not additional AI models. No subagents were used. The exact deployment build identifier is not exposed in this session.

Selected excerpts and linked effects:

- User: “please view the following instructions and only complete what is asked for part 1 please.” → [live service](../backend/app/hotel_search.py), [discovery view](../frontend/src/HotelDiscovery.vue), [map](../frontend/src/HotelMap.vue); existing sample app preserved; no shortlist.
- Agent asked: “May I install Leaflet 1.9.4 in frontend/ for the required interactive map?” User: “Approve Leaflet 1.9.4 installation.” → CHECK found it absent; TAKE ACTION installed the exact approved version; VERIFY `npm ls leaflet`, tests, lint and build passed.
- Design decision: exact requested postcode and U.S. country must match before Places; public records are not room inventory → [research](../docs/assignment-2-part-1/research.md), [early mockup](../docs/assignment-2-part-1/mockup.svg), [provider tests](../backend/tests/test_hotel_search.py).
- Failed/revised approach: first environment check used root `.venv`, which lacked dotenv. The project's documented `backend/.venv` already had the required libraries; switched to that runtime without installing another Python dependency.
- Failed/revised approach: normal sandbox install could not reach npm. The approved installation succeeded with network access; no package/version substitution.
- Failed/revised approach: the bundled Playwright browser and recording helper were unavailable. Browser verification switched to the existing Chrome installation; recording helper approval was requested separately.
- Verification decision: use one real ZIP response for live evidence, and label simulated empty/unresolved/failure states; automated tests simulate provider rate limits, never deliberately exhaust quota. See [verification](../docs/assignment-2-part-1/verification.md).

All generated work remains subject to student review. No commit, push, repository visibility change, deployment, or course submission was performed by the agent in this turn.
- Browser-discovered correction: Leaflet Enter opened a popup without firing the marker click selection handler. Added explicit Enter/Space selection handling and preserved marker DOM while highlighting; reran the browser check. This was a real implementation failure, not a simulated provider failure.
- User approved: “Approve video helper download.” Downloaded Playwright FFmpeg v1011 solely for verification, leaving app manifests unchanged; existing Chrome used for browser capture.

- Student review: “once i click sample stays, should i be able to go back to the new search” → added a visible return link in [LegacyApp.vue](../frontend/src/LegacyApp.vue), with keyboard focus styling and wrapping navigation. No dependencies changed.

## Publication approval

User: “okay it looks really good. Unless there's anything extra you want to add to make this look more fancy, please commit and push”. No extra visual features added. Manual review and return-navigation correction accepted; approved implementation committed, repository verified public, and report finalized with public links. Prior “no commit” statements describe earlier checkpoints.

## October 1, 2026 — Database/API comparison

User requested inspection of the existing hotels schema and sample rows, a live ZIP search with Network response inspection, field/price/date-storage comparison, and evidence for a later schema request. Agent inspected the actual SQLite file read-only and submitted ZIP 16802 once in Chrome (21 hotels, HTTP 200). Recorded schema, full copied response, screenshot, and findings in docs/assignment-2-part-2/. DB Explorer UI inspection remains incomplete because VS Code displayed a blank project window; this does not represent student manual verification. No schema or application changes were made.

## October 1, 2026 — Additive saved hotel schema

User confirmed the manual DB Explorer comparison and requested saved_hotels (exact provider ID, nullable name/address, valid required coordinates) and demo_hotel_nights (hotel FK, valid date, composite key, nonnegative integer defaults of 10000 cents and 20 rooms). Scope explicitly excludes frontend controls, API behavior changes, chatbot features, and dependencies; stop for manual review. Added repeatable startup migration and constraint tests. Existing database schemas/rows verified unchanged; new tables empty. Results: 88 backend tests, 24 frontend tests, lint/build passed. See docs/assignment-2-part-2/schema-migration.md. No commit or push.

## October 1, 2026 — Wire local storage and local-first lookup

User requested transactional save/delete endpoints, separate searched-ZIP context, five demo dates October 10–14, 2026 with non-overwriting defaults, Add/Remove buttons, database-backed saved status after refresh, and local-first search with no fallback on local failure. Implemented within the existing dependencies while preserving the Part 1 endpoint and Assignment 1 records. Added temporary-database mutation and frontend flow tests: 95 backend / 30 frontend tests pass, lint/build pass. Verified server ownership before restarting only project servers; read-only health/proxy checks passed. Manual browser and database changes remain for the student. Details in docs/assignment-2-part-2/local-storage.md. No commit/push.

## October 1 — Delegated rate/room edit verification

User requested that the agent perform the rate/room edit and verification due to time constraints. Updated only Nittany Lion Inn's October 10 demo row from 10000 cents/20 rooms to 500 cents/10 rooms in a committed SQLite transaction. Repeated ZIP 16802 in the browser and observed matching $5.00/10-room display. Captured before/after screenshots and database values; preserved every unrelated record. Not a student-performed DB Browser check. No commit/push.

## October 6, 2026 — revised Part 2 SQL RAG implementation

User prompt: “Please begin Assignment 2 part 2” with the revised full-credit sequence, mandatory local storage, backend-only credentials, read-only SQL checks, multi-night totals and a second grounded-answer request. User asked which provider was recommended; free OpenRouter/Nemotron was recommended based on class alignment and official availability research. Exact class configuration remains pending.

Codex (GPT-6-based agent; exact app model variant not exposed) inspected existing MVC/storage and dependencies, created `docs/assignment-2-part-2/chatbot-mockup.svg` before implementation, and wrote `backend/app/hotel_chat.py`, `model_preflight.py`, the `/api/hotel-chat` controller, `frontend/src/HotelChat.vue`, tests and draft evidence. No dependencies installed, no commit/push.

Query-prompt excerpt: “Return ONLY JSON ... Query ONLY hotel_stay_options ... total_cost_cents is NULL if any requested night is missing ... Read-only SELECT only.” Grounding excerpt: “Answer the original question ONLY from the supplied retrieved records ... Missing nights imply insufficient data, never availability.” Full prompts live in `hotel_chat.py` and link directly to service behavior. Model SQL chooses relevant IDs; backend canonical calculations replace any proposed price columns.

Revised approaches: unrestricted joins were narrowed during design to a temporary view so complete-stay totals/availability are enforced centrally. Initial Vue lint emitted 33 formatting warnings; formatting was fixed and lint rerun clean. The first browser fixture inherited Boston locality from a shared helper despite ZIP 16802; fixture center was corrected to State College before final captured evidence. No claim is made that these fixture outputs came from Nemotron.

Verification: 122 backend/34 frontend tests pass; lint/build pass. Browser: mocked $105 full stay, keyboard no-match, rejected DELETE, normal missing-model configuration feedback, real local-first ZIP 16802 and list/map selection, sample-stays navigation. Full mock trace at `docs/assignment-2-part-2/chat-fixture-evidence.json`; SQLite rejects disallowed proposals without changing database bytes. Live model generation remains pending key/class model configuration and must be logged separately.

## October 6 — supplied RAG-context activity, persistent history and OpenAI

User supplied the full class activity and asked to complete it. Refined requirements: a separate startup-loaded prompt, actual JOIN relationships, checked SQL with parameters, a second grounded request, and “Save records as each step occurs, including failed attempts.” User asked whether the agent could pick an API/key and store it privately. The agent chose class model **gpt-5.6-luna**, prepared ignored `.env` with owner-only 0600 permissions and OPEN_AI blank, and explained that a valid personal key must be created in the student's OpenAI account; none was invented or transmitted.

OpenAI Docs skill was used to fetch official gpt-5.6-luna, Responses and conversation-state pages. The custom OPEN_AI value is passed explicitly via existing httpx to Responses; no SDK/dependency installed. Current model pricing was verified, but account credit/model access/live success remain unverified without a key. Medium reasoning/verbosity, default tier, 4000-token output cap, 60-second timeout and store=false adapt the reference without streaming or provider-managed conversation storage.

Code/evidence: prompts/hotel-assistant.md contains purpose, actual postcode column, both hotel_id JOINs and the two model-stage instructions. backend/app/chat_history.py and additive migrations store each stage and recover interrupted turns. hotel_chat.py now binds parameters and supports basic greetings, clarifications and successful-history context for fresh follow-up retrieval. FastAPI exposes saved history, and HotelChat.vue restores conversations from SQLite. User/assistant/error roles remain distinct. No model query can read chat/private tables or mutate hotels.

Revised/failed approach: the earlier stateless OpenRouter/view-only implementation could not meet the newly supplied history/follow-up/prompt-file activity, so it was replaced. The initial scripted class fixture carried an unrequested $250 budget from the old sample; corrected before final class screenshots/export. Final class query has both JOINs, ZIP/date parameters, complete-night room requirements, deterministic price ordering and LIMIT 3. Mocks are not live model evidence.

Final checks: **132 backend tests, 37 frontend tests, clean lint and build**. Browser mocks verify greeting, class example, dated follow-up, no-match, saved DELETE rejection, backend restart/page refresh persistence. The normal app saved an honest missing-key failure before making any remote call. Nine pre-existing table schemas/rows compared identical after migration and verification. docs/rag-context.md records the full workflow; docs/assignment-2-part-2/rag-conversation-evidence.json contains the labeled 38-message isolated trace. No commit/push. Exact Codex app model variant remains a student disclosure field; agent context identifies it as GPT-6-based.


## October 6 — actual OpenAI verification

Student privately saved OPEN_AI. Read-only model access preflight succeeded for gpt-5.6-luna. Browser calls used normal 5173/8000, actual saved SQLite, no provider hotel fabrication. Initial trace: bde6c942-71b8-4fae-b7fc-6f1fcac69ee4.

| Input/action | Expected | Observed |
|---|---|---|
| ZIP16802, one room Oct10–12, under $250 | Both nightly records; checkout excluded; $105 | Live SQL JOIN retrieval + second model answer: $5/$100, $105, minimum 10 rooms, simulated label |
| What about October12? | Preserve ZIP/year/rooms; one night Oct12–13 | Fresh live query; $100; 20 rooms; simulated label |
| ZIP00000 Oct12–13 | Empty local records; no invented quote/hotel | Live second call receives []; explains no matches/unknown prices |
| Backend restart + page refresh | Durable messages/trace | Previous successful and failed turns restored |
| Original hotel/sample tables | No schema/row change | Nine original tables unchanged in rag-live-preservation.json |

Evidence: assignment-2-part-2/rag-live-initial-evidence.json, rag-live-evidence.json, rag-live-success.png, rag-live-no-match.png. Model source is live-model, unlike retained fixtures. ZIP00000 checks local SQL no-match; it is not a successful geocoding claim.

Failed/revised live proposals: extra top-level nights rejected; exact JSON keys added to prompt. GROUP_CONCAT rejected; exact allowlist/hotel_id-only projection added. No automatic retries or quota exhaustion. App import during verification initially marked a pending turn interrupted; moved recovery to actual server lifespan, added regression assertions, retained original trace for disclosure. Successful final turn confirms revised behavior. Backend tests remain 132 passing; prior frontend37/lint/build unchanged. Live recording, manual review, assessed commit/publishing/access are still pending.

Final confirmation: conversation cf2f2335-a33f-4c73-81a0-0b56fe886730 completed the corrected prompt’s two-call workflow with $105 and no spurious interruption; final trace rag-live-evidence.json has 15 messages, including the earlier rejected GROUP_CONCAT. Ten total paid generation requests were attempted this turn, no automatic retries; actual cost must be read in the account usage dashboard. Backend remains running on 8000 (PID24403), frontend5173; live success tab left open. No dependency installations, commits or pushes.


## October 6 — student empty-storage retest correction

Student screenshots at 20:48–20:51 UTC showed empty results for the first two questions. Direct read-only inspection found saved_hotels, saved_hotel_zips and demo_hotel_nights all empty. Saved proposal logs use the correct ZIP, cents budget and dates; empty results are genuine, not a retrieval regression. Prior expected $105/$100 values were conditional on the saved hotel and manual $5 nightly edit remaining. No deleted hotel/rates were restored. Re-saving provider hotel seeds default $100 nightly rates for Oct10–14: two-night expected $200, Oct12 expected $100, Oct14–16 incomplete because Oct15 missing.

Adjustment: second LLM receives saved_hotel_count, with instructions to distinguish empty storage from filtered no-match; frontend shows explicit Add to Local guidance for zero saved hotels. General empty-filter feedback no longer implies all dated records are absent. Regression tests prove the count reaches the second call and empty inventory is not mutated, and verify frontend guidance. Verification: 133 backend / 38 frontend tests, lint/build pass. Live empty-storage evidence in docs/assignment-2-part-2/rag-empty-storage-live.json. Historical successful traces remain labeled with their earlier data state. No dependency change, commits or pushes.


October 8 presentation/manual-review update: assistant display removes Markdown bold/backticks, replaces long provider IDs and wraps long text; raw saved messages and workflow evidence remain intact and HTML stays escaped. Runtime answer prompt requests plain text and names instead of provider IDs. Added docs/assignment-2-part-2/manual-review.md with unfilled student observations, report review and labeled student-run rejection checks. Student manual verification is pending; agent cannot certify it on the student’s behalf. No dependencies installed or commits/pushes.


October8 demo/report packaging: docs/assignment-2-part-2/part-2-rag-demo.webm (81sec edited silent browser screen capture at about1fps; LIVE/MOCK footer); live trace demo-live-trace-oct8.json and isolated rejected DELETE/before-after trace demo-rejection-trace-oct8.json. Student confirmed GPT-6.1 Sol and that ZIP/chat questions were performed; copied supplied screenshots into student-{success,followup,insufficient-data}.png. manual-review.md records only confirmed observations and leaves other checks pending. Report reviewed before these final edits; new video/report review needed. Assessed commit/public links remain pending; no commit/push. No dependencies installed; existing bundled Pillow and previously approved FFmpeg used to encode actual CUA browser captures.
