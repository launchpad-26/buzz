# RQA gap analysis — dispositions: dispatch

Cluster `dispatch` per [`../clusters.md`](../clusters.md): turning a queued job into a
run — the dispatcher and its runtime-operations subcommands, model runners, the
plan, and isolated author worktrees. Revision `9267b6308714454a3b987622d90cda03a8972827`.
Paths are relative to `launchpad/skills/review-queue-automation/`, per
[`../methodology.md`](../methodology.md).

One entry per `### U-DISPATCH-NN` heading of
[`../evidence/dispatch.md`](../evidence/dispatch.md), in that file's order. The four
dispositions are defined in [`../methodology.md`](../methodology.md) §7, and the
justification rule binding every `keep` and `salvage` is stated there: no unit is
retained on account of incumbency, test coverage or present behaviour; each names the
requirement it serves and says why no materially simpler approach suffices.

Every gap degree and root cause quoted below is
[`../register/br.md`](../register/br.md), [`../register/fr.md`](../register/fr.md) and
[`../register/nfr.md`](../register/nfr.md) exactly as written. This file follows those
rows and changes none of them.

## Searches these dispositions rest on

**S-D1 — the frozen specification obliges no backup, restore, retention, purge or
cooldown-clearing behaviour.** Bears on U-DISPATCH-04, U-DISPATCH-05, U-DISPATCH-06.

```
$ grep -rniE "backup|restore|retention|purge|archive|housekeep|cooldown" requirements/requirements-specification.md
requirements/requirements-specification.md:937:*In plain terms: The system only switches to a backup model or provider when that's been explicitly turned on — never automatically.*
```

That single hit is the plain-terms gloss on the configured-fallback obligation — a
backup *model or provider* — not a copy of, or a purge of, anything the system stores.

---

### U-DISPATCH-01 — Onboarding/config fail-closed gate

Disposition: salvage
Requirements: RQA-NFR-018
Root cause: RQA-NFR-018 is `conflicting` / `built contrary`, and its row locates both
widening executions inside `resolve_snapshot` (`scripts/dispatcher.py:1584-1593`,
`:1567-1571`) — U-DISPATCH-09's lines, not this gate's. The requirement is therefore open
across this cluster and closing it is subtractive elsewhere, so
[`../methodology.md`](../methodology.md) §7's rule applies: a unit whose requirements are
all `conflicting` is not a `keep`. The mechanism is carried forward instead of the code.

The mechanism to lift: **a single fail-closed admission gate sited before subcommand
dispatch, refusing every command when no valid repo-local config resolves, and naming the
missing-config reason and the onboarding command in the refusal.** Sited *before*
dispatch is the load-bearing half — the gate's value is that the unreadable-policy case is
answered once for the whole command surface rather than per activity, and that refusing is
the only thing it does.

RQA-NFR-018 forbids a malformed or unreadable policy widening authority, and its fit
criterion extends the check to a policy input unreadable for a reason other than
malformation — permission denied, unavailable, timed out. The gate at
`scripts/dispatcher.py:2242-2255` answers the whole unreadable case once, for every
subcommand, before any GitHub or model activity: nothing downstream can widen because
nothing downstream runs. The materially simpler alternatives both fail the requirement.
Substituting an empty or disabled configuration and letting subcommands proceed makes
non-widening depend on every per-activity gate downstream being consulted, and
RQA-NFR-017's row records that of the six activities `authority.ACTIVITIES` declares,
only `comment`, `approve` and `request_changes` are ever passed to `mode_for`/`can_act`
(search S4 of [`../register/nfr.md`](../register/nfr.md)) — so three activities would run
past a gate nobody reads. Repeating the check per subcommand restates one refusal nine
times, with nine opportunities to omit it. Naming the missing-config reason and the
onboarding command in the refusal is what keeps a fail-closed default distinguishable
from a broken install, which is the difference between a gate an operator can clear and
one they work around.

---

### U-DISPATCH-02 — Exclusive, crash-recoverable runtime lock

Disposition: salvage
Requirements: RQA-NFR-010
Root cause: RQA-NFR-010 is `conflicting` / `built contrary`; its row names the contrary
execution as `_ledger_record`'s bare `except` (U-DISPATCH-20) and says the same module's
conversion of an equivalent failure into `SafeStopSignal` is the behaviour that path
should have taken. The requirement is open on that account, and
[`../methodology.md`](../methodology.md) §7 forbids `keep` for a unit whose requirements
are all `conflicting`; the earlier reading of this unit as sitting "on the compatible
side" of that row was an argument against the rule rather than an exception the rule
grants, and it is withdrawn.

The mechanism to lift: **exclusive access to a state directory delegated to the kernel —
an exclusive, non-blocking `fcntl.flock` on a lock file inside that directory, released by
the kernel when the owning process dies — with contention reported as a named, successful
no-op rather than as an error.** Both halves are the asset: kernel release is what makes a
crash self-healing without an owner-liveness heuristic, and `sweep_already_running` with
exit 0 is what lets a timer overlap a manual run without a failure an operator must
interpret.

RQA-NFR-010's fit criterion checks three invariants independently — not ambiguous, not
corrupted, not partially authoritative. Two commands writing one state directory at once
is the corruption case, and this is the mechanism that makes it impossible rather than
unlikely. The decision worth carrying is that exclusion is delegated to
the kernel: an exclusive non-blocking `fcntl.flock` on `runtime.lock`
(`scripts/common.py:156-165`) is released by the kernel when the owning process dies. The
materially simpler alternatives — a PID file, or a `locks` row in the same SQLite
database the lock protects — are simpler in code and strictly worse here, because after a
crash each needs either an owner-liveness heuristic or a manual clear, and both endings
are bad: a stale lock wedges the harness against RQA-NFR-007's progression obligation, or
an override defeats the exclusion the lock exists to provide. Reporting
`sweep_already_running` and exiting 0 rather than failing is what lets a launchd timer
overlap a manual run without producing an error an operator has to interpret.

---

### U-DISPATCH-03 — Local health and status diagnostics (no network, mutation, or model calls)

Disposition: rework
Requirements: RQA-NFR-010, RQA-FR-016
Root cause: RQA-FR-016 is `full gap` / `not built`, and its row cites this unit's
`runtime_status` (`scripts/dispatcher.py:2125-2137`) as the nearest reachable command that
does not do it — "`runtime_status` takes no PR argument at all… Nothing maps the 29 job
statuses onto AC08's six values." RQA-NFR-010 is `conflicting` / `built contrary` at
U-DISPATCH-20's swallow.

Retained in intent: a local, side-effect-free way to ask the state directory what it
holds — no network, no mutation, no model call — which is exactly the property that makes
the command usable when the failure being investigated is in the network path; and the
SQLite integrity check, which is the only reachable probe of RQA-NFR-010's "not corrupted"
limb. What changes is the reporting shape, not its plumbing. RQA-FR-016 asks for one
command that returns a *named pull request's* current disposition from a six-value set
with its reason; `runtime_status` returns per-status counts for the whole directory and
accepts no PR argument, so it cannot answer that question by being called differently. The
projection from the 29 internal job statuses onto the six values does not exist anywhere,
which is why the row's root cause is `not built`: the rework has to produce that mapping
and change what the command returns, and `runtime_health`'s degraded-reason reporting
(open breakers, oldest unfinished job) is the model to follow, since it already answers a
question with a cause attached rather than with a count.

---

### U-DISPATCH-04 — Backup: a consistent local copy of the state database and snapshot archive

Disposition: bin
Requirements: RQA-NFR-010
Root cause: RQA-NFR-010 is `conflicting` / `built contrary`, and its row states the unmet
obligation as the discarded ledger append on the authoritative-action paths — not the
absence of a copy of the state directory.

What is lost: a one-command consistent copy of `state.sqlite3` plus the `snapshots`
archive into a timestamped destination, and with it a design decision worth writing down
even though the responsibility goes — a WAL-mode SQLite database is copied with
`sqlite3.Connection.backup` and never with a file copy, because a `shutil.copy` taken
while a WAL write is in flight yields a torn file that reads as a database. That is a note
for whoever writes a replacement that copies a database; it is not a responsibility the
specification asks for.

No requirement depends on this unit. S-D1 shows the frozen specification's only
occurrence of backup/restore vocabulary is a gloss about a fallback *model or provider*.
RQA-NFR-010's three invariants are properties of a review outcome at the moment a failure
occurs; a copy taken beforehand neither establishes nor preserves them, and one taken
afterwards records the damage rather than preventing it. RQA-FR-012's single-command
reconstruction runs `explain.py` against the live state directory
([`../register/fr.md`](../register/fr.md), RQA-FR-012 evidence: `scripts/explain.py:53-81`),
not against a backup, so binning this takes nothing away from that row either. The
mapping to RQA-NFR-010 is read here for what the requirement's text carries, in the spirit
of the maintainer's 2026-09-06 no-nearest-fit ruling: a mapping that survived wave 1 is
still not evidence that a behaviour is required if the requirement's own words do not
cover it.

---

### U-DISPATCH-05 — Cooldown/circuit-breaker reset

Disposition: bin
Requirements: RQA-NFR-010
Root cause: RQA-NFR-010 is `conflicting` / `built contrary` at `_ledger_record`'s bare
`except`; nothing in that row's unmet obligation concerns the lifetime of a provider
cooldown or a circuit-breaker row.

What is lost: an operator's ability to end a cooldown before it expires, and to clear both
cooldown stores — the `providers` table and the circuit breakers — in one command with a
scope filter.

No requirement depends on it, and both stores already return to service without it.
`budget.breaker_state` half-opens an open breaker whose `open_until` has passed
(`scripts/budget.py:259-260`), and `_expired` treats an unparseable timestamp as expired
precisely so a bad value cannot pin a breaker open for ever (`scripts/budget.py:270-276`);
a provider route is available again as soon as `unavailable_until` is in the past
(`scripts/routing.py:108-113`). So the command shortens a wait — it is not the path back
to a working state, which is what the evidence row's "no recorded path back" phrase would
need it to be. S-D1 shows the specification states no cooldown-clearing obligation of any
kind, and RQA-NFR-010's text governs review outcomes rather than the lifetime of a
cooldown row. Visibility of an open breaker is not lost with it: `runtime_health` reports
open breakers by name (U-DISPATCH-03), and that unit is reworked, not binned.

---

### U-DISPATCH-06 — Retention purge of terminal-job artifacts, dry-run by default

Disposition: bin
Requirements: RQA-FR-012, RQA-NFR-010
Root cause: RQA-FR-012 is `partial gap` / `not built`, and its two failing elements are the
never-recorded protocol identity and `_ledger_record`'s swallowed write — neither is
retention. RQA-NFR-010 is `conflicting` / `built contrary` at that same swallow.

What is lost: a dry-run-by-default purge of artifact bytes for jobs already in one of the
eight `TERMINAL_STATUSES` and older than a configured window, and the `retention_manifest`
ledger entry that records each purged artifact's size and sha256 — or a path-plus-error
marker when the file will not read — so the deletion itself stays reconstructible.

No requirement depends on it. S-D1 finds no retention, purge or storage obligation in the
frozen specification. And the unit's most careful properties are mitigations of a risk it
introduces rather than obligations it discharges: RQA-FR-012's reconstruction is strictly
better served by artifacts that were never purged, and the reason the purge must spare
`jobs`, `ledger_entries`, `mutations`, `approval_decisions` and `human_requests` is that
deleting them would break that row further. Removing the purge removes the risk and the
mitigation together. The eligibility rule it encodes is worth reading alongside
U-DISPATCH-07 — `safe_stop` is one of those eight terminal statuses
(`scripts/dispatcher.py:1882-1885`), which is what makes crash recovery's choice of target
consequential — but that is a fact about the status set, not a reason to retain a purge.

One operational point, recorded with its standing made explicit: an unbounded artifact
directory on the single contributor's machine that RQA-NFR-006 describes is a genuine
concern, and the frozen specification does not state it. [`../methodology.md`](../methodology.md)
§1 forbids this analysis to add a requirement on account of what the implementation does,
so the concern is reported here and decided by whoever owns the specification, not
answered by keeping code no frozen requirement obliges.

---

### U-DISPATCH-07 — Crash recovery: releasing stranded leases and safe-stopping interrupted jobs without re-deciding

Disposition: rework
Requirements: RQA-FR-027, RQA-FR-038, RQA-NFR-010
Root cause: RQA-FR-027 is `partial gap` / `not built` — "Supplying an approval decision
resumes a `human_approval_pending` job through `approval_revalidation` with no re-review.
Nothing else resumes." RQA-FR-038 is `partial gap` / `not built` and cites this unit for
the recoverable-stop half. RQA-NFR-010 is `conflicting` / `built contrary` at
U-DISPATCH-20's swallow.

Retained in intent, and these three are the reason recovery is a responsibility rather
than a script: every lease recorded in the state directory is released through the normal
REST-verifying helper rather than deleted locally, so recovery cannot drop a lease a live
process still holds; no model or approval decision is ever re-run, so recovery cannot
manufacture a second authoritative outcome; and jobs legitimately waiting on a person —
`human_approval_pending`, `human_required`, `degraded_draft`, `held`, `retryable`, and
queued `detected` — are deliberately untouched, so recovery cannot discard pending human
work.

What changes is the only outcome recovery offers an interrupted job. `safe_stop` is a
member of `TERMINAL_STATUSES` (`scripts/dispatcher.py:1882-1885`), and queue reconciliation
creates at most one job per `(repo, number, head, lane)` key, skipping creation when a row
for that key already exists (`scripts/queue.py:116-118`). Together those two facts mean a
job killed mid-panel is terminated at that revision and no replacement job is ever created
for the same head — the PR advances only if its head moves. That is where RQA-FR-027's
"nothing else resumes" is decided for the crash case, and it is why RQA-FR-038's
recoverable-stop obligation is met in form while progression is not. A rework must let
recovery return an interrupted job to the last durable state it can be resumed from;
stopping at the floor is the safe answer to a question recovery should not be asking of
every job.

---

### U-DISPATCH-08 — Bounded managed sweep: queue reconciliation, FIFO job selection, and cadence gating

Disposition: keep
Requirements: RQA-BR-012
Root cause: RQA-BR-012 is `partial gap` / `not built`; its row cites this unit on the met
side ("the sweep is batch-bounded and cadence-gated") and locates the unmet obligation in
the absent comparison of recorded consumption against the policy's stated required
assurance, which no code performs and which is decided nowhere in this unit.

RQA-BR-012 requires review activity to use scarce model capacity efficiently, given the
capacity is shared with implementation work. Two properties here supply that bound and
neither has a materially simpler equivalent. The batch limit caps how many jobs one
invocation may start, so a backlog cannot turn a single tick into an unbounded run of
panels — a bound expressed in wall-clock time instead would still admit an arbitrary
number of concurrent spends within the window. And the persisted cadence decouples "the
timer fired" from "a sweep is due": `tick` consults `cadence_read`/`cadence_due` and
reports `not_due` without a GitHub read or a model call, and reschedules from
`cadence_decide` only after a sweep actually ran. The simpler design — sweep on every
timer fire — pays the inventory read and potentially a panel on each fire regardless of
whether anything changed, which is the inefficiency the requirement names. The stable
`(created_at, id)` FIFO order is what keeps the batch bound from starving an old job: a
bound applied over an unstable order silently reorders work every sweep, so a job can be
deferred indefinitely without anything recording that it was.

---

### U-DISPATCH-09 — Snapshot pinning and capability-clamped authority: a job never runs with more authority than its pinned snapshot or proven GitHub capability grants

Disposition: rework
Requirements: RQA-NFR-018, RQA-FR-004, RQA-NFR-005, RQA-NFR-010
Root cause: RQA-NFR-018 is `conflicting` / `built contrary`, and its row names **both**
reachable widening executions as being inside `resolve_snapshot` — this unit
(`scripts/dispatcher.py:1584-1593`, `:1567-1571`). RQA-FR-004 and RQA-NFR-005 are `fit`
and both cite this unit. RQA-NFR-010 is `conflicting` / `built contrary` at
U-DISPATCH-20's swallow.

Retained in intent: a job's governing configuration and policy are pinned at dispatch and
re-read from the pin on resume, so editing the repo-local config mid-flight cannot
retroactively change an in-flight job's authority, thresholds or model routes — that
mechanism is what RQA-FR-004 and RQA-NFR-005 are `fit` on; and the GitHub capability probe
is monotone downward, able only to reduce the authority the pinned snapshot already
grants, probed once per invocation rather than once per job.

What changes is the failure branch, and it must change rather than be added to. When
`build_snapshot` raises for an absent or unresolvable policy section
(`scripts/snapshot.py:117-119`), `resolve_snapshot` returns the caller's unclamped
`local_cfg` instead of the clamped configuration the snapshot was being built from — so an
unreadable policy hands the job whatever approve authority the live configuration carries,
which is exactly what RQA-NFR-018 forbids and why its degree is `conflicting`. The instinct
in the neighbouring branch is right and worth carrying: refusing to silently upgrade a job
whose pinned snapshot hash no longer resolves, and recording the missing-archive reason, is
the correct handling of an unresolvable pin. Recording the reason while returning a wider
configuration is the defect, and no additive change closes it.

---

### U-DISPATCH-10 — Review-lease claim and guaranteed release around one job's dispatch

Disposition: keep
Requirements: RQA-NFR-010, RQA-BR-007
Root cause: RQA-NFR-010 is `conflicting` / `built contrary` at U-DISPATCH-20's swallow, not
here. RQA-BR-007 is `fit`, and its row rests in part on the local-holder check at
`scripts/dispatcher.py:1699-1700` — a line inside this unit's own evidence range in
[`../evidence/dispatch.md`](../evidence/dispatch.md) (`:1684-1720`). That row attributes
the line to U-QUEUE-04, which is the queue cluster's view of the same lease contract;
`scripts/dispatcher.py` is in this cluster's disposition scope, and per
[`../methodology.md`](../methodology.md) §4 an evidence citation carries no cluster
restriction. So this unit's requirement pairing is not `keep`-enabling padding: it predates
round 2 and rests on a register row's own citation, not on a nearest fit.

Two concurrent dispatches against one pull request is how duplicated reviewer work and a
duplicated public artifact arise, and the runtime lock (U-DISPATCH-02) does not cover it:
that lock is scoped to one state directory, so it orders commands on one machine and says
nothing about a second checkout, a second machine or a second reviewer identity claiming
the same PR. The lease is the only mechanism in this cluster scoped to the PR rather than
to the local process — checked against the two other exclusion or gating units,
U-DISPATCH-02 (one state directory's `runtime.lock`) and U-DISPATCH-11 (a per-lane gate,
not per PR) — so RQA-BR-007's "requesting review again queues no second
review" and RQA-NFR-010's prohibition on a partially authoritative duplicate both rest on
it. Two ordering decisions carry the weight. The claim happens *before* any model spend —
a claim taken afterwards would already have paid for the duplicate work the lease is there
to prevent. And the release is in a `finally` that cannot raise, so an unexpected exception
cannot strand the lease: the materially simpler "claim, run, release on success" leaves one
crashed job holding a PR indefinitely, which converts a transient failure into a
permanently unreviewable pull request — a worse outcome than the duplication being avoided.

---

### U-DISPATCH-11 — Canary/lane gating before any dispatch work begins

Disposition: rework
Requirements: RQA-FR-004, RQA-NFR-005
Root cause: both are `fit`, with root cause `-`. The rework does not follow from an unmet
obligation; it follows from [`../methodology.md`](../methodology.md) §7's other clause — a
unit whose requirement a materially simpler approach would serve is `rework`, whatever its
present behaviour.

The responsibility is required: a per-lane gate consulted before any GitHub or model
activity, changeable without a rebuild or redeploy, is what RQA-FR-004 and RQA-NFR-005
describe, and the `gated` result with no GitHub or model activity is the right shape for a
refusal. What changes is that one answer has two authoritative sources. `canary_allowed`
returns the `canaries` row's status whenever a row exists and consults the repo-local
config key only otherwise (`scripts/dispatcher.py:1801-1805`). The config-key path alone
discharges both requirements — they are about an edit taking effect on the next review with
no build or deployment step — so the SQLite row is not carried by the requirements this
unit is credited with. It also costs something specific: the row is read live at dispatch,
so the effective gate is not part of the snapshot the job pins in U-DISPATCH-09, and two
operators reading the two sources can reach opposite conclusions about whether a lane is
approved. One source of truth for the gate, on the same path as the rest of the job's
pinned authority, is what the requirements need.

---

### U-DISPATCH-12 — Pre-spend budget reservation gates the panel

Disposition: salvage
Requirements: RQA-FR-022, RQA-FR-039
Root cause: both are `conflicting` / `built contrary`, and both rows locate the contrary
execution inside `budget.reserve` — the `checks` tuple covering only `per_pr_tokens` and
`per_repo_daily_tokens` while `per_model_daily_tokens` is configured, defaulted and never
projected (`scripts/budget.py:396-401`, `:408`), and the equality boundary on the two axes
that are enforced. That is U-RESILIENCE-01's mechanism in the resilience cluster, behind
this call. Neither requirement is met, so
[`../methodology.md`](../methodology.md) §7's rule applies directly — a unit whose
requirements are all `conflicting` cannot be a `keep`, and §7 defines `keep` as requiring
the unit to *meet* the requirement, which the paragraph below states in terms that it does
not. The ordering is carried forward as a mechanism instead.

The mechanism to lift: **the spend gate is consulted before the work it bounds, and its
refusal is a value rather than an exception** — the reservation is taken before the panel
runs, and a refused reservation carries the downgrade to apply (`human_required` or
`degraded_draft`), so the caller demotes the job with no model call in between. Both halves
matter independently: ordering is what makes a bound respected rather than noticed, and
refusal-as-a-value is what keeps a budget decision distinguishable from a failure.

What this unit decides is ordering and consequence, and both requirements are about a bound
being respected rather than noticed afterwards. The reservation is taken before the panel
runs (`scripts/dispatcher.py:1108-1150`), and a refusal is *returned* rather than raised so
the caller applies the downgrade the reservation demands — `human_required` or
`degraded_draft` — with no model call in between (`scripts/dispatcher.py:1252-1286`). No
materially simpler arrangement gives that guarantee: recording consumption after the panel
and comparing later cannot refuse a spend that has already happened, which is the
"exceeded and then noticed" failure the code's own comment names; and raising on refusal
would convert a budget decision into an exception the sweep must interpret, losing the
distinction between a job that must not spend and a job that failed. Salvaging this unit is
not a claim that RQA-FR-022 or RQA-FR-039 is met — neither is — but that the pre-spend
ordering is the mechanism they require, and that the change both rows demand is subtractive
inside `budget.reserve` and additive nowhere here.

---

### U-DISPATCH-13 — Post-panel spend recording uses the reservation as a stand-in when no actual token count is available

Disposition: rework
Requirements: RQA-FR-021
Root cause: `partial gap` / `not built` — runners report no token count, so the reservation
is written into `cost_ledger` as what the attempt cost, and the row records that the
insert's columns (`scripts/budget.py:223-231`) carry a `kind` separating a reservation row
from a spend row but nothing separating an estimate from a measurement.

The responsibility — every panel run records its consumption against the job — is required
and stays. The shape is wrong at one line:
`spend = int(result.get("budget_tokens") or reserved_tokens or 0)`
(`scripts/dispatcher.py:1325`) puts an estimate and a measurement into the same field with
nothing to tell them apart afterwards, so the record cannot answer the question it exists
to answer. The consequence is not local to this row: RQA-BR-012's single dependency is
recorded as substrate on exactly this point — the comparison against required assurance
"acts on a recorded consumption figure that RQA-FR-021's behaviour must first produce as a
measurement, or at least mark as not one". So what changes is that a recorded figure must
carry its own provenance; whether a transport can be made to report tokens is a separate
question this analysis does not answer and the disposition does not presume. One property
is worth keeping through the rework: the stand-in is an upper bound, never lower than the
reservation, so a mis-recorded figure makes the next reservation stricter rather than
looser.

---

### U-DISPATCH-14 — Panel-driving evidence and degradation loop

Disposition: keep
Requirements: RQA-BR-012, RQA-FR-026, RQA-FR-038, RQA-NFR-007, RQA-NFR-010
Root cause: RQA-BR-012, RQA-FR-026, RQA-FR-038 are `partial gap` / `not built` and
RQA-NFR-007 is `partial gap` / `built then orphaned`; each row cites this unit among the
met behaviours, and each locates its unmet obligation elsewhere — the assurance comparison
for BR-012, the bare `"HUMAN"` escalation reason for FR-026 (U-DISPATCH-15's lines), the
unobservable credential invariants for FR-038, and the orphaned worktree and degrade
mechanisms for NFR-007 (U-DISPATCH-26, U-DISPATCH-23). RQA-NFR-010 is `conflicting` /
`built contrary` at U-DISPATCH-20's swallow.

Three decisions carry these requirements and each has a simpler alternative that fails.
A `MISSING_EVIDENCE` verdict raises out of the drive loop instead of re-entering it, and
the response is exactly one bounded, deterministic gather: re-running the identical loop
is the simpler option and it is the one RQA-BR-012 forbids, because it spends shared
capacity repeating a call whose inputs have not changed. A gather that itself fails
escalates naming that failure, which is the concrete cause RQA-FR-026 demands instead of a
generic notice. And a panel that completes with a reviewer slot still empty after its
fallback chain becomes `degraded_draft` — a distinct, explicitly non-authoritative
artifact — rather than either a verdict or an error: RQA-NFR-010 forbids a partially
authoritative outcome, and both simpler options produce one, since treating an incomplete
panel as complete publishes an unearned verdict while failing the job discards the work and
the progression RQA-NFR-007 requires. `drive(minimum, assess, max_steps=6)` bounds the loop
structurally rather than by timeout, so the bound holds even when each step is fast.

---

### U-DISPATCH-15 — Approval evaluation and human-escalation routing

Disposition: rework
Requirements: RQA-FR-026, RQA-FR-011, RQA-FR-028, RQA-FR-037, RQA-NFR-010
Root cause: RQA-FR-026 is `partial gap` / `not built`, and the obligation its row records
as unmet is decided in this unit's range — "any non-SUCCESS, non-REQUEST_CHANGES decision
transitions to `human_required` with the bare decision label `"HUMAN"` as its reason"
(`scripts/dispatcher.py:1408-1417`). RQA-FR-011 and RQA-FR-037 are `conflicting` /
`built contrary` at `human_cli.persist_human_approval` in the authority cluster;
RQA-FR-028 is `conflicting` / `built contrary` at the non-live terminal branches
(U-DISPATCH-17, U-DISPATCH-18); RQA-NFR-010 is `conflicting` / `built contrary` at
U-DISPATCH-20's swallow.

Retained in intent: evaluation runs on persisted PR facts and collected verdicts before any
action is taken, so no action can precede its own authorisation; and an escalation is
enqueued as a durable request whose delivery failure is logged and reported but never
removes it from the pending queue, so a notification problem cannot silently discard a
human's outstanding decision.

What changes is what the escalation carries. Routing by decision label rather than by cause
is a structural choice, not a missing string: `classify` returns the same `"HUMAN"` label
for a reserved-for-human signal, for material disagreement and for other distinct
conditions, so the condition that produced the escalation is known where the decision is
taken and discarded before the request is written. RQA-FR-026 requires the record to name
the specific unresolved decision, conflicting judgement, evidence gap, required information
or authority requirement, and a reader of the request cannot recover which of those it was.
The target shape is already present on the same path — the evidence-gather failure, the
uncorroborated finding, `authority_not_live`, and the failed gates with risk score and band
each name their cause — so the rework is to make the terminal path carry what the
neighbouring paths already carry.

---

### U-DISPATCH-16 — Live-approval mutation execution and its guarded failure paths

Disposition: keep
Requirements: RQA-FR-028, RQA-FR-026, RQA-NFR-010
Root cause: RQA-FR-028 is `conflicting` / `built contrary`, and its row names the forbidden
executions as the non-live terminal branches while naming this unit as one of the two
submissions that do exist and are reachable — "APPROVE in `_execute_live_approval`
(dispatcher.py:631-665)". RQA-FR-026 is `partial gap` / `not built`, met on this unit's
paths. RQA-NFR-010 is `conflicting` / `built contrary` at U-DISPATCH-20's swallow.

This is one of only two paths that submits the verdict RQA-FR-028 requires — the other is
U-DISPATCH-17's CHANGES_REQUESTED mutation (`scripts/dispatcher.py:1010-1035`), and
U-DISPATCH-18's advisory path is not a third, its GraphQL event being hard-coded `COMMENT`
— and two
mechanisms inside it are why no materially simpler approach suffices. First,
`approval_action.approve` re-validates the PR head over REST immediately before mutating.
A design that mutated straight from the stored decision is simpler and would submit an
APPROVED attributed to a revision the panel never examined whenever the head moved between
evaluation and action — an ambiguous authoritative outcome under RQA-NFR-010's first
invariant, and uniquely bad because the submission is public and cannot be retracted by the
system. Second, the mutation is idempotency-keyed on the decision id
(`approve-{decision_id}`, `scripts/approval_action.py:166`), so re-entry after a crash
mid-call re-validates rather than duplicating; a key derived from the attempt rather than
from the decision cannot distinguish a retry from a second approval, which is the
duplicate-authority case RQA-NFR-010 rules out. The guarded failures follow the same
discipline: `DENIED` and `STALE` enqueue a human request naming the risk score, band, failed
gates and outcome — the concrete cause RQA-FR-026 asks for — and `UNCERTAIN` safe-stops
without retry, so an unknown mutation outcome is never resolved by guessing.

---

### U-DISPATCH-17 — CHANGES_REQUESTED execution: corroboration, per-activity authority, and a revalidation gate before any mutation

Disposition: rework
Requirements: RQA-FR-028, RQA-BR-008, RQA-NFR-017, RQA-FR-010, RQA-FR-026, RQA-NFR-010
Root cause: RQA-FR-028 is `conflicting` / `built contrary`, and its row names this unit's
authority branch among the reachable executions producing the forbidden outcome — "a
satisfied review carrying corroborated defects under a non-live `request_changes` authority
transitions to `human_required` and returns, again submitting nothing
(dispatcher.py:941-950)". RQA-BR-008 and RQA-FR-026 are `partial gap` / `not built`,
RQA-FR-010 is `full gap` / `not built`, RQA-NFR-017 is `conflicting` / `built contrary` on
the activities never consulted — of which `request_changes` is not one. RQA-NFR-010 is
`conflicting` / `built contrary` at U-DISPATCH-20's swallow, not here.

Retained in intent, stated at mechanism level because it is the most valuable thing here:
a finding may be acted on only when two distinct provider families report it, or one family
cites a check that actually failed, and an uncorroborated finding escalates to a person
instead of blocking the pull request; the posted body then lists only corroborated findings
and states that the rest were excluded and escalated. That rule is what makes "verified"
mean something other than "a model asserted it", which is RQA-BR-008's obligation, and no
simpler rule survives a single model's unreplicated assertion. The deterministic
revalidation gate against a fresh head before the mutation is retained on the same
reasoning as U-DISPATCH-16's head re-validation, and checking `request_changes` authority
independently of every other activity is the per-activity model RQA-NFR-017 requires.

What changes: under a non-live `request_changes` authority a satisfied review submits
nothing, and RQA-FR-028's row records this as the common case rather than an edge, since
`DEFAULT_MODE` is `disabled` and `defaults()` disables every activity
(`scripts/authority.py:44`, `:149-151`). Closing RQA-FR-028 means changing what that branch
does. The same row states that the relationship between RQA-FR-028 and RQA-NFR-017's
per-activity gate is "a tension the replacement must reconcile, not a precedence", so this
rework carries a real design question rather than a mechanical edit, and this analysis
records it rather than settling it. Separately, RQA-FR-010 is a full gap this unit does not
close and must not be credited with: corroborated/uncorroborated is a two-valued judgement,
and RQA-FR-010 requires each obligation to carry a state from a seven-value set that no
reachable code supplies.

---

### U-DISPATCH-18 — Advisory-mode review posting (shadow / disabled dispositions)

Disposition: rework
Requirements: RQA-FR-028, RQA-BR-007, RQA-BR-008, RQA-NFR-017
Root cause: RQA-FR-028 is `conflicting` / `built contrary`, and its row names this unit's
two terminal branches as the forbidden executions — the `disabled` branch transitioning to
`advisory_action` and terminating `completed_advisory` (`scripts/dispatcher.py:1513-1523`),
with the `shadow` disposition terminating identically (`:1471-1481`), the transition being
unconditional. RQA-BR-007 is `fit` and rests in part on this unit's per-job idempotency;
RQA-BR-008 is `partial gap` / `not built`; RQA-NFR-017 is `conflicting` / `built contrary`.

Retained in intent: a non-mutating disposition still publishes what was found, and
publishes it from the ledger rather than from configuration, so the record names the routes
and activities that actually executed rather than the ones configuration would have
selected — the two diverge exactly when a fallback fired, which is when the record is read.
The post is idempotent per job, which is part of what makes RQA-BR-007 `fit`, so
re-dispatching the same revision does not duplicate the comment.

What changes: under the maintainer's 2026-09-06 ruling an advisory-mode review is inside
RQA-FR-028's population, and both branches terminate `completed_advisory` unconditionally,
so a satisfied review ends having submitted neither APPROVED nor CHANGES_REQUESTED. The
register adds a detail the rework must not miss — the comment itself is gated by a second
activity, `post_advisory` returning `posted: false` unless `comment` mode is `live`
(`scripts/advisory.py:154-156`) — so under full defaults the job reaches its terminal state
with nothing delivered at all, and the GraphQL event is hard-coded `COMMENT`
(`scripts/github_mutate.py:99-113`), structurally not a submission. The change is at the
terminal branch and is subtractive; the ledger-sourced publication and its idempotency
should survive it intact.

---

### U-DISPATCH-19 — Observability: one otel-jsonl event per orchestration milestone

Disposition: keep
Requirements: RQA-BR-003, RQA-FR-012, RQA-NFR-010
Root cause: RQA-BR-003 is `partial gap` / `built against superseded intent`, and its row
attributes that cause to the unpinned policy path, citing the fixed trace vocabulary on the
met side. RQA-FR-012 is `partial gap` / `not built`, its two failing elements being the
never-recorded protocol identity and U-DISPATCH-20's swallowed write. RQA-NFR-010 is
`conflicting` / `built contrary` at that same swallow, and its row holds this unit's
failure conversion up as the correct contrast.

RQA-BR-003 requires the record to establish who or what performed the review and on what
basis, and RQA-FR-012 requires one command to reconstruct it. Two decisions are why no
simpler emission suffices. Event names are validated against the `logging_otel.JOB_EVENTS`
registry at emission and an unregistered name raises `SafeStopSignal`, so the vocabulary a
trace consumer keys off cannot drift by accident; free-form event strings are the
materially simpler alternative and they degrade the trace precisely over time, which is
when it is read. And `_emit_panel_trace` reads the planner's activities and the executed
routes back from the ledger rather than re-deriving them from configuration, so the trace
states what ran rather than what was intended — again, the two diverge exactly when a
fallback fired. Bounding the route events at `_MAX_LOGGED_ROUTES=4` with a single distinct
`unrouted` event when nothing was recorded keeps an unbounded route list from being the
reason an emission fails, which matters because an emission failure here is deliberately
fatal to the job rather than silent — the behaviour RQA-NFR-010's row contrasts favourably
with the ledger path's discarded write.

---

### U-DISPATCH-20 — Ledger recording of every decision, action, assurance computation and finding

Disposition: rework
Requirements: RQA-FR-012, RQA-NFR-010, RQA-NFR-032, RQA-BR-003
Root cause: RQA-NFR-010 is `conflicting` / `built contrary` and **this unit is the named
contrary execution** — "`_ledger_record`'s bare except, on the authoritative-action paths
that call it — the approve action at :653, the request-changes action at :1027, the
decision record at :1451, among the nine call sites search S11 counts". RQA-FR-012 is
`partial gap` / `not built` and names the same swallow as one of its two failing elements;
RQA-BR-003 is `partial gap` / `built against superseded intent` and records this swallow as
"a second, distinct weakness"; RQA-NFR-032 is `fit` and its row
expressly does not inherit this claim.

The responsibility is required and precisely shaped: one ledger entry per decision, action,
finding and assurance computation, tagged with the job's pinned snapshot hash and policy
version — RQA-FR-012's single-command reconstruction is built on nothing else. What is
wrong is the failure policy at one place: `except Exception: pass`
(`scripts/dispatcher.py:217-218`) discards a failed append, so a review can complete
authoritatively while its provenance record is knowingly incomplete, which is the partially
authoritative result RQA-NFR-010 forbids. The docstring's claim that failures "surface in
the JSONL log" does not hold at this revision — no logging call exists in that write path —
and correcting the docstring is not the fix; the entry must not be silently lost. The
estate already contains the answer, which is why this is a rework of a wrong shape rather
than an invention: the same module converts an equivalent JSONL logging failure into
`SafeStopSignal`, and RQA-NFR-010's row says in terms that both behaviours exist here and
this path chose the wrong one. Retained in intent: the per-decision granularity and the
snapshot-hash/policy-version tagging, which is what makes an entry attributable to the
policy actually in force rather than to whatever the configuration says later.

---

### U-DISPATCH-21 — Safe-stop containment: a state-persistence or audit-logging failure stops only the affected job

Disposition: salvage
Requirements: RQA-NFR-010
Root cause: RQA-NFR-010 is `conflicting` / `built contrary` at U-DISPATCH-20's swallow;
its row names this unit's conversion of a persistence or logging failure into a safe stop
as the behaviour the ledger path should have taken. The requirement stays open until that
path changes, and [`../methodology.md`](../methodology.md) §7 forbids `keep` for a unit
whose requirements are all `conflicting`, so the containment discipline is carried forward
as a mechanism rather than the code retained as it stands — which is the honest reading
anyway, since the residue recorded at the end of this entry means the arrival path does not
survive unchanged.

The mechanism to lift: **a typed containment boundary that converts any persistence or
audit-logging exception into a single "stop this job safely" signal, with the
programming-error class deliberately excluded from the conversion so it still fails
loudly.** The exclusion is as much of the asset as the conversion: containment that
absorbs `JobBlockingError` too would turn an illegal or nonexistent transition into a
routine safe stop and hide it.

RQA-NFR-010's fit criterion checks ambiguity, corruption and partial authority
independently, and the failure this unit contains — the state store refusing a write
mid-job — threatens all three at once. Converting it into a `SafeStopSignal` that arrives
at a recorded `safe_stop` gives the job one unambiguous terminal state with its reason
attached. Letting the exception propagate is the materially simpler alternative and it
leaves the job in whatever in-flight status it last persisted, with the failure recorded
only against the sweep, which is the ambiguity the requirement names. The exclusion of
`JobBlockingError` from the conversion is the part that makes this more than a blanket
`except`: an illegal or nonexistent transition is a defect and still fails loudly instead
of being absorbed into a safe stop, so containment does not become a way of not noticing
bugs.

One residue is recorded for whoever reworks U-DISPATCH-20 rather than left to be
rediscovered: `_arrive_safe_stop` swallows a failure of the safe-stop transition itself
(`scripts/dispatcher.py:182-185`) and still returns `status: safe_stop`, so when the state
store is the thing that failed, the caller's result and the state directory can disagree.
The persisted side of that disagreement is caught by `recover`, whose
`ACTIVE_WORKER_STATUSES` sweep exists for exactly that case; what `recover` then does with
the job is U-DISPATCH-07's rework, not this unit's.

---

### U-DISPATCH-22 — Managed-sweep per-job batch-error isolation

Disposition: keep
Requirements: RQA-NFR-007
Root cause: RQA-NFR-007 is `partial gap` / `built then orphaned`, and the orphaned
mechanisms behind that cause are the worktree operations and the degrade ladder
(U-DISPATCH-26, U-DISPATCH-23). Nothing in that row's unmet obligation is decided here.

RQA-NFR-007 requires every managed pull request to be carried through its lifecycle
whenever progression remains possible, and the managed sweep is the only path that advances
jobs unattended: checked against the other dispatch units that touch job progression —
U-DISPATCH-08 (the timer's `tick`/`sweep`, which drives this batch), U-DISPATCH-07
(`recover`, which releases leases and stops jobs rather than advancing them) and the
`dispatch-one` subcommand, which advances a single named job on an operator's initiative.
That makes one job's exception a lifecycle event for every job behind it in
the batch: without this catch, an unexpected failure on the first job ends the invocation
and the remaining FIFO jobs are not reached, with nothing recorded against them to say why.
Recording the exception as that job's own `error` result is the part that matters — a
batch-level catch is equally simple and loses the attribution, so an operator sees a failed
sweep rather than a failed job and cannot tell which PR to look at. The alternative of
aborting and retrying the whole batch repeats work already done, which RQA-BR-012 counts as
spend against shared capacity.

---

### U-DISPATCH-23 — Degradation-ladder helper (`degrade()`), reachable only from a resilience-cluster test

Disposition: salvage
Requirements: RQA-NFR-010, RQA-NFR-007
Root cause: RQA-NFR-007 is `partial gap` / `built then orphaned`, and its row names this
unit's missing product caller as part of that cause — "The degrade ladder has no product
caller either (negative-caller search quoted in U-DISPATCH-23: the only caller in the tree
is tests/test_degradation.py)". RQA-NFR-010 is `conflicting` / `built contrary` at
U-DISPATCH-20's swallow. Orphaned code cannot be `keep`, and a mechanism the register
counts as part of an unmet obligation cannot be `bin`.

The mechanism to lift is the **total ordering of outcome authority** — live above shadow
above human-pending above advisory above degraded-evidence above safe stop — together with
the two rules the ladder enforces over it: a degradation moves exactly one *reachable* rung,
and an unranked (terminal) status, a nonexistent job, or a job already at the floor is
refused rather than moved. The ordering, not the function, is the asset, and it is needed
because the reachable estate degrades at several independent sites that each choose a
target locally: `_budget_refused` selects `human_required` or `degraded_draft` from the
reservation's own `downgrade` field, `_arrive_safe_stop` goes straight to the floor, and
the partial-panel path selects `degraded_draft`. With no single ranking, nothing
structurally prevents a downgrade that skips the human rung or one that raises authority
relative to where the job already stood — which is how an outcome ends up partially
authoritative, the result RQA-NFR-010 forbids, and how progression stalls against
RQA-NFR-007. A per-site convention is the materially simpler alternative and it cannot be
checked: correctness would live in the agreement between call sites rather than in a
definition.

Lifting it means the ordering becomes the single definition every downgrade site consults.
It does not mean preserving `dispatcher.degrade`, which no file under `scripts/` calls and
whose only caller in the tree is a test belonging to another cluster.

---

### U-DISPATCH-24 — Deterministic review-activity planning

Disposition: keep
Requirements: RQA-BR-014, RQA-BR-002, RQA-FR-019, RQA-BR-009
Root cause: all four are `partial gap` / `not built`, and each row cites this unit on its
met side. Their unmet obligations are decided elsewhere: the findings taxonomy that does
not exist (RQA-BR-002), the per-obligation evidence state that RQA-BR-014's single contract
edge points at RQA-FR-010 for, the comparison of reasoning strategy against stated assurance
(RQA-FR-019), and check-failure attribution in `checks.py` (RQA-BR-009).

Two properties carry these requirements and neither survives a simpler design.
Determinism first: `plan_review` derives every selection from the explicit keyword
arguments it is given, with no `random`, `time` or `uuid` import and no module-level state
read, which is what makes RQA-BR-002's "one shared definition applied identically whatever
ran the review" a checkable property for review scope rather than an assertion. A
model-derived or environment-derived plan cannot be replayed, so two reviews of the same
change cannot be compared, and the concept RQA-BR-002 pins would be pinned in name only.
Symmetry of the record second: a reason is recorded for every *omitted* activity as well as
every selected one, and RQA-BR-014's obligation is that the record demonstrate what was
undertaken rather than ask for trust in volume — a selections-only record cannot show a
reader that a question was deliberately not asked, which is the whole difference between a
plan and a list of things that happened. The risk-class selections are pattern-class rules
over changed paths — security/auth, migration/schema/dependency, infrastructure/CI/
concurrency — so the same change always draws the same questions and each omission carries
its own reason; RQA-FR-019's met half is exactly that, and RQA-BR-009's
`INVESTIGATE_HYPOTHESIS` selection on a failing required check is the same rule applied to
a check signal.

---

### U-DISPATCH-25 — Reviewer runner adapters: read-only, auditable invocations per transport

Disposition: rework
Requirements: RQA-FR-030, RQA-NFR-001, RQA-BR-003, RQA-FR-012
Root cause: RQA-FR-030 is `full gap` / `not built` and RQA-NFR-001 is `partial gap` /
`not built`; both rows name the same cause — `ADAPTERS` is a fixed three-entry mapping,
`adapter_for` raises `UnknownRunnerError` for every other name, and search S7 finds no
plugin, hook or entry-point path admitting a fourth, "which is exactly the hard-coded-to-N-
known-combinations disqualifier the fit criterion names — so adding a fourth built-in
adapter cannot close this row either". RQA-BR-003 is `partial gap` /
`built against superseded intent`; RQA-FR-012 is `partial gap` / `not built`.

The responsibility — one interface behind which a reviewer transport is invoked, with the
invocation recorded — is required and survives. The shape is wrong for the requirements
this unit is credited with: admission is closed, so a harness that was not coded in cannot
participate without a source change, and both rows state that extending the mapping does
not close them. That rules out `keep` and rules out treating the gap as additive.

Two mechanisms must not be lost in the rebuild, and they are named at mechanism level so
they can be carried without the module. First, effort honesty: `build_invocation` records
`effort_enforced=False` whenever the requested reasoning-effort level is outside a
transport's `enforceable_efforts` — always so for `claude`, which exposes no such flag — so
the record states the assurance axis the transport actually applied rather than the one
that was asked for. A boolean "effort requested" field is the simpler design and it
misstates exactly the case that matters. Second, `read_only_proof` carries the exact flags
the read-only claim rests on, so RQA-FR-012's reconstruction names the enforcement rather
than asserting it, and RQA-BR-003's judgement-basis obligation is answered by the record
instead of by the reader's trust in the module.

---

### U-DISPATCH-26 — Isolated author-triage worktree operations (unreachable from any product entrypoint)

Disposition: salvage
Requirements: RQA-NFR-020, RQA-NFR-021, RQA-NFR-007
Root cause: RQA-NFR-020 and RQA-NFR-021 are `full gap` / `built then orphaned` —
[`../methodology.md`](../methodology.md) §2.4's worked example, with search S1 of
[`../register/nfr.md`](../register/nfr.md) establishing that no product path reaches
`create`/`commit`/`push`/`clean`, the only `scripts/` occurrence being a docstring line in
`runners.py`. RQA-NFR-007 is `partial gap` / `built then orphaned` for the same reason.
Code nothing reaches cannot be `keep`; requirements that still state bounds on the
behaviour rule out `bin`.

Two mechanisms are worth lifting, each stated so it can be carried without the file.
First, the isolation decision: the working copy is created at
`<repo_root>/.worktrees/rqa-<job>` — a directory separate from the repository's own working
tree — from the exact configured PR head SHA or head branch, and a missing head
configuration raises `WorktreeError` rather than falling back to the base branch. The
fallback is the tempting simplification and it is the one that has an agent commit against
the wrong ref; refusing it is what RQA-NFR-020's isolation bound actually needs, and a
convention that callers pass a head cannot enforce it. Second, the push restriction
expressed as refusals in the transport rather than as a caller contract: only the exact
configured PR head branch is pushed, an internal `rqa/` branch is refused against the PR
remote, and `force=True` is refused outright. A refusal in the transport holds when a
caller is wrong, which is the only case that matters for RQA-NFR-021, and a documented rule
does not.

What must not be inherited is the surroundings. No entrypoint class reaches the module;
`fix` — the code's name for the specification's `remediate` — is one of the three
activities in `authority.ACTIVITIES` never passed to `mode_for`/`can_act` (search S4); and
RQA-NFR-019, RQA-NFR-031 and RQA-NFR-033 record that no mechanical-remedy or
behaviour-change classification exists for a policy to bound (search S2). So lifting these
two mechanisms into a remediation path means building the authority consultation and the
finding classification around them, not porting the module.
