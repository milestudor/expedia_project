# Student manual verification and report review

Status: PARTIALLY COMPLETED. Student confirmed reading the report and performing ZIP searches and the chatbot question sequence; other checks remain unconfirmed. Fill observed results yourself after performing each action. Agent-generated tests and screenshots remain separate supporting evidence. Do not copy expected results into observed results without checking.

Reviewer: _____l_  Date/time/timezone: ______  Branch/commit reviewed: ______

## Prepare

Open http://127.0.0.1:5173/. Search ZIP16802 and save Nittany Lion Inn. Inspect its simulated nightly records. If freshly saved, Oct10–14 default to $100 and 20 rooms; prior manual edits may change expectations. Keep this hotel saved through the chatbot checks. Use a different hotel for removal.

## Perform and record

| Action | Expected result | My actual observation | Evidence link / correction |
|---|---|---|---|
| Search16802; select hotel/list/map | ZIP/location correct; selections synchronize; compare API response in browser Network panel, not a fixed count | Student reports completing ZIP questions; exact ZIP/search observations and list/map/API comparison not yet supplied | Partial; supply details |
| Enter123 | Clear validation, no stuck loading | Not yet confirmed by student | Pending |
| Save another hotel twice | One saved record | Not yet confirmed by student | Pending |
| Refresh and restart backend | Saved hotel and conversation persist | Not yet confirmed by student | Pending |
| Remove the other hotel | It disappears locally; target Nittany Lion Inn remains saved | Not yet confirmed by student | Pending |
| Start new chat; ask one room ZIP16802 Oct10–12 under$250 | Both nightly records, checkout excluded; newly seeded rates total$200; minimum20 rooms | Student-supplied screenshot shows $100 on Oct10 and Oct11, $200 total, at least20 rooms, simulated label | [Student screenshot](student-success.png) |
| Expand workflow evidence | Proposed SELECT with hotel_id JOINs, checked SQL/parameters, retrieved records and answer agree | Not yet confirmed by student | Pending |
| Follow up: What about October12? | Same conversation, Oct12–13, newly seeded total$100/20 rooms | Student-supplied screenshot shows Oct12–13, $100 total,20 rooms, simulated label | [Student screenshot](student-followup.png) |
| Ask ZIP00000 Oct12–13 | Empty retrieved records; no fabricated hotel/price | Student reports performing series; no latest no-match screenshot supplied | Confirmation/details pending; agent evidence separate |
| Ask Nittany Lion Inn Oct14–16 | No confirmed full-stay availability or full total because Oct15 missing; an empty filtered lookup does not mean Oct14 has no record | Student screenshot shows availability/full total unconfirmed; answer describes an empty filtered lookup | [Student screenshot](student-insufficient-data.png); empty lookup does not prove both nights missing |
| Refresh chat; restart backend; refresh again | Conversation/trace remain; no repeated model calls from refresh | Not yet confirmed by student | Pending |
| Use Tab/Enter across controls | Keyboard access; loading disables repeated submit | Not yet confirmed by student | Pending |
| Open Sample stays and return | Original sample behavior/navigation works | Not yet confirmed by student | Pending |

To restart: stop the backend in its terminal with Ctrl+C, then from the project root run `backend/.venv/bin/python -m uvicorn backend.app.main:app --reload --port 8000`. If the agent started it in another terminal and you cannot stop it, ask for help instead of starting a duplicate server.

## Personally inspect the rejected-query check

From the project root, run `backend/.venv/bin/python -m pytest backend/tests/test_hotel_chat.py -q -k rejected_queries_cannot_modify_or_read_private_tables`. Open that test and review how a disallowed proposal is run against temporary SQLite and original bytes/rows are compared. Record your command, observed output and what assertion you inspected. This is a student-run automated check, not a manual live-model DELETE demonstration. Label it MOCK MODEL / TEMPORARY DATABASE. Do not try to modify your real hotel database.

## Review report before submission

Read report.md in this folder line by line. Check repository/assessed commit, startup instructions, research links, early mockup, video link, actual ZIP/date, verification observations, failures/corrections and AI disclosure. Historical $105 evidence used an earlier $5 edit; your current $200 result is not contradictory. Keep historical observations dated and separate.

Add a section headed Student manual review with your own completed table, screenshots and date. State which parts you checked personally and which evidence was produced by the agent or automated tests. Leave unperformed checks marked not tested. Record yourself demonstrating the running app, both model stages/SQL/records, no-match and labeled rejected-query evidence. Do not show .env, API keys or private account pages.

Open every final link while signed out or use instructor permissions to verify access. Replace pending fields only with verified facts. No commit/push or submission is authorized by this checklist.

Student report review: student stated “I’ve read report and it looks good” on October8. This confirmation predates the final video/report edits; review those edits again before submission. Remaining checklist rows are not certified as completed.
