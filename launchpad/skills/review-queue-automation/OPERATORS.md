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
8. [Authority is not wired to a grant](#8-authority-is-not-wired-to-a-grant)
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

Onboarding makes no GitHub call and mutates nothing outside the one file it
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
| `authority` | `review`, `comment`, `approve`, `request_changes`, `remediate`, `merge` (each `true`/`false`) | Derived from the closed `Activity` enum, so this key set cannot drift from what the authority gate names. Every omitted key defaults `false` — nothing is granted by omission. **Configuring `true` here does not currently cause an activity to run — see §8.** |
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

## 4a. Anchoring a job's record

```
rqa anchor <job-id>
```

Publishes that job's current chain head and records it locally, so a later
`rqa explain` can tell you whether entries are **missing**, not just whether
the ones present are intact. Run it on a timer, at the end of a job, or by
hand — it is idempotent, so running it twice on an unchanged record does
nothing.

It always exits 0 when it ran. An anchor that could not be published is a
reported state, not an error:

| `detail` says | What happened | What it still gives you |
|---|---|---|
| (nothing) | Published | Full detection, including against a deleted local anchor |
| `not published: …` | No comment authority for that repository | The local anchor — a crash-truncated log is still detected offline |
| a failure message | GitHub was unreachable | Same; the anchor stays pending and the next run retries it |

**Anchoring can never fail a review.** That is deliberate: a review that
stopped because an audit-trail nicety could not reach the network would be a
worse outcome than an unanchored record.

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
capability probe proves the credential can perform it on that exact
repository; a failed probe yields no grant and an `authority_requirement`
escalation rather than an attempted mutation. `rqa` never addresses a
repository outside its configured set and never persists the credential.
What the token could do on an unmanaged repository is a known, accepted, and
unclosed residual (RQA-NFR-030) — not something `rqa` can narrow.

**ADR-0066 — the record is a hash chain, and there is no key to keep.** Every
record entry is chained to the one before it, so an edit, a reordering, an
interrupted write, or an accidental corruption is detected. **You hold no
secret and there is nothing to lose or rotate.** ADR-0066 superseded ADR-0063,
which additionally authenticated each entry with an operator-held HMAC key
from the OS keychain: that key had to be readable by `rqa` on every append, so
anything running as you could read it too, and it cost a separate credential
integration per platform.

On its own the chain does **not** detect two things: an actor who rewrites a
row *and* recomputes every hash after it, and a removed tail — a record with
its last entries deleted is shorter but internally consistent, and verifies
clean. **Anchoring closes both**, up to the last anchor.

**What anchoring is.** RQA periodically publishes the record's current head —
a job id, a sequence and a hash, never any content — somewhere the reviewed
agent cannot rewrite it, and keeps a local copy. `verify` then compares the
two. If entries the anchor proves existed are gone, you get `tail_removed`
rather than a clean pass; if the chain was rebuilt, `anchor_mismatch`.

**The bound, which matters when you read a report.** Anchoring is periodic,
so the guarantee is "complete as at the last anchor", never "complete as at
the final entry". Entries appended after the most recent anchor are
unattested, and truncation inside that window is undetectable. Anchor more
often to narrow the window; there is no setting that closes it.

**What works with no network.** The local anchor copy is written before the
publish is attempted, so a crashed agent's truncated log is detected offline
— which is the common case. An actor who deleted the local anchors *as well*
is only caught by comparing against the published copy. A publish that fails
never blocks a review: the anchor is recorded as pending and retried.

**Authority.** Publishing to a pull request needs comment authority for that
repository. An advisory-only repository publishes nothing rather than
widening what RQA may do — you get an unanchored record, honestly reported,
not a silent escalation of privilege.

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

## 8. Authority is not wired to a grant

**Configuring `authority.*` does not currently cause `rqa` to act.**
`rqa/authority/gate.py`'s `_configured_repositories()` is a hardcoded empty
`frozenset()`, and `rqa/cli/composition.py`'s `AuthorityClient` has no
parameter to supply a managed-repository set. The result: in production,
every activity on every repository is denied (`REPO_NOT_MANAGED`), regardless
of what `authority.*` says. This is tracked as **#2274**, a
`deferred-blocker` against this Feature (#2188 cannot close until it lands).
Do not configure `authority.*` expecting an activity to run, and do not treat
its presence in `config.example.json` as evidence that granting works — it
is one of the five groups `rqa.policy.validate` accepts, nothing more.

---

## 9. What logging and tracing currently do

`rqa/record/trace.py` defines `append_trace`, which can append one row to
`jobs/<job>/trace.jsonl`. **Nothing in `rqa/` calls it** — it has zero callers
outside its own module and is absent from `rqa/record/__init__.py`'s
`__all__`. There is no otel-jsonl milestone trace, no event vocabulary, and no
per-job trace file an operator can currently rely on; that gap is tracked as
**#2273**. `scripts/logging_otel.py`, the single file remaining under
`scripts/`, is kept **only as a reference implementation for #2273** — it is
not live code, it is not importable (it imports a `common` module #2213
deleted), and it is not on any path `rqa` runs. Do not point an operator at
it.

---

## 10. Platform

**No platform constraint.** `rqa` reads no credential store, spawns no
platform-specific process, and has no `sys.platform` branch in its record
path. Appending works identically on macOS, Linux, Windows, in a container,
and in CI, with nothing to install and no daemon to run.

This was not always true. Until ADR-0066 the record read an HMAC key from the
OS keychain: macOS-only at first, so every append failed on Linux (#2272),
then macOS plus Linux Secret Service (PR #2287), which would have needed a
third integration for Windows and left headless Linux operators needing a
running Secret Service session. Removing the key removed the whole class of
problem rather than adding a third backend.

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
