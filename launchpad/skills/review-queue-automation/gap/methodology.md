# RQA gap analysis — methodology

The definitions this fit/gap analysis runs on. Every other document under
`gap/` is an application of the rules stated here, and a reader who has this
file needs no other context to check whether a row was decided correctly.

- **Revision under analysis:** `9267b6308714454a3b987622d90cda03a8972827`
  (short `9267b6308`). Every claim, citation and register row in this analysis
  is a claim about the tree at that revision and nothing else.
- **Packaging provenance:** the analysis was originally authored against
  `eb1cedb19d02e61426bc5e75b7a43cc485c8a133`. Its complete
  `launchpad/skills/review-queue-automation/` tree and the tree at `9267b6308`
  both resolve to `31e8eedc6744328c156b64cf506cd68464fbc458`; the revision references were
  repointed during clean-branch assembly so the published validator does not
  depend on an otherwise unrelated source branch. This is a content-identical
  packaging anchor, not a claim that the research was re-authored.
- **Paths:** every path written anywhere under `gap/` is relative to
  `launchpad/skills/review-queue-automation/` — `scripts/queue.py`,
  `tests/test_queue.py`, `references/contracts.md`. A path that starts
  `launchpad/` is a mistake.
- **Estate:** [`manifest.md`](manifest.md) pins the 135 tracked files and
  states which 121 are assessed. [`clusters.md`](clusters.md) partitions those
  121 into seven disjoint clusters.

---

## 1. Purpose and standing

This analysis answers two questions and no others:

1. For each of the 86 requirements in the frozen specification, how far does the
   implementation at `9267b6308` meet it, why does it fall short, and what
   evidence establishes that?
2. For each named behavioural responsibility in the assessed estate, what should
   happen to it — keep, salvage, rework or bin — given the requirements it does
   or does not serve?

**The future state is the requirements specification, as frozen.** The future
state of this analysis is
[`requirements/requirements-specification.md`](../requirements/requirements-specification.md)
and its sibling documents exactly as they stand at `9267b6308`. This analysis
**adds no requirement, rewords no requirement and drops no requirement on
account of what the implementation does.** The implementation is the subject of
the analysis, never a source of authority over the specification.

Three consequences, each binding:

- A requirement that the current design makes awkward, expensive or apparently
  unimplementable is recorded as a **gap with a root cause**. It is never edited
  away, never softened, and never marked `fit` because meeting it would be hard.
- Where an analyst comes to believe a requirement is itself wrong — internally
  inconsistent, contradicted by an accepted decision, or impossible as written —
  the row still carries its honest gap degree, and the belief is recorded as
  `PENDING-HUMAN:<short-id>` in that row's `notes` cell. `PENDING-HUMAN` is an
  escalation to a person; it is not a licence to depart from the specification
  while waiting for the answer.
- This analysis prioritises nothing and defers nothing. Every requirement in the
  frozen specification is mandatory, so the register carries **no priority
  column** and no ranking (§9).

**Out of scope**, per issue #2070 and binding on every lane of this work:
changing any script, schema or test; designing the replacement; editing the
requirements specification; prioritising or deferring any requirement.

---

## 2. The "implements" test

The load-bearing definition. Every `fit` judgement and every `keep`/`salvage`
disposition rests on a claim that some code **implements** a behaviour, so the
test for that claim has to be stated before any row is written.

### 2.1 The test

> Code **implements** a required behaviour when, at `9267b6308`, (a) code
> exists that performs the behaviour, (b) that code is **reachable** from a
> product entrypoint (§2.2) by a path that does not pass through a test, and
> (c) the behaviour it performs is the behaviour the requirement describes,
> not a near neighbour of it.

All three conjuncts are required.

- Fails (a) → the behaviour is absent: `not built`.
- Fails (b) → the mechanism exists but nothing in the product reaches it:
  **an orphaned function is not an implementation.** A called one is.
- Fails (c) → code exists and runs, but does something else. If what it does
  merely stops short, that is a shortfall; if what it does is incompatible with
  the requirement, that is `conflicting` (§5).

### 2.2 Entrypoints — the reachability frontier

A **product entrypoint** for this skill is any of:

| # | Entrypoint | Concretely |
|---|---|---|
| E1 | The scheduled tick | `scripts/scheduled-tick.sh`, and the timer definition `scripts/launchd.plist.example` that fires it |
| E2 | A `dispatcher.py` subcommand | `sweep`, `tick`, `dispatch-one`, `status`, `health`, `retention`, `cooldown-reset`, `recover`, `backup` — i.e. anything registered on `dispatcher.main`'s subparser |
| E3 | A module's own `__main__` CLI | a `scripts/*.py` with an `if __name__ == "__main__"` block **and** an operator-facing citation that **instructs someone to run it** (`SKILL.md`, `OPERATORS.md`, `onboarding/SKILL.md`, `references/**`) — a runbook step, a documented command line, or a procedure the reader is told to perform |
| E4 | A documented operator procedure | a runbook step in `OPERATORS.md` or `references/runtime-ops.md` naming a command an operator is instructed to run |
| E5 | An inbound external trigger | a GitHub webhook, timer or platform callback the skill is documented to receive |

Reachability is **transitive through ordinary calls** — if E2 calls `f` and `f`
calls `g`, `g` is reachable. It is **not** transitive through a test: a call
made only from `tests/**` does not confer reachability, because the test
demonstrates the code can work, not that the product runs it.

A module that has an `if __name__ == "__main__"` block but **no** operator-facing
citation is *not* an entrypoint under E3. Executability is not exposure: a file
is reachable because a person or a timer is told to invoke it, not because
Python would run it if someone did.

**An inventory listing is not an instruction.** A table that merely *names* a
script and says what it is does not satisfy E3, and a listing that is
affirmatively disclaimed defeats E3 outright. `OPERATORS.md:560-564` introduces
its second script table with "**Internal modules that are also executable.** Each
of these has a `__main__` block used for debugging and by the harness's own
tests. They are **not** operator commands: running them by hand takes the step
outside the state-directory ownership boundary that `dispatcher.py` enforces".
**Every one of the twelve scripts listed under that header fails E3 on the
strength of that listing alone** — `queue.py`, `scheduled-tick.sh`,
`launchd.plist.example`, `cadence.py`, `lease.py`, `evidence.py`, `panel.py`,
`worktree.py`, `github_rest.py`, `github_query.py`, `github_mutate.py`,
`approval_action.py` (`OPERATORS.md:566-579`). No wave-1 lane may cite a row of
that table as evidence that a script is reachable.

Two corollaries, so the rule is not over-applied either:

- **Another entrypoint class may still reach the same file.** The disclaimer
  speaks only to operator invocation. `scripts/scheduled-tick.sh` and
  `scripts/launchd.plist.example` are reachable under **E1** because a timer
  fires them; `scripts/queue.py`, `scripts/lease.py`, `scripts/evidence.py`,
  `scripts/panel.py` and the GitHub transports are reachable under **E2**
  wherever `dispatcher.py` calls into them. E3 failing is not a finding on its
  own — it is a finding only when no other class reaches the file either.
- **The first table is different.** `OPERATORS.md:549-558` maps seven scripts —
  `onboarding.py`, `route_probe.py`, `dispatcher.py`, `human_cli.py`,
  `history.py`, `shadow.py`, `explain.py` — to numbered runbook sections that
  tell an operator to run them. Those citations satisfy E3/E4; cite the runbook
  section, not the index row.

### 2.3 When the only caller is a test

State it plainly, because it is the most common trap in this estate:

> **A behaviour whose only caller is a test is not implemented.** The claim
> "there is a test for it" is evidence that the mechanism runs under test
> conditions and is evidence of nothing else.

Such a claim is classified by whether the mechanism is otherwise exposed:

- **Test-only, no entrypoint** → the requirement's degree is `full gap` (or
  `partial gap` where a different, reachable mechanism covers part of it), and
  the root cause is `built then orphaned` (§6) — the mechanism was built, and
  nothing in the product calls it.
- **Test-only within the pipeline, but genuinely exposed by E3/E4 as a manual
  command** — the citation instructs a person to run it, and is not a disclaimed
  inventory listing — → the *manual* behaviour is implemented and the
  *automated* behaviour is not. These are two disposition units (§4), judged
  separately. Do not average them into one half-credit row. Establish the
  instruction before splitting: absent one, this is the first case, not this one.

A test file is admissible as evidence **of what the code does**, and is never
admissible as evidence that a behaviour is reached in production.

### 2.4 Worked example — `worktree.py` and the author-triage lane

Run the test on the case the PRD's own evidence section flagged.

**The documentation claim.** `references/contracts.md:16` states the
`author_triage` lane "evaluates feedback on the operator's PR, then may modify
and push the PR branch". `SKILL.md:76` describes fixing valid findings "in an
isolated worktree". `references/classification.md:21` lists "Set up and remove
isolated author worktrees" as a Script-class action.

**The code.** `scripts/worktree.py` implements `create` (`scripts/worktree.py:102`),
`commit` (`scripts/worktree.py:170`), `push` (`scripts/worktree.py:195`) and
`clean` (`scripts/worktree.py:229`), plus a CLI `main` whose `operation` choices
are exactly those four (`scripts/worktree.py:262`, `scripts/worktree.py:265`).

**The callers.** No file under `scripts/` imports or invokes `worktree` — the
only occurrence of the string in another script is a comment
(`scripts/runners.py:120`). The importers are `tests/test_worktree.py:20` and
`tests/test_integration.py:133`. `dispatcher.py` never names the author-triage
lane; it treats it as a generic `lane` parameter (job selection at
`scripts/dispatcher.py:2162`), gated by the `author_canary_approved` config key
(`scripts/dispatcher.py:1797-1800`). Nothing on the dispatch path creates,
commits to or pushes a worktree.

**The entrypoint question.** `scripts/worktree.py` does have a `__main__` CLI, so
E3 has to be tested rather than assumed. It fails. The only place any document
names the script is `OPERATORS.md:575` — a row of the table headed "Internal
modules that are also executable… They are **not** operator commands"
(`OPERATORS.md:560-564`). That is an inventory listing under an explicit
disclaimer, not an instruction to run anything (§2.2). A full search of the
operator-facing documents — `SKILL.md`, `OPERATORS.md`, `onboarding/SKILL.md`,
`references/**` and `config.example.json` — returns three occurrences of
"worktree" in total: `SKILL.md:76` and `references/classification.md:21`, which
describe *behaviour the system performs*, and `OPERATORS.md:575` itself. **No
document instructs anyone to run `scripts/worktree.py`.** E1, E2, E4 and E5 do
not reach it either: no timer fires it, no `dispatcher.py` subcommand calls it,
no runbook step names it, no external trigger arrives at it.

**Applying the test — one unit, one answer.**

- *Unit "isolated author worktree operations for the author-triage lane".*
  (a) code exists and is complete; (b) **fails** — no entrypoint class reaches
  it, and the only callers are two test modules, which §2.3 says confer nothing;
  (c) not reached. → **Not implemented.** Any requirement resting on this
  behaviour is `full gap`; root cause `built then orphaned` — built, tested,
  documented as something the system does, and never wired to anything that runs
  it.

There is no second, "operator-invoked" unit to carve out here. A manual unit
exists only where a document tells a person to run the command (§2.3), and here
no document does. Splitting a file into a "manual" and an "automated" unit on
the strength of a `__main__` block alone manufactures an implementation that
does not exist.

**The general lesson this example teaches:** documentation describing an
automated behaviour, plus code able to perform it, plus tests exercising it, plus
an inventory row naming the file, do **not** add up to an implementation when no
product path connects them. Any analyst tempted to write `fit` here should
re-read §2.1(b) — and should check whether the citation they are about to lean on
is an instruction or a listing.

---

## 3. Evidence rules

1. **Code first, cited by line.** Every behavioural claim cites at least one
   `path:line` in a non-test source file at `9267b6308` — the line where the
   behaviour is decided, not the module's first line. Cite several lines when
   the behaviour is decided in several places.
2. **Line numbers are revision-bound.** A citation means "line N of that file at
   `9267b6308`". Any later re-evaluation re-reads the file at its own revision
   and updates both the citation and the row's `revision` cell (§8).
3. **Tests are corroborating, never constitutive.** `tests/**` may be cited to
   show *what* code does or to show a behaviour is exercised only under test.
   A `fit` row must not rest on a test citation alone.
4. **Documentation as evidence — admissible only in the negative case.** A
   documentation path (`SKILL.md`, `OPERATORS.md`, `onboarding/SKILL.md`,
   `references/**`) is admissible as the primary evidence for a row **only where
   the "implements" test finds no code** — i.e. to establish what was intended
   or claimed, for a behaviour that is absent, orphaned or contradicted. Such a
   row must (a) cite the documentation `path:line`, (b) state in its notes that
   no code implements the behaviour, and (c) never carry degree `fit`. A
   documentation citation may never be the sole support for a claim that
   something **works**.
5. **Prior analyses are leads, not evidence.** The branch
   `docs/rqa-architecture-reference` and the material under
   `launchpad/research/rqa-specialist-suite-analysis` may be read to find
   things worth checking. Nothing from either is ever cited as evidence in this
   analysis, because both pre-date the amended PRD and may describe intent this
   specification has since superseded. Anything they suggest must be
   re-established against code at `9267b6308` before it enters a row.
6. **Contradiction is reportable, not resolvable by preference.** Where
   documentation and code disagree, the code establishes the behaviour and the
   documentation establishes the claim; the row records both and the divergence
   is itself a finding (the `worktree.py` case in §2.4 is the worked example).

---

## 4. The disposition unit

A disposition applies to a **named behavioural responsibility**, not to a file.
"What should happen to `scripts/dispatcher.py`" is not a question this analysis
can answer; "what should happen to *lease acquisition and renewal*" is.

**Identifier.** `U-<CLUSTER>-NN`, where `<CLUSTER>` is one of the seven cluster
names upper-cased — `QUEUE`, `DISPATCH`, `POLICY`, `VERDICT`, `AUTHORITY`,
`RESILIENCE`, `DOCS` — and `NN` is a zero-padded two-digit number counting from
`01` within that cluster. Example: `U-QUEUE-03`.

**One unit = one named behavioural responsibility.** A unit's name states a
behaviour the system performs or a guarantee it upholds, in terms a reader of
the requirements specification would recognise. If the name only repeats a
module name, it is not yet a unit name.

**Splitting a file with several responsibilities.** A file yields as many units
as it has separable responsibilities. Two responsibilities in one file are
separable when they could be judged differently — one could be kept while the
other is reworked — without the judgement on either becoming incoherent.
Practical tests, any one sufficient:

- they serve **disjoint requirement sets**;
- they have **different reasons to change** (one follows GitHub's API, the other
  follows local policy);
- one could be removed and the other would still be required.

**The three tests are triggers, not competing rules.** Any one of them firing
establishes separability, and they do not need to agree. Each is a sufficient
trigger for the definition above it, not a rule in its own right that another
test could outvote, so a test that fires while the other two stay silent has
still decided the question. Disagreement among the tests is not a conflict to
adjudicate and never a reason to hold a unit together.

**A test firing against an apparently incoherent split is a mapping defect.**
Where a test fires but the resulting halves genuinely could not be disposed of
separately without the judgement on either becoming incoherent, the fault lies
in the requirement mapping that made the test fire, not in the unit boundary.
Split the unit and record the doubt as a `PENDING-HUMAN:<short-id>` row against
the mapping (§1). It is never grounds to keep the unit merged.

**Worked example — `scripts/cadence.py`.** Its interval selection, its
config-reload freshness and its per-scope isolation serve disjoint requirement
sets — `RQA-BR-010`, `RQA-FR-004`/`RQA-NFR-005` and `RQA-NFR-004` respectively.
The disjoint-requirements test fires, so the file yields three units. The
objection that the three are not independently removable — that binning
per-scope isolation would contradict `RQA-NFR-004` while the interval algorithm
is still required — does not survive the definition. It describes the halves
taking **different dispositions**, one binned and one kept, which is precisely
what separability means. Incoherence would be a judgement on one half that left
the judgement on the other unreadable, not two halves judged differently.

**The tests apply to responsibilities, not to evidence rows.** The three tests
are run against candidate responsibilities. Two rows of one unit that bear on
different requirements do not by themselves trigger a split: one responsibility
routinely serves several requirements, and treating rows as the subject of the
tests would collapse every unit onto its requirement mapping and discard §4's
own definition of a unit as a named behavioural responsibility. This does not
weaken "any one test firing is sufficient". `cadence.py` splits three ways
because it holds three responsibilities that happen to serve disjoint sets, not
because one responsibility had three rows — one trigger is still enough, and
what it fires on is a responsibility.

Each unit derived from a shared file names its own line ranges or function names
in its evidence, so two units of the same file are never confused.

**Multi-file units.** A unit may span files **only when** it (a) lists every
member file explicitly and (b) gives **one shared rationale** that applies to
all of them — i.e. the members are so coupled that a disposition on one forces
the same disposition on the rest. A unit that spans files with per-file caveats
is really several units and must be split. A unit that spans clusters is
prohibited: clusters are file-disjoint by construction, so a would-be
cross-cluster unit indicates the cluster boundary or the unit boundary is wrong,
and it is escalated with `PENDING-HUMAN`, not silently merged.

**`Files:` is disposition scope; the evidence cell is not.** A unit's `Files:`
line names the files a disposition — `keep`, `salvage`, `rework` or `bin` — will
be recommended over, and the cross-cluster prohibition above is about that
membership: it exists so that two lanes never disposition the same file. A
unit's evidence cell does something else. It establishes a claim, and §3 rule 1
governs it — the line where the behaviour is decided — imposing no cluster
restriction at all. So a deciding line in another cluster's file is admissible
as primary evidence, and it never enters `Files:`. Citing `dispatcher.py` to
establish how `lease.py`'s contract is actually invoked leaves `dispatcher.py`
in the dispatch cluster's disposition scope, where it is already assessed —
nothing goes unassessed, and nothing is dispositioned twice.

**Coverage.** Every assessed file in a cluster is named by at least one unit of
that cluster. A file no unit needs is itself a finding — record it as a unit
whose disposition is `bin`, with the reason that no requirement is served.

---

## 5. Gap degrees

Every requirement carries exactly one degree. The register admits no other
value, and no requirement is left unjudged.

| Degree | Definition |
|---|---|
| `fit` | The implementation satisfies the requirement **in full** at `9267b6308`. Every obligation the requirement states is met by code that passes the "implements" test (§2). No qualification, no "in the common case". |
| `partial gap` | Code implements **some but not all** of the requirement's obligations, and what it does implement is **compatible** with the requirement — a subset, not a contradiction. Closing the gap adds to or extends existing reachable behaviour; it does not have to undo it. |
| `full gap` | **None** of the requirement's obligations are met by code that passes the "implements" test. This includes the case where a mechanism exists but is orphaned or test-only (§2.3): from the product's point of view the behaviour does not happen at all. |
| `conflicting` | Behaviour that **passes** the "implements" test **contradicts** the requirement: reachable code does something the requirement forbids, or takes a decision the requirement assigns elsewhere. Closing the gap requires **changing or removing** existing behaviour, not merely adding to it. |

**Deciding `partial gap` vs `full gap`.** Ask: *does any reachable code satisfy
at least one complete obligation of this requirement?*

- Yes → `partial gap`.
- No → `full gap`.

Partial credit is for **complete obligations**, not for partial progress towards
one. A module that begins the work but never reaches the required outcome
satisfies no obligation: that is `full gap`. Reachability is decided by §2.2, so
an orphaned or test-only mechanism contributes nothing to this count, however
complete it looks.

**Deciding `full gap` vs `conflicting`.** Ask: *to satisfy the requirement, must
existing reachable behaviour change or be removed?*

- No — the fix is purely additive, whatever exists can stay → `full gap`.
- Yes — some reachable behaviour must be altered, constrained or deleted because
  it is incompatible with the requirement → `conflicting`.

`conflicting` is a claim about **contradiction**, not about disappointment.
Silence is never a conflict: a requirement the code simply ignores is a
`full gap`. Two positive statements that cannot both hold — the requirement says
a human decides X and reachable code decides X itself; the requirement forbids Y
and reachable code performs Y — are a conflict. When both readings look
arguable, the deciding question is the fix: additive → `full gap`, subtractive
or corrective → `conflicting`.

**Degree is per requirement, not per unit.** One weak unit does not downgrade a
requirement that other reachable code satisfies in full; one strong unit does
not upgrade a requirement whose remaining obligations are unmet.

---

## 6. Root causes

Every row whose degree is other than `fit` carries exactly one root cause. Rows
of degree `fit` carry `-`. The set is closed.

| Root cause | Definition | Evidence that establishes it |
|---|---|---|
| `not built` | No code implementing the behaviour exists **in the tree at `9267b6308`** — there is nothing to reach, orphaned or otherwise. Evaluated snapshot-locally: see "Evaluation frame" below. | Absence at the pinned revision: the behaviour is nowhere in `scripts/` or `schemas/`. Support the absence with the search actually run, plus the citation of the nearest thing that exists and does not do it. |
| `built against superseded intent` | Code exists and is reachable, but it implements an **earlier** understanding of the behaviour that the frozen specification has since replaced. It is coherent on its own terms and wrong against the current terms. | A `path:line` for the reachable behaviour, **plus** the specification text (or the decision it cites) that supersedes it. The two must be shown to describe the same behaviour differently. |
| `built then orphaned` | Code exists and would perform the behaviour, but nothing reaches it — the only callers are tests, or nothing calls it at all. | The implementing `path:line`, **plus** the negative caller search that establishes no product path reaches it, **plus** the test-only callers if any. This is §2.4's classification. |
| `built contrary` | Reachable code takes a position the requirement forbids: it performs a prohibited action, or arrogates a decision the requirement assigns to a human or another component. | The `path:line` of the contrary behaviour and the requirement text it contradicts. Nearly always paired with degree `conflicting`. |

**Telling them apart.**

- `not built` vs `built then orphaned`: does implementing code exist anywhere in
  the tree at `9267b6308`? If yes it is never `not built`, however unreachable
  it is.
- `built then orphaned` vs `built against superseded intent`: is the code
  **reached**? Orphaned code is unreached; superseded code runs and is wrong.
- `built against superseded intent` vs `built contrary`: does the code merely
  reflect an older intent, or does it do something the requirement **forbids**?
  Supersession is a version problem; contrariety is a prohibition problem. When
  both apply, `built contrary` wins — a prohibited behaviour must be reported as
  such regardless of why it was written.
- A degree of `conflicting` cannot carry root cause `not built`: nothing that
  does not exist can contradict anything. Such a row is an error.

**Evaluation frame — `not built` is decided at the pinned revision, never from
history.** This resolves escalation `RC-DECIDE`, authorised for
this analysis.

A root cause is a claim about the **state of the tree at `9267b6308`**, not about
what happened in the repository's past. `not built` therefore means *no
implementing code is present at that revision*. It does not mean "no one ever
wrote it", and establishing it requires **no** archaeology: no `git log`, no
blame, no deleted-code search, no reasoning about which commit removed what.
The evidence is the search actually run over the tree at `9267b6308` and its
null result.

Two consequences:

- Code that once existed and has since been deleted is `not built` here, because
  at the assessed revision it is absent. The deletion may be worth a note; it
  never changes the cause.
- The other three causes are equally snapshot-local. `built then orphaned`
  asserts code is present and unreached **now**; it makes no claim that the code
  was once wired and later unwired. `built against superseded intent` is
  established by comparing reachable code against the **frozen specification**,
  not against an older revision of the code. Nothing in this analysis needs the
  repository's history, and no row may rest on it.

**One row, one root cause — and how "largest" is measured.** Where several
causes apply to different obligations of one requirement, record the cause of
the **largest unmet part** and name the others in the notes. "Largest" is
measured by **count of distinct unmet obligations**, using the same obligation
enumeration §5 uses to decide `partial gap` against `full gap`:

1. Enumerate the requirement's obligations, and list them in the row's evidence
   so the count is reproducible by the next reader.
2. Attribute each **unmet** obligation to exactly one cause. Met obligations are
   not counted; they have no cause.
3. The cause holding the most unmet obligations is the row's cause.
4. **On a tie, apply this fixed precedence, highest first:**
   `built contrary` > `built against superseded intent` > `built then orphaned` >
   `not built`. It ranks by what a reader most needs to see: a prohibition
   breached, then reachable code that is wrong, then code that exists but is
   unreached, then simple absence. This precedence also settles the §6
   "when both apply, `built contrary` wins" rule, of which it is the
   generalisation.

Obligation counting is not severity weighting: no obligation counts for more
than one because it looks more important. Judgements about importance are
prioritisation, which §9 forbids this analysis to make.

---

## 7. Dispositions

Each disposition unit (§4) carries exactly one.

| Disposition | Meaning |
|---|---|
| `keep` | Retain as it is. The unit serves a named requirement, meets it, and no materially simpler approach would serve that requirement. |
| `salvage` | Do not retain the code as it stands, but carry forward a **specific mechanism or design decision** it embodies, named explicitly. |
| `rework` | The responsibility is required and the current implementation is the wrong shape for it. Rebuild the unit against the requirement. |
| `bin` | Remove. No requirement in the frozen specification needs this responsibility, or the requirement it serves is better met without it. |

**The justification rule — binding, and the one most often broken.**

> No unit is recommended `keep` or `salvage` **because it exists, because it has
> tests, or because it works today.** Every `keep` and every `salvage` must
> (a) name the requirement ID(s) the unit serves, and (b) state why no
> materially simpler approach suffices for those requirements.

Incumbency is not a reason. "It passes its tests" is not a reason — tests
establish that code does what it does, never that the requirement needs it done
that way. A unit that cannot name a requirement it serves is `bin`, whatever its
test coverage; a unit whose requirement a materially simpler approach would
serve is `rework`, however well the current one works.

**`salvage` names a mechanism, not a file.** "Salvage `scripts/lease.py`" is not
a disposition — it is a wish to keep a file. A salvage reads like "salvage the
node-id-scoped lease key, which is what makes concurrent claims safe", and names
the requirement that mechanism serves. A salvage that cannot name the mechanism
in one sentence is a `rework` in disguise.

Dispositions follow from the register: a unit's disposition must be consistent
with the degrees and root causes of the requirements it serves. `keep` for a
unit whose requirements are all `conflicting` is a contradiction; so is `bin`
for the only unit serving a `fit` requirement.

---

## 8. The split-AC rule

Carried forward from
[`requirements/traceability.md`](../requirements/traceability.md), which binds
this analysis:

> **A source acceptance criterion is satisfied only when every requirement
> derived from it is satisfied, not merely one.**

The specification adopts the same atomicity discipline for its splits of P, C,
project-requirement, closing-criterion and security-implications clauses.
Applied here:

- **Never mark a source clause covered because one child requirement holds.**
  Where a clause produced several requirements — CL-034/AC07 into `RQA-FR-014`,
  `RQA-FR-015` and `RQA-FR-036` is the specification's own worked example — the
  clause is met only when **all** of its children are `fit`. One `fit` child
  alongside a `full gap` sibling means the clause is **not** met.
- Degrees are assigned **per requirement**, never per clause. Nothing in this
  analysis rolls several requirements up into one clause-level judgement.
- Any summary or narrative in `gap-analysis.md` that counts clause coverage
  applies the conjunction above; a clause-level "covered" that would be false
  for any child is prohibited.
- The specification's split inventory is
  [`requirements/singular-splits.md`](../requirements/singular-splits.md); every
  multi-requirement entry there is subject to this rule.

---

## 9. Dependency ordering, and no priority

**`depends on`.** A row for requirement A lists requirement B when **A's gap
cannot be closed until B's is closed** — a technical precedence, not an opinion
about importance. Admissible reasons, and only these:

- **Substrate:** the behaviour A requires is expressed in terms of a structure,
  state or record that B's behaviour creates. Nothing can act on a record that
  is not yet written.
- **Authority:** A's behaviour is only permitted once B's control, gate or
  record exists — implementing A first would mean shipping the action without
  the check.
- **Contract:** A is defined against an interface, schema or vocabulary that B
  establishes; A cannot be built to a shape B has not yet fixed.

Rules for the cell:

- Every entry is a requirement ID that exists in the frozen specification.
- A row never depends on itself, and the dependency graph carries no cycle. A
  cycle means the split is wrong; report it with `PENDING-HUMAN` rather than
  breaking the cycle by preference.
- `fit` rows normally list `-`: a closed gap has nothing to wait for.
- Dependencies are recorded **only** where they exist. An empty cell (`-`) is
  the common case and the correct default; a chain invented to look orderly is
  worse than none.
- "A and B are related", "A is more urgent than B" and "the same lane would do
  both" are **not** dependencies.

**No priority ranking.** The register has no priority column and this analysis
assigns no ranking, sequencing recommendation, phase or wave to any requirement.
Every requirement in the frozen specification is mandatory; ranking mandatory
work is a planning decision that belongs to the people who plan the replacement,
not to a fit/gap analysis. `depends on` states what is technically forced and
stops there.
