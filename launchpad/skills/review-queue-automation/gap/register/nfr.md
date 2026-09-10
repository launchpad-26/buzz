# RQA gap register — non-functional requirements

The 33 non-functional requirements of the frozen specification, one row each. How the system must behave while doing it — the non-functional obligations.
Sibling registers hold the other two classes:
[`br.md`](br.md), [`fr.md`](fr.md), [`nfr.md`](nfr.md).

**This file is evaluated.** Every requirement of this class has a row, in the
order the specification lists them, carrying the `gap degree`, `root cause`,
`evidence` and `depends on` this lane assigned against revision `9267b6308`
using the definitions in [`methodology.md`](../methodology.md). A later
re-evaluation replaces those four cells of a row in place and bumps its
`revision`; it does not restructure the table, reorder it, add columns to it, or
write a new file.

## Why the register is keyed by requirement ID

The requirement identifier is the only key in this analysis that is stable
across revisions. Files get renamed, split and deleted; clusters and disposition
units are this analysis's own constructs and will change when the estate does;
requirement IDs are fixed by the frozen specification, which
[`methodology.md`](../methodology.md) §1 forbids this analysis to edit. Keying on
the ID gives three properties the analysis depends on:

- **Completeness is checkable.** 14 + 39 + 33 = 86 rows against 86 `### RQA-…`
  headings in
  [`requirements-specification.md`](../../requirements/requirements-specification.md).
  A requirement with no row is a mechanical failure, not a judgement call.
- **A row is addressable.** Any later document, issue or decision cites
  `RQA-NFR-NNN` and lands on exactly one row.
- **Re-evaluation is diffable.** Re-running the analysis at a later revision
  updates the same rows, so the diff shows what *changed about the assessment*
  rather than what changed about the document's layout.

## How a row is updated

The register is **updated in place, never superseded by a new document.** There
is one register per requirement class, for the life of this analysis.

1. Re-read the requirement in the frozen specification and the code it concerns
   at the revision being evaluated.
2. Apply the "implements" test ([`methodology.md`](../methodology.md) §2), then set
   `gap degree` (§5), `root cause` (§6) and `evidence` (§3) from what that test
   found. `root cause` is `-` when and only when `gap degree` is `fit`.
3. Set `depends on` to the requirement IDs whose gaps must close before this
   one's can (§9), or `-`. Never a priority, never a sequence number.
4. **Set `revision` to the short SHA the row was evaluated against.** The
   `revision` cell records when this row was last *evaluated*, not when the
   register file was last touched. A row still reading an older SHA than its
   siblings is a row nobody has re-checked — that is the cell's whole purpose,
   so it is only ever bumped by an evaluation that actually re-read the code.
5. Where the evaluation runs into something a person must decide, add
   `PENDING-HUMAN:<short-id>` to `notes` and leave the rest of the row at its
   honest value. An escalation never justifies changing the specification.

Rows are **never deleted**: the frozen specification defines the row set, so a
row disappears only if the specification does, and nothing in this analysis may
edit it. A requirement that turns out to be met needs its degree changed to
`fit`, not its row removed.

## Column meanings

| column | meaning |
| --- | --- |
| `id` | The requirement identifier from the frozen specification. The row's key. |
| `gap degree` | `fit`, `partial gap`, `full gap` or `conflicting`, as defined in [`methodology.md`](../methodology.md) §5. Exactly one, always present. |
| `root cause` | `-` for `fit`; otherwise `not built`, `built against superseded intent`, `built then orphaned` or `built contrary` — [`methodology.md`](../methodology.md) §6. |
| `evidence` | Disposition-unit IDs (`U-<CLUSTER>-NN`) and/or `path:line` citations relative to `launchpad/skills/review-queue-automation/`, at the row's `revision`. Never empty. A `fit` row never rests on a test or a document alone ([`methodology.md`](../methodology.md) §3). |
| `depends on` | Requirement IDs whose gaps must close before this one's can, or `-`. A technical precedence only — [`methodology.md`](../methodology.md) §9. |
| `revision` | Short SHA the row was last evaluated against. `9267b6308` throughout this skeleton. |
| `notes` | Free text; `-` when there is nothing to say. `PENDING-HUMAN:<short-id>` marks an escalation to a person. |

There is deliberately **no priority column**. Every requirement in the frozen
specification is mandatory, so ranking them is a planning decision this analysis
does not make ([`methodology.md`](../methodology.md) §9).

## Row order

Rows follow the order in which the specification lists the requirements of this
class — the order of the `### RQA-NFR-NNN` headings in
[`requirements-specification.md`](../../requirements/requirements-specification.md),
which is thematic and **is not** ascending numeric order. This is the order the
mechanical conformance check requires, and it keeps the register readable
alongside the specification it mirrors. **Do not re-sort this table**: a
numerically sorted register fails the check.

## The split-AC rule applies to every row here

A source clause that produced several requirements is satisfied only when
**all** of them are satisfied. Never record or summarise a clause as covered
because one child row reads `fit` while a sibling does not
([`methodology.md`](../methodology.md) §8). Degrees are assigned per requirement;
nothing in this file is a clause-level judgement.

## Class-specific note: where the non-functional gaps concentrate

Four clusters of this class share one cause each, and reading the rows together
is easier than reading them one by one.

- **The remediation family** (`RQA-NFR-019`, `RQA-NFR-020`, `RQA-NFR-021`,
  `RQA-NFR-031`, `RQA-NFR-033`) has no reachable behaviour at all. The isolation
  and force-push refusals exist in `scripts/worktree.py` and nothing calls them
  — methodology §2.4's worked example — while the mechanical-category and
  behaviour-change classifications the other three rows need were never built.
  The bounds these rows state must land before the action they bound, so the
  ordering edge sits on `RQA-FR-017`'s row, not on theirs
  ([`methodology.md`](../methodology.md) §9, authority).
- **The external-provider family** (`RQA-NFR-012`, `RQA-NFR-013`,
  `RQA-NFR-023`, `RQA-NFR-029`) fails on a single missing concept: there is no
  permit-or-forbid decision for sending content to a provider, at any
  granularity. `RQA-NFR-027` is `fit` only because the absence of a configured
  pool means nothing is sent — a consequence of having no reviewer, not of a
  decision the system makes.
- **The merge family** (`RQA-NFR-008`, `RQA-NFR-026` and the merge half of
  `RQA-NFR-017`) fails because no merge capability exists anywhere:
  `authority.ACTIVITIES` has no `merge` entry and the mutation registry no
  merge operation. That absence is `RQA-NFR-026`'s `partial gap`, ruled by the
  maintainer on 2026-09-08; its other five activities do default to disabled.
- **The authority-enforcement family** (`RQA-NFR-017`) fails on a fact a reader
  would not guess from the config model: of the six declared activities, only
  `comment`, `approve` and `request_changes` reach `mode_for`/`can_act` under
  `scripts/`; `review`, `fix` and `triage` are configurable, never consulted.

**Four rows carry degree `conflicting`** (`RQA-NFR-010`, `RQA-NFR-017`,
`RQA-NFR-018`, `RQA-NFR-030`), each with root cause `built contrary`. The test
applied to every row of this class is whether **any reachable execution at
`9267b6308` produces an outcome the requirement forbids**; where it does, the
degree is `conflicting`, because satisfying the requirement means that execution
must stop producing that outcome. Each of the four names the execution and the
line range that decides it: a discarded ledger-write failure, a review activity
run without consulting its own authority mode, a discarded shadow clamp, and a
credential fallback that takes the operator's user-wide token.

**Where that test lands "no", and why three rows that look alike read alike.**
The discriminator is whether reachable code **decides the matter the requirement
governs, and decides it the way the requirement forbids.** The four rows above
all do: the code poses the question (what to do when a ledger append fails,
whether to run the review, which config to return when the snapshot cannot be
built, which credential to acquire) and answers it contrary to the requirement,
on a path the system takes itself. Three other rows share a surface pattern —
*data is trusted because nothing verifies it* — and none of them meets the test,
so all three read alike:

- `RQA-NFR-028`: nothing anywhere poses the question "is this stored provenance
  row authentic". No row carries an integrity field of its own; `entries()` is a
  SELECT, and the `snapshot_hash` a row does carry is a pointer that nothing
  verifies on the reconstruction path (search S8).
- `RQA-NFR-016`: nothing poses the question "is this pull request crafted to
  induce a clean review". Findings are whatever the reviewer model reported.
- `RQA-NFR-024`: nothing poses the question "what scopes does this credential
  carry". The capability probe answers a different question — what role the
  repository grants — and reduces authority accordingly.

In each the requirement's subject matter is absent from the code rather than
decided wrongly by it, closing the gap adds a check where no check exists rather
than correcting one that does, and methodology §5's "silence is never a conflict"
governs. Principle 1's gloss about adding a missing check to a **decision
function** presupposes a function that decides the matter; these three have none.
All three are `full gap`. A round-2 revision carved `RQA-NFR-028` out at
`partial gap`, on the ground that the policy and protocol in force are protected
by the snapshot payload's hash check. That carve-out is withdrawn: search S8
shows the check lives on the live-dispatch path deciding a *new* job's policy,
while `explain.py` — the single command RQA-FR-012's reconstruction runs
through — imports only `cli` and `ledger`, and nothing cross-references a stored
`snapshot_hash` at read time. With the carve-out gone the three rows do not
differ, and reading alike is the result of the test rather than a target set for
it.

`RQA-NFR-024` and `RQA-NFR-030` are the pair most worth reading together, since
they are adjacent obligations on one credential: NFR-024's floor is never posed
as a question anywhere (`full gap`), while NFR-030's ceiling is breached by a
specific reachable branch that chooses which credential to hold (`conflicting`).

## Searches these rows rest on

Every asserted absence in this register is a claim about the tree at
`9267b6308`, and the standing rule is that such a claim quotes the command run
and the output it returned. The searches below were re-run in a clean worktree at
that revision, from `launchpad/skills/review-queue-automation/`, and each is
cited by ID from the rows that rest on it. Where a search returns an incidental
hit that is not what the row claims, the hit is named here rather than filtered
out of the quote.

**S1 — nothing outside `worktree.py` calls the worktree operations.** Bears on
`RQA-NFR-007`, `RQA-NFR-020`, `RQA-NFR-021`.

```
$ grep -rn "worktree" scripts/ tests/ | grep -v "^scripts/worktree.py:" | grep -v "^tests/test_worktree.py:"
scripts/runners.py:120:    `--skip-git-repo-check` keeps the call usable from a worktree or bare path.
tests/test_repairs.py:5:mutation authority, lease node-id, worktree, supersede, risk boundaries, protected
tests/test_integration.py:131:def test_worktree_create_clean_repeatable_with_fake() -> None:
tests/test_integration.py:133:    import worktree
tests/test_integration.py:144:        worktree.create(config, "a/b", "job1", base="launchpad", runner=fake_run)
tests/test_integration.py:146:    except worktree.WorktreeError as exc:
tests/test_integration.py:149:    out = worktree.create(config, "a/b", "job1", head_sha="deadbeef", runner=fake_run)
tests/test_integration.py:153:    result = worktree.clean(config, "a/b", "job1", runner=fake_run)
tests/test_integration.py:156:    worktree.clean(config, "a/b", "job1", runner=fake_run)
tests/test_integration.py:157:    assert any("worktree" in " ".join(a[1]) for a in calls) or True
```

The only `scripts/` hit is a docstring line in `runners.py`, not a call. The only
invoking callers are `tests/test_integration.py` and `tests/test_worktree.py`
(excluded above as the module's own test; its import is
`tests/test_worktree.py:20`). `tests/test_repairs.py:5` is a docstring naming
coverage the file does not in fact carry — a divergence wave 1 already records.

**S2 — no mechanical-remedy vocabulary exists.** Bears on `RQA-NFR-019`,
`RQA-NFR-031`, `RQA-NFR-033`.

```
$ grep -rin "mechanical" scripts/ schemas/ config.example.json
scripts/planner.py:125:#: mechanically narrower and does not need the deep code questions.
```

The single hit is a comment about a review activity's scope, unrelated to
classifying a finding's remedy.

**S3 — no merge capability.** Bears on `RQA-NFR-008`, `RQA-NFR-017`,
`RQA-NFR-026`.

```
$ grep -rn "merge" scripts/authority.py scripts/github_mutate.py
$ echo $?
1
```

No match in either the activity model or the mutation registry.

**S4 — only three of the six activities are ever authorised.** Bears on
`RQA-NFR-017`, `RQA-NFR-026`.

```
$ grep -rn "mode_for(\|can_act(" scripts/ | grep -v "^scripts/authority.py:" | grep -v "^scripts/modes.py:"
scripts/dispatcher.py:941:    mode = mode_for(local_cfg, repo, "request_changes")
scripts/advisory.py:154:    mode = mode_for(local_cfg, repo, "comment")
scripts/action_gate.py:64:    if not can_act(cfg, repo, "request_changes", repo_hard_gate_ok=True):
scripts/approval_evaluate.py:151:    approve_authority = mode_for(cfg, slug, "approve") == "live"
```

`authority.py` is excluded as the definitions themselves and `modes.py` as an
unrelated same-named function (`modes.mode_for` maps a strategy to an execution
mode). No call site passes `review`, `fix` or `triage`.

**S5 — nothing inspects the credential's granted scopes.** Bears on
`RQA-NFR-024`, `RQA-NFR-030`.

```
$ grep -rniE "oauth|x-oauth-scopes|token_scope|granted[_ ]scope|pull_requests:write|contents:read" scripts/
$ echo $?
1
```

The word `scope` does occur under `scripts/`, but only as a SQLite column name
for cadence and circuit-breaker keying (`common.py:283`, `:349`, `:361`) — a
different sense, named here so the next reader is not surprised by it.

**S6 — no configuration expresses an external-send choice.** Bears on
`RQA-NFR-013`, `RQA-NFR-023`, `RQA-NFR-029`.

```
$ grep -rniE "\"(external|send|egress|offline|local_only)[a-z_]*\"" scripts/ config.example.json
scripts/errors.py:43:EXTERNAL_VERIFICATION = "external_verification"
```

The single hit is an error-disposition constant, not a configuration key. The two
pool fields that might carry such a choice are consumed 29 times across eleven
modules:

```
$ grep -rn "provider_family" scripts/ | wc -l
29
$ grep -rl "provider_family" scripts/ | sort | tr '\n' ' '
scripts/approval_evaluate.py scripts/budget.py scripts/common.py scripts/config.py scripts/dispatcher.py scripts/findings.py scripts/model_registry.py scripts/modes.py scripts/panel.py scripts/route_probe.py scripts/routing.py
```

Every consumer is one of four kinds, each checkable at the line cited: cost
accounting (`budget.py:213-228`), route identity and log attribution
(`routing.py:147-165`, `model_registry.py:69`, `dispatcher.py:1209`),
provider-diversity corroboration (`findings.py:168`, `modes.py:203`,
`approval_evaluate.py:113`, `panel.py:657`) and provider-failure cooldown
(`route_probe.py:117`). `config.py:168` validates the field as a non-empty
string. None is a sending or sensitivity decision.

**S7 — no plugin, hook or entry-point admission path.** Bears on `RQA-NFR-001`,
`RQA-NFR-002`, `RQA-NFR-014`.

```
$ grep -rniE "plugin|entry_point|\bhook\b" scripts/
$ echo $?
1
```

**S8 — a ledger row's stored snapshot reference is never verified on the
reconstruction path.** Bears on `RQA-NFR-028`.

```
$ grep -n "^from \|^import " scripts/explain.py
13:from __future__ import annotations
15:import argparse
16:import json
17:import sys
19:from cli import make_state, resolve_or_onboarding
20:from ledger import explain, render_explanation, revisions
$ grep -n "snapshot" scripts/ledger.py | grep -i import
$ echo $?
1
```

`explain.py` — the single command RQA-FR-012's reconstruction runs through —
imports only `cli` and `ledger`, and `ledger.py` imports nothing from
`snapshot.py`. The recompute-and-reject check at `snapshot.py:185-188` lives in
`SnapshotStore._load`, reached only from `.active()`/`.get()` in
`dispatcher.resolve_snapshot` (`dispatcher.py:1562`, `:1595`) while deciding a
**new** job's governing policy. `ledger.explain` returns the stored
`snapshot_hash`/`policy_version` strings verbatim (`ledger.py:89`, `:143`).

**S9 — GitHub is the only platform addressed.** Bears on `RQA-NFR-011`.

```
$ grep -rniE "gitlab|bitbucket|gitea" scripts/
scripts/planner.py:114:    "ci": re.compile(r"(^|/)\.github/workflows/|(^|/)(Jenkinsfile|\.gitlab-ci\.yml)$",
```

The single hit is a changed-path pattern that classifies a `.gitlab-ci.yml` file
*inside a reviewed repository* as CI configuration. It is not support for
GitLab-hosted review, and no transport module addresses any host but GitHub.

**S10 — nothing detects a crafted pull request.** Bears on `RQA-NFR-015`,
`RQA-NFR-016`.

```
$ grep -rniE "injection|crafted|prompt.?inject|tamper" scripts/
scripts/planner.py:69:             "injection, and privilege boundaries."),
```

The single hit is prompt text asking the reviewer to look for injection
vulnerabilities **in the code under review** — the opposite direction from
detecting a PR crafted against the reviewer.

**S11 — `_ledger_record`'s call sites.** Bears on `RQA-NFR-010`.

```
$ grep -c "_ledger_record(" scripts/dispatcher.py
10
```

Ten occurrences, of which one is the definition at `dispatcher.py:202`, leaving
nine call sites.

**S12 — the fixed sets this register names, quoted from where they are
defined.** A claim about a named set's membership is as unfalsifiable to the next
reader as an asserted absence, so the definitions are quoted here rather than
paraphrased. Bears on `RQA-NFR-008`, `RQA-NFR-013`, `RQA-NFR-014`,
`RQA-NFR-017`, `RQA-NFR-019`, `RQA-NFR-026`.

```
$ sed -n '31,34p' scripts/authority.py
#: The full set of supported activities.
ACTIVITIES = frozenset(
    {"review", "comment", "approve", "request_changes", "triage", "fix"}
)
$ grep -n "^ADAPTERS\|RunnerAdapter(" scripts/runners.py | head -4
138:ADAPTERS: dict[str, RunnerAdapter] = {
139:    "omp": RunnerAdapter(
145:    "claude": RunnerAdapter(
151:    "codex": RunnerAdapter(
$ grep -n '"provider_family"' config.example.json
35:        "provider_family": "anthropic",
48:        "provider_family": "z-ai-openrouter",
58:        "provider_family": "qwen-openrouter",
72:        "provider_family": "openai",
85:        "provider_family": "deepseek-openrouter",
95:        "provider_family": "google-openrouter",
```

Two things follow that the rows must not blur. **The code's six activities are
not the requirement's six names.** `ACTIVITIES` holds `review`, `comment`,
`approve`, `request_changes`, `triage` and `fix`; CL-056 names `review`,
`comment`, `approve`, `request-changes`, `remediate` and `merge`. `fix` is the
code's name for `remediate`; `triage` has no counterpart in the requirement; and
`merge` has no counterpart in the code — it is absent from the set entirely, not
a member that happens to be off. **And the transport set is three entries**, so
"exactly three transports" is `ADAPTERS`' own membership, not an inference from
observed behaviour.

## Register

| id | gap degree | root cause | evidence | depends on | revision | notes |
| --- | --- | --- | --- | --- | --- | --- |
| RQA-NFR-022 | fit | - | U-VERDICT-11; scripts/panel.py:249-263; scripts/panel.py:711-715; scripts/ledger.py:70-73; scripts/runners.py:6-10 | - | 9267b6308 | System-written provenance only: the identity sidecar is built by panel.py outside the model-controlled verdict JSON, ledger.record refuses an entry lacking job/repo/head identity, and every runner invocation is flag-enforced read-only, so neither PR content nor model output can write into the state directory. |
| RQA-NFR-028 | full gap | not built | U-RESILIENCE-06; scripts/ledger.py:76-83; scripts/ledger.py:86-103; scripts/ledger.py:121-126; scripts/common.py:331; search S8 | - | 9267b6308 | No row carries an integrity field of its own: the INSERT writes no digest and the schema declares none, so entries() - a plain SELECT - and the explain() reconstruction built on it return whatever the table holds, and an unauthorised SQLite edit reads back as authentic. The snapshot_hash column a row does carry is a pointer to the snapshot in force, and search S8 shows nothing verifies it on this path: explain.py imports only cli and ledger, ledger.py imports nothing from snapshot.py, and the recompute-and-reject check at snapshot.py:185-188 runs inside SnapshotStore._load while resolve_snapshot decides a NEW job's policy - a different artifact, at a different time, for a different purpose. Round 2's partial gap rested on that check as a carve-out for the policy and protocol in force; the carve-out is withdrawn because the citation does not reach the reconstruction path this requirement governs, leaving no complete obligation met. The question the requirement governs - is this stored row authentic - is posed nowhere, so this is silence rather than conflict, the same reading and now the same degree as RQA-NFR-016 and RQA-NFR-024. |
| RQA-NFR-032 | fit | - | U-VERDICT-11; scripts/panel.py:249-263; U-DOCS-01; scripts/approval_action.py:39-46; scripts/github_mutate.py:99-113 | - | 9267b6308 | Every element is constructed and committed by the system: machinery-attested route identity, an APPROVE executed only from a decision record loaded from SQLite by id, and mutation events fixed at module scope. U-DISPATCH-20 tags this row with the swallowed ledger write at dispatcher.py:202-218; that claim bears on whether every element is recorded (RQA-FR-012) and on RQA-NFR-010, not on who writes the record, so it is not inherited here. |
| RQA-NFR-007 | partial gap | built then orphaned | U-DISPATCH-14; U-QUEUE-11; U-VERDICT-08; U-DOCS-56; U-DISPATCH-26; U-DISPATCH-23; scripts/dispatcher.py:424-459; search S1 | RQA-FR-017 | 9267b6308 | The lifecycle is managed end to end for the incoming_review lane and both authoritative outcomes are reachable, but the author-triage remediation step exists only as orphaned code: search S1 shows the sole scripts/ occurrence of worktree outside its own module is a runners.py docstring line, and the only invoking callers are two test modules. The degrade ladder has no product caller either (negative-caller search quoted in U-DISPATCH-23: the only caller in the tree is tests/test_degradation.py). So a PR whose progression needs remediation cannot be carried further. Substrate: the remediation step this row must manage is the behaviour RQA-FR-017 creates, so that row's gap closes first. |
| RQA-NFR-008 | full gap | not built | U-AUTHORITY-01; scripts/authority.py:32-34; scripts/github_mutate.py:99-113; search S3; search S12 | - | 9267b6308 | There is no merge to configure: search S12 quotes ACTIVITIES' membership at scripts/authority.py:32-34 - review, comment, approve, request_changes, triage, fix - and merge is not in it, while search S3 returns no match for merge in either that activity model or the mutation registry. So the per-repository switch this row requires has nothing to switch. RQA-FR-029 states the same absence as a behaviour; under the split-AC rule CL-023 and CL-041 are met only when both close. |
| RQA-NFR-019 | full gap | not built | scripts/authority.py:32-34; scripts/authority.py:42; U-DISPATCH-26; U-DOCS-13; search S2 | - | 9267b6308 | No mechanical-category vocabulary exists: search S2 returns one hit across scripts/, schemas/ and config.example.json, a planner comment about a review activity's scope. The only bound that exists is the activity-level fix gate, which is not category-bounded. The remediation action this row would bound is RQA-FR-017's, and methodology section 9 puts the gate before the action, so the ordering edge is recorded on that row rather than here. |
| RQA-NFR-020 | full gap | built then orphaned | U-DISPATCH-26; U-DOCS-13; U-DOCS-53; scripts/worktree.py:121-134; search S1 | - | 9267b6308 | Methodology section 2.4's worked example: worktree.create builds at repo_root/.worktrees/rqa-<job>, outside the repository's own working tree, and search S1 establishes that no product path reaches create/commit/push/clean - one docstring mention in runners.py, invoking callers only in tests/test_integration.py and tests/test_worktree.py. Ordering as for RQA-NFR-019. |
| RQA-NFR-021 | full gap | built then orphaned | U-DISPATCH-26; scripts/worktree.py:213-222; U-DOCS-13; search S1; search S3 | - | 9267b6308 | worktree.push pushes only the exact configured PR head branch, refuses an internal rqa/ branch and refuses force outright, but search S1 shows nothing reaches it. Separately there is no merge capability to deny: search S3 returns no match for merge in the activity model or the mutation registry. Ordering as for RQA-NFR-019. |
| RQA-NFR-031 | full gap | not built | U-VERDICT-04; scripts/findings.py:88-121; schemas/reviewer-verdict.json:16-21; scripts/planner.py:125; search S2 | - | 9267b6308 | Nothing classifies a finding's remedy as deterministic or behaviour-preserving: the finding object's required keys are fixed at schemas/reviewer-verdict.json:16-21 as severity, title, location, evidence and primary_source, none of which carries a remedy property, and search S2 - shared with RQA-NFR-019 and RQA-NFR-033 - returns a single hit for mechanical across scripts/, schemas/ and config.example.json, an unrelated planner comment. There is therefore no classification for a policy to widen and no ceiling to enforce. |
| RQA-NFR-033 | full gap | not built | U-VERDICT-04; U-DISPATCH-17; schemas/reviewer-verdict.json:16-21; search S2 | RQA-NFR-031 | 9267b6308 | No behaviour-changing finding class exists - search S2, shared with RQA-NFR-019 and RQA-NFR-031 - and the corroborated-blocker path posts CHANGES_REQUESTED with no record that a named human received the finding; only an uncorroborated finding escalates, and for a different reason. Nothing decides anything contrary here - the determination the row turns on is simply absent - so this is silence, not conflict. Contract: this row's population is exactly the findings RQA-NFR-031's behaviour-change test identifies, and until that test exists the system cannot tell which findings the row governs. |
| RQA-NFR-009 | fit | - | U-POLICY-10; scripts/routing.py:66-98; scripts/routing.py:116-186; U-DOCS-37; U-DOCS-27 | - | 9267b6308 | Ladder rungs are derived solely from models.primary and models.secondary or an operator's explicit per-rung pin; when every configured rung is exhausted resolve_route sets final to human and returns without selecting any model, so no unconfigured alternative is ever substituted. |
| RQA-NFR-010 | conflicting | built contrary | U-DISPATCH-20; scripts/dispatcher.py:202-218; scripts/dispatcher.py:653; scripts/dispatcher.py:1027; scripts/dispatcher.py:1451; search S11; U-DISPATCH-19; U-DISPATCH-21; U-RESILIENCE-14; U-QUEUE-09; U-AUTHORITY-08 | - | 9267b6308 | The contrary execution is _ledger_record's bare except, on the authoritative-action paths that call it - the approve action at :653, the request-changes action at :1027, the decision record at :1451, among the nine call sites search S11 counts. A ledger append that fails is discarded and the job proceeds to completion, leaving an authoritative outcome whose provenance record is knowingly incomplete, which is the partially-authoritative result this requirement forbids; the same module converts an equivalent JSONL logging failure into SafeStopSignal, so the estate has both behaviours and this path chose the wrong one. Much else in the requirement is met by compatible behaviour - atomic writes, WAL-wrapped persistence errors, mandatory pre/post REST verification, safe-stop containment, fail-closed inventory reads - but a met majority does not outrank a reachable forbidden outcome. |
| RQA-NFR-001 | partial gap | not built | U-DISPATCH-25; scripts/runners.py:138-157; scripts/runners.py:164-171; search S7 | RQA-FR-030 | 9267b6308 | Three interchangeable transports behind one adapter interface mean the core review logic is not tied to one particular harness, model or provider. But adapter_for raises for any runner outside the fixed three and search S7 finds no plugin, hook or entry-point path admitting another, which is exactly the hard-coded-to-N-known-combinations disqualifier the fit criterion names - so adding a fourth built-in adapter cannot close this row either. Contract: the demonstration this row requires is against the published interaction contract RQA-FR-030 establishes, which is the only route by which a not-previously-used environment can participate at all. |
| RQA-NFR-002 | full gap | not built | scripts/runners.py:164-171; scripts/runners.py:138-157; U-DISPATCH-25; search S7 | RQA-FR-030 | 9267b6308 | No admission path of any kind for a non-built-in environment: ADAPTERS is a three-entry mapping, adapter_for raises for every other name, and search S7 returns no plugin, hook or entry-point mechanism anywhere under scripts/ - so there is neither a skill/plugin/hook acceptance path nor a way for the environment to speak the contract directly, which the fit criterion would also accept. Contract: this row's participation is defined against the published interaction contract RQA-FR-030 establishes, and there is nothing for a conforming environment to conform to until that contract exists. |
| RQA-NFR-003 | partial gap | not built | U-DOCS-50; U-VERDICT-02; schemas/reviewer-verdict.json:4-5; scripts/runners.py:71-137 | - | 9267b6308 | The data formats at the integration boundaries are open, portable and implementation-neutral: JSON config and evidence, a JSON Schema verdict contract, JSONL traces, and standard HTTP Link pagination. The reviewer-harness boundary is not: scripts/runners.py:71-137 is three hard-coded per-CLI flag contracts, and the module's own docstring at :12-21 records design rules for them without recording any reason why an open, portable, neutral contract was impractical - the evidenced impracticality the fit criterion accepts as an alternative is therefore not present at the place it would be stated. The RQA-FR-030 edge recorded in round 1 is withdrawn: this row's obligation is the boundary's format, and that boundary could be restated in an open, portable, neutral contract while adapter_for still refused every unlisted harness, so the precedence is not forced under any of section 9's three categories. |
| RQA-NFR-004 | fit | - | U-QUEUE-07; U-QUEUE-08; scripts/config.py:27-28; scripts/scheduled-tick.sh:60-62 | - | 9267b6308 | Configuration, state directory and cadence are keyed per repository: the authoritative config path is computed from the repo root, cadence rows are keyed by an opaque scope string, and one timer drives several independently-configured repo roots with the worst per-repo exit status reported rather than the first failure halting the rest. The owner and organisation reach the code only as the configured repository slug, and no cited path branches on public versus private. The single shared credential is RQA-NFR-030's concern, not this row's. |
| RQA-NFR-005 | fit | - | U-RESILIENCE-09; U-POLICY-01; scripts/common.py:45-57; scripts/config.py:446-455; U-QUEUE-06 | - | 9267b6308 | Config and policy are read and re-normalised from the live repo-local JSON path on every call - load_config re-reads and re-normalises per call rather than memoising, and load_repo_config JSON-parses the file at call time - so an edit is visible on the very next invocation with no build, install or deployment step in between. The shadow lock on changed route material is a re-qualification step, not a rebuild or redeploy. |
| RQA-NFR-006 | fit | - | U-POLICY-06; U-RESILIENCE-10; U-RESILIENCE-16; U-DOCS-03; scripts/common.py:97-111; scripts/config.py:27-28 | - | 9267b6308 | Every component is local: repo-local config, a SQLite state directory, a launchd timer, CLI subcommands, and an onboarding step that contacts neither GitHub nor a model. U-DOCS-24 tags this row with conftest.py being dead under run_all.py; that claim bears on test-suite isolation, not on whether one contributor can run the workflow locally, so it is not inherited here. |
| RQA-NFR-012 | partial gap | not built | scripts/panel.py:598-616; scripts/evidence.py:91-126; U-VERDICT-07; scripts/runners.py:6-10; U-DISPATCH-25 | - | 9267b6308 | What the system itself sends is the prompt quoted in full at scripts/panel.py:598-616: repo, PR number, lane, job and a local filesystem path to the evidence envelope - metadata only, with no code, diff or evidence content interpolated into it. The bundle those three content types live in is written to the local artifact directory (scripts/evidence.py:91-126) and reaches a provider only if the runner's own file access reads it, which the omp transport's --no-tools disables outright, so on the cited paths no RQA mechanism sends the other three named content types. NFR012-RUNNER-SEND was settled by the maintainer on 2026-09-08: "permit … to be sent" in this requirement means RQA must not prevent it, not that RQA must itself transmit, so no transport or egress component is required, and RQA writing the evidence bundle to the local artifact directory (scripts/evidence.py:91-126) with a harness reading it from there satisfies the permission. His reasoning, recorded as he gave it: AC17 requires the active external provider path be identifiable *before evidence is sent*. That is satisfied from configuration at preflight — a disclosure check, not an egress proxy — so the identifiability obligation does not force RQA to own the send. Reading it as active transmission would add a component with a security boundary that AC17 does not require, against C1's tooling independence, which puts the model call in the harness rather than in RQA. The ruling settles what the requirement means, not whether the code meets it, so the degree stays partial gap and the root cause stays not built. What it leaves as the residual gap, and the reason this row is not fit, is that --no-tools categorically disables the harness file access the permission depends on: in every configuration that sets it, RQA does prevent code, diffs and evidence reaching the explicitly configured provider, however permissively the requirement is read, and the fit criterion needs each of the four named content types to be individually sendable. Metadata is the one type the prompt itself carries. |
| RQA-NFR-013 | full gap | not built | scripts/runners.py:164-171; scripts/runners.py:138-157; U-DISPATCH-25; U-POLICY-10; scripts/routing.py:66-98; scripts/config.py:158-173; config.example.json:105-106; search S6; search S12 | - | 9267b6308 | The system has no concept of a review path that avoids an external provider. Search S6 finds no configuration key expressing such a choice - its only hit is an error-disposition constant - and shows the one pool field that might carry it, provider_family, consumed 29 times across eleven modules for cost accounting, route identity and log attribution, provider-diversity corroboration and provider-failure cooldown, each checkable at the line cited there, and never as a sending or sensitivity decision; validate_config constrains it only to a non-empty string. What an operator can select is which of the three transports ADAPTERS declares runs (search S12 quotes its membership: omp, claude, codex), since adapter_for raises UnknownRunnerError for any other runner. So there is no path to select, distinct from one that permits sending, and no obligation of this row is met. Whether some transport could in principle be pointed at a self-hosted model is not evidenced either way in this estate and is not what the row turns on. assurance.sensitive_paths is the nearest concept and raises the assurance floor rather than choosing a sending path. |
| RQA-NFR-023 | full gap | not built | scripts/config.py:27-28; U-POLICY-01; scripts/routing.py:66-98; search S6 | - | 9267b6308 | The configuration substrate is genuinely per-repository - the authoritative config is repo-local, so there is no installation-wide file for a global switch to live in - but search S6, shared with RQA-NFR-013 and RQA-NFR-029, finds no permit-or-forbid key for external-provider sends at any scope, so there is no such decision to be scoped per repository and the obligation is unmet rather than partly met. The RQA-NFR-013 edge recorded in round 1 is withdrawn: a per-repository permit boolean is buildable in the repo-local config without RQA-NFR-013's richer appropriate-path concept existing, so the precedence is not forced under any of section 9's three categories. |
| RQA-NFR-027 | fit | - | U-POLICY-10; scripts/routing.py:66-98; scripts/routing.py:116-186; scripts/panel.py:576-582; scripts/route_probe.py:174-182 | - | 9267b6308 | With no model pool configured, routing derives no candidate, resolve_route returns human without selecting a model, and a lane with no qualifying candidate is dropped rather than filled by a substitute, so no code, diff, metadata or evidence leaves for a provider. GitHub, as the platform under review, is not an external provider in CL-026's sense. |
| RQA-NFR-029 | full gap | not built | scripts/config.py:27-28; U-POLICY-10; scripts/panel.py:576-582; search S6 | - | 9267b6308 | No per-change control exists: search S6, shared with RQA-NFR-013 and RQA-NFR-023, finds no send-permission key at any scope, and the candidate-selection path at scripts/panel.py:576-582 filters on capability and effort only, reading no per-PR flag before a candidate is invoked. The RQA-NFR-023 edge recorded in round 1 is withdrawn: today's non-empty repo-local pool already supplies the repository-otherwise-permits precondition this row's fit criterion needs, so a per-change deny gate is buildable against the configuration that exists and the precedence is not forced under any of section 9's three categories. |
| RQA-NFR-015 | partial gap | not built | U-RESILIENCE-15; U-VERDICT-07; scripts/common.py:570-572; scripts/panel.py:598-616; scripts/runners.py:6-10; search S10 | - | 9267b6308 | Untrusted content is nonce-delimited in the evidence envelope and every reviewer invocation is flag-enforced read-only, so an embedded instruction cannot reach GitHub or the filesystem and cannot set an evidence state directly. The prompt, quoted in full at scripts/panel.py:598-616, names the envelope path and says nothing about the status of what it contains, and search S10 finds no injection-handling code anywhere under scripts/, so the review's own judgement is unprotected at every authority level. |
| RQA-NFR-016 | full gap | not built | U-VERDICT-04; scripts/findings.py:88-121; scripts/panel.py:598-616; search S10 | - | 9267b6308 | Nothing detects or records an attempt to induce a clean review or a fabricated evidence state: search S10's single hit under scripts/ is prompt text asking the reviewer to look for injection vulnerabilities in the code under review, the opposite direction, and extract_findings records only what a reviewer model reported. The question this row governs - is this pull request crafted against the reviewer - is posed nowhere, so nothing decides it wrongly and this is silence rather than conflict, the same reading and the same degree as RQA-NFR-028's authenticity question and RQA-NFR-024's credential-scope question. Split-AC sibling of RQA-NFR-015 under CL-055 - the clause is met only when both close. |
| RQA-NFR-017 | conflicting | built contrary | U-AUTHORITY-01; scripts/authority.py:32-34; scripts/dispatcher.py:1316; scripts/advisory.py:154; scripts/approval_evaluate.py:151; scripts/dispatcher.py:941; scripts/action_gate.py:64; scripts/github_mutate.py:99-113; search S4; search S3; search S12 | - | 9267b6308 | The code's activity set is not the requirement's: search S12 quotes ACTIVITIES at scripts/authority.py:32-34 as review, comment, approve, request_changes, triage and fix, so fix is the code's remediate, triage has no counterpart in the requirement, and merge is absent from the set entirely rather than present and disabled. Of the five activities that do map, only three are ever enforced: search S4 returns every mode_for and can_act call under scripts/ outside the definitions themselves - comment at advisory.py:154, approve at approval_evaluate.py:151, request_changes at dispatcher.py:941 and action_gate.py:64 - and no call site passes review, fix or triage. Those three are declared and resolvable by mode_for, so setting authority.review to disabled has no effect: dispatcher.py:1316 runs the reviewer panel with no authority check on the review activity at all, gated only by the separate canary and lane mechanism. That is a reachable execution performing a named activity in defiance of its own authorisation setting, which is the outcome this requirement forbids. Note also that can_act's repo_hard_gate_ok defaults True, so a caller that omits it still gets a live mutating action authorised. |
| RQA-NFR-018 | conflicting | built contrary | scripts/dispatcher.py:1584-1593; scripts/dispatcher.py:1567-1571; scripts/dispatcher.py:1600; scripts/snapshot.py:117-119; U-POLICY-02; U-POLICY-04; U-DISPATCH-01; U-DISPATCH-09; U-POLICY-12 (comparison baseline, not a mapping) | - | 9267b6308 | Two reachable executions produce the forbidden widening, both in resolve_snapshot. First, when route material has changed the function builds a shadow clamp into effective_cfg (approval.mode, approval_enabled, live_canary_approved and authority.approve all forced to shadow), passes effective_cfg to build_snapshot, and then, on a SnapshotError raised for an absent or unresolvable policy section (scripts/snapshot.py:117-119), returns the unclamped local_cfg instead - so an unreadable policy hands the job whatever approve authority the live config carries, where a resolvable one would have returned the clamped config the snapshot was built from (dispatcher.py:1600 returns snap.config, which is the config object build_snapshot was handed) and held it at shadow. Second, an in-flight job whose pinned snapshot is no longer archived resumes on the caller's current config rather than the narrower authority it was pinned to. A malformed inline policy is genuinely caught earlier at config load and the subcommand refuses outright, and the other fail-closed paths hold - unreadable file, invalid JSON, discontinuous risk bands, capability probe reducing only - but a met majority does not outrank a reachable forbidden outcome. U-POLICY-12 is cited as a comparison baseline, not as a unit mapped to this requirement: after the no-nearest-fit ruling its requirements cells all read -, its trigger is a well-formed deliberate edit to configured route material rather than a malformed or unreadable policy, and its direction is narrowing rather than widening, so it cannot be evidence that this requirement is met or breached. What it corroborates is that the clamp the first execution above discards is a live gate on the same code path - model_registry marks a changed scope shadow_locked at scripts/model_registry.py:133-138 and resolve_snapshot acts on that flag - rather than a hypothetical one; the degree rests on the resolve_snapshot ranges alone and does not move if the citation is dropped. The ranges over that clamp are not a duplicated citation of one behaviour. This row cites dispatcher.py:1584-1593, running from the effective_cfg binding through the clamp, the build_snapshot call that raises, and the except branch at :1592-1593 that returns local_cfg - the discard, which is the whole conflict. U-POLICY-12's second row cites dispatcher.py:1579-1590, running from the observe_runtime_routes call that produces shadow_locked through the last clamp assignment - the lock, without the discard. They overlap on :1584-1590 because both claims pass through the clamp; each range decides its own claim and neither is a correction of the other. |
| RQA-NFR-024 | full gap | not built | U-AUTHORITY-02; scripts/github_auth.py:103; scripts/github_auth.py:197; scripts/common.py:97-111; U-DISPATCH-09; search S5 | - | 9267b6308 | Nothing inspects the credential's granted scopes: search S5 returns no match under scripts/ for any scope-inspection term, and names the incidental sense of the word scope in the tree (SQLite column keying for cadence and circuit breakers). The capability probe reads the repository's own returned permissions object (pull/triage/push/admin role flags) and can only reduce configured authority; that answers a different question and is progress toward the obligation rather than one complete obligation of it, for which methodology section 5 gives no credit. One ambient token from GITHUB_TOKEN, GH_TOKEN or gh auth token serves every managed repository, so no per-repository scope shape is established anywhere. The remediation-push and merge-after-review half cannot be exercised either, since neither operation exists to be configured. Silence, not conflict: the question of what scopes the credential carries is posed nowhere, the same reading and the same degree as RQA-NFR-028 and RQA-NFR-016. Contrast RQA-NFR-030, whose ceiling IS decided by a reachable branch. |
| RQA-NFR-025 | fit | - | U-RESILIENCE-10; scripts/common.py:97-111; scripts/config.py:203-205; scripts/config.py:409-423; U-POLICY-01 | - | 9267b6308 | The only credential the system takes in is a GitHub token from the environment or gh. find_secret_keys detects any token-, key-, password- or secret-shaped key anywhere in the config and validate_config turns a non-empty hit list into an issue, which is what refuses the config at load and at onboarding, so no deploy key, relay or VPS credential can enter that way either. Runner CLIs authenticate through the operator's own sessions, which the system neither holds nor reads. |
| RQA-NFR-026 | partial gap | not built | U-AUTHORITY-01; scripts/authority.py:44; scripts/authority.py:88-121; scripts/authority.py:149-151; U-DOCS-29; U-DOCS-28; search S3; search S12 | - | 9267b6308 | defaults() returns disabled for every activity, DEFAULT_MODE is disabled, and mode_for returns disabled for an unrecognised activity, an absent authority section or a dict matching nothing - so in the unconfigured deployment this row's fit criterion names, every activity the code declares is off, and the dispatcher refuses every subcommand outright without a valid repo-local config. Merge is a different case and the row does not claim otherwise: search S12 quotes ACTIVITIES at scripts/authority.py:32-34 and merge is not a member of it, so merge is not an activity that defaults off - it does not exist as an authority activity at all, and search S3 shows no merge operation exists on any path for it to authorise. The five activities that do exist default to disabled exactly as this requirement demands; that met portion is what the citations above establish. Once a deployment IS configured, review, fix and triage modes are never consulted (search S4) - a separate-authorisation failure carried at degree conflicting on RQA-NFR-017 rather than hedged here. NFR026-MERGE-VACUOUS was settled by the maintainer on 2026-09-08: an activity the system cannot perform at all does not count as defaulting to disabled. The degree changed from fit to partial gap and the root cause from - to not built, on his reasoning as he gave it: RQA-NFR-026 names six activities and obliges each to default to disabled. Five exist in ACTIVITIES and do default to disabled via DEFAULT_MODE, which the row already establishes correctly. merge is not a member of ACTIVITIES at all, so it cannot be said to default to anything — the obligation is not met for it, it is vacuously unevaluable. Under §5, code implementing some but not all of a requirement's obligations, compatibly rather than contradictorily, is partial gap; absence is not contrary, so this is not conflicting. Treating the row as fit would rest a satisfied requirement on a vacuous truth, which is the same defect this project has refused three times already — the nfr.md "0 pairs, NOT APPLICABLE, this is not a clean bill" wording, gapcheck's DELIBERATELY NOT CHECKED note, and check 3's own 72-citation disclosure. A green result carrying an unchecked premise is worse than no result. Cross-reference RQA-FR-029 and RQA-NFR-008, which record the same underlying absence from their own angles; recording it here too is correct, since degrees are per requirement. One consequence to keep straight, because it is the distinction the ruling turns on: the fail-closed safety goal is met in practice for merge, since a capability that is absent cannot be exercised, and the requirement is nonetheless unmet. That matters because RQA-FR-029 requires merge be configurable in both directions, which absence cannot deliver either. |
| RQA-NFR-030 | conflicting | built contrary | scripts/common.py:97-111; U-AUTHORITY-02; scripts/github_auth.py:103; search S5 | - | 9267b6308 | The contrary execution is github_token's credential selection: with neither GITHUB_TOKEN nor GH_TOKEN set it shells out to gh auth token and adopts the operator's own user-wide credential, which can carry permission on every repository that operator can reach - including repositories the system does not manage, which this requirement forbids outright. That is a specific reachable mechanism choosing the credential, not an absent ceiling: satisfying the row means this path must stop returning that token. Search S5 additionally establishes that no code inspects granted scopes, and there is no per-repository credential. The floor half sits on RQA-NFR-024, which is full gap because nothing there decides anything - it simply never checks. |
| RQA-NFR-011 | fit | - | U-AUTHORITY-09; U-AUTHORITY-10; U-AUTHORITY-11; scripts/github_query.py:478-503; scripts/github_rest.py:60-90; search S9 | - | 9267b6308 | GitHub is the platform the code addresses - a GraphQL inventory read, an allowlisted per-PR REST surface, and a fixed GraphQL review-mutation registry, all reachable from dispatcher subcommands - and search S9 finds one mention of another forge in the tree, a changed-path pattern classifying a .gitlab-ci.yml file inside a reviewed repository as CI configuration, which is not support for a second host. The row is read as the platform-support obligation its shall statement makes; lifecycle shortfalls carry their own degrees on their own rows rather than being rolled into this one. NFR011-LIFECYCLE was settled by the maintainer on 2026-09-08, and his ruling confirms that reading rather than changing it: the escalation is closed and nothing about this row moves - the degree stays fit, the root cause stays -, the evidence is unchanged, and the sentence before this one stands exactly as it was written. His reasoning, as he gave it: RQA-NFR-011's own fit criterion settles it — a system supporting GitHub review as the specification requires satisfies the row regardless of whether it also supports a second platform, since C8 and Non-goal 1 release cross-SCM support as out of scope rather than prohibiting it. Lifecycle shortfalls carry their own degrees on their own rows and are not rolled into this one; rolling them in would double-count them and make one row's degree depend on another's, which §5's one-degree-per-requirement rule forbids. Both things are true here and both are said deliberately: the escalation is closed, and the row is unchanged - the marker was answered, not dropped. |
| RQA-NFR-014 | full gap | not built | scripts/runners.py:164-171; scripts/runners.py:138-157; scripts/runners.py:6-10; U-DISPATCH-25; config.example.json:29-103; search S7; search S12 | - | 9267b6308 | RQA's own code is standard-library-only Python with no third-party dependency, so it is itself freely usable; the gap is the reviewer transport, which is mandatory for any review. ADAPTERS declares exactly three runners - omp, claude and codex, quoted in search S12 - adapter_for raises for every other, search S7 finds no plugin or entry-point path admitting a fourth, and search S12 also quotes the six provider_family values the shipped example configures, all of them vendor subscriptions or metered APIs. The claim is scoped to what those citations carry - the fixed transport set and the fact that no route this estate ships or documents is free and open-source - and not to the licence of the CLI wrappers themselves, which nothing here establishes; round 2's paid-or-hosted-access wording is withdrawn for the same reason round 1's proprietary-CLIs wording was. The RQA-FR-030 edge recorded in round 1 is withdrawn: a free path could be opened by adding one more built-in adapter over a free, self-hosted model without harness admission changing at all, so the precedence is not forced under any of section 9's three categories. |
