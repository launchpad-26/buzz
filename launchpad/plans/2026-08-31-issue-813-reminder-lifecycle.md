# Issue #813: document capabilities/reminders/reminder-lifecycle.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/` does not exist yet on `origin/launchpad` (no
  `capabilities`-directory nodes merged at all) — confirmed via
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`.
- The target file `launchpad/docs/corpus/capabilities/reminders/reminder-lifecycle.md`
  does not exist anywhere in this worktree or on `origin/launchpad`.
- `launchpad/docs/corpus/templates/flow.md` (id `corpus-template-flow`, merged via
  PR #1556) is the merged template for flow-shaped nodes. It resolves the `type`
  ambiguity itself: no `node.schema.json` enum member is named `flow`; the closest
  fit is `type: architecture`, extending the precedent the merged C4
  architecture-triad templates already set. Flow instance nodes `references`
  architecture/interface/capability/event-kind nodes rather than being typed
  `capabilities` themselves.
- A real, merged flow *instance* node already exists at
  `launchpad/docs/corpus/architecture/flows/websocket-authentication.md`
  (`id: architecture-flows-websocket-authentication`, from issue #686, whose DoD
  wording is verbatim identical to #813's four flow-specific bullets: trigger/
  preconditions/termination, ordered interactions, auth/trust-boundary crossings,
  failure/abort/rollback + verification). It uses `type: architecture`, no Mermaid
  diagram, and these six body sections: intro paragraph, "Trigger, preconditions,
  and termination", "Ordered interactions and data/state movement",
  "Trust-boundary and authorization crossings", "Failure, abort, and rollback
  behavior", "Verification", "Scope and omissions". This is the closest real
  precedent for #813's shape and is followed directly rather than the more
  elaborate (and never-yet-instantiated) template skeleton.
- The reminder capability is real and implemented, not aspirational: NIP-ER
  (`docs/nips/NIP-ER.md`) is the wire spec; `desktop/src/features/reminders/lib/
  reminderService.ts` implements create/complete/snooze/cancel against
  `KIND_EVENT_REMINDER` (`crates/buzz-core/src/kind.rs:102`, `= 30300`);
  `crates/buzz-relay/src/handlers/ingest.rs:1956-2054` validates the public
  `not_before`/`d`/`expiration` tag envelope on write; `crates/buzz-relay/src/
  handlers/req.rs` enforces author-only reads (`AUTHOR_ONLY_KINDS`); and
  `crates/buzz-relay/src/main.rs:769-891` runs a background scheduler that polls
  `query_due_reminders` and fans due reminders out over Redis pub/sub. An
  `#[ignore]`d (live-relay) e2e suite exists at `crates/buzz-test-client/tests/
  e2e_event_reminder.rs`.
- `origin/launchpad`'s merged corpus already has `architecture-containers-relay`
  and `architecture-containers-desktop` (both `type: architecture`) — valid
  `references` targets for a flow node whose actors are exactly those two
  containers, unlike the earlier-revision precedent nodes which had no merged
  container nodes to point at yet.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/capabilities/reminders/reminder-lifecycle.md` with:
- Front matter: `id: capabilities-reminders-reminder-lifecycle`, `type:
  architecture` (per the flow template's own resolved precedent above — not
  `capabilities`, since this document narrates the step-by-step interaction, not
  the capability's own "what it does" statement, which is a separate, not-yet-
  drafted sibling node), `status: draft`, `origin: launchpad`, `audiences: [agent,
  developer, reviewer]`, one commit-citation FACT recording `git rev-parse HEAD`,
  and one FACT/INFERENCE per substantive body claim, each citing real `path:line`
  or `path:start-end` (never `#symbol=`/`#line=` fragments).
- `relationships: [{type: references, target: architecture-containers-relay},
  {type: references, target: architecture-containers-desktop}]`.
- Body mirroring `websocket-authentication.md`'s six sections: Flow intro;
  Trigger/preconditions/termination (create → pending, `not_before` due →
  fired/notified, snooze → pending w/ new `not_before`, complete/cancel →
  terminal, NIP-09 hard delete); Ordered interactions and data/state movement
  (client encrypt+publish → relay tag-envelope validation → NIP-33 replacement →
  scheduler poll → Redis fan-out → client watermark/toast); Trust-boundary and
  authorization crossings (NIP-42 author-only reads, relay-blind-to-content
  privacy boundary); Failure/abort/rollback (malformed `not_before`, duplicate/
  empty `d` tag, `expiration <= not_before`, cross-author read/subscribe denial)
  as a table linking representative verification; Verification (unit tests in
  `ingest.rs`/`reminderService.ts`, `#[ignore]`d e2e suite); Scope and omissions
  (excludes the capability-level "what reminders let a user do" node, the
  interface-level CLI/HTTP contract, and mobile's parallel Dart implementation,
  named as unverified-in-depth rather than silently absent).

**Done when:** the file exists, front matter parses as valid YAML, and every
`evidence[].evidence[]` path was opened during this session (no guessed line
numbers).

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo
root. Confirm exit 0 and that the only FAIL-severity findings reported are the
21 pre-existing ones tracked in issue #1951 (i.e. zero new FAIL entries
attributable to this node).

**Done when:** validator exits with the same FAIL count as an `origin/launchpad`
baseline run, plus this node passing cleanly (UNVERIFIED notices on the
commit-citation FACT are expected and fine).

## STEP 3 — Self-review against #813's DoD

Re-read the diff line by line against issue #813's checklist (one canonical
document; schema-valid front matter; one independently maintainable idea;
FACT/INFERENCE/TEAM_KNOWLEDGE not conflated; links neighboring nodes without
duplicating their content; checked against the recorded revision; validator
clean; the four flow-specific bullets). Re-open every cited source to confirm
it says what the statement claims — not just that the path resolves.

**Done when:** every DoD bullet has a concrete answer, not an assumption.

## STEP 4 — Earn the commit gate and commit

Run, as the sole command in its own tool call:
```
python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"
```
Confirm `OK`. Then, in a separate call, `git add` the new node file plus this
plan file and commit with `-s`.

**Done when:** the test suite reports `OK` and the commit is created with a
`Signed-off-by` trailer, no `--no-verify`.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 with no
  new FAIL entries.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.

## BUDGET

Single-session, no parallelism — one document, ~4 focused edit/verify passes.

## OPEN

- Whether `type: architecture` (this plan's choice, following the merged flow
  template's own resolved precedent) or `type: capabilities` (matching the
  target directory's name) is the better long-term fit is not settled by any
  authority stronger than that template's own INFERENCE (confidence 0.6). This
  plan follows the template and the one real merged instance rather than the
  directory name, and says so in the node's own body.
- Whether a sibling `capabilities-reminders` (the capability-level "what") node
  will ever be drafted in this directory is out of this task's control; this
  node names that gap rather than filling it.

## LEFT OUT

- No Mermaid `sequenceDiagram` block — the merged `websocket-authentication.md`
  precedent and #813's own DoD checklist both omit a diagram requirement; adding
  one anyway would be scope the DoD does not ask for.
- No relationships toward mobile's Dart reminder implementation, the CLI, or any
  interface-level node — none exist yet on `origin/launchpad` as valid targets.
- No edits to any other corpus file, generated index, or template.
