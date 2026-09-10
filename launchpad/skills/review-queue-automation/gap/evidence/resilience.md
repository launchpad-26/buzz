# RQA gap analysis — evidence: resilience

Cluster `resilience` per [`../clusters.md`](../clusters.md): budget, fallback and its
recipes, the error taxonomy, OTel logging, the explain surface, the ledger,
advisory output, and the shared `common`/`cli` substrate. Revision
`9267b6308714454a3b987622d90cda03a8972827`. All paths below are relative to
`launchpad/skills/review-queue-automation/`, per [`../methodology.md`](../methodology.md).

### U-RESILIENCE-01 — Pre-spend budget reservation and spend accounting
Files: scripts/budget.py, tests/test_budget_controls.py
Rationale: tests/test_budget_controls.py is the sole test exercising reserve()'s token/attempt/concurrency gate and budget.py's spend accounting, and shares its disposition.

| claim | evidence | requirements |
| --- | --- | --- |
| reserve() projects already-spent tokens plus the requested reservation against `per_pr_tokens` and `per_repo_daily_tokens` and refuses the reservation, downgrading to `draft`, before recording any spend when the projection would exceed either ceiling | scripts/budget.py:396-414 | RQA-FR-039, RQA-BR-012 |
| reserve() separately refuses when the job's recorded attempt count has reached `max_attempts_per_job` (downgrading to `human`) or when `max_concurrent_jobs` other jobs are already in flight (downgrading to `draft`), naming which specific limit was hit in each refusal | scripts/budget.py:377-394 | RQA-FR-022, RQA-FR-039 |
| record_reservation() is called only on the success path, immediately before reserve() returns allowed=True; every refusal branch returns before that call, so a refused attempt is never counted toward a later ceiling check | scripts/budget.py:416-420 | RQA-FR-039 |
| record_spend() persists the strategy's reserved token count as what an attempt cost because runners never report an actual token count, and the module's own docstring states this over-counts rather than under-counts; the stored row carries no field distinguishing this estimated figure from a measured one | scripts/budget.py:16-19, 217-220, 226-230 | RQA-FR-021 |

### U-RESILIENCE-02 — Circuit breaker: per-scope failure counting, cooldown and reset
Files: scripts/budget.py, tests/test_budget_controls.py
Rationale: same file and test as U-RESILIENCE-01 but a distinct, failure-driven mechanism — the breaker could be removed while the token/attempt/concurrency ceilings remained fully functional, and vice versa.

| claim | evidence | requirements |
| --- | --- | --- |
| record_failure() opens a persistent per-scope circuit once consecutive failures reach the configured `failure_threshold`, and reserve() refuses every subsequent reservation for that scope, downgrading to `human`, while the breaker stays open | scripts/budget.py:279-301, 352-359 | RQA-FR-038, RQA-NFR-010 |
| breaker_state() reports `half_open` for an open breaker once its `open_until` cooldown has elapsed, and treats an unparseable `open_until` timestamp as expired rather than pinning the breaker open forever | scripts/budget.py:252-260, 270-276 | RQA-FR-038, RQA-NFR-010 |
| record_success() unconditionally closes the breaker for a scope and zeroes its failure count, and reset_breakers() lets an operator clear one named scope or every scope in a single call | scripts/budget.py:304-313, 316-323 | RQA-FR-038 |

### U-RESILIENCE-03 — Provider-diverse fallback recipe ordering
Files: scripts/fallback.py, tests/test_fallback_recipes.py
Rationale: tests/test_fallback_recipes.py is the sole test of fallback.py's tier classification, recipe selection and ordering.

| claim | evidence | requirements |
| --- | --- | --- |
| order_candidates() stable-sorts an already-qualified candidate list into the ladder its recipe declares, preserving each tier's operator-configured relative order, and never adds, removes or re-derives a candidate — only positions change | scripts/fallback.py:89-98 | RQA-FR-023 |
| `preferred` and `diverse` both lead with the paid Claude/Codex subscription tiers before a metered OpenRouter call; `fallback` (used by strategies that run as a second opinion) leads with the diverse/OpenRouter tier instead so a second view does not repeat the first view's subscription route at extra cost; `economical` is cost-led by definition and leads with the economy tier itself, placing the subscription tiers last | scripts/fallback.py:46-60 | RQA-BR-012, RQA-FR-019 |
| an OpenRouter candidate explicitly marked `economy` capability is classified into its own last-resort `economical` tier rather than the ordinary `openrouter` tier, and a candidate with an unrecognised runner sorts to the end of the ladder rather than raising | scripts/fallback.py:38-43, 65-74 | RQA-BR-012 |
| recipe_for() returns the subscription-first `preferred` recipe whenever the caller supplies no strategy name or one unrecognised in `STRATEGY_BY_NAME`, so an absent or unknown strategy configuration still selects a fixed default ordering rather than an ad hoc one | scripts/fallback.py:77-86 | RQA-NFR-009 |

### U-RESILIENCE-04 — Error taxonomy: disposition classification, typed exceptions, and the coarse failure vocabulary the estate acts on
Files: scripts/errors.py, tests/test_fallback.py, tests/test_degradation.py
Rationale: both test files exercise how other estate code (panel.py's fallback loop, dispatcher.py's degrade ladder) consumes the disposition/exception vocabulary this module defines; classifying a failure and giving the rest of the system a typed signal it acts on is one responsibility. The disposition *metadata registry* that used to sit in this unit is a separate responsibility and is now U-RESILIENCE-17: per methodology §4 the third separability test fires — the registry could be removed and everything named here would still be required, because `dispatcher.degrade()` and `panel.py`'s fallback loop consume the typed exception and the coarse constants and never the registry.

| claim | evidence | requirements |
| --- | --- | --- |
| classify_error() maps free-text failure messages to one of three legacy dispositions by ordered token match (job_blocking, then transient, then candidate_terminal), defaulting an empty or unmatched message to candidate_terminal rather than leaving it unclassified | scripts/errors.py:55-71, 79-90 | RQA-BR-009 |
| classify_disposition() runs a fixed, ordered rule list (invalid_config, evidence_incomplete, job_blocking, decision_stale, policy_protected, mutation_uncertain, permission_authority, transient_infrastructure, candidate_terminal) and returns the first matching fine-grained disposition, defaulting unmatched text to candidate_terminal | scripts/errors.py:94-115 | RQA-BR-009 |
| JobBlockingError (disposition job_blocking) is the typed signal dispatcher.degrade() raises to refuse degrading a nonexistent job, a job in an unranked terminal status, or a job with no lower reachable rung, in every case before any state write | scripts/errors.py:156-160, scripts/dispatcher.py:442, scripts/dispatcher.py:444, scripts/dispatcher.py:454 | RQA-NFR-010 |
| panel.py's fallback loop keys its retry/cooldown/fallback behaviour on errors.TRANSIENT, PROVIDER_TERMINAL and CANDIDATE_TERMINAL, each returned from its own branch: a genuine timeout returns TRANSIENT after retrying the same candidate once (scripts/panel.py:385-393), any other exception returns PROVIDER_TERMINAL and retires every candidate of that provider family for the run (scripts/panel.py:394-404), and a verdict that fails validation returns CANDIDATE_TERMINAL (scripts/panel.py:405-413, scripts/panel.py:424); the family cooldown consults TRANSIENT and PROVIDER_TERMINAL only (scripts/panel.py:721). JOB_BLOCKING is not cooled down at all - JobBlockingError is re-raised to the caller before any of those branches is reached (scripts/panel.py:383) | scripts/errors.py:20-30, scripts/panel.py:383, scripts/panel.py:393, scripts/panel.py:404, scripts/panel.py:413, scripts/panel.py:424, scripts/panel.py:721 | RQA-FR-023, RQA-BR-009 |

### U-RESILIENCE-05 — Advisory review comment: content and posting
Files: scripts/advisory.py, tests/test_advisory.py
Rationale: tests/test_advisory.py is the sole test of advisory.py's body rendering and posting gate, one responsibility (producing and delivering the advisory comment).

| claim | evidence | requirements |
| --- | --- | --- |
| build_body() always states the review is advisory and approves nothing and requests no changes, and separates corroborated findings from unconfirmed ones into two headed sections that are never merged; an empty corroborated section states explicitly that no finding met the corroboration bar | scripts/advisory.py:63-69, 71-95 | RQA-BR-005, RQA-BR-008 |
| the body's "How this review was produced" section names the reviewer routes, whether the panel could enforce the requested effort, the achieved versus required assurance, the final disposition and any unmet gates | scripts/advisory.py:97-119 | RQA-BR-014, RQA-FR-012 |
| post_advisory() posts the COMMENT review only when the repository's configured `comment` authority resolves to `live`; any other mode withholds the post and returns that mode as the reason instead of posting anyway | scripts/advisory.py:152-158 | RQA-NFR-017, RQA-NFR-026 |
| post_advisory() never raises: a missing cached PR node id or a mutation exception both produce a posted=False record carrying the reason, so a withheld or failed comment is visible in the job result rather than silently absent | scripts/advisory.py:157-158, 174-184 | RQA-NFR-010 |

### U-RESILIENCE-06 — Durable ledger: append-only recording and revision reconstruction
Files: scripts/ledger.py, tests/test_ledger.py
Rationale: tests/test_ledger.py is the sole test of ledger.py's identity checks, append-only recording and reconstruction, one responsibility (the durable "why" record for a job).

| claim | evidence | requirements |
| --- | --- | --- |
| record() refuses to append an entry whose kind is not one of the eight declared kinds, or that is missing job_id, repo or head_sha, raising LedgerError before any row is written, so a provenance entry can never be accepted without the revision identity that would let it be misattributed | scripts/ledger.py:70-73 | RQA-NFR-028 |
| every ledger entry is append-only: record() only ever INSERTs, there is no update path, so a correction is a new entry rather than an edit of an existing one; revisions() groups entries by head_sha so nothing carries between two reviewed revisions of the same PR | scripts/ledger.py:9-10, 76-83, 106-118 | RQA-NFR-028 |
| explain() reconstructs a job's strategies, routes, evidence, findings (separately listing only those with verified is True), assurance, human events, decisions and the final decision/action from the ledger alone, returning explained=False with a stated reason when no entries exist for the job | scripts/ledger.py:121-163 | RQA-FR-012, RQA-BR-014, RQA-BR-003 |

### U-RESILIENCE-07 — Explain: read-only operator reconstruction of a job's outcome
Files: scripts/explain.py

| claim | evidence | requirements |
| --- | --- | --- |
| `python3 scripts/explain.py --repo-root <repo> pr <number>` is a documented operator procedure at OPERATORS.md section 9, listed in the entry-point index as an operator command distinct from the internal-module disclaimer covering queue.py/lease.py/evidence.py and the rest of OPERATORS.md's second table | scripts/explain.py:28-43, OPERATORS.md:411-419, OPERATORS.md:558 | RQA-FR-012 |
| main() reads only ledger.explain()/ledger.revisions() to answer "why did this PR get this outcome"; its own docstring and imports show it never contacts GitHub, never invokes a model, and never mutates a job | scripts/explain.py:2-6, 19-20, 53-81 | RQA-BR-003, RQA-FR-012 |
| when no ledger entries exist for a `pr <number>` query, main() prints a JSON error naming the repo and PR number and exits 1 rather than fabricating an explanation; `--repo` defaults to the configured repository slug | scripts/explain.py:50, 57-66 | RQA-FR-012 |

### U-RESILIENCE-08 — Structured JSONL job trace and its safe artifact writers
Files: scripts/logging_otel.py, tests/test_logging.py, tests/test_logging_concurrency.py
Rationale: both test files exercise the same JobLogger responsibility from two angles (single-writer event/attempt/diagnostic behaviour and concurrent-writer safety); the mechanism under test is one JobLogger, not two.

| claim | evidence | requirements |
| --- | --- | --- |
| JOB_EVENTS names the 15 canonical event kinds an orchestrator may emit for one job — including `route_selection` (which harness/model route ran), `strategy` (which reasoning strategy/recipe ran) and `decision` (the disposition reached and why) — and REQUIRED_JOB_EVENTS is the 9-name subset that must appear in any job reaching a terminal decision, a single authority a trace consumer checks against rather than a convention left to each caller | scripts/logging_otel.py:54-70, 75-78 | RQA-BR-003 |
| JobLogger._append_event appends one complete JSON object per line to events.jsonl under an advisory fcntl exclusive lock (skipped only when fcntl is unavailable), so two concurrent writers to the same file cannot interleave a partial line | scripts/logging_otel.py:208-219 | RQA-NFR-010 |
| attempt() allocates the next attempt-NNN.json number with O_CREAT and O_EXCL, retrying on FileExistsError so two concurrent callers cannot claim the same number, then writes the file atomically via a temp file plus os.replace so it is never observed partially written | scripts/logging_otel.py:302-318, 380-394 | RQA-NFR-010 |
| metric_attributes() clamps every cost/token/latency value to a non-negative integer bounded by MAX_METRIC_VALUE and omits a value entirely, rather than logging zero, when it was never supplied; cost.tokens and cost.tokens_reserved are the only two token-named keys exempted from the generic sensitive-key redaction so a real token count is not overwritten by "<redacted>" | scripts/logging_otel.py:88-91, 99-128, 257-263 | RQA-FR-021 |

### U-RESILIENCE-09 — Config normalization
Files: scripts/common.py

| claim | evidence | requirements |
| --- | --- | --- |
| normalize_config() always synthesizes a `repos` dict from the repo-local `repository` block when present, and defaults an absent `github` transport block, so a downstream consumer can index config["repos"]/config["github"] without a legacy-shape KeyError regardless of which config shape was loaded | scripts/common.py:60-94 | RQA-NFR-005, RQA-FR-004 |
| load_config()/cli.resolve() re-read and re-normalize the config file on every call rather than caching a compiled form, so an edited config is picked up on the very next invocation with no separate reload step | scripts/common.py:45-57, scripts/cli.py:24-32 | RQA-NFR-005, RQA-FR-004 |

### U-RESILIENCE-10 — GitHub token resolution
Files: scripts/common.py

| claim | evidence | requirements |
| --- | --- | --- |
| github_token() reads GITHUB_TOKEN then GH_TOKEN from the environment, falling back to `gh auth token` only when neither is set, and raises SystemExit rather than proceeding with no credential when every source is empty | scripts/common.py:97-111 | RQA-NFR-006 |

### U-RESILIENCE-11 — Durable SQLite state: persistence-failure typing and the transition guard
Files: scripts/common.py

| claim | evidence | requirements |
| --- | --- | --- |
| State.__init__ opens the database in WAL mode and wraps any sqlite3.Error/OSError raised while opening or migrating it as StatePersistenceError; execute()/_commit() wrap every subsequent sqlite3.Error the same way, so no raw driver exception reaches a caller | scripts/common.py:140-154, 184-199 | RQA-NFR-010 |
| State.transition() refuses a transition on a job that does not exist, raising JobBlockingError before any write; for an existing job it calls states.assert_transition and, on an illegal move, logs an error event (when a logger is supplied) and re-raises without applying the update | scripts/common.py:398-431 | RQA-NFR-010 |
| try_runtime_lock() acquires the state directory's exclusive advisory lock non-blockingly, returning None rather than blocking when another process already holds it, so a scheduled sweep is naturally serialized per state directory; the lock is released automatically by the kernel if the holding process crashes | scripts/common.py:114-121, 156-175 | RQA-NFR-010 |

### U-RESILIENCE-12 — The sole GitHub REST read transport (GithubRest)
Files: scripts/common.py

| claim | evidence | requirements |
| --- | --- | --- |
| GithubRest.get() caches each URL's ETag and body in the etags table, sends If-None-Match on the next call, and reuses the cached body on a 304 response instead of re-fetching or re-parsing it | scripts/common.py:525-546 | RQA-FR-020 |
| pagination follows the response's Link rel="next" header, and when a page is served from cache (a 304), the Link header is re-read from the cached row rather than the in-flight response, so a paginated cursor is not lost across a cache hit | scripts/common.py:552-566 | RQA-FR-020 |
| every REST call, success or failure, is recorded via state.record_api_call(), which persists the rate-limit remaining/reset values read from the response headers, giving budget.reserve()'s rest_remaining floor check an actual queryable rate-limit reading rather than an assumption | scripts/common.py:441-454, 522 | RQA-FR-021 |

### U-RESILIENCE-13 — Stable job and mutation identity
Files: scripts/common.py

| claim | evidence | requirements |
| --- | --- | --- |
| job_id()/mutation_id() derive a stable identifier by SHA-256-hashing their inputs (repo+number+head_sha+lane, or job+operation+discriminator), so the same logical job or mutation always yields the same id and a re-dispatch of the same revision does not mint a new identity | scripts/common.py:471-478 | RQA-FR-005, RQA-BR-007 |

### U-RESILIENCE-14 — Crash-safe durable file write
Files: scripts/common.py

| claim | evidence | requirements |
| --- | --- | --- |
| atomic_write() writes to a temporary file in the target's own directory, flushes and fsyncs it, then renames it into place with os.replace, so a crash mid-write can never leave the destination path holding partial content | scripts/common.py:457-468 | RQA-NFR-010 |

### U-RESILIENCE-15 — Untrusted-content nonce envelope
Files: scripts/common.py

| claim | evidence | requirements |
| --- | --- | --- |
| nonce_envelope() wraps a value between "<<<label:nonce>>>" and "<<<END:label:nonce>>>" delimiters keyed on a per-run nonce, giving evidence assembled from PR content an unambiguous, machine-checkable boundary wherever it is embedded in a reviewer prompt | scripts/common.py:570-572 | RQA-NFR-015 |

### U-RESILIENCE-16 — Unified CLI config-resolution entrypoint helper
Files: scripts/cli.py

| claim | evidence | requirements |
| --- | --- | --- |
| resolve_or_onboarding() prints a machine-readable {"status": "onboarding_required", ...} payload naming the exact onboarding command to run when config resolution fails, and always returns a 2-tuple so a caller must unpack before testing for None (its own docstring warns against testing the tuple itself) | scripts/cli.py:35-66 | RQA-FR-016, RQA-NFR-005 |
| make_state() constructs the shared State object from the resolved config's state_dir, so every CLI entrypoint that calls resolve_or_onboarding then make_state shares one authoritative state directory rather than each computing its own default | scripts/cli.py:69-70 | RQA-NFR-006 |

### U-RESILIENCE-17 — Disposition metadata registry: retryability, authority impact and escalation per disposition
Files: scripts/errors.py

| claim | evidence | requirements |
| --- | --- | --- |
| CATEGORY_META attaches retryability, a named behaviour, an authority_impact (none / no_mutate / escalate / safe_stop) and an escalation flag to every disposition; category_meta() fails safe for an unregistered disposition rather than returning a permissive default, giving it retryable false, behavior safe_stop, authority_impact no_mutate, severity ERROR and escalate true. Not the maximum the vocabulary admits: the named invariant_violation entry carries authority_impact safe_stop and severity CRITICAL, each a step beyond the fallback on the module's own documented ordering none < no_mutate < escalate < safe_stop | scripts/errors.py:207-231, scripts/errors.py:227, scripts/errors.py:244-252 | RQA-NFR-010 |
| Nothing under `scripts/` outside `errors.py` reads this registry, so no product path acts on it. Quoted as the search returned, run from `launchpad/skills/review-queue-automation/`: `grep -rn -e category_meta -e CATEGORY_META -e authority_impact scripts/ --exclude=errors.py` → no output, exit 1. The estate's reachable failure handling keys on the coarse constants instead: panel.py imports TRANSIENT, PROVIDER_TERMINAL, CANDIDATE_TERMINAL and JOB_BLOCKING directly (scripts/panel.py:51-58) and returns them from their own branches (scripts/panel.py:393, scripts/panel.py:404, scripts/panel.py:413, scripts/panel.py:424), re-raising JobBlockingError ahead of all of them (scripts/panel.py:383) | scripts/errors.py:207-231, scripts/panel.py:51-58, scripts/panel.py:383, scripts/panel.py:393, scripts/panel.py:404, scripts/panel.py:413, scripts/panel.py:424 | RQA-NFR-010 |
| The registry's only callers anywhere in the tree are tests, in one module belonging to another cluster: `tests/test_phase4.py`, in three test functions - `test_error_category_metadata`, `test_every_named_category_is_safe` and `test_logging_failure_blocks_authority`. Quoted as the search returned, run from `launchpad/skills/review-queue-automation/`: `grep -rn -e category_meta -e CATEGORY_META -e authority_impact tests/` → 12 lines, every one in tests/test_phase4.py, at :17, :22, :23, :24, :25, :26, :28, :29, :36, :37, :67 and :68. Under methodology §2.3 a behaviour whose only callers are tests is not implemented | scripts/errors.py:244-252, tests/test_phase4.py:22-37, tests/test_phase4.py:65-68 | RQA-NFR-010 |
