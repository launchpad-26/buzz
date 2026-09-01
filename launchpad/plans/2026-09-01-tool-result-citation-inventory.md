# Tool-result citation inventory

Measured 2026-09-01 against `launchpad/docs/corpus/` on branch
`fix/validate-fail-closed-citations` at the completion of step 6, by running
`evidence.parse_citation` and `evidence.verify_citation` over every citation in
the tree. Counts here are outputs of that run, not estimates.

Step 7 of `2026-09-01-corpus-evidence-verifier-registry-completion.md`.

## Headline

- **213** tool-result citations, across **47** distinct family names.
- **14** now report a hard `error` — all of them `git_show` citations naming
  task branches deleted after their pull requests merged, in 5 nodes.
- **199** remain blocking `unverified`, now carrying a reason specific to their
  family rather than one generic string.
- **0** return `ok`. No verifier built in steps 3–5 can pass a citation; each
  may only fail one or leave it blocking. See DECISION-1 in the plan.

Blocking is conserved against the step-1 baseline: **405** citations blocked
then, **405** block now (391 `unverified` + 14 `error`). Nothing was
reclassified into a pass.

## Per-family

`verified` here means *a verifier ran against it*, never *the claim was
established*. No column in this table asserts a citation is true.

| Family | n | error | blocking | Status |
|---|---:|---:|---:|---|
| `git_ls_tree` | 60 | 0 | 60 | verified — reachability checked, all resolve |
| `grep_recursive` | 21 | 0 | 21 | verified — replayed where pinned |
| `git_show` | 19 | 14 | 5 | **verified — 14 cite deleted branches** |
| `grep_case_insensitive` | 16 | 0 | 16 | verified — replayed where pinned |
| `grep_repo` | 10 | 0 | 10 | verified — replayed where pinned |
| `grep_recursive_case_insensitive` | 7 | 0 | 7 | verified — replayed where pinned |
| `git_diff_name_only` | 6 | 0 | 6 | needs-decision — replayable, prose result |
| `shell` | 6 | 0 | 6 | blocking, permanently — see below |
| `webfetch` | 5 | 0 | 5 | needs-decision — recite as a URL |
| `grep` | 5 | 0 | 5 | verified — replayed where pinned |
| `git.ls_tree` | 4 | 0 | 4 | verified — reachability checked |
| `gh_pr_list` | 3 | 0 | 3 | blocking — mutable, authenticated |
| `github_api` | 3 | 0 | 3 | blocking — mutable, authenticated |
| `gh_issue_list` | 3 | 0 | 3 | blocking — mutable, authenticated |
| `validate.py` | 3 | 0 | 3 | needs-decision — cite the file instead |
| `grep_extended_regex` | 3 | 0 | 3 | verified — replayed where pinned |
| `git_log` | 3 | 0 | 3 | needs-decision — replayable, prose result |
| `git_grep` | 2 | 0 | 2 | needs-decision — a grep under a git name |
| `grep_case_sensitive` | 2 | 0 | 2 | verified — replayed where pinned |
| `git_log_oneline` | 2 | 0 | 2 | needs-decision — replayable, prose result |
| `git_log_last_commit` | 2 | 0 | 2 | needs-decision — replayable, prose result |
| `gh_issue_view` | 2 | 0 | 2 | blocking — mutable, authenticated |
| `grep_reload` | 2 | 0 | 2 | needs-decision — invented grep name |
| 24 further families | 24 | 0 | 24 | needs-decision — one citation each |

The 24 singletons: `gh_api_repo_license`, `curl_fetch`, `gitlab_api`,
`fetch_attempt`, `find_crates_readmes`, `file_exists`, `grep_word_count`,
`run_command`, `run_python_check`, `find_file`, `yaml.safe_load`,
`path_exists`, `find`, `grep_id_field`, `grep_imeta`, `grep_literal`,
`cargo_test`, `grep_networkpolicy`, `grep_rli`, `grep_instrument`,
`grep_pg_discrete_vars`, `grep_typesense`, `grep_search`, `git_merge_base`.

## What the measurement exposed beyond the counts

**The family vocabulary is unconstrained.** 47 names describe roughly six
operations, and 24 of them appear exactly once. 18 names are grep-shaped but
only 7 are ones a verifier recognises; the other 11 (`grep_typesense`,
`grep_networkpolicy`, `grep_pg_discrete_vars`, …) encode *what was being
searched for* in the tool name rather than in the pattern. 11 names are
git-shaped and 3 are recognised. Nothing validates a family name, so each
author invents one, and every invented name is invisible to every verifier.

This is the ceiling on verifier coverage, and it will not be lifted by writing
more verifiers. A citation reading `grep_typesense(...)` cannot be routed to
the grep verifier without either an alias table that grows forever or a rule
that any `grep_*` prefix means grep — and the latter is a guess about intent
made against untrusted document text.

**Coverage is bounded by pinning, not by parsing.** Of the grep citations a
verifier does recognise, only 7 pinned `ref=` to a full SHA and were replayed.
38 name a branch or no ref at all. Parsing them is easy; the limit is that
replaying an unpinned citation against a moving tree cannot distinguish a
false citation from ordinary drift.

## Recommended dispositions

1. **`shell`, `run_command`, `run_python_check` (8) — blocking, permanently.**
   Replaying these means executing text from a corpus document. The refusal is
   the feature. Migrate each to a file or commit citation naming what the
   command inspected.
2. **`webfetch`, `curl_fetch`, `fetch_attempt` (7) — recite as URLs.** The URL
   citation form already exists and is checked under `--check-links`. This is a
   mechanical rewrite, not new machinery.
3. **`gh_*`, `github_api`, `gitlab_api` (13) — blocking.** Issue and PR state
   is mutable and authenticated; a replay would report today rather than what
   was cited. Cite the pinned permalink instead where a claim needs support.
4. **`git_log*`, `git_diff_name_only`, `git_merge_base`, `git_grep` (16) —
   needs-decision.** These are replayable read-only plumbing. Whether to build
   verifiers depends on whether their asserted results can be pinned to a
   checkable verdict, which today they cannot: the results are prose.
5. **The 14 `git_show` errors — fix the citations.** These are the only
   citations this branch proves wrong rather than merely unproven. Each names a
   deleted task branch; each should be repinned to the commit SHA that branch
   merged as, which is still reachable from `launchpad`.
6. **The naming tail — constrain the vocabulary before extending coverage.**
   A closed set of family names in `CONTRACT.md`, enforced by the validator,
   is worth more than any individual verifier. Until it exists, coverage
   degrades every time someone invents a name.

Items 1–4 and 6 are OPEN-1's migration and belong in their own issue and PR.
Item 5 is the only one this branch could reasonably absorb, and it edits corpus
prose, which steps 3–5 deliberately did not.
