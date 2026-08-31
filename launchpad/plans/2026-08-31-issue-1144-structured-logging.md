Issue #1144: task: document layers/observability/structured-logging.md
Stated size: not stated in issue body -> cap: 5 steps

ALREADY TRUE
- `launchpad/docs/corpus/layers/observability/structured-logging.md` does not exist
  in this worktree or on `origin/launchpad` (`git ls-tree -r --name-only
  origin/launchpad -- launchpad/docs/corpus` has no `layers/` directory at all yet).
- Worktree base commit `ed133f4c5dbd546a67d963f11ffa630a4513b228` is identical to
  `origin/launchpad` HEAD (freshly fetched) — this is the provenance revision.
- Premise correction: the task brief states sibling docs #1138
  (observability-liveness) and #1139 (logging) are "ALREADY MERGED." This is false
  as of this revision: `gh issue view 1139` returns `state: OPEN`, no PR exists for
  it (`gh pr list --search "1139"` -> empty), and no `layers/` directory exists
  anywhere in the corpus tree on `origin/launchpad`. Proceeding on verified repo
  state, not the stale brief.
- `node.schema.json`'s `type` enum includes `layers` (confirmed by direct read); no
  sibling `layers/observability/*.md` node exists yet to mirror front-matter shape
  from, so front matter is written directly against `node.schema.json` and
  `launchpad/docs/corpus/AGENTS.md`'s "Creating a node" steps instead.
- The relay (`crates/buzz-relay`) and push gateway (`crates/buzz-push-gateway`)
  install `tracing_subscriber::fmt().json()`; `buzz-agent`, `buzz-acp`,
  `buzz-dev-mcp`, and `buzz-test-client` install plain-text (non-JSON) formatters
  instead — verified by reading each crate's subscriber-init call site.
- Real `#[tracing::instrument(fields(...))]` usage with deferred
  `Span::current().record(...)` exists in `crates/buzz-relay/src/handlers/auth.rs`
  and `crates/buzz-relay/src/handlers/event.rs`; a proc-macro
  (`crates/buzz-datastore-tracing/src/lib.rs`) generates a similar
  `#[::tracing::instrument(fields(..., otel.status_code = ::tracing::field::Empty))]`
  attribute for datastore spans. No standalone `#[instrument]` usage without the
  `tracing::` prefix exists (grepped for `#\[instrument` first, got a false negative
  from a doc comment, then confirmed real usages with `instrument(`).
- `crates/buzz-relay/src/telemetry.rs` (`TraceContextJson`) is the concrete JSON
  shape mechanism: it wraps the stock `tracing_subscriber` JSON formatter, injects
  `trace_id`/`span_id` string fields into the emitted JSON object only when a valid
  OTel span context exists, and has a documented, tested fallback for events whose
  fields already collide with those two names (re-parses the line as JSON and
  overwrites, `crates/buzz-relay/src/telemetry.rs:150-165`, tested at
  `crates/buzz-relay/src/telemetry.rs:307-472`).
- `launchpad/docs/Observability/current-state/relay.md` is a pre-existing, older
  (non-corpus-schema) research document already covering the JSON log surface,
  `RUST_LOG`, and field classification at a broader level, pinned to an older
  revision (`678008ea...`). It is prior art, not a corpus node and not something to
  duplicate structurally.
- `CONTRIBUTING.md`'s "Logging and Tracing" section (line ~291) states the
  project-wide style preference (structured fields over string interpolation) but
  gives no field-naming convention or JSON-shape detail — confirmed by reading it.

STEP 1 [independent] <- RUNS HERE
Draft the corpus node at
`launchpad/docs/corpus/layers/observability/structured-logging.md` with schema-valid
front matter (`id: layers-observability-structured-logging`, `type: layers`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, operator]`, a
full `evidence` ledger classifying every claim FACT/INFERENCE/TEAM_KNOWLEDGE with
real citations, and NO `relationships` entry, since the natural target
`layers-observability-logging` (#1139) does not exist on `origin/launchpad` and
adding it would be a hard validation error). Body: one-sentence definition,
scope/non-goals naming what this node does not cover, the
`#[instrument(fields(...))] + Span::current().record()` deferred-field pattern, the
sigil conventions observed at call sites (bare/`%`/`?`), the JSON-shape and
trace-correlation mechanism in `telemetry.rs`, and the JSON-vs-plain-text split
across crates. Datastore-specific field policy is named by path only (owned by
#1136), not expanded.
done when: the file exists, front matter parses and matches the schema fields
above, and every substantive statement in the body has a matching `evidence`
entry citing a path/symbol actually opened during research.

STEP 2 [needs 1]
Run `python3 launchpad/project-intelligence/corpus/validate.py` and confirm it ends
`PASS` with zero FAIL-class errors attributable to the new node (pre-existing
UNVERIFIED noise and unrelated pre-existing FAILs elsewhere are not in scope). Then,
as the sole command in one separate tool call, run
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
and confirm it prints `OK`.
done when: both commands have been run and both produced the expected terminal
output (`PASS` / `OK`) in this session's tool output.

STEP 3 [needs 2]
`git add` the new document and this plan file, then `git commit -s` with message
`docs(corpus): document structured logging (#1144)`, in a separate tool call from
step 2's verification commands — never combined, never `--no-verify`.
done when: `git log -1` shows the new commit and `git show --stat HEAD` lists only
the corpus document and this plan file.

PARALLEL
None declared — single-file authoring task, steps are strictly sequential
(draft -> validate -> commit).

GATES
- `python3 launchpad/project-intelligence/corpus/validate.py` must print `PASS`
  with zero FAIL-class errors from the new node.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  must print `OK`.
- No `git push`, no `gh pr create` — the batch owner cherry-picks this commit onto
  the shared feature branch later.

BUDGET
One corpus document (~150-250 lines including front matter), one plan file. No
runtime code changes. Single commit.

OPEN
- The brief's claim that #1138/#1139 are "already merged" is contradicted by
  direct verification (`gh issue view`, `gh pr list`, and `origin/launchpad`'s
  tree). Proceeding without a `relationships` edge and without a sibling
  front-matter precedent to mirror; flagged in the final report. If #1139 merges
  before this branch's cherry-pick lands, the batch owner should consider adding
  the `references` edge at that point — not this task's job to guess at unmerged
  content.
- #1136 (datastore-tracing) is also OPEN, not merged — the datastore-specific
  field-policy detail in `buzz-datastore-tracing` is named here only by path,
  deliberately not expanded, to avoid preempting or duplicating that sibling's
  scope.
- Whether `#[instrument]` proliferates further as the relay grows was not
  surveyed exhaustively beyond the grep in ALREADY TRUE; the body states the
  observed call sites, not completeness.

LEFT OUT
- Any edit to `launchpad/docs/corpus/layers/observability/logging.md` (#1139) —
  does not exist yet; out of scope regardless.
- Any relationship edge to unmerged sibling nodes.
- Datastore-specific tracing field policy (owned by #1136).
- Any change to `crates/buzz-relay/src/telemetry.rs` or other runtime code.
- Broad recount of the entire observability landscape already covered by
  `launchpad/docs/Observability/current-state/relay.md`.
