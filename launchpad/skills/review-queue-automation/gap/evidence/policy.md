# RQA gap analysis — evidence: policy

Cluster `policy` (18 assessed files, per [`../clusters.md`](../clusters.md)): config load and
validation, policy-as-data, review strategies and execution modes, model routing and the model
registry, route probing, and onboarding. Revision: `9267b6308714454a3b987622d90cda03a8972827`.
Paths below are relative to `launchpad/skills/review-queue-automation/`, per
[`../methodology.md`](../methodology.md).

Confirmed before writing: `git diff 9267b6308714454a3b987622d90cda03a8972827 HEAD -- scripts tests
config.example.json onboarding` is empty in this worktree — every citation below is a citation
against the pinned revision, not a later edit.

This revision responds to review-gate round 1 (sha `7d3f47305`): every requirement ID is re-checked
against the cited requirement's own text, not its topic; several rows found to rest on a real but
requirement-less behaviour were converted to prose (methodology forbids a fabricated ID, and
`gapcheck.py`'s `RQA_RE` rejects a literal `none` in a requirements cell — see this lane's
`.workmux/HANDOFF.md` for the reasoning); three factual errors were corrected against the cited
source lines; two rows that rested on a test citation alone now cite the deciding production line;
and one unit-boundary issue is addressed with reasoning recorded below rather than silently applied.

It also responds to the maintainer's removal of `gapcheck.py`'s mechanical "no test-only citation"
rule: that rule could not tell a claim about product behaviour from a claim about a test suite's
own coverage, and a green run against it was the absence of a check, not a ruling. Applying the
distinction myself — a row citing only test files is legitimate exactly where it is honestly
worded as what the suite asserts and covers, not where it is actually a claim about product
behaviour that needs its own `scripts/`/non-test line — seven rows previously padded with a
duplicate production citation purely to satisfy the old mechanical rule are reworded below to
their honest coverage-claim form (test-only citation, no padding), since each duplicates a
product-behaviour claim already established with its own citation elsewhere in the same unit. That
pass also surfaced one genuine gap: a `validate_config` check (risk-band continuity) had no
standalone product-behaviour claim of its own, only a padded test-only summary row; it now has one.

Round 2 (this revision): the false substring-search assertions in the earlier audit are corrected
against the actual requirement text — RQA-NFR-018's fit criterion names "a tracked file" at
requirements-specification.md:1240, RQA-BR-013's fit criterion is the sole notification-family text
at :659, and RQA-NFR-020's fit criterion contains "concurrently" at :756. The onboarding
runtime-readiness gate and the model-registry shadow-lock/re-qualification gate are each split into
their own unit (U-POLICY-07 and U-POLICY-12) per the maintainer's mandatory-split ruling, each with
a residual requirement-mapping question raised against it (escalations R2-runtime-readiness and
R2-shadowlock); unit IDs renumber sequentially U-POLICY-01..14. Five deciding-line
citations were moved to the deciding line, one mis-mapped requirement ID corrected, and two
clause/range attributions fixed. Both of those escalations are now resolved in place, under the
maintainer's ruling that there are no nearest-fit mappings: each was tested candidate by candidate
against the requirement text and none covered, so U-POLICY-07 and U-POLICY-12 carry `-` in every
requirements cell. See each unit's own note for the test and the reproducible searches.


---

### U-POLICY-01 — Repo-local config discovery and version-control isolation

Files: scripts/config.py, tests/test_config_onboarding.py, tests/test_onboarding.py

Rationale: `config.py`'s path/ignore/tracking helpers and the two test files that exercise them
are one responsibility — the authoritative runtime config lives at exactly one repo-relative
location and must never enter version control — separable from schema validation (U-POLICY-02)
because it could be rewritten (a different storage location, a different VCS) without touching a
single validation rule, and vice versa.

| claim | evidence | requirements |
| --- | --- | --- |
| The authoritative per-repo config has exactly one path, `<repo>/.review-queue-automation/config.json`, computed by `repo_config_path`, and no other path is treated as authoritative — the config is read from that live filesystem path at each call, never compiled into an artifact. | scripts/config.py:27-28, scripts/config.py:60-61, scripts/config.py:446-455 | RQA-NFR-005 |
| `load_repo_config` reads and JSON-parses that file directly at call time (no build/compile step) and returns `None` plus a human-readable issue list on missing file, invalid JSON, or an unreadable file, rather than raising. | scripts/config.py:446-455 | RQA-NFR-005 |
| `tests/test_config_onboarding.py:56-58` (`test_authoritative_config_path_is_repo_local`) asserts and covers that the repo-local config path equals `repo_config_path`'s own computation — a claim about the test suite's coverage of the canonical-path claim above, not a separate product-behaviour claim. | tests/test_config_onboarding.py:56-58 | RQA-NFR-005 |

Note (prose — the fail-closed VCS and secret-hygiene behaviours; the search claim corrected in
round 2): the earlier draft asserted a search of `requirements-specification.md` for "tracked"
returns nothing; that is false. RQA-NFR-018's fit criterion names "a tracked file" as one
representation of the policy input whose corruption or truncation must never widen authority
(requirements-specification.md:1240), and rejecting a git-tracked config at load is the
fail-closed half of exactly that ("never applied, so never widened"). The behaviour is therefore
consistent with NFR-018 rather than foreign to it; it is recorded as prose because the primary
reason a config must stay untracked is repository hygiene (keep secrets and logs out of version
control), which no requirement's text mandates per se. Concretely, `load_repo_config` additionally
fails closed
(appends an issue, forcing `config = None`) when the config file or its directory is git-tracked,
or when the config directory or the resolved logging directory is not git-ignored
(scripts/config.py:458-467), and `is_ignored`/`is_tracked` both return `False` outright — rather
than raising or assuming an answer — when the target is not inside a git working tree
(scripts/config.py:71-88). `tests/test_onboarding.py:91-106` (`test_onboarding_refuses_tracked_config`)
exercises this directly. Separately, `config.py`'s docstring states "No secrets/tokens in the
config; auth stays in environment/keychain" (scripts/config.py:10), and `validate_config` backs
this with a recursive secret-key scan (`find_secret_keys`, `SECRET_KEY_HINTS`, scripts/config.py:343,
scripts/config.py:409-423) that rejects a config containing any
`token`/`api_key`/`password`/`secret`/`private_key`/`client_secret`-shaped key outside a small
numeric allowlist (`SECRET_KEY_ALLOWLIST`, scripts/config.py:345-354;
`tests/test_config_onboarding.py:208-215` exercises it). Both are real, load-bearing, fail-closed
behaviours; the secret-key scan has no counterpart in the 86 frozen requirements — RQA-NFR-024,
RQA-NFR-025 and RQA-NFR-030 govern the scope of the GitHub credential the system holds, not what an operator's
local JSON file may contain or whether it is version-controlled. These are defense-in-depth
measures beyond the frozen specification, not gaps against it.

---

### U-POLICY-02 — Fail-closed schema and semantic validation of the runtime config

Files: scripts/config.py, tests/test_config_onboarding.py

Rationale: n/a (single production file; the test file is corroborating).

| claim | evidence | requirements |
| --- | --- | --- |
| `validate_config` returns a deterministic list of issues (empty == valid) and never partially applies a config: on missing required top-level keys it returns immediately with only that issue, short-circuiting every other check — so no section, including `authority`, can partially apply while another is silently skipped. | scripts/config.py:114-119 | RQA-NFR-018 |
| The `authority` section and the inline `policy` section are each validated by their owning module — `authority.validate_authority` for `authority`, `policy.validate_policy` for `policy` — and folded into the same fail-closed issue list, so a malformed authority or policy value makes the whole config unusable rather than silently dropping just that section. | scripts/config.py:207-219 | RQA-NFR-018 |
| `approval.mode` defaults to `"disabled"` when absent and is rejected outright unless it is one of the four known modes (`disabled`, `shadow`, `human_escalation`, `live`); `live` additionally requires `approval.live_canary_approved` to be `true` and a non-empty `risk.protected_triggers`, so a config cannot reach the live-approval mode by omission. | scripts/config.py:242-246, scripts/config.py:292-293 | RQA-NFR-026, RQA-NFR-018 |
| Every `risk.protected_triggers` entry must be a string and a valid regex (`re.compile`); an invalid pattern is recorded as an issue rather than raised or silently skipped, so a typo'd trigger can never silently narrow the set of paths `live` mode treats as protected. | scripts/config.py:278-291 | RQA-NFR-018 |
| `risk.bands` must be present with `low`, `medium` and `high` keys, each an integer, and pass `risk.validate_bands`' continuity check; a missing, non-integer, or discontinuous band map is recorded as an issue rather than loaded, so the blocking threshold two reviewers must apply consistently is never left undefined or discontinuous by a malformed config. | scripts/config.py:255-273 | RQA-BR-004 |
| `tests/test_config_onboarding.py:218-241` asserts and covers three of `validate_config`'s fail-closed paths established above: `test_live_approval_is_fail_closed` (a `live` approval mode without canary approval is rejected), `test_risk_band_continuity_fails_closed` (a discontinuous risk-band map is rejected), and `test_bad_protected_trigger_fails_closed` (an invalid regex trigger is rejected). | tests/test_config_onboarding.py:218-241 | RQA-NFR-018, RQA-BR-004 |

Note (prose — re-checked against the requirement text, not the topic, per review-gate round 1;
none of these three checks bears on any of the 86 requirements): `validate_config` also delegates
to `budget.validate_budget` unconditionally (scripts/config.py:225-227) and validates a present
`notifications` section's transport/fields (scripts/config.py:316-338) — both real, fail-closed
checks, but neither is about authority widening (RQA-NFR-018's actual population) or about
anything else in the frozen set. (Corrected in round 2 — the earlier draft's search attributions were wrong:
the sole notification-family text is RQA-BR-013's fit criterion, "No condition genuinely requiring no human
judgement ever raises a notification demanding a human's immediate attention"
(requirements-specification.md:659), which concerns human-interruption escalation for routine conditions,
unrelated to this operator notification-transport section; and RQA-NFR-020's fit criterion contains
"concurrently" — "whether a contributor was concurrently or 'actively' using that tree"
(requirements-specification.md:756) — which concerns remediation isolation, unrelated to a config
concurrency ceiling. A search for "budget" still returns nothing.) Separately,
`dispatch.incoming_concurrency` and `dispatch.author_concurrency_per_repo` must each equal exactly
`1` (scripts/config.py:192-196, "a state directory has one worker"), a real invariant with no
counterpart requirement either. All three are recorded here rather than mapped to a
proximate-but-inapplicable ID.

---

### U-POLICY-03 — The tracked example config stays runtime-shippable

Files: config.example.json, tests/test_config_onboarding.py

Rationale: n/a (one non-code artifact; the test file is the only code that reads it for this
purpose).

| claim | evidence | requirements |
| --- | --- | --- |
| `config.example.json` is a fully-populated template — including the `policy`, `budget` and `retention` sections `onboarding_defaults` also writes — copyable as an operator's starting config without a rebuild or redeploy step. | config.example.json:1-242 | RQA-NFR-005 |
| A regression test asserts the example produces a pinned snapshot (a non-blank `policy_version` and content hash) by calling `snapshot.build_snapshot(_example(), validate_policy=policy.validate_policy)` — i.e. the same production `build_snapshot` entrypoint `dispatcher.resolve_snapshot` uses, with this cluster's own `policy.validate_policy` injected as its validator — guarding against the exact prior drift where the example lacked a `policy` section and every job ran unpinned. | config.example.json:194-241, tests/test_config_onboarding.py:260-268, scripts/dispatcher.py:1591 | RQA-FR-004 |
| A second test asserts every top-level section `onboarding_defaults` writes is also present in the example, so a newly added default section cannot silently drift out of the copyable template again. | scripts/config.py:471-527, config.example.json:1-242, tests/test_config_onboarding.py:271-280 | RQA-FR-004 |

Note (prose): `config.example.json` declares a `strategies.active` allowlist
(`config.example.json:166-172`) naming four strategy names. No script under `scripts/` reads
`config["strategies"]` or `config.get("strategies")` at all (confirmed by a repo-wide search of
`scripts/` and `tests/` for that key) — `select_strategy` (U-POLICY-08 below) accepts an optional
`candidates` restriction, but every call site (`strategies.strategy_for_profile`,
`scripts/dispatcher.py:1119-1121`) invokes it with no `candidates`, so all twelve registered
strategies remain selectable regardless of this config section. This is a genuine dead config key,
not a documentation claim about behaviour that runs — the code is the evidence, and it shows the
key has no effect. It bears on no requirement's text directly (no RQA item mandates a
per-repository strategy allowlist), so it is recorded here rather than in a claim row.

---

### U-POLICY-04 — Policy-as-data validation, versioning and content-hash pinning

Files: scripts/policy.py, tests/test_policy_reload.py

Rationale: n/a (single production file; the test file is corroborating for this cluster's own
code only — see the note below on what it is not cited for).

| claim | evidence | requirements |
| --- | --- | --- |
| `validate_policy` is a deterministic, non-raising schema/semantic check (empty list == valid) over a policy object carried as data — authority, risk bands, approval thresholds, human-queue expiry — independent of any build artifact. | scripts/policy.py:61-110 | RQA-NFR-005, RQA-FR-004 |
| `canonicalize` refuses (raises `PolicyValidationError` via the `validate_or_raise` it calls at scripts/policy.py:129-132) rather than partially accepting a malformed policy, and the exception's own docstring records that on rejection "existing policy stands" — a bad edit cannot take effect even partially. | scripts/policy.py:129-132, scripts/policy.py:113-116, scripts/policy.py:38 | RQA-NFR-018 |
| Every validated policy is pinned by both a monotonic-looking version string (`policy_version`, defaulting to `"unversioned"` when absent) and a stable SHA-256 content hash over the canonical (sort-keyed) JSON, so a later reader can name exactly which policy produced a given decision. | scripts/policy.py:41-44, scripts/policy.py:119-132 | RQA-FR-012 |

Note (prose — review-gate round 1, F01/F02): `policy.py`'s own module docstring states it "owns
policy VALIDATION and versioning only" and that the durable runtime store is
`snapshot.SnapshotStore`, "which activates config and policy together as one content-hashed
snapshot" (scripts/policy.py:8-12). The actual reload/pinning behaviour —
`dispatcher.resolve_snapshot` reloading a job's pinned snapshot by hash, or building a new one via
`snapshot.build_snapshot` when none is pinned yet (scripts/dispatcher.py:1535-1605) — is decided in
`dispatcher.py` and `snapshot.py`, both `dispatch`-cluster files. `tests/test_policy_reload.py`
exercises that dispatch-cluster behaviour end to end (a valid edit applies to new jobs only, an
in-flight job keeps its pinned policy, a malformed edit retains the last-known-good snapshot) and
is kept in this cluster's `Files:` only because `../clusters.md` assigns the test file here and it
does incidentally exercise `policy.validate_policy`/`canonicalize` as the classifier
`build_snapshot` calls into (scripts/dispatcher.py:1572, scripts/dispatcher.py:1591) — no claim
above rests on it, and no claim about the reload/pinning behaviour itself is made in this file:
that behaviour is the dispatch cluster's to evidence in its own units, against `dispatcher.py` and
`snapshot.py`, which this cluster's `Files:` may not include.

---

### U-POLICY-05 — Policy derived from config, never invented

Files: scripts/config.py

Rationale: n/a (single file, single function).

| claim | evidence | requirements |
| --- | --- | --- |
| `policy_defaults` copies the `approval`, `risk`, `authority`, `human_queue` and `assurance` sections directly from the source config it is given (`dict(config.get("authority") or {})`, `dict(config.get("human_queue") or {})`, `dict(config.get("assurance") or {})`, and the `risk.bands`/`risk.protected_triggers` sub-keys) — it does not compute any of these from a wider or more permissive source, so deriving a policy from a config can never widen that config's own authority or thresholds. It is not a verbatim copy of the whole input, though: the returned `"version"` is always the fixed literal `"v1"`, not copied from the source config's own version, and each `approval` key absent from the source is filled from a fixed structural fallback (`required_approval`) rather than copied. | scripts/config.py:377-406 | RQA-NFR-018 |
| Every one of those structural fallbacks is the *same* safe default `onboarding_defaults` already writes for `approval` (e.g. `mode` falling back to `"disabled"`, `effective_risk_max` to `24`) — not a new, more permissive threshold introduced only when a key happens to be absent. | scripts/config.py:384-392, scripts/config.py:499-507 | RQA-NFR-026, RQA-NFR-018 |

---

### U-POLICY-06 — Onboarding: a valid, never-overwritten starter config

Files: scripts/config.py, scripts/onboarding.py, onboarding/SKILL.md, tests/test_config_onboarding.py, tests/test_onboarding.py

Rationale: `onboarding_defaults` (config.py) and `init_onboard`/`update_config`/`main`
(onboarding.py) are one responsibility end to end — first-run setup and safe update that never
overwrites an existing config and never touches GitHub, models, or a lease — documented as a
single operator procedure in `onboarding/SKILL.md` and exercised by both test files. The
runtime-readiness gate is split into its own unit, U-POLICY-07, per the maintainer's ruling that a
fired methodology §4 separability test is a mandatory split trigger: the gate could be removed or
reworked while this unit's write/backup/no-overwrite flow stayed.

| claim | evidence | requirements |
| --- | --- | --- |
| `onboarding/SKILL.md` instructs an operator to run `python3 .../onboarding.py init <repo-root> --slug OWNER/REPO --base launchpad` as the documented first step for a new repository, on the operator's own machine — this is an E3/E4 citation, not an inventory listing (it is also indexed at `OPERATORS.md:552` against runbook §1). | onboarding/SKILL.md:16-20 | RQA-NFR-006 |
| `onboarding_defaults` returns a config with every section `validate_config` requires already populated with safe values — all six `authority` activities `"disabled"`, `approval.mode` `"disabled"`, empty `models.primary`/`models.secondary` — but the bare defaults are not themselves schema-valid: `repository.slug` is deliberately left `""` pending the operator's own value, and `validate_config` requires every `REPOSITORY_KEYS` entry, including `slug`, to be truthy. `onboarding_defaults(root)` alone therefore fails `validate_config`; it becomes schema-valid only once `init_onboard`/`update_config` inject the operator-supplied `--slug` (and any other caller-provided fields). | scripts/config.py:471-479, scripts/config.py:45, scripts/config.py:124-127, scripts/onboarding.py:107 | RQA-NFR-026 |
| `update_config` refuses if no config exists yet (directing the operator to `init`), takes an atomic backup (`_backup`) before writing, and restores that backup (`_restore`) on every downstream failure — a root mismatch, an unwritable log directory, or `validate_config` rejecting the written result — so a corrupted or truncated config input — RQA-NFR-018's fit criterion names "a tracked file" as one such representation, sourced from CL-056 (requirements-specification.md:1240) — is never left live. | scripts/onboarding.py:146-187 | RQA-NFR-018 |
| Neither `init_onboard` nor `update_config` calls GitHub, a model, or claims a lease — the whole module confines itself to local filesystem, `git` plumbing (via `config.py`'s `is_git_repo`/`is_ignored`/`is_tracked`), and JSON I/O, matching the single-contributor, no-hosted-service workflow this module exists to set up. | scripts/onboarding.py:2-6 | RQA-NFR-006 |
| `tests/test_config_onboarding.py:135-151` (`test_update_restores_corrupted_config`) and `:153-169` (`test_update_restores_on_secret_key`) assert and cover `update_config`'s rollback claim above against two distinct failure causes; the same file's `test_update_refuses_root_mismatch` (`:172-181`) and `test_update_from_other_repo_has_no_config` (`:184-190`) assert and cover its two refusal paths; `tests/test_onboarding.py:122-129` (`test_onboarding_invokes_no_forbidden_tools`, alongside `test_no_subprocess_gh_during_onboarding` in the same file) asserts and covers the no-external-calls claim above. | tests/test_config_onboarding.py:135-169, tests/test_config_onboarding.py:172-190, tests/test_onboarding.py:122-129 | RQA-NFR-018, RQA-NFR-006 |

Note (prose — re-checked against requirement text; neither of these two behaviours has a
frozen counterpart): (1) `init_onboard` refuses outright — writes nothing — when a config already
exists, when the target is not a directory, when it is not a git work tree, or when `--slug` is
empty (scripts/onboarding.py:94-104; corroborated by `tests/test_config_onboarding.py:99-107`,
`test_init_refuses_existing_config`); no RQA item addresses refusing to overwrite an existing
local file. (2) Unlike `update_config`, `init_onboard` writes the config *before* validating it:
`_atomic_write` runs at scripts/onboarding.py:120, and `validate_config`/`_check_runtime_ready` run
only afterward at :122-123; on an invalid result `init_onboard` returns an error at :124-125 with
no call to restore or delete the file it just wrote (contrast `update_config`'s `_restore` calls at
:157, :162, :177 and :186) — so an invalid config generated by `init` can be left on disk even
though the CLI correctly reports the run as failed. This is a real, narrow finding (bounded in
practice by `load_repo_config` re-validating on every subsequent load, scripts/config.py:457), but
no RQA item is about leaving a stray invalid artifact on disk after a reported CLI failure. (The onboarding runtime-readiness gate — `_check_runtime_ready` and its surfacing — is split
into its own unit, U-POLICY-07, per the maintainer's mandatory-split ruling.)

---

### U-POLICY-07 — Onboarding runtime-readiness gate

Files: scripts/onboarding.py, scripts/config.py, tests/test_config_onboarding.py, tests/test_onboarding.py

Rationale: split from U-POLICY-06 per the maintainer's ruling that a fired §4 separability test is
a mandatory split trigger: `_check_runtime_ready` and its surfacing could be removed or reworked
while the write/backup/no-overwrite flow stayed. The gate's own obligation — a repository is not
treated as "runtime-ready" until nonempty login, nonempty `repository.slug` and at least one
configured model-pool candidate are present — has no counterpart among the 86 frozen requirements,
so every row below carries `-` in its requirements cell. This replaces an earlier RQA-FR-031
mapping recorded as "the nearest but not a settled fit", and it discharges escalation
R2-runtime-readiness under the maintainer's ruling that there are no nearest-fit mappings: a
requirement is cited when its own text covers the obligation the claim describes, and where none
does, the cell is `-` and says so. The test that produced `-` is recorded in the note below.

| claim | evidence | requirements |
| --- | --- | --- |
| `_check_runtime_ready` reports a config not ready when `login` is empty, when `repository.slug` is empty, or when both `models.primary`/`models.secondary` are empty — i.e. a repository is only treated as a reviewable instance once a reviewer route is present in its own local config. No frozen requirement obliges this precondition; see the note below. | scripts/onboarding.py:76-87 | - |
| Both `init_onboard` and `update_config` call `_check_runtime_ready` on the config they just wrote and surface `runtime_ready`/`readiness_issues` in their returned summary, so a caller does not have to separately query readiness. No frozen requirement obliges a readiness state to be computed or surfaced; see the note below. | scripts/onboarding.py:122-136, scripts/onboarding.py:188-196 | - |
| `tests/test_config_onboarding.py:79-88` (`test_init_with_usable_pools_is_runtime_ready`) and `:192-205` (`test_runtime_ready_requires_nonempty_login_and_pools`) assert and cover both paths: a config with a usable model pool reports `runtime_ready is True`, and one with an empty login/no pools reports the missing-pool problem. These corroborate a behaviour no frozen requirement obliges; see the note below. | tests/test_config_onboarding.py:79-88, tests/test_config_onboarding.py:192-205 | - |

Note (prose — requirement mapping, resolving escalation R2-runtime-readiness). Each candidate was
tested text-exactly against the obligation the rows describe: *a repository is not runtime-ready
until nonempty `login`, nonempty `repository.slug` and at least one configured model-pool candidate
are present, and that state is surfaced to the caller.*

- **RQA-FR-031** — "One operator running locally shall be able to review pull requests across at
  least two independently configured repositories under different GitHub owners or organisations,
  with no centrally hosted service." Its fit criterion is that one operator completes a review on
  each of two repositories under two different owners with no central service. **Does not cover.**
  FR-031 obliges a *capability* (multi-repository, multi-owner, local operation); it says nothing
  about a precondition on configuration, about which fields must be nonempty, or about a readiness
  state being computed or reported. An implementation with no readiness gate whatever satisfies
  FR-031's fit criterion in full. Per-repository configuration independence is adjacent subject
  matter, not the obligation the claims describe, and the previous mapping was recorded in this
  file as "the nearest but not a settled fit" — which is the defect, stated honestly.
- **RQA-NFR-004** — "The system shall operate across multiple repositories and multiple
  organisations, including both public and private repositories under different owners."
  **Does not cover**, for the same reason as FR-031: a capability obligation, silent on
  configuration preconditions.
- **RQA-NFR-006** — "One contributor shall be able to run the complete review workflow locally,
  with no central hosting, tenancy or SaaS functionality required." **Does not cover**: it obliges
  local end-to-end operability, not a gate that classifies a config as ready or not ready.
- **RQA-FR-032** — "The active external provider path shall be identifiable before evidence is
  sent to it." **Does not cover**: its trigger is an evidence send and its obligation is
  identifiability of the path then; `_check_runtime_ready` runs at config-write time, obliges
  nonemptiness of `login` and `repository.slug` (neither of which is a provider path), and is not
  on the send path at all.

The absence is reproducible, not asserted. Run from
`launchpad/skills/review-queue-automation/`:

    $ grep -nEi '\b(ready|readiness)\b' requirements/requirements-specification.md
    $ echo "exit=$?"
    exit=1

    $ grep -nEi 'onboard|bootstrap|precondition' requirements/requirements-specification.md
    $ echo "exit=$?"
    exit=1

    $ grep -nEi 'slug|login|model pool|model-pool' requirements/requirements-specification.md
    $ echo "exit=$?"
    exit=1

All three return no matching lines (grep exit status 1 = no match). A substring search
`grep -nEi 'ready|readiness' requirements/requirements-specification.md` does return lines
136, 263, 840, 873, 1231, 1233 and 1240, but every one of those is the substring inside "already"
("already in this set", "already granted", …); no requirement in the frozen set uses readiness as
a concept. The 86 statements were additionally read in full (`grep -c '^### RQA-'
requirements/requirements-specification.md` → `86`) and the four candidates above are the only
ones whose subject matter comes near this gate.

**What `-` means for wave 3.** `-` is not a neutral outcome and must not be read as one. It is the
finding that **no requirement in the frozen specification obliges this behaviour** — this is a
claim about the specification's text, not about the diligence of the search. The runtime-readiness
gate is therefore a candidate for `bin` in the wave-3 disposition, and the disposition lane must
reason from that rather than inherit a stretched FR-031 mapping that would have made the unit look
required. That is exactly why a nearest-fit mapping is worse than none: it launders an unrequired
behaviour into a requirement-serving one. (Whether the gate is nonetheless worth keeping on
engineering grounds is a disposition judgement for wave 3, not a requirement mapping.)

---

### U-POLICY-08 — Named reasoning strategies and deterministic, signal-driven selection

Files: scripts/strategies.py, tests/test_strategy_metadata.py

Rationale: n/a (single production file; the test file is corroborating).

| claim | evidence | requirements |
| --- | --- | --- |
| `select_strategy` chooses one strategy deterministically and in a fixed specificity order — `specialist_need`, then `prior_disagreement`, then `required_independence == "panel"`, then `"challenger"`, then `risk == "high"`, then `complexity >= 3`, defaulting to `direct_analysis`/`checklist` — from the review's own signals, never from an ad hoc or random choice, and returns the selection reason alongside the strategy; this is the mechanism that keeps a review from reaching for a higher-cost method (e.g. `specialist_panel`, `debate`) the signals do not call for. | scripts/strategies.py:137-181 | RQA-FR-019, RQA-BR-012 |
| `signals_for_profile`/`strategy_for_profile` is the one shared selector both the pre-spend budget reservation (`dispatcher._reserve_budget`) and the executing panel (`panel._selection_context`) call, so the same job can never have its budget reserved against one strategy and executed under a different one. | scripts/strategies.py:109-134, scripts/dispatcher.py:1119-1121, scripts/panel.py:435-439 | RQA-FR-019 |

Note (prose — re-checked against requirement text): at import time, an assertion rejects any
registry row whose `aggregation` is outside `VALID_AGGREGATIONS` (scripts/strategies.py:95-98) —
real, load-bearing, but it is a data-integrity guard (a strategy cannot declare an aggregation no
execution mode knows how to run) rather than anything about capacity efficiency or reviewer-pass
bounds; no RQA item is about registry-metadata integrity, so it is not mapped to RQA-BR-012 here.
Separately, a test asserts every declared `Strategy` field is read by a runtime module other than
`strategies.py` itself (`modes.py` for `aggregation`, `panel.py` for
`roles`/`output_schema`/`disagreement_handling`, `budget.py` for `budget_tokens`, `fallback.py` for
`model_route`) via a source-text grep (`tests/test_strategy_metadata.py:37-63`). Per methodology
§2.3, this is corroborating evidence that the fields are consumed today, not proof of an enforced
invariant: the check is test-only, so a newly added dead field would ship without any
production-code failure — nothing under `scripts/` re-runs this check at import time or at
dispatch, and no RQA item is about strategy-metadata dead-field detection either.

---

### U-POLICY-09 — Execution-mode semantics: whether a panel happened

Files: scripts/modes.py, tests/test_modes.py

Rationale: n/a (single production file; the test file is corroborating).

| claim | evidence | requirements |
| --- | --- | --- |
| `aggregate` discounts a participant that timed out, produced no schema-valid verdict, or duplicates a provider family already counted, before any counting occurs — such a participant contributes nothing toward the mode's required count, and the specific reason is recorded per participant. | scripts/modes.py:185-211 | RQA-BR-002, RQA-FR-002 |
| A mode declaring a required `verifier_role` (`generator_verifier`, `executor_verifier`, `debate_adjudicate`) is `HUMAN` (or `DEGRADED` for `debate_adjudicate`, whose spec sets `on_missing_verifier="degraded"`) whenever no counted participant filled that role — an unverified generation is never treated as a pass. | scripts/modes.py:99-115, scripts/modes.py:224-232 | RQA-FR-002 |
| `for_profile` derives the execution mode from the assurance profile's own `independence`/`required` values (`single` when `independence == "single"` or `required <= 1`, else `independent_review` sized to `max(2, required)`) rather than from the strategy's own aggregation — so the mode actually executed can never demand more independent participants than the profile itself calls for. | scripts/modes.py:155-179 | RQA-FR-019 |
| `mode_for` resolves an unknown or absent strategy name to `single` rather than raising, and `spec_for` raises `ModeError` only for a genuinely unknown mode string — the mapping is total over every registered strategy, so the execution-mode concept always means the same thing regardless of which strategy (and, transitively, which harness/model) selected it. | scripts/modes.py:136-152 | RQA-FR-002 |
| `tests/test_modes.py:54-135` asserts and covers the participation/agreement-discounting claim above across each discount reason and the unanimity boundary: a same-family second participant is discounted (`test_second_participant_from_the_same_family_is_not_agreement`), an invalid or timed-out participant is discounted with the specific reason (`test_invalid_verdict_is_not_agreement`, `test_timed_out_participant_is_not_agreement`, `test_timeout_is_reported_as_timeout_even_though_it_is_also_invalid`), and disagreement is a HUMAN escalation only for unanimity-requiring modes (`test_modes_that_require_unanimity_do_escalate_on_disagreement`) while non-unanimous modes still count a disagreeing panel as having happened (`test_disagreement_does_not_break_participation_for_the_executed_mode`). | tests/test_modes.py:54-135 | RQA-BR-002, RQA-FR-002 |

---

### U-POLICY-10 — Subscription-first model routing with an explicit, non-inventive fallback ladder

Files: scripts/routing.py, tests/test_route_config.py

Rationale: n/a (single production file; the test file is corroborating).

| claim | evidence | requirements |
| --- | --- | --- |
| `_routes_from_config` derives the four ladder rungs (`claude`, `codex`, `openrouter`, `economical`) solely from `models.primary`/`models.secondary` — the same pools `panel.py` executes — grouped by each entry's own `runner`/`capability`, unless an operator has pinned an explicit per-rung list (`models.claude`, etc.), which then wins outright. Nothing is invented outside the configured pools. | scripts/routing.py:66-98 | RQA-NFR-009 |
| `resolve_route` walks the fixed rung order `claude, codex, openrouter, economical, human`, honouring an optional `provider_hint` by trying that rung first, and returns the first available, not-yet-attempted candidate; reaching the `human` rung sets `final = "human"` and returns without selecting any model — an explicit "no automatic candidate left" outcome, never a silently substituted one. | scripts/routing.py:116-186 | RQA-NFR-009, RQA-FR-024, RQA-FR-038 |
| A candidate already recorded in `run.attempted` is skipped (the fallback-loop guard), and `is_route_available` additionally skips a candidate under an active cooldown recorded in state — so the same unavailable route is never retried within one resolution, and an unavailable configured route is passed over in favour of the next configured rung rather than stalling. | scripts/routing.py:101-113, scripts/routing.py:151-155 | RQA-FR-023 |
| Every selected candidate is passed through `model_registry.qualified_route` before being recorded, so a `ResolvedRoute` always carries the fully qualified provider/model identity, not just the raw config entry. | scripts/routing.py:156-181 | RQA-FR-032 |
| `tests/test_route_config.py:53-96` and `:99-159` assert and cover the ladder-resolution claims above against the shipped example and canonical pools: the example config resolves to a real model rather than an empty ladder (`test_example_config_resolves_to_a_real_model`, a regression guard against a prior bug where 6 configured models still resolved to `"human"`), an explicit pinned ladder overrides derivation (`test_explicit_rungs_still_win_when_present`), cooldowns advance to the next rung and, when every rung is cooled, escalate to `human` (`test_cooldown_advances_to_the_next_rung`, `test_both_subscriptions_cooled_falls_to_openrouter`, `test_all_unavailable_escalates_to_human`), and an unknown runner is never routed (`test_unknown_runner_is_not_routed`). | tests/test_route_config.py:53-96, tests/test_route_config.py:99-159 | RQA-NFR-009, RQA-FR-023, RQA-FR-024, RQA-FR-038 |

---

### U-POLICY-11 — Model alias registry and qualified-route identity

Files: scripts/model_registry.py, tests/test_model_registry.py

Rationale: `ALIASES`/`resolve`/`qualified_route` (naming and identifying a route) are one
responsibility — naming and identifying an executable reviewer route. Separable from the
changed-route shadow-lock/re-qualification gate (methodology §4: `qualified_route` would still be
required without the gate), which is therefore split into its own unit, U-POLICY-12, per the
maintainer's ruling that a fired §4 separability test is a mandatory split trigger.

| claim | evidence | requirements |
| --- | --- | --- |
| `ALIASES` is a closed, hand-maintained map of six named aliases (e.g. `CLAUDE_FAST`, `CODEX_STRONG`) to an exact `runner`/`selector`/`provider_family` triple; `resolve` raises `ValueError` on an unsupported alias rather than guessing a "latest" route — there is no implicit alias resolution. | scripts/model_registry.py:27-51 | RQA-FR-032 |
| `qualified_route` builds the complete execution identity of a route — runner, provider, model, model_version, effort, execution_mode, tools, prompt_version, policy_version — and raises `ValueError` if `selector`, `runner` or `provider` end up empty, then fingerprints the whole identity with a sorted-key SHA-256 hash; it is the identity `routing.resolve_route` attaches to a resolved candidate (scripts/routing.py:156-181); no evidence-sending timing claim is made here, because in the active panel path the candidate is executed first and `qualified_route` is called only afterward to record the route that actually ran (scripts/panel.py:668, scripts/panel.py:688-698). No frozen requirement obliges the building of that identity record once the before-send timing claim is withheld; see the note below. | scripts/model_registry.py:54-82 | - |
| `runtime_route_material`/`route_material_fingerprint` reduce the configured pools to only the model/prompt/tool inputs that can change a review result (excluding, e.g., cost/concurrency settings), and hash that reduced material — a config edit outside that material cannot register as a route change. No frozen requirement obliges change-detection scoping; see the note below. | scripts/model_registry.py:85-104 | - |
| `tests/test_model_registry.py:58-73` asserts and covers the alias/identity claims above: historical shorthand normalizes to the canonical alias (`test_registry_resolves_normalized_native_alias`), and a qualified route carries every execution-identity input plus a 64-character fingerprint (`test_qualified_route_contains_all_execution_identity_inputs`). The RQA-FR-032 mapping here is carried by the first test, which corroborates the mapped row 1; the second corroborates row 2, whose cell is now `-`. | tests/test_model_registry.py:58-73 | RQA-FR-032 |

Note (prose — requirement mapping, RQA-FR-032 re-tested row by row under the maintainer's
no-nearest-fit ruling, per review gate P2-policymap round 1 item 3). RQA-FR-032 reads: "The active
external provider path shall be identifiable before evidence is sent to it", with the fit
criterion "Before any evidence leaves the system for an external provider, the specific provider
path it will use can be named." Its whole obligation is that timing-bounded nameability.

- **Row 1 (`ALIASES`/`resolve`) — covers; mapping kept.** A closed, hand-maintained table mapping
  each alias to an exact `runner`/`selector`/`provider_family` triple, with `resolve` raising
  rather than guessing a "latest" route, is precisely what makes "the specific provider path it
  will use can be named" true. The table is a static constant, so the naming is available at any
  point, including before any evidence leaves the system; the timing bound is satisfied a
  fortiori. Trigger, subject and direction all match the requirement's own text.
- **Row 2 (`qualified_route`) — does not cover; cell is now `-`.** FR-032's obligation is
  *entirely* a timing one, and this row explicitly withholds any before-send timing claim: in the
  active panel path the candidate is executed first and `qualified_route` is called only afterward
  to record the route that actually ran. A post-hoc identity record is not "identifiable before
  evidence is sent to it". The row's own disclaimer therefore defeats the mapping rather than
  qualifying it. (The before-send half of FR-032 is genuinely evidenced — by U-POLICY-10's fourth
  row, where `resolve_route` attaches the qualified identity to a candidate at *selection* time,
  before that candidate is executed. That mapping stands and is untouched.)
- **Row 3 (`runtime_route_material`/`route_material_fingerprint`) — does not cover; cell is now
  `-`.** The obligation this row describes is which inputs are admitted to a change-detection
  hash, so that a non-material config edit does not register as a route change. Its consumer is
  the shadow-lock gate in U-POLICY-12. FR-032 obliges nothing about detecting a change, about
  which config edits count as material, or about hashing; naming the active provider path and
  scoping a change fingerprint are different obligations that happen to share the word "route".
  This is the same nearest-fit defect the ruling names, one row further on.
- **Row 4 (tests) — covers; mapping kept**, on the strength of
  `test_registry_resolves_normalized_native_alias`, which corroborates row 1.
  `test_qualified_route_contains_all_execution_identity_inputs` corroborates row 2 and carries no
  mapping now; the row records that division rather than letting one mapped test launder the
  other.

No other frozen requirement covers rows 2 or 3. Run from
`launchpad/skills/review-queue-automation/`:

    $ grep -nEi 'fingerprint|hash|checksum' requirements/requirements-specification.md
    $ echo "exit=$?"
    exit=1

    $ grep -nEi 'route|routing' requirements/requirements-specification.md
    $ echo "exit=$?"
    exit=1

    $ grep -nEi 'alias' requirements/requirements-specification.md
    $ echo "exit=$?"
    exit=1

All three printed no output (grep exit status 1 = no match). RQA-FR-012 (one command reconstructs
the exact revision, protocol, reviewer identity, harness, model, provider and decision basis of an
authoritative outcome) was tested against row 2 and does not cover it: FR-012 obliges
*reconstruction of a completed outcome by a single command*, not the construction of an identity
record, and nothing in `qualified_route` is that command. RQA-FR-020 ("A valid existing result
shall be reused rather than regenerated"), RQA-BR-007 and RQA-FR-005 were tested against row 3 and
do not cover it: all three are about reuse across an unchanged *revision or push*, not about which
*configuration* edits are admitted to a route-change fingerprint.

**What `-` means for wave 3.** As in U-POLICY-07 and U-POLICY-12, `-` is not a neutral outcome:
it is the finding that **no requirement in the frozen specification obliges these two behaviours**
— a claim about the specification's text, not about the diligence of the search. `qualified_route`
as an identity-record builder, and route-material fingerprint scoping, are therefore `bin`
candidates for the wave-3 disposition on their own account, and the disposition lane must weigh
them as such rather than inherit a stretched FR-032 mapping that made them look required. This
does **not** put the whole unit in question: rows 1 and 4 remain mapped to FR-032, so
`ALIASES`/`resolve` is requirement-serving and only these two behaviours are unserved.

---

### U-POLICY-12 — Changed route material is locked to shadow until re-qualified

Files: scripts/model_registry.py, scripts/route_probe.py, tests/test_model_registry.py

Rationale: split from U-POLICY-11 per the maintainer's ruling that a fired §4 separability test
is a mandatory split trigger — this gate could be removed or reworked while alias/identity-building
(U-POLICY-11) stayed, and vice versa. As established in review-gate round 1 and re-confirmed by both
round-2 seats, the gate's deciding production evidence is scripts/model_registry.py:107-138 and
:141-153 and scripts/route_probe.py:196-202. The gate's own obligation — a CHANGED configured
route must be re-verified by a probe before it becomes authoritative again, else the job's
approval and authority are forced down to `shadow` — has no counterpart among the 86 frozen
requirements, so every row below carries `-` in its requirements cell. This replaces earlier
RQA-NFR-009 and RQA-NFR-018 mappings that this file itself recorded as not "text-exact for the
gate's core obligation", and it discharges escalation R2-shadowlock under the maintainer's ruling
that there are no nearest-fit mappings. The candidate-by-candidate test and the reproducible
searches are in the note below.

| claim | evidence | requirements |
| --- | --- | --- |
| `observe_runtime_routes` computes the current route-material fingerprint and, on the first observation for a `scope`, records it with status `"observed"`; on a later call with an unchanged fingerprint it returns the stored status unchanged; on a changed fingerprint it unconditionally overwrites the row to status `"shadow_locked"`. `mark_runtime_qualified` is the only function that can move a scope's status to `"qualified"`, and it is called only from `route_probe.py`, only after every probed route for that scope returned `OK`. No frozen requirement obliges a configured route to be re-verified after its material changes; see the note below. | scripts/model_registry.py:107-138, scripts/model_registry.py:141-153, scripts/route_probe.py:196-202 | - |
| When `observe_runtime_routes` returns a scope as `shadow_locked`, `dispatcher.resolve_snapshot` forces that job's `approval.mode` to `"shadow"` and its `authority.approve` to `"shadow"` (scripts/dispatcher.py:1579-1590) — a changed route cannot silently retain its prior approval authority without re-qualification. No frozen requirement obliges that narrowing; see the note below. | scripts/model_registry.py:133-138, scripts/dispatcher.py:1579-1590 | - |
| `tests/test_model_registry.py:94-137` asserts and covers both the lock and the release: a changed route forces a new job to shadow (`test_changed_route_material_forces_new_job_to_shadow`) and a probe run persists provider health and qualifies the current routes (`test_probe_persists_provider_health_and_qualifies_current_routes`). These corroborate a behaviour no frozen requirement obliges; see the note below. | tests/test_model_registry.py:94-137 | - |

Note (prose — requirement mapping, resolving escalation R2-shadowlock). Each candidate was tested
text-exactly against the obligation the rows describe: *when a configured route's material changes,
that route stops being authoritative until a probe re-qualifies it, and any job resolved meanwhile
has its approval mode and approve authority forced to `shadow`.*

- **RQA-NFR-009** — "An alternative model or provider shall be used only when explicitly
  configured." Its fit criterion is: "With no alternative model or provider configured, none is
  substituted; one only activates once configuration names it." **Does not cover.** NFR-009's
  obligation is a prohibition on *unconfigured substitution*. This gate's subject is a route that
  *is* explicitly configured, whose material the operator changed, and its obligation is
  *re-verification before restoring authority* — a different act with a different trigger. An
  implementation that never observed a fingerprint, never shadow-locked and never probed would
  still satisfy NFR-009's fit criterion in full, provided it substituted only configured routes.
  Configuration presence is adjacent subject matter, not coverage.
- **RQA-NFR-018** — "A malformed or unreadable policy shall never widen authority beyond what was
  already granted." Its fit criterion exercises deliberately corrupted, truncated or unreadable
  policy input and confirms no activity gains authorisation it did not already have.
  **Does not cover**, on both the trigger and the direction. Trigger: the gate fires on a
  well-formed, readable, deliberate configuration edit — a changed route-material fingerprint is
  not a malformed or unreadable policy, and nothing in `observe_runtime_routes` reads or parses a
  policy. Direction: NFR-018 forbids *widening*; this gate *narrows*, from whatever authority the
  scope previously held down to `shadow`. The specific thing the gate prevents — a changed route
  silently **retaining** its prior authority — is retention, not widening, and NFR-018's text
  permits it. The earlier row asserted this was "the fail-closed direction RQA-NFR-018 requires";
  NFR-018 requires non-widening, and a system that let a changed route keep its existing approval
  authority would violate nothing in NFR-018's text.
- **RQA-FR-032** — "The active external provider path shall be identifiable before evidence is
  sent to it." **Does not cover**: it obliges identifiability of the path at send time, which is
  U-POLICY-11's `qualified_route` and is mapped there. It obliges nothing about re-verifying a
  changed route or about withholding authority until a probe passes.
- **RQA-NFR-010** — "A failure during review shall never leave an ambiguous, corrupted or
  partially authoritative outcome." **Does not cover**: its trigger is a failure *during a review
  run*. A route-material change between runs is not a failure during review, and the gate acts at
  job-resolution time, before any review work occurs.
- **RQA-FR-004 / RQA-NFR-005** — a policy or configuration change takes effect on the next review
  with no rebuild, reinstall or redeploy. **Do not cover**: they oblige propagation without a
  rebuild step, and say nothing about re-qualifying the changed configuration before it is trusted.

The absence is reproducible, not asserted. Re-run from
`launchpad/skills/review-queue-automation/` (this replaces the earlier unquoted assertion that
such a search "returns no match anywhere in the frozen set"):

    $ grep -nEi 'shadow|qualif' requirements/requirements-specification.md
    $ echo "exit=$?"
    exit=1

    $ grep -nEi 're-verif|reverif|re-probe|probe|re-qualif|attest' requirements/requirements-specification.md
    $ echo "exit=$?"
    exit=1

Both return no matching lines at all (grep exit status 1 = no match); neither printed any output,
which is why no result lines appear above. The 86 statements were additionally read in full
(`grep -c '^### RQA-' requirements/requirements-specification.md` → `86`) and the five candidates
above are the only ones whose subject matter comes near this gate.

**What `-` means for wave 3.** `-` is not a neutral outcome and must not be read as one. It is the
finding that **no requirement in the frozen specification obliges this behaviour** — a claim about
the specification's text, not about the diligence of the search. The shadow-lock gate is therefore
a candidate for `bin` in the wave-3 disposition, and the disposition lane must reason from that
rather than inherit stretched NFR-009/NFR-018 mappings that would have made the unit look required.
That is the whole reason a nearest-fit mapping is worse than none. Note for whoever evaluates the
register: striking the NFR-018 mapping means this unit is no longer evidence for RQA-NFR-018, and
any register row citing U-POLICY-12 against NFR-018 must be re-derived from its remaining evidence.

---

### U-POLICY-13 — Route probing against the real transport

Files: scripts/route_probe.py, tests/test_model_registry.py

Rationale: n/a (single production file; the corroborating test is the shared model-registry
suite, since probing and qualification are tested together there — the qualification half of that
suite is cited by U-POLICY-12 instead).


| claim | evidence | requirements |
| --- | --- | --- |
| `persist_probe_result` records a failed probe as a timed provider cooldown (`unavailable_until`, derived from `models.cooldown_seconds`) rather than an immediate hard failure, and a passing probe clears any cooldown — this is the same `providers` table `routing.is_route_available` reads at scripts/routing.py:151-155 to decide that an unavailable configured rung is passed over in favour of the next one (U-POLICY-10). | scripts/route_probe.py:113-135, scripts/routing.py:151-155 | RQA-FR-023 |

Note (prose — round 2, R2-008): `probe_route` invokes one candidate through the same
`runners.build_invocation` adapter the panel's `_run_reviewer` uses (scripts/panel.py:304-312),
classifies the outcome, and validates the resulting stdout against `verdict.validate_verdict`
(scripts/route_probe.py:59-110) — so a route is reported usable only once it produces a schema-valid
verdict through the real transport. An earlier revision mapped this to RQA-FR-030 (a harness not
built into the system participates by satisfying the published interaction contract alone, with no
change to the system's own source); that does not hold: route_probe is a built-in, operator-invoked
probe of the repo's own configured pools, and FR-030's admission-without-source-change obligation
for a non-built-in harness is not evidenced here, so FR-030 is not mapped in this file.

Also re-checked against requirement text: `OPERATORS.md` documents
`route_probe.py --repo-root <repo> --json` and `route_probe.py --runner claude --selector sonnet
--effort medium` as commands an operator runs, distinct from the disclaimed internal-modules table
— a genuine E3/E4 citation (also indexed against runbook §4 at `OPERATORS.md:553`), establishing
that `route_probe.py` is reachable and not merely test-invoked (OPERATORS.md:151-153); this fact is
methodological (it is what makes every other claim in this unit admissible under §2.1(b)), not
itself a behavioural claim about non-built-in harness participation, so it carries no ID of its
own. Separately, the module's own docstring states it is read-only with respect to GitHub and the
repository — never claims a lease, never writes PR state, and runs the same read-only adapter the
panel uses (scripts/route_probe.py:4-11) — real, but RQA-NFR-020 is specifically about
*remediation* isolation (auto-fix pushes), and route probing performs no remediation at all, so
that ID does not apply here and no other item addresses a routine read-only operation in general.
Finally, `main` refuses to probe when no route is configured at all (`models.primary` and
`models.secondary` both empty), reporting `"no_routes_configured"` rather than a false pass, and
exits non-zero unless every probed route was usable (scripts/route_probe.py:174-182, :225) — a
real fail-closed CLI behaviour with no counterpart in the frozen set (this is a single-repository
configuration-completeness check, not a demonstration of multi-repository/multi-organisation
operation).

---

### U-POLICY-14 — Distinct-family candidate eligibility across model pools

Files: tests/test_panel_policy.py

Rationale: n/a (this unit exists to cover a test file `../clusters.md` assigns to `policy` whose
own subject, `scripts/panel.py`, is `verdict`-cluster code; the claims below are about the
policy-cluster config contract the test's fixtures exercise, cited to the policy-cluster code that
defines that contract plus the `panel.py` production lines that actually decide the behaviour, with
`panel.py` cited only as out-of-cluster corroboration, never as the sole citation).

| claim | evidence | requirements |
| --- | --- | --- |
| `validate_config` also requires every pool entry to declare a non-empty `provider_family` (scripts/config.py:168); `panel.py`'s candidate loop tracks `used_families` and skips a pool whose `provider_family` is already in that set (scripts/panel.py:656-661), adding the chosen family to it only on a successful invocation (scripts/panel.py:708-710) — the same distinct-family exclusion `modes.py` re-derives at aggregation time from trusted sidecar metadata (U-POLICY-09). The test suite exercises that a second candidate from an already-used family is never counted a second time within one lane (`test_duplicate_family_used_only_once`) and that a lane's second slot is filled from a distinct family across the primary/secondary pools (`test_slot_uses_distinct_family_across_lanes`). | scripts/config.py:168, scripts/panel.py:656-661, scripts/panel.py:708-710, tests/test_panel_policy.py:189-213 | RQA-BR-002, RQA-FR-002 |

Note (round 2, R2-010): `validate_config` also requires every pool entry to declare a
non-empty `capability` and a non-empty `efforts` list (scripts/config.py:168-173), and `panel.py`'s
`_qualifying` uses exactly those two to decide whether a candidate is invoked at all — rejecting a
pool below the profile's required capability rank and one whose declared `efforts` excludes the
requested effort (scripts/panel.py:546-557) — exercised by `test_candidate_below_required_capability_not_invoked`
and `test_candidate_without_required_effort_not_invoked` (tests/test_panel_policy.py:159-185). An
earlier revision mapped this to RQA-NFR-009 (an alternative model/provider shall be used only when
explicitly configured); that does not hold — this gate decides eligibility *among already-configured*
candidates for a profile, not whether an alternative is substituted without configuration — so
RQA-NFR-009 is restricted to U-POLICY-10's configured-pool rows and this capability/effort gate,
bearing on no requirement, is recorded here rather than in a claim row.

Note (prose): every other assertion in `tests/test_panel_policy.py` — malformed/missing-field/
contradictory/prose verdicts falling through to the next candidate, partial-panel handling, stale
verdict clearing, and retry-once-on-a-genuine-timeout — exercises `panel.run_panel`'s own
selection/retry logic (`scripts/panel.py`, `verdict` cluster) through a fake `_run_reviewer`, not a
policy-cluster behaviour; no further claim is drawn from those assertions here.

---

---

## Coverage check

Every file `../clusters.md` assigns to `policy` (18) appears in at least one unit's `Files:` line
above: `config.example.json` (U-POLICY-03), `onboarding/SKILL.md` (U-POLICY-06),
`scripts/config.py` (U-POLICY-01, 02, 05, 06, 07), `scripts/model_registry.py` (U-POLICY-11, 12),
`scripts/modes.py` (U-POLICY-09), `scripts/onboarding.py` (U-POLICY-06, 07),
`scripts/policy.py` (U-POLICY-04), `scripts/route_probe.py` (U-POLICY-12, 13),
`scripts/routing.py` (U-POLICY-10), `scripts/strategies.py` (U-POLICY-08),
`tests/test_config_onboarding.py` (U-POLICY-01, 02, 03, 06, 07),
`tests/test_model_registry.py` (U-POLICY-11, 12), `tests/test_modes.py` (U-POLICY-09),
`tests/test_onboarding.py` (U-POLICY-01, 06, 07), `tests/test_panel_policy.py` (U-POLICY-14),
`tests/test_policy_reload.py` (U-POLICY-04), `tests/test_route_config.py` (U-POLICY-10),
`tests/test_strategy_metadata.py` (U-POLICY-08).
