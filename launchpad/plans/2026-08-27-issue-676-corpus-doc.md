# Plan: issue #676 — corpus doc `architecture/flows/event-ingestion.md`

ALREADY TRUE: `node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are merged on
`origin/launchpad` (confirmed at HEAD `a44cf52fc740ebebbdd671427480d14f0bce0115`), and
`launchpad/docs/corpus/architecture/flows/event-ingestion.md` does not exist yet
(confirmed via `test -f`, and no `architecture/` subtree exists under
`launchpad/docs/corpus/` at all yet).

STEP 1: Gather evidence — read the relay's event-ingestion pipeline end to end:
`crates/buzz-relay/src/handlers/event.rs` (`handle_event`, fan-out, dispatch),
`crates/buzz-relay/src/handlers/ingest.rs` (`ingest_event`/`ingest_event_inner`, the
shared WS/HTTP seam), `crates/buzz-core/src/verification.rs` (signature/id check),
`crates/buzz-db/src/event.rs` (`insert_event_with_thread_metadata`, dedupe, thread
counters), `crates/buzz-db/src/deletion.rs` (`is_serving_active` write fence), and
`crates/buzz-relay/src/api/bridge.rs` (`submit_event`/`submit_event_authed`, the HTTP
transport onto the same seam). RUNS HERE.

STEP 2: Write front matter (id `architecture-flows-event-ingestion`, type
`architecture`, status `draft`, origin `launchpad`, audiences `developer`+`agent`) and
the body against `node.schema.json`, satisfying the issue's own DoD checklist plus the
category-specific flows tail (trigger/preconditions/termination, ordered
interactions/data movement, auth/trust-boundary crossings, failure/abort/rollback +
verification links). RUNS HERE.

STEP 3: Validate — `python3 launchpad/project-intelligence/corpus/validate.py` must
exit 0 against the full tree including the new file. Fix and re-run until clean.

STEP 4: Commit — earn the verification stamp via
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole prior command, then commit the plan + document in a separate call.

PARALLEL: none — single document, single file, no fan-out.

GATES: `validate.py` only. `review-adjudicate` and the cross-model final-review pass
are explicitly deferred to the batch owner's morning review — not run in this task.

BUDGET: single-session, read-then-write; no multi-day/multi-agent budget needed.

OPEN: the relay's event-ingestion pipeline (`ingest_event_inner`) is ~1,900 lines with
dozens of per-kind envelope validators (persona, project, engram, reminder, diff,
team-catalog, push-lease, etc.). The issue's DoD asks for "ordered interactions and
data/state movement" for *the* flow, not an enumeration of every one of those ~30
per-kind branches — the document covers the common-path pipeline (auth → verify →
scope/moderation gates → channel/membership resolution → kind-specific dispatch →
storage → fan-out/audit/workflow) and names the per-kind validators as a category this
node does not enumerate exhaustively, rather than silently picking a subset to
describe as if it were the whole set. This is stated as scope in the document itself,
not resolved by guessing which subset the issue author wanted.

LEFT OUT: no relationships to other corpus nodes (only `AGENTS.md`, `README.md`, and
`standards/confidence.md`/`standards/decision-references.md` are merged on
`origin/launchpad` today — none is a suitable relationship target for an
architecture/flows node, so `relationships` is omitted per the schema's optional-field
rule). No changes to runtime behavior. No second canonical document.
