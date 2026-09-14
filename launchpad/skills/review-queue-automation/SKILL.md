---
name: review-queue-automation
description: Operate the `rqa` command surface for review-queue-automation —
  sweep configured repositories, read a PR's disposition, list and decide
  open escalations, and reconstruct an outcome offline from the tamper-evident
  record. Use when a repository needs onboarding, a PR's status is unclear, an
  escalation needs a human decision, or an outcome needs explaining without a
  GitHub or model call.
---

# Review queue automation

`rqa` is a Python command surface. It has no packaged console-script entry
point yet (`CUTOVER.md`, #2212), so every invocation below is run from the
skill root as `python3 -m rqa.cli <command> ...` — `rqa/cli/__main__.py` is
the sanctioned form; `python3 -m rqa.cli.main` also works but is not the one
this document uses, since it triggers a `RuntimeWarning` about the module
already being in `sys.modules`.

State lives under `--state-dir` (default `$RQA_STATE_DIR`, else
`~/.local/state/rqa`) as a SQLite database plus job artifacts. Per-repository
configuration lives at `<repo>/.rqa/config.json`, written by `rqa onboard` and
read by `rqa.policy.validate`; `config.example.json` is the tracked example of
that file's shape, never itself a populated config.

## The six commands

Every command exists in `rqa/cli/main.py` and nothing else does. Global flag:
`--state-dir <path>`.

### `rqa tick`

One sweep over every configured repository — creates at most one job per PR
revision, admits or refuses each repository, and dispatches a bounded, fair
batch to the lifecycle.

```bash
python3 -m rqa.cli tick [--repo <owner/repo> ...] [--batch-size <int>]
```

`--repo` is repeatable. Omit it and `tick` reads `<state-dir>/repos.json` (a
JSON array of `owner/repo` strings); a missing file sweeps zero repositories,
which is not an error. A concurrent `tick` against the same state directory
returns `outcome: "sweep_already_running"` rather than blocking or double
-dispatching.

### `rqa onboard`

Writes a starter `<repo>/.rqa/config.json`.

```bash
python3 -m rqa.cli onboard <repo> [--migrate]
```

`<repo>` is the repository root. Plain `onboard` refuses if a config already
exists (`already_exists`). `--migrate` instead converts an old-shape config in
place — dropping the notification-transport and retention-window keys and
zeroing every `authority` entry the old shape never named — and refuses if no
old config is present, or if the migrated result itself fails validation.
Every refusal is a value, not a crash: exit 1, `outcome: "refused"`.

### `rqa status`

The current FR-016 disposition and its reason for one pull request, read-only.

```bash
python3 -m rqa.cli status <repo> <number>
```

Three plain `SELECT`s, no GitHub call, no lock. An unknown `(repo, number)`
returns `outcome: "not_found"` (exit 1), never a crash.

### `rqa pending`

Every open escalation, oldest first, each naming its cause and question.

```bash
python3 -m rqa.cli pending
```

Takes no arguments beyond the global `--state-dir`.

### `rqa decide`

Records a human decision against one open escalation and resumes the
lifecycle it belongs to.

```bash
python3 -m rqa.cli decide <escalation_id> --actor <name> --basis <text> [--outcome {approved,changes_requested}]
```

`--actor` and `--basis` are required and must be non-blank. `--outcome` may
only be supplied when the escalation's cause is `authority_requirement`; on
any other cause it is a hard programming-error rejection (`outcome:
"rejected"`, exit 1), not a silently ignored flag. Decide also refuses
(`outcome: "refused"`, exit 1) an unknown escalation id, an already-closed
escalation, a moved head, or a moved policy snapshot — each names which.

There is no `supersede` command and none is planned as a port of the retired
estate's. Supersession is detected structurally, by P-01 at inventory time on
a head change, not by an operator invoking anything.

### `rqa explain`

Reconstructs an outcome from the tamper-evident record alone — no GitHub
call, no model call, no write.

```bash
python3 -m rqa.cli explain <repo> <number>
python3 -m rqa.cli explain job <job-id>
```

The first positional is `repo` (an `owner/repo` slug) or the literal `job`;
the second is the PR number or the job id accordingly. An unreconstructable
target returns `outcome: "unavailable"` (exit 1).

## Exit codes

`rqa/cli/exitcodes.py` declares five: `0` OK, `1` INPUT_ERROR, `2` NETWORK,
`3` AUTH, `4` OTHER — the module's own docstring says "and nothing else". In
the current `rqa/cli/main.py`, only three of those five are ever actually
returned: `0` on success, `1` for a bad invocation or a command's own refusal
value (`not_found`, `refused`, `rejected`, `usage_error`), and `4` for every
other exception a provider raises (`LifecycleError`, `AppendFailed`,
`ReuseResolutionError`, and anything unanticipated). No code path in
`rqa/cli/main.py` returns `2` or `3` today, and no test exercises either —
`GithubUnavailable` is a returned value inspected by callers, not an
exception the CLI's dispatch loop maps to a network-specific code. Do not
expect a network or auth failure to produce a distinct exit code until that
changes.

## Configuration and policy

`<repo>/.rqa/config.json` validates against exactly five top-level groups —
`authority`, `routes`, `external`, `policy`, `budget` — through
`rqa.policy.validate.validate()`. Every top-level key outside that set is
rejected (`UNKNOWN_KEY`), fail-closed and collected: a config with three
errors is reported with all three in one pass, never one per run.
`config.example.json` tracks a config of exactly that shape, including the
optional per-route `command`; see [OPERATORS.md](OPERATORS.md) §2 for the
full field-by-field reference and the frozen requirement text driving the
six dispositions and five escalation causes.

## Authority is not yet wired to a grant

Configuring `authority.*` `true` for an activity does not currently cause
`rqa` to act on a pull request. `rqa/authority/gate.py`'s
`_configured_repositories()` is a hardcoded empty set and
`rqa/cli/composition.py`'s `AuthorityClient` has no way to supply a managed
repository list, so in production every activity on every repository is
denied (`REPO_NOT_MANAGED`) regardless of configuration. This is filed as
#2274, a `deferred-blocker` against this Feature. Do not configure
`authority.*` expecting an activity to run; treat every deployment today as
advisory-only until #2274 lands.

## Tests

```bash
python3 launchpad/skills/review-queue-automation/tests/run_all.py \
        launchpad/skills/review-queue-automation
```

No pytest dependency for that runner; the same suite also runs under the
acceptance venv's real `pytest` (`architecture/validate.py` and
`tests/test_cutover_map.py` are separate, non-pytest checks — see
[CUTOVER.md](CUTOVER.md)).

## Onboarding a new repository

See [onboarding/SKILL.md](onboarding/SKILL.md) for the first-time-per-repo
procedure. Full operator reference — config fields, the six dispositions, the
five escalation causes and what an operator does for each, the four ratified
architecture decisions, and every currently-open caveat — is in
[OPERATORS.md](OPERATORS.md).
