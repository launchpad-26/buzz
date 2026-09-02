# Complete the corpus evidence-verifier registry

Stated size: Deep Plan  →  cap: 15 steps

Continues committed work on `fix/validate-fail-closed-citations` (worktree
`/tmp/buzz-validate-rollout`). Builds on it; does not redo it.

ALREADY TRUE  (verified against git and a live validator run, not notes)

- Branch `fix/validate-fail-closed-citations` carries 5 commits ahead of
  `origin/launchpad`: `4c774012d`, `23dbb4a27`, `2b0d1bb70`, `32c8d006f`,
  `3f5c45559`. Working tree clean. 20 files, +728/-231.
- `evidence.py` owns `EvidenceKind` (9 kinds), `ParsedCitation`,
  `parse_citation()`, `VerificationResult(status, detail)`, and
  `verify_citation()` covering local file / line / range / commit.
- `validate.py:785-808` routes local-file and commit citations through
  `_EVIDENCE_PARSER.verify_citation()`. That boundary is real, not decorative.
- URL verification is **not** in the registry. `_url_resolves` and
  `_url_request_target` (`validate.py:624-654`) and `_classify_url`
  (`validate.py:707-741`) still live in `validate.py`;
  `evidence.py:219-220` returns the placeholder `"requires the URL verifier"`.
- `.github/workflows/launchpad-corpus-validate.yml` runs one validation step:
  `validate.py --check-links`. No structural/link stage split exists.
- Full suite: `Ran 187 tests ... OK`.
- Offline validator on the real corpus: `{'UNVERIFIED': 405, 'FAIL': 1}` —
  211 graph-edge/tool-result, 194 URL-needs-`--check-links`.
- **Measured citation inventory across the real corpus** (via
  `evidence.parse_citation`): `local_file` 3136, `local_file_range` 1405,
  `local_file_line` 412, `commit` 211, `tool_result` 210, `external_url` 144,
  `github_url` 49, **`graph_edge` 0**.
- **Tool-result families, measured**: `git_ls_tree` 60, `grep_recursive` 20,
  `git_show` 19, `grep_case_insensitive` 15, `grep_repo` 10,
  `grep_recursive_case_insensitive` 7, `shell` 6, `webfetch` 5, `grep` 5,
  `git_diff_name_only` 4, `git.ls_tree` 4, then a long tail of `gh_*`,
  `github_api`, `git_log*`, `curl_fetch` at 1-3 each.
- `graph.py` builds `ProjectGraph.from_symbols()` at runtime. There is no
  persisted graph artifact for a validator to read.
- Dead after the prior session's wiring, 0 callers each:
  `_classify_repo_path`, `_classify_commit_reference`,
  `_classify_repo_position` — and `_resolved_repo_file` / `_file_line_count`
  are reachable only from those. Each duplicates logic `evidence.py` now owns.
- Four front-matter FACT entries in `launchpad/docs/corpus/AGENTS.md` describe
  pre-refactor behaviour and are now false: external URL always `UNVERIFIED`
  (:64), GitHub link never checked for existence (:68), commit-only FACT is
  non-fatal (:96), line number never compared against file length (:100). Its
  citation table (:216-224) says the same. That file is also the resolved
  `AGENTS.md` for the whole corpus subtree.
- The prior session's plan sits at `docs/superpowers/plans/`. Repo convention
  and `~/.claude` guidance both put plans under `launchpad/plans/`.

---

STEP 1  Move URL verification into the registry              [independent]  ← RUNS HERE
        `evidence.py`'s `verify_citation`
        gains `check_links`, and owns the GitHub pin/verb/path syntax rules,
        `_url_request_target`, and the bounded HEAD→ranged-GET probe.
        `validate.py._classify_url` becomes a delegate.
        done when: `grep -c 'urllib\|_url_resolves' validate.py` returns 0;
        187 tests pass; offline run still reports
        `{'UNVERIFIED': 405, 'FAIL': 1}` and a `--check-links` run reports the
        same counts it reports on `3f5c45559` before the change.

STEP 2  Delete the now-dead duplicated helpers                   [needs 1]
        `_classify_repo_path`, `_classify_commit_reference`,
        `_classify_repo_position`, `_resolved_repo_file`, `_file_line_count`
        from `validate.py`.
        done when: `grep -n 'def _classify_repo_path\|def _classify_commit_reference\|def _classify_repo_position\|def _resolved_repo_file\|def _file_line_count' validate.py`
        returns nothing; 187 tests pass; validator counts unchanged from step 1.

STEP 3  Add a `git_ls_tree` / `git_show` reachability verifier    [needs 1]
        **Revised 2026-09-01 — see DECISION-1. Fail-only, not replay-and-pass.**
        In `evidence.py`: parse the citation's arguments, resolve the cited
        `ref` and `path` through read-only git plumbing via an argument list
        (never a shell string). The asserted result is NOT compared — it is
        prose, and only 1 of 80 is machine-comparable.
        Verdicts: `error` when the cited ref or path no longer resolves;
        `unverified` (still blocking) when the source is reachable, with a
        detail saying the assertion was not compared; `unverified` when the
        arguments cannot be parsed into known keys.
        done when: a test asserts a citation naming a missing ref verifies
        `error`; one naming a live ref and existing path verifies `unverified`
        with a detail distinguishable from the generic string; one carrying
        shell metacharacters (`;`, `$(`, backtick) verifies `unverified`
        without spawning a process; **no input to this verifier returns `ok`**;
        187+ tests pass.

STEP 4  Add a SHA-pinned `grep` replay verifier                      [needs 3]
        **Revised 2026-09-01 — see DECISION-1. Pinned inputs only.**
        Covering `grep_recursive`, `grep_case_insensitive`, `grep_repo`,
        `grep_recursive_case_insensitive`, `grep`, `grep_case_sensitive`,
        `grep_extended_regex`. Pattern and path are passed as arguments.
        Replay happens **only** when the citation pins `ref=` to a full
        40-hex SHA that exists locally (8 of 78 citations today) and the
        asserted result leads with a checkable verdict (`zero matches`,
        `N matches`). Everything else stays blocking.
        Verdicts: `error` when a pinned replay contradicts the asserted
        verdict, or when the pinned commit does not exist; `unverified`
        otherwise. **No input returns `ok`** — a matching replay confirms the
        count, not the claim the count was cited to support.
        done when: a test asserts a pinned citation whose verdict is
        contradicted by replay verifies `error`; a pinned citation whose
        verdict matches verifies `unverified` (not `ok`); an unpinned
        citation verifies `unverified` without spawning a process; a pattern
        containing shell metacharacters verifies `unverified` without
        spawning a process; 187+ tests pass.

STEP 5  Name each unsupported tool family in its detail          [needs 4]
        Every still-unsupported family (`shell`, `webfetch`,
        `curl_fetch`, `gh_*`, `github_api`, `git_log*`, `git_diff_name_only`,
        misc) an explicit blocking `unverified` detail that names the family
        and why no verifier exists — replacing today's single generic
        "names no openable file" string.
        done when: an offline run's `UNVERIFIED` details resolve to more than
        one distinct message for tool-result citations, no detail contains any
        citation value, and the total blocking count still accounts for every
        previously-blocking citation (none silently reclassified to `ok`).

STEP 6  Split CI into named stages                               [needs 5]
        In
        `.github/workflows/launchpad-corpus-validate.yml`: structural
        (offline) and link-check, each its own step with its own name, so a
        network failure is distinguishable from a structural one.
        done when: the workflow contains two separately-named validation steps;
        `actionlint` (or `gh workflow view` after push) reports no syntax error;
        the structural step's command carries no `--check-links`.

STEP 7  Re-measure and write the tool-result policy inventory    [needs 5]
        After steps 3-5, write the
        inventory to `launchpad/plans/` — per-family counts, which families the
        new verifiers now cover, which remain blocking and why.
        done when: the document states a current measured count for every
        family in ALREADY TRUE, and each is marked verified / blocking /
        needs-decision.

STEP 8  Correct AGENTS.md's four false FACT entries              [needs 5]
        Those entries and the citation table in
        `launchpad/docs/corpus/AGENTS.md` to describe post-refactor behaviour,
        and move its recorded revision per that file's own *Updating a node*
        rule.
        done when: `validate.py` passes on the corpus; no remaining front-matter
        statement in that file contradicts a behaviour a test in
        `tests/test_validate.py` asserts.

STEP 9  Relocate the prior session's plan file              [independent]
        Move `docs/superpowers/plans/2026-09-01-evidence-verifier-registry.md`
        to `launchpad/plans/` (git mv, preserving history).
        done when: nothing remains under `docs/superpowers/plans/`; `git log
        --follow` on the new path shows the original commit.

---

PARALLEL  Steps 1 and 9 may run as parallel subagents — step 9 touches only a
          plan file path, nothing step 1 reads. Steps 2-8 are strictly
          sequential: 2, 3, 4 and 5 all edit `evidence.py` and/or `validate.py`,
          step 6 depends on the CLI surface step 5 finalizes, and steps 7 and 8
          both need the post-step-5 measured corpus state. Do not fan 3 and 4
          out concurrently despite their apparent independence — same file.

GATES     `review-code` and `review-tests` after step 5, on the cumulative diff
          — these steps add subprocess execution driven by document content,
          which is the highest-risk change in the branch. `review-final` after
          step 8, before any PR. `qa` explore mode **applies**: the validator is
          a CLI with a real runtime surface (`--check-links`, `--root`, exit
          codes), and steps 3-5 add argument-parsing paths reachable from
          untrusted corpus prose — exercise hostile citation text against it.
          No UI, so `review-a11y` does not apply.

BUDGET    Step 4. Seven grep families with differing flag semantics
          (recursive, case-insensitive, extended-regex) each need their
          asserted-result grammar parsed, and "absence" is the harder half:
          proving a pattern is absent from a scope requires getting the scope
          exactly right or the verifier passes vacuously.

DECISION-1  **Tool-result verifiers are fail-only. Decided 2026-09-01.**
          The plan's original steps 3-4 assumed a citation's asserted result
          could be compared against a replay. Measured against the real
          corpus, it cannot:

          `git_ls_tree` + `git_show`, 80 citations — arguments fully tractable
          (80/80 parse, **0** carry shell metacharacters), but only **1 of 80**
          asserted results is a machine-comparable list. 41 carry negations
          ("no layers/ directory present"), 30 partial-list hedges
          ("includes ..."), 33 globs (`schema/**`), 36 provenance tails
          ("run 2026-08-27"). A strict comparator would fail ~79 true
          citations; a lenient one would pass vacuously on every "includes"
          and could not evaluate a negation at all.

          `grep_*`, 78 citations — 49 lead with a checkable verdict
          ("zero matches", "N matches"), but only **8** pin `ref=` to a full
          SHA. Replaying the other 41 against a moving tree cannot distinguish
          a false citation from ordinary drift.

          So the verifiers check **reachability, not assertion**, and may only
          ever fail a citation. `error` when a source is gone or a pinned
          replay is contradicted; otherwise the citation keeps blocking as
          `unverified` with a per-family detail. Nothing here returns `ok`.

          This keeps the branch's thesis intact — unverifiable is not a passing
          state — while adding detection that has immediate teeth: **10 of the
          14 distinct refs cited by `git_show`/`git_ls_tree` no longer exist**
          (`origin/task/1329-corpus-template-capability` and nine siblings,
          deleted after their PRs merged).

DECISION-2  **`invariants.md` cites `validate.py` by bare path. Decided 2026-09-01.**
          That node documents the validator by citing its own source at seven
          line positions, and this branch reshapes that source. After step 2
          the file went 905 -> 834 lines: `:836` fell out of bounds and failed,
          the other six kept passing while naming the wrong code. All seven are
          now bare paths, which is what `AGENTS.md:279-281` already prescribes
          ("a position that has silently drifted is worse than no position").
          Each statement names its function in the prose, so the locator
          survived. The absent symbol-anchored citation form is filed as #2012.

OPEN      1. **The 211 blocking tool-result citations.** Steps 3-4 should cover
             roughly 135 of them (git_ls_tree 60, git_show 19, grep families
             ~57). The remainder — `shell`, `webfetch`, `gh_*`, `github_api`,
             `curl_fetch`, `git_log*` — have no safe replay and need a decision
             per family: replace with a file citation, reclassify the entry, or
             accept a permanent blocking state. Not decided here.
          2. **Graph-edge verification (originally item 3) is CLOSED as
             unneeded — decided 2026-09-01, not left open.** Reasoning, in
             order of weight: (a) under fail-closed a graph-edge citation
             already blocks, so the gap cannot go unnoticed and no guard is
             needed; (b) issue #1314, which owned the graph-edge form, is
             closed, and the standard it produced
             (`standards/evidence.md:522`) documents graph edge → `unverified`
             → "Nothing"; (c) the corpus contains **0** graph-edge citations
             today; (d) `ProjectGraph` has no persisted artifact, so
             verification means rebuilding from symbols per run — really
             #633's deterministic graph/index generation, not the validator's.
             It *will* eventually matter: `CONTRACT.md` §8 shows the
             project-intelligence answer pipeline emitting graph-edge
             citations as its native form for dependency claims. Revisit when
             that output starts landing in nodes, or when #633 produces a
             graph artifact to check against.
          3. **Whether CI's link-check stage may fail the build on network
             error.** A dead-link check is nondeterministic by nature; a flaky
             third-party host would redden an unrelated PR. Step 6 splits the
             stages but does not decide whether the link stage is required.
          4. **When to open the PR.** Merging while any citation still blocks
             turns CI red on `launchpad` immediately. Sequencing of PR vs.
             OPEN-1 cleanup is the user's call.

LEFT OUT  - Fixing the 211 citations themselves. Steps 3-5 build verifiers and
            measure; they do not edit corpus prose. That is OPEN-1's migration
            and belongs in its own issue and PR.
          - Any verifier that executes citation text as a shell string. The
            prior session refused this and the refusal stands: corpus documents
            are the input, so `shell(...)` replay is command injection through
            documentation.
          - Squashing the duplicate-message commits `32c8d006f` / `3f5c45559`.
            Cosmetic, and rewriting shared history is a separate decision.
          - Filing the related open issues (#1459, #1478, #1619, #1951) as
            closed. Several describe behaviour this branch changes, but
            confirming and closing them is post-merge work.
