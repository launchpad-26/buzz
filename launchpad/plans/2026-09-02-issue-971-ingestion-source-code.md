# Issue #971 — ingestion/source-code.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `AGENTS.md`,
`standards/code-references.md` (id `corpus-standard-code-references`) and
`standards/test-references.md` (id `corpus-standard-test-references`) are merged on
`origin/launchpad`. `launchpad/docs/corpus/ingestion/source-code.md` does not exist yet.
`code-references.md`'s own words: it governs "which forms are permitted, which are
forbidden, how they are pinned and positioned, and what a passing validation run does and
does not establish about" a code citation — pure citation *mechanics*. It explicitly does
NOT decide "whether a citation supports its claim" (structural checking only, stated in its
own Enforcement section) and its Scope-and-omissions table reserves nothing for claim-shape
or source-specific epistemic risk. `test-references.md` demonstrates the non-duplicative
pattern this task follows for a sibling source type: it explicitly delegates generic
path/GitHub-link mechanics to #1308 (code-references) and instead adds *"which claim [a
test] citation actually supports"* (existence vs. run-result vs. current-behavior) plus
*source-type-specific* epistemic traps (`#[ignore]`-gated tests, CI retry masking). Its own
Scope-and-omissions table names, verbatim, **"Citing the production source code a test
exercises, as evidence of that code's own behavior | #1308"** — but #1308 shipped as
`code-references.md` without that content (verified by reading it in full: no claim-shape
or conditional-compilation discussion anywhere in it). That is this task's real,
non-duplicative gap: the source-code analogue of test-references' claim-shape section,
covering what a source-code citation does and does not establish about the *system's
current behavior* specifically — existence-vs-behavior, and this repository's own concrete
cases of conditional compilation (`desktop/src-tauri/build.rs` sets `cargo:rustc-cfg` and
`cargo:rustc-env` conditionally from build-time env vars), a proc-macro crate whose expanded
behavior isn't visible at the call site (`buzz-datastore-tracing`, `proc-macro = true`), and
`#[cfg(test)]`-gated code (256 occurrences) that never ships in the production binary.

STEP 1  Confirm the gap and gather evidence. Already largely done in this session: read
`code-references.md`, `test-references.md`, `AGENTS.md`, and `templates/policy.md` in
full; ran `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` (no
`ingestion/` nodes merged yet, so no relationships target exists for this node). Confirm
the three concrete repository examples still hold at `HEAD`: `desktop/src-tauri/build.rs`
(conditional `cargo:rustc-cfg=buzz_updater_enabled` and `cargo:rustc-env=...` lines),
`crates/buzz-datastore-tracing/Cargo.toml` (`proc-macro = true`), and a fresh count of
`#[cfg(test)]` across `crates/`. Record `git rev-parse HEAD` for provenance. ← RUNS HERE

STEP 2  [needs 1] Write front matter: `id: corpus-ingestion-source-code`, `type: ingestion`
(per node.schema.json — the corpus surface this node documents), `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, reviewer]`, no `relationships` (no
`ingestion/` sibling or other legitimate target is merged on `origin/launchpad` at the
recorded revision — checked, not assumed). One evidence entry per claim: the provenance
commit citation; the code-references.md/test-references.md scope quotes (FACT, citing
those files); the three repository examples above (FACT, citing the actual files/counts);
and the reasoned conclusion that this constitutes real non-duplicative scope (INFERENCE
with confidence).

STEP 3  [needs 2] Write the body using `templates/policy.md`'s six required sections
(Scope and authority; MUST; SHOULD; Enforcement; Exceptions and escalation; Scope and
omissions), since issue #971's own DoD tail ("states scope and authority," "separates MUST
from SHOULD," "enforcement/exceptions," "links decisions instead of duplicating") is the
policy-template checklist verbatim — matching `code-references.md` and
`test-references.md`'s own shape. Content: which claim a source-code citation can support
(exists vs. currently-runs-this-way), and this repository's own conditional-compilation,
macro-expansion and test-only-code traps that make "the file says X" weaker evidence of
"the system does X" than it looks. Explicitly defer citation format/pinning mechanics to
`code-references.md` and defer evidence classification/graph-edge/tool-result forms to
whatever standard eventually owns them, exactly as `test-references.md` defers those same
two things. State plainly, in Scope and omissions, that citing tests specifically remains
`test-references.md`'s territory, not this node's.

STEP 4  [needs 3] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and
re-run until exit 0.

STEP 5  [needs 4] Run the corpus unittest suite
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"`) as the sole prior command to earn the verification stamp, then commit the
plan + document in a separate call. Dispatch an independent `review-code` pass on the diff
and fix real findings before stopping.

PARALLEL: none — single file, single task.

GATES: `validate.py` must exit 0. `review-adjudicate` and the cross-model final review pass
are deferred to the batch owner's morning review — not run here.

BUDGET: small — one document, no code changes; evidence gathering scoped to the ~4 files
already inspected above plus a `grep` count.

OPEN: Whether this node should declare `references` toward
`corpus-standard-code-references` and `corpus-standard-test-references` once those ids are
confirmed present on `origin/launchpad` (they are, per `git ls-tree` run in this session) —
resolved in favor of declaring both, since the body explicitly builds on and defers to
their stated scope, mirroring `test-references.md`'s own `references: corpus-agents` edge.

LEFT OUT: No claim about generated/vendored *corpus* artifacts (owned by #1316, a different
subject — corpus-generated files, not product source code). No re-litigation of citation
pinning/format rules (owned by `code-references.md`). No content about citing tests
specifically (owned by `test-references.md`). No relationships to other unmerged
`ingestion/*` sibling tasks in this same batch.
