# RQA gap analysis — dispositions — `queue` cluster

Revision: `9267b6308714454a3b987622d90cda03a8972827`. Every claim below is a claim
about that revision. Paths are relative to
`launchpad/skills/review-queue-automation/`, per
[`../methodology.md`](../methodology.md).

One entry per `### U-QUEUE-NN` heading of
[`../evidence/queue.md`](../evidence/queue.md), in that file's order. The four
dispositions and the justification rule they answer to are
[`../methodology.md`](../methodology.md) §7; the register rows every `Root cause`
line cites are [`../register/br.md`](../register/br.md),
[`../register/fr.md`](../register/fr.md) and
[`../register/nfr.md`](../register/nfr.md).

**Reading a `Root cause:` line.** It names the register's own cause for each
requirement the unit serves or fails, with the row's location, and `-` where the
row is `fit`. A cause located outside the unit is said to be so, with the unit
the register puts it in — several `queue` units serve requirements whose degree
is decided elsewhere, and a disposition that did not say where would be
unreadable.

**Commands.** Every command quoted below was run from
`launchpad/skills/review-queue-automation/`, and its stdout is pasted as it was
returned.

**Outcome:** 11 `keep`, 1 `salvage`, 2 `bin`. The cluster carries the estate's
`fit` rows — `RQA-BR-007`, `RQA-NFR-004`, `RQA-NFR-005`, `RQA-FR-004` and
`RQA-FR-031` all rest on units named here — so the keep count is high; each keep
below still has to name the requirement and say what a simpler approach would
fail to do, and a keep with only incumbency behind it is struck.

---

### U-QUEUE-01 — PR inventory detection and per-lane job creation

Disposition: keep

Requirements: RQA-BR-007, RQA-FR-020, RQA-FR-016, RQA-NFR-010

Root cause: RQA-BR-007 `-` (fit, gap/register/br.md:141); RQA-FR-020 `not built` (gap/register/fr.md:197); RQA-FR-016 `not built` (gap/register/fr.md:187); RQA-NFR-010 `built contrary`, located outside this unit in U-DISPATCH-20 (gap/register/nfr.md:400).

`RQA-BR-007` is `fit`, and the register's evidence for that fit is this unit's
key: at most one job per exact `(repo, number, head, lane)`, an existing row for
that key blocking a second. No materially simpler approach serves it. Dedupe on
`(repo, number)` alone is the simpler design and it fails the requirement from
the other side — it suppresses review of a genuinely different revision, which
`RQA-BR-007` does not ask for; dedupe on nothing repeats reviewer work on an
unchanged revision, which it forbids. The head component only carries that weight
because it is the head observed in the same inventory pass that created the job,
so the fact upsert and the job key are one mechanism and not two: a key whose
head came from a later, separate read would not be stable across a sweep.

`RQA-FR-020`'s `not built` cause is scoped by its own row to reviewer results —
"No reviewer result is ever reused" — while naming job non-recreation as one of
three reuse classes that are complete. That unmet part is additive panel work and
does not require this key to change.

`RQA-FR-016`'s `not built` cause is the absent per-PR disposition command and the
absent mapping of the 29 job statuses onto AC08's six values. The row's own note
is that "the per-PR state itself is maintained and kept fresh"; this unit is the
writer of that state, so closing the gap adds a reader rather than replacing a
writer.

One constraint the keep carries, and it is not cosmetic. `RQA-BR-010` is
`conflicting`, and its row cites `scripts/queue.py:116-118` as one of three
reasons a parked job is never re-driven (gap/register/br.md:148). The key does not
have to change to close that row — its own note is that every citation the degree
rests on closes by rerouting its own execution — but whatever closes it must
resume the parked job in place, not by creating a second job for the same head. A
replacement that closed `RQA-BR-010` by relaxing the key would break
`RQA-BR-007`.

The fail-closed abort — no exception handling around the per-page inventory read,
so no partial queue survives a reader's rejection — is on the compatible side of
`RQA-NFR-010`; that row names "fail-closed inventory reads" among the behaviours
that meet the requirement, and puts the contrary execution in `_ledger_record`'s
bare `except`.

### U-QUEUE-02 — supersede stale jobs and pending approval requests on head change

Disposition: keep

Requirements: RQA-FR-016

Root cause: RQA-FR-016 `not built` (gap/register/fr.md:187).

`RQA-FR-016`'s fit criterion disqualifies "a stale or generic answer after a
transition has occurred… even if the value it returns is individually legal".
Supersession is what keeps the stored per-PR state answering that criterion, and
the register's own note separates the two halves: the state is maintained and
kept fresh, and what is missing is a command that returns it. The `not built`
cause therefore points at a reader this unit does not contain, and the
disposition follows: the writer is required and correct.

No materially simpler approach suffices, and the reason is the second row rather
than the first. Filtering at read time — a status command comparing each job's
stored `head_sha` against the current head — would answer the job half with no
writes at all. It cannot answer the approval half. `approval.supersede_for_head`
**revokes** an outstanding human-approval request; a request that is merely
filtered out of a display is still answerable, so a human decision could land
against a revision the PR has moved past. Revocation is a write, and it has to
happen in the pass that first observes the new head.

The closed-PR half is not reducible either. No inbound external trigger reaches
this cluster — [`../evidence/queue.md`](../evidence/queue.md):20-46 establishes
its reachability under E1, E2 and E4 only, and E5 is the inbound-trigger class
([`../methodology.md`](../methodology.md):93) — so a PR's disappearance from the
open-PR inventory is observable only by diffing successive inventories, which is
exactly what the reset-then-reopen does; a per-PR close event would need a
trigger class that does
not exist here.

### U-QUEUE-03 — assignee review lease: GitHub-verified claim/release contract

Disposition: keep

Requirements: RQA-BR-007, RQA-NFR-010

Root cause: RQA-BR-007 `-` (fit, gap/register/br.md:141); RQA-NFR-010 `built contrary`, located outside this unit in U-DISPATCH-20 (gap/register/nfr.md:400).

The mechanism is read-after-write REST verification in both directions: the local
`leases` row is written only after a fresh REST read lists the login as an
assignee, and deleted only after a fresh REST read stops listing it. Two simpler
approaches exist and both fail. Trusting the mutation's own response is simpler
and produces the ambiguous record `RQA-NFR-010` forbids — local state asserting a
lease GitHub may not have granted, with no way after the failure to tell which is
true. A local-only lock is simpler still and fails `RQA-BR-007`, whose `fit` the
register rests partly on this unit: a lock invisible to GitHub is invisible to a
second actor — a human, a second checkout, a second machine — so the PR can be
claimed twice and the work duplicated.

The release arm is the same discipline and is not redundant with the claim arm:
raising rather than deleting the row when REST still lists the login keeps a
half-released lease detectable instead of silently lost, which is the difference
between a recoverable state and an ambiguous one.

Node-id addressing is part of the same mechanism rather than a detail: addressing
the PR by its cached GraphQL node id and the user by the node id read from
`/users/{login}` means a renamed login cannot silently address a different
account, which a hardcoded login string would.

`RQA-NFR-010`'s row names "mandatory pre/post REST verification" among the
behaviours that meet the requirement; this unit is on that side of the row, so
the keep is consistent with a `conflicting` degree decided elsewhere.

### U-QUEUE-04 — dispatch-side lease-lifecycle invocation and local exclusivity

Disposition: keep

Requirements: RQA-NFR-010, RQA-BR-007

Root cause: RQA-NFR-010 `built contrary`, located outside this unit in U-DISPATCH-20 (gap/register/nfr.md:400); RQA-BR-007 `-` (fit, gap/register/br.md:141).

Within this unit's `Files:` scope of `scripts/lease.py`, what is kept is the local
`leases` row as a **job-attributed** exclusivity record distinct from the GitHub
assignee, together with `release()` being safe to call unconditionally on every
exit path.

Collapsing to one source of truth — the GitHub assignee alone — is the materially
simpler design and it fails `RQA-BR-007` twice. The assignee records *who* holds
the PR and not *which job*, so a second dispatch of the same PR under the same
configured login cannot be refused at all; and every dispatch attempt would need a
REST read before it could refuse anything, which puts a network call in front of a
decision that must be takeable without one. The local row carries the job id,
which is what the register's `RQA-BR-007` evidence turns on when it cites the
refusal of a locally-held lease recording a different job.

A TTL or expiry lease is the other simpler candidate and is worse against the same
requirement: an expiry short enough to recover from a crashed run is short enough
to expire under a running review, which permits precisely the concurrent second
claim the requirement forbids. The always-release-in-`finally` discipline obtains
recovery without a clock, and against `RQA-NFR-010` it is what stops a failure
mid-review leaving a lease that asserts an in-flight review that is not running.

The two arms stay one keep because the evidence establishes they are one record
lifecycle: with no always-release, `claim()`'s own refusal of a PR assigned to a
different login turns a lingering assignee into a permanent block, so dropping
either arm disables the other.

### U-QUEUE-05 — adaptive sweep-interval selection

Disposition: salvage

Requirements: RQA-BR-010

Root cause: RQA-BR-010 `built contrary`, located outside this unit in the live-mode gate escalation (`scripts/approval_evaluate.py:268-288`, `scripts/dispatcher.py:1482-1502`) (gap/register/br.md:148).

Two mechanisms are worth lifting and the algorithm they sit in is not.

**Salvage the fail-toward-run default in `due()`** — a schedule that is missing or
not in the expected shape means "sweep now", never "skip". It serves
`RQA-BR-010`, whose obligation is that progression not depend on an owner acting,
and no materially simpler approach serves it: the simpler default is to fail
closed and skip the sweep, which stops discovery silently and needs a person to
notice, which is the manual-intervention dependence the requirement names. The
asymmetry is the design decision, not the code — one early inventory read against
losing discovery entirely.

**Salvage next-due as persisted per-scope state** rather than an in-process timer.
That is what lets a machine that was asleep, or a tick process that has exited,
resume on the correct schedule with nothing running in between, which is what a
timer-fired, no-daemon estate needs; and it is the substrate U-QUEUE-07's
per-scope isolation stands on, without which that unit has nothing to key.

**Do not salvage the three-rule algorithm** — idle-streak step growth, the cap at
the longest configured interval, and the REST-remaining floor that treats an
unknown remaining count as below-floor. The unit's own evidence establishes, with
the specification search quoted at
[`../evidence/queue.md`](../evidence/queue.md):207-220, that
no frozen requirement obliges an adaptive interval, and for the one requirement
that is cited a materially simpler approach does suffice: the launchd timer
already fires at a fixed 300-second interval (U-QUEUE-08), which removes the owner
from discovery without any of these rules. Carrying them forward would be
retention with no requirement behind it, which is the ground `RQA-FR-034` tests.

An observation, not a mapping: `RQA-BR-012`'s row credits "the sweep is
batch-bounded and cadence-gated" through U-DISPATCH-08 (gap/register/br.md:150), so
the persisted schedule is load-bearing for a behaviour that row counts as met.
That is why the persistence is salvaged while the rules are dropped; no
requirement is claimed here that the register does not already carry.

This unit's disposition differs from U-QUEUE-06's and U-QUEUE-07's over the same
file. That is separability as [`../methodology.md`](../methodology.md) §4 defines
it — its own `cadence.py` worked example says two halves judged differently is
what separability means — not an inconsistency.

### U-QUEUE-06 — cadence config-reload freshness

Disposition: keep

Requirements: RQA-NFR-005

Root cause: RQA-NFR-005 `-` (fit, gap/register/nfr.md:405).

`RQA-NFR-005` is `fit` and this unit is one of the three the register cites for
it. What is kept is a calling convention, not an algorithm: `_intervals()` and
`decide()` re-derive every `poll.*` value from the argument passed on that call,
and nothing is held between calls.

There is no materially simpler approach because there is nothing left to remove —
every alternative *adds*. A module-level parse at import, a memoised loader, or a
watcher with invalidation are all more machinery than reading the argument you
were handed, and each reintroduces a window in which an edited configuration is
not yet in force. That window is the substance of what the requirement forbids;
"no build or deployment step" is met trivially by a Python script, so the
obligation that actually bites is that the change takes effect on the next call.

This keep binds whatever replaces U-QUEUE-05's interval rules: the per-call
re-derivation is a property of the interface, and it survives a rewrite of the
rules it feeds. Keeping it while salvaging U-QUEUE-05 leaves both judgements
readable — rebuild the rules, keep the convention they are called under.

### U-QUEUE-07 — per-scope cadence isolation

Disposition: keep

Requirements: RQA-NFR-004

Root cause: RQA-NFR-004 `-` (fit, gap/register/nfr.md:404).

`RQA-NFR-004` is `fit` and the register's evidence for the cadence half of it is
this unit: "cadence rows are keyed by an opaque scope string".

A single global schedule row is the materially simpler design and it does not
merely degrade multi-repository operation — it can suspend it. `write()` upserts
on conflict, so with one shared key the last scope to write owns the next-due time
for every scope: a repository that has just backed off to its longest idle
interval sets that interval for a busy one, and the busy one's sweeps stop
happening for reasons nothing in its own state explains. A requirement to operate
across multiple repositories and organisations is not met by a scheduler one
repository can impose on another.

The keyed design is also already the minimum: one opaque text column, with no
knowledge of what a scope denotes, so nothing in the cadence layer has to learn
the repository or lane vocabulary to stay isolated.

### U-QUEUE-08 — the scheduled-tick timer and its macOS launchd definition

Disposition: keep

Requirements: RQA-NFR-004, RQA-FR-031, RQA-BR-012, RQA-BR-010

Root cause: RQA-NFR-004 `-` (fit, gap/register/nfr.md:404); RQA-FR-031 `-` (fit, gap/register/fr.md:206); RQA-BR-012 `not built` — the unmet obligation is the consumption-against-required-assurance comparison, located in U-RESILIENCE-01/U-DISPATCH-13 (gap/register/br.md:150); RQA-BR-010 `built contrary`, located outside this unit in the live-mode gate escalation (gap/register/br.md:148).

Two `fit` rows rest on this unit's own lines. `RQA-FR-031` cites
`scripts/scheduled-tick.sh:44-47`, `:49-66` and `:68`, and `RQA-NFR-004` cites
`scripts/scheduled-tick.sh:60-62` — in both cases the per-repo-root loop and the
worst-status exit.

That aggregation is what no materially simpler approach supplies. One cron line
per repository gives independence but no single status for the timer as a whole. A
single invocation over several roots either halts on the first failing repository,
which stops ticking the others, or discards the failure and reports success. Both
fit criteria turn on at least two independently configured repositories under
different owners actually being reviewed; continuing through every root while
still surfacing a failure is the specific behaviour that delivers it. The trigger
itself is equally irreducible for `RQA-BR-010`: a timer is the minimum thing that
takes the owner out of discovery.

`RunAtLoad` false is a separate design decision worth naming because
`RQA-BR-012`'s row cites it: loading or reloading the agent must not itself spend
model capacity. The plist's fixed `StartInterval` is the correct half of the split
it documents — launchd cannot vary an interval, so adaptivity, if any survives,
belongs in the cadence table and not here.

`RQA-BR-010` is `conflicting` and this unit is on the compatible side of it: the
contradiction the register describes is a job parked in `human_approval_pending`
on a mechanical gate failure, decided in `approval_evaluate` and `dispatcher`, and
the timer is cited among the behaviours that already run without an operator. A
keep is therefore consistent with that degree rather than in tension with it.

Platform, stated so a later reader does not have to re-derive it:
`launchd.plist.example` is macOS-only. Neither requirement whose `fit` this unit
carries names a host platform — `RQA-NFR-004` at
requirements-specification.md:1045-1056 and `RQA-FR-031` at
requirements-specification.md:993-1004 — and `RQA-FR-031`'s criterion expressly
contemplates two different local machines. The macOS specificity is therefore a
portability observation at this revision, not a requirement failure, and this
analysis adds no requirement for it.

### U-QUEUE-09 — atomic, crash-safe snapshot activation

Disposition: keep

Requirements: RQA-NFR-010

Root cause: RQA-NFR-010 `built contrary`, located outside this unit in U-DISPATCH-20's `_ledger_record` bare `except` (gap/register/nfr.md:400).

A keep against a `conflicting` requirement needs the contradiction located before
it can stand, and the register locates it: the contrary execution is
`_ledger_record` swallowing a ledger-write failure on the authoritative-action
paths, and the row names atomic writes among the behaviours that meet the
requirement. This unit is on the met side.

Why nothing simpler: the fit criterion requires three invariants — unambiguous,
uncorrupted, not partially authoritative — to be checked independently and all to
hold. Two ordered write-to-temp-then-rename operations, archive before pointer,
are what leave the previously active payload byte-for-byte intact when activation
is interrupted; writing either file in place is the simpler alternative and
produces exactly the half-written mixture the requirement forbids. Recomputing the
hash over a payload's own contents at load, rather than trusting the hash stored
alongside it, catches the corruption ordering cannot prevent — a truncated or
externally damaged archive — and the criterion is explicit that a clearly labelled
but corrupted record still fails. Neither half substitutes for the other, so
neither is removable.

### U-QUEUE-10 — content-hashed snapshot identity and pin/resume

Disposition: keep

Requirements: RQA-FR-004, RQA-NFR-005, RQA-FR-012, RQA-NFR-010

Root cause: RQA-FR-004 `-` (fit, gap/register/fr.md:204); RQA-NFR-005 `-` (fit, gap/register/nfr.md:405); RQA-FR-012 `not built` — the unmet obligations are the never-recorded protocol identity and the swallowed ledger write, located in U-RESILIENCE-06 and U-DISPATCH-20 (gap/register/fr.md:184); RQA-NFR-010 `built contrary`, located outside this unit in U-DISPATCH-20 (gap/register/nfr.md:400).

`RQA-FR-004` is `fit` and the register cites this unit for it. The keep argument
is that `RQA-FR-004` and `RQA-FR-012` pull in opposite directions and this
mechanism is what reconciles them: an edited policy
must apply on the *next* review with no redeploy, and an authoritative outcome
must stay reconstructible against the policy in force when it was produced. Live
re-reading alone gives the first and loses the second — an in-flight job's
authority would change under it. Pinning alone gives the second and loses the
first. A content hash pinned per job gives both, and nothing simpler does.

No materially simpler identity suffices either. A policy version integer or a
config file mtime is the simpler candidate and fails in both directions: it is
maintained by hand or by the filesystem rather than derived from the bytes, so a
policy edited without a bump is indistinguishable from one that was not, and a
later reader cannot reproduce it from the archived payload. Sorted-key canonical
JSON over configuration and policy together is what makes the hash independently
recomputable by anyone holding that payload — the property `RQA-FR-012`'s
single-command reconstruction needs, and the reason the same hash can serve
`RQA-FR-004`'s "did the policy change" question without a second record.

`pin()` refusing to re-pin a result to a different hash is the other half and is
not decoration: without it a result could be relabelled to a snapshot it was not
produced under, which is precisely the partially authoritative outcome
`RQA-NFR-010` forbids. Neither of `RQA-FR-012`'s unmet obligations is decided
here; both are additive or corrective work in the ledger units.

### U-QUEUE-11 — validated job-transition table and enforcement

Disposition: keep

Requirements: RQA-NFR-007, RQA-NFR-010, RQA-FR-038

Root cause: RQA-NFR-007 `built then orphaned` — the orphaned code is the author-triage remediation step and the degrade ladder, located in U-DISPATCH-26 and U-DISPATCH-23 (gap/register/nfr.md:392); RQA-FR-038 `not built` — the unmet obligation is the unobservable credential floor and ceiling, located in U-AUTHORITY-02 (gap/register/fr.md:202); RQA-NFR-010 `built contrary`, located outside this unit in U-DISPATCH-20 (gap/register/nfr.md:400).

Both non-`fit` causes are located outside this unit and the register says where,
so neither is a finding against the transition table; both rows cite this unit for
what does hold.

Why no materially simpler approach: `RQA-FR-038`'s obligation is a clear, safe,
**recoverable** non-success stop, and the mechanism the register credits is
`safe_stop` being a legal target from every one of the fourteen nonterminal
statuses. A free-form status string, with each failure site choosing its own stop
label, is the simpler alternative and has no way to be complete — every new
in-progress status is a new place where a stop has to be invented, and nothing
checks that one exists. The module-load assertion that `ALL_STATES` equals the
table's key set is what turns that from a convention into an import failure, and
it is the reason "there is always a legal stop" is checkable rather than asserted.
Against `RQA-NFR-010`, an unvalidated status write is itself an ambiguity: a job
that reached a terminal, authoritative-looking status without passing the
transitions that earn it is indistinguishable from one that did.

The keep does not extend to `states.assert_job_exists`. It has no caller, the
refusal a reader would expect from it is performed instead by `common.py`'s
`current_status(job_id) is None` check, and `RQA-FR-034`'s row
(gap/register/fr.md:209) names it among components retained serving no
requirement. Removing it is a subtraction this keep does not defend. Search re-run
and quoted as it returned:

```
$ grep -rn "assert_job_exists" scripts/
scripts/states.py:129:def assert_job_exists(current: str | None) -> None:
$ echo $?
0
```

### U-QUEUE-12 — legacy `action` → `completed` compatibility path

Disposition: bin

Requirements: RQA-FR-034

Root cause: RQA-FR-034 `not built` (gap/register/fr.md:209).

`RQA-FR-034` is a `full gap` and this transition is the register's worked
counter-example for it: the only recorded justification is "preserved for existing
callers", the docstring names no caller, and no code under `scripts/` transitions
a job into the `action` status. That is what the fit criterion disqualifies — a
ground named with no supporting specific content — so removing the transition
moves the row toward `fit` rather than away from it. `RQA-FR-034` is this unit's
only requirement in the evidence file, and the `RQA-FR-034` row is the only
register row that cites the unit at all, so nothing depends on the behaviour
being retained:

```
$ grep -rc "U-QUEUE-12" gap/register/br.md gap/register/fr.md gap/register/nfr.md
gap/register/br.md:0
gap/register/fr.md:1
gap/register/nfr.md:0
$ echo $?
0
```

The single hit is `gap/register/fr.md:209`, the `RQA-FR-034` row cited above.

The `"action"` search re-run at this revision, stdout as it was returned:

```
$ grep -rn '"action"' scripts/
scripts/dispatcher.py:653:    _ledger_record(state, job, head_sha, "action", {
scripts/dispatcher.py:846:    _ledger_record(state, job, head_sha, "action", {
scripts/dispatcher.py:1027:    _ledger_record(state, job, head_sha, "action", {
scripts/queue.py:34:               "action", "retryable", "held")
scripts/ledger.py:41:ACTION = "action"
scripts/notify.py:118:        "action_required": request.get("action"),
scripts/approval.py:59:    "rationale", "action", "decision", "decision_actor", "decided_at",
scripts/approval.py:143:        "action": action,
scripts/lease.py:125:    parser.add_argument("action", choices=["claim", "release", "verify"])
scripts/states.py:59:        "action",          # preserved legacy sink -> completed
scripts/states.py:89:    "adjudication": frozenset({"action", "approval_evaluation", "human_required", "held", "retryable", "superseded", "safe_stop"}),
scripts/states.py:104:    "action": frozenset({"completed", "held", "human_required", "superseded", "approval_evaluation", "safe_stop"}),
$ echo $?
0
```

What is lost, precisely: the `"action"` member of `ALL_STATES`
(`scripts/states.py:59`), its transition-table entry (`scripts/states.py:104`), the
`"adjudication" -> "action"` edge (`scripts/states.py:89`), and the `"action"`
member of `queue.py`'s `NONTERMINAL` tuple (`scripts/queue.py:34`). The
consequence to carry into the removal is the count: `NONTERMINAL` drops from
fourteen members to thirteen. U-QUEUE-11's kept guarantee — `safe_stop` legal from
every nonterminal status — is a universal over that set and survives the removal
unchanged; `RQA-FR-038`'s register row quantifies over "all 14 nonterminal
statuses" and would need its number re-read, not its judgement revisited. The two
assertions in `tests/test_errors_states.py` that exercise the edge go with it;
per [`../methodology.md`](../methodology.md) §2.3 they establish nothing that
keeps it.

Occurrences in the output above that are different subjects and must not be swept
up with it: `ledger.ACTION` (an entry kind), `approval.py`'s packet field,
`notify.py`'s `action_required` key, `lease.py`'s CLI positional, and the three
`_ledger_record(..., "action", ...)` call sites, which write a ledger entry kind
and not a job status.

### U-QUEUE-13 — closed-PR ingestion into independent, fail-closed calibration samples

Disposition: bin

Requirements: RQA-NFR-006

Root cause: RQA-NFR-006 `-` (fit, gap/register/nfr.md:406).

This is, in substance, a unit whose behaviour serves no frozen requirement, and
the one mapping it carries does not change that. The evidence file's single row
maps to `RQA-NFR-006`, but the claim that row makes is about **how the module is
reached** — locally, from a documented operator command, with no other product
caller — not about calibration sampling. The unit's own prose concedes the rest:
the outcome discipline, the hindsight rule and the fail-closed check evidence
"have no genuine requirement tie", and the specification search it quotes at
[`../evidence/queue.md`](../evidence/queue.md):428-437 establishes that
calibration and backtesting are not requirement subjects in the frozen
specification.

`RQA-NFR-006` is `fit` without this unit. Its row's evidence cell names
U-POLICY-06, U-RESILIENCE-10, U-RESILIENCE-16, U-DOCS-03,
`scripts/common.py:97-111` and `scripts/config.py:27-28`, and no `queue` unit
(gap/register/nfr.md:406) — so removing this behaviour costs that row nothing. No
register row cites the unit at all; search re-run and quoted as it returned:

```
$ grep -rn "U-QUEUE-13" gap/register/
$ echo $?
1
```

What is lost is real and should not be understated: `history.py` is the only
producer of the `--samples` file `scripts/shadow.py` consumes, which
`OPERATORS.md:300-301` states in terms — "`history.py` produces the samples file;
`shadow.py` consumes it. Nothing else produces it — a `--samples` file does not
materialise on its own." Binning this unit therefore strands `shadow.py`'s
backtest mode. That is a consequence for the `verdict` cluster's own units, not a
disposition this lane makes; those units are likewise cited by no register row, so
no register row's degree changes with them, but the call belongs to that lane:

```
$ grep -rn -e U-VERDICT-19 -e U-VERDICT-20 -e U-VERDICT-21 gap/register/
$ echo $?
1
```

Nothing else in the estate is lost. No file under `scripts/` imports or calls
`history`; the search returns four hits, none of them an import or a call site:

```
$ grep -rn -e "import history" -e "from history" -e "history\." scripts/
scripts/checks.py:10:    history.py:189      (...).upper() not in ("SUCCESS", "NEUTRAL", "SKIPPED")
scripts/route_probe.py:114:    """Persist real transport health; a probe result is not a guess from history."""
scripts/github_rest.py:100:          - `history.py:240`  — `--with-files` ingest, so every sample lost its
scripts/shadow.py:248:                     remaining floor cannot be reconstructed from history at all,
$ echo $?
0
```

### U-QUEUE-14 — the persisted PR-fact cache is the sole source of the observed current head used to detect a stale review

Disposition: keep

Requirements: RQA-FR-006, RQA-NFR-010, RQA-BR-007

Root cause: RQA-FR-006 `not built` — the unmet obligation, per-file invalidation of review obligations, is implemented nowhere in the tree, so it has no location; the register's row records the planner's changed-path fan-out as the nearest existing mechanism and states in terms that it "is not cross-revision invalidation" (gap/register/fr.md:178); RQA-NFR-010 `built contrary`, located outside this unit in U-DISPATCH-20 (gap/register/nfr.md:400); RQA-BR-007 `-` (fit, gap/register/br.md:141).

The kept mechanism is a freshness contract rather than a cache: `prs.payload`'s
head is written only by the reconciliation pass that observed it, so the head the
`head_matches` gate compares against is **independent of the job being judged**.
That independence is the entire content of what the requirement needs here. The
regression the test module records is the dependent case — `_load_pr_facts`
falling back to the job's own head, at which point the gate compares a value with
itself and can never fail — and a gate that cannot fail is the partially
authoritative outcome `RQA-NFR-010` forbids, because `evaluate()` withholds
`_persist_eligible` only on the branch a failed gate takes.

No materially simpler approach suffices. The alternatives are to drop the
independent observation, which is the regression above, or to read the head live
from GitHub at gate-evaluation time. The second is not simpler in the way that
matters: it makes an authority gate's own evaluability depend on the REST budget
that one of its sibling gates, `rate_limit_ok`, exists to police, and it still
needs somewhere to record what was observed for the reconstruction `RQA-FR-012`
asks for. The sweep already performs the observation; making that observation the
record costs one persisted payload and no additional call.

`RQA-FR-006` is a `full gap` and this unit does not close it — what is missing is
computing which obligations a given file change invalidates, and the register
cites this unit's supersession only as the coarser thing present instead. That
work is additive, and it consumes an independently observed current head rather
than replacing one, so keeping this unit is a prerequisite for closing that row
rather than an obstacle to it.
