---
id: release-desktop-release
type: release
status: draft
origin: launchpad
audiences:
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "Buzz has three independent release lanes; desktop and relay use release PRs, while mobile uses immutable release-candidate tags cut directly from remote main."
    entry_class: FACT
    evidence:
      - "RELEASING.md:1-4"
  - statement: "The desktop lane's entry point is `just release-desktop <version>`, producing a packaged desktop app: signed/notarized macOS, unsigned Windows, and Linux artifacts."
    entry_class: FACT
    evidence:
      - "RELEASING.md:6-8"
  - statement: "Desktop's release-version authority is `desktop/package.json` and its synchronized manifests; `just bump-desktop-version <version>` updates those manifests and regenerates their lockfiles."
    entry_class: FACT
    evidence:
      - "RELEASING.md:129"
      - "RELEASING.md:133"
      - "RELEASING.md:137-139"
  - statement: "At the recorded revision, `desktop/package.json`'s version (0.5.20) matches the topmost entry in `CHANGELOG.md` (`## v0.5.20`), consistent with the version-authority claim above."
    entry_class: FACT
    evidence:
      - "desktop/package.json:4"
      - "CHANGELOG.md:3"
  - statement: "Squash-merging the reviewed candidate PR after all protected-branch checks pass is the stated human authorization event for a desktop release; an authorized owner/admin bypass is treated the same way, and unrelated changes that reach main afterward do not invalidate the reviewed candidate."
    entry_class: FACT
    evidence:
      - "RELEASING.md:53-58"
  - statement: "`auto-tag-on-release-pr-merge.yml` triggers on `pull_request` events of type `closed` against `main`, and its `auto-tag` job runs only when `github.event.pull_request.merged == true` and the PR's head repository matches the target repository."
    entry_class: FACT
    evidence:
      - ".github/workflows/auto-tag-on-release-pr-merge.yml:28-46"
  - statement: "For a `version-bump/<v>` branch the workflow resolves the tag `desktop-v<v>`, validates the version string as semver, and — only for this desktop lane — runs `scripts/verify-desktop-release-merge.sh` before any tag is created."
    entry_class: FACT
    evidence:
      - ".github/workflows/auto-tag-on-release-pr-merge.yml:54-119"
  - statement: "`scripts/verify-desktop-release-merge.sh` re-fetches the pull request from the GitHub API and asserts its `merged`, `head.sha`, `head.ref`, `head.repo.full_name`, `base.ref`, `merge_commit_sha`, and `merged_at` fields all match the closed webhook event, rather than trusting the event payload alone; branch names are explicitly noted as mutable and never used to resolve the artifact."
    entry_class: FACT
    evidence:
      - "scripts/verify-desktop-release-merge.sh:32-48"
  - statement: "The same script reads its own trusted verifier code (`scripts/desktop_release.py`, `scripts/required-check-succeeded.jq`) from the candidate's frozen parent commit rather than from the candidate itself, and requires the candidate to have exactly one parent that is an ancestor of `origin/main` before running `desktop_release.py validate` against the candidate."
    entry_class: FACT
    evidence:
      - "scripts/verify-desktop-release-merge.sh:50-70"
  - statement: "The script then requires a fixed list of required checks, each pinned to an explicit GitHub App/producer `integration_id` rather than only a display name, to have succeeded at merge time, querying with `filter=latest` because GitHub exposes no per-rerun creation time — so an ordinary check rerun after merge deliberately fails this verification closed."
    entry_class: FACT
    evidence:
      - "scripts/verify-desktop-release-merge.sh:11-30"
      - "scripts/verify-desktop-release-merge.sh:72-84"
  - statement: "The release tag is created through a short-lived token from a dedicated `buzz-release-bot` GitHub App at the exact resolved `target_sha`; a retry is accepted only when it created the identical tag at the identical SHA, and any other pre-existing tag at a different SHA is a hard error."
    entry_class: FACT
    evidence:
      - ".github/workflows/auto-tag-on-release-pr-merge.yml:121-163"
  - statement: "`release.yml` triggers on `push` of tags matching `desktop-v[0-9]*`, is gated to `github.repository == 'block/buzz'`, and its `setup` job derives the version from `GITHUB_REF_NAME`, validates it as semver by regex, and calls `scripts/verify-release-ref.sh desktop-v <version>` to confirm the checked-out commit is exactly the tag's commit before anything else runs."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml:1-50"
      - "scripts/verify-release-ref.sh:17-35"
  - statement: "Four independent platform jobs build the release — macOS Apple Silicon (`release`), macOS Intel (`release-macos-x64`), Linux (`release-linux`), and Windows (`release-windows`) — each re-running `scripts/verify-release-ref.sh` against its own checkout before building."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml:52-777"
  - statement: "Both macOS DMGs are codesigned and notarized via `block/apple-codesign-action`; the Windows NSIS installer ships unsigned, with an `_alpha-unsigned` filename marker; the Linux job ships a `.deb` (not auto-updatable — the Tauri updater supports only AppImage on Linux) and an `.AppImage` post-processed by `desktop/scripts/fix-appimage.sh`."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml:172-217"
      - ".github/workflows/release.yml:584-595"
      - ".github/workflows/release.yml:643"
      - ".github/workflows/release.yml:749-760"
  - statement: "At the recorded revision, the `release-linux` job runs inside an `ubuntu:24.04` container, not the `ubuntu:22.04` container that `RELEASING.md`'s own prose currently states — a documentation-drift point, not a resolved conflict this node adjudicates, recorded here per the corpus rule that executable evidence outranks documentation for current behavior."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml:431"
  - statement: "`assemble-manifest` runs only when `setup` and all four platform jobs succeeded; it builds a combined `latest.json` via `desktop/scripts/generate-oss-latest-json.sh`, extracts the release-notes block matching `## v<version>` from `CHANGELOG.md` and fails if that block is empty, creates or re-verifies a draft `desktop-v<version>` GitHub Release targeted at the exact tag-bound commit, uploads every staged artifact, and only then flips the release from draft to published."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml:778-950"
  - statement: "Desktop publishes two separate GitHub releases: the versioned `desktop-v<version>` release, and a separate rolling `buzz-desktop-latest` release whose `latest.json` is what auto-update clients actually read. Publishing the versioned release does not by itself expose it through in-app auto-update."
    entry_class: FACT
    evidence:
      - "RELEASING.md:199-207"
  - statement: "Promoting a stable version to auto-update is a distinct, manually dispatched workflow (`promote-oss-desktop-release.yml`) restricted to running from `main`, which fetches the target release's `updater-manifest.json`, validates its version/platform/signature/URL shape and rejects a downgrade, then re-reads the currently-served `latest.json` digest immediately before its one write and again immediately after, to catch a promotion racing against a concurrent change."
    entry_class: FACT
    evidence:
      - ".github/workflows/promote-oss-desktop-release.yml"
      - "scripts/promote-oss-desktop-release.sh:1-77"
  - statement: "A same-version promotion retry succeeds only when the candidate manifest is byte-identical to what is already promoted; a bad promoted release is fixed by promoting a newer version, since the manifest is never downgraded to an older one."
    entry_class: FACT
    evidence:
      - "scripts/promote-oss-desktop-release.sh:53-59"
      - "RELEASING.md:219-221"
  - statement: "`release.yml` has no manual-dispatch trigger and cannot build from `main` or any caller-selected ref. Recovering a failed platform job for an existing tag means rerunning that failed workflow run (`gh run rerun <run-id> --failed`), never recreating or moving the immutable `desktop-v<version>` tag."
    entry_class: FACT
    evidence:
      - "RELEASING.md:171-179"
      - ".github/workflows/release.yml:7-11"
  - statement: "For the corresponding internal, Block-signed build, `RELEASING.md` states only that an operator starts the private \"Release Desktop\" Buildkite pipeline and supplies the exact public `desktop-v<version>` tag as `desktop_ref`, and that a generic `v<version>` tag is deliberately rejected; the pipeline's own internal steps are not discoverable from this repository."
    entry_class: FACT
    evidence:
      - "RELEASING.md:190-195"
  - statement: "This repository's root `AGENTS.md` states that `squareup/buzz-releases` runs Buildkite pipelines producing Block-signed macOS and iOS builds with a `-block` desktop version suffix, publishing to Artifactory, GitHub, and Mobile Releases."
    entry_class: FACT
    evidence:
      - "AGENTS.md:37"
      - "AGENTS.md:44"
  - statement: "The repository's only tag-target ruleset is `14378754` (\"Release\"), enforcement `active`; its live `ref_name` include conditions are `~ALL`, `refs/tags/v*`, `refs/tags/relay-v*`, `refs/tags/mobile-v*`, `refs/tags/chart-v*`, `refs/tags/push-chart-v*`, and `refs/tags/sprig-v*`, with rules `deletion`, `non_fast_forward`, `creation`, and `update`. The special `~ALL` value means every tag — including `desktop-v*` — is covered today, even though `desktop-v*` is not itself one of the specifically named patterns; `RELEASING.md`'s Prerequisites section describes this same ruleset ID as \"active for `desktop-v*` and `mobile-v*`\", which names a narrower configuration than what the live API returns."
    entry_class: FACT
    evidence:
      - "gh_api(repos/block/buzz/rulesets/14378754) -> {\"id\":14378754,\"name\":\"Release\",\"target\":\"tag\",\"enforcement\":\"active\",\"conditions\":{\"ref_name\":{\"include\":[\"~ALL\",\"refs/tags/v*\",\"refs/tags/relay-v*\",\"refs/tags/mobile-v*\",\"refs/tags/chart-v*\",\"refs/tags/push-chart-v*\",\"refs/tags/sprig-v*\"],\"exclude\":[]}},\"rules\":[{\"type\":\"deletion\"},{\"type\":\"non_fast_forward\"},{\"type\":\"creation\"},{\"type\":\"update\"}]}"
  - statement: "This repository has exactly three GitHub rulesets in total (`Default` on branches, `Mobile Release Branches` on branches, `Release` on tags), so no separate, more specific ruleset exists anywhere that names `desktop-v*` explicitly — the blanket `~ALL` entry on the `Release` ruleset is the only mechanism currently protecting desktop tags from deletion, non-fast-forward, or re-creation."
    entry_class: FACT
    evidence:
      - "gh_api(repos/block/buzz/rulesets) -> [{\"id\":13596885,\"name\":\"Default\",\"target\":\"branch\"},{\"id\":19321162,\"name\":\"Mobile Release Branches\",\"target\":\"branch\"},{\"id\":14378754,\"name\":\"Release\",\"target\":\"tag\"}]"
  - statement: "`node.schema.json`'s closed `type` enum includes `release` as one of the corpus's thirteen surfaces, distinct from `governance`, `operations`, and the other twelve values."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "The merged `corpus-template-procedure` node states its own worked example for the shape it covers as 'a task the reader chooses to perform on their own schedule -- \"cut a relay release\"', distinguishing that from a runbook's already-firing operational condition; this document's subject (cutting and shipping a desktop release) is the same shape, and `type` (the corpus surface, here `release`) is independent of which documentation-form template a node's body follows, per that same template's own note on `type`."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md:227-233"
      - "launchpad/docs/corpus/templates/procedure.md:255-268"
  - statement: "No corpus template specifically named `release` exists, merged or via an open PR, as of the recorded revision — the templates directory holds documentation-form templates (procedure, runbook, reference, concept, and others), not corpus-surface names, and a search of open/merged PRs for a release-specific template returned nothing."
    entry_class: FACT
    evidence:
      - "gh_pr_list(repo='launchpad-26/buzz', search='release template in:title') -> []"
      - "ls(launchpad/docs/corpus/templates) -> architecture-component.md, architecture-container.md, architecture-context.md, capability.md, component.md, concept.md, configuration.md, data-entity.md, datastore.md, decision-reference.md, deployment.md, event-kind.md, flow.md, generated-index.md, glossary-term.md, implementation-reference.md, interface.md, invariant.md, policy.md, procedure.md, reference.md, runbook.md, specification.md, test-contract.md, test-strategy.md, threat-model.md (no release.md present)"
  - statement: "Sibling tasks #1292 (`releases/desktop-candidate.md`), #1301 (`releases/versioning.md`), and #1299 (`releases/release-tags.md`) are all open with no drafted corpus node yet, and no `release-*` node id exists anywhere in the merged corpus at the recorded revision."
    entry_class: FACT
    evidence:
      - "gh_issue_view(1292,1301,1299) -> all state OPEN"
      - "grep(pattern='^id: ', path='launchpad/docs/corpus/') -> no release-* id present at recorded revision"
  - statement: "Issue #1293's own Definition of Done and Out of Scope sections require exactly one hand-authored canonical document, forbid creating or materially editing a second one, forbid changing runtime release behavior, forbid deciding unresolved ADR outcomes, and forbid broad 'while here' documentation cleanup."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1293 (issue body: Definition of done, Out of scope)"
relationships:
  - type: implements
    target: corpus-template-procedure
---

# Desktop release: candidate merge to published, promoted build

How a reviewed desktop release candidate becomes a published, and eventually
auto-updating, `desktop-v<version>` release of the Buzz desktop app — from the
squash-merge that authorizes it through automatic tagging, the four-platform build,
publication, and the separate manual promotion to auto-update. This node picks up
*after* a candidate PR already exists and has passed review; cutting that candidate is
a different task (see *Boundary*, below).

## Before you start

- Write access to `block/buzz`, and reviewer/owner authority to approve and merge a
  release candidate PR on a branch named `version-bump/<version>`.
- The candidate PR must already exist, target `main`, and have all required checks
  passing — this document does not cover producing that PR (`just release-desktop
  <version>` and its underlying `scripts/prepare-desktop-release.sh`); see *Boundary*.
- For the separate promotion step: `gh` access to dispatch a workflow on `main`, and
  the exact stable `X.Y.Z` version already published as `desktop-v<version>`.
- For the equivalent internal, Block-signed build: access to the private "Release
  Desktop" Buildkite pipeline (`buildkite.com/runway/sprout-releases`); this document
  only records what `RELEASING.md` states about that handoff, since the pipeline
  itself lives outside this repository (see *Scope and omissions*).

## Merge, tag, build, and publish

1. **Review the candidate PR.** Confirm the exact candidate SHA, the complete
   changelog block, and that CI is green on the protected-branch checks. Regenerating
   or pushing the candidate branch again creates a new candidate and requires checks
   to run again from scratch.
2. **Squash-merge the PR** once every required check passes. This merge is the human
   authorization event; an authorized owner/admin bypass counts the same way. Unrelated
   commits that later reach `main` do not invalidate this reviewed candidate, because
   the next release's ledger boundary is computed from validated prior-candidate
   metadata, not from `main`'s tip at merge time.
3. **Let `auto-tag-on-release-pr-merge.yml` verify and tag automatically** — no manual
   action here, but understand what it checks, because a failure here is diagnosed by
   reading its output, not by retrying blindly. It fires on the PR's `closed` event,
   confirms `merged == true` and that the head repository is internal, then — because
   the branch matches `version-bump/<v>` — runs `scripts/verify-desktop-release-merge.sh`.
   That script re-fetches the PR from the GitHub API and checks its `merged`,
   `head.sha`, `head.ref`, `base.ref`, `merge_commit_sha`, and `merged_at` fields
   against the webhook event; reads its own trusted verifier code from the candidate's
   frozen parent commit (never from the candidate itself); confirms the candidate has
   exactly one parent and that parent is an ancestor of protected `main`; and requires
   a fixed list of required checks, each pinned to a specific GitHub App producer
   `integration_id`, to have succeeded *at merge time*. Because GitHub exposes no
   per-rerun creation timestamp, an ordinary check rerun after merge makes this
   verification fail closed by design — see *Release Retry* in `RELEASING.md` and the
   troubleshooting note below for what to do instead of retrying it. Once verified,
   the workflow creates `desktop-v<version>` through a dedicated `buzz-release-bot`
   GitHub App token, at the exact reviewed PR head commit — never the squash commit on
   `main`.
4. **`release.yml` builds and publishes automatically** once the tag exists — again no
   manual action, but understand the gate. The workflow triggers only on a
   `desktop-v[0-9]*` tag push and only in `block/buzz`; its `setup` job derives the
   version from the tag name, validates it as semver, and every subsequent job
   re-verifies that its own checkout's HEAD is exactly that tag's commit before
   building anything. Four independent platform jobs build in parallel: macOS Apple
   Silicon and Intel DMGs (both codesigned and notarized), an unsigned Windows NSIS
   installer (filename-marked `_alpha-unsigned`), and Linux `.deb` plus `.AppImage`
   packages (the AppImage is post-processed by `desktop/scripts/fix-appimage.sh` to
   strip infra libraries that crash newer Mesa/GLib hosts). Only once `setup` and all
   four platform jobs succeed does `assemble-manifest` run: it builds the combined
   updater `latest.json`, pulls the release-notes block matching `## v<version>` out
   of `CHANGELOG.md` (failing if that block is missing or empty), creates or re-verifies
   a draft `desktop-v<version>` GitHub Release targeted at the exact tag commit,
   uploads every staged artifact, and only then flips the release from draft to
   published.
5. **Verify what got published.** Desktop now has two GitHub releases: the versioned,
   user-facing `desktop-v<version>` (installers plus the `updater-manifest.json`
   promotion candidate) and the separate rolling `buzz-desktop-latest`, whose
   `latest.json` is what auto-update clients actually read. Publishing the versioned
   release does **not** by itself put it in front of existing users — that is the
   separate step below.

## Promote to auto-update

A separate, deliberate action — not a continuation of the pipeline above.

1. Install and test the published `desktop-v<version>` artifacts.
2. Run the **Promote OSS Desktop Auto-Update** workflow from `main`, entering the
   exact stable `X.Y.Z` version (the workflow itself refuses to dispatch from anything
   other than `refs/heads/main`).
3. The workflow validates the release is neither a draft nor a prerelease, confirms
   the tag and its release target resolve to the same commit, downloads and validates
   `updater-manifest.json`'s version, exact platform set, per-platform signatures, and
   canonical download URLs, then compares against the currently promoted
   `buzz-desktop-latest/latest.json`: a same-version retry succeeds only if the
   manifest is byte-identical to what's live; any other version is rejected unless it
   is strictly newer. Immediately before its one write it re-reads the live manifest's
   digest to catch a concurrent promotion, and immediately after the write it
   downloads the manifest again and compares digests to confirm the upload actually
   served what was intended.
4. If a promoted release turns out to be bad, ship and promote a higher patch version.
   The manifest is never downgraded to an older version, so existing auto-updated
   clients would otherwise stay on the bad build with no path back except a new,
   higher release.

## Release retry (when a platform build fails)

`release.yml` has no manual-dispatch trigger and cannot build from `main` or any
caller-supplied ref — it only reacts to the immutable tag. If a platform job fails
after the tag exists, rerun that failed workflow run (via the Actions UI, or
`gh run rerun <run-id> --failed --repo block/buzz`); this repairs the versioned draft
if publication did not complete. A rerun does **not** promote that version to
auto-update — that is always the separate, explicit step above. Never recreate, move,
or delete the immutable `desktop-v<version>` tag to retry a failed build.

## Internal (Block-signed) build

For the equivalent Block-signed desktop build, an operator starts the private
"Release Desktop" Buildkite pipeline and enters the exact public source tag as
`desktop_ref=desktop-v<version>`; a generic `v<version>` tag is deliberately rejected.
Per this repository's own `AGENTS.md`, that pipeline lives in
`squareup/buzz-releases`, produces Block-signed macOS and iOS builds carrying a
`-block` desktop version suffix, and publishes to Artifactory, GitHub, and Mobile
Releases. This document records only that hand-off contract, not the private
pipeline's internal steps — see *Scope and omissions*.

## See also

No other corpus node exists yet under `launchpad/docs/corpus/releases/` to link to.
Once #1292 (candidate-cutting), #1301 (versioning policy), and #1299 (tag format) each
land, this section is where their nodes belong.

## Boundary

This node does not describe:

- **How a candidate is cut.** `just release-desktop <version>` and
  `scripts/prepare-desktop-release.sh` producing the `version-bump/<version>` PR,
  including how the candidate's frozen base and prior-release ledger are computed, is
  #1292's subject (`releases/desktop-candidate.md`), not this one.
- **The semver policy itself** — what qualifies as a patch vs. minor vs. major bump,
  and how `just get-next-patch-version` fits a broader versioning policy — is #1301's
  subject (`releases/versioning.md`).
- **The tag naming/format contract in general** (why `desktop-v<version>` rather than
  a bare `v<version>`, and how that generalizes across the desktop/relay/mobile/chart
  lanes) is #1299's subject (`releases/release-tags.md`).
- **The relay and mobile release lanes.** `RELEASING.md` documents all three lanes;
  this node is scoped to desktop only, per corpus's "one node, one idea" rule.
- **The private `squareup/buzz-releases` Buildkite pipeline's internal steps** —
  signing mechanics, artifact promotion within Artifactory/Mobile Releases, or its
  own approval gates. This repository's own governing documents (`RELEASING.md`,
  `AGENTS.md`) describe only the hand-off contract to that pipeline, and this session
  has no access to inspect the pipeline itself.
- **A newcomer's first walkthrough of releasing** (a tutorial) or a lookup table of
  every workflow input/output (reference-shaped content) — this is a how-to for
  someone who already knows they need to ship a desktop release.
- **Why this design exists** (e.g., why squash-merge is the authorization event rather
  than approval alone, or why mobile diverges to immutable RC tags) beyond what
  `RELEASING.md` states directly — a fuller rationale, if one is wanted, belongs in a
  concept/explanation-shaped node, not here.

## Relationships

- **Declared:** `implements` → `corpus-template-procedure`, since this node is built
  against that merged template's required sections (overview, prerequisites, numbered
  steps with a permitted fork for the retry/promotion branches, boundary, scope and
  omissions) and its own worked example for the procedure shape names cutting a
  release directly.
- **Checked, not declared:** #1292/#1301/#1299 are the natural `references` targets
  once their nodes exist — confirmed via `gh issue view` that none of the three has
  landed yet, and via `grep`/`ls-tree` against `origin/launchpad` that no `release-*`
  id exists in the merged corpus tree. No edge is declared to an id that does not yet
  exist.

## Scope and omissions

**This node covers** the desktop release process from a reviewed, merged candidate PR
through automatic tagging, verification, the four-platform build, publication of both
GitHub releases, the separate manual promotion to auto-update, and the release-retry
path for a failed platform build — plus the documented hand-off to the private,
Block-signed internal build.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Cutting the release candidate itself | #1292, open, not yet drafted |
| The versioning/semver policy | #1301, open, not yet drafted |
| The tag-format contract across all lanes | #1299, open, not yet drafted |
| The relay and mobile release lanes | Not this node — `RELEASING.md` covers all three; no corpus task for relay/mobile release process was found in this session's search |
| The private `squareup/buzz-releases` Buildkite pipeline's internal signing/publishing steps | Outside this repository; not inspectable from this session |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating, and retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **This process was not exercised end-to-end.** Every claim above traces to
  `RELEASING.md`'s prose, the workflow YAML, or the shell scripts the workflows call —
  no candidate was actually merged and watched through tagging, build, and publish
  during this session. The corpus's own evidence standard treats a step's described
  effect as a `FACT` only when its source was actually opened and read, which was
  done here; it does not claim the described sequence was freshly observed running.
- **The `Release` tag ruleset's `bypass_actors` list could not be read from this
  session's GitHub identity** — the field was entirely absent from the `gh api
  repos/block/buzz/rulesets/14378754` response, rather than present and empty, which
  is consistent with (but does not prove) an access-level restriction rather than an
  empty configuration. `RELEASING.md`'s claim that `buzz-release-bot` is the ruleset's
  "sole always-bypass actor" is therefore neither confirmed nor refuted here.
- **Whether the `ubuntu:24.04` vs. `ubuntu:22.04` container discrepancy noted above
  (release.yml vs. RELEASING.md) reflects an intentional, undocumented upgrade or
  simple documentation drift** was not resolved — only the live discrepancy itself
  was confirmed, by reading both sources directly rather than trusting either one's
  restatement of the other.
- **Whether the `Release` ruleset's named-but-non-matching patterns (`v*` rather than
  `desktop-v*`, alongside the blanket `~ALL`) are deliberate legacy entries or drift**
  was not resolved. The practical effect — `desktop-v*` tags remain protected via
  `~ALL` regardless — was confirmed directly against the live API, not assumed from
  `RELEASING.md`'s prose.
- **The internal Buildkite pipeline's actual behavior** beyond the `desktop_ref`
  input contract stated in `RELEASING.md` was not verified and could not be, from
  this repository.
