Issue #885: document the event kind registry (Feature #616)

Stated size: issue #885 states no explicit Size line; task brief caps this at 5 steps because it is a small single-document task -> cap: 5 steps

ALREADY TRUE

- Worktree `__worktrees/task-885-events-registry` exists, branched from `origin/launchpad` at
  commit `650354eab8d41ab6ce1a71de079a6c6d95c69052` (confirmed via `git rev-parse HEAD`).
- Target file `launchpad/docs/corpus/events/registry.md` does NOT exist yet (confirmed via
  `test -f`) — this is a create, not an update.
- `crates/buzz-core/src/kind.rs` was read in full (886 lines). It defines every kind constant,
  `ALL_KINDS` (the complete registry array), `AUTHOR_ONLY_KINDS`, `P_GATED_KINDS`,
  `SHARED_GATED_KINDS`, `RESULT_GATED_KINDS`, and the range-classification helpers
  (`is_ephemeral`, `is_replaceable`, `is_parameterized_replaceable`).
- No `kind-*.md` corpus node exists anywhere under `launchpad/docs/corpus` at this revision
  (confirmed via `find`), and no sibling corpus node's `id` collides with `events-registry`
  (confirmed via `grep -rn "^id:"` across the corpus, excluding `schema/`).
- `node.schema.json`'s `type` enum contains `interfaces-events` — the dedicated value for the
  combined interface/event surface — and no `reference` value exists; `type` names corpus
  surface, not documentation form (confirmed by reading the schema directly, and corroborated
  by `templates/reference.md`'s and `templates/event-kind.md`'s own front matter, which both
  state this explicitly).
- `templates/reference.md` (Diátaxis Reference form: description + structured entries +
  optional commands + boundary + relationships + scope/omissions) and
  `templates/event-kind.md` (per-kind instance shape) were both read in full. Neither is a
  binding template yet — `AGENTS.md` states no per-type templates have landed — but both
  describe conventions this task should follow where they apply to a multi-kind lookup table
  rather than a single-kind instance node.
- The issue's own Definition of Done additionally requires: labeling generated vs. authored
  values, defining scope/omissions explicitly, and linking the authoritative source
  (`kind.rs`) — these are lookup-table-specific requirements this plan must satisfy alongside
  the generic corpus DoD bullets.
- `launchpad/project-intelligence/corpus/validate.py` is the deterministic corpus checker;
  21 pre-existing FAIL lines exist on `origin/launchpad` today, tracked as issue #1951, and
  are out of scope for this task — the bar is zero *additional* FAIL lines, not global exit 0.

STEP 1 [independent]

Draft `launchpad/docs/corpus/events/registry.md`: front matter (`id: events-registry`,
`type: interfaces-events`, `status: draft`, `origin: launchpad`, `audiences: [agent,
developer, reviewer]`, `evidence` ledger, no `relationships` — no `kind-*.md` node exists to
target). Body: a Reference-description paragraph, one lookup table (kind number, constant
name, one-line purpose, NIP/spec reference, delivery classification, corpus-node link only
where a `kind-*.md` id already resolves — none do today, so this column stays a note, not a
schema `relationships` entry), a note on which sets (`ALL_KINDS`, `AUTHOR_ONLY_KINDS`,
`P_GATED_KINDS`, `SHARED_GATED_KINDS`, `RESULT_GATED_KINDS`) are generated-vs-authored (the
constants and doc comments are hand-authored in `kind.rs`; the table below is a hand-derived
transcription of that source, not machine-generated — say so explicitly), a Boundary section,
and a Scope-and-omissions section naming what this registry does not cover (per-kind wire
contracts, access-control rationale beyond set membership, and anything `kind.rs` documents
that this table does not attempt to restate in full prose).

done when: the file exists, every row in the table cites a real constant name and integer
value present in `crates/buzz-core/src/kind.rs` at commit `650354eab8d41ab6ce1a71de079a6c6d95c69052`
(spot-checked by grepping the constant name in `kind.rs`), and every evidence entry's
`entry_class` is FACT with an `evidence` array pointing at `crates/buzz-core/src/kind.rs`
(or, where applicable, INFERENCE with `confidence` or TEAM_KNOWLEDGE with `provided_by`).

STEP 2 [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py`, capture the full error list,
and diff it against the 21 known pre-existing errors (tracked in #1951: the
architecture-containers-postgres, architecture-context-human-user,
architecture-flows-event-ingestion, architecture-flows-workflow-execution,
architecture-principles-community-is-security-boundary, and corpus-template-* nodes). Fix
anything attributable to the new node until the diff shows zero new FAIL lines.

done when: `validate.py`'s error output, diffed against the pre-existing 21, shows zero new
FAIL lines attributable to `launchpad/docs/corpus/events/registry.md`.

STEP 3 [needs 2]

<- RUNS HERE

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as the sole command in its own tool call, and confirm it prints `OK`. Then, in a
separate tool call, stage and commit `launchpad/docs/corpus/events/registry.md` and this plan
file with `git commit -s -m "docs(corpus): document event kind registry (#885)"`.

done when: the unittest run prints `OK`, and `git log -1 --format=%H` on the worktree branch
shows a new commit whose message matches the one above and whose diff contains exactly those
two files.

STEP 4 [needs 3]

Self-review the committed diff line by line against issue #885's Definition of Done
checklist: exactly one hand-authored canonical document; schema-valid front matter with
stable id/type/status/origin/audiences/evidence; one independently maintainable node;
FACT/INFERENCE/TEAM_KNOWLEDGE not conflated and each evidence entry's citation re-opened and
confirmed to actually support its statement; links to `kind.rs` present; checked against the
recorded commit; validate.py introduces zero new errors; structured for lookup, not
narrative; facts only, generated-vs-authored labeled; scope/omissions defined; authoritative
source linked.

done when: every DoD bullet has been checked against the actual committed file content (not
assumed), and any gap found is fixed with a follow-up commit before reporting done.

STEP 5 [needs 4]

Report back: issue number, worktree path, branch name, and `git rev-parse HEAD` — no PR, no
push, no merge.

done when: the final message contains exactly those four facts (or a `BLOCKED:` line naming
the specific blocker) and nothing else.

PARALLEL

None of these steps can run in parallel with each other — this is a single linear
single-document task (draft, validate, commit-gate, self-review, report), each depending on
the previous step's output existing on disk or in git history.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must show zero new FAIL lines
  beyond the 21 pre-existing ones (STEP 2).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  must print `OK`, run alone in its own tool call, before the commit (STEP 3).
- If the commit is rejected for a missing gate stamp, that is reported as a blocker — no
  `--no-verify`, no self-created stamp file (per task brief).

BUDGET

Single document, ~5 tool-call-heavy steps. No code changes, no tests beyond the existing
corpus test suite, no new dependencies. Expected total: under an hour of agent time.

OPEN

- Whether a `kind-*.md` per-kind instance node should eventually declare a `references` or
  `part-of` edge back to `events-registry` is left to whichever future task authors the first
  such node — not decided here, since none exist yet.
- Whether the registry table should be regenerated mechanically from `kind.rs` in the future
  (a `generated/` projection) is explicitly out of scope per `AGENTS.md`: no generator exists
  yet (#1316), so this task adds hand-authored Markdown only.

LEFT OUT

- Any second corpus document (e.g., a per-kind `kind-*.md` instance) — issue #885 and the
  task brief are explicit that this task produces exactly one canonical document.
- Reconciling `events-registry` against the `interfaces-events` boundary questions raised in
  `templates/event-kind.md` (event-kind vs. interface node boundary, #1342) — that boundary
  concerns single-kind instance nodes, not a multi-kind lookup table, and is out of scope for
  a registry-shaped reference node.
- Any change to `crates/buzz-core/src/kind.rs` itself or any other runtime code — this is a
  documentation-only task.
