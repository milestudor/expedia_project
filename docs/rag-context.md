# RAG context activity — implementation and verification

Observation date: **October 6, 2026 (Eastern)**. Branch: `rag_integration`. This checkpoint follows the attached “RAG Context for Expedia Replica Lite” activity. **Implementation and mocked checks are complete; live OpenAI exchanges remain blocked by an unconfigured API key.** No live success, purchased credit, instructor submission, commit or push is claimed.

## OpenAI setup and privacy

The activity supersedes the earlier provisional OpenRouter implementation. The backend now uses OpenAI Responses with **`gpt-5.6-luna`**, matching the class model. Official [model documentation](https://developers.openai.com/api/docs/models/gpt-5.6-luna) was checked October 6: text input $0.20, cached input $0.02, output $1.20 per million tokens. Account model access, credit and limits are not established without the student's key.

[Responses reference](https://developers.openai.com/api/reference/python/resources/responses/methods/create) and [conversation-state guidance](https://developers.openai.com/api/docs/guides/conversation-state) informed the implementation. Existing httpx makes backend HTTPS calls directly; no OpenAI SDK installation is needed. Requests supply actual input, the loaded prompt, medium reasoning/verbosity, default service tier, a 4,000-output-token ceiling and a 60-second timeout. Unlike the streaming reference, the application waits for one completed response, then extracts text from output message items. Incomplete, refusal-only, malformed and failed responses are errors. `store=false` avoids remote response-state storage; this does not imply zero provider data retention. Local SQLite stores the application's trace.

The root `.env` is ignored/untracked and was set to owner-only read/write permissions (0600). Existing settings were preserved. These are the required backend variables:

```dotenv
OPEN_AI=your_private_OpenAI_API_key
OPENAI_MODEL=gpt-5.6-luna
```

`OPEN_AI` is a custom class variable, passed explicitly as the bearer credential. A standard SDK environment-variable assumption is not used. The agent set the model but did not generate a key. The student must create a key in their own OpenAI API account, ensure API credit, and enter it privately. Do not paste it into chat or use a `VITE_` variable. Owner-only permissions do not exclude administrators or software running as the same user.

Check without generation:

```sh
backend/.venv/bin/python -m backend.app.model_preflight
```

It detects configuration without printing the key, and, when configured, checks `/v1/models/gpt-5.6-luna`. It does not prove credit or generate a reply. Current observed result: configured=false. Restart the backend after editing `.env` or the prompt.

## Actual schema and both JOINs

[Prompt file](../prompts/hotel-assistant.md) is read on backend startup. Its SHA-256 version and full query/answer prompt snapshots are saved per turn. `AGENTS.md` contains developer guidance; it is not the runtime system prompt.

| Table | Actual columns and meaning |
| --- | --- |
| saved_hotels | hotel_id provider ID; nullable name/address; latitude/longitude |
| saved_hotel_zips | hotel_id, **postcode**; composite primary key; ZIP association |
| demo_hotel_nights | hotel_id, stay_date; unique per hotel/date; nightly_rate_cents and rooms_available are simulated course data |
| saved_zip_contexts | postcode, country_code, latitude, longitude, locality; original searched location |

The class's example column `zip` is called `postcode` here. No column was renamed or hotel data rewritten to imitate the example.

First JOIN: `saved_hotels h JOIN saved_hotel_zips z ON z.hotel_id=h.hotel_id` selects hotel associations near a searched ZIP. Second JOIN: `JOIN demo_hotel_nights n ON n.hotel_id=h.hotel_id` supplies dated demo costs and rooms. A locality lookup can additionally join saved_zip_contexts by postcode.

For the class question:

> Show the three cheapest saved hotels near ZIP 16803 with at least one room available for the night of October 11, 2026.

The **mocked** final proposed SQL was:

```sql
SELECT h.hotel_id
FROM saved_hotels h
JOIN saved_hotel_zips z ON z.hotel_id=h.hotel_id
JOIN demo_hotel_nights n ON n.hotel_id=h.hotel_id
WHERE z.postcode=:postcode
  AND n.stay_date>=:check_in AND n.stay_date<:check_out
GROUP BY h.hotel_id
HAVING COUNT(n.stay_date)=:nights
   AND MIN(n.rooms_available)>=:rooms
ORDER BY SUM(n.nightly_rate_cents), h.hotel_id
LIMIT 3
```

Parameters: postcode=16803, check_in=2026-10-11, check_out=2026-10-12, nights=1, rooms=1. The single requested night implies next-day checkout. For several nights, COUNT must match the requested duration and MIN must satisfy the room count every night; total cents equals SUM(nightly_rate_cents)*rooms. Checkout is excluded. Missing dates mean unknown availability and no complete total. Cents are divided by 100 for USD display.

## Complete request and persisted trace

1. Vue sends question and, for a follow-up, conversation_id to the application's FastAPI endpoint. No credential is included.
2. The backend creates/reserves a turn and saves user input before the model call. It includes up to 12 previous successful user/assistant messages (each capped at 2,000 context characters) and previous interpreted stay/question. Failed attempts remain in the trace but do not become hotel evidence.
3. First OpenAI request receives the prompt/schema/rules, question and bounded history. It proposes SQL, scalar named parameters and dates/rooms. Basic greetings use one call and make no hotel claims; unclear hotel intent can produce a saved clarification. Hotel recommendations cannot use the direct-chat shortcut.
4. Validate proposal shape, scalar parameter types, dates, 1–30 night duration and 1–20 rooms. Canonical date/room/night parameters override proposed values. Permit one SELECT, deny separators/comments and reject unauthorized operations through SQLite's authorizer.
5. Use a read-only SQLite URI, query_only, approved-table/function allowlist, and approximately 2-million VM instruction/two-second progress budget. Queries can read only the four relevant hotel tables or the backend hotel_stay_options view. Assignment 1 tables, conversation tables, metadata, PRAGMAs, extensions and writes are denied. No remote model accesses SQLite directly.
6. Execute `SELECT DISTINCT hotel_id FROM (<proposal>) LIMIT 21`, return at most 20 hotels and mark truncation. Fetch canonical hotel details, all requested nights, totals and availability from a backend-created TEMP view in the same read snapshot. Model-created price columns are not trusted.
7. Save the executed query/parameters and retrieved records, then send those actual records with the original question to OpenAI again. The answer prompt requires honest no-match/incomplete-data handling, simulated labels and no invented prices, rooms or hotels.
8. Save the final assistant answer and complete result only after successful generation. Display it with dates, canonical evidence and workflow disclosure. Errors are saved as tool/error stages without a fabricated success.

Each stage commits separately, while hotel retrieval uses its own read-only connection. **Conversation logging writes are server-owned and are not model-authorized hotel writes.** No long write transaction is held during a remote call.

Tables added: chat_conversations (ID/title/timestamps), chat_turns (turn ID, status, prompt version, result JSON), chat_messages (unique message_id, conversation_id, turn_id, timestamp, role, stage, content, prompt_version; sequence orders records). Roles are system/user/assistant/tool; labels distinguish prompt_snapshot, query_request, proposed_sql, validated_proposal, executed_sql, retrieval_result, answer_request, assistant_answer and error.

GET `/api/hotel-chat/conversations` returns the 20 most recently updated conversations. GET `/api/hotel-chat/conversations/{id}` returns the latest 200 trace rows plus latest turn result and truncation signal. Older rows remain in SQLite. Browser storage remembers only the selected ID; content is loaded from the backend after refresh. Start new conversation clears the selection without deleting backend history. A pending turn blocks overlapping same-conversation requests; startup records an unfinished turn as interrupted. This is a local single-user course application, with no multi-user authentication or public deployment added.

## Expected versus observed verification

Final automated checks: **132 backend tests and 37 frontend tests pass; clean lint; production build passes.** One existing AnyIO deprecation warning remains. Existing ZIP/provider/list-map/local-save/removal/restart tests also pass.

| Check | Expected | Observed October 6 |
| --- | --- | --- |
| Greeting, followed by class hotel question | Distinct user/assistant messages; hotel query uses retrieval | Browser/mock: greeting saved; class question proposes both JOINs, binds 16803 and Oct 11, returns Fixture Inn at $100 for one night |
| “What about October 12?” | Same conversation; prior context supplied; new dated lookup | Mock/browser retrieves Oct 12 only, $100; previous successful exchange passed in query context |
| ZIP 00000, Oct 11 | Empty retrieval and grounded explanation | Mock/browser: empty records and clear no-match answer saved |
| DELETE proposal | Reject and log error; no hotel mutation/answer | Mock/browser/test: 422, saved proposed SQL and error; no assistant_answer for failed turn |
| Second-call provider failure | Preserve retrieval trace and failure, no false completion | Test: retrieval_result and answer_request saved; rate-limit error saved; latest_result=null |
| Multi-night missing record | No complete price or confirmed availability | Test: 5/6 nights, NULL total, available=0 |
| Two rooms with one on one night | Availability false, two-room total | Test: minimum=1, available=0, total=$210 |
| Approved parameterized joins and table restrictions | Relevant data readable; private/history tables denied | Tests pass; query params bind, privileged date values override proposal |
| Expensive query / unauthorized function | Interrupt or reject | Progress/function checks reject |
| Backend restart and page refresh | Messages/trace reload, including failures | Browser restarted isolated backend twice and refreshed; greeting, hotel answers, no-match and error remained |
| Unfinished turn | Preserve trace and mark interruption | Test: pending turn recovered to interrupted/error, no fabricated answer |
| Missing OpenAI key | Safe error with retry, failed attempt recorded | Preflight configured=false; backend missing-key tests and normal-browser saved failure pass; no live generation performed |
| Root .env | Ignored and private permissions; no key exposed | git check-ignore confirms; 0600; only configuration booleans printed |
| Existing real SQLite records | All old schema/rows unchanged | [Preservation evidence](assignment-2-part-2/rag-schema-preservation.json): all nine pre-existing tables unchanged; chat tables plus SQLite's sequence table added |

Repeat:

```sh
backend/.venv/bin/python -m pytest backend/tests -q
cd frontend
npm test
npm run lint
npm run build
```

Fixed model inputs: [chat-fixture.json](assignment-2-part-2/chat-fixture.json). Current persisted trace: [rag-conversation-evidence.json](assignment-2-part-2/rag-conversation-evidence.json). Conversation ID **5ee71404-a624-41ee-898b-85436a569854** in that exported isolated run has 38 messages across greeting, class lookup, follow-up, no-match and rejected write. It is a mock model run with real SQLite, not live OpenAI evidence. Exact IDs differ when rerun.

Browser screenshots: [class success](assignment-2-part-2/rag-class-success-mock.png), [follow-up](assignment-2-part-2/rag-followup-mock.png), [persisted messages](assignment-2-part-2/rag-history-mock.png), [no match](assignment-2-part-2/rag-no-match-mock.png), [saved rejection](assignment-2-part-2/rag-rejected-mock.png). Browser's corrected class/no-match/rejected conversation ID is 95423834-d4e2-4f19-858c-ce4b1a2f0659 in the isolated browser database; screenshots and JSON export intentionally come from distinct labeled verification runs.

Repeat the browser mocks in separate terminals:

```sh
backend/.venv/bin/python -m backend.tests.rag_fixture_server --database /private/tmp/expedia-rag-browser-demo.db
```

```sh
cd frontend
VITE_API_TARGET=http://127.0.0.1:8001 npm run dev -- --port 5180 --strictPort
```

Open port 5180, send Hi, the class example, the October 12 follow-up, a ZIP 00000 question and a Delete proposal. Restart the mock backend with the same `--database` path and refresh. The fixture server uses scripted model outputs and real isolated SQLite; it must never point at the project database or be described as live. Stop both fixture processes afterward. Production uses ports 8000/5173 and never falls back to mocks.

For SQLite inspection of any real conversation, use DB Explorer or a parameterized local query:

```sql
SELECT message_id, conversation_id, timestamp, role, stage, content, prompt_version
FROM chat_messages WHERE conversation_id=:conversation_id ORDER BY sequence;
```

## Remaining human/live evidence

Create a private OpenAI API key and ensure API credit. The agent cannot invent an account key or buy credit on the student's behalf. Add OPEN_AI, restart the backend, run preflight, then demonstrate a real greeting/follow-up and the full two-call hotel workflow in the normal application. Compare retrieved nights/total to SQLite and capture a live no-match/insufficient-data case. Retain mocks for rejected SQL/quota failures; do not exhaust service quotas.

The actual saved hotel is associated with ZIP 16802; do not expect a 16803 match unless an actual provider hotel is saved with that association. Do not fabricate a hotel to make a live demonstration match. The course rates currently cover Oct 10–14, 2026. Existing Nittany Lion Inn has the prior Oct 10 $5/10-room edit; its Oct 11 $100/20-room record is preserved.

Finalize recorded live demo, actual model disclosure, assessed commit and instructor-accessible links only after student manual review. No commit/push or graded submission was performed. Semantic intent and prose grounding still require live review; SQL safety does not prove that every generated sentence is correct.

Normal application missing-key evidence: [saved configuration error](assignment-2-part-2/rag-openai-unconfigured.png). The request was logged in the actual chat tables, but stopped before any remote generation call.


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
