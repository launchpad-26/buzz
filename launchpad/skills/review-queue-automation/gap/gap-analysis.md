# RQA fit/gap analysis

The entry point to the #2070 analysis. It says what this estate is, where it
stands against the frozen requirements, what a transition has to preserve, and
where every other part of the analysis lives.

Revision under analysis: `9267b6308714454a3b987622d90cda03a8972827`
(short `9267b6308`). Every claim, count and citation anywhere under `gap/` is a
claim about the tree at that revision and nothing else.

Paths are relative to `launchpad/skills/review-queue-automation/`, as every path
under `gap/` is ([`methodology.md`](methodology.md)).

---

## 1. What this is and how to read it

Issue #2070's objective, in its own terms:

> A fit/gap analysis and a re-runnable gap register recording, for every
> requirement, its gap degree, root cause and evidence, and for every tracked
> file in the assessed estate a recommended disposition.

This document is **synthesis**. It does not re-tabulate the register and it
opens no second evidence base: every behavioural claim below is already
evidenced under `gap/evidence/` and is cited by its disposition-unit id
(`U-<CLUSTER>-NN`). A few claims are this document's own — the transition
account in §6, and one schema fact in §4 — and each of those carries its own
`path:line`.

### Where each part of the analysis lives

| # | Definition-of-done item | Where it is answered |
|---|---|---|
| 1 | A manifest pins every tracked file at a named revision and states the count | [`manifest.md`](manifest.md) — 135 rows, revision and reproducing `git ls-tree` command at the top |
| 2 | The disposition unit is defined, including how a multi-responsibility file splits | [`methodology.md`](methodology.md) §4, with the `scripts/cadence.py` worked example |
| 3 | Every manifest file maps to at least one unit; groups list members and one shared rationale | [`clusters.md`](clusters.md) partitions the 121 assessed files; `gap/evidence/*.md` name every file in a unit, with `Files:` and a `Rationale:` for multi-file units |
| 4 | The assessed scope distinguishes exclusion from omission | [`manifest.md`](manifest.md) "Assessed scope", restated in §2 below |
| 5 | Current state described from evidence, file-and-line for every behavioural claim, nothing resting on documentation where doc and code could disagree | `gap/evidence/*.md` (seven files); [`methodology.md`](methodology.md) §3 rules 1–4 and 6; summarised in §3 below |
| 6 | The future state is the requirements specification; no requirement added, reworded or dropped | [`methodology.md`](methodology.md) §1; `requirements/**` is excluded from assessment for exactly this reason (§2) |
| 7 | Every requirement carries a defined gap degree | [`methodology.md`](methodology.md) §5; `gap/register/{br,fr,nfr}.md` — 14 + 39 + 33 = 86 rows |
| 8 | Every non-`fit` gap carries a root cause from a defined set | [`methodology.md`](methodology.md) §6; the `root cause` column of the three registers |
| 9 | Every unit carries a disposition following from its root cause and naming requirements served or failed | [`methodology.md`](methodology.md) §7; `gap/dispositions/*.md` — 162 units |
| 10 | No `keep`/`salvage` on the ground that it exists, has tests or works today | [`methodology.md`](methodology.md) §7's justification rule; enforced per unit in `gap/dispositions/*.md` |
| 11 | Salvage named at mechanism level, not file level | [`methodology.md`](methodology.md) §7 ("`salvage` names a mechanism, not a file"); the 18 `salvage` units |
| 12 | Transition needs: what stays operable, what is taken out of service, what carries over | **§6 of this document — no other artefact carries it** |
| 13 | A recorded rerun procedure that re-inventories and fails on the named conditions | §7 of this document; the script is `gap/validate.py` |
| 14 | Register keyed by requirement id, recording the revision each row was evaluated at, updated in place | `gap/register/{br,fr,nfr}.md` — "Why the register is keyed by requirement ID" and "How a row is updated"; §7 below |
| 15 | Gaps carry a dependency ordering; no priority ranking | [`methodology.md`](methodology.md) §9; the `depends on` column; §5 below |

Read in this order if you are new to it: §2 here, then
[`methodology.md`](methodology.md), then §§3–6 here, then the register for the
requirement you care about, then that requirement's units in
`gap/evidence/` and `gap/dispositions/`.

---

## 2. Assessed scope

Restated from [`manifest.md`](manifest.md) so this document stands on its own.

- **135 files** are tracked under `launchpad/skills/review-queue-automation/` at
  `9267b6308`, reproducible with
  `git ls-tree -r --name-only 9267b6308714454a3b987622d90cda03a8972827 -- launchpad/skills/review-queue-automation`.
- **121 are assessed** — `SKILL.md`, `OPERATORS.md`, `onboarding/SKILL.md`,
  `config.example.json`, and everything under `references/`, `schemas/`,
  `scripts/` and `tests/`. By area: 48 under `scripts/`, 63 under `tests/`
  (61 `test_*.py` plus `conftest.py` and `run_all.py`), and 10 root, docs and
  schema files. 48 + 63 + 10 = 121.
- **14 are excluded** — everything under `requirements/`, which is the ten
  top-level files of the frozen #2069 specification plus the four under
  `requirements/adr-drafts/`.
- 135 − 14 = 121.

**Why the 14 are an exclusion and not an omission.** They are this analysis's
**future state, not its subject**. The requirements specification is the
standard the estate is measured against; measuring it against itself is
meaningless, and disposing of it would be editing the specification, which
#2070 places out of scope. They are read constantly — every register row is
keyed by an id defined there — and assessed never.

**Exclusion is recorded, not assumed.** Every one of the 135 tracked files has a
row in [`manifest.md`](manifest.md), and every excluded row carries a non-empty
reason. A tracked file with no row is a defect in that document, not a silent
judgement here.

**The 121 are partitioned, not sampled.** [`clusters.md`](clusters.md) assigns
each of them to exactly one of seven file-disjoint clusters — `queue` 18,
`dispatch` 11, `policy` 18, `verdict` 18, `authority` 21, `resilience` 17,
`docs` 18; 18 + 11 + 18 + 18 + 21 + 17 + 18 = 121 — and every file in a cluster
is named by at least one of that cluster's disposition units.

---

## 3. The current state, in summary

162 disposition units describe this estate: `queue` 14, `dispatch` 26,
`policy` 14, `verdict` 21, `authority` 12, `resilience` 17, `docs` 58;
14 + 26 + 14 + 21 + 12 + 17 + 58 = 162. What follows is their shape, by cluster
remit. Every claim is the cited unit's, established in `gap/evidence/`.

**It detects work and holds it.** A GraphQL inventory read enumerates pull
requests (U-AUTHORITY-10); reconciliation creates at most one job per exact
`(repo, number, head, lane)` key and an existing row for that key blocks a
second (U-QUEUE-01), on an identity that is a stable hash of those four inputs
(U-RESILIENCE-13). A head change supersedes the stale job and any pending
approval request (U-QUEUE-02). Concurrency is held off two ways: a
GitHub-verified assignee lease (U-QUEUE-03) invoked with a guaranteed release
around one dispatch (U-QUEUE-04, U-DISPATCH-10), and an exclusive,
crash-recoverable runtime lock on the state directory (U-DISPATCH-02). A
launchd timer fires a tick per configured lane and repo root (U-QUEUE-08);
the interval is chosen adaptively and persisted rather than typed by hand
(U-QUEUE-05), with config-reload freshness (U-QUEUE-06) and per-scope isolation
(U-QUEUE-07). Job status moves through a validated transition table
(U-QUEUE-11).

**It is configured, not coded, per repository.** Config is repo-local and
version-control-isolated (U-POLICY-01), normalised on load and re-read from the
live path on every call (U-RESILIENCE-09), validated fail-closed
(U-POLICY-02), with policy-as-data versioned and content-hash pinned
(U-POLICY-04) into a snapshot a job pins atomically for its lifetime
(U-QUEUE-09, U-QUEUE-10, U-DISPATCH-09). Policy is derived from config and
never invented (U-POLICY-05). Onboarding writes a valid starter config and
never overwrites one (U-POLICY-06).

**It plans, routes and runs a review panel.** Activities are planned
deterministically from observable PR facts, each selection and omission
carrying a recorded reason (U-DISPATCH-24). A named reasoning strategy is
selected by a fixed specificity order (U-POLICY-08) and the execution mode is
sized from the assurance profile (U-POLICY-09). Routing is subscription-first
over the configured pools with an explicit, non-inventive fallback ladder
(U-POLICY-10, U-RESILIENCE-03), route identity resolved through an alias
registry (U-POLICY-11) and probeable ahead of any review (U-POLICY-13);
candidate families are kept distinct (U-POLICY-14). Three runner adapters
invoke a reviewer read-only and auditably (U-DISPATCH-25). Evidence for one PR
is bundled fail-closed (U-VERDICT-07) and untrusted content is nonce-enveloped
(U-RESILIENCE-15). Verdict text is parsed and fence-normalised (U-VERDICT-01),
schema-validated with contradiction detection (U-VERDICT-02), and the
machinery — not the model — attests what ran (U-VERDICT-11). The panel runs to
a completeness predicate (U-VERDICT-12) over a qualified candidate pool
(U-VERDICT-09, U-VERDICT-10) with an assurance escalation ladder
(U-VERDICT-08) and a budget reservation gate before any spend (U-DISPATCH-12,
U-RESILIENCE-01).

**It judges, then decides what it is allowed to do.** Findings are extracted
behind an evidence-completeness filter (U-VERDICT-04) and blocking requires
corroboration by two provider families or a cited failing check
(U-VERDICT-05). Risk is scored as a maximum RPN and banded (U-VERDICT-13),
protected paths matched deterministically from policy (U-VERDICT-14), and
achieved assurance derived from evidence completeness against a required floor
(U-VERDICT-18). Auto-approval is a fail-closed conjunction over 22 named gates
(U-VERDICT-16); request-changes has its own deterministic action gate
(U-AUTHORITY-04). Authority is resolved per repo and per activity
(U-AUTHORITY-01), clamped by proven GitHub capability (U-AUTHORITY-02,
U-DISPATCH-09), and evaluated to a disposition deterministically
(U-AUTHORITY-03). Acting on GitHub goes through one fixed-event mutation
registry, deduplicated by a deterministic mutation id (U-AUTHORITY-09), with
the APPROVE path guarded by mandatory pre- and post-checks (U-AUTHORITY-08).
Where a human is required, a durable SQLite request queue holds the ask
(U-AUTHORITY-05), a CLI inspects and decides it (U-AUTHORITY-06), and a guarded
executor resumes on that authorization (U-AUTHORITY-07).

**It records and explains itself.** Every decision, action, assurance
computation and finding is appended to a ledger (U-DISPATCH-20,
U-RESILIENCE-06); one otel-jsonl event marks each orchestration milestone
(U-DISPATCH-19) over a locked, crash-safe writer (U-RESILIENCE-08,
U-RESILIENCE-14); and one read-only command reconstructs a job's outcome from
that record without contacting GitHub or a model (U-RESILIENCE-07). Failures
are classified by a typed error taxonomy (U-RESILIENCE-04), contained per job
(U-DISPATCH-21) and per sweep batch (U-DISPATCH-22), with a per-scope circuit
breaker and cooldown (U-RESILIENCE-02) and crash recovery that releases
stranded leases without re-deciding anything (U-DISPATCH-07).

**Four things it does not do, each established by the unit's own evidence rather
than announced in its name.** The author-triage remediation cycle exists as
complete code that no product entrypoint reaches (U-DISPATCH-26, U-DOCS-13,
U-DOCS-53). The bounded-change aggregator and the versioned
`risk-assessment.json` envelope are likewise reachable only from tests
(U-VERDICT-15, U-VERDICT-17). The disposition metadata registry has no consumer
anywhere outside its own module, and its only callers in the tree are three test
functions in one module belonging to another cluster (U-RESILIENCE-17, whose
coverage unit U-DOCS-38 goes with it). And the degradation ladder helper has
no product caller either (U-DISPATCH-23). Under
[`methodology.md`](methodology.md) §2.3 a behaviour whose only callers are tests
is not implemented, so none of these is part of what the system does.

---

## 4. The gap, in summary

### By degree, and by root cause

86 requirements, one row each.

| degree | BR | FR | NFR | total |
|---|---|---|---|---|
| `fit` | 1 | 9 | 9 | **19** |
| `partial gap` | 9 | 10 | 6 | **25** |
| `full gap` | 2 | 13 | 14 | **29** |
| `conflicting` | 2 | 7 | 4 | **13** |
| total | 14 | 39 | 33 | **86** |

| root cause | BR | FR | NFR | total |
|---|---|---|---|---|
| `not built` | 8 | 21 | 17 | **46** |
| `built contrary` | 2 | 7 | 4 | **13** |
| `built then orphaned` | 1 | 2 | 3 | **6** |
| `built against superseded intent` | 2 | 0 | 0 | **2** |
| `-` (`fit`) | 1 | 9 | 9 | **19** |
| total | 14 | 39 | 33 | **86** |

The shape is: **most of the gap is absence, not error.** 46 of the 67 non-`fit`
rows are `not built` — a required behaviour whose subject matter the code never
poses as a question. Only 6 rows are code that exists and is unreached, and
only 2 are reachable code implementing an earlier intent. The remaining 13 are
the rows where the code decides the matter and decides it the way the
requirement forbids.

**A `fit` row does not make its source clause covered.** Degrees are per
requirement; a clause that produced several requirements is met only when all
of them are ([`methodology.md`](methodology.md) §8). `gap/register/fr.md` records
three clauses where a `fit` child sits beside an unmet sibling — CL-028, CL-031
and CL-039 — none of which is covered.

### The findings a reader must not miss

1. **No finding carries a category, anywhere.** The verdict schema sets
   `additionalProperties: false` on the finding object and then fixes exactly
   five finding keys, with no category among them
   (`schemas/reviewer-verdict.json:16-23`). This is the single most
   load-bearing absence in the analysis: it makes `RQA-BR-005` and
   `RQA-FR-008` `full gap`, and it is the prerequisite named by more rows than
   any other (four in-edges, §5).
2. **The whole remediation family has no reachable behaviour.** `RQA-BR-006`,
   `RQA-FR-017`, `RQA-FR-018`, `RQA-NFR-007`, `RQA-NFR-020` and `RQA-NFR-021`
   rest on `scripts/worktree.py`, which implements create/commit/push/clean
   completely, refuses force-push and refuses any branch other than the
   configured head — and which nothing under `scripts/` calls. Documentation
   describes the behaviour as something the system does (U-DOCS-13). This is
   [`methodology.md`](methodology.md) §2.4's worked example and the reason
   `built then orphaned` exists as a cause.
3. **No merge capability exists at all.** `merge` is not one of the six
   authority activities and the mutation registry has no merge entry, so
   neither direction of `RQA-FR-029`'s biconditional is exercisable, and
   `RQA-NFR-008` and the merge half of `RQA-NFR-017` fail for the same reason.
   `RQA-NFR-026` is the same absence read from a third angle, and the
   difference matters rather than flattening into the others: five of the six
   activities it names do default to disabled, so it is a `partial gap` on the
   `merge` obligation alone — an activity that does not exist cannot be said to
   default to anything (the maintainer's 2026-09-08 ruling, §8).
4. **Three declared authority activities are never consulted.** Of the six
   activities the code declares, only `comment`, `approve` and
   `request_changes` are ever passed to the authority check; `review`, `fix`
   and `triage` are configurable and read by nothing. That is what makes
   `RQA-NFR-017` `conflicting` rather than merely short.
5. **Every ledger-write failure is discarded.** `_ledger_record`'s bare
   `except` sits on the authoritative-action paths — the approve action, the
   request-changes action, the decision record — so a job completes with a
   knowingly incomplete provenance record (`RQA-NFR-010`, U-DISPATCH-20). It is
   also why `RQA-BR-001`'s auditability obligation is unmet on the failure
   path.
6. **Three separate questions are never posed.** Whether a stored provenance
   row is authentic (`RQA-NFR-028`), whether a pull request is crafted to
   induce a clean review (`RQA-NFR-016`), and what scopes the credential
   carries (`RQA-NFR-024`). All three are `full gap` rather than `conflicting`,
   because silence is never a conflict ([`methodology.md`](methodology.md) §5)
   — closing them adds a check where none exists.
7. **`RQA-FR-035` cannot be settled from the tree, and was settled off it.** It
   is satisfied or not by GitHub issue state, which a tree-scoped analysis
   cannot observe, so it is recorded `full gap` on the evidence available. The
   maintainer queried the tracker himself on 2026-09-08 and found #109, #535
   and #536 all open and none re-parented, which confirms that degree; his
   command and its output are in the row (§8, `gap/register/fr.md:210`). The
   requirement is closable only by action on the issue tracker, so no
   disposition unit serves it.

### The `conflicting` rows — where the transition must *remove* behaviour

These 13 are the rows where satisfying the requirement means a reachable
execution has to stop producing the outcome it produces today. Every one
carries root cause `built contrary`. Grouped by the mechanism the registers
name:

| mechanism | rows | what must stop |
|---|---|---|
| Live mode escalates on **any** failed gate, including the purely mechanical `checks_complete_ok`, `rate_limit_ok` and `audit_writable` — enqueuing a human request, delivering a notification for it, and parking the job in `human_approval_pending` with nothing that re-drives it | `RQA-BR-010` (the parking), `RQA-BR-013` (the interruption) | A PR needing no judgement must stop requiring a human, and a routine gate failure must stop going out through the same transport as a protected-trigger denial |
| The head-checks gate treats an **inherited** failing check as the pull request's own blocker; only the base ref *name* is ever read | `RQA-FR-014`, `RQA-FR-036` | The inherited failure must stop contributing to a blocking disposition — a removal, not an addition |
| The human-resume path writes a decision row already marked `eligible` **from the authorization alone**, without re-running the gates that failed, with a basis that may be the empty string, reaching `completed_auto_approved` and a submitted APPROVED | `RQA-FR-011`, `RQA-FR-037` | That bypass must be constrained or refused |
| `budget.reserve` returns a permissive decision when a configured bound has been reached: the `per_model_daily_tokens` axis is configured, defaulted, validated and advertised but never queried, and the two enforced axes compare strictly greater, so exact equality passes | `RQA-FR-022`, `RQA-FR-039` | A run that has reached a configured bound must stop proceeding to a successful outcome |
| A review whose obligations are satisfied terminates in an advisory COMMENT or in `human_required` **without submitting either verdict** whenever the relevant authority is not `live` — which `RQA-NFR-026` makes the default | `RQA-FR-028` | The satisfied review must stop ending without a verdict |
| `_ledger_record`'s bare `except` on the authoritative-action paths | `RQA-NFR-010` | A discarded provenance append must stop being compatible with a completed authoritative outcome |
| A review activity runs without consulting its own authority mode | `RQA-NFR-017` | Activities must stop acting unenforced |
| `resolve_snapshot` builds a shadow clamp for changed route material and then, on a `SnapshotError` for an absent or unresolvable policy section, returns the **unclamped** config | `RQA-NFR-018` | The discarded clamp must stop widening authority |
| `github_token` shells out to `gh auth token` and adopts the operator's own user-wide credential, which can carry permission on repositories the system does not manage | `RQA-NFR-030` | That credential fallback must stop being taken |

`RQA-BR-010`/`RQA-BR-013` and `RQA-FR-011`/`RQA-FR-037` are each one mechanism
seen from two requirements. That is an observation about the pairs, not an
ordering between them: neither register records a dependency edge for it.

---

## 5. Dependency ordering

The register holds **22 `depends on` edges over 86 rows, leaving 72 rows with
no prerequisite, and the graph is acyclic.**
`python3 .workmux/gapcheck.py register <worktree> <class>` verifies that
mechanically and prints it (`dependency graph: 86 rows, 22 edges, 72 with no
prerequisite`), so it is stated here as the fact it is rather than re-derived.

**This is not a priority ranking and #2070 forbids one.** Every requirement in
the frozen specification is mandatory. There is no priority column, no phase, no
wave and no sequencing recommendation anywhere in this analysis
([`methodology.md`](methodology.md) §9).

**What the shape means.** 72 of 86 requirements have no prerequisite at all:
**most of this gap is closable in any order.** The ordering constrains a
minority — 14 rows carry a non-empty cell — and the longest chain in the whole
graph is three rows deep (`RQA-NFR-007` → `RQA-FR-017` → `RQA-FR-008`). There is
no long pole here to schedule around.

**The ordering is a forced one.** An edge survived only if its reason named one
of [`methodology.md`](methodology.md) §9's three categories — **substrate**,
**authority** or **contract** — in those words, one sentence per edge in the
row's `notes`. The 22 split:

- **substrate** (7) — the behaviour acts on a record the prerequisite must
  first write: `RQA-BR-001` → `RQA-FR-012`, `RQA-FR-013`, `RQA-FR-021`,
  `RQA-NFR-028`; `RQA-BR-012` → `RQA-FR-021`; `RQA-FR-017` → `RQA-FR-008`;
  `RQA-NFR-007` → `RQA-FR-017`.
- **authority** (4) — the action is only permitted once the prerequisite's gate
  or bound exists: `RQA-BR-001` → `RQA-FR-011`, `RQA-NFR-022`; `RQA-BR-006` →
  `RQA-NFR-019`; `RQA-FR-029` → `RQA-NFR-017`.
- **contract** (11) — the behaviour is defined against a vocabulary or
  interface the prerequisite fixes: `RQA-BR-002` → `RQA-FR-001`, `RQA-FR-008`;
  `RQA-BR-005` → `RQA-FR-008`; `RQA-BR-006` → `RQA-FR-008`; `RQA-BR-008` →
  `RQA-FR-010`; `RQA-BR-014` → `RQA-FR-010`; `RQA-FR-038` → `RQA-NFR-024`,
  `RQA-NFR-030`; `RQA-NFR-001` → `RQA-FR-030`; `RQA-NFR-002` → `RQA-FR-030`;
  `RQA-NFR-033` → `RQA-NFR-031`.

7 + 4 + 11 = 22.

**What must close first.** Sixteen distinct requirements appear as a
prerequisite. Four carry more than one dependent, and they are where the
ordering actually bites:

| prerequisite | dependents | why |
|---|---|---|
| `RQA-FR-008` (`full gap`, `not built`) | `RQA-BR-002`, `RQA-BR-005`, `RQA-BR-006`, `RQA-FR-017` | The finding category vocabulary. A population like "a finding classified as mechanical" cannot exist until a finding carries a category, and a record-level readability obligation cannot be expressed in terms that do not exist. |
| `RQA-FR-010` (`full gap`, `not built`) | `RQA-BR-008`, `RQA-BR-014` | The per-obligation evidence-state vocabulary — the terms in which "which were examined, and which were verified" can be answered at all. |
| `RQA-FR-021` (`partial gap`, `not built`) | `RQA-BR-001`, `RQA-BR-012` | A consumption figure must exist as a measurement, or at least be marked as not one, before anything can compare it against the policy's stated assurance. |
| `RQA-FR-030` (`full gap`, `not built`) | `RQA-NFR-001`, `RQA-NFR-002` | The published harness interaction contract. There is nothing for a not-previously-used environment to conform to until it exists. |

One edge is already discharged: `RQA-BR-001` → `RQA-NFR-022`, whose target is
`fit`. Two prerequisites are themselves `conflicting` — `RQA-FR-029` waits on
`RQA-NFR-017` and `RQA-FR-038` on `RQA-NFR-030` — so in those two cases the
thing that must happen first is a *removal*.

**Where a reader expects an edge and finds none, that absence was a ruling.**
Edges were dropped when the dependent obligation turned out to have a truthful
realisation independent of the named prerequisite. `gap/register/fr.md` records
eleven such drops with the reason for each — among them `RQA-FR-007` on
`RQA-FR-006` (a record reading "reused = none, regenerated = all" satisfies
FR-007 with no invalidation computation), `RQA-FR-015` on `RQA-FR-014` (FR-014's
own fit criterion declares the classification testable independent of whether it
is persisted), and `RQA-FR-025` on `RQA-FR-008` (a prohibition is satisfiable by
issuing no request at all). `gap/register/br.md` records three more dropped from
`RQA-BR-001`, and `gap/register/nfr.md` four withdrawn (`RQA-NFR-003` and
`RQA-NFR-014` on `RQA-FR-030`, `RQA-NFR-023` on `RQA-NFR-013`, `RQA-NFR-029` on
`RQA-NFR-023`) plus `RQA-NFR-031` considered and not added to `RQA-BR-006`. An
empty `depends on` cell is the correct default, and in these cases it is a
decision with a reason attached.

---

## 6. Transition needs

This section is this analysis's only account of the transition. Every limb is
grounded in named units and register rows.

### 6.1 What must remain operable during the change

These behaviours cannot go dark. Each is reachable today, each is named by the
register as support for a `fit` row or for the met portion of a partial one, and
each has a stated consequence if it stops. A unit appearing here is a statement
that the *responsibility* must stay operable, not that its current
implementation is `keep` — several are `rework`.

| behaviour | units | requirements | if it goes dark |
|---|---|---|---|
| PR detection and per-lane job creation on a stable identity | U-QUEUE-01, U-RESILIENCE-13, U-AUTHORITY-10 | `RQA-BR-007` `fit` | No work is found; nothing else in the pipeline has an input |
| Exclusive claim on a pull request under review — GitHub-verified lease plus local exclusivity | U-QUEUE-03, U-QUEUE-04, U-DISPATCH-10, U-DISPATCH-02 | `RQA-BR-007` `fit` | Two runs review and act on one PR concurrently; `RQA-BR-007`'s "no second review" guarantee fails |
| Unattended, per-repository ticking | U-QUEUE-08, U-QUEUE-06, U-QUEUE-07 | `RQA-FR-031`, `RQA-NFR-004`, `RQA-NFR-005` `fit` | The system requires an operator to run it, contradicting `RQA-BR-010`'s own met half |
| Repo-local config read live, normalised, validated fail-closed, pinned per job | U-POLICY-01, U-POLICY-02, U-POLICY-04, U-RESILIENCE-09, U-QUEUE-09, U-QUEUE-10 | `RQA-FR-004`, `RQA-NFR-005`, `RQA-NFR-025` `fit` | An edited policy stops applying to the next review without a rebuild; an in-flight job stops keeping its pin |
| Off by default in an unconfigured deployment | U-AUTHORITY-01, U-POLICY-02 | `RQA-NFR-026`, met portion of a `partial gap` | The estate's only standing safety property against misconfiguration. The safety *goal* and the *requirement* part company here after the maintainer's 2026-09-08 ruling: the five declared activities do default to disabled, which is what must remain operable; `merge` defaults to nothing because it is not an activity, which is why the row is no longer `fit` and is not something this behaviour can preserve |
| Routing and fallback confined to the configured pools | U-POLICY-10, U-POLICY-11, U-POLICY-13, U-VERDICT-09, U-VERDICT-10, U-RESILIENCE-03 | `RQA-FR-023`, `RQA-FR-024`, `RQA-FR-032`, `RQA-FR-033`, `RQA-NFR-009`, `RQA-NFR-027` `fit` | An unconfigured route can be substituted for a configured one — six `fit` rows fail together |
| Identical inputs give an identical judgement basis | U-DISPATCH-24, U-POLICY-09, U-POLICY-14, U-VERDICT-04, U-VERDICT-07, U-VERDICT-12 | `RQA-FR-002` `fit` | The review stops being reproducible, which every evidentiary row is read against |
| The machinery, not the model, attests what ran | U-VERDICT-11 | `RQA-NFR-022`, `RQA-NFR-032` `fit` | Model-controlled content becomes indistinguishable from attested identity |
| Guarded APPROVE with mandatory pre/post checks, and mutation idempotency | U-AUTHORITY-08, U-AUTHORITY-09 | `RQA-BR-007` `fit` | A duplicate or unguarded authoritative mutation reaches GitHub |
| The deterministic request-changes action gate | U-AUTHORITY-04 | `RQA-FR-009` `fit` | Reviewer severity alone starts deciding a blocking outcome |
| Local-only operation over one state directory | U-RESILIENCE-10, U-RESILIENCE-16, U-DOCS-03 | `RQA-NFR-006` `fit` | Records split across directories and a later command cannot see an earlier job |
| Read-only single-command reconstruction of an outcome | U-RESILIENCE-07 | `RQA-FR-012` (met portion) | The only path by which any past decision can be explained |
| Crash recovery that releases leases without re-deciding | U-DISPATCH-07 | `RQA-FR-038` (met portion) | An interrupted job either strands its lease or replays a decision |

### 6.2 What is deliberately taken out of service

Two kinds: responsibilities recommended `bin`, and reachable behaviour the
`conflicting` rows require to be removed. Both are decisions with reasons
recorded per unit and per row; neither is an accident of the rewrite.

**The 18 `bin` units.** `queue` 2, `dispatch` 3, `policy` 2, `verdict` 4,
`authority` 1, `docs` 5, `resilience` 1; 2 + 3 + 2 + 4 + 1 + 5 + 1 = 18.

| going out of service | units | what is lost, and why it goes |
|---|---|---|
| Operator maintenance commands: `backup`, `cooldown-reset`, `retention` | U-DISPATCH-04, U-DISPATCH-05, U-DISPATCH-06, and their documentation U-DOCS-18, U-DOCS-20 | Three `dispatcher.py` subcommands disappear from the operator surface. No frozen requirement obliges backup/restore, cooldown clearing or retention. Both cooldown stores already return to service on their own deadlines, so the reset command shortened a wait rather than being the path back; retention's careful purge-with-manifest was a mitigation of a risk it introduced, and removing the purge removes both. **A consequence to plan for: artefacts and ledger rows accumulate without bound once the purge goes.** |
| Human notification delivery (file / command transports) | U-AUTHORITY-12 | The push path goes; the durable human-request queue that records the ask does not. `RQA-FR-025` needs only a durable record, and `RQA-BR-013` is the requirement this unit's own reachable code contradicts — it sends a routine gate failure through the same transport as a protected-trigger denial |
| Shadow / calibration operator surface and its sample source | U-VERDICT-21, U-QUEUE-13 | Two commands an operator is instructed to run, and closed-PR ingestion into calibration samples. No requirement in the frozen specification names shadow mode or backtesting |
| Risk machinery nothing reaches | U-VERDICT-15 (bounded-change seven-gate aggregation), U-VERDICT-17 (the versioned `risk-assessment.json` writer, reader and version-mismatch refusal) | Both are reachable only from `tests/test_risk.py`. What is lost is worth naming — the seven-way articulation of "bounded", and a versioned envelope whose reader raises rather than reinterpreting a payload from another version — and neither is a responsibility the specification asks for |
| The disposition metadata registry, and its coverage | U-RESILIENCE-17 (`CATEGORY_META`, `category_meta` and their `authority_impact` vocabulary), U-DOCS-38 (the `test_phase4.py` assertions on that registry) | Split out of U-RESILIENCE-04 on the maintainer's 2026-09-08 ruling and binned. Nothing under `scripts/` outside `errors.py` reads it, and its only callers in the tree are three test functions in `tests/test_phase4.py` — which is why U-DOCS-38 goes with it rather than surviving as coverage of a binned responsibility (§6.3). What is lost is a per-disposition statement of retryability, authority impact and escalation, failing safe for an unregistered disposition — real, but an outcome property provable only where terminal outcomes are minted, not a table other components consult. The typed exception and coarse constants the estate does act on stay with U-RESILIENCE-04 |
| The author-triage verdict schema | U-VERDICT-03 | The only written contract for author-triage output in the tree, including its four-value per-comment classification. No code reaches it |
| Legacy `action` → `completed` transition | U-QUEUE-12 | The register's own worked counter-example for `RQA-FR-034`: justified only as "preserved for existing callers", with no caller named and no code transitioning a job into `action`. Removing it moves the row toward `fit` |
| Route-material shadow lock | U-POLICY-12 | Two waves independently found no frozen requirement obliging it |
| Onboarding runtime-readiness report | U-POLICY-07 | Named a gate; refuses, delays and narrows nothing. No requirement covers it |
| Two test-coverage units | U-DOCS-22 (the whole `tests/test_docs_contract.py` drift suite), U-DOCS-46 (the lease node-id regression check inside `tests/test_repairs.py`) | See §6.3 |

**The reachable behaviour the `conflicting` rows require removed** is the
right-hand column of §4's table, and it is the part of this transition that is
subtractive rather than additive: the mechanical-gate escalation and its
notification, the inherited-check blocker, the human-resume bypass, the
permissive budget reserve, the verdict-less termination of a satisfied review,
the discarded ledger append, the unenforced activity, the discarded shadow
clamp, and the user-wide credential fallback. Each is reachable today, so each
is a **behaviour change a user or operator can observe**, not an internal
cleanup.

### 6.3 What carries over

**State.** All persistence is one SQLite database plus a snapshot archive and
per-job artefact directories. `State._migrate` declares fifteen tables, and
which of them carries over is decided per table, not per database:

| table | `path:line` | carries over? |
|---|---|---|
| `jobs` | `scripts/common.py:231` | **Yes** — the `UNIQUE (repo, number, head_sha, lane)` constraint at `:244` *is* `RQA-BR-007`'s at-most-one-job guarantee (U-QUEUE-01). Plus the `snapshot_hash` column added by migration at `scripts/common.py:375`, which is the per-job pin (U-QUEUE-10) |
| `leases` | `scripts/common.py:246` | **Yes** — exclusivity under `RQA-BR-007` (U-QUEUE-03, U-QUEUE-04) |
| `ledger_entries` | `scripts/common.py:321` | **Yes** — the record `RQA-FR-012`'s reconstruction reads (U-RESILIENCE-06, U-RESILIENCE-07). Carrying the rows over does not close `RQA-NFR-028`: no row carries an integrity field, so authenticity is unverifiable for history as well as for new entries |
| `mutations` | `scripts/common.py:260` | **Yes** — `client_mutation_id` as primary key is the idempotency `RQA-BR-007` rests on (U-AUTHORITY-09) |
| `prs` | `scripts/common.py:221` | **Yes** — the persisted PR-fact cache is the sole source of the observed head used to detect a stale review (U-QUEUE-14) |
| `human_requests` | `scripts/common.py:288` | **Yes** — the durable ask survives even though delivery does not (U-AUTHORITY-05, §6.2). It already carries `decision_actor` at `:311` and `rationale` at `:308` |
| `approval_decisions` | `scripts/common.py:268` | **Yes, but not unchanged.** Its DDL declares exactly `id, job_id, repo, number, head_sha, policy_hash, status, mode, risk_score, created_at, expires_at` (`scripts/common.py:268-281`) — **no actor and no basis column**. That is `RQA-FR-013`'s unmet obligation, so this table needs a migration, not a copy |
| `cadence` | `scripts/common.py:360` | **Yes** — one row per swept scope is what makes `RQA-NFR-004`'s per-scope isolation hold across a short-lived timer (U-QUEUE-07) |
| `etags` | `scripts/common.py:204` | **Yes** — the 304 cache is one of `RQA-FR-020`'s three met reuse classes (U-RESILIENCE-12) |
| `route_qualifications` | `scripts/common.py:282` | **No** — it is the store behind the binned route-material shadow lock (U-POLICY-12) |
| `providers`, `circuit_breakers` | `scripts/common.py:254`, `scripts/common.py:348` | **Yes** — the breaker responsibility is `keep` for `RQA-FR-038` (U-RESILIENCE-02); only the manual reset command goes (U-DISPATCH-05) |
| `canaries` | `scripts/common.py:315` | **Yes** — canary/lane gating is `rework`, not `bin` (U-DISPATCH-11) |
| `cost_ledger` | `scripts/common.py:334` | **Yes as rows, no as a contract.** Its declared columns are `id` plus `recorded_at, job_id, repo, number, model, provider_family, kind, tokens, latency_ms` (`scripts/common.py:334-345`), and the insert writes the latter nine (`scripts/budget.py:223-231`): `kind` separates a reservation row from a spend row and **nothing separates an estimated spend from a measured one**, which is `RQA-FR-021`'s unmet obligation and, through it, `RQA-BR-001`'s and `RQA-BR-012`'s substrate edges (§5) |
| `api_calls` | `scripts/common.py:211` | **Yes** — rate-limit consumption recorded from response headers is `RQA-FR-021`'s met half (U-DISPATCH-13) |

Snapshot archive and per-job artefacts carry over: atomic activation with
last-known-good retention (U-QUEUE-09), content-hashed snapshot identity
(U-QUEUE-10), the locked JSONL trace with exclusive attempt-number allocation
(U-RESILIENCE-08) and crash-safe durable writes (U-RESILIENCE-14) are all
`keep`. With the retention purge binned, they accumulate — see §6.2.

**Configuration.** The repo-local config file and its inline policy carry over
whole: discovery and version-control isolation (U-POLICY-01), normalisation
(U-RESILIENCE-09), fail-closed validation (U-POLICY-02) and policy versioning
with content-hash pinning (U-POLICY-04) are all `keep`, and the tracked
`config.example.json` must stay runtime-shippable (U-POLICY-03). Four groups of
keys do **not** carry over:

- `budget.per_model_daily_tokens` (`config.example.json:182`) — configured,
  defaulted, validated, advertised and never queried; it is half of
  `RQA-FR-022`/`RQA-FR-039`'s contradiction. A replacement either enforces it or
  stops advertising it; carrying it forward unenforced reproduces the finding.
- The `authority` entries for `review`, `fix` and `triage` — configurable and
  consulted nowhere (`RQA-NFR-017`).
- The notification transport keys — the responsibility is binned
  (U-AUTHORITY-12).
- The retention window key — the responsibility is binned (U-DISPATCH-06).

**Test coverage.** The seven clusters' units cite tests as corroborating
evidence throughout; the `docs` cluster additionally holds the cross-cutting
suites and the harness as units in their own right — 37 units whose members are
only test files, disposed `keep` 25, `salvage` 7, `rework` 2, `bin` 3
(25 + 7 + 2 + 3 = 37).

*Coverage that asserts a requirement which survives*, and therefore carries
over as-is: `RQA-NFR-006`'s local-operation coverage (U-DOCS-23, U-DOCS-51),
`RQA-FR-023`/`RQA-FR-024`/`RQA-NFR-009`'s routing and fallback-loop coverage
(U-DOCS-27, U-DOCS-37), and `RQA-NFR-026`'s canary-default coverage
(U-DOCS-28). All five are `keep`. Four stand against `fit` rows; U-DOCS-28
stands against the met portion of a `partial gap` row, since the maintainer's
2026-09-08 ruling moved `RQA-NFR-026` off `fit` for the `merge` activity the
code does not declare — an obligation no canary-default test bears on, so the
coverage carries over unchanged.

*Coverage that asserts behaviour which does not survive*, and therefore must not
be carried over as evidence of anything:

- U-DOCS-22 and U-DOCS-46 are **removed** with their responsibilities
  (documentation-to-code naming checks; the lease node-id representation). No
  frozen requirement maps to either.
- U-DOCS-38 is **removed** with the responsibility it covers, and is the third
  `bin` in that tally: every one of its assertions reads the disposition
  metadata registry `RES04-META-UNREACHED` binned as U-RESILIENCE-17, and
  coverage of a binned responsibility is exactly what this paragraph says must
  not carry over. It read `keep` until re-review; §7 also forbade that
  independently, since the one requirement it names, `RQA-NFR-010`, is
  `conflicting`.
- U-DOCS-56 (`tests/test_e2e_outcomes.py`) is `rework`: it **pins the advisory
  terminal outcomes `RQA-FR-028` forbids** for a satisfied review, so as written
  it defends a reachable contrary path. Its exact
  successfully-recorded-versus-attempted mutation accounting is worth keeping;
  its terminal expectations are not.
- U-DOCS-53 (`tests/test_integration.py`) is `salvage`: it exercises worktree
  create/clean under a fake runner only, and that **must not be read as product
  reachability** — `RQA-NFR-020` is a `full gap`, `built then orphaned`.
- U-DOCS-40 (`tests/test_phase4.py`) is `salvage`: attribute-existence checks
  cannot prove the shadow entrypoints are read-only or enforce the cutoff, so
  the current suite must not stand as coverage of that guarantee.
- U-DOCS-30 and U-DOCS-31 (`tests/test_phase1.py`) are `salvage`: isolated
  policy-validation and snapshot-activation coverage must not stand in for the
  snapshot-resolution authority boundary `RQA-NFR-018` shows to be broken.
- U-DOCS-13 is the documentation counterpart rather than coverage, and it is
  `rework` for the same reason: the claim that the author-triage lane performs
  isolated remediation must go, while the isolated, head-pinned, non-force-push
  intent is retained.
- U-DOCS-24 (`tests/conftest.py`) is `salvage`: its guards are dead under the
  tracked runner, but the mechanism — a deliberately non-token-shaped credential
  paired with a socket constructor that raises on construction — is what turns a
  suite regressing into a live GitHub call into a deterministic failure. Carry
  the mechanism, not the file.

---

## 7. The rerun procedure

This analysis is re-runnable at a later revision. The command is:

```
python3 launchpad/skills/review-queue-automation/gap/validate.py
```

It re-inventories the manifest and the requirements set **at the revision
`manifest.md` records** and exits non-zero on any structural failure in checks
1–3 or any open escalation in check 4. The four conditions the contract fixes,
and which a later reader should treat as the floor rather than the whole list —
the checker's own structural checks additionally cover manifest integrity that
no condition below names:

1. any assessed file maps to no disposition unit;
2. any requirement has no register row;
3. any row's recorded `revision` predates the last commit touching a file it
   cites;
4. any `PENDING-HUMAN` marker remains.

**A later evaluation updates the register in place.** It does not write a new
document. For each row: re-read the requirement in the frozen specification and
the code it concerns at the new revision, re-apply the "implements" test
([`methodology.md`](methodology.md) §2), reset `gap degree`, `root cause`,
`evidence` and `depends on` from what that test found, and **bump that row's
`revision` to the short SHA it was evaluated against**. The `revision` cell
records when the row was last *evaluated*, not when the file was last touched,
so a row still reading an older SHA than its siblings is a row nobody
re-checked — that is the cell's entire purpose. Rows are never deleted and the
table is never reordered or restructured; a requirement that turns out to be met
has its degree changed to `fit`, not its row removed
(`gap/register/{br,fr,nfr}.md`, "How a row is updated").

**A red run has two possible meanings and they are separated.** Check 4 —
open escalations — is reported under its own heading, separately from the
structural checks 1–3. A reader seeing a non-zero exit must read which check
failed: 1–3 are structural failures in the artefacts and must be fixed; 4 is the
analysis correctly refusing to present itself as complete while a human has not
answered. **On this branch check 4 passes.** The maintainer answered all six
outstanding questions on 2026-09-08 (§8); each answer was applied to the
artefact it lands in and each marker was removed with it, so no `PENDING-HUMAN`
escalation is open anywhere under `gap/`. This is the first revision at which
`gap/validate.py` exits 0.

**Distinct ids and marker occurrences are counted separately — check 4 lists
lines, not questions.** The check reports **every occurrence** of a marker with
its `file:line`, and a marker is quoted wherever an open question has to be
findable, so the occurrence count is normally the larger of the two: while these
six escalations were open they stood at fourteen occurrences over six distinct
ids, six of the occurrences being in this document because §8 then quoted each
marker once. That two-number reading is a standing property of the checker and
the reason its output is not read as a single figure; it was never a fact about
those six items in particular. It now reports **zero distinct ids and zero
occurrences**, and the check itself is unchanged: the escalations were answered
and their markers removed, which is precisely the state check 4 exists to
detect. It remains able to report an escalation the moment one is raised.

The lane-side format contract is checked separately and mechanically by
`python3 .workmux/gapcheck.py all <worktree>` — table shapes, degree and
root-cause vocabularies, unit-id coverage, count-versus-enumeration arithmetic,
the acyclicity and edge count of the dependency graph, and marker/manifest
agreement in both directions.

---

## 8. Settled questions

**No `PENDING-HUMAN` escalation is open under `gap/`.** Six were, and the
maintainer settled all six on 2026-09-08. Each is recorded below by bare id,
with his ruling in his own terms and the artefact the ruling landed in, so that
a reader searching for an id lands on the answer rather than on the question.
Two of the six — `NFR012-RUNNER-SEND` and `RES04-META-UNREACHED` — were decided
under his explicit directive to prefer the simpler design wherever review
quality is not reduced. These are his decisions, not this document's, not a
review seat's, and not provisional.

The marker grammar is three-way and only the first form is an open question: a
marker followed by a real id is in use; the definitional form with a literal
placeholder in `gap/methodology.md` is where the marker is *defined*; and bare
`PENDING-HUMAN` with no colon is prose about the mechanism. A settled escalation
is referred to by bare id and never by quoting a marker string, which is why
nothing below reproduces one — quoting a marker string here would re-open all
six as far as both checkers can tell.

### `VERDICT-ORPHANED` — settled 2026-09-08

Raised on U-VERDICT-15 and U-VERDICT-17 in `gap/evidence/verdict.md`: whether
`(orphaned)` in a wave-1 unit name was lane-boundary language or plain
description of the reachability fact the unit's own evidence establishes.

**Ruled:** `(orphaned)` comes out of both unit names; the reachability fact
stays, in each unit's evidence, as a fact with its citation and its quoted
negative search. `built then orphaned` is a §6 root-cause term and root cause is
a register judgement made per requirement row, so a unit name carrying it
pre-empts the row that should reach it — and does so for a whole unit when the
cause is per requirement. Evidence establishes what the code does and whether it
is reached; the register decides degree and cause from that.

Landed in `gap/evidence/verdict.md` (both headings renamed to the behavioural
responsibility, both reachability facts now carrying the exact commands and
their actual output) and `gap/dispositions/verdict.md` (matching headings; the
ruling and its one factual correction recorded under U-VERDICT-15). Neither
disposition moves: both units were `bin` and remain `bin`.

### `FR035-TRACKER-STATE` — settled 2026-09-08

Raised on the `RQA-FR-035` row: the requirement is satisfied or not by GitHub
issue state, which this tree-scoped analysis at `9267b6308` cannot observe, so a
person had to confirm the issues' actual state rather than let the row stand as
a claim about the tracker.

**Settled by observation, not interpretation.** The maintainer queried the
tracker himself and found #109, #535 and #536 all open, with no state reason on
any of them, so none is closed and none is re-parented and none of the row's
three conditions holds. The recorded `full gap` / `not built` is confirmed. The
requirement is satisfiable only by action on the issue tracker — #2068's work,
not code — so no disposition unit can ever serve it, and the row now says so
rather than leaving a reader to infer it from the absent `U-` id.

Landed in `gap/register/fr.md:210`, which carries his command and its output
verbatim, and in that file's class note.

### `NFR011-LIFECYCLE` — settled 2026-09-08

Raised on the `RQA-NFR-011` row: whether reading it as the platform-support
obligation its shall statement makes, with lifecycle shortfalls carried on their
own rows, is the right reading.

**Ruled:** it is, and the row stands at `fit`, unchanged. The requirement's own
fit criterion settles it — a system supporting GitHub review as the
specification requires satisfies the row whether or not it also supports a
second platform, since C8 and Non-goal 1 release cross-SCM support as out of
scope rather than prohibiting it. Rolling lifecycle shortfalls in would
double-count them and make one row's degree depend on another's, which §5's
one-degree-per-requirement rule forbids.

This is the one escalation where "closed" and "nothing changes" are both true,
and `gap/register/nfr.md:420` says both explicitly: the marker was answered, not
dropped.

### `NFR012-RUNNER-SEND` — settled 2026-09-08

Raised on the `RQA-NFR-012` row: what "the system sends" means, given that RQA
writes the evidence bundle locally and only the runner's own file access carries
it to a provider.

**Ruled:** "permit … to be sent" means RQA must not prevent it, not that RQA
must itself transmit. No transport or egress component is required: RQA writing
the bundle to the local artifact directory (`scripts/evidence.py:91-126`) and a
harness reading it from there satisfies the permission. AC17's identifiability
obligation is satisfied from configuration at preflight — a disclosure check,
not an egress proxy — so it does not force RQA to own the send, and reading it
as active transmission would add a component with a security boundary AC17 does
not require, against C1's tooling independence, which puts the model call in the
harness rather than in RQA.

The degree stays `partial gap` and the cause stays `not built`: the ruling
settles what the requirement means, not whether the code meets it. The residual
gap the row now states in those terms is that `--no-tools` categorically
disables the harness file access the permission depends on, so in the
configurations that set it RQA does prevent code, diffs and evidence reaching
the configured provider. Landed in `gap/register/nfr.md:407`.

### `NFR026-MERGE-VACUOUS` — settled 2026-09-08

Raised on the `RQA-NFR-026` row: whether an activity the system cannot perform
at all counts as defaulting to disabled.

**Ruled:** it does not. The degree changes from `fit` to `partial gap` and the
root cause from `-` to `not built`. Five of the six activities the requirement
names exist in `ACTIVITIES` and do default to disabled via `DEFAULT_MODE`;
`merge` is not a member at all, so it cannot be said to default to anything and
the obligation is vacuously unevaluable rather than met. Under §5 that is
`partial gap` — compatible partial implementation — and not `conflicting`, since
absence is not contrary. Treating the row as `fit` would rest a satisfied
requirement on a vacuous truth, the defect this project has already refused
three times.

The fail-closed *safety goal* is met in practice for `merge`, because absent
capability cannot be exercised; the *requirement* is nonetheless unmet, and the
distinction matters because `RQA-FR-029` requires `merge` be configurable in
both directions. This is the ruling with the widest ripple: it landed in
`gap/register/nfr.md:418` and that file's class note, in §4's two summary tables
and the prose under them, in §6.1's transition row and §6.3's coverage note
here, and in every disposition whose `Root cause:` line or justification named
the requirement — `dispositions/authority.md`, `dispositions/resilience.md`,
`dispositions/docs.md` (U-DOCS-04, U-DOCS-12, U-DOCS-28, U-DOCS-29) and
`dispositions/policy.md` (U-POLICY-02, U-POLICY-05, U-POLICY-06). No
disposition changed: a `keep` beside a `partial gap` row is legitimate, and each
justification now claims the met portion rather than the whole requirement.
`RQA-FR-028` is deliberately untouched — its degree was set by a separate ruling
and its reasoning turns on `authority`'s default mode, which this does not move.

### `RES04-META-UNREACHED` — settled 2026-09-08

Raised on U-RESILIENCE-04: the register credited `CATEGORY_META` as consumed
safe-degradation signalling, while the product-source consumer search returned
nothing outside `errors.py`.

**Ruled:** `CATEGORY_META` / `authority_impact` is **binned**, not reworked into
the active path; `panel.py` consuming the coarse constants directly
(`scripts/panel.py:51-58`, `scripts/panel.py:381-403`, his citations, with the
two `CANDIDATE_TERMINAL` returns just past their end at `scripts/panel.py:413`
and `scripts/panel.py:424`) is the real mechanism.
#2006 §6 requires every retained component to materially serve a criterion with
no materially simpler approach sufficing, and a registry with no consumers fails
that on its face. The obligations it appeared to serve are outcome properties,
not vocabulary: AC11 forbids a resource bound producing a successful review and
AC12 requires either a configured fallback or a clear, safe, recoverable
non-success state, and both are provable only where terminal outcomes are
minted. Degradation is therefore an obligation of the single place that produces
non-success outcomes, not a registry other parts consult.

Because U-RESILIENCE-04 is not wholly that registry — it also covers
`classify_error` and `classify_disposition`, the typed `JobBlockingError` signal
`dispatcher.degrade()` raises, and `panel.py`'s fallback loop on the coarse
constants — the unit was split under methodology §4 rather than re-dispositioned
whole. U-RESILIENCE-04 keeps its id and the responsibilities above at `rework`;
the registry is **U-RESILIENCE-17**, appended at the end of
`gap/evidence/resilience.md` and `gap/dispositions/resilience.md` at `bin`, so
that no existing unit id moves and no register citation breaks. Its coverage
unit, U-DOCS-38, is binned with it on re-review. The estate is 162 units and
**18** `bin` units as a result (§3, §6.2). One qualification the ruling did not
reach: of the responsibilities U-RESILIENCE-04 retains, the two classifier
functions are themselves reached only under test — `RQA-BR-009`'s row records
the searches — so the reachable part of that unit is the typed exception and the
coarse constants. That changes no degree; `gap/register/br.md:142` now rests the
row's met obligation on the reachable evidence alone.

`RES04-PREJUDGED-ESCALATION`, the subsidiary dispute recorded beside the marker,
is resolved by the same ruling. A review seat had objected that the rework
sentence then standing above the marker presupposed one answer to the parked
question; a second seat passed the same lines. The ruling settles the
presupposed question, and settles it in the direction the objection said must
not be presupposed, so the sentence is gone rather than reworded. It was
deliberately never given a marker of its own — whoever answered the escalation
answered it, which is what happened. Recorded in
`gap/dispositions/resilience.md` under U-RESILIENCE-04.
