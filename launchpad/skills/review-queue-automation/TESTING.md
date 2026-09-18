# RQA conformance proof — recorded runbook

This document records what Review Queue Automation **did**, on a named machine, at a
named commit, against real GitHub pull requests. It is not a description of what RQA
is designed to do; the architecture under `architecture/` and the requirements under
`requirements/` already do that, and a conformance proof that cited them would be
circular.

Its purpose is to falsify. Every criterion below is reported **demonstrated**,
**partially demonstrated** or **not demonstrated**, on the evidence of pasted command
output and nothing else. Several are not demonstrated. An honest "not met" with
reproducible evidence is worth more than a "met" claim that cannot be reproduced, and
this document is written to that standard.

Nothing here was produced by wiring, stubbing, monkeypatching or otherwise adjusting
RQA to make a criterion reachable. Where a criterion is blocked, the block is
recorded, attributed to the defect that causes it, and left in place. One
counterfactual probe appears in [§6.3](#63-counterfactual-is-2274-the-only-thing-in-the-way);
it is labelled a counterfactual everywhere it appears and contributes to no verdict.

## Document structure

| Part | Scope | Author |
|---|---|---|
| **Part 1 — lifecycle** (this part, §1–§9) | The end-to-end lifecycle proof: two independently configured repositories, one public and one private, one local operator process; disposition, reconstruction, policy differentiation, provider identification, component inventory. Task #2215. | Task #2215 |
| **Part 2 — decided ADR paths and the credential floor** | Appended below Part 1, unchanged above this line. Task #2216. | Task #2216 |
| **Part 3 — completion run** | Appended live proof after the blockers found in Part 1 were corrected: authoritative reviews, policy differentiation, two local routes, public/private organisations, and merge/no-merge behavior. Task #2215. | Task #2215 |

Parts 2 and 3 conform to the re-run contract defined in [§3](#3-the-re-run-contract).
They do not rewrite Part 1; later evidence annotates or supersedes its conclusions.

> **Current implementation validation (2026-09-18, separate from the historical Part 1 capture).**
> `python3 -m pytest tests --collect-only -qq` collected **1528 tests**. The final
> #2299/#2300 focused command ran 172 tests, and `architecture/validate.py`,
> `requirements/validate.py`, and `tests/test_cutover_map.py` passed. The all-at-once
> pytest and dependency-free runner did not emit a final summary within this execution
> environment's time window, so this document does not claim they passed.

---

## 1. Front matter — where and when this run happened

Everything in Part 1 was produced by one operator, on one machine, in one sitting.

```
$ git -C "$REPO" rev-parse HEAD
b9c98f423a1333aa4449ffce2e2418e3be364b39
$ uname -a
Darwin Jeffs-MacBook-Pro.local 24.6.0 Darwin Kernel Version 24.6.0: Tue Apr 21 20:17:54 PDT 2026; root:xnu-11417.140.69.710.16~1/RELEASE_X86_64 x86_64 Darwin
$ sw_vers | tr '\n' ' '
ProductName:		macOS ProductVersion:		15.7.7 BuildVersion:		24G720 
$ python3 -V
Python 3.14.6
$ gh --version | head -1
gh version 2.100.0 (2026-09-03)
$ git --version
git version 2.52.0
$ python3 -c 'import sqlite3;print("sqlite3 (stdlib) library version", sqlite3.sqlite_version)'
sqlite3 (stdlib) library version 3.53.4
```

| Fact | Value |
|---|---|
| Commit | `b9c98f423a1333aa4449ffce2e2418e3be364b39` on `feature/2189-conformance` |
| Branch of record | `rqa-2215` (this lane), branched from the above |
| Platform | macOS 15.7.7, Darwin 24.6.0, x86_64 |
| Python | 3.14.6 (system `python3`) |
| State directory | `/tmp/rqa-2215/proof/state` — a scratch directory, not `~/.local/state/rqa` |
| Host clock during the run | `2026-09-14` UTC. Every `raised_at` / `activated_at` below is host-clock. |
| **Was the record keyed?** | **No.** All 55 record rows have `keyed=0` and `hmac=NULL`. See [§7.2](#72-2272-the-record-was-appended-but-not-keyed). |

> **Superseded by ADR-0066 / #2299 for any run after 2026-09-16.** The macOS dependency
> described below no longer exists: the key, `keychain.py` and the `sys.platform` branch
> are all removed, and a reader reproducing Part 1 on Linux or Windows now gets exactly
> as far as one on macOS. The paragraph is kept as the record of what the #2189 run saw.

**On macOS specifically.** This run could happen at all *because* it ran on macOS.
`rqa/record/keychain.py:89-92` branches on `sys.platform`; on any other platform the
key read raises and `rqa/record/writer.py:118-123` turns that into `AppendFailed`, so
no record row can be appended at all. That is defect **#2272**. On this host the
keychain item `rqa-record-hmac` is simply absent, which is the *other* branch: the
record is appended unkeyed. No keychain item was created to make this look better. A
reader reproducing Part 1 on Linux will not get as far as the first record row.

### Repositories used

All four are controlled by the operator. None belongs to `launchpad-26` or
`block/buzz`, and no pull request belonging to this programme was touched.

| Repository | Owner | Owner type | Visibility | Role in this proof |
|---|---|---|---|---|
| `tucktuck101/inTooDeep` | `tucktuck101` | User | **PUBLIC** | Primary public target (9 open PRs) |
| `tucktuck101/agent-trust-platform` | `tucktuck101` | User | **PRIVATE** | Primary private target (2 open PRs) |
| `tucktuck101/test_workflow` | `tucktuck101` | User | PUBLIC | AC02 policy differentiation (2 open PRs) |
| `tucktuck101/collaboration-repo-template` | `tucktuck101` | User | PUBLIC | AC17 / NFR-014 provider enable-then-remove (3 open PRs) |

---

## 2. Prerequisites

A reader reproducing this needs all of the following. Nothing else.

1. **This repository** at commit `b9c98f423`, with the skill at
   `launchpad/skills/review-queue-automation/`. No build, no install, no packaging
   step: RQA is run in place as `python3 -m rqa.cli` (`SKILL.md:13-18`; there is no
   console-script entry point — that is #2212).
2. **Python 3.11 or newer.** RQA imports nothing outside the standard library (see
   [§6.6](#66-nfr-014--the-component-and-licence-inventory)).
3. **`gh`, the GitHub CLI, authenticated.** This is RQA's only credential source:
   `rqa/github/transport.py:106-132` resolves the token by running `gh auth token` as
   a subprocess, per call. There is no `GITHUB_TOKEN` environment variable in this
   path and no credential file RQA reads.
   *The credential is named here and never shown.* The account used was
   `tucktuck101`; the token's scopes are quoted in [§6.3](#63-counterfactual-is-2274-the-only-thing-in-the-way)
   because a capability denial turns on them. The token value appears nowhere in this
   document, the record, the configs, or the test suite.
4. **Four repositories the reader controls**, matching the visibility mix in §1. They
   do not have to be these four, but a public/private pair is required or §6.1 proves
   nothing.
5. **No harness and no model are required to reproduce Part 1.** That is not a
   convenience: no review ever starts, so no harness is ever invoked. See
   [§5](#5-the-blocking-defect-that-shapes-this-entire-proof).
6. **Policy files are not pre-existing artefacts.** Each is generated by `rqa onboard`
   during the run and then edited in place; every edit is shown.

### How `repo` resolves, and why no clone is needed

`rqa/policy/snapshot.py:62-69` defines `config_path(repo) = Path(repo)/".rqa"/"config.json"`,
recomputed on every call and never cached. The `repo` argument is therefore *both* a
GitHub slug (for API reads) and a **filesystem path relative to the process's working
directory** (for configuration). Running `rqa onboard tucktuck101/inTooDeep` from
`/tmp/rqa-2215/proof/repos` writes
`/tmp/rqa-2215/proof/repos/tucktuck101/inTooDeep/.rqa/config.json`.

Two consequences that matter for reproduction:

- **No clone, no push, no GitHub write is needed to configure a repository for RQA.**
  Everything in §6.4 and §6.5 is a local file edit.
- **The working directory is part of the command.** Every command below is run from
  `/tmp/rqa-2215/proof/repos`. Run them elsewhere and RQA will read a different (or
  missing) config, and `tick` will refuse the repository rather than admit it.

### Layout this run used

```
/tmp/rqa-2215/proof/
├── repos/                                   # working directory for every rqa command
│   └── tucktuck101/
│       ├── inTooDeep/.rqa/config.json
│       ├── agent-trust-platform/.rqa/config.json
│       ├── test_workflow/.rqa/config.json
│       └── collaboration-repo-template/.rqa/config.json
├── state/                                   # $RQA_STATE_DIR — all durable state
│   ├── lock
│   ├── snapshots/<policy-hash>.json
│   └── state.db
├── state-ext-on/                            # §6.5 phase 1
└── state-ext-off/                           # §6.5 phase 2
```

### Environment every command below assumes

```bash
REPO=<path to this checkout>
SKILL="$REPO/launchpad/skills/review-queue-automation"
export PYTHONPATH="$SKILL"
export RQA_STATE_DIR=/tmp/rqa-2215/proof/state
export RED='s/(gho_|ghp_|ghu_|ghs_|github_pat_)[A-Za-z0-9_]+/[REDACTED]/g'
mkdir -p /tmp/rqa-2215/proof/repos && cd /tmp/rqa-2215/proof/repos
```

`PYTHONPATH` rather than `cd "$SKILL"` is deliberate: `rqa` must be importable while
the working directory is the one whose `.rqa/` trees RQA reads. Running from the skill
root instead would scatter `tucktuck101/...` config trees inside the checkout.

---

## 3. The re-run contract

**Every pasted result in this document — Part 1 and Part 2 — carries all five of the
following, or it is not evidence.** A result a reader cannot re-obtain is a claim, not
a proof.

| Field | Meaning |
|---|---|
| **Command** | The exact argv, including working directory and any environment that changes its behaviour. Not a paraphrase, not a shortened form. |
| **Commit** | The `git rev-parse HEAD` the command ran against. |
| **Job id / record locator** | For anything touching the record: the job id, or the record row's `(job, seq)`. Content-addressed job ids are reproducible — see the note below. |
| **Platform** | OS and architecture. Non-negotiable while #2272 makes the record platform-dependent. |
| **Repository** | The `owner/name` it ran against, with visibility. |

Three further rules bind every result:

1. **Redaction happens at the point of capture.** Every command whose output is pasted
   was piped through `sed -E "$RED"` *as it ran*. Redacting a file that already hit
   disk is not redaction at the point of capture, and this document contains no
   output that was cleaned up afterwards.
2. **Pasted, not summarised.** Where output is long, it is elided with an explicit
   marker and the eliding is stated. It is never replaced by a description of itself.
3. **Counterfactuals are labelled at every appearance** and contribute to no verdict.

**Job ids are reproducible.** Job ids are content-addressed over the repository and
the PR revision, not generated. The `tick` in §6.1 was run twice, hours apart, into
two different state directories, and produced byte-identical job ids both times. A
reader whose targets are at the same revisions will see the same ids; a reader whose
targets have moved on will see different ids and the same *shape* of result.

**Where the raw captures live.** Each result below names its capture file, e.g.
`[capture: 03-tick.txt]`. Those files were written under `/tmp/rqa-2215/proof/out/`
during the run. They are scratch, not committed — the pasted text here is the
artefact. The file names are recorded so a re-runner can name their own the same way.

**Sweep of every capture against the five fields (gate round 1, `RQA2215-EVIDENCE-FORMAT`).**
All fourteen numbered captures in this document were audited against the table above
and against rule 2. Result:

- **Two genuine violations, both fixed by re-running and re-capturing**: captures 10
  (§6.4) and 11 (§6.5) previously pasted condensed prose (`outcome swept | jobs 3`) in
  place of the CLI's real JSON, with no elision marker and no job ids. Both sections
  now paste the complete, unelided `tick` stdout and name every job id created. The
  re-run used fresh state directories so both are reproducible from an empty start.
- **Seven captures name no job id because none applies**, and each now says so
  explicitly rather than leaving the field silently absent: 01 and 12 run no RQA
  command at all; 02 (`onboard`) writes a config file and no record row; 04
  (`status`), 06 (`explain`) and 09 are read-only; **historical** capture 13 probes `OSKeyStore` in-process
  with no append attempted. "Not applicable, because nothing touched the record" is a
  value this field can take; "absent" is not.
- **Five captures already conformed**: 03, 05, 07, 08 and F-2's enumeration block,
  each carrying command, commit, locator, platform and repository, with every elision
  explicitly marked.

**Sweep of every out-of-diff source citation (gate round 1, Lesson 5).** All ~28 line
citations in §5–§7 and the findings were re-checked against the files at
`b9c98f423`. **Three had drifted and are corrected**: `transport.py:106-133` →
`106-132`, `gate.py:423-437` → `418-436`, `SKILL.md:12-18` → `13-18`. Every citation in
F-1 and F-2 was verified accurate as written. A wrong line number in a finding meant
to be filed standalone is a defect in the deliverable, so these are listed rather than
silently fixed.

---

## 4. The boundary this proof was run inside

These are hard constraints on the run, not descriptions of RQA.

- **No GitHub write of any kind was performed.** No pull request was opened,
  commented on, approved or merged; no review was submitted; no issue was touched; no
  repository was created; nothing was pushed. Everything below is reads plus local
  file writes. Where a criterion requires a write to demonstrate, it is reported not
  demonstrated rather than demonstrated by a write.
- **`launchpad-26` and `block/buzz` were out of bounds for read as well as write.**
  RQA was never pointed at either.
- **No credential value appears anywhere** in this document, the configs, the record,
  the test suite or the commit.
- **`authority.merge` was never set to `true` on a live repository.** AC14's
  merge/no-merge half would require it, and a configuration that could merge a real PR
  is a GitHub write waiting to happen. The conservative reading was taken; see
  [§8, AC14](#8-criterion-by-criterion-verdict).

### AC16's second half is a boundary limitation, not a product limitation

AC16 asks for repositories "under different GitHub owners or organisations". The
credential reaches exactly one user and one organisation, and the organisation is the
excluded one:

```
$ gh api user --jq ".login + \" type=\" + .type"
tucktuck101 type=User
$ gh api user/orgs --jq ".[].login"
launchpad-26
$ gh repo list tucktuck101 --limit 200 --json owner --jq "[.[].owner.login]|unique|.[]"
tucktuck101
```
*[capture: 01-owner-census.txt · commit `b9c98f423` · macOS x86_64 · repository: none — this is a credential/owner census, not a run against a repository · record locator: none — no RQA command ran, so no record row was written · unelided]*

All 34 repositories the credential can enumerate have exactly one owner. The only
second owner it can reach is `launchpad-26`, which this proof may not touch.

**Therefore the "different owners" half of AC16 is NOT DEMONSTRATED.** No second
organisation was simulated and no repository was created to manufacture one.

**This is a limitation of the run's boundary, not of the product.** Nothing observed
suggests RQA would behave differently under a second owner: the owner string is
carried through as opaque data in `config_path()`, in the `h`-free GitHub slug used
for API reads, and in the record's `repo` field. `tick` admitted repositories under
both visibilities with no owner-specific branch anywhere in the path exercised. RQA
simply was not run under two owners, because inside this boundary it could not be.
A reader with a second organisation can reproduce §6.1 against it unchanged.

The *other* half of AC16 — two independently configured repositories, one public and
one private, one local operator process, no centrally hosted service — is
demonstrated in [§6.1](#61-ac16--rqa-nfr-004-one-local-process-two-repositories-two-visibilities)
and [§6.6](#66-nfr-014--the-component-and-licence-inventory).

---

## 5. The blocking defect that shapes this entire proof

Read this before the results, or several of them will look like the proof was done
badly.

Three facts, each verified at source in this worktree at `b9c98f423`:

1. **`rqa/authority/gate.py:95-110`** — `_configured_repositories()` returns a bare
   `frozenset()`. Its own docstring: *"Unwired it is empty, and then every repository
   is `REPO_NOT_MANAGED`: a gate that does not know which repositories it governs must
   answer for none of them. Real wiring constructs `Gate(repos=...)` and injects its
   bound `grant` as P-02's `AuthorityClient`."*
2. **`rqa/cli/composition.py:113-122`** — the composed `AuthorityClient.__init__` is
   `(self, *, github, store)`, and its `grant` delegates to the module-level free
   function `authority_mod.grant(**kwargs)`, which builds
   `Gate(repos=_configured_repositories())` (`gate.py:418-436`). **The composition root
   constructs no `Gate` and exposes no parameter, config key or environment variable
   by which a managed set could be supplied.** That is **#2274**, confirmed from both
   ends.
   *(`rqa/cli/main.py:105` also has a `repos` name. It is unrelated: that is `tick`'s
   sweep list, the set of repositories to look at, not the gate's set of repositories
   it is authorised over. The collision is a trap for a reader skimming for "repos".)*
3. **`rqa/lifecycle/steps.py:196-224`** — the gate is called with `Activity.REVIEW`
   **before the review runs**. On `Deny`, the job escalates with reason
   `review authority denied (repo_not_managed)`. The lifecycle never reaches the lease
   claim, the facts capture, the harness, the judgement, the verdict or any submission.

**Consequence: through the composed system, on any repository, no review ever starts.**
This is not "the review runs and submission is denied". Every criterion downstream of
step 3 is unreachable through `rqa tick` today: AC01, AC05, AC09, AC10, AC11, AC12,
AC14, and the completed-review half of AC06.

**Recording the denial is running the proof.** The composed system was run, it
produced an outcome, that outcome is authoritative, and it is reconstructed below.
Nothing was wired to route around it.

---

## 6. The run

### 6.1 AC16 / RQA-NFR-004: one local process, two repositories, two visibilities

**Step 1 — onboard both repositories and grant review authority.**

```
$ python3 -m rqa.cli onboard tucktuck101/inTooDeep
{
  "command": "onboard",
  "outcome": "written",
  "result": {
    "path": "tucktuck101/inTooDeep/.rqa/config.json"
  }
}
$ python3 -m rqa.cli onboard tucktuck101/agent-trust-platform
{
  "command": "onboard",
  "outcome": "written",
  "result": {
    "path": "tucktuck101/agent-trust-platform/.rqa/config.json"
  }
}
$ # grant review+comment authority in BOTH configs, so a denial cannot be
$ # explained away as "the operator never granted review"
$ jq -c .authority */*/.rqa/config.json
  tucktuck101/inTooDeep/.rqa/config.json  {"approve": false, "comment": true, "merge": false, "remediate": false, "request_changes": false, "review": true}
  tucktuck101/agent-trust-platform/.rqa/config.json  {"approve": false, "comment": true, "merge": false, "remediate": false, "request_changes": false, "review": true}
```
*[capture: 02-onboard.txt · commit `b9c98f423` · macOS x86_64 · `tucktuck101/inTooDeep` PUBLIC + `tucktuck101/agent-trust-platform` PRIVATE · record locator: none — `onboard` writes a config file and no record row · unelided]*

`authority.review: true` is set deliberately. A run with `review: false` would earn a
denial for the wrong reason and prove the wrong thing.

**Step 2 — one sweep, one local process, both repositories.**

```
$ echo $RQA_STATE_DIR
/tmp/rqa-2215/proof/state
$ python3 -m rqa.cli tick --repo tucktuck101/inTooDeep --repo tucktuck101/agent-trust-platform
{
  "command": "tick",
  "outcome": "swept",
  "result": {
    "jobs_created": [
      "1126fea21076c076004da790e5d80952a2ef4981a2540822f1149f81c6810115",
      "34726e9159652a261f7f9ebb71e1bd3ebbeae8bbaa72fce605b35cbd39abd558",
      "5f9982762c48e9b1fbba6ada06c447ff358b52ed89c8b577996556eb8b41e064",
      "b7d868a1efc44bf4a1fe86e039b626ffc49edc168206294f3aad35ceaa8fc4c7",
      "e6d0f5216952dd12d947f98408c5003d39eb06a3a6071691a65bc05f4bb9b7c3",
      "2f8f6adcaaad76f08940080f0215f4f04e35acab8de8bdef5f2954973656c837",
      "1b4b20f6f435f02bf799fcd5f000c9d3ef689a7f84153d647bffe13ecbe8388b",
      "d2736ae80f3f8ec7927ec6df16d7a86456c2305698401a49d94cbc2106f621b0",
      "62944f4f3ea9289e6a9f7420dac305b3c365b229e4afa0ec94fc256c2a47e36c",
      "6b4f93aeb1ca1b5ba919236e2e21fe821f295bdbf5348c72889284c3938b8ff8",
      "61e931c37f810d4d8b1c05ca48eefe5127e42733170645cc76b8d9087d53d271"
    ],
    "jobs_dispatched": [ … the same eleven ids, in the same order … ],
    "jobs_failed": [],
    "outcome": "swept",
    "repos_admitted": [
      "tucktuck101/inTooDeep",
      "tucktuck101/agent-trust-platform"
    ],
    "repos_refused": [],
    "revisited_resting_jobs": []
  }
}
```
*[capture: 03-tick.txt · commit `b9c98f423` · macOS x86_64 · `tucktuck101/inTooDeep` PUBLIC + `tucktuck101/agent-trust-platform` PRIVATE. `jobs_dispatched` elided only because it repeats `jobs_created` exactly; the full text is in the capture.]*

Eleven jobs: nine open PRs on the public repository plus two on the private one. Both
repositories admitted, none refused. One process, one `--state-dir`, no service.

**What this demonstrates:** two independently configured repositories, one PUBLIC and
one PRIVATE, swept by one local operator process in one invocation, with every
durable artefact under a local state directory. **What it does not demonstrate:** two
owners — see [§4](#ac16s-second-half-is-a-boundary-limitation-not-a-product-limitation).

### 6.2 AC08 and AC06: the disposition and its reconstruction

**`rqa status` — AC08's one command, for a PR in each repository.**

```
$ python3 -m rqa.cli status tucktuck101/inTooDeep 14      # PUBLIC
{
  "command": "status",
  "outcome": "ok",
  "result": {
    "disposition": "awaiting human judgement",
    "internal_state": "escalated",
    "job_id": "1126fea21076c076004da790e5d80952a2ef4981a2540822f1149f81c6810115",
    "reason": "review authority denied (repo_not_managed)"
  }
}
$ python3 -m rqa.cli status tucktuck101/agent-trust-platform 107   # PRIVATE
{
  "command": "status",
  "outcome": "ok",
  "result": {
    "disposition": "awaiting human judgement",
    "internal_state": "escalated",
    "job_id": "6b4f93aeb1ca1b5ba919236e2e21fe821f295bdbf5348c72889284c3938b8ff8",
    "reason": "review authority denied (repo_not_managed)"
  }
}
```
*[capture: 04-status.txt · commit `b9c98f423` · macOS x86_64 · `tucktuck101/inTooDeep` PUBLIC #14 (job `1126fea21076c076004da790e5d80952a2ef4981a2540822f1149f81c6810115`) and `tucktuck101/agent-trust-platform` PRIVATE #107 (job `6b4f93aeb1ca1b5ba919236e2e21fe821f295bdbf5348c72889284c3938b8ff8`) · `status` is read-only and writes no record row · unelided]*

One command, one answer from RQA-FR-016's closed six, plus a reason, with no human
reconciling history. That is AC08, and it works — including for a PR whose review
never started, which is the harder case.

**`rqa pending` — the escalation.**

```
$ python3 -m rqa.cli pending | python3 -c "…len(result), then result[0]…"
11 open escalations; first:
{
  "cause": "authority_requirement",
  "context": {
    "detail": "review denied (repo_not_managed)",
    "repo": "tucktuck101/inTooDeep"
  },
  "entry_seq": 4,
  "head_sha": "be2a13be4c5b623ce0218074de80ce6c78eb0b2b",
  "id": 1,
  "job_id": "1126fea21076c076004da790e5d80952a2ef4981a2540822f1149f81c6810115",
  "question": "RQA lacks authority on tucktuck101/inTooDeep: review denied (repo_not_managed)",
  "raised_at": "2026-09-14 14:49:23.934613+00:00",
  "snapshot_hash": "51bbd033e4ff56777869dd605a8964553e38f7f2e2e4390714a407d702b9ff9d"
}
```
*[capture: 05-pending.txt · commit `b9c98f423` · macOS x86_64 · job `1126fea2…` · `tucktuck101/inTooDeep` PUBLIC. Ten further escalations of identical shape elided; the capture holds all eleven.]*

**This escalation's `question` is specific, but that is not evidence that specificity
is enforced.** #2260 records that `raise_` accepts a generic question and nothing
validates it. This one reads well because its call site happens to construct it well.
Do not read the output above as a demonstration of AC13's specificity requirement.

**`rqa explain` — AC06's offline reconstruction.**

```
$ python3 -m rqa.cli explain tucktuck101/inTooDeep 14
{
  "command": "explain",
  "outcome": "ok",
  "result": {
    "decision_basis": null,
    "disposition": "awaiting human judgement",
    "evidence": {},
    "findings": [],
    "harness": [],
    "hmac_checked": false,
    "job_id": "1126fea21076c076004da790e5d80952a2ef4981a2540822f1149f81c6810115",
    "legacy": false,
    "model": [],
    "number": 14,
    "policy_version": null,
    "pr_revision": "be2a13be4c5b623ce0218074de80ce6c78eb0b2b",
    "protocol_hash": null,
    "provider": [],
    "repo": "tucktuck101/inTooDeep",
    "reviewer_identity": [],
    "reviewer_type": "none",
    "snapshot_hash": null,
    "truncated_at": null,
    "unverifiable": [
      {
        "first_seq": 1,
        "job_id": "1126fea21076c076004da790e5d80952a2ef4981a2540822f1149f81c6810115",
        "last_seq": 5,
        "reason": "no key"
      }
    ],
    "verified": false
  }
}
$ python3 -m rqa.cli explain job 6b4f93aeb1ca1b5ba919236e2e21fe821f295bdbf5348c72889284c3938b8ff8   # PRIVATE, by job id
{
  "command": "explain",
  "outcome": "ok",
  "result": {
    "decision_basis": null,
    "disposition": "awaiting human judgement",
    "evidence": {},
    "findings": [],
    "harness": [],
    "hmac_checked": false,
    "job_id": "6b4f93aeb1ca1b5ba919236e2e21fe821f295bdbf5348c72889284c3938b8ff8",
    "legacy": false,
    "model": [],
    "number": 107,
    "policy_version": null,
    "pr_revision": "efa61025874f1ce4bb0a693bef3108eaa5de3565",
    "protocol_hash": null,
    "provider": [],
    "repo": "tucktuck101/agent-trust-platform",
    "reviewer_identity": [],
    "reviewer_type": "none",
    "snapshot_hash": null,
    "truncated_at": null,
    "unverifiable": [
      {
        "first_seq": 1,
        "job_id": "6b4f93aeb1ca1b5ba919236e2e21fe821f295bdbf5348c72889284c3938b8ff8",
        "last_seq": 5,
        "reason": "no key"
      }
    ],
    "verified": false
  }
}
```
*[capture: 06-explain.txt · commit `b9c98f423` · macOS x86_64 · `tucktuck101/inTooDeep` PUBLIC #14 (job `1126fea21076c076004da790e5d80952a2ef4981a2540822f1149f81c6810115`) and `tucktuck101/agent-trust-platform` PRIVATE #107 (job `6b4f93aeb1ca1b5ba919236e2e21fe821f295bdbf5348c72889284c3938b8ff8`) · `explain` is read-only and writes no record row · unelided]*

Read this honestly. `explain` **names every AC06 element** — the field set is
complete, and it reconstructs the PR revision and the disposition correctly from the
record alone, with no GitHub call. It also **tells the truth about what it cannot
establish**: `verified: false`, `hmac_checked: false`, and an explicit `unverifiable`
segment saying "no key". A reconstruction that had silently reported `verified: true`
over an unkeyed record would be far worse than this.

But **nine of the twelve** AC06 elements are empty, and they are empty for two
different reasons that must not be conflated:

- **Seven are honestly empty** — `harness`, `model`, `provider`, `reviewer_identity`,
  `evidence`, `findings`, `decision_basis` — **because no review ran** (#2274 and
  F-2). There is genuinely nothing to reconstruct.
- **Two are wrongly `null`** — `protocol_hash` and `policy_version` — **even though the
  record contains both**. That is not honest emptiness but a reconstruction gap:
  [Finding F-1](#f-1--explain-reports-null-for-three-pins-the-record-demonstrably-holds).

*Counting footnote, because the arithmetic is easy to get wrong and an earlier draft of
this document did.* The twelve are the elements AC06 itself enumerates, listed as
`AC06_RECONSTRUCTION_ELEMENTS` in `tests/test_rqa_conformance_lifecycle.py`. Three of
the twelve are populated: `pr_revision` (`be2a13be…`), `disposition`
(`awaiting human judgement`) and `reviewer_type` (`"none"` — a real, informative value,
not an absence). 12 − 3 = **9** empty, split 7 + 2 as above. **F-1 names *three* pins,
not two**: its third, `snapshot_hash`, is also wrongly `null` but is a supporting
trust/rendering field rather than one of AC06's twelve, so it is counted in the finding
and not in the nine.

### 6.3 Counterfactual: is #2274 the only thing in the way?

> **COUNTERFACTUAL. This is not the composed system and it contributes to no verdict
> in [§8](#8-criterion-by-criterion-verdict).** It constructs `Gate(repos={...})` and
> calls it directly — the arrangement `gate.py:107-108` calls "real wiring", and which
> no CLI flag, config key or environment variable can produce today. It exists for one
> reason: whoever fixes #2274 needs to know whether fixing it is sufficient.

```
$ # COUNTERFACTUAL PROBE — not the composed system; labelled as such everywhere.
$ # Purpose: separate "blocked by #2274 alone" from "blocked for other reasons too".
[A] COMPOSED SYSTEM  (the product as shipped, via cli/composition.py):
     Deny reason = repo_not_managed
[B] COUNTERFACTUAL   (Gate(repos={repo}) — the arrangement gate.py:107-108 calls
                      'real wiring'; NOT reachable through any CLI flag or config key):
     Deny reason = capability_missing
     detail = the credential cannot review on tucktuck101/inTooDeep: missing ['issues:write']
```
*[capture: 08-counterfactual.txt · commit `b9c98f423` · macOS x86_64 · job `1126fea2…` · `tucktuck101/inTooDeep` PUBLIC]*

**#2274 is not the only blocker.** With the managed set supplied, the gate still
denies. The obvious reading — "the operator's token is under-scoped" — is wrong:

```
$ gh api /repos/tucktuck101/inTooDeep --jq .permissions
{"admin":true,"maintain":true,"pull":true,"push":true,"triage":true}
$ gh auth status | grep "Token scopes"
  - Token scopes: 'gist', 'project', 'read:org', 'repo', 'workflow'

$ # Set arithmetic over the two modules own published constants (no network):
  activities.py:30  REQUIRED_CAPABILITY[REVIEW] = ['checks:read', 'contents:read', 'issues:write', 'pulls:read']
  capability.py:34  probe can ever PROVE         = ['checks:read', 'contents:read', 'pulls:read']
  capability.py:36  probe can only ATTEST        = ['contents:write', 'issues:write', 'pulls:write']
  gate.py:236       missing = REQUIRED - proof.capabilities   (attested_not_proven unused)
  => permanently unsatisfiable residue for REVIEW = ['issues:write']
  => is Activity.REVIEW grantable by ANY credential on ANY repo? False
```
*[capture: 09-capability-contradiction.txt · commit `b9c98f423` · macOS x86_64 · `tucktuck101/inTooDeep` PUBLIC · record locator: none — two `gh` reads plus set arithmetic over two modules' published constants; nothing is written and no job is involved · unelided]*

GitHub reports the credential as `admin`/`push`/`triage` on the repository. The denial
is structural, not credential-specific, and it generalises from this one activity to
all six — it is
[Finding F-2](#f-2--the-authority-gate-can-never-grant-any-activity-6-of-6-even-with-2274-fixed).

### 6.4 AC02: a policy edit takes effect on the next sweep, with no rebuild

Run from `/tmp/rqa-2215/proof/repos` with `RQA_STATE_DIR=/tmp/rqa-2215/proof/state-ac02`
— a state directory dedicated to this demonstration, so that both sweeps below are
reproducible from an empty start rather than depending on §6.1's jobs already existing.
`tucktuck101/test_workflow` was first onboarded exactly as in §6.1
(`python3 -m rqa.cli onboard tucktuck101/test_workflow`, `outcome: "written"`), then
`authority.review`/`authority.comment` set true and `policy.blocking` set as shown.

```
$ # policy A: block on correctness/high, corroboration 1
   {"categories": ["correctness"], "corroboration": 1, "severities": ["high"]}
$ python3 -m rqa.cli tick --repo tucktuck101/test_workflow
{
  "command": "tick",
  "outcome": "swept",
  "result": {
    "jobs_created": [
      "732d4dd9c74f111d39b41f28b1d91c9bb6e1808404170b1cca626c815412583c",
      "96ddf95b6517b1fa387ea2cd21cd42f38780de50fb3a52572eaf2b6a33e7ca06"
    ],
    "jobs_dispatched": [
      "732d4dd9c74f111d39b41f28b1d91c9bb6e1808404170b1cca626c815412583c",
      "96ddf95b6517b1fa387ea2cd21cd42f38780de50fb3a52572eaf2b6a33e7ca06"
    ],
    "jobs_failed": [],
    "outcome": "swept",
    "repos_admitted": [
      "tucktuck101/test_workflow"
    ],
    "repos_refused": [],
    "revisited_resting_jobs": []
  }
}
$ # policy snapshots activated in this state directory so far:
  90e180be20991fa9bb10f3149bb1416a290f65098553779eaac294bf373adda8  unversioned  2026-09-14T15:41:31.374669+00:00

$ # edit ONLY policy.blocking -> variant B. No rebuild, reinstall, redeploy or restart.
   {"categories": ["correctness", "security"], "corroboration": 2, "severities": ["high", "medium"]}
$ python3 -m rqa.cli tick --repo tucktuck101/test_workflow      # the NEXT sweep
{
  "command": "tick",
  "outcome": "swept",
  "result": {
    "jobs_created": [],
    "jobs_dispatched": [],
    "jobs_failed": [],
    "outcome": "swept",
    "repos_admitted": [
      "tucktuck101/test_workflow"
    ],
    "repos_refused": [],
    "revisited_resting_jobs": []
  }
}
$ # policy snapshots activated in this state directory now:
  90e180be20991fa9bb10f3149bb1416a290f65098553779eaac294bf373adda8  unversioned  2026-09-14T15:41:31.374669+00:00
  455309fd8de0a421c13a33a53c89e5fa6f35ecc9f4d05d79c756afbd3547086b  unversioned  2026-09-14T15:41:51.967907+00:00
$ # and the newly activated archive holds exactly policy B, not a coincidental rehash:
$ python3 -c "json.load(open($RQA_STATE_DIR/snapshots/455309fd….json))["policy"]["blocking"]"
{
  "categories": [
    "correctness",
    "security"
  ],
  "corroboration": 2,
  "severities": [
    "high",
    "medium"
  ]
}
```
*[capture: 10-ac02-policy-edit.txt · commit `b9c98f423` · macOS x86_64 · `tucktuck101/test_workflow` PUBLIC · state dir `/tmp/rqa-2215/proof/state-ac02` throughout · record locators: jobs `732d4dd9c74f111d39b41f28b1d91c9bb6e1808404170b1cca626c815412583c` and `96ddf95b6517b1fa387ea2cd21cd42f38780de50fb3a52572eaf2b6a33e7ca06`, created by the first tick; the second tick creates none, which is the point. Unelided: this is the complete stdout of both commands.]*

**What this demonstrates.** One state directory, one unchanged tree of installed code,
no build step of any kind between the two sweeps. Editing `policy.blocking` alone
caused the next sweep to read the file, validate it, and activate a **new** pinned
policy `455309fd…`, whose archived content is byte-for-byte the edit that was made.
The mechanism is `rqa/policy/snapshot.py:169` — *"A live read, unconditionally, every
call"* — and `config_path()`'s refusal to cache. That is AC02's "no rebuild, reinstall
or redeploy" clause, demonstrated.

**What this does not demonstrate.** `jobs_created 0` on the second sweep is the tell:
the two PRs already had jobs at those revisions, and those jobs are resting in
`escalated`, so **no next review occurred**. AC02's headline — *"two repositories
configured with different review policies produce demonstrably different **blocking
outcomes** on the same diff"* — requires a judgement, and no judgement is reachable
(#2274). Two policies were configured and pinned distinctly; neither produced a
blocking outcome, because neither produced any outcome.

### 6.5 AC17 and NFR-014: identify the provider, then remove it

Run from `/tmp/rqa-2215/proof/repos`. Each phase uses its own empty state directory so
that both are reproducible from scratch and neither inherits the other's jobs.
`tucktuck101/collaboration-repo-template` was first onboarded exactly as in §6.1
(`python3 -m rqa.cli onboard tucktuck101/collaboration-repo-template`,
`outcome: "written"`), then `authority.review`/`authority.comment` set true.

```
$ # PHASE 1 — the optional non-free provider ENABLED (external anthropic route):
   external.allowed = True
   routes = [('anthropic', 'external'), ('local', 'local')]
$ RQA_STATE_DIR=/tmp/rqa-2215/proof/state-ext-on python3 -m rqa.cli tick --repo tucktuck101/collaboration-repo-template
{
  "command": "tick",
  "outcome": "swept",
  "result": {
    "jobs_created": [
      "64f94555cc454b4119d45fa0a49448e8a6f376fa24b018a44fd3d0413fbd3e50",
      "d07db1826c96af66b78bc21f16b5e7accb70db91267d0ae00cc86a8ba3388ea9",
      "986375f452efe9a804a4928b28ebfc7c858128d9cd3050b0b60560db6a4f79b0"
    ],
    "jobs_dispatched": [
      "64f94555cc454b4119d45fa0a49448e8a6f376fa24b018a44fd3d0413fbd3e50",
      "d07db1826c96af66b78bc21f16b5e7accb70db91267d0ae00cc86a8ba3388ea9",
      "986375f452efe9a804a4928b28ebfc7c858128d9cd3050b0b60560db6a4f79b0"
    ],
    "jobs_failed": [],
    "outcome": "swept",
    "repos_admitted": [
      "tucktuck101/collaboration-repo-template"
    ],
    "repos_refused": [],
    "revisited_resting_jobs": []
  }
}

$ # PHASE 2 — the same optional non-free provider REMOVED from configuration:
   routes = [('local', 'local')]
$ RQA_STATE_DIR=/tmp/rqa-2215/proof/state-ext-off python3 -m rqa.cli tick --repo tucktuck101/collaboration-repo-template
{
  "command": "tick",
  "outcome": "swept",
  "result": {
    "jobs_created": [
      "64f94555cc454b4119d45fa0a49448e8a6f376fa24b018a44fd3d0413fbd3e50",
      "d07db1826c96af66b78bc21f16b5e7accb70db91267d0ae00cc86a8ba3388ea9",
      "986375f452efe9a804a4928b28ebfc7c858128d9cd3050b0b60560db6a4f79b0"
    ],
    "jobs_dispatched": [
      "64f94555cc454b4119d45fa0a49448e8a6f376fa24b018a44fd3d0413fbd3e50",
      "d07db1826c96af66b78bc21f16b5e7accb70db91267d0ae00cc86a8ba3388ea9",
      "986375f452efe9a804a4928b28ebfc7c858128d9cd3050b0b60560db6a4f79b0"
    ],
    "jobs_failed": [],
    "outcome": "swept",
    "repos_admitted": [
      "tucktuck101/collaboration-repo-template"
    ],
    "repos_refused": [],
    "revisited_resting_jobs": []
  }
}

$ # the pins each phase recorded, keyed by the job ids above:
  provider ENABLED  job=64f94555cc454b41…  policy_snapshot=f2e7f784f28127187d4ebc2b…  protocol_hash=82cce34d9446fc7d766f040e597492df5fc4fa89e257eb11d234460a35008598
  provider ENABLED  job=d07db1826c96af66…  policy_snapshot=f2e7f784f28127187d4ebc2b…  protocol_hash=82cce34d9446fc7d766f040e597492df5fc4fa89e257eb11d234460a35008598
  provider ENABLED  job=986375f452efe9a8…  policy_snapshot=f2e7f784f28127187d4ebc2b…  protocol_hash=82cce34d9446fc7d766f040e597492df5fc4fa89e257eb11d234460a35008598
  provider REMOVED  job=64f94555cc454b41…  policy_snapshot=93b55d8fcdf2db80c1b7d5af…  protocol_hash=82cce34d9446fc7d766f040e597492df5fc4fa89e257eb11d234460a35008598
  provider REMOVED  job=d07db1826c96af66…  policy_snapshot=93b55d8fcdf2db80c1b7d5af…  protocol_hash=82cce34d9446fc7d766f040e597492df5fc4fa89e257eb11d234460a35008598
  provider REMOVED  job=986375f452efe9a8…  policy_snapshot=93b55d8fcdf2db80c1b7d5af…  protocol_hash=82cce34d9446fc7d766f040e597492df5fc4fa89e257eb11d234460a35008598
```
*[capture: 11-ac17-provider.txt · commit `b9c98f423` · macOS x86_64 · `tucktuck101/collaboration-repo-template` PUBLIC · state dirs `/tmp/rqa-2215/proof/state-ext-on` and `/tmp/rqa-2215/proof/state-ext-off` · record locators: jobs `64f94555…`, `d07db182…`, `986375f4…` in both phases, listed in full in the pasted JSON. Unelided: this is the complete stdout of both commands.]*

The job ids are **identical across the two phases**, which is the control that makes
the comparison meaningful: job ids are content-addressed over repository and PR
revision, so the same three pull requests at the same three revisions were swept both
times. The only thing that differed was the provider configuration.

**AC17's second half splits into two clauses, and only one of them is demonstrated.**

*Protocol unchanged — demonstrated.* The configuration genuinely changed — the policy
pin moved from `f2e7f784…` to `93b55d8f…` — while `protocol_hash` stayed byte-identical
at `82cce34d…`, and the path stayed runnable (`swept`, three jobs, nothing refused).
That is also the whole of RQA-NFR-014's "enabling then removing an optional non-free
provider leaves that path runnable" clause. The invariance is structural, not a
coincidence of these two configs: `rqa/protocol/version.py:29-40` computes
`protocol_hash()` over exactly two packaged files, `schema/verdict-1.json` and
`PROTOCOL.md`, and reads no configuration at all. The executable half asserts that
property directly (§9's `_protocol_invariance_violations`).

*Semantics unchanged — **not** demonstrated.* "Semantics unchanged" is a claim about
two **verdicts**: what RQA concluded with the provider enabled, and what it concluded
with the provider removed, reduced to concepts and compared. No verdict is produced in
either phase — #2274 and F-2 stop the lifecycle before any harness runs — so there is
nothing to compare, and neither the capture above nor §9 compares it. Note precisely
what §9 does and does not cover: `_protocol_invariance_violations` compares protocol
**identity** across the two provider configs; `_semantic_divergence` does compare
**concepts**, but across two *route identities* on a synthesised payload (that is
AC01's property), never across provider-enabled versus provider-removed. Passing one
clause of a multi-part criterion does not satisfy the criterion, so this half is
reported not demonstrated rather than folded into the first.

**AC17's first half is only partially demonstrated.** The criterion asks that the
active external provider path be "identifiable **before** evidence is sent". Two
observations, and they pull in opposite directions:

- The filter that decides whether an external route may be used,
  `rqa/supply/ladder.py:93-101`, reads `snapshot.external.allowed` and the PR's labels
  from the pinned snapshot, and runs before any harness is invoked. The information is
  available at the right moment in the design.
- But **RQA emits no pre-send provider identification through its operator surface.**
  None of the six commands reports the active provider path, and the `snapshot` record
  row it does write carries only `hash`, `policy_version`, `protocol_hash`, `repo` and
  `activated_at` — no routes, no providers (see §6.7's row dump). An operator deciding
  "may this private repository's content be sent to this provider at all" must read
  `.rqa/config.json` themselves.

And the ordering itself cannot be observed here: under #2274 **no evidence is ever
sent**, so "before evidence is sent" is satisfied vacuously. A vacuous satisfaction is
not a demonstration.

### 6.6 NFR-014 — the component and licence inventory

```
$ grep -rhoE "https?://[A-Za-z0-9._-]+" rqa/ --include=*.py | sort -u
https://api.github.com
https://github.com
$ # …only GitHub. No RQA control plane, no queue broker, no callback host.
$ lsof -nP -iTCP -sTCP:LISTEN | grep -ci rqa || echo "0 listening sockets owned by any rqa process"
0
$ # all durable state is local files under the operator-chosen --state-dir:
$ find /tmp/rqa-2215/proof/state -maxdepth 1
/tmp/rqa-2215/proof/state
/tmp/rqa-2215/proof/state/lock
/tmp/rqa-2215/proof/state/snapshots
/tmp/rqa-2215/proof/state/state.db

$ # every non-stdlib import in rqa/ (AST scan, not a requirements file):
   non-stdlib third-party imports: (none)
$ # and the external binaries it executes:
rqa/authority/capability.py:106
rqa/github/transport.py:112
rqa/record/keychain.py:60
rqa/supply/probe.py:90
rqa/supply/probe.py:98
"gh"
"git"
```
*[capture: 12-nfr-004-014.txt · commit `b9c98f423` · macOS x86_64 · repository: none — a source scan of `rqa/` plus host inspection · record locator: none — no RQA command ran · unelided]*

**Inventory of every component a complete review path needs.** The scan is an AST walk
over every module in `rqa/`, not a reading of a dependency manifest — there is no
dependency manifest, which is itself the result.

| Component | Role | Licence | Free / open source |
|---|---|---|---|
| CPython 3.14.6 | The entire runtime; RQA imports **nothing** outside its standard library | PSF-2.0 | Yes |
| SQLite 3.53.4 | All durable state, via the stdlib `sqlite3` module | Public domain | Yes |
| `gh` (GitHub CLI) 2.100.0 | Credential resolution only — `gh auth token`, `rqa/github/transport.py:106-132` | MIT | Yes |
| `git` 2.52.0 | Repository operations in `rqa/supply/probe.py` | GPL-2.0 | Yes |
| `security` (macOS keychain) | Optional record-HMAC key read; absent item is a successful unkeyed append | Apple system component | No — but **optional and absent in this run** |
| Anthropic via `claude` route | Optional external provider, §6.5 phase 1 | Proprietary service | No — **optional, and removed in phase 2 with the path still runnable** |

Everything in the mandatory path is free and open source. The two non-free entries are
both optional, and both were demonstrated absent or removed with the system still
working. That satisfies NFR-014's clause and its boundary clause.

**NFR-004's "no centrally hosted service".** The only hostnames anywhere in the source
are GitHub's own. No RQA-operated endpoint, control plane, broker or callback host
exists to point at. No `rqa` process holds a listening socket. Every durable artefact
is a file under a directory the operator chose. The `tick` in §6.1 was one
short-lived local process.

### 6.7 What the record actually contains

```
$ sqlite3-equivalent read-only forensics over $RQA_STATE_DIR/state.db
-- every record row for job 1126fea21076c076004da790e5d80952a2ef4981a2540822f1149f81c6810115
   seq=1 kind=transition  keyed=0 hmac=NULL
   seq=2 kind=snapshot    keyed=0 hmac=NULL
   seq=3 kind=grant       keyed=0 hmac=NULL
   seq=4 kind=escalation  keyed=0 hmac=NULL
   seq=5 kind=transition  keyed=0 hmac=NULL

-- the kind:'snapshot' row this job recorded (seq=2), in full
   {
     "activated_at": "2026-09-14T14:49:04.997589+00:00",
     "hash": "51bbd033e4ff56777869dd605a8964553e38f7f2e2e4390714a407d702b9ff9d",
     "policy_version": "unversioned",
     "protocol_hash": "82cce34d9446fc7d766f040e597492df5fc4fa89e257eb11d234460a35008598",
     "repo": "tucktuck101/inTooDeep"
   }

-- of contracts.py's 14 declared entry kinds, which the composed system ever wrote
   transition   WRITTEN
   plan         -- never written --
   carry_over   -- never written --
   bundle       -- never written --
   attestation  -- never written --
   spend        -- never written --
   panel        -- never written --
   judgement    -- never written --
   grant        WRITTEN
   action       -- never written --
   escalation   WRITTEN
   decision     -- never written --
   snapshot     WRITTEN
   legacy       -- never written --

-- keyed column across the whole record (#2272: appended, not keyed)
   keyed=0: 55 rows
```
*[capture: 07-record-forensics.txt · commit `b9c98f423` · macOS x86_64 · job `1126fea2…` · `tucktuck101/inTooDeep` PUBLIC]*

Three things fall out of this dump, and all three matter:

1. **Four of `rqa/contracts.py:524-528`'s fourteen declared entry kinds are ever
   written** by the composed system. The ten that are not are exactly the ten the
   lifecycle would write *after* the authority gate — direct confirmation, from the
   record rather than from code reading, that §5's claim is the whole story and not an
   over-reading of one code path.
2. **`policy_version: "unversioned"` is correct, not a bug.** `rqa onboard` writes
   `policy.version: "unversioned"` from `POLICY_VERSION_DEFAULT`
   (`rqa/policy/validate.py:76`). `config.example.json`'s `"v1"` is an illustrative
   example, not a generated default. Checked before reporting it as a finding; it is
   not one.
3. **The `snapshot` row holds all three pins `explain` reported as `null`.** That is
   Finding F-1, below, and this row is its evidence.

---

## 7. The three known defects, as this run saw them

### 7.1 #2274 — the authority gate can never grant

Covered in [§5](#5-the-blocking-defect-that-shapes-this-entire-proof) and observed in
§6.1, §6.2 and §6.7. Reproduced identically on a PUBLIC and a PRIVATE repository, with
`authority.review: true` in both configs. **Not routed around.**

Newly learned here, and not previously recorded on #2274: fixing it is **necessary but
not sufficient**. A second, independent defect sits immediately behind it, and it is
not confined to `REVIEW` — **all six** of RQA's activities are ungrantable for the
same structural reason. See Finding F-2.

### 7.2 Historical capture — #2272: the record was appended but not keyed

**Historical at commit `b9c98f423`; superseded by ADR-0066 / #2299.** All 55 rows: `keyed=0`, `hmac=NULL` (§6.7). `explain` reported this itself rather than
hiding it: `verified: false`, `hmac_checked: false`,
`unverifiable: [{"reason": "no key", …}]` (§6.2).

Reproduced on this macOS host by perturbing only the harness's view of `sys.platform`.
No file under `rqa/` was modified:

```
$ # #2272, reproduced on this macOS host by perturbing only the harness's view of
$ # sys.platform. rqa/ is not modified. keychain.py:89-92 branches on sys.platform.
  [macOS, sys.platform='darwin'] OSKeyStore().read('rqa-record-hmac') -> None   (item absent -> unkeyed append, keyed=0)
  [harness view forced to sys.platform='linux'] read('rqa-record-hmac') -> raises KeyStoreExplanationUnavailable: no platform keychain command on 'linux'; the record can still be appended unkeyed
  writer.py:118-123 turns exactly that exception into AppendFailed,
  so on any non-darwin platform every record append fails -> #2272.
  Note the internal contradiction: keychain.py:91 says 'the record can still be
  appended unkeyed', while writer.py:119-123 makes it a hard AppendFailed.
```
*[capture: 13-2272-platform.txt · commit `b9c98f423` · macOS x86_64 · repository: none — an in-process probe of `OSKeyStore` · record locator: none — no append was attempted, so no record row exists · unelided]*

The contradiction in the last two lines is worth carrying onto #2272 if it is not
already there: `keychain.py:91`'s own message tells the caller the record can still be
appended unkeyed, and `writer.py:118-123` is the caller that refuses to.

### 7.3 #2273 — no validated milestone-event registry

Confirmed from the record rather than from the architecture. `rqa/record/trace.py:117-138`
accepts a free-form `event` with no registry check, and `CUTOVER.md:548-550` records
that `append_trace` has no caller in `rqa/` at all. The dump in §6.7 is consistent:
no trace-shaped rows exist, and the kinds that do exist are the `Literal` members of
`rqa/contracts.py:524-528`, which is a type annotation rather than a validated
registry.

**Consequence for AC06, stated plainly:** AC06 was judged against what the record
actually contains, never against what the architecture says it should contain. That
is what surfaced Finding F-1.

---

## 8. Criterion-by-criterion verdict

Scope: the criteria this Task (#2215) is judged against. Part 2 adds its own rows for
the ADR paths and the credential floor. Every row's evidence ran on **macOS 15.7.7
x86_64** at commit **`b9c98f423`** with an **unkeyed** record.

| Criterion | Verdict | Evidence | Repositories | If not demonstrated, blocked by |
|---|---|---|---|---|
| **AC16** — two independently configured repos, one public one private, one local operator process, no hosted service | **Partially demonstrated** | §6.1 (both admitted in one sweep), §6.6 (no hosted service) | `inTooDeep` PUBLIC + `agent-trust-platform` PRIVATE | The "different owners or organisations" half: **the credential boundary** (§4). One user, one org, and the org is excluded. A *boundary* limitation, not a *product* one. |
| **RQA-NFR-004** — multiple repositories and organisations, public and private | **Partially demonstrated** | §6.1, §6.6 | as above | Same as AC16. Multiple repositories and both visibilities: yes. Multiple organisations: not run. |
| **AC08** — one command returns the disposition and reason | **Demonstrated** | §6.2 `rqa status`, both repos | `inTooDeep` PUBLIC, `agent-trust-platform` PRIVATE | — |
| **AC06** — one command reconstructs revision, protocol, policy, reviewer identity and type, harness, model, provider, evidence, findings, basis, disposition | **Partially demonstrated** | §6.2 `rqa explain`, §6.7 record dump | both | Field set complete; revision + disposition reconstructed; unverifiability disclosed honestly. **Nine of the twelve** elements empty: seven legitimately (no review ran — **#2274 and F-2**), two (`protocol_hash`, `policy_version`) wrongly `null` — **Finding F-1**, which names a third wrongly-`null` pin, `snapshot_hash`, outside the twelve. See §6.2's counting footnote. |
| **AC02** — policy edit takes effect on the next review with no rebuild/reinstall/redeploy | **Demonstrated** (mechanism clause) | §6.4 — one state dir, no build, new pin `455309fd…` matching the edit exactly | `test_workflow` PUBLIC | — |
| **AC02** — two policies differing only in blocking rules produce different **blocking outcomes** on the same diff | **Not demonstrated** | §6.4 — `jobs_created 0`; no judgement reachable | `test_workflow` PUBLIC | **#2274 and F-2.** A blocking outcome requires a judgement; no review starts, and fixing #2274 alone would not change that. |
| **AC17** — active external provider path identifiable **before** evidence is sent | **Partially demonstrated** | §6.5, §6.7 | `collaboration-repo-template` PUBLIC; the private repo `agent-trust-platform` is what makes it matter | The information exists in the pinned snapshot before any harness call (`ladder.py:93-101`), but no operator-facing command reports it and the `snapshot` record row omits routes (§6.7) — that disclosure gap is **[Finding F-5](#f-5--rqa-never-tells-the-operator-which-provider-path-is-active-before-evidence-is-sent)**, a security gap that survives both #2274 and F-2. And under **#2274 and F-2** no evidence is ever sent, so the ordering is satisfied only vacuously. |
| **AC17** — removing the provider leaves the **protocol** unchanged | **Demonstrated** | §6.5 — policy pin moved `f2e7f784…`→`93b55d8f…` while `protocol_hash` stayed byte-identical, path still runnable; plus §9's `_protocol_invariance_violations` | `collaboration-repo-template` PUBLIC | — |
| **AC17** — removing the provider leaves the **semantics** unchanged | **Not demonstrated** | — | — | **#2274 and F-2.** Semantic invariance means two verdicts compared before and after removal, and **no verdict is ever produced**, so there is nothing to compare. Both the §6.5 capture and §9's `_protocol_invariance_violations` compare protocol identity only; §9's `_semantic_divergence` compares concepts, but across two *route identities* on a synthesised payload (AC01), never across the provider-enabled/provider-removed configs. Two clauses, one criterion: only the first has direct evidence. |
| **RQA-NFR-014** — complete review assembled from free, open-source components; enabling then removing an optional non-free provider leaves the path runnable | **Partially demonstrated** | §6.5 (enable → remove → still runnable), §6.6 (inventory: zero non-stdlib imports) | `collaboration-repo-template` PUBLIC | The inventory and the enable/remove cycle are demonstrated. A **complete review** was not assembled and run, because no review starts — **#2274 and F-2**. |
| **AC01** — same PR through two harness/model/provider routes, same concept semantics | **Not demonstrated** (composed system) | §9 asserts route-independence of the protocol; no live route ran | — | **#2274 and F-2.** Two routes were configured (§6.5 phase 1); neither was ever invoked. |
| **AC14** — submits APPROVED / CHANGES_REQUESTED when obligations are satisfied; cannot manufacture success when they are not | **Not demonstrated** (submission half) | §6.7 — no `action`, `judgement` or `decision` row exists | both | **#2274 and F-2.** No verdict, so no submission; and `approve`/`request_changes` are themselves two of F-2's six ungrantable activities. The *fail-closed* half holds and is asserted in two places — this lane's assurance-arithmetic check plus the **pre-existing** `tests/test_rqa_judgement_judge.py` tests that call `judge()` and assert `disposition != "approve"`; see §9's split table. |
| **AC14 / RQA-FR-029** — one repo configured to merge after review merges, another configured not to does not | **Not demonstrated** | — | — | **#2274**, **F-2** (`merge` is one of the six ungrantable activities) *and* the run boundary (§4): `authority.merge: true` was deliberately never set on a live repository, because a config that could merge a real PR is a GitHub write this run may not perform. All three blocks are real and independent. |
| **DoD row 8** — every claim evidenced by pasted command output | **Demonstrated** | Every §6 subsection. Round 1 of the review gate found captures 10 and 11 pasting prose paraphrases instead of the CLI's JSON; both were re-run and re-captured in full, and §3 records the sweep of all fourteen captures that followed. | — | — |
| **DoD row 9** — re-runnable by someone who did not write it | **Demonstrated** | §2 prerequisites, §3 re-run contract, §6 exact commands in order. The same round-1 finding also broke this row — a reader could not reproduce §6.4 or §6.5 from paraphrased output with no job ids — and the same re-capture restores it: both sections now name their state directory, their onboard step and every job id. | — | — |

### Summary

Of the criteria in this Task's scope: **three demonstrated**, **five partially
demonstrated**, **five not demonstrated**, plus the two DoD process rows demonstrated.
Every "not demonstrated" is attributable to **#2274 *and* F-2 together** — with
AC14/FR-029 additionally constrained by the run's no-writes boundary, and
AC16/NFR-004's organisation clause attributable to the credential boundary alone, not
to any defect.

*The count moved from four "not demonstrated" to five in review round 1.* AC17's
second half was a single row reading "protocol **and semantics** unchanged", marked
Demonstrated on evidence that only ever compared protocol identity. It is now two
rows: protocol unchanged (demonstrated) and semantics unchanged (not demonstrated,
because no verdict is ever produced to compare). Passing one clause of a multi-part
criterion does not satisfy the criterion.

**Two independent defects, not one, stand between this run and most of the PRD.**
#2274 is what the composed system hits first, so it is the denial every capture above
shows. F-2 is what it would hit next: with `repos` wired, all six activities remain
ungrantable and no review still ever starts. An earlier draft of this document
attributed these rows to #2274 alone; that was an under-attribution, and a remediation
plan built on it would have shipped a fix that changed the error message and nothing
else.

---

## 9. The executable half

Live evidence cannot live in CI: the suite runs on Linux with no credentials, and
`tests/conftest.py` replaces `socket.socket` so egress is an error. What *can* live
there is the part of these criteria that is **contract-permanent** — true of every
build, not merely of the build measured on 2026-09-14.

Two files, 25 tests:

| File | Tests | Asserts |
|---|---|---|
| `tests/test_rqa_conformance_lifecycle.py` | 11 | AC08's closed FR-016 vocabulary and that `status` and `explain` never disagree; AC06's twelve reconstruction elements and its trust disclosure; AC05's seven evidence states and the fail-closed assurance core; AC02's live re-read per call; AC17's protocol invariance under provider removal; AC01's single published definition and route-independent semantics. |
| `tests/test_rqa_conformance_lifecycle_mutation.py` | 14 | That each of the above **can fail**. Every check is a pure `_..._violations` helper; the mutation file hands each one a non-conforming system and asserts it reports the violation. |

**Which tests establish the AC05/AC14 fail-closed property — both halves, and only one
half is this lane's.** The property has two parts, and this document would overclaim if
it credited both to the new files:

| Half | Established by | Written by |
|---|---|---|
| The *arithmetic*: an unsatisfied obligation cannot reach full assurance | `_fail_closed_violations` / `test_ac05_an_unsatisfied_obligation_cannot_reach_full_assurance` (`tests/test_rqa_conformance_lifecycle.py`), over an injected assurance callable, across the whole `EvidenceState` vocabulary with `VERIFIED` as the control | this lane |
| The *consumer*: `judge()` will not return `approve` when that shortfall exists | `tests/test_rqa_judgement_judge.py::test_t5_a_required_obligation_with_no_positive_evidence_is_unknown_and_not_approved` (161-169) and `::test_approve_is_unreachable_when_bound_reached_is_true` (276-285), which call `judge()` directly and assert `disposition != "approve"` | **pre-existing suite, not this lane** |

The new tests deliberately do not re-test `judge()`'s disposition selection
(`rqa/judgement/judge.py:373-391`) — that is already covered, and duplicating it would
add a second assertion of one contract rather than close a gap. The safety property is
contract-permanent across the suite as a whole; the split is recorded here so a reader
auditing AC05/AC14 knows to read both files, not just the two this lane added.

**Deliberately not asserted.** No test pins today's broken state. There is no assertion
that `_configured_repositories()` is empty, that `explain` returns `verified: false`,
or that the composition root lacks a `repos` parameter. Those would promote #2274 and
#2272 to permanent contract and force their own deletion by whoever fixes them. The
broken state is recorded above as dated, commit-pinned evidence — that is what §6 and
§7 are for.

**And deliberately not asserted for F-2 either — a judgement call, recorded.** The
obvious candidate test is the fail-closed property behind F-2: *a grant is never
issued on a capability the probe only attested*. It passes today and reads like
permanent contract, since ADR-0062's accepted option (a) requires a grant to rest on a
**proved** capability. It was still not added, because F-2's own fix direction (1)
is to **weaken exactly that floor** — to accept `attested_not_proven` for write
capabilities — and direction (3) is to revisit ADR-0062 outright. A test pinning the
floor would silently pre-judge which of the three remediations is correct and would
have to be deleted by two of them. Asserting a contract that is itself under dispute
is the same Lesson 1 error as asserting a defect, pointed the other way. It stays
recorded evidence in F-2 until the owning Feature decides.

### Mutation verification

Lesson: a guard a demonstrated mutation survives is not a guard. Every mutation
perturbs the **proof harness's view of the world**; none edits `rqa/`.

| Mutation | Regression it represents | Check that fires |
|---|---|---|
| `DISPOSITION["reviewing"] = "in progress"` | A new state's operator-facing answer invented at the render site | `_disposition_vocabulary_violations` |
| Drop `"unable to progress"` from the vocabulary | A disposition quietly removed from the enum | `_disposition_vocabulary_violations` |
| `DISPOSITION_TABLE["escalated"] = "blocked"` | `explain`'s table updated, `status`'s not — one job, two answers | `_disposition_drift` |
| Remove `"merged"` from `DISPOSITION_TABLE` | A state with no reconstruction row; raw internal name shown to an operator | `_disposition_drift` |
| Drop each AC06 element in turn (12 cases) | A refactor removes `provider`, so no outcome can name its provider | `_missing_reconstruction_elements` |
| Drop each trust-disclosure field in turn (4 cases) | `unverifiable` removed — an unauthenticated record reads like an authenticated one | `_missing_trust_disclosure` |
| Add `"assumed"` to the evidence vocabulary | A permissive state lets a reviewer record evidence it never examined | `_evidence_vocabulary_violations` |
| Assurance function that always reports the bar met | **The one this batch exists to catch**: a successful disposition becomes producible with nothing verified | `_fail_closed_violations` |
| Assurance function that always falls short | Fail-closed silently becomes fail-always; every review impossible | `_fail_closed_violations` (its `verified` control) |
| Identical pin across an edit | Config memoised — a policy edit needs a restart | `_policy_reread_violations` |
| Pin never returns to its original value | Pin folds in time or call order; "reproduce what this job ran under" breaks | `_policy_reread_violations` |
| Truncate the config on disk after one good read | Last-known-good served from cache instead of refusing — every AC02 demo becomes meaningless | live `snapshot_for` must return `ValidationFailure` |
| Differing protocol pins across two provider configs | Protocol identity becomes a function of who produced the verdict | `_protocol_invariance_violations` |
| One route's obligation state renamed | Two reviews of one PR stop carrying the same concepts | `_semantic_divergence` |

### Running the gates

```bash
python3 launchpad/skills/review-queue-automation/tests/run_all.py launchpad/skills/review-queue-automation
python3 launchpad/skills/review-queue-automation/architecture/validate.py
cd launchpad/skills/review-queue-automation && python3 -m pytest tests -q
```

At `b9c98f423` before this Task: `PASSED: 1410 test(s)` / `PASS` / `1410 passed`.
After: **1435 / PASS / 1435**. Arithmetic: 1410 + 11 + 14 = 1435.

---

## 10. Findings

Defects this proof found. **No issues were filed from this lane — it performs no
GitHub writes.** Each is written to be filed from this text alone.

### F-1 — `explain` reports `null` for three pins the record demonstrably holds

**Owning behaviour:** the record and reconstruction part (P-12), `rqa/record/explain.py`.
Not #2273, though it was found while testing AC06 against the record rather than
against the architecture, which is what #2273's absence made necessary.

**Observed.** For job `1126fea21076c076004da790e5d80952a2ef4981a2540822f1149f81c6810115`
(`tucktuck101/inTooDeep` #14, PUBLIC), `rqa explain` returns
`protocol_hash: null`, `policy_version: null`, `snapshot_hash: null` (§6.2). The same
job's record row `seq=2, kind='snapshot'` contains all three:
`protocol_hash: "82cce34d9446fc7d766f040e597492df5fc4fa89e257eb11d234460a35008598"`,
`policy_version: "unversioned"`,
`hash: "51bbd033e4ff56777869dd605a8964553e38f7f2e2e4390714a407d702b9ff9d"` (§6.7).
`rqa pending`, reading the same record, reports the snapshot hash correctly (§6.2).

**Cause.** `rqa/record/explain.py:274-277` sources all three pins from the last `plan`
row and only from there. A job that escalates before P-05 plans has no `plan` row, so
all three are `None` — even though the `snapshot` row written at `seq=2` carries
exactly these fields, and the `grant` and `escalation` rows each carry `snapshot_hash`
too. The module's docstring (`explain.py:41-43`) states this provenance rule
deliberately, citing §3.3 step 2.

**Why it matters.** AC06 requires reconstructing "the exact PR revision, **protocol and
policy in force**". For any outcome reached before planning, RQA cannot name the
protocol or policy in force, while its own record can. Reconstruction is strictly
weaker than the record it reads. Two different commands give an operator two different
answers about the same job's policy snapshot.

**Class, enumerated, not just the instance.** Every AC06 element sourced from a record
kind the lifecycle writes only after the gate is unreportable for a pre-gate outcome:
`protocol_hash`, `policy_version`, `snapshot_hash` (from `plan`); `harness`, `model`,
`provider`, `reviewer_identity` (from `attestation`); `evidence`, `findings`,
`decision_basis` (from `judgement`). Of those ten, seven are *legitimately* empty — the
data does not exist. **Three are not**: the data exists in a row `explain` does not
consult. Only those three are this finding.

*These ten are not §6.2's nine, and the difference is deliberate.* §6.2 counts AC06's
own twelve enumerated elements and finds nine empty. This list is the ten *reported
from post-gate record kinds* — it drops `pr_revision` and `disposition` (both from
`transition`, written pre-gate, both populated) and `reviewer_type` (derived, and
populated as `"none"`), and it adds `snapshot_hash`, which is a supporting
trust/rendering field rather than one of AC06's twelve. The overlap is the seven
honestly-empty elements, which appear in both counts.

**Suggested fix direction (not applied):** fall back to the last `snapshot` row's
`protocol_hash` / `policy_version` / `hash` when no `plan` row is in the trusted
prefix. Deciding whether that is the right reading of §3.3 step 2, or whether §3.3
itself should be amended, belongs to the owning Feature.

### F-2 — the authority gate can never grant *any* activity: 6 of 6, even with #2274 fixed

**Owning behaviour:** the authority gate (P-08, `rqa/authority/gate.py`,
`rqa/authority/activities.py`) together with the GitHub capability probe (P-09,
`rqa/github/capability.py`), resting on **ADR-0062** (drafted as
`architecture/adr-drafts/ADR-E.md`). **Distinct from #2274** — different cause,
different fix, and #2274's fix does not address it.

**Observed, live, via the COUNTERFACTUAL probe (§6.3) — not the composed system.**
Through the composed CLI the managed set is always empty (#2274), so this result can
only be obtained by supplying it directly: `Gate(repos={repo})`, the arrangement
`gate.py:107-108` calls "real wiring". Under that **counterfactual** condition the gate
still denies: `Deny(capability_missing)`, `detail: "the credential cannot review on
tucktuck101/inTooDeep: missing ['issues:write']"`. GitHub reports the same credential
as `{"admin":true,"maintain":true,"pull":true,"push":true,"triage":true}` on that
repository, with token scopes `'gist', 'project', 'read:org', 'repo', 'workflow'`.

The counterfactual is how the *live* half of this finding was obtained and it justifies
no verdict on its own. The finding does not rest on it: the enumeration below is
hermetic set arithmetic over the product's own published constants, needs no probe, no
credential and no repository, and holds for the composed system exactly as shipped.

**The class, enumerated.** The live probe above exercises one activity. Reporting only
that instance would understate the defect by a factor of six. Enumerating every member
of `REQUIRED_CAPABILITY` against the best case any credential can ever achieve:

```
max provable capabilities, any credential/repo/platform : ['checks:read', 'contents:read', 'pulls:read']
only ever attested_not_proven                           : ['contents:write', 'issues:write', 'pulls:write']

activity          required                                                     residue after best-case proof
review            ['checks:read', 'contents:read', 'issues:write', 'pulls:read'] ['issues:write']
comment           ['pulls:write']                                              ['pulls:write']
approve           ['pulls:write']                                              ['pulls:write']
request_changes   ['pulls:write']                                              ['pulls:write']
remediate         ['contents:write']                                           ['contents:write']
merge             ['contents:write', 'pulls:write']                            ['contents:write', 'pulls:write']

ACTIVITIES THAT CAN NEVER BE GRANTED: ['review', 'comment', 'approve', 'request_changes', 'remediate', 'merge']
count: 6 of 6
```
*[commit `b9c98f423` · macOS x86_64 · hermetic: set arithmetic over the two modules' own published constants, no network, no credential, no repository]*

The residue is non-empty for **every** activity, so the result holds for every
credential, every repository and every platform — not merely for the one probed above.
**The gate is structurally incapable of granting anything.**

**Cause — structural, not credential-specific.** Three links, all verified at source:
- `rqa/github/capability.py:70-77` — the **only** statement that ever adds to `proven`
  is `if permissions.get("pull"): proven |= _READ_CAPABILITIES` (line 72-73), and
  `_READ_CAPABILITIES` (line 34) is exactly the three reads. Write capabilities reach
  `attested` only, via `_PUSH_CAPABILITIES` (line 36) and `_TRIAGE_CAPABILITIES`
  (line 38). The module docstring (lines 15-20) states this deliberately: *"Write
  capabilities are only ever attested_not_proven: GitHub's `permissions` block reports
  them, but the probe never writes to prove one."*
- `rqa/authority/gate.py:236` — `missing = REQUIRED_CAPABILITY[activity] - proof.capabilities`
  subtracts `proof.capabilities` **only**; `attested_not_proven` is never consulted.
- `rqa/authority/activities.py:29-36` — **all six** activities require at least one
  write capability, not just `REVIEW`.

**This is an unsatisfiable requirement pair, not an implementation slip.** ADR-0062's
accepted option (a) (`architecture/adr-drafts/ADR-E.md:28`) requires that P-08 *"grants
an activity only when the pinned snapshot grants it **and** a per-job capability probe
(E-16) **proves** the `gh auth token` can perform it on that repository"*. The same
decision records write capability as attested-not-proven precisely because **proving a
write would mean performing one** — and E-16 is specified read-only and needing no
grant (`capability.py:1-7`). For any activity that is itself a write, no
implementation can satisfy both halves at once. Every one of RQA's six activities is,
or entails, a write.

That is the class of defect a conformance proof exists to surface: each half is
individually reasonable, each was reviewed and accepted, and their conjunction is
empty. Code review of either module in isolation would not find it, and did not.

**Programme consequence, in one sentence.** #2274 is necessary but **not sufficient** —
wiring `repos` moves every denial from `REPO_NOT_MANAGED` to `CAPABILITY_MISSING` and
no review still ever starts, so any plan to close PRD #2006 by fixing #2274 alone is
wrong.

**Suggested fix direction (not applied).** Three readings, and the choice is the owning
Feature's because they differ in what they assert about ADR-0062's floor:
1. `gate.py:236` checks `proof.capabilities | proof.attested_not_proven` for write
   capabilities, accepting ADR-0062's recorded attested-not-proven residual as
   sufficient for a grant. This weakens the floor ADR-0062 §(a) set.
2. `REQUIRED_CAPABILITY` is re-derived so each activity requires only what E-16 can
   prove, with the write expectation carried in the `attestation` entry instead.
3. ADR-0062 is revisited, since its two clauses cannot both hold. This is the honest
   option if the floor is meant to stay as written.

Whichever is chosen, the fix must be evaluated against **all six** activities; a change
validated only against `REVIEW` leaves five ungrantable.

### F-3 — `keychain.py` promises an unkeyed append that `writer.py` refuses to make

> **RESOLVED by ADR-0066 / #2299.** The contradiction below is gone because both sides
> of it are gone: `rqa/record/keychain.py` is deleted and `append` no longer has a
> credential-store branch at all. Every append is unkeyed on every platform, so there is
> no message promising a recovery and no caller refusing it. The observation is kept
> verbatim as the record of what the #2189 conformance run actually saw.

**Owning behaviour:** the record part (P-12), `rqa/record/keychain.py` and
`rqa/record/writer.py`. **Carry onto #2272** if not already there, rather than filing
separately: it is the same defect seen from inside.

**Observed (§7.2).** On a non-darwin platform, `OSKeyStore.read()` raises
`KeyStoreExplanationUnavailable("no platform keychain command on 'linux'; **the record
can still be appended unkeyed**")`. Its caller, `rqa/record/writer.py:118-123`, catches
exactly that exception and raises `AppendFailed`. The error message tells the caller a
recovery is available; the only caller refuses it. Whichever side is wrong, the two
must be made to agree as part of fixing #2272, or the fix will look complete while the
message still misdescribes the behaviour.

### F-4 — pre-existing issues confirmed by this run, not re-filed

- **#2233** (`snapshots.repo` cannot hold what the DDL describes) — observed directly:
  the `snapshots` table's `repo` column is empty for every activated row, while the
  record's `snapshot` entry carries the repository correctly (§6.7). No new issue.
- **#2260** (escalation specificity unenforced) — the escalation in §6.2 is specific,
  but by its call site's construction, not by validation. Flagged inline so the pasted
  output is not misread as evidence of enforcement.

### F-5 — RQA never tells the operator which provider path is active before evidence is sent

**Owning behaviour:** the operator command surface (`rqa/cli/main.py`) together with
the record's `snapshot` entry (P-12, `rqa/record/writer.py` via
`rqa/policy/snapshot.py:209-219`). Not #2274, not F-2: this gap would remain after
both are fixed, and it is the only finding here that is a **security** gap rather than
a correctness one.

**Why it is a security gap, in the PRD's own words.** CL-059, the Security
implications clause behind AC17 and RQA-NFR-023/029: *"External providers receive
repository content. The active provider path must be identifiable before evidence is
sent, so an operator can decide whether a given repository or change may be sent at
all. Private repositories under AC16 make this a per-repository decision, not a global
one."* The decision that clause protects is precisely the one an operator of a private
repository has to make, and this run used a private repository
(`tucktuck101/agent-trust-platform`).

**Observed.** Two things, both from this run:
- **No command reports it.** RQA's surface is exactly six commands
  (`tick`, `onboard`, `status`, `pending`, `decide`, `explain` — `rqa/cli/main.py:90-134`).
  None of them answers "which provider would this repository's content be sent to?".
  An operator must open `.rqa/config.json` and read `routes` and `external` themselves
  — that is the operator inspecting their own input, not RQA identifying its active
  path.
- **The record does not carry it either.** The `snapshot` entry written for every job
  carries exactly `activated_at`, `hash`, `policy_version`, `protocol_hash`, `repo`
  (§6.7's full row dump). No routes, no providers, no `external.allowed`. So the
  active provider path is not identifiable *after* the fact from the record either,
  only re-derivable by re-reading a config file that may since have changed.

**What does exist, so the finding is not overstated.** The information is present in
the pinned `Snapshot` object at the right moment: `rqa/supply/ladder.py:93-101` filters
external routes out of the candidate set using `snapshot.external.allowed` and the PR's
labels, and that runs before any harness invocation. The mechanism is in place; the
*disclosure* is not. Nothing surfaces it to the operator before the send, and nothing
durably records which path was active.

**Why this run cannot report the ordering as satisfied.** Under #2274 and F-2 no
evidence is ever sent at all, so "identifiable before evidence is sent" is true only
vacuously. A vacuous satisfaction is not a demonstration, which is why the AC17 row in
§8 reads *partially demonstrated* and cites this finding.

**Suggested fix direction (not applied):** the smaller half is to add the configured
routes — or at minimum the set of distinct `(provider, external)` pairs — to the
`snapshot` record entry, making the active path reconstructable after the fact by
`explain`. The larger half is a pre-send disclosure on the operator surface. Which of
the two (or both) AC17 demands is the owning Feature's reading to make.

---

<!-- Part 2 (Task #2216) appends below this line. Do not edit above it. -->

---

# Part 3 — completion run after the Part 1 blockers were corrected

Part 1 is preserved as the record of the system before its findings were corrected.
This addendum records the first composed run that crossed the authority gate, invoked
reviewers, submitted authoritative GitHub reviews, and exercised both merge settings.

## 11. Run identity and prerequisites

Every command in this part ran from `/private/tmp/rqa-2215-final/repos` on one local
operator machine. RQA itself ran in process; there was no hosted RQA service.

```text
$ git -C /private/tmp/rqa-conformance-final rev-parse 879696b58
879696b583268e6a0c47d8e3655b4f50c913290c
$ uname -a
Darwin Jeffs-MacBook-Pro.local 24.6.0 Darwin Kernel Version 24.6.0: Tue Apr 21 20:17:54 PDT 2026; root:xnu-11417.140.69.710.16~1/RELEASE_X86_64 x86_64
$ sw_vers
ProductName:		macOS
ProductVersion:		15.7.7
BuildVersion:		24G720
$ python3 -V
Python 3.14.6
$ gh --version | head -1
gh version 2.100.0 (2026-09-03)
$ git --version
git version 2.52.0
```

The run needs Python 3.11+, an authenticated `gh`, controlled test pull requests,
the checked-out RQA source, and the repository-local configs shown below. The two
review routes are external-command adapters that run
`tests/test_rqa_conformance_harness_command.py`; they use only Python's standard
library. RQA and the harness are Apache-2.0 under the repository `LICENSE`. GitHub
remains the reviewed host; it is not an RQA hosting service.

The exact environment was:

```bash
export PYTHONPATH=/private/tmp/rqa-conformance-final/launchpad/skills/review-queue-automation
export RQA_STATE_DIR=<the state directory named with each capture>
cd /private/tmp/rqa-2215-final/repos
python3 -m rqa.cli tick --repo <owner/repository> --batch-size 1
```

| Repository | Owner boundary | Visibility | Head | Role |
|---|---|---|---|---|
| `launchpad-26/solo-repo-template#3` | `launchpad-26` organisation | PRIVATE | `49698900d8d24cba6e5eb6ca25b7a292307e45bb` | same-diff policy differentiation; merge disabled |
| `tucktuck101/collaboration-repo-template#3` | `tucktuck101` user | PUBLIC | `50ea9c46dcf4c52fab742821b4fa4d931c8e5260` | two free/local reviewer routes; merge disabled |
| `tucktuck101/agent-trust-platform#107` | `tucktuck101` user | PRIVATE | `efa61025874f1ce4bb0a693bef3108eaa5de3565` | two free/local reviewer routes; merge enabled |

This supplies two genuinely different owners, both visibilities, and one operator
process. Temporary assignment was the lease; every final GitHub observation below
shows an empty assignee list.

## 12. AC02 — the same diff under two blocking policies

The two configs have identical policy versions, routes, obligations, authority, and
budgets. This is their complete diff:

```diff
--- private-block.json
+++ private-allow-blocking-only.json
@@ -24,9 +24,7 @@
       "standard": 2
     },
     "blocking": {
-      "categories": [
-        "procedural"
-      ],
+      "categories": [],
       "corroboration": 2,
       "severities": []
     },
```

The blocking run used
`RQA_STATE_DIR=/private/tmp/rqa-2215-final/state-private-block-fixed`:

```text
$ python3 -m rqa.cli tick --repo launchpad-26/solo-repo-template --batch-size 1
{
  "command": "tick",
  "outcome": "swept",
  "result": {
    "jobs_created": [
      "c01a2585ab9608d55b4ac628c6d1d39ed8e12cececb469b422579526810bab78",
      "0ec215708b9857f24739fbd39473b702b24ad445ce6f7773e658cbe4616330dd",
      "0838ca605abcb95355aeb9eb7f4c93f4e9e6c9cb844e891a8fcba296973ee1b4"
    ],
    "jobs_dispatched": [
      "c01a2585ab9608d55b4ac628c6d1d39ed8e12cececb469b422579526810bab78"
    ],
    "jobs_failed": [],
    "outcome": "swept",
    "repos_admitted": ["launchpad-26/solo-repo-template"],
    "repos_failed": [],
    "repos_refused": [],
    "revisited_resting_jobs": []
  }
}
$ python3 -m rqa.cli status launchpad-26/solo-repo-template 3
{
  "command": "status",
  "outcome": "ok",
  "result": {
    "disposition": "blocked",
    "internal_state": "changes_requested",
    "job_id": "c01a2585ab9608d55b4ac628c6d1d39ed8e12cececb469b422579526810bab78",
    "reason": "review submitted: request_changes"
  }
}
```

The next review used the edited config directly, with no build, install, restart, or
deployment, and a fresh
`RQA_STATE_DIR=/private/tmp/rqa-2215-final/state-private-allow-blocking-only`:

```text
$ python3 -m rqa.cli tick --repo launchpad-26/solo-repo-template --batch-size 1
{
  "command": "tick",
  "outcome": "swept",
  "result": {
    "jobs_created": [
      "c01a2585ab9608d55b4ac628c6d1d39ed8e12cececb469b422579526810bab78",
      "0ec215708b9857f24739fbd39473b702b24ad445ce6f7773e658cbe4616330dd",
      "0838ca605abcb95355aeb9eb7f4c93f4e9e6c9cb844e891a8fcba296973ee1b4"
    ],
    "jobs_dispatched": [
      "c01a2585ab9608d55b4ac628c6d1d39ed8e12cececb469b422579526810bab78"
    ],
    "jobs_failed": [],
    "outcome": "swept",
    "repos_admitted": ["launchpad-26/solo-repo-template"],
    "repos_failed": [],
    "repos_refused": [],
    "revisited_resting_jobs": []
  }
}
$ python3 -m rqa.cli status launchpad-26/solo-repo-template 3
{
  "command": "status",
  "outcome": "ok",
  "result": {
    "disposition": "review-complete",
    "internal_state": "approved",
    "job_id": "c01a2585ab9608d55b4ac628c6d1d39ed8e12cececb469b422579526810bab78",
    "reason": "review submitted: approve"
  }
}
```

The same job id and revision produced different authoritative outcomes because only
the blocking category changed. Both routes reported the same procedural finding; it
was blocking in the first judgement and non-blocking in the second.

## 13. AC01, AC06, AC08 and AC14 — two routes and offline reconstruction

The public run used
`RQA_STATE_DIR=/private/tmp/rqa-2215-final/state-public-local` and required two
participants:

```text
$ python3 -m rqa.cli tick --repo tucktuck101/collaboration-repo-template --batch-size 1
{
  "command": "tick",
  "outcome": "swept",
  "result": {
    "jobs_created": [
      "64f94555cc454b4119d45fa0a49448e8a6f376fa24b018a44fd3d0413fbd3e50",
      "d07db1826c96af66b78bc21f16b5e7accb70db91267d0ae00cc86a8ba3388ea9",
      "986375f452efe9a804a4928b28ebfc7c858128d9cd3050b0b60560db6a4f79b0"
    ],
    "jobs_dispatched": [
      "64f94555cc454b4119d45fa0a49448e8a6f376fa24b018a44fd3d0413fbd3e50"
    ],
    "jobs_failed": [],
    "outcome": "swept",
    "repos_admitted": ["tucktuck101/collaboration-repo-template"],
    "repos_failed": [],
    "repos_refused": [],
    "revisited_resting_jobs": []
  }
}
$ python3 -m rqa.cli status tucktuck101/collaboration-repo-template 3
{
  "command": "status",
  "outcome": "ok",
  "result": {
    "disposition": "review-complete",
    "internal_state": "approved",
    "job_id": "64f94555cc454b4119d45fa0a49448e8a6f376fa24b018a44fd3d0413fbd3e50",
    "reason": "review submitted: approve"
  }
}
$ python3 -m rqa.cli explain job 64f94555cc454b4119d45fa0a49448e8a6f376fa24b018a44fd3d0413fbd3e50
{
  "command": "explain",
  "outcome": "ok",
  "result": {
    "decision_basis": "# Judgement\\u000a\\u000a## Obligations\\u000a- `O1`: verified\\u000a\\u000a## Findings\\u000a- `RQA-CONFORMANCE-MARKER` [non-blocking] categories=procedural provenance=`attempt=64f94555cc454b4119d45fa0a49448e8a6f376fa24b018a44fd3d0413fbd3e50:03` evidence=`The diff updates a GitHub workflow action or carries the explicit conformance marker.`\\u000a- `RQA-CONFORMANCE-MARKER` [non-blocking] categories=procedural provenance=`attempt=64f94555cc454b4119d45fa0a49448e8a6f376fa24b018a44fd3d0413fbd3e50:06` evidence=`The diff updates a GitHub workflow action or carries the explicit conformance marker.`\\u000a\\u000a## Inherited check attribution\\u000a- `Repository check`\\u000a\\u000a## Assurance\\u000a- required=2 achieved=2\\u000a\\u000a## Reused from\\u000a- (none)",
    "disposition": "review-complete",
    "escalation_subjects": [],
    "evidence": {"O1": "verified"},
    "findings": [
      {"behaviour_changing": false, "blocking": false, "categories": ["procedural"], "corroborated": true, "evidence": "The diff updates a GitHub workflow action or carries the explicit conformance marker.", "extra_tags": ["conformance"], "id": "RQA-CONFORMANCE-MARKER", "location": {"line": 1, "path": "RQA-CONFORMANCE.md"}, "remedy": null, "severity": "low", "source_attempt": "64f94555cc454b4119d45fa0a49448e8a6f376fa24b018a44fd3d0413fbd3e50:03"},
      {"behaviour_changing": false, "blocking": false, "categories": ["procedural"], "corroborated": true, "evidence": "The diff updates a GitHub workflow action or carries the explicit conformance marker.", "extra_tags": ["conformance"], "id": "RQA-CONFORMANCE-MARKER", "location": {"line": 1, "path": "RQA-CONFORMANCE.md"}, "remedy": null, "severity": "low", "source_attempt": "64f94555cc454b4119d45fa0a49448e8a6f376fa24b018a44fd3d0413fbd3e50:06"}
    ],
    "harness": ["rqa-foss-a", "rqa-foss-b"],
    "hmac_checked": false,
    "job_id": "64f94555cc454b4119d45fa0a49448e8a6f376fa24b018a44fd3d0413fbd3e50",
    "legacy": false,
    "model": ["deterministic-1", "deterministic-2"],
    "number": 3,
    "policy_version": "conformance-public-local",
    "pr_revision": "50ea9c46dcf4c52fab742821b4fa4d931c8e5260",
    "protocol_hash": "82cce34d9446fc7d766f040e597492df5fc4fa89e257eb11d234460a35008598",
    "provider": ["local-python-a", "local-python-b"],
    "repo": "tucktuck101/collaboration-repo-template",
    "reviewer_identity": ["rqa-foss-a", "rqa-foss-b"],
    "reviewer_type": "ai",
    "snapshot_hash": "8f9e0c03dc36e1000548532b77c5910e3f7095b1db2785d7ede87cf58915400a",
    "truncated_at": null,
    "unverifiable": [{"first_seq": 1, "job_id": "64f94555cc454b4119d45fa0a49448e8a6f376fa24b018a44fd3d0413fbd3e50", "last_seq": 26, "reason": "no key"}],
    "verified": false
  }
}
```

The two attested attempts carry the same obligation and finding concepts while naming
different harnesses, models, providers, families, and attempt ids. The `hmac_checked`
and `unverifiable` fields record the implementation at commit `879696b58`; ADR-0066
and #2299 remove those obsolete fields for later runs rather than changing this output.

## 14. Merge disabled and merge enabled

The successful public and private-policy runs above had `authority.merge=false` and
remained open. The otherwise successful merge case used
`RQA_STATE_DIR=/private/tmp/rqa-2215-final/state-merge` with
`authority.merge=true`:

```text
$ python3 -m rqa.cli tick --repo tucktuck101/agent-trust-platform --batch-size 1
{
  "command": "tick",
  "outcome": "swept",
  "result": {
    "jobs_created": [
      "6b4f93aeb1ca1b5ba919236e2e21fe821f295bdbf5348c72889284c3938b8ff8",
      "61e931c37f810d4d8b1c05ca48eefe5127e42733170645cc76b8d9087d53d271"
    ],
    "jobs_dispatched": [
      "6b4f93aeb1ca1b5ba919236e2e21fe821f295bdbf5348c72889284c3938b8ff8"
    ],
    "jobs_failed": [],
    "outcome": "swept",
    "repos_admitted": ["tucktuck101/agent-trust-platform"],
    "repos_failed": [],
    "repos_refused": [],
    "revisited_resting_jobs": []
  }
}
$ python3 -m rqa.cli status tucktuck101/agent-trust-platform 107
{
  "command": "status",
  "outcome": "ok",
  "result": {
    "disposition": "review-complete",
    "internal_state": "merged",
    "job_id": "6b4f93aeb1ca1b5ba919236e2e21fe821f295bdbf5348c72889284c3938b8ff8",
    "reason": "merged under merge grant"
  }
}
```

The trace captures the two routes followed by the separately gated review and merge
mutations, then lease release:

```json
{"at":"2026-09-16T03:05:01.918144+00:00","event":"route_selection","job":"6b4f93aeb1ca1b5ba919236e2e21fe821f295bdbf5348c72889284c3938b8ff8","routes":[{"family":"local-a","harness":"rqa-foss-a","model":"deterministic-1","provider":"local-python-a"},{"family":"local-b","harness":"rqa-foss-b","model":"deterministic-2","provider":"local-python-b"}],"truncated":false,"unrouted":false}
{"at":"2026-09-16T03:05:02.115191+00:00","event":"mutation","job":"6b4f93aeb1ca1b5ba919236e2e21fe821f295bdbf5348c72889284c3938b8ff8","kind":"submit_review","state":"APPROVE"}
{"at":"2026-09-16T03:05:05.178779+00:00","event":"mutation","job":"6b4f93aeb1ca1b5ba919236e2e21fe821f295bdbf5348c72889284c3938b8ff8","kind":"merge"}
{"at":"2026-09-16T03:05:11.727013+00:00","event":"lease_released","job":"6b4f93aeb1ca1b5ba919236e2e21fe821f295bdbf5348c72889284c3938b8ff8","mutation_id":"c07031d5f2b735b0ee06b9a26f88a25192f0e7a6d939eac6dd0e568dd2ea4c3c"}
```

Final GitHub observations, captured after all runs:

```text
{"assignees":[],"headRefOid":"49698900d8d24cba6e5eb6ca25b7a292307e45bb","mergedAt":null,"repo":"launchpad-26/solo-repo-template","review_states":["CHANGES_REQUESTED","APPROVED","APPROVED"],"state":"OPEN","visibility":"PRIVATE"}
{"assignees":[],"headRefOid":"50ea9c46dcf4c52fab742821b4fa4d931c8e5260","mergedAt":null,"repo":"tucktuck101/collaboration-repo-template","review_states":["APPROVED","APPROVED"],"state":"OPEN","visibility":"PUBLIC"}
{"assignees":[],"headRefOid":"efa61025874f1ce4bb0a693bef3108eaa5de3565","mergeCommit":"94fbc14b69e71edb1c3e75211f0456093f34587a","mergedAt":"2026-09-16T03:05:07Z","repo":"tucktuck101/agent-trust-platform","review_states":["APPROVED"],"state":"MERGED","visibility":"PRIVATE"}
```

## 15. Optional external provider enable/remove boundary

The configured-provider and removed-provider snapshots validate against the same
protocol. This command constructs snapshots only; it does not build a review bundle,
invoke a harness, or send repository content:

```text
$ PYTHONPATH=/private/tmp/rqa-conformance-final/launchpad/skills/review-queue-automation python3 -c 'import json,pathlib; from rqa.policy.snapshot import digest_of,snapshot_from_unverified_config; from rqa.protocol import protocol_hash; p=protocol_hash();
for label,path in (("provider-enabled","/private/tmp/rqa-2215-final/configs/public-external-configured.json"),("provider-removed","/private/tmp/rqa-2215-final/configs/public-external-removed.json")):
 raw=json.loads(pathlib.Path(path).read_text()); snap=snapshot_from_unverified_config(raw=raw,digest=digest_of(raw),repo="tucktuck101/collaboration-repo-template",protocol=p); print(label,"snapshot="+snap.hash,"protocol="+snap.protocol_hash,"external_allowed="+str(snap.external.allowed),"routes="+repr([(r.provider,r.external) for r in snap.routes]))'
provider-enabled snapshot=aa867bcc77d11e8ea8e668d610f902dcde340d04661f620eec26a2e68e575c59 protocol=82cce34d9446fc7d766f040e597492df5fc4fa89e257eb11d234460a35008598 external_allowed=True routes=[('local-python-a', False), ('openai', True)]
provider-removed snapshot=dcd7a495e7ac45394399ecf80353e8fa97d3e1f8612b853dd6d1e829e316760b protocol=82cce34d9446fc7d766f040e597492df5fc4fa89e257eb11d234460a35008598 external_allowed=False routes=[('local-python-a', False)]
```

After removal, the `state-public-external-removed` run completed and posted approval
with `O1=verified`, policy `conformance-public-external-removed`, provider
`local-python-a`, and protocol
`82cce34d9446fc7d766f040e597492df5fc4fa89e257eb11d234460a35008598`.
The full two-route free/open-source run in §13 then produced the same obligation and
finding semantics under that protocol.

No OpenAI tick was required or executed. AC17 makes an external provider optional: the
configured snapshot identifies the provider path before any possible send, while the
removed snapshot proves that the same protocol remains active without it. The
removed-provider run and the two-route free/open-source run then complete reviews with
the same `O1=verified` concept semantics. This demonstrates provider removal without
sending repository content to the optional provider.

## 16. Completion matrix for Task #2215

| Criterion | Result | Direct evidence |
|---|---|---|
| Public repository in one owner and private repository in another; one local operator; no hosted RQA | Demonstrated | §11, §12, §13 |
| End-to-end authoritative outcome plus `status` and offline `explain` | Demonstrated | §12, §13 |
| Same diff, blocking-only policy edit, different blocking outcome, no redeploy | Demonstrated | §12 |
| Same PR through two harness/model/provider routes with the same concepts | Demonstrated | §13 |
| Complete review using only free/open-source components and standard library | Demonstrated | §11, §13 |
| Merge-enabled repository merges; merge-disabled repositories stay open | Demonstrated | §14 |
| External provider identified in config before any possible send; removal leaves protocol and local path runnable | Demonstrated | §15 |
| Every claim backed by command output and repeatable identifiers | Demonstrated for every completed row | §11–§15 |

The live run also found and fixed a GraphQL boundary defect before these results were
recorded: `addPullRequestReview` accepts `event:REQUEST_CHANGES`; the implementation
had used the returned review-state spelling `CHANGES_REQUESTED`. The invalid mutation
failed closed and posted no review. Commit `879696b58` corrects the fixed literal and
adds a regression assertion for both the accepted and rejected spellings.

## 17. Validation of the recorded implementation

```text
$ python3 launchpad/skills/review-queue-automation/tests/run_all.py launchpad/skills/review-queue-automation
repo inventory unavailable: o/r: GithubUnavailable(op='inventory', reason='unreachable', retriable=True)
repo inventory unavailable: o/r: GithubUnavailable(op='inventory', reason='unauthenticated', retriable=False)
PASSED: 1498 test(s)
$ python3 launchpad/skills/review-queue-automation/architecture/validate.py
parts 13 · requirements 86 · units 162 · records 20 · edges 26 · ADRs 5 · constraints 22 · states 13 · code contracts 13
PASS
$ python3 launchpad/skills/review-queue-automation/requirements/validate.py
PASS
- 86 requirements: 14 business, 39 functional, 33 non-functional
- 65 clauses, 95 requirement→clause edges, 26 split clauses
- 774 QA judgements (9 per requirement), all verdicts match the frozen baseline
- every candidate field byte-matches commit 9267b6308's statement/fit/EARS/priority/status/ADR/source-clause/quote
- both traceability directions hold; note-cell equality holds; every relative link resolves
```
