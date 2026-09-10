---
id: verification-ci-ci-gates
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "The `CI` workflow (`.github/workflows/ci.yml`) triggers on every `pull_request` event and on every `push` to the `main` and `release` branches."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:1-5"
  - statement: "ci.yml's `changes` job ('Detect Changed Paths') carries no `needs` and no `if` of its own, so it runs unconditionally on every triggering event; every other job in the workflow (rust-lint, unit-tests, desktop-core, desktop-smoke-e2e, desktop, desktop-e2e-relay, desktop-e2e-integration-shard, desktop-e2e-integration, backend-integration, relay-e2e, web, mobile, mobile-swift, security, server-cross-compile, windows-rust, desktop-build-macos) declares `needs: [changes]` directly or transitively through another job that does, so a failure in `changes` prevents every other job from running and fails the overall workflow run."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:17-30"
      - ".github/workflows/ci.yml"
  - statement: "The `changes` job's 'Changed-paths filter contract' step runs `scripts/test-ci-changed-paths-filter.sh`, which parses the `filters: |` block passed to the `dorny/paths-filter` action in `.github/workflows/ci.yml` and fails if any single filter's pattern list mixes a positive pattern with a negated (`!`-prefixed) pattern."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:93-94"
      - "scripts/test-ci-changed-paths-filter.sh"
  - statement: "The script's own comment states the rule it guards: `dorny/paths-filter` (via picomatch) treats every pattern in a filter's list as an independent OR clause, so a standalone negated pattern mixed with positive patterns does not act as an 'AND NOT' exclusion and instead matches almost every file outside the negated path -- silently making the whole filter evaluate true for nearly any change in the repo -- and the comment names this as the mechanism behind launchpad-26/buzz#181."
    entry_class: FACT
    evidence:
      - "scripts/test-ci-changed-paths-filter.sh"
  - statement: "Issue #181, closed, is titled 'Docs-only PRs blocked by unrelated Desktop CI failures (flaky E2E, real regressions, GH Actions infra)'; the fix commit 329edeb496afdee3c5af139af48679331c644ba0 ('fix(ci): stop the desktop paths-filter from matching every PR') states in its own message that the `desktop` filter's mixed `desktop/**` / `!desktop/src-tauri/**` pattern list made `desktop` evaluate true for almost any change, including plain `launchpad/*.md` docs, and names docs-only PRs #147, #167, #168, #172, #174, #175 and #179 as having been run against, and blocked by, the full Desktop Core / Desktop Smoke E2E / Desktop E2E Integration suites as a result."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#181 (issue title and state) and commit 329edeb496afdee3c5af139af48679331c644ba0's own commit message"
  - statement: "Running `bash scripts/test-ci-changed-paths-filter.sh` from the repository root at the recorded revision exits 0 and prints 'changed-paths filter contract passed'."
    entry_class: FACT
    evidence:
      - "run_command('bash scripts/test-ci-changed-paths-filter.sh') -> changed-paths filter contract passed, exit status 0"
  - statement: "At the recorded revision, none of ci.yml's five paths-filter definitions (`rust`, `desktop`, `desktop-rust`, `web`, `mobile`) contains a negated (`!`-prefixed) pattern, so the script's guard is currently prophylactic rather than actively rejecting a live violation."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:39-74"
  - statement: "The script's awk parser recognizes a filter's name only at exactly 12-space indentation and a filter's own patterns only at exactly 14-space indentation within the `filters: |` block, and the script asserts no minimum count of filters found before declaring the run passed."
    entry_class: FACT
    evidence:
      - "scripts/test-ci-changed-paths-filter.sh"
  - statement: "Because the parser is indentation-based rather than a real YAML parser and asserts no minimum filter count, a syntactically valid but differently-indented rewrite of the `filters:` block would make the parser match zero filters, leave the failure counter at its initial 0, and cause the script to print 'changed-paths filter contract passed' and exit 0 without having evaluated any filter -- so the obligation's enforcement is contingent on the block's current indentation persisting, not on its semantic content alone."
    entry_class: INFERENCE
    evidence:
      - "scripts/test-ci-changed-paths-filter.sh"
    confidence: 0.8
  - statement: "Parent Feature #617's child issue list carries #1352 (this task, ci-gates.md) alongside #1353 (pre-commit.md), #1354 (pre-push.md), #1355 (release-validation.md) and #1356 (required-checks.md) as separate verification/ci/ tasks, so this node's scope is deliberately narrower than 'everything CI enforces' and excludes local git-hook behavior, release-pipeline validation, and which checks GitHub branch protection marks required for merge."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#617 child issue list, compared against this task's own title and #1353/#1354/#1355/#1356's titles"
  - statement: "This node's citation of the verifying test's run result and existence follows corpus-standard-test-references' shape rules (bare/`path:line` for an existence claim, the tool-result shape for a run-result claim), so a `references` edge from this node to `corpus-standard-test-references` names a real dependency rather than a generic cross-reference to `AGENTS.md`."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/standards/test-references.md"
    confidence: 0.8
relationships:
  - type: references
    target: corpus-standard-test-references
---

# CI changed-paths filter contract — test contract

## Purpose and boundary

This node documents one obligation enforced inside Buzz's `CI` GitHub Actions
workflow (`.github/workflows/ci.yml`): that the workflow's own per-language path
filters cannot silently defeat their own gating logic by mixing a positive and a
negated pattern in one filter. This is one obligation among several the `changes`
job's "contract" steps enforce (see *Scope and omissions*), and this node covers
that one obligation only -- not the other contract-test steps in the same job,
not local pre-commit/pre-push hooks, not which CI jobs GitHub branch protection
marks as required for merge, and not release-pipeline validation. Those are
separate, sibling corpus tasks (see *Scope and omissions*).

## Obligation

> No filter definition in `.github/workflows/ci.yml`'s `filters: |` block (passed
> to the `dorny/paths-filter` action in the `changes` job) mixes a positive
> pattern with a negated (`!`-prefixed) pattern within the same filter's pattern
> list.

This matters because `dorny/paths-filter` (via picomatch) evaluates every pattern
in a filter's list as an independent OR clause, not as a `.gitignore`-style
"AND NOT" exclusion. A filter that mixes quantifiers -- e.g. `['desktop/**',
'!desktop/src-tauri/**']` -- has its negated entry alone match almost every file
outside that one excluded directory, which silently makes the *entire* filter
evaluate `true` for nearly any change in the repository, including a change that
never touched the filter's intended surface at all.

## Verifying test(s)

- `scripts/test-ci-changed-paths-filter.sh` -- a standalone bash script. It reads
  `.github/workflows/ci.yml`, extracts the `filters: |` block passed to
  `dorny/paths-filter` with an indentation-based `awk` parser (filter names at
  12-space indent, patterns at 14-space indent), and for each filter checks
  whether its pattern list contains both a positive and a `!`-prefixed entry. It
  exits non-zero and prints a `::error::` annotation naming the offending filter
  and citing issue #181 if any filter mixes quantifiers; otherwise it prints
  `changed-paths filter contract passed` and exits 0.

This is the only test covering this specific obligation. It is invoked from CI as
the "Changed-paths filter contract" step in the `changes` job.

## How to run it

```bash
bash scripts/test-ci-changed-paths-filter.sh
```

No flags, no gating, no infrastructure dependency -- it only reads the workflow
file at the path it resolves relative to its own location
(`$(dirname "${BASH_SOURCE[0]}")/..`), so it must be run from inside a checkout of
this repository but needs nothing else running.

## Current enforcement status

**Verified**, as of `473205a7457b208455f188847bfb27b01aa83cac`. The test exists,
is invoked unconditionally in CI (the `changes` job carries no `needs` or `if`, so
it runs on every `pull_request` and every `push` to `main`/`release`), and running
it directly against the recorded revision exits 0. Because every other job in the
workflow depends on `changes` either directly (`needs: [changes]`) or transitively
through a job that does, a failure of this step fails the `changes` job, which in
turn blocks every downstream job from running and fails the overall `CI` workflow
run -- there is no path by which a mixed-quantifier filter could pass CI silently.

Whether the `CI` workflow (or the `changes` job specifically) is itself configured
as a *required* status check in GitHub branch protection -- i.e. whether a red `CI`
run can be merged over -- is not established here; see *Scope and omissions*.

## Limits

- **The check is syntactic, not semantic.** It confirms no filter's pattern list
  contains both a positive and a negated entry; it does not execute
  `dorny/paths-filter` or picomatch itself, so it cannot catch a different
  picomatch quirk that produces the same "filter always true" failure through some
  other pattern shape.
- **It checks exactly one file.** The script's `workflow` path is hardcoded to
  `.github/workflows/ci.yml`. A `filters:` block with the same defect written into
  any other workflow file in `.github/workflows/` is not checked by this test.
- **It does not check consumption of the filter's outputs.** A job's `if:`
  condition referencing `needs.changes.outputs.<name>` incorrectly (wrong output
  name, inverted logic) is outside this test's scope -- it only inspects the
  filter *definitions*, not how their outputs are used downstream.
- **The parser can silently see nothing.** As recorded in this node's own
  evidence ledger, the `awk` parser depends on the `filters:` block using exactly
  12-space filter-name indentation and 14-space pattern indentation today. If that
  formatting changed, the parser could match zero filters and the script would
  still print "passed" and exit 0 -- the obligation's enforcement is contingent on
  that formatting, not verified independently of it.
- **A negative result today proves absence, not immunity.** At the recorded
  revision no filter mixes quantifiers, so every run of this test to date has
  taken the "nothing to reject" path; the test has not been observed actually
  catching a live violation since the #181 fix landed (per this node's evidence
  ledger, the fix commit and the test script were introduced together).

## Relationships

**Checked against `origin/launchpad`, not this worktree**, per `AGENTS.md`'s
warning that a target resolving only in a local branch is a hard validation error
once merged:

```
git fetch origin launchpad
git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus
```

`corpus-standard-test-references` is present in that tree at the recorded
revision. This node declares one `references` edge to it, because this node's own
citations for the verifying test's existence and run result follow that
standard's shape rules directly (bare path for the existence claim, the
tool-result shape -- `run_command(...) -> ...` -- for the run-result claim), not
merely `AGENTS.md`'s generic evidence rules. No other node in the tree at the
recorded revision is specific to this obligation; a future `implements` edge to a
sibling `verification/ci/required-checks` node (once #1356 lands) would be the
next one to add, since that node would state whether this obligation's owning job
is a required merge check -- but that node does not exist yet, so no edge is
declared to it now.

## Scope and omissions

**This node covers** one obligation -- that `.github/workflows/ci.yml`'s
paths-filter definitions cannot mix a positive and a negated pattern in one
filter -- the test that verifies it, how to run that test, and this obligation's
current enforcement status and limits.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Local pre-commit hook behavior (lefthook, `stage_fixed`, format auto-fix) | `launchpad-26/buzz#1353` (`verification/ci/pre-commit.md`) |
| Local pre-push hook behavior (the differential file-size gate, clippy, `tsc --noEmit`, fast unit tests) | `launchpad-26/buzz#1354` (`verification/ci/pre-push.md`) |
| Release-pipeline validation (`release.yml`, desktop/mobile release-candidate workflows) | `launchpad-26/buzz#1355` (`verification/ci/release-validation.md`) |
| Which specific checks GitHub branch protection/rulesets mark as required before a PR can merge | `launchpad-26/buzz#1356` (`verification/ci/required-checks.md`) |
| The other "contract" test steps that also run inside the same `changes` job -- `Release workflow source contract` (`scripts/test-release-ref-contract.sh`), `Relay image eligibility contract` (`scripts/test-relay-image-eligibility-workflow.sh`), `Desktop release candidate contract` (`scripts/test-desktop-release-candidate.sh`), `OSS desktop promotion contract`, `Mobile release contract`, `Mobile worktree identity contract`, `File size ratchet unit tests` (`node --test scripts/check-file-sizes-core.test.mjs`), `Codex security review contract` (`just security-review-check`), `Rust cache contract`, and `File size policy` (`just file-size-check`) | Each is its own testable obligation and, per `AGENTS.md`'s one-node-one-idea rule, would need its own corpus node rather than being folded into this one; none is filed as a task at the time this node was written |
| The full job graph of `ci.yml` beyond the `changes` job's role as a universal dependency (what `rust-lint`, `desktop`, `mobile`, etc. individually assert) | Not a single obligation and not in scope for a test-contract node; a broader architecture or per-job node, if ever written, would own it |
| Whether this same defect class could recur in `.github/workflows/mobile-release-candidate.yml`, which the `mobile` filter also lists as a path that re-triggers path detection | Not checked by `scripts/test-ci-changed-paths-filter.sh` (see *Limits*) and not established here |

**Expected but not verified when this node was written:**

- **No corpus node yet exists for `required-checks.md`, `pre-commit.md`,
  `pre-push.md` or `release-validation.md`** (issues #1353-#1356 were open,
  unauthored, at the recorded revision), so none of the boundary claims above
  could be checked against a merged sibling node's actual content -- they are
  checked against those issues' titles only.
- **Whether GitHub Actions' own scheduling guarantees a `needs`-chain failure
  always reports the overall workflow run as failed (as opposed to some jobs
  merely being skipped while the run reports success) was not verified against
  GitHub's own documentation** -- it is asserted here from the observed
  `needs: [changes]` structure and ordinary GitHub Actions behavior, not from a
  cited GitHub Actions reference.
