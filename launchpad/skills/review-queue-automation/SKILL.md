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

`0` means success; `1` means input error or policy refusal; `2` means a GitHub
network or availability failure; `3` means authentication failed; `4` means an
internal, persistence or job failure. A partial or wholly unavailable inventory
reports `outcome: "incomplete"` and names failed repositories. A failed job cannot
produce a successful tick exit code. All five are emitted: `tick` maps an
`unauthenticated` inventory outage to `3` and any other unreachable one to `2`
(`rqa/cli/main.py`), which `tests/test_rqa_cli_regressions.py` pins.

## Platform and state

macOS Keychain and Linux Secret Service (`secret-tool`) are supported.
`onboard`, `tick` and `decide` check keychain availability before work; an absent
key is explicitly unkeyed, while an unavailable backend is an error.
`onboard` requires an existing local directory. Read and decision commands require
an existing state database so a mistyped state directory creates nothing.
`explain` uses the writer's keychain and reports the stored human decision basis.
Control characters in operator text render as visible escapes, preserving line
boundaries without activating terminal controls.

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

## Authority and credential evidence

The CLI passes the configured repository set to the gate. An activity needs
its explicit policy flag and credential evidence: GitHub write attestations
qualify only when repository permissions and OAuth scopes both support the
operation. Unknown evidence denies, exercised and attested provenance remain
separate, and grants never bypass GitHub protection. See [OPERATORS.md](OPERATORS.md) §8.

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
