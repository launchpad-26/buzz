---
id: verification-ci-release-validation
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "scripts/verify-release-ref.sh takes a tag prefix and a version, rejects a version that does not match the semver pattern ^[0-9]+\\.[0-9]+\\.[0-9]+(-[0-9A-Za-z.-]+)?$, then fails with a non-zero exit and an ::error:: line unless $GITHUB_REF exactly equals refs/tags/<prefix><version> AND the current HEAD commit is identical to the commit that tag points at; it only prints 'Verified ...' and exits 0 when both hold."
    entry_class: FACT
    evidence:
      - "scripts/verify-release-ref.sh"
  - statement: "scripts/test-release-ref-contract.sh exercises verify-release-ref.sh directly against a throwaway git repo: it accepts GITHUB_REF=refs/tags/desktop-v1.2.3 with desktop-v 1.2.3 at the tagged commit, rejects the same call under GITHUB_REF=refs/heads/main, rejects it again once a further commit has been added after the tag (HEAD no longer equals the tag commit), and accepts a differently-prefixed relay-v2.0.0 tag verified with relay-v 2.0.0 -- covering the accept path, the wrong-ref-kind rejection, and the stale-HEAD rejection."
    entry_class: FACT
    evidence:
      - "scripts/test-release-ref-contract.sh"
  - statement: "The same script also greps that .github/workflows/release.yml and .github/workflows/docker.yml contain no 'inputs.ref' (i.e. neither publisher workflow accepts a caller-selected source ref), and that both files, plus .github/workflows/ci.yml, each contain a literal reference to verify-release-ref.sh or test-release-ref-contract.sh respectively -- so the contract also asserts the check is actually wired into both publisher workflows and into CI, not only that the script behaves correctly in isolation."
    entry_class: FACT
    evidence:
      - "scripts/test-release-ref-contract.sh"
  - statement: ".github/workflows/release.yml (workflow 'Release', triggered on push of desktop-v[0-9]* tags) invokes scripts/verify-release-ref.sh desktop-v \"$VERSION\" in six separate steps, one per job (setup, release, release-macos-x64, release-linux, release-windows, assemble-manifest), each unconditional -- every job independently re-verifies the tag-bound source before doing any of its own build, sign, or publish work, rather than trusting a value computed once in an earlier job."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml"
  - statement: ".github/workflows/docker.yml (workflow 'Docker image', triggered on push of relay-v[0-9]* tags, on push to the launchpad branch, and on workflow_dispatch) invokes scripts/verify-release-ref.sh relay-v \"$VERSION\" in exactly two jobs, build and push-gateway-build, each gated 'if: github.ref_type == 'tag' || github.event_name == 'workflow_dispatch'' -- so the check runs only on a release-shaped trigger and is skipped for an ordinary push to the launchpad branch, which publishes only the rolling :launchpad/:sha-<commit> tags and is not a versioned release."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "docker.yml's push-gateway-build job additionally carries 'if: github.repository == 'block/buzz'', so on this fork's own checkout (launchpad-26/buzz) that job -- and therefore its call to verify-release-ref.sh -- never runs at all; only the build job's call is live on this fork's relay-v tag releases."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: ".github/workflows/ci.yml's 'changes' job, which runs unconditionally on every push to main/release and on every pull_request per the workflow's top-level 'on:' block, contains a step named 'Release workflow source contract' that runs scripts/test-release-ref-contract.sh with no further 'if:' guard and no dependency on the job's own changed-path filter outputs."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "RELEASING.md and scripts/mobile-release.sh describe and implement a mobile release lane that does not call scripts/verify-release-ref.sh at all: mobile-release.sh resolves and fetches the exact current remote origin/main commit itself (using git rev-parse --verify against the freshly fetched ref) and publishes a new, never-moved mobile-vX.Y.Z-rc.N tag at that commit through a dedicated GitHub App, rather than checking an already-created tag's ref against an already-checked-out HEAD the way the desktop and relay lanes do."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
      - "scripts/mobile-release.sh"
  - statement: "RELEASING.md's Prerequisites section names a separate GitHub 'Release tag ruleset (14378754)' active for desktop-v* and mobile-v* tags, with creation/update/deletion/non-fast-forward protections and buzz-release-bot as sole always-bypass actor, as the mechanism that keeps a release tag itself from being created or moved by an unauthorized actor in the first place -- a control this node's obligation does not implement or verify; verify-release-ref.sh only checks consistency of a workflow run that has already started against whatever tag triggered or was supplied to it."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "scripts/test-release-ref-contract.sh's own file also asserts, in the same script and same CI step, unrelated release-workflow properties -- the required-check-succeeded.jq filter's handling of stale/pending/rerun check runs, auto-tag-on-release-pr-merge.yml's GitHub App token and merge-verification wiring, desktop-release-candidate.yml's PR-read permissions, and release.yml's single-writer/single-upload invariants -- none of which this node's obligation covers; those are distinct obligations bundled into the same executable file and CI step rather than a sign that this node's obligation is broader than stated."
    entry_class: FACT
    evidence:
      - "scripts/test-release-ref-contract.sh"
relationships:
  - type: references
    target: corpus-standard-test-references
---

# Release-tag source verification — test contract

## Purpose and boundary

This node documents one obligation in Buzz's release-publishing CI: that a job
building or publishing a versioned release artifact for the desktop or relay
lanes runs at the exact commit its immutable release tag names, never at a
caller-selected or drifted ref. It covers **only** that one ref/commit
consistency check, implemented once in `scripts/verify-release-ref.sh` and
invoked independently by every desktop- and relay-release job that needs it.
It does not cover release-tag creation authorization, required-check
verification before a tag is created, code-signing/notarization correctness,
or the mobile release lane's own (different) source-verification mechanism —
each is named as a boundary below rather than folded in here.

## Obligation

> A job in the desktop (`release.yml`) or relay (`docker.yml`) release
> workflows that builds or publishes a tagged release artifact must run with
> `GITHUB_REF` equal to `refs/tags/<prefix><version>` for its own release's
> tag prefix and declared version, and with the checked-out `HEAD` commit
> identical to the commit that tag points at; if either does not hold, the
> job fails closed before doing any build, sign, or publish work.

## Verifying test(s)

- `scripts/test-release-ref-contract.sh` — its first block (direct
  invocations of `verify-release-ref.sh` against a scratch git repository,
  lines constructing and tagging `desktop-v1.2.3` and `relay-v2.0.0`) is the
  part that verifies this obligation: it asserts the accept path (correct
  `GITHUB_REF` at the tagged commit), the wrong-ref-kind rejection
  (`GITHUB_REF=refs/heads/main`), and the stale-`HEAD` rejection (a commit
  added after the tag). Its later grep-based assertions confirm
  `verify-release-ref.sh` is actually invoked from `release.yml` and
  `docker.yml` and that neither workflow accepts a caller-selected
  `inputs.ref`. The remainder of the same file (required-check-filter
  fixtures, `auto-tag-on-release-pr-merge.yml` wiring, `desktop-release-candidate.yml`
  permissions, `release.yml`'s single-writer checks) verifies other,
  unrelated release obligations bundled into the same script and is out of
  this node's scope — see *Limits* below.

## How to run it

```bash
scripts/test-release-ref-contract.sh
```

Plain Bash, no external services required; it builds its own scratch git
repository under `mktemp -d` and tears it down on exit.

## Current enforcement status

**Verified.** `.github/workflows/ci.yml`'s `changes` job runs this script
unconditionally, as the step named "Release workflow source contract", on
every push to `main`/`release` and on every pull request — it carries no
`if:` guard and does not depend on the job's own changed-path filter output.
The obligation itself is exercised in production by every desktop release tag
push (six independent call sites across `release.yml`'s `setup`, `release`,
`release-macos-x64`, `release-linux`, `release-windows` and
`assemble-manifest` jobs) and by relay release tag pushes and manual rescue
dispatches (`docker.yml`'s `build` job, gated to run only when
`github.ref_type == 'tag' || github.event_name == 'workflow_dispatch'`).
`docker.yml`'s second call site, in `push-gateway-build`, is additionally
gated `if: github.repository == 'block/buzz'` and therefore never executes on
this fork's own `launchpad-26/buzz` checkout — only the `build` job's call is
live here.

## Limits

What this obligation's verification does and does not establish:

- **It proves ref/commit consistency, not authorization to tag.** Passing
  confirms the workflow run is operating on the exact commit its tag name
  claims; it says nothing about whether that tag was created by an
  authorized actor. That is a separate control — RELEASING.md's Prerequisites
  name a GitHub tag ruleset (`14378754`) with `buzz-release-bot` as sole
  always-bypass actor for exactly this purpose, outside this obligation.
- **It proves nothing about what the tagged commit contains.** Neither
  `verify-release-ref.sh` nor its test asserts that the tagged commit passed
  CI, was reviewed, or matches any changelog entry. Verifying that the
  required checks were green when a desktop candidate PR merged is a
  different, already-tested obligation (`verify-desktop-release-merge.sh` and
  the required-check-succeeded.jq fixtures in the same
  `test-release-ref-contract.sh` file) and is out of scope here.
  `assemble-manifest`'s later step does separately assert a non-empty
  changelog block exists for the version, but that is a distinct check this
  node does not document.
- **It covers only the desktop and relay lanes.** The mobile release lane
  never calls `verify-release-ref.sh`; it uses its own mechanism
  (`mobile-release.sh` fetching and pinning the exact `origin/main` commit
  before it ever creates a tag, rather than checking an already-created tag
  after the fact). That mechanism is a separate obligation this node does not
  document.
- **It covers only a narrow slice of the file it is tested alongside.**
  `scripts/test-release-ref-contract.sh` is one CI step that also verifies
  several unrelated release-workflow properties (required-check-run
  filtering behaviour, `auto-tag-on-release-pr-merge.yml`'s GitHub App
  wiring, `desktop-release-candidate.yml`'s permissions). A failure in that
  step does not necessarily mean this node's obligation regressed — the exact
  failing assertion has to be read to tell which obligation broke.
- **No production release run was inspected.** Enforcement status above is
  established from the workflow YAML and the test script's own logic at the
  recorded revision, not from observing a real tagged release run's logs.

## Scope and omissions

**This node covers** the ref/commit consistency check `verify-release-ref.sh`
performs, where it is invoked in `release.yml` and `docker.yml`, and how
`test-release-ref-contract.sh` verifies that behavior plus its wiring.

**It does not cover, and these are named gaps rather than silence:**

| Not covered here | Where it actually lives |
|---|---|
| Whether a release tag was created by an authorized actor | GitHub's `desktop-v*`/`mobile-v*` tag ruleset (`14378754`), documented in RELEASING.md |
| Whether the tagged commit's required checks were green at merge time | `scripts/verify-desktop-release-merge.sh` and the `required-check-succeeded.jq` fixtures in `scripts/test-release-ref-contract.sh` |
| Code-signing and notarization correctness | `release.yml`'s "Verify code signature" steps (`codesign`, `spctl`, `desktop/scripts/verify-macos-entitlements.sh`) |
| Mobile's own source-commit verification mechanism | `scripts/mobile-release.sh`, `scripts/test-mobile-release-contract.sh` |
| Auto-updater manifest promotion validation | `scripts/test-oss-desktop-promotion.sh` / `-behavior.sh`, the "Promote OSS Desktop Auto-Update" workflow |
| General rules for how any corpus node cites a test as evidence | `corpus-standard-test-references` |

**Relationships actually checked, not assumed absent.** At the recorded
revision `origin/launchpad`'s corpus tree includes `corpus-standard-test-references`
(`launchpad/docs/corpus/standards/test-references.md`), which this node
declares a `references` edge to because it directly governs how the test
citations above are written. No other existing node in that tree documents
release publishing, release-tag ruleset enforcement, or the mobile release
lane specifically, so no further edge is declared; a future node documenting
`verify-desktop-release-merge.sh`'s required-check verification or the
mobile release lane would be a natural `references` target once it exists.
