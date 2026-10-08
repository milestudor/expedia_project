# Current Part 2 / RAG-context demonstration

Live OpenAI verification complete; final recording pending. Label fixtures as mocks throughout.

1. Show configured model gpt-5.6-luna and safe preflight, without opening .env or exposing headers. Check account API credit/limits privately. Normal app uses 5173/8000; fixtures use 5180/8001.
2. Demonstrate saved provider hotels and local-first lookup, duplicates, removal and persistence using existing storage checks. Show simulated nightly rates/rooms. Preserve original sample tables and provider results.
3. Send Hi and then a hotel question in one saved conversation. Show distinct user/assistant roles. Use actual saved ZIP 16802 for live success; the class's 16803 question may honestly have no saved matches unless an actual provider hotel was saved there.
4. Expand workflow evidence: question, proposed hotel JOINs, checked bounded SQL, bound ZIP/dates/rooms, retrieved nightly records, final answer. For a single Oct 11 night, checkout Oct 12 is excluded. For Oct 10–12, compare the sum of both requested nights; do not count checkout. Read the actual records before claiming totals.
5. Ask “What about October 12?” Show the same conversation ID, prior context, changed retrieval dates and grounded new answer.
6. Ask a real no-match or insufficient-data question. Missing nights must not become available or a complete total. Show the second model request's records and answer.
7. Refresh the page, restart the backend and reload. Show saved messages and trace. In DB Explorer, filter chat_messages by conversation_id and follow sequence/timestamps from user through proposal, executed query, retrieval, answer/error and prompt version.
8. Separately run the fixture server/temporary tests. Show a DELETE proposal rejected and saved as an error with no fabricated answer; confirm hotel tables unchanged. Quota/provider failures remain mocks, not exhausted-service demos.
9. Record a sanitized live video, finalize expected/observed checks and actual model disclosure, then request final commit/push only after manual review. No publish/submission is authorized by this script.
