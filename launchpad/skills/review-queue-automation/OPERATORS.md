# Operator guide — review-queue-automation

Everything an operator needs to run `rqa`, read its output, and act on an
escalation, without reading the implementation.

Every command, exit code and config key named below was read out of the code
in this worktree — `rqa/cli/main.py`, `rqa/cli/exitcodes.py`,
`rqa/policy/validate.py` and `rqa/policy/schema.py` — not carried over from an
earlier document. See [SKILL.md](SKILL.md) for the command reference itself;
this document is the field-by-field config reference, the disposition and
escalation vocabularies, the four ratified architecture decisions, and the
open caveats an operator needs before trusting any of it.

Contents:

1. [Onboarding](#1-onboarding)
2. [Config reference](#2-config-reference)
3. [The six dispositions (RQA-FR-016)](#3-the-six-dispositions-rqa-fr-016)
4. [The five escalation causes (RQA-FR-026)](#4-the-five-escalation-causes-rqa-fr-026)
5. [Deciding an escalation](#5-deciding-an-escalation)
6. [The four ratified architecture decisions](#6-the-four-ratified-architecture-decisions)
7. [Two requirements this delivery does not implement as code](#7-two-requirements-this-delivery-does-not-implement-as-code)
8. [Authority and credential evidence](#8-authority-and-credential-evidence)
9. [What logging and tracing currently do](#9-what-logging-and-tracing-currently-do)
10. [Platform](#10-platform)
11. [Tests](#11-tests)

`<repo>` below is the repository being reviewed, named as `owner/repo` to
`rqa status`/`rqa explain` and as a filesystem path to `rqa onboard`.

---

## 1. Onboarding

```bash
python3 -m rqa.cli onboard <repo-path>
python3 -m rqa.cli onboard <repo-path> --migrate
```

Writes `<repo-path>/.rqa/config.json` — the starter document
`rqa.policy.validate.starter_config()` builds, with every `authority` entry
`false`, every `routes` entry absent, `external.allowed` `false`, an empty
`policy.obligations`, and every `budget` axis unset (`null`, meaning no
configured ceiling). Plain `onboard` refuses (`already_exists`, exit 1) if the
file is already there. `--migrate` instead reads an existing old-shape config
at that path, drops the notification-transport and retention-window keys,
discards `authority.triage` with no replacement (the lane it gated is not
carried forward at all, by any name), and carries `authority.review`'s
Boolean value through unchanged under the same key and `authority.fix`'s
Boolean value through unchanged under the renamed key `authority.remediate`
— an old config's `authority.review: true` survives migration as `true`, it
is not reset. It also zeroes every `authority` entry the old shape never
named at all (`comment`/`approve`/`request_changes`/`merge`), and refuses
(`no_config_to_migrate` / `unreadable_existing` / `migrated_config_invalid`, exit 1) if there is
nothing to migrate or the result itself fails validation.

The path must already be an existing local directory. Onboarding checks the
keychain before writing and makes no GitHub call and mutates nothing outside the one file it
writes.

---

## 2. Config reference

`<repo>/.rqa/config.json` is checked by `rqa.policy.validate.validate()`
against exactly five top-level groups (`rqa/policy/schema.py`'s
`TOP_LEVEL_KEYS`); every one is required, and any sixth top-level key is
rejected. `config.example.json` at the skill root tracks an example of this
exact shape — it is an example of the per-repo `.rqa/config.json`, **not** of
any older top-level `~/.config/...` file; no such file is validated by this
code.

Validation is fail-closed and collected: every error is gathered and reported
together, never one per run.

| Group | Keys | Notes |
|---|---|---|
| `authority` | `review`, `comment`, `approve`, `request_changes`, `remediate`, `merge` (each `true`/`false`) | Derived from the closed `Activity` enum, so this key set cannot drift from what the authority gate names. Every omitted key defaults `false` — nothing is granted by omission. Every grant also requires credential evidence and membership in the configured repository set — see §8. |
| `routes` | array of `{harness, model, provider, family, external, command?}` | `harness`, `model`, `provider`, `family` are required non-empty strings; `external` is required Boolean. `command` is **optional** — the operator-declared argv for a harness `rqa` ships no built-in alias for; its absence means a built-in alias is used. |
| `external` | `allowed` (bool), `deny_label` (string) | Whether an external (non-subscription) route may be used, and the label recorded when one is denied. |
| `policy` | `version?` (default `"unversioned"`), `obligations` (array), `blocking` (`{categories, severities, corroboration}`), `mechanical` (`{categories, tools}`), `assurance` (object), `remediation?` (`{allow_forks}`, default `allow_forks: false`) | `obligations`, `blocking`, `mechanical` and `assurance` are required — an absent one would *widen* what a review has to satisfy, not narrow it. `categories` values are drawn from the closed `Category` enum: `mechanical`, `procedural`, `creation_time`. |
| `budget` | `per_pr_tokens`, `per_repo_daily_tokens`, `per_model_daily_tokens` (each an integer or `null`) | `null` means no configured ceiling on that axis; all three are checked in order by `rqa/supply/budget.py`, and an axis with no configured bound is never checked. |

No secret belongs in this file; nothing in `rqa.policy.validate` inspects it
for one, so this is an operator discipline, not an enforced check — do not
read the absence of a rejection here as a guarantee.

---

## 3. The six dispositions (RQA-FR-016)

`requirements/requirements-specification.md`, RQA-FR-016, verbatim:

> For any managed pull request, one command shall return its current disposition from {being reviewed, blocked, awaiting remediation, awaiting human judgement, review-complete, unable to progress} and the reason, without a human reconciling historical reviews, comments or checks.

That command is `rqa status <repo> <number>`. The six values are
`rqa/lifecycle/states.py`'s `Disposition` enum, and they match the frozen
wording exactly — no divergence between the specification's vocabulary and
the implemented one was found.

| Disposition | What it means | What an operator does |
|---|---|---|
| `being reviewed` | The job is queued, claimed, planned, reviewing, judged, or submitting — in flight, no verdict yet. | Nothing; re-run `rqa status` later if curious. |
| `blocked` | A CHANGES_REQUESTED verdict is recorded; the PR needs author changes. | Read the posted review on GitHub; no `rqa` action needed until the author pushes a new revision, which starts a new job. |
| `awaiting remediation` | A mechanical remedy (ADR-0064) is being applied to named files. | Nothing; re-run `rqa status` later. If it stays here unexpectedly long, use `rqa explain <repo> <number>` to see the record. |
| `awaiting human judgement` | An escalation is open against this job. | Run `rqa pending` to find it, investigate its cause and question, then `rqa decide` it (§5). |
| `review-complete` | An authoritative APPROVED verdict exists, or the PR merged. | Nothing further; the review reached its terminal success. |
| `unable to progress` | The job stopped without a verdict — RQA-FR-038's safe non-success stop. | Use `rqa explain <repo> <number>` to see why, then fix the named cause (policy, credential, or repository state) outside `rqa`. |

---

## 4. The five escalation causes (RQA-FR-026)

`requirements/requirements-specification.md`, RQA-FR-026, verbatim:

> A required escalation shall name the specific unresolved decision, conflicting judgement, evidence gap, required information or authority requirement that produced it.

The five causes are `rqa/contracts.py`'s `EscalationCause` enum
(`unresolved_decision`, `conflicting_judgement`, `evidence_gap`,
`required_information`, `authority_requirement`) — the same five, named as
the underscored form of the frozen prose rather than a sixth vocabulary.

**What the code actually guarantees about the question, and what it does
not (#2260):** `rqa/escalation/escalate.py`'s `raise_()` rejects a cause
outside these five, and rejects a blank or all-whitespace `question` string.
**Nothing checks that the question names its cause *concretely*** — the
`question` is not otherwise validated for specificity. Treat every
escalation's question as a non-blank string naming one of the five causes,
and read its actual content before acting; do not assume the wording is
guaranteed to be actionable just because the escalation exists.

| Cause | What it means | What an operator does |
|---|---|---|
| `unresolved_decision` | A decision the review needs a human to make exists and has not been made. | Read the question, make the decision, run `rqa decide` with `--actor`/`--basis` (no `--outcome`). |
| `conflicting_judgement` | Two reviewers (or two runs) disagreed. | Read both sides in the question/context, decide which stands, `rqa decide` with your basis. |
| `evidence_gap` | A required piece of evidence is missing. | Supply or locate the missing evidence, then `rqa decide` recording it as the basis. |
| `required_information` | The review needs information only a human has (e.g. an obligation's `required_for` target). | Supply the information out of band, then `rqa decide` recording it as the basis. |
| `authority_requirement` | The job's obligations are satisfied but the repository has granted neither `approve` nor `request_changes` (ADR-0061). | Post the actual GitHub review yourself (APPROVE or CHANGES_REQUESTED), then `rqa decide <id> --actor <you> --basis <why> --outcome {approved,changes_requested}`. `rqa/lifecycle/resume.py`'s step 12b then admits that outcome only if it can find **exactly one** submitted GitHub review matching your `--actor`, that same `--outcome`, and the job's exact head, submitted at or after the escalation was raised — a mismatched actor, a different outcome, a stale head, or no matching review at all is refused rather than recorded on trust. This is the **only** cause `--outcome` may accompany; supplying it against any other cause is rejected before any of this runs. |

---

## 5. Deciding an escalation

```bash
python3 -m rqa.cli pending
python3 -m rqa.cli decide <escalation_id> --actor <you> --basis "<why>" [--outcome {approved,changes_requested}]
```

`decide` refuses (exit 1) an unknown id, an already-closed escalation, a job
whose head has moved since the escalation was raised, or a job whose policy
snapshot has moved — each of the last two means the escalation's own premise
is stale, and re-running `rqa tick` will raise a fresh one against the
current head if the condition still holds. A successful decision is recorded
in the tamper-evident record (§6.3, ADR-0063) and resumes the job's
lifecycle; supplying an input a raised escalation names never restarts the
review from the beginning.

---

## 6. The four ratified architecture decisions

All four are `status: Accepted` under `launchpad/decisions/`. What each one
means for what `rqa` does, in the present tense:

**ADR-0061 — a satisfied review without verdict authority escalates; it
never completes.** When a job's obligations are satisfied but the repository
has granted neither `approve` nor `request_changes`, `rqa` posts its
rendering as a comment (if `comment` is granted) and raises an
`authority_requirement` escalation rather than fabricating a verdict. The job
sits at `awaiting human judgement` until a human records the outcome through
`rqa decide --outcome`. `review-complete` therefore always means an
authoritative verdict exists — never a plausible-looking stand-in.

**ADR-0062 — the credential's floor is proven, its ceiling is an accepted
residual.** `rqa` uses the operator's own `gh auth token`. An activity is
granted only when the pinned policy snapshot allows it **and** a per-job
capability probe supplies exercised or scope-qualified attested evidence for it on that exact
repository; a failed probe yields no grant and an `authority_requirement`
escalation rather than an attempted mutation. `rqa` never addresses a
repository outside its configured set and never persists the credential.
What the token could do on an unmanaged repository is a known, accepted, and
unclosed residual (RQA-NFR-030) — not something `rqa` can narrow.

**ADR-0063 — the record is a hash chain plus an operator-held HMAC.** Every
record entry is chained and, when the operator's OS keychain holds the HMAC
secret, additionally authenticated; `rqa` never writes or rotates that
secret itself. A missing key degrades an append to explicitly unkeyed —
`rqa explain` then reports that span `unverifiable: no key`, never as a
break and never as a stopped review. Neither the hash chain nor the HMAC
detects truncation of the record's tail; both detect edits and reordering of
the rows that remain.

**ADR-0064 — the only remedy `rqa` applies and pushes itself is a closed-set
tool run on exact named files, never a model-supplied patch.** A remedy names
one registered tool, the exact changed files it runs against (never a
pattern), and is refused unless the tool's own check passes, the diff scope
is exactly those files, the fix is a fixpoint, and a parser-derived semantic
fingerprint is unchanged before and after. Import-fixing is excluded by
design. No model-authored diff ever reaches a branch through `rqa`.

---

## 7. Two requirements this delivery does not implement as code

**RQA-FR-034** — *"Every architectural component retained in the delivered
design shall be justified as materially serving a criterion, as having no
materially simpler sufficient approach, or as required by a constraint."*
This is discharged by the **merged #2071 architecture document**
(`architecture/`), which records that justification per component. It is not
a runtime check `rqa` performs, and no command surfaces it.

**RQA-FR-035** — *"Exactly one authoritative review-agent scope shall remain
open, achieved by closing or explicitly re-parenting #109 and reconciling its
features #535 and #536 against this scope."* This is **#2068's** issue-admin
action (closing/re-parenting GitHub issues), not code in this repository.
Neither requirement is implemented as `rqa` behaviour, and neither retirement
happens as part of this document or this Task.

---

## 8. Authority and credential evidence

The CLI supplies the repository set from `tick --repo` or
`<state-dir>/repos.json` to the authority gate. Decisions use `repos.json`;
keep that durable set current when a scheduled sweep or resumed job needs it.
An unconfigured repository is denied before credential probing. Each activity
also requires its own Boolean policy flag and the required capabilities.

GitHub-attested writes satisfy the gate only when both repository permissions
and authenticated OAuth scopes support them (`repo`, or `public_repo` for an
explicitly public repository). Missing scope headers and ambiguous permissions
deny. The record keeps exercised and attested capabilities separate. The probe
performs no test writes and grants never bypass branch protection. Upgrading
invalidates unscoped capability-cache evidence and probes again.

---

## 9. Job milestone traces

Each lifecycle admission appends validated orchestration milestones to
`<state-dir>/jobs/<job-id>/trace.jsonl`. Every line is one JSON object. The
closed fifteen-name vocabulary and its nine required events live in
`rqa.record.trace`; an unknown event is refused before a trace file is created.
The completed-review lifecycle test proves that all required milestones are
emitted.

The trace is diagnostic and non-authoritative. `rqa explain` reconstructs from
the hash-chained SQLite record and never reads this file. Concurrent writers use
an exclusive per-job lock; each update is flushed, synced, and atomically
renamed. Inspect a trace with standard JSON Lines tools, for example:

```bash
jq . <state-dir>/jobs/<job-id>/trace.jsonl
```

Route metadata is bounded to four executed routes per event. Emitted fields are
counts, identifiers, fixed outcomes, and route metadata; PR bodies, file
contents, credentials, environment values, and model output are absent.

---

## 10. Platform

Supported backends are macOS Keychain (`security`) and Linux Secret Service
(`secret-tool`, with a running user Secret Service session). The operator-held
item is identified by service `rqa-record-hmac`; RQA reads it and never creates
or rotates it. Linux lookup failure is checked with a metadata search so a
locked matching item cannot be mistaken for an absent item.

A missing tool, unavailable session, locked matching item or timeout stops
`onboard`, `tick` and `decide` before work. An absent key permits explicitly
unkeyed records; `explain` marks them unverifiable. `status` and `pending` need
no key, and `explain` reports integrity using the same backend as the writer.
A typo in `--state-dir` on a read or decision command is an input error and
creates no database.

---

## 11. Tests

```bash
python3 launchpad/skills/review-queue-automation/tests/run_all.py \
        launchpad/skills/review-queue-automation
python3 launchpad/skills/review-queue-automation/architecture/validate.py
python3 launchpad/skills/review-queue-automation/tests/test_cutover_map.py
```

The first is a no-pytest-dependency runner and is also collected as-is by the
acceptance venv's real `pytest -q` from the skill root. The second and third
are independent structural checks, not part of the behavioural suite.
