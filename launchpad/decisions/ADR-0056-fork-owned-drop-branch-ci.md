---
status: Accepted
date: 2026-08-31
issue: launchpad-26/buzz#299
decided_in: launchpad-26/buzz#299
supersedes: ADR-0039
---

# ADR-0056 — A fork-owned workflow runs CI on the vendor-drop branch

## Decision

The vendor-drop pull request is opened by the scheduled job using the Actions
`GITHUB_TOKEN`, and CI is provided by a **fork-owned workflow** —
`.github/workflows/launchpad-vendor-drop-ci.yml` — that triggers on `push` to the drop
branch namespace (`sync-upstream-**`) rather than on `pull_request`.

No GitHub App is created or installed, and no personal access token is used.

This supersedes [ADR-0039](./ADR-0039-app-token-authors-drop-pr.md), which chose a GitHub
App installation token. That option is not rejected on merit — it remains the standard
answer to the underlying problem — but it is **not executable under this project's
constraints**: installing an App on an org-owned repository is an org-owner action, and
org-level permissions are out of scope for the Buzz project.

**What carries over from ADR-0039 unchanged:**

- The problem statement. A pull request opened with the Actions `GITHUB_TOKEN` triggers no
  `pull_request` workflow runs, and `.github/workflows/ci.yml` triggers only on
  `push: [main, release]` plus `pull_request:`. A drop pull request opened by the obvious
  implementation therefore arrives with **zero checks**, and merging untrusted upstream
  content unchecked is the outcome this decision exists to prevent.
- The refusal of a personal access token, on [ADR-0008](./ADR-0008-security-audit-privilege.md)'s
  grounds: *"a PAT held by a person outlives that person and is a standing liability on a
  public repo"*.
- The refusal to edit upstream's `ci.yml` triggers. That file already conflicts on
  vendor drops, and deepening its divergence to obtain CI would buy a recurring merge cost
  for a one-off need.
- **Authorship confers no approval.** Nothing here lets an automated identity approve or
  merge its own work, and nothing here permits a push to `main`, which stays with the named
  humans in [ADR-0038](./ADR-0038-named-humans-advance-vendor-branch.md).

**Why a fork-owned workflow rather than an edit to upstream's.**
[ADR-0043](./ADR-0043-prefer-fork-owned-overrides.md) sets the fork's default: a
fork-owned file that overrides, wraps or delegates to upstream's, never an in-place edit
where an override is available. A new `launchpad-*.yml` workflow is exactly that shape, and
the fork already carries ten such workflows, so the mechanism is established rather than
invented here.

## Context

Issue #299 was decided on 2026-08-31 in favour of an App token, and the constraint that
org-level permissions are out of scope was stated by Jeffrey later the same day. The
decision was therefore reopened rather than left standing as an instruction nobody could
execute.

Measured on 2026-08-31 against `launchpad`:

- `.github/workflows/ci.yml` triggers are `push: branches: [main, release]` and
  `pull_request:` — confirmed by reading the file.
- Ten `launchpad-*.yml` workflows already exist in `.github/workflows/`, so a fork-owned
  workflow is the repository's normal way to add cohort CI.

## Consequences

- Drop pull requests are accompanied by check results, and the unattended path in PRD
  #273's second success criterion survives: the schedule still pushes the branch and opens
  the pull request with no human involvement.
- No credential is created, installed or stored by this decision. The credential surface
  stays at zero, which is a stronger position than ADR-0039's and is the one genuine
  improvement in this record rather than a compromise.
- **Check results attach to the branch push, not to the pull request.** A reviewer sees
  them on the commit rather than in the pull request's own check list, which is weaker
  presentation than a `pull_request`-triggered run. This is the real cost of the option and
  it is accepted knowingly.
- The fork-owned workflow must reproduce or call the check set that matters for a vendor
  drop. It is a second place where that set is named, so it can drift from `ci.yml`.
  Calling `ci.yml`'s reusable jobs where possible, rather than copying steps, is the way to
  bound that; the implementing task owns the choice.
- **Gating is still out of reach, exactly as ADR-0039 recorded.** This settles whether
  checks *run*, not whether they *gate*.
  [ADR-0019](./ADR-0019-review-checks-gate-only-when-deterministic.md) records that zero
  required status checks are configured. Making a check required is a branch-protection
  change — repository admin, not org — so it remains available in principle and is tracked
  separately (#153, #154); it is not delivered here.
- **Task #541 does not cover this record's mechanism.** Its acceptance criteria must gain
  the fork-owned drop-branch CI workflow and the `sync-upstream-**` branch namespace, or
  the work must be filed separately under Feature #525. This record does not claim it
  creates no implementation work.

## Security implications

The drop branch carries untrusted upstream content, and this decision means CI executes
that content on the cohort's runners — which is the reviewed, intended posture, and the
alternative is merging it unread. Two properties bound it:

- The workflow runs on a `push` to a branch the scheduled job created, not on a
  `pull_request` from a fork, so it does not introduce a `pull_request_target`-style
  elevated-trust path. It must not be given one.
- Its `permissions:` block should be the least needed to report status — `contents: read`
  — and it must hold no secret it does not need. A workflow that runs untrusted code is
  the wrong place for a credential of any kind.

Relative to ADR-0039 this is a net reduction in trust surface: there is no App, no
installation, no private key held as an Actions secret, and nothing to rotate or revoke.

## Supersedes

[ADR-0039](./ADR-0039-app-token-authors-drop-pr.md) — a GitHub App installation token
authors the vendor-drop pull request. Superseded because org-level permissions are out of
scope for this project, not because the reasoning was wrong.

## Provenance

Drafted by an agent on 2026-08-31 after Jeffrey (@tucktuck101) stated the constraint
verbatim: **"Anything requiring org level permissions is out of scope for the buzz
project."** The agent established which of the day's decisions that constraint actually
invalidated — reporting that ADR-0033's CODEOWNERS half survives (teams `maintainers` and
`students` already exist with repository access, so research #369's "a team would have to
be created" no longer applies) and that ADR-0038 survives (the `main` restriction list is
user-based and branch protection is a repository-admin action) — and presented four
options for this record's question with their positive and negative consequences. Jeffrey
chose the fork-owned drop-branch CI workflow, replying verbatim: **"Agreed"**.

Not verified in this document: that a `push`-triggered fork-owned workflow reproduces
`ci.yml`'s check set faithfully, and that GitHub reports its results where a reviewer of
the drop pull request will find them. Both are the implementing task's to establish; this
record decides the mechanism, not its correctness in practice.
