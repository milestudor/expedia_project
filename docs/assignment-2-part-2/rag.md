# Revised Part 2 SQL RAG — current implementation

The attached class RAG activity now provides the implementation requirements. The current provider is **OpenAI / gpt-5.6-luna**, using the custom backend variable `OPEN_AI`; the earlier provisional OpenRouter plan has been replaced. No live key is configured.

See [docs/rag-context.md](../rag-context.md) for the actual schema, both JOIN relationships, prompt startup loading, Responses API setup, read-only retrieval, persistent conversation/history endpoints, current expected-versus-observed checks, and remaining live evidence. The final test counts are **132 backend / 37 frontend**, with clean lint and passing production build.

The early [mockup](chatbot-mockup.svg) predates chatbot implementation. The final design adds persistent user/assistant messages, a saved-conversation selector and a saved step trace in addition to canonical nightly evidence. [Current fixed JSON](chat-fixture.json) uses parameterized hotel JOINs. [Current mock conversation export](rag-conversation-evidence.json) includes roles, stages, timestamps, prompt version, successful retrieval, no-match and failure evidence after backend restart.

Earlier `chat-fixture-evidence.json` and `chat-fixture-*.png` document the initial stateless, view-only mock checkpoint. They are historical mock evidence, not the current prompt/query contract or successful live model calls. Current browser images are the `rag-*-mock.png` files linked in rag-context.md.

No dependencies were added. Part 1 and local storage are preserved. [Schema/record preservation](rag-schema-preservation.json) verifies all pre-existing tables/rows unchanged. Live OpenAI success, recorded live demo, instructor-accessible final links and student manual review remain pending.


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
