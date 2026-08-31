# Plan: issue #1136 — document layers/observability/datastore-tracing.md

Issue #1136 <- RUNS HERE

Stated size: no Size label on the issue itself; the batch dispatch brief caps every #611 child document task at 5 steps -> cap: 5 steps

ALREADY TRUE

- `crates/buzz-datastore-tracing` exists: a proc-macro-only crate
  (`crates/buzz-datastore-tracing/Cargo.toml`) describing itself as
  "Privacy-preserving datastore tracing policy macros for Buzz", exposing one
  public attribute macro, `#[datastore_span]`, from `src/lib.rs`.
- The macro is used at 258 call sites across `buzz-db`, `buzz-audit`,
  `buzz-search`, and one handler in `buzz-relay`
  (`crates/buzz-relay/src/handlers/command_executor.rs`); every call site sets
  `system = "postgresql"` and the macro rejects any other value at compile
  time.
- `crates/buzz-relay/src/telemetry.rs`'s `otel_env_filter` and
  `crates/buzz-relay/src/main.rs`'s `log_env_filter` wire the `buzz_datastore`
  tracing target into two independently configured filters: stdout/JSON logs
  default to `buzz_relay=info` (datastore spans excluded), OTel export
  defaults to `buzz_relay=info,buzz_datastore=info` (datastore spans
  included) — confirmed by `crates/buzz-relay/src/main.rs`'s
  `env_filter_tests` module and `crates/buzz-relay/src/telemetry.rs`'s own
  test `http_and_datastore_spans_are_exported_in_the_same_trace`.
- `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum is
  `architecture, layers, capabilities, platforms, implementation,
  interfaces-events, verification, operations, development, release,
  governance, agent, ingestion` — no separate "template" or "policy" value;
  `layers` is the correct member for this node (mirrors the precedent set by
  the parallel, unmerged sibling `layers/compute/*.md` docs in PR #1903, e.g.
  `layers-compute-liveness`, `type: layers`).
- `launchpad/docs/corpus/layers/observability/datastore-tracing.md` does not
  exist yet (`test -f` confirmed) — full build from scratch, no update path.
- `origin/launchpad`'s `launchpad/docs/corpus` tree carries **no `layers/`
  directory at all** (`git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus` — confirmed against the fetched remote ref). No
  sibling `layers/observability/*.md` or `layers/compute/*.md` node is a
  legal `relationships.target` yet; only pre-existing `architecture/*`
  nodes are.
- `launchpad/docs/corpus/architecture/containers/postgres.md` exists on
  `origin/launchpad` (`id: architecture-containers-postgres`) and describes
  `buzz-db` as the crate owning Postgres access generally — a legal, useful
  relationship target for this node (`references`, since this node zooms
  into one cross-cutting instrumentation concern of that container, not a
  containment/part-of relationship).
- `launchpad/docs/corpus/templates/datastore.md` (merged, `type: governance`)
  already names the `buzz-datastore-tracing` instrumentation-coverage gap
  (Postgres only, enforced at compile time) as a fact and explicitly defers
  the full access-pattern/schema shape of Postgres itself to a future
  `architecture`-type Postgres *instance* document — this node does not
  restate that template's material, only cites the one fact it already
  established about this crate.
- Current HEAD / repository revision for provenance: `ed133f4c5dbd546a67d963f11ffa630a4513b228`.

STEP 1 — Draft the node body and front matter [independent]

Write `launchpad/docs/corpus/layers/observability/datastore-tracing.md` with:
- Front matter: `id: layers-observability-datastore-tracing`, `type: layers`,
  `status: draft`, `origin: launchpad`, `audiences: [agent, developer,
  operator, reviewer]`, one `relationships` entry (`type: references`,
  `target: architecture-containers-postgres`), and an `evidence` ledger
  citing only sources actually opened this session: the crate's
  `Cargo.toml`/`src/lib.rs`/`tests/runtime.rs`, the 258-call-site scan, the
  `buzz-audit`/`command_executor.rs` non-`buzz-db` call sites, the two
  `EnvFilter` functions and their tests in `buzz-relay`, and the commit
  citation for `ed133f4c5dbd546a67d963f11ffa630a4513b228`.
- Body sections: one-sentence definition; boundary/non-goals (not general
  OpenTelemetry pipeline setup — #1141; not general application tracing
  spans elsewhere in the codebase — #1145; not the metrics pipeline overall —
  #1140; not Postgres's own schema/access-pattern shape — the future
  `architecture`-type Postgres instance doc); what the macro actually
  instruments (span fields, the privacy-preserving redaction policy, the
  paired duration histogram, the sampled slow-operation log); the dual-filter
  integration point (log vs. OTel defaults); links to
  `architecture-containers-postgres` and the sibling issues named above;
  scope-and-omissions naming what's expected-but-unverified (e.g., whether
  #1140/#1141/#1145 land with matching boundary language, not yet checked
  since those PRs don't exist yet either).

done when: the file exists, every DoD checklist bullet in issue #1136's body
is addressed, and no claim in it is uncited.

STEP 2 — Validate against the schema and the merge base [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root and confirm the run's own output shows zero FAIL-class errors
attributable to the new node (pre-existing UNVERIFIED noise and up to ~21
pre-existing FAIL-class errors elsewhere are known and out of scope). Fix
any schema or citation-shape problem the validator names in the new node
specifically.

done when: `validate.py`'s output contains no error line whose file path is
`layers/observability/datastore-tracing.md`.

STEP 3 — Run the corpus test suite [needs 2]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in one tool call.

done when: the command's own output ends with `OK`.

STEP 4 — Commit [needs 3]

In a separate tool call from STEP 3 (never combine verify+commit): `git add`
the new document and this plan file, then `git commit -s -m "docs(corpus):
document datastore tracing (#1136)"`. No `--no-verify`.

done when: `git log -1` shows the new commit and `git show --stat HEAD`
lists exactly the corpus doc plus this plan file.

STEP 5 — Self-review against the DoD [needs 4]

Re-read the committed document line by line against every bullet in issue
#1136's Definition of done, and confirm `git show --stat HEAD` names no
second hand-authored canonical document.

done when: every DoD bullet is checked off against the actual committed
text, not assumed.

PARALLEL

None of these steps are parallel with each other in practice (each STEP here
depends on the previous), but this task itself runs fully independently of
the 8 sibling observability-document tasks (#1135, #1137, #1140–#1145) being
authored concurrently by other agents in the same batch — no shared state,
no ordering dependency, because none of those sibling nodes exist yet as
`relationships.target`s this node could point to.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must show zero
  new FAILs (STEP 2).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK`, run alone in its own tool call, never combined
  with the commit (STEP 3/4).
- No `git push`, no `gh pr create` — this document ships as part of one
  batched PR for all of #611's children, assembled later by the batch owner.

BUDGET

One file created (~150-250 lines of Markdown, in line with the sibling
`layers/compute/*.md` nodes' 200-280 line size), one plan file, one commit.
No code changes — this is a documentation-only task.

OPEN

- Whether `#1140` (metrics), `#1141` (opentelemetry), or `#1145` (tracing)
  land with boundary language that actually matches what this node assumes
  about them — none of their PRs exist yet at authoring time, so the
  boundary stated here is this node's own placement, to be revisited once
  they merge (the same caveat PR #1903's `layers-compute-liveness` node
  records for its own undrafted siblings).
- Whether a future `architecture`-type Postgres *instance* document (built
  from the merged `templates/datastore.md` template) will want a `part-of`
  or `depends-on` edge back to this node once it exists — not this node's
  call to make unilaterally.

LEFT OUT

- No relationship to any `layers/*` sibling node (compute or observability) —
  none exist on `origin/launchpad` at this revision; declaring one would
  validate locally but hard-fail in CI once merged, per
  `launchpad/docs/corpus/AGENTS.md` step 9's explicit warning.
- No restatement of `templates/datastore.md`'s required datastore-document
  sections (schema inventory, migration mechanism, operational
  characteristics) — this node's subject is the tracing/observability
  instrumentation layer, not Postgres's own internal shape; that boundary is
  stated once and linked, not duplicated.
- No attempt to instrument or extend `buzz-datastore-tracing` to cover Redis
  or the object store — that is a code-level design decision for a future
  issue, already named as a live, enforced restriction in `templates/datastore.md`, not something this documentation task decides.
