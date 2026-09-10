# Issue #955 — ingestion/concept-extraction.md

ALREADY TRUE: `launchpad/docs/corpus/AGENTS.md`, `templates/procedure.md` (id `corpus-template-procedure`), `standards/atomicity.md` (id `corpus-standard-atomicity`), and `agents/invariants.md` (id `agents-invariants`) are merged on `origin/launchpad`. No `ingestion/` directory exists yet. Sibling `agents/concept-resolution.md` (#642) exists only as a local, unmerged commit in another worktree and is NOT a valid relationship target. `node.schema.json`'s `type` enum includes `ingestion` for exactly this corpus surface.

STEP 1  Gather evidence for one real, verifiable worked example of "noticing a candidate concept before it is checked against the corpus" (the step before #642's dedup check), across the three signal shapes named in the task brief. ← RUNS HERE
  - Code-pattern signal: confirm via `grep` that the `reply_count`/`descendant_count` counter-update SQL idiom is independently duplicated in `crates/buzz-db/src/store/thread.rs`, `crates/buzz-db/src/store/event.rs`, and `crates/buzz-db/src/store/relay_admin_actions.rs` — already partially captured as a "Common Gotcha" in `/home/serina/Launchpad/buzz/CLAUDE.md` ("Thread counters"), which is itself evidence that this repetition was previously recognized as worth documenting.
  - Decision-record signal: read `launchpad/decisions/ADR-0043-prefer-fork-owned-overrides.md`'s Context section, which explicitly generalizes ADR-0005's "a copy trades a conflict Git shows you for a divergence nothing does" reasoning — a rationale recurring across two decision records.
  - GitHub-issue signal: read upstream `block/buzz#3293` and `block/buzz#3799` — two independently filed, still-open issues (mobile and desktop respectively) both describing thread-summary staleness/render failures under specific reply orderings. Confirm they are a *related but distinct* concept from the backend counter idiom (client-side display vs. server-side counter maintenance), not the same one — do not conflate them.

STEP 2  [needs 1] Write the front matter: `id: ingestion-concept-extraction`, `type: ingestion`, `status: draft`, `origin: launchpad`, `audiences: [agent, reviewer]`, one evidence entry per substantive claim (commit citation for the recorded revision; FACT entries for grep/read results; TEAM_KNOWLEDGE for issue #955/#620/#642's own DoD text and for `block/buzz#3293`/`#3799`, since those are external attributed sources with no openable file). `relationships`: `references: corpus-agents`, `implements: corpus-template-procedure` — both merged and resolvable; no edge to `agents-concept-resolution` (unmerged) or to `agents-invariants` (no genuine dependency).

STEP 3  [needs 2] Write the body from `templates/procedure.md`'s required sections (Overview, Before you start, one numbered task sequence with the three-signal fork per Diátaxis's allowed non-linear structure, See also, Boundary, Relationships, Scope and omissions). State the boundary against `agents/concept-resolution.md` (#642) precisely: extraction notices a candidate exists; resolution (the next, separate step) checks it against the existing corpus for duplication. Name the atomicity question (one concept or several) as explicitly out of scope, owned by `standards/atomicity.md`.

STEP 4  [needs 3] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until exit 0.

STEP 5  [needs 4] Run the corpus unittest suite as the sole prior command to earn the verification stamp, then commit the plan + document in a separate call. Do not push, do not open a PR (per batch-run instructions — that is the batch owner's step).

PARALLEL: none — single file, single task, no code changes.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report OK before commit. `review-code` (or self-review if unreachable) before calling the task done.

BUDGET: small — one document, no code changes; evidence gathering scoped to ~3 Rust source files, one ADR, two upstream GitHub issues, and the already-merged corpus scaffolding (AGENTS.md, procedure template, atomicity standard).

OPEN: Whether `block/buzz#3293`/`#3799` really are best read as *evidence of a related-but-distinct concept* rather than *noise* is a judgment call this node states explicitly rather than resolving silently — flagged in the body's evidence, not hidden.

LEFT OUT: No claim about implementing a concept-extraction *tool* or pipeline (explicitly out of scope per parent Feature #620). No relationship to `agents/concept-resolution.md` (#642) or any other Feature #620 sibling — none are merged on `origin/launchpad` at plan time. No resolution of whether the thread-summary GitHub issues and the backend counter idiom should eventually become one corpus node or two — that is `standards/atomicity.md`'s question, not this one's.
