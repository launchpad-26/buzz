# RQA gap analysis — evidence — `queue` cluster

Revision: `9267b6308714454a3b987622d90cda03a8972827`. Every citation below is a
claim about that revision. Paths are relative to
`launchpad/skills/review-queue-automation/`, per `../methodology.md`.

Cluster remit, per [`../clusters.md`](../clusters.md): "Detecting work and
holding it: queue reconciliation, leases, the job state machine, cadence,
snapshots and history — plus the timer that fires the tick." 18 assessed
files. Every one is named by at least one unit below.

**Round 2 revision note.** This revision responds to review-gate round 1
(13 blocking, 5 notes) and the maintainer's resolution of
escalation `CADENCE-SPLIT`. Every finding is fixed except none are left
outstanding; the cadence unit, previously a single unit pending a parked
boundary question, is now three units per the maintainer's explicit
direction. No `PENDING-HUMAN` marker is carried for it — the question is
resolved, not deferred.

**Entrypoint note, established once here rather than repeated per unit.**
`scripts/queue.py`, `scripts/lease.py`, `scripts/cadence.py`,
`scripts/scheduled-tick.sh` and `scripts/launchd.plist.example` all appear in
`OPERATORS.md`'s disclaimed "internal modules that are also executable" table
(`OPERATORS.md:566-579`), so none of them is E3 on that row's strength. Each is
nonetheless reachable:

- `scripts/queue.py`, `scripts/lease.py`, `scripts/cadence.py`,
  `scripts/states.py` and `scripts/snapshot.py` are called by `dispatcher.py`
  (E2) — `from queue import reconcile` (`scripts/dispatcher.py:64`), `from
  lease import claim`/`release` (`scripts/dispatcher.py:1611`,
  `scripts/dispatcher.py:1617`), `from cadence import decide as cadence_decide,
  due as cadence_due, read as cadence_read, schedule_after, write as
  cadence_write` (`scripts/dispatcher.py:35`), `from states import TRANSITIONS`
  / `from states import can_transition` (`scripts/dispatcher.py:438`,
  `scripts/dispatcher.py:1819`), `from snapshot import SnapshotError,
  SnapshotStore, build_snapshot` (`scripts/dispatcher.py:1549`).
- `scripts/scheduled-tick.sh` and `scripts/launchd.plist.example` are
  reachable under E1 — the plist's `ProgramArguments` names the shell script
  as the command a macOS timer fires (`scripts/launchd.plist.example:36-40`),
  and the script itself is "what a timer... invokes"
  (`scripts/scheduled-tick.sh:7`).
- `scripts/history.py` is **not** in the disclaimed table at all: it is a row
  of the other, undisclaimed entry-point index (`OPERATORS.md:556`, `§8.1`),
  with its own documented command line at `OPERATORS.md:308` — E4.

No file in this cluster is orphaned.

---

### U-QUEUE-01 — PR inventory detection and per-lane job creation

Files: scripts/queue.py, tests/test_queue.py

Rationale: tests/test_queue.py is the deterministic suite exercising exactly
the fact-persistence and job-creation half of `queue.py`'s single
reconciliation pass, driving the real `github_query.InventoryReader` over a
stubbed transport rather than a hand-written fake.

| claim | evidence | requirements |
|---|---|---|
| `reconcile()` reads one GraphQL inventory query per page of open PRs (up to fifty PRs per query, per `github_query.InventoryReader.queue_inventory`'s own docstring) and, for each PR, upserts its full fact payload (head SHA, node id, assignees, reviews, checks) into the `prs` table, keyed by `(repo, number)`, before any job is created for it. | scripts/queue.py:93, scripts/queue.py:96, scripts/queue.py:105, scripts/queue.py:109, scripts/queue.py:111 | RQA-FR-016 |
| `reconcile()` creates at most one job per exact `(repo, number, head, lane)` key: an existing row for that key blocks creating a second one, so replaying the same revision through `reconcile()` does not duplicate the job. | scripts/queue.py:116, scripts/queue.py:117, scripts/queue.py:118 | RQA-BR-007, RQA-FR-020 |
| An `author_triage` job is created only when the PR's own latest-per-reviewer review state includes `CHANGES_REQUESTED`; a `DISMISSED` review, or one a reviewer's own later, differing verdict overwrites, does not queue it. | scripts/queue.py:37, scripts/queue.py:45, scripts/queue.py:53, scripts/queue.py:66, scripts/queue.py:68, scripts/queue.py:119, scripts/queue.py:120, scripts/queue.py:121, scripts/queue.py:122 | RQA-BR-010 |
| An `incoming_review` job is not created while the PR already carries an assignee other than the configured login: the queue defers to whoever already holds it instead of creating a competing job. | scripts/queue.py:123, scripts/queue.py:124 | RQA-BR-007 |
| `reconcile()` has no exception handling around the per-page inventory read: any error the reader raises — including the real `InventoryReader`'s fail-closed rejections of an incomplete file-connection or a failed read — propagates out of `reconcile()` and aborts the whole sweep before any job is written, rather than reconciling a partial queue. | scripts/queue.py:93 | RQA-NFR-010 |

`github_query.py`'s own docstring corroborates the first row's "one query per
page, not one page per PR" reading directly: "One GraphQL query returns all of
it for up to fifty pull requests at a time" (scripts/github_query.py:9) and
`queue_inventory`'s own docstring, "every open pull request in `repo`,
enriched, in one query per page" (scripts/github_query.py:479).
`test_incomplete_file_list_fails_closed` and `test_inventory_read_failure_fails_closed`
(tests/test_queue.py:226-258) corroborate the last row end to end: both assert
`state.execute("SELECT 1 FROM jobs").fetchone() is None` after the raise, i.e.
no partial queue state survives the abort. The fail-closed decision itself is
made inside `github_query.InventoryReader` (an `authority`-cluster file), not
in `queue.py`; the claim above is scoped to what `queue.py` itself does —
decline to catch and paper over that failure.

### U-QUEUE-02 — supersede stale jobs and pending approval requests on head change

Files: scripts/queue.py, tests/test_queue.py

Rationale: shares its source file with U-QUEUE-01 but is a materially
different responsibility — invalidating work already in flight rather than
detecting new work — that could be rebuilt independently of job-creation
logic; `test_new_head_supersedes_old_job_and_pending_request` is the direct
test for this exact mechanism.

| claim | evidence | requirements |
|---|---|---|
| `_supersede_old` marks every job for the same `(repo, number)` whose stored `head_sha` differs from the newly observed head, and whose status is one of the 14 `NONTERMINAL` statuses, as `superseded`; a job already in a terminal status is left untouched — so a status command reading the `jobs` table never reports a job against a revision the PR has since moved past. | scripts/queue.py:159, scripts/queue.py:160, scripts/queue.py:166, scripts/queue.py:168, scripts/queue.py:169 | RQA-FR-016 |
| `reconcile()` also supersedes any pending human-approval request for the same PR whose head is now stale, via `approval.supersede_for_head`, in the same reconciliation pass that supersedes the job — the same stale-answer-after-a-transition failure mode `RQA-FR-016`'s own fit criterion names, applied to the pending-request record rather than the job record. | scripts/queue.py:137 | RQA-FR-016 |
| `reconcile()` resets every previously-open PR row for the repo to closed, then re-opens exactly the PR numbers seen in the current inventory read — so a PR that dropped out of the open-PR inventory (closed or merged) is reflected as closed without a separate closing event. | scripts/queue.py:148, scripts/queue.py:149, scripts/queue.py:150 | RQA-FR-016 |

`test_new_head_supersedes_old_job_and_pending_request` (tests/test_queue.py:341-370)
corroborates the first two rows together: it seeds an `assurance`-status job
and a pending `human_requests` row for an old head, reconciles a new head for
the same PR number, and asserts both moved to `superseded`.

`RQA-BR-007` ("Review work shall not be duplicated across a revision that has
not changed", requirements-specification.md:261) was cited here in round 1 and
is wrong on direct reading: this unit's whole mechanism runs precisely when
the head **does** change, abandoning stale work so a new job can be created
for the new revision — the opposite scenario from BR-007's text. `RQA-FR-016`
is used instead for all three rows: its own fit criterion is explicit that "a
command that returns a stale or generic answer after a transition has
occurred fails this check even if the value it returns is individually
legal" — exactly the failure this unit's supersession mechanism prevents.

### U-QUEUE-03 — assignee review lease: GitHub-verified claim/release contract

Files: scripts/lease.py, tests/test_lease.py

Rationale: tests/test_lease.py is the dedicated suite for `lease.py`'s
REST-verification contract in isolation, with no dispatcher in the loop —
every call in this unit goes through a fake `RestReader`/`github_mutate.post`,
never `dispatcher.run_job`.

| claim | evidence | requirements |
|---|---|---|
| `claim()` refuses to claim a PR that already lists an assignee other than the requested login, without attempting any GitHub mutation. | scripts/lease.py:73, scripts/lease.py:74 | RQA-BR-007 |
| `claim()` writes the local `leases` row only after a REST re-read (`current_logins`) confirms the login is listed as an assignee; a mutation that is sent but not confirmed on REST leaves no local lease row. | scripts/lease.py:84, scripts/lease.py:85, scripts/lease.py:86, scripts/lease.py:89 | RQA-NFR-010 |
| `release()` deletes the local `leases` row only after a REST re-read confirms the login is no longer listed; if REST still lists it, `release()` raises `RuntimeError` and the local row survives. | scripts/lease.py:111, scripts/lease.py:112, scripts/lease.py:113, scripts/lease.py:114 | RQA-NFR-010 |
| The assignee mutation always addresses the PR by its cached GraphQL node id (`queue.py`'s own persisted `prs.payload`) and the target user by the node id read from the REST `/users/{login}` endpoint, never a hardcoded login. | scripts/lease.py:31, scripts/lease.py:39, scripts/lease.py:50, scripts/lease.py:53 | RQA-BR-007 |

Corroborating tests: `test_claim_wont_steal_another_assignees_pr`,
`test_claim_rest_verify_failure_leaves_no_local_lease`,
`test_release_verifies_before_dropping_local_lease`,
`test_claim_uses_pr_node_id_and_user_node_id`
(tests/test_lease.py:69-183).

### U-QUEUE-04 — dispatch-side lease-lifecycle invocation and local exclusivity

Files: scripts/lease.py, tests/test_lease_lifecycle.py

Rationale: `tests/test_lease_lifecycle.py` is a `queue`-cluster file per
`clusters.md`. Its subject is one behavioural responsibility, not two: the
local `leases` row `lease.py` writes is the single piece of local state that
is claimed/released across `dispatcher.run_job`'s lifecycle and that a second
job's dispatch reads before ever attempting a GitHub call. The two
half-mechanisms guard the same record lifecycle and are not independently
dispositionable without incoherence: dropping the always-release guarantee
while keeping the local-exclusivity check would let a released-never local
row permanently block future dispatch of the same PR (the dispatcher gate
returns `gated` on any locally-held row whose job id differs,
`scripts/dispatcher.py:1699-1700`); and, mirroring that, absent always-release,
a lingering GitHub assignee would permanently block future `claim()` calls
even after the local row were gone — `claim()` refuses a PR already assigned
to a different login (`scripts/lease.py:73-74`), so releasing the GitHub
assignee (which always-release does, via `scripts/lease.py:98-114`) is what
lets anyone claim the PR again. Both arms describe the same record lifecycle,
so the halves stay one unit even though their rows cite different requirement
IDs — per the ruling on escalation `SPLIT-GRANULARITY`, §4's tests apply to
the candidate responsibility as a whole, not to individual evidence rows, and
two rows citing disjoint IDs within one coherent responsibility do not by
themselves force a split.

This unit's `Files:` line — its disposition scope — is limited to
`scripts/lease.py`, because the decisive gate/wrapper code the rows below
also cite (`scripts/dispatcher.py`) is already assessed and dispositioned by
the `dispatch` cluster's own unit; per the ruling on
escalation `FOREIGN-EVIDENCE`, citing it here to establish what actually
happens does not add it to this unit's disposition scope. This unit judges
only whether `lease.py`'s own `claim()`/`release()` functions and the local
`leases` row `lease.py` writes / a second job's dispatch reads behave as
designed under real dispatch conditions — not whether `dispatcher.py`'s
surrounding gate/wrapper design is itself the right shape; that is
`dispatch`'s own unit to evidence.

| claim | evidence | requirements |
|---|---|---|
| `dispatcher.run_job` invokes `lease.claim()` (via the thin wrapper `_lease_claim`) before any review work, and invokes `lease.release()` (via `_lease_release`) in a `finally` block on every exit path it exercises — success, a degraded panel outcome, an uncertain/safe-stop mutation, and an unhandled exception from the panel — with exactly one release recorded per run in every case. | scripts/lease.py:65, scripts/lease.py:98 (the two functions invoked); scripts/dispatcher.py:1610, scripts/dispatcher.py:1613, scripts/dispatcher.py:1616, scripts/dispatcher.py:1619 (the thin wrappers), scripts/dispatcher.py:1736, scripts/dispatcher.py:1739, scripts/dispatcher.py:1740, scripts/dispatcher.py:1741 (the `finally`-wrapped release) | RQA-NFR-010 |
| The local `leases` row `claim()` writes (`scripts/lease.py:89-94`) is the data a second job's dispatch reads and refuses to act on before attempting any GitHub call: a lease row already recording a different job id for the same `(repo, number)` blocks a second `claim()` attempt outright. | scripts/lease.py:89, scripts/lease.py:90, scripts/lease.py:91, scripts/lease.py:92, scripts/lease.py:93, scripts/lease.py:94; scripts/dispatcher.py:1623, scripts/dispatcher.py:1624, scripts/dispatcher.py:1625 (the read), scripts/dispatcher.py:1699, scripts/dispatcher.py:1700 (the refusal) | RQA-BR-007 |

`dispatcher.py`'s thin wrappers are patched directly by
`patch_dispatcher(..., _lease_claim=trace.claim, _lease_release=trace.release)`
(tests/test_lease_lifecycle.py:63, tests/test_lease_lifecycle.py:64,
tests/test_lease_lifecycle.py:65, tests/test_lease_lifecycle.py:66), which is
how the tests observe both rows' behaviour without needing GitHub or a real
`leases` table write for every scenario.

Corroborating tests: `test_lease_is_claimed_before_review`
(tests/test_lease_lifecycle.py:86-96),
`test_locally_held_lease_by_another_job_is_respected`
(tests/test_lease_lifecycle.py:122-157),
`test_lease_is_released_after_success`,
`test_lease_is_released_after_a_degraded_outcome`,
`test_lease_is_released_when_the_mutation_is_uncertain`,
`test_lease_is_released_when_the_panel_raises`
(tests/test_lease_lifecycle.py:185-240).

### U-QUEUE-05 — adaptive sweep-interval selection

Files: scripts/cadence.py, tests/test_cadence.py

Rationale: `decide()`, `due()` and `schedule_after()` are read together by
`tests/test_cadence.py`'s "the three rules"/"timer semantics" test groups;
together they are the one decision this unit is named for — how long until
the next sweep, and why — as distinct from *where that decision is persisted*
(U-QUEUE-06) or *which scope it is persisted under* (U-QUEUE-07).

| claim | evidence | requirements |
|---|---|---|
| `decide()` chooses the next sweep delay from three rules — REST-budget floor, work pending, idle backoff — so new work is discovered on a timer rather than requiring an operator to run `sweep` by hand; `due()` decides whether that persisted schedule has elapsed. `cadence.py`'s own docstring states this replaces "Work was only ever discovered when an operator ran `sweep` by hand." | scripts/cadence.py:109, scripts/cadence.py:112, scripts/cadence.py:116, scripts/cadence.py:174 | RQA-BR-010 |

The three-rule algorithm's own internals — idle-streak step growth capped at
the longest configured interval (scripts/cadence.py:114-116), the REST-budget
floor treating an unknown remaining count as below-floor without resetting
the streak (scripts/cadence.py:106-109), and `due()`'s fail-toward-run
treatment of a missing or malformed schedule (scripts/cadence.py:166-174) —
has no corresponding requirement anywhere in the frozen specification.
`poll`, `cadence`, `sweep`, `schedul`, `timer`, `idle`, `interval`, `backoff`
and `rate limit` do not occur in `requirements/requirements-specification.md`
at all; `sweep` and `tick` each occur exactly once, and both are unrelated
("ticked" boxes at line 386, an unrelated "ISO/IEC 25010:2023 sweep of the
non-functional class" at line 1371). Only the existence of a timer-driven
decision, not its specific rules, connects to spec text (`RQA-BR-010`,
above). This is a genuine scope gap, out of scope for this analysis (the
gap-degree register is a later step); it is not an omission here.

### U-QUEUE-06 — cadence config-reload freshness

Files: scripts/cadence.py, tests/test_cadence.py

Rationale: a materially different responsibility from interval selection
(U-QUEUE-05): whether a changed `poll.*` config value is honoured at all, as
distinct from what interval the algorithm computes from it. Binning this
freshness property would contradict `RQA-NFR-005` while the interval
algorithm itself remained required — the two are separable exactly because
they take different dispositions.

| claim | evidence | requirements |
|---|---|---|
| `_intervals()` and `decide()` re-derive `poll.active_seconds`/`poll.idle_seconds`/`poll.rest_remaining_floor` from whichever `poll_cfg` argument is passed to that specific call — nothing is cached across calls — so a repository's edited config values are visible on the very next call with no rebuild, reinstall or redeploy of the module itself. | scripts/cadence.py:66, scripts/cadence.py:69, scripts/cadence.py:79, scripts/cadence.py:100, scripts/cadence.py:102 | RQA-NFR-005 |

`test_missing_or_malformed_poll_config_falls_back_to_defaults`
(tests/test_cadence.py:75-78) corroborates that every call re-reads and
re-validates its own `poll_cfg` argument rather than trusting a cached,
possibly-stale parse. `RQA-FR-004`'s text ("a change to a repository's
**review policy**... on that repository's **next review**") does not fit this
row: `poll.*` is scheduler/timer configuration, not review policy, and "next
timer firing" is not "next review" — `RQA-NFR-005` alone is cited, matching
its own broader wording ("Updating a repository's policy **or
configuration**... no rebuild or redeploy").

### U-QUEUE-07 — per-scope cadence isolation

Files: scripts/cadence.py, tests/test_cadence.py

Rationale: a third, separately-removable responsibility from the other two
cadence units — dropping per-scope keying would still leave a working
interval-selection algorithm and a working config-reread property, but would
silently merge every repository/lane's backoff into one shared schedule.

| claim | evidence | requirements |
|---|---|---|
| `read()`/`write()` key every cadence row by an opaque `scope` string (a repo+lane pair, in practice); two different scopes back off independently, so one repository's or lane's idle streak never influences another's next-due calculation. | scripts/cadence.py:126, scripts/cadence.py:150, scripts/cadence.py:152 | RQA-NFR-004 |

`test_scopes_do_not_share_a_schedule` (tests/test_cadence.py:130-141)
corroborates this directly: two scopes seeded with different idle streaks
retain distinct rows after independent `write()` calls.

### U-QUEUE-08 — the scheduled-tick timer and its macOS launchd definition

Files: scripts/scheduled-tick.sh, scripts/launchd.plist.example

Rationale: one file is the trigger script, the other is the macOS timer
definition that fires it; neither is the queue's E1 entrypoint without the
other, and both encode the same "timer, not daemon" design the two files'
comments state in nearly identical language.

| claim | evidence | requirements |
|---|---|---|
| `scheduled-tick.sh` invokes one `dispatcher.py tick --lane <lane> --limit <limit>` per configured lane for every repo-root argument given to it, defaulting to the `incoming_review` lane and a limit of 2 when unset — the operator-independent trigger that makes automatic discovery/dispatch possible instead of requiring a human to invoke `tick` by hand. | scripts/scheduled-tick.sh:40, scripts/scheduled-tick.sh:41, scripts/scheduled-tick.sh:42, scripts/scheduled-tick.sh:60, scripts/scheduled-tick.sh:61, scripts/scheduled-tick.sh:62 | RQA-BR-010 |
| The script's own exit status is the worst (non-zero) of every per-repo, per-lane tick it ran, so one failing repository or lane is reported without halting ticks for the others — the mechanism that lets one timer manage several independently-configured repositories at once. | scripts/scheduled-tick.sh:49, scripts/scheduled-tick.sh:53, scripts/scheduled-tick.sh:63, scripts/scheduled-tick.sh:68 | RQA-NFR-004 |
| `launchd.plist.example`'s `StartInterval` fires the trigger at a fixed 300-second cadence with `RunAtLoad` false, so loading the timer agent never itself spends model tokens (the plist's own comment: "RunAtLoad is deliberately false: loading an agent should not immediately spend model tokens"); the adaptive backoff intentionally does not live in the plist at all — it lives in the `cadence` table cadence.py persists, because "launchd cannot vary an interval." | scripts/launchd.plist.example:16, scripts/launchd.plist.example:19, scripts/launchd.plist.example:20, scripts/launchd.plist.example:55, scripts/launchd.plist.example:58, scripts/launchd.plist.example:59 | RQA-BR-012 |

### U-QUEUE-09 — atomic, crash-safe snapshot activation

Files: scripts/snapshot.py, tests/test_snapshot.py

Rationale: durability under a mid-write failure is a separable concern from
what a snapshot's identity is or how a job pins to one (U-QUEUE-10) —
dropping resume-by-hash would still require atomic activation to be safe, and
reworking activation would still need the identity/pin contract to work
unchanged.

| claim | evidence | requirements |
|---|---|---|
| `SnapshotStore.activate()` writes the by-hash archive file before the active-pointer file, each via write-to-temp-then-rename, so a failure at any point during activation leaves the previously active payload byte-for-byte intact rather than a half-written mixture; `SnapshotStore._load()` independently rejects any payload whose stored hash does not match a fresh recomputation over its own contents, rather than trusting a corrupted file. | scripts/snapshot.py:231, scripts/snapshot.py:232, scripts/snapshot.py:235, scripts/snapshot.py:236, scripts/snapshot.py:237, scripts/snapshot.py:238, scripts/snapshot.py:239, scripts/snapshot.py:186, scripts/snapshot.py:187, scripts/snapshot.py:188 | RQA-NFR-010 |

`test_failed_activation_retains_last_known_good`,
`test_no_temp_file_left_behind_after_activation`,
`test_corrupt_payload_is_rejected_not_trusted`
(tests/test_snapshot.py:177-241) corroborate this end to end.

### U-QUEUE-10 — content-hashed snapshot identity and pin/resume

Files: scripts/snapshot.py, tests/test_snapshot.py, tests/test_snapshot_pinning.py

Rationale: construction (fail-closed build), identity (content hash) and the
pin/resume guarantee are one responsibility — a job's snapshot must be built
and identified the same way it is later resumed, or the "a config edit
cannot retroactively change an in-flight job's authority" guarantee (the
module's own stated purpose) breaks.

| claim | evidence | requirements |
|---|---|---|
| `build_snapshot()` is fail-closed: it raises `SnapshotError` and produces no snapshot object for a non-object config or an unresolvable/invalid policy — never a partial or best-effort snapshot. | scripts/snapshot.py:134, scripts/snapshot.py:135, scripts/snapshot.py:136, scripts/snapshot.py:138, scripts/snapshot.py:139, scripts/snapshot.py:140 | RQA-NFR-010 |
| `content_hash()` covers the sorted-key canonical JSON of config and the review policy together in one hash, so any authority, model, threshold or route change in either value yields a different, independently reproducible hash — an edited policy is detectable without a rebuild, reinstall or redeploy. | scripts/snapshot.py:71, scripts/snapshot.py:72, scripts/snapshot.py:75, scripts/snapshot.py:78, scripts/snapshot.py:79 | RQA-FR-004, RQA-NFR-005 |
| `SnapshotStore.pin()` binds a result to a snapshot hash exactly once — re-pinning the same result to a different hash raises `SnapshotPinError` instead of silently relabelling it — and `SnapshotStore.get(hash)` lets a resumed job be dispatched under the exact archived config+policy its own job row recorded, rather than whatever snapshot happens to be active now, so an authoritative outcome can always be reconstructed against the protocol/policy actually in force when it was produced. | scripts/snapshot.py:244, scripts/snapshot.py:245, scripts/snapshot.py:246, scripts/snapshot.py:202, scripts/snapshot.py:208, scripts/snapshot.py:210 | RQA-FR-012 |

`resolve_snapshot` (scripts/dispatcher.py:1556, scripts/dispatcher.py:1559,
scripts/dispatcher.py:1561, scripts/dispatcher.py:1562,
scripts/dispatcher.py:1564, scripts/dispatcher.py:1565 — `dispatch`-cluster
code, cited for corroboration only) is the actual caller that reads a job's
`snapshot_hash` column and calls `store.get()` to resume under it; the
guarantee that makes that resumption safe is `SnapshotStore.get`/`pin`
themselves. `test_resumed_job_keeps_its_original_pin`
(tests/test_snapshot_pinning.py:124-141) corroborates the pair end to end.
`RQA-FR-004` is retained on the `content_hash()` row (unlike the analogous
cadence-config row in U-QUEUE-06): the hashed policy here is literally the
review policy `config["policy"]` carries, not scheduler/timer configuration,
so "a change to a repository's review policy... on that repository's next
review" is the correct subject.

### U-QUEUE-11 — validated job-transition table and enforcement

Files: scripts/states.py, tests/test_errors_states.py, tests/test_state_persistence.py

Rationale: the transition table (`states.py`) and its enforcement point
(`State.transition` in `scripts/common.py`, a `resilience`-cluster file) are
one mechanism — a table with no enforcement is decorative, and enforcement
with nothing to check against has nothing to refuse. The legacy `action` →
`completed` compatibility path is a separate, disposable responsibility;
see U-QUEUE-12.

| claim | evidence | requirements |
|---|---|---|
| `TRANSITIONS` enumerates a legal-move frozenset for every one of the 29 `ALL_STATES` states; a module-load assertion (`assert ALL_STATES == frozenset(TRANSITIONS)`) fails import if any state lacks an entry, so the table can never silently omit one. | scripts/states.py:43, scripts/states.py:78, scripts/states.py:118 | RQA-NFR-007 |
| `State.transition` (`common.py`) refuses to apply any transition for a job that does not exist: `current_status(job_id)` returning `None` raises `JobBlockingError` before `states.assert_transition` is ever called and before any write, regardless of the requested target. | scripts/common.py:413, scripts/common.py:414, scripts/common.py:415, scripts/common.py:418 | RQA-NFR-010 |
| Separately, and only for a job whose current status IS known, `can_transition`/`assert_transition` refuse any move outside that status's legal-targets frozenset in `TRANSITIONS`, raising `JobBlockingError` without changing the persisted status. `can_transition(None, target)` itself does not implement the nonexistent-job refusal above — it special-cases only the bootstrap case, returning `target == "detected"` for a `None` current status — so a caller that skipped `State.transition`'s own prior existence check could still create a job via this path. | scripts/states.py:121, scripts/states.py:123, scripts/states.py:124, scripts/states.py:126, scripts/states.py:134, scripts/states.py:136, scripts/states.py:138, scripts/states.py:139 | RQA-NFR-010 |
| `safe_stop` is a legal target from every one of the 14 `NONTERMINAL` statuses `queue.py` tracks, giving a persistence or logging failure partway through any in-progress job a deterministic, always-legal stop rather than requiring an invented transition. | scripts/states.py:79, scripts/states.py:86, scripts/states.py:87, scripts/states.py:88, scripts/states.py:89, scripts/states.py:92, scripts/states.py:94, scripts/states.py:96, scripts/states.py:100, scripts/states.py:102, scripts/states.py:104, scripts/states.py:105, scripts/states.py:108, scripts/states.py:109; scripts/queue.py:31, scripts/queue.py:34 | RQA-FR-038, RQA-NFR-010 |

`test_transition_on_nonexistent_job_raises_without_write` and
`test_illegal_transition_leaves_state_and_logs_error_not_success`
(tests/test_state_persistence.py:38-76), plus
`test_assert_transition_raises_on_illegal` and
`test_illegal_transitions_rejected` (tests/test_errors_states.py:68-83),
corroborate rows two and three end to end. `tests/test_state_persistence.py`
also covers idempotent `human_requests`/approval table creation and a
`StatePersistenceError` wrapper around raw `sqlite3.Error` — behaviour
`scripts/common.py` (`resilience`) implements and decides, named here only
because `clusters.md` places the whole test file in `queue`.

`assert_job_exists` (scripts/states.py:129-131) is present in the module but
has no caller anywhere under `scripts/` — confirmed by search (the only match
for the name in `scripts/` is its own definition). It is dead code: the
nonexistent-job refusal a reader might expect it to provide is actually
performed by `common.py`'s own `current_status(job_id) is None` check (row
two, above), not by this function.

### U-QUEUE-12 — legacy `action` → `completed` compatibility path

Files: scripts/states.py, tests/test_errors_states.py

Rationale: split out of U-QUEUE-11 because it is separable under
methodology §4's own definition — it serves a disjoint requirement
(`RQA-FR-034` alone), it exists for a different reason to change (existing-
caller compatibility, not the general validation guarantee), and it is
independently removable: deleting the `action`/`completed` legacy states
would leave the validated transition machinery in U-QUEUE-11 completely
intact.

| claim | evidence | requirements |
|---|---|---|
| The transition table legalises `action` → `completed` (`"action": frozenset({"completed", ...})`) alongside the newer approval-aware flow (`adjudication` → `approval_evaluation` → ... → `completed_auto_approved`/`completed_human_declined`/`completed_advisory`); the module's own docstring states this legacy path "is preserved for existing callers but now coexists with the approval-aware flow." | scripts/states.py:104 | RQA-FR-034 |

`test_legal_transitions_flow` (tests/test_errors_states.py:59-65) exercises
`can_transition("action", "completed")` directly, corroborating the table
entry is live and reachable, not vestigial. `RQA-FR-034` ("every
architectural component retained... shall be justified as materially
serving a criterion... or as required by a constraint") is a genuine fit
here specifically because the module's own comment supplies exactly that
justification — existing-caller compatibility — rather than this analysis
inferring one.

### U-QUEUE-13 — closed-PR ingestion into independent, fail-closed calibration samples

Files: scripts/history.py, tests/test_history.py

Rationale: `classify_outcome`, `_timestamps` and `checks_ok_timestamp` are
read separately by `tests/test_history.py`, but all three exist to serve one
responsibility — producing a calibration sample whose outcome label was not
produced by, and cannot be flattered by, the thing later being calibrated.

| claim | evidence | requirements |
|---|---|---|
| No file under `scripts/` other than `history.py` itself imports `history` or calls `ingest()` — confirmed by search — and `ingest()` is reachable only from the module's own documented CLI `main` (`scripts/history.py:302-305`) and via the operator command in `OPERATORS.md`'s undisclaimed entry-point table, run as `python3 scripts/history.py --repo-root <repo> ...` from the operator's own machine. The only importers anywhere in the tree are `tests/test_shadow_cli.py:34`, `tests/test_checks_vocabulary.py:30` and `tests/test_history.py:17`, which establish that the module is tested, not that anything reaches it from a product path outside its own documented command (§2.3). | OPERATORS.md:308, OPERATORS.md:556 | RQA-NFR-006 |

`classify_outcome`'s outcome discipline, `_timestamps`'s hindsight rule and
`checks_ok_timestamp`'s fail-closed check evidence have **no** genuine
requirement tie and are deliberately left out of the table above rather than
forced onto one, per round-1 findings against this exact substitution
(`RQA-FR-037` and `RQA-NFR-010` were each cited in round 1 for a live-review
obligation, not history.py's offline classification of already-closed PRs —
a different subject, as this same paragraph already conceded). Documented
here as prose instead:

- `classify_outcome` requires positive human-review evidence before ever
  labelling an outcome anything other than `unknown`: a later revert PR
  naming the number is `adverse` regardless of prior approval
  (scripts/history.py:68-69); a human `CHANGES_REQUESTED` review is
  `contested` (scripts/history.py:77-78); a PR merged with no human review
  signal at all is `unknown`, never `clean` (scripts/history.py:85-86,
  scripts/history.py:90-91).
- `checks_ok_timestamp` treats a still-running check
  (scripts/history.py:187-188), a failed check (scripts/history.py:191-192),
  or a check with no completion time (scripts/history.py:193-196) as
  fail-closed — the whole check-evidence result becomes `None` — rather than
  as partial success.
- the self-review exclusion (scripts/history.py:71-74), the
  at-or-before-merge-cutoff hindsight rule that deliberately excludes
  `pr.updated_at` (scripts/history.py:104-119), and revert-title detection
  (scripts/history.py:42-54).

`calibrat`, `backtest`, `shadow` and `historical accuracy` do not occur as a
requirement subject in `requirements/requirements-specification.md`
(`historical` occurs three times, all inside `RQA-FR-016`'s and
`RQA-NFR-007`'s own text about *not* needing a human to reconcile "historical
reviews, comments or checks" — a different concern from calibration
sampling). The calibration/backtest tooling this file supports (consumed
downstream by `scripts/shadow.py`, a `verdict`-cluster file) is real, tested,
and reachable, but bears on no requirement in the 86 — a genuine
unrequired-behaviour finding, out of scope for this analysis (requirement
coverage is judged in the register); it is not an oversight here.

### U-QUEUE-14 — the persisted PR-fact cache is the sole source of the observed current head used to detect a stale review

Files: scripts/queue.py, tests/test_stale_head.py

Rationale: the regression this file guards against is a queue-owned data
freshness contract — that `prs.payload`'s head SHA is the truly-observed
current head, not a copy of whatever head a job happened to be reviewed
against — even though the consuming gate computation
(`dispatcher._load_pr_facts`, `approval_evaluate.compute_gates`,
`approval_evaluate.evaluate`) lives in `dispatch`/`authority`-cluster files,
cited below for corroboration and, for the gate/persistence decision itself,
as primary evidence alongside `queue.py`.

| claim | evidence | requirements |
|---|---|---|
| `queue.py`'s `reconcile()` is the only writer of the `prs.payload` row for a given `(repo, number)`: every reconciliation pass upserts the head SHA it just observed from the inventory read, so `prs.payload["head"]["sha"]` is the queue's own record of the currently observed head, independent of any job's own previously-reviewed head. | scripts/queue.py:96, scripts/queue.py:105, scripts/queue.py:109 | RQA-FR-006 |
| That persisted head is compared against the head a job was reviewed against in `approval_evaluate.compute_gates`'s own `head_matches` gate; when they diverge, `evaluate()` includes `head_matches` in `failed`, takes the `if failed:` branch, and returns `human_escalation` **without** ever calling `_persist_eligible` — so a stale value in `queue.py`'s own persisted fact cache is what prevents an eligible decision being recorded against a revision that has since moved on, not merely what a test happens to assert about it. | scripts/approval_evaluate.py:189, scripts/approval_evaluate.py:272, scripts/approval_evaluate.py:281, scripts/approval_evaluate.py:284, scripts/approval_evaluate.py:286 | RQA-NFR-010, RQA-BR-007 |

`dispatcher._pr_payload`/`_load_pr_facts` (scripts/dispatcher.py:221,
scripts/dispatcher.py:223, scripts/dispatcher.py:257, scripts/dispatcher.py:258
— `dispatch`-cluster code) is the reader that turns `queue.py`'s persisted fact
into `PRFacts.head_sha`; the regression the test file's own docstring
describes (tests/test_stale_head.py:4-7: "`_load_pr_facts` fell back to the
job's own head... could never fail") is precisely about that reader ceasing
to trust a stale local fallback in favour of the queue's persisted
observation. `test_advanced_head_fails_the_gate`
(tests/test_stale_head.py:75-81) and
`test_head_gate_blocks_the_live_approval_decision`
(tests/test_stale_head.py:50-58, tests/test_stale_head.py:98-136) corroborate
the second row end to end, including the assertion that no
`approval_decisions` row is written for the stale-head case.
