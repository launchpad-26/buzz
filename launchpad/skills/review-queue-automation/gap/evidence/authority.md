# RQA gap analysis — evidence: authority

Cluster `authority`: what the system is allowed to do to a pull request and how
that is gated — the authority model, the action gate, approval evaluation and
execution, the GitHub auth/query/mutate/REST surface, notification, and the
human queue CLI. 21 assessed files, per [`../clusters.md`](../clusters.md).
Revision `9267b6308714454a3b987622d90cda03a8972827`. Citations are `path:line`
relative to `launchpad/skills/review-queue-automation/`.

### U-AUTHORITY-01 — Per-repo, per-activity authority mode resolution

Files: scripts/authority.py

| claim | evidence | requirements |
| --- | --- | --- |
| The module recognises exactly six activities — `review`, `comment`, `approve`, `request_changes`, `triage`, `fix` — each resolving to an independent mode; no `merge` activity is defined anywhere in the module. | scripts/authority.py:32-34 | RQA-NFR-017, RQA-FR-029, RQA-NFR-008 |
| `mode_for` resolves the effective mode by precedence — a repo-scoped `authority[repo][activity]` override, then a global `authority[activity]` key, then `authority.default`, then the module constant `DEFAULT_MODE` — and returns `"disabled"` for an unrecognised activity, an absent/falsy authority section, or a dict that matches nothing at any level; a truthy *non-dict* `authority` value (e.g. a string or list) is not handled — `_repo_authority` calls `.get(repo)` on it unconditionally and raises `AttributeError` rather than failing closed. | scripts/authority.py:88-121 | RQA-NFR-018, RQA-NFR-026 |
| `defaults()` returns `"disabled"` for every one of the six activities, and `DEFAULT_MODE` (`"disabled"`) is the value `mode_for` falls back to whenever no configuration matches; nothing in the module defaults an activity to an enabled mode. | scripts/authority.py:44, 149-151 | RQA-NFR-026 |
| `can_act` denies every activity in `"disabled"`, `"shadow"`, and `"human_escalation"` modes outright; for a `"live"`-mode activity classified mutating (`approve`, `request_changes`, `fix`), it returns `True` only when `repo_hard_gate_ok` is true — but that parameter **defaults to `True`** in the function's own signature, so a caller that simply omits it (not only one that explicitly passes it) still gets a live mutating action authorised; a non-mutating activity (`review`, `comment`, `triage`) needs only a non-disabled mode. | scripts/authority.py:40-42, 128-146 | RQA-NFR-017 |
| `validate_authority` returns a list of issue strings for a malformed authority section (wrong type, unknown activity name, unrecognised mode) rather than raising, and never itself grants a mode — the module's own comment records that a `"live"` mutating mode still depends on "the full gate" enforced by the action executors regardless of what this function accepts. | scripts/authority.py:51-85 | RQA-NFR-018 |

### U-AUTHORITY-02 — GitHub auth token discovery, proven-capability probing and capability-bounded downgrade

Files: scripts/github_auth.py, tests/test_github_auth.py

Rationale: token discovery, capability derivation from proven repository
permissions, and the authority downgrade that follows from an unproven
capability are one continuous "prove capability, then bound configured
authority to it" pipeline that `probe()` and `downgrade_config_for_mode`
implement together; `test_github_auth.py` is the only test exercising every
stage of it.

| claim | evidence | requirements |
| --- | --- | --- |
| `capabilities_from_permissions` derives `can_submit_review`/`can_add_labels` from the repository's returned `permissions` object (`pull`/`triage`/`push`/`admin`); `can_create_issue` additionally depends on a separate caller-supplied `has_issues` flag, not on the permissions object alone. `unknown = ("permissions",)` is recorded only when the whole permissions object is absent, non-dict, or empty — an individual omitted key inside an otherwise-present object (e.g. no `triage` key) is never flagged unknown, it is silently read as `False` via `flags.get(k, False)`. Nothing in this module inspects the credential's own granted OAuth/PAT scope, so it cannot confirm the token itself is scoped to exactly pull-request-write plus contents-read (plus remediation/merge write only where configured). | scripts/github_auth.py:103-142; tests/test_github_auth.py:159-164 (absent permissions object is unknown and absent), 167-172 (issues disabled blocks issue creation) | RQA-NFR-024, RQA-NFR-030 |

### U-AUTHORITY-03 — Deterministic approval gate computation and disposition

Files: scripts/approval_evaluate.py, tests/test_approval_policy.py

Rationale: `compute_gates` (the gate state) and `evaluate` (the disposition that
follows from it) are one evaluated-then-dispositioned pipeline; every gate
`test_approval_policy.py` exercises is asserted through `evaluate`'s returned
disposition, never through `compute_gates` in isolation.

| claim | evidence | requirements |
| --- | --- | --- |
| `compute_gates` treats `approval.approval_enabled` (with `approval.mode == "live"`) and the per-activity `authority.approve == "live"` mode as conjunctive — both must hold for the resulting gate's `approval_enabled` to be true; the module's own comment records that only the former was consulted previously, so `authority.approve: disabled` used to be silently ignored. | scripts/approval_evaluate.py:139-151, 183-184; tests/test_approval_policy.py:147-153 (approval_enabled=False and live_canary_approved=False each independently block live) | RQA-NFR-017 |
| Every external-evidence gate (`bounded_change`, `audit_writable`, `assurance_met`, `revalidation_ok`, `rate_limit_ok`) is `False` whenever the caller passes an explicit `ApprovalEvidence` and leaves that field `None`; only an explicit caller-supplied `True` can satisfy it. | scripts/approval_evaluate.py:170-213; tests/test_approval_policy.py:140-146 (each external-evidence gate individually blocks live when set False) | RQA-FR-011, RQA-FR-037 |
| `evaluate()` in `"live"` mode returns `"human_escalation"` — never a persisted eligible decision — whenever any changed file matches a configured protected-trigger pattern, or whenever any gate in `gates.failed()` is non-empty; it persists an eligible decision only when both are clear. | scripts/approval_evaluate.py:268-288; tests/test_approval_policy.py:120-155 (every negative gate blocks live), 158-167 (protected trigger always blocks live, no decision row is ever written) | RQA-FR-011, RQA-FR-037, RQA-BR-011 |
| `policy_hash_of` hashes the full current config, not a fragment, so a change anywhere in the runtime policy (not only the risk section) invalidates a decision keyed to the previous hash. | scripts/approval_evaluate.py:61-65; tests/test_approval_policy.py:187-193 (an unrelated logging-key edit still changes the hash) | RQA-FR-004 |

### U-AUTHORITY-04 — Deterministic request-changes action gate

Files: scripts/action_gate.py, tests/test_request_changes.py

Rationale: `action_gate.py`'s single gate function has no `__main__` and no
caller of its own within this cluster; it is exercised end to end only through
`dispatcher.py`'s wiring into `github_mutate.execute_request_changes`, which
`test_request_changes.py`'s dispatcher-path tests drive — the gate and the
mutation it authorises are one behavioural unit.

| claim | evidence | requirements |
| --- | --- | --- |
| `request_changes_gate` denies the action unless every one of: `request_changes` authority resolves live, `verified_blocker` is true, `blocker_evidence_sufficient` is true, `assurance.assurance_met` is true, and a supplied `revalidate()` callable returns true; any missing or false condition appends a named entry to `failed` and the gate denies rather than defaulting to allow. The exact-head check is conditional, not fail-closed: `if pr.get("head") and pr["head"] != head_sha` only fires when `pr["head"]` is present and non-empty — an absent or empty `pr["head"]` skips the check entirely rather than being treated as a denial (no `exact_head` entry is appended). The only production caller, `dispatcher.py`, always supplies a non-empty `pr["head"]` that defaults to `head_sha` itself when the cached payload has none, which closes this gap operationally but not inside the gate function itself. | scripts/action_gate.py:63-71 | RQA-FR-009, RQA-BR-004 |
| `dispatcher.py` is the only caller that wires `request_changes_gate`, supplying `revalidate` bound to a fresh REST read and a `rest_probe` used to confirm the posted review afterward, and it does so for every `dispatch-one`/`sweep`/`tick` job carrying a corroborated defect — the gate is reachable under E2 despite having no CLI or `__main__` of its own. | scripts/action_gate.py:49-83 (the gate's signature requiring an injected `revalidate`); scripts/dispatcher.py:878-879, 965-968, 708-736 | RQA-FR-009, RQA-BR-004 |
| Under live `request_changes` authority, a defect is corroborated — and only then eligible to produce a `CHANGES_REQUESTED` mutation — under a two-branch rule: two distinct provider families independently locate it, **or** one family locates it citing a check that actually failed. An uncorroborated defect (a single family with no corroborating failed check) never mutates and instead escalates to a human (`request_changes_outcome` of `"uncorroborated"`); a `request_changes` authority not live also escalates rather than mutating (`"authority_not_live"`). | scripts/dispatcher.py:870-877 (the two-branch corroboration rule, in the function's own docstring), 914-950 (corroborate() call, the uncorroborated-escalates branch, and the authority-not-live branch); tests/test_request_changes.py:246-253 (default authority never requests changes), 256-262 (uncorroborated defect escalates without mutating), 265-277 (two families with live authority requests changes), 279-287 (a single family backed by one failing named check also requests changes) | RQA-FR-009, RQA-BR-004 |
| A failed `revalidate()` denies the gate (`"final_revalidation"` recorded in `failed_gates`, via the `g.allowed = len(g.failed) == 0` aggregate), no mutation is posted, and the job is queued for a human decision rather than left stalled or silently marked successful. | scripts/action_gate.py:78-83 (final-revalidation deny and the aggregate denial); scripts/dispatcher.py:964-990 (the gate call and the human-queue handoff on denial); tests/test_request_changes.py:302-310 (failed revalidation denies and queues human) | RQA-FR-037, RQA-NFR-010 |

### U-AUTHORITY-05 — Durable SQLite human-approval request queue

Files: scripts/approval.py, tests/test_human_queue.py
Rationale: `approval.py` is the SQLite persistence layer for a human request
and `test_human_queue.py` is the only test exercising its full lifecycle
(enqueue, decide, expire, supersede) end to end; neither is coherent judged
apart from the other.


| claim | evidence | requirements |
| --- | --- | --- |
| `enqueue` is idempotent per `(repo, number, head_sha, policy_hash, job_id)` — a matching pending row is returned unchanged rather than duplicated — and the schema carries `recommendation`, `rationale`, `action` and `failed_gates` columns on every enqueued row. `enqueue` performs no non-empty/content validation on any of these fields (`(rationale or "")[:800]`, `failed_gates or []` both accept and store an empty value without complaint), so the function itself guarantees the columns exist, not that a caller populated them with a specific name. | scripts/approval.py:85-155 (dedupe at 109-118, unvalidated storage at 122-146); tests/test_human_queue.py:277-286 (idempotent enqueue) | RQA-BR-007, RQA-FR-026 |
| `decide` only accepts `approve`/`decline`/`request_changes` on a row whose state is still `"pending"` and that is not expired, and it always records the deciding `actor` and `reason` on the row; `decline` and `request_changes` additionally move a bound job to the terminal state `completed_human_declined`, but only when that job's current status is exactly `human_approval_pending` — `_decline_job` returns `False` and leaves any other job status untouched. | scripts/approval.py:233-271, 274-290 (esp. the status guard); tests/test_human_queue.py:259-274 (decline is terminal; a decided request cannot be decided again) | RQA-FR-013, RQA-BR-011 |
| `is_eligible`/`find_approved` reject a decision whose stored `head_sha` or `policy_hash` no longer matches the caller-supplied current values, or whose `expires_at` has passed, before treating it as usable — an approval cannot outlive the revision or the policy it was made against. | scripts/approval.py:183-201, 204-230; tests/test_human_queue.py:214-233 (expired approval cannot resume), 237-256 (stale-SHA cannot resume) | RQA-FR-011, RQA-FR-037 |
| `supersede_for_head`/`supersede_for_policy` mark every other pending request for a `(repo, number)` as `"superseded"` once its head SHA or policy hash no longer matches current state, so a stale request cannot later be approved against a newer revision. | scripts/approval.py:316-352; tests/test_human_queue.py:289-303 (superseded on changed head and policy) | RQA-FR-011 |

### U-AUTHORITY-06 — Human decision CLI: inspect and decide pending requests

Files: scripts/human_cli.py

| claim | evidence | requirements |
| --- | --- | --- |
| The CLI requires `--actor` for `decide` (argparse `required=True`), so a decision can never be recorded through this surface without naming who made it; `OPERATORS.md`'s runbook table names `scripts/human_cli.py` against its own section (§6) and separately documents the exact `list`/`show`/`decide`/`resume`/`supersede` invocations as commands an operator runs, so this named-authorship enforcement is reachable under E4 as a documented operator procedure, not merely an inventoried `__main__` block. | scripts/human_cli.py:216-220; OPERATORS.md:554-555, 249-254 | RQA-FR-013 |

### U-AUTHORITY-07 — Human-authorized resume through the guarded approval executor

Files: scripts/human_cli.py, tests/test_human_execution.py

Rationale: `resume` is the one code path in `human_cli.py` that mutates GitHub;
it is exercised end to end (live-head reread, staleness revalidation, guarded
execution) only by `test_human_execution.py`, which is why it is judged
separately from the read-only CLI surface of U-AUTHORITY-06.

| claim | evidence | requirements |
| --- | --- | --- |
| `_cmd_resume` refuses — returning an `"error"` without transitioning the job — when the job is not `status == "human_approval_pending"`, when the live PR head cannot be read and `--allow-recorded-head` was not passed, or when the live/override head does not match the job's recorded head; an unreadable head is treated as a refusal, never as a pass. | scripts/human_cli.py:83-112; tests/test_human_execution.py:167-183 (stale head never reaches the executor), 186-200 (job not awaiting approval is refused), 203-209 (unknown job is refused) | RQA-FR-011, RQA-FR-037, RQA-NFR-010 |
| `_cmd_resume` locates the bound approval only through `approval.find_approved`, which itself rejects an expired, stale-SHA, or stale-policy decision, so a human decision that no longer matches current state cannot resume a job. | scripts/human_cli.py:114-119 | RQA-FR-011, RQA-FR-037 |
| `_apply_human_approval` records the human authorization through `persist_human_approval` and then runs the *same* `approval_action.approve` executor the automatic live path uses — mandatory REST revalidation before the mutation, REST verification after — so a human decision authorizes an approval rather than bypassing those checks. | scripts/human_cli.py:147-185; tests/test_human_execution.py:80-98 (human decision uses the same guarded executor), 101-117 (decision is recorded as human-authorized; the review body names the authorizing actor) | RQA-FR-028, RQA-BR-011, RQA-FR-013 |
| On any outcome other than a verified `APPROVED` (uncertain mutation, missing cached PR node id, other failure), the job is moved to `safe_stop` with the reported reason, rather than left pending or marked approved. | scripts/human_cli.py:165-171, 186-204; tests/test_human_execution.py:64-77 (a verified approval reaches `completed_auto_approved`), 121-132 (uncertain mutation safe-stops), 135-147 (missing node id safe-stops before any mutation) | RQA-NFR-010, RQA-FR-037 |

### U-AUTHORITY-08 — Guarded APPROVE mutation execution with mandatory pre/post REST checks

Files: scripts/approval_action.py, scripts/github_mutate.py, tests/test_mutations.py, tests/test_approval_policy.py

Rationale: `approval_action.approve` loads the decision and immediately calls
`github_mutate.execute_approval`; the two implement one indivisible
guarded-executor responsibility — decision loaded from SQLite by ID,
independently revalidated, mandatory REST checks before and after the
mutation — that could not be disposed of separately without the judgement on
one becoming incoherent against the other.

| claim | evidence | requirements |
| --- | --- | --- |
| `approve()` loads the decision exclusively from SQLite by `decision_id` (never from caller-supplied JSON) and only then calls `execute_approval`, passing its own `repo`/`number` keyword arguments straight through. `execute_approval`'s "independent" comparison is conditional on those being non-empty: its own signature defaults `repo=""`/`number=0`, and when either is falsy, `require_eligible_decision` substitutes the decision record's own stored `repo`/`number` (`repo or record.get("repo", "")`, `number if number else int(record.get("number", 0))`), so the comparison degenerates into checking the stored record against itself. This fallback is **not reachable through `approval_action.approve`**: `approve()`'s own signature declares `repo: str` and `number: int` as required keyword-only parameters with no default, and both of its production callers (`dispatcher.py`'s `_execute_live_approval` and `human_cli.py`'s `_apply_human_approval`) source them from the `jobs` table's `repo`/`number` columns, which `common.py`'s schema declares `NOT NULL`. The fallback is reachable only through `github_mutate.py`'s own disclaimed `main()` CLI, whose `--repo`/`--number` argparse flags default to `""`/`0` when omitted. | scripts/approval_action.py:39-46, 126-141, 152-183 (required `repo`/`number` parameters); scripts/github_mutate.py:173-207, 304-321, 343-358, 463-478 (the defaulted signature, the fallback, and the CLI argparse defaults); scripts/common.py:231-245 (`jobs.repo`/`jobs.number` are `NOT NULL`); tests/test_mutations.py:159-184 (loads eligible decision by id from SQLite; caller JSON is forged and ignored) | RQA-FR-011, RQA-FR-037 |
| `execute_approval` refuses the mutation with `PermissionAuthorityError` unless `rest_before()` is supplied and every reported check is truthy — a missing revalidation callable, or any single failing check, blocks the mutation before it is ever sent. | scripts/github_mutate.py:255-272, 368-369; tests/test_mutations.py:187-208 (mandatory revalidation before mutation), 211-232 (revalidation failure blocks mutation) | RQA-NFR-010, RQA-FR-037 |
| After sending, `_normalize_verification` classifies the post-mutation REST read into `verified`/`failed`/`uncertain`; only `verified` is persisted as the mutation's final state, `uncertain` raises `MutationUncertainError` without a second send, and a retry against an already `pending`/`uncertain`/`failed` client-mutation-id re-verifies rather than re-sending. The actual login/state/head-SHA confirmation this classification depends on is decided one layer up, in `approval_action.build_verification`, which confirms an `APPROVED` review by the expected login on the exact head SHA before `_normalize_verification` ever sees a string result. | scripts/github_mutate.py:275-301, 392-409 (the classification and lifecycle); scripts/approval_action.py:79-99 (`build_verification`, where the login/state/head-SHA confirmation is actually decided); tests/test_mutations.py:235-275 (uncertain persists and is never blindly retried), 278-295 (verified only persisted after confirmation), 298-316 (failed lifecycle raises without ever recording verified) | RQA-NFR-010, RQA-BR-007 |
| The generic `post()` entry point refuses every mutation flagged `approval_required` (currently only `approve_review`) before it builds a request, so no caller can reach an APPROVE mutation through the non-guarded path. | scripts/github_mutate.py:116-117, 209-229; tests/test_mutations.py:65-81 (generic post cannot approve) | RQA-NFR-017 |
| `build_revalidation`/`build_verification` bind the mandatory pre/post checks to live `RestReader` reads (`pr_meta`, `pr_reviews`) whenever the caller does not inject fakes, so production approval can never skip revalidation or verification for lack of wiring. | scripts/approval_action.py:49-113; tests/test_approval_policy.py:201-236 (load_eligible_decision and revalidation in approval_action; a protected file in the revalidated set fails `no_protected_trigger` closed) | RQA-NFR-010 |

### U-AUTHORITY-09 — Fixed-event GitHub mutation transport (comment / request-changes / issue / labels / reviewer-request / thread-reply / assignee)

Files: scripts/github_mutate.py

| claim | evidence | requirements |
| --- | --- | --- |
| Every mutation named in the `MUTATIONS` registry fixes its GraphQL `event` (or has none) at module scope; the caller supplies only variables such as `pullRequestId`/`body`, never an `event` value, so `add_comment_review` can only ever post `COMMENT` and `request_changes_review` only `CHANGES_REQUESTED`. | scripts/github_mutate.py:40-64, 99-113; tests/test_mutations.py:84-88 (fixed events are never caller supplied) | RQA-NFR-017 |
| `post()` keys every non-approval mutation by a deterministic `mutation_id(job, operation)` and returns the previously recorded `"completed"` response instead of re-sending when that id already exists, so a retried caller cannot duplicate a comment/request-changes/label/issue mutation raised for the same job. | scripts/github_mutate.py:142-160, 209-252 (dedupe at 231-234) | RQA-BR-007 |
| `execute_request_changes`/`execute_comment_review` verify their own effect through an injected `rest_probe` *when one is supplied and confirmable*: `if rest_probe is not None and login and head_sha` gates the check entirely, so a caller that passes no probe (or no login/head_sha) skips verification with no error at all, and a `rest_probe` that itself raises propagates that exception uncaught rather than being converted to `MutationUncertainError` — only a probe that runs, returns, and fails to confirm the expected review state raises `MutationUncertainError`. Despite `OPERATORS.md`'s disclaimed second table listing this module as an internal, non-operator-invoked module, `execute_request_changes` is exactly what `dispatcher.py` imports directly for the CHANGES_REQUESTED path, and `dispatcher.py`'s own `_rc_transport` always supplies a real probe/login/head_sha, so this verification is what actually runs in production under E2, not merely in a hand-invoked `__main__`. | scripts/github_mutate.py:412-437 (the conditional probe check); OPERATORS.md:560-564, 578; scripts/dispatcher.py:701-705, 708-736 (`_rc_transport` supplying the real probe) | RQA-NFR-010 |

### U-AUTHORITY-10 — Bulk read-only GraphQL queue-inventory transport

Files: scripts/github_query.py, tests/test_github_query.py

Rationale: `github_query.py` is the bulk-inventory transport and
`test_github_query.py` is the dedicated test closing the coverage gap
`tests/test_queue.py` left (the outer page cap and the allowlist rejection
were untested until this file existed); the two are judged as one read-path
chokepoint.

| claim | evidence | requirements |
| --- | --- | --- |
| `_complete` refuses (raises `InventoryError`) rather than returning a partial list once a paginated connection (files/reviews/assignees/review-requests/check-contexts) exceeds `_CONNECTION_PAGE_CAP` pages, and the outer pull-request walk in `queue_inventory` refuses to continue once it exceeds `_PR_PAGE_CAP` pages, rather than silently returning a truncated queue. | scripts/github_query.py:306-334, 478-503 (esp. 484-490); tests/test_github_query.py:67-95 (exceeding the outer page cap raises rather than truncating), 98-116 (a walk that fits inside the cap completes) | RQA-NFR-010 |
| `_packet` raises when the completed file list's length disagrees with GitHub's own `changedFiles` count, and separately raises when a node carries no `headRefOid`, so a PR is never folded into the inventory with an understated file set or an unresolved head SHA. | scripts/github_query.py:392-395, 415-423 | RQA-NFR-010 |
| `queue_inventory` raises `InventoryError` when the queried repository comes back `null` (not visible to the authenticated token) rather than silently returning an empty or partial queue for it. | scripts/github_query.py:494-496; tests/test_github_query.py:119-127 (a repository the token cannot see raises) | RQA-NFR-010 |
| GraphQL `errors` in a response are raised as `InventoryError` carrying the operation name and error payload, never silently swallowed or treated as an empty result. | scripts/github_query.py:298-301; tests/test_github_query.py:194-203 (GraphQL errors are reported, not swallowed) | RQA-NFR-010 |

### U-AUTHORITY-11 — Allowlisted per-PR REST read transport and its ETag-cached backing GET

Files: scripts/github_rest.py, tests/test_rest_reader_surface.py, tests/test_rest_cache.py

Rationale: `github_rest.RestReader` is the sole per-PR REST surface every other
module in this cluster constructs; its correctness rests on the ETag-cached
`GithubRest.get` it wraps (defined in `scripts/common.py`, cited here rather
than assumed present on `github_rest.py` itself, per the "attribute by the
module that defines the symbol" rule); `test_rest_reader_surface.py` and
`test_rest_cache.py` are the two tests guarding, respectively, the wrapper's
method surface and the cache's fail-closed behaviour.

| claim | evidence | requirements |
| --- | --- | --- |
| `RestReader` exposes one method per allowlisted REST read (`pr_meta`, `pr_reviews`, `review_comments`, `issue_comments`, `requested_reviewers`, `changed_files`, `checks`), each hitting exactly one path; `changed_files` is paginated (`paginate=True`) so a large PR's file list is never returned truncated to the caller that decides `no_protected_trigger`/`limits_pass` from it. | scripts/github_rest.py:14, 60-90, 92-121; tests/test_rest_reader_surface.py:132-142 (changed_files specifically exists and is paginated) | RQA-NFR-010 |
| The `GithubRest.get` transport `RestReader` wraps caches each URL's `etag`+`body`+`Link` header in SQLite and reuses the cached body on a `304`, but raises rather than silently returning nothing when a `304` arrives with no cached body on record, and re-derives the pagination `Link` from the cached row (not just the in-flight response) so a `304`'d page never loses its own "next page" link. | scripts/common.py:525-566 (esp. 535-537, 552-566); tests/test_rest_cache.py:94-121 (a cached page 1 hitting 304 still returns page 2 via the persisted Link), 123-137 (304 without a cached body fails closed) | RQA-NFR-010 |
| `open_prs`/`closed_prs` refuse to keep paginating once more than `page_cap` (default 5) REST pages have been walked, raising rather than returning a silently truncated PR list. | scripts/github_rest.py:18-35 | RQA-NFR-010 |

### U-AUTHORITY-12 — Human notification delivery (file/command/none transports)

Files: scripts/notify.py, tests/test_notify.py
Rationale: `notify.py` is the sole delivery mechanism for a durable
`human_requests` row and `test_notify.py` is the only test asserting its
behaviour (packet construction, redaction, and every transport's failure
mode); neither is meaningful judged apart from the other.


| claim | evidence | requirements |
| --- | --- | --- |
| `deliver()` carries no urgency or routing parameter: every dispatched escalation, whatever gate or trigger raised it, is delivered through the same single configured transport with no distinction in delivery transport or urgency routing between a routine gate failure and a protected-trigger denial. `build_packet` does still render the `protected_paths` field (populated from the request's stored `protected` list) when non-empty, so the packet's *content* can differ by cause even though the delivery mechanism does not. | scripts/notify.py:94-135 (esp. the `protected_paths` field), 180-196 | RQA-FR-025, RQA-BR-013 |
