---
id: releases-release-tags
type: release
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "auto-tag-on-release-pr-merge.yml's own header comment maps four PR-driven release lanes to their tag prefixes: branch prefix `version-bump/<v>` to tag `desktop-v<v>` (triggers release.yml, the desktop app); `relay-release/<v>` to `relay-v<v>` (triggers docker.yml, the relay image); `chart-release/<v>` to `chart-v<v>` (triggers helm-chart.yml, the main Helm chart); `push-chart-release/<v>` to `push-chart-v<v>` (triggers push-gateway-helm-chart.yml); and states that any other internal PR that bumps deploy/charts/buzz/Chart.yaml's `version` also produces a `chart-v<v>` tag."
    entry_class: FACT
    evidence:
      - ".github/workflows/auto-tag-on-release-pr-merge.yml:1-16"
  - statement: "auto-tag-on-release-pr-merge.yml's 'Resolve release lane and version' step derives VERSION and TAG_PREFIX from the merged PR's head branch name by case-matching the four prefixes above, falls back to a Chart.yaml version-bump detection for any other branch, and validates VERSION against the single shared regex `^[0-9]+\\.[0-9]+\\.[0-9]+(-[0-9A-Za-z.-]+)?$` before emitting `tag=${TAG_PREFIX}${VERSION}` -- so desktop-v*, relay-v*, chart-v* and push-chart-v* all share one version grammar: a plain X.Y.Z core with an optional free-form `-`-prefixed suffix."
    entry_class: FACT
    evidence:
      - ".github/workflows/auto-tag-on-release-pr-merge.yml:52-92"
  - statement: "For a desktop-v tag specifically, the same step sets target_sha to the PR head SHA (not the squash-merge commit) and a 'Verify immutable reviewed desktop candidate' step runs scripts/verify-desktop-release-merge.sh before the tag is created; every other lane tags $GITHUB_SHA (the merge commit) directly with no equivalent verification step."
    entry_class: FACT
    evidence:
      - ".github/workflows/auto-tag-on-release-pr-merge.yml:96-115"
  - statement: "release.yml triggers only on tags matching the literal glob `desktop-v[0-9]*`."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml:6-10"
  - statement: "docker.yml triggers on tags matching `relay-v[0-9]*`, and its own header comment states the relay is versioned independently of the desktop app via its own relay-v* tags, tracking crates/buzz-relay/Cargo.toml; the same comment states desktop v* tags and agent sprig-v* tags do NOT publish this image."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml:1-46"
  - statement: "helm-chart.yml triggers on tags matching `chart-v[0-9]*` (workflow_dispatch aside) and its own header comment states the chart is versioned independently via its own chart-v* tags (Chart.yaml's `version`, cut by merging a chart-release/<version> PR), and that only chart-v* tags publish -- ordinary main pushes and PRs stay lint/render-only."
    entry_class: FACT
    evidence:
      - ".github/workflows/helm-chart.yml:1-36"
  - statement: "push-gateway-helm-chart.yml triggers on tags matching `push-chart-v[0-9]*` and publishes to the OCI target ghcr.io/block/buzz/charts; its workflow_dispatch inputs are described as 'Chart semver (without push-chart-v prefix)' and 'Matching push-chart-v tag'."
    entry_class: FACT
    evidence:
      - ".github/workflows/push-gateway-helm-chart.yml:1-20"
  - statement: "scripts/mobile-release.sh's usage text describes its one subcommand as `candidate X.Y.Z`, publishing 'the next immutable mobile-vX.Y.Z-rc.N candidate tag at the exact current commit of block/buzz's remote main branch'; require_clean_semver enforces the strict regex `^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)$` on the X.Y.Z input -- no leading zeros and no pre-release suffix accepted from the operator, unlike the desktop/relay/chart/push-chart lanes' looser `-suffix`-permitting regex."
    entry_class: FACT
    evidence:
      - "scripts/mobile-release.sh:1-45"
  - statement: "scripts/mobile-release.sh derives the next `-rc.N` candidate number by listing existing remote tags matching `refs/tags/mobile-v${version}-rc.*` via `git ls-remote --refs --tags origin` and constructs `tag=\"mobile-v${version}-rc.${next}\"` -- the integer is auto-incremented from observed remote tags, not operator-supplied."
    entry_class: FACT
    evidence:
      - "scripts/mobile-release.sh:118-131"
  - statement: "RELEASING.md states mobile candidate tags are published 'through the dedicated buzz-release-bot GitHub App' rather than through a merged PR, and that the script 'never uses the operator's checked-out commit and never moves an existing candidate' -- distinguishing the mobile lane from the four PR-merge-triggered lanes in auto-tag-on-release-pr-merge.yml."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "crates/sprig/Cargo.toml's own header comment states sprig 'ships as a pinnable artifact (sprig-v* tags), released on its own cadence' and does not inherit the workspace version; its `version` field is `0.1.0`."
    entry_class: FACT
    evidence:
      - "crates/sprig/Cargo.toml:1-7"
  - statement: "sprig.yml triggers a versioned release on tags matching the loose glob `sprig-v*`, while sprig-image.yml (a separate workflow publishing the multi-arch OCI image ghcr.io/block/buzz-sprig) triggers on the stricter `sprig-v[0-9]*` and its changelog-generation step documents the parser pattern `^sprig-v(.*)$` for stripping the prefix."
    entry_class: FACT
    evidence:
      - ".github/workflows/sprig.yml:14-20"
      - ".github/workflows/sprig-image.yml:14-26"
  - statement: "No script, Justfile recipe, or workflow step in this repository was found that creates or pushes a sprig-v* tag; searching every file for the literal string 'sprig-v' surfaces only the two consuming workflows (sprig.yml, sprig-image.yml), docker.yml's exclusion comment, the Cargo.toml header comment, and two corpus prose mentions -- none of them a producer. How a sprig-v* tag actually gets created is expected but not verified by this node; see Scope and omissions."
    entry_class: FACT
    evidence:
      - "grep_repository(pattern='sprig-v') -> .github/workflows/docker.yml, .github/workflows/sprig.yml, .github/workflows/sprig-image.yml, crates/sprig/Cargo.toml, docs/remote-agents.md, launchpad/docs/corpus/architecture/containers/agent-runtime.md, launchpad/docs/corpus/layers/compute/sprig-runtime.md -- no script or workflow step creates the tag"
  - statement: "The merged corpus node layers-compute-sprig-runtime records that 'sprig ships as a pinnable artifact released on its own cadence via sprig-v* tags' and that sprig.yml and sprig-image.yml are the two workflows sharing that tag family, one building a musl tarball and the other the OCI image -- consistent with what this node found directly in the workflow files."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/compute/sprig-runtime.md:21"
      - "launchpad/docs/corpus/layers/compute/sprig-runtime.md:61"
  - statement: "Querying block/buzz's tag list directly (the upstream repository RELEASING.md and the ruleset both describe) shows a bare, unprefixed `v<version>` series (v0.0.1 through v0.5.2) immediately preceding the first `desktop-v*` tag, and a separate, even older `desktop/v<version>-rcN` slash-form series (desktop/v0.1.0-rc2 through -rc12) with no `desktop-v*` or bare-`v*` equivalents at that vintage -- two historical naming schemes distinct from every scheme above."
    entry_class: FACT
    evidence:
      - "gh_api(endpoint='repos/block/buzz/tags', paginate=true) -> v0.0.1..v0.5.2 (bare series), desktop/v0.1.0-rc2..rc12 (slash series), both with no later occurrences"
  - statement: "desktop-v0.5.3 is a real tag on block/buzz while desktop-v0.5.0, desktop-v0.5.1 and desktop-v0.5.2 are not (their bare v-form equivalents are the ones that exist), and ADR-0041 independently records desktop-v0.5.3, .4 and .5 as three of six tags it measured as ancestors of the launchpad/upstream merge-base on 2026-08-26 -- consistent with the bare-v* to desktop-v* rename happening at exactly 0.5.3."
    entry_class: FACT
    evidence:
      - "gh_api(endpoint='repos/block/buzz/git/refs/tags/desktop-v0.5.3') -> 200, ref resolves"
      - "gh_api(endpoint='repos/block/buzz/git/refs/tags/desktop-v0.5.0') -> 404, ref does not exist"
      - "launchpad/decisions/ADR-0041-pin-main-to-relay-desktop-tags.md"
  - statement: "The bare v* and slash-form desktop/v* schemes are superseded: no tag in either form was found created after the desktop-v* switch, and neither scheme's tags are referenced anywhere in RELEASING.md, the release workflows, or scripts/release-rulesets.sh as a still-active target."
    entry_class: INFERENCE
    evidence:
      - "gh_api(endpoint='repos/block/buzz/tags', paginate=true) -> no v<version> or desktop/v<version>-rcN tag postdating the desktop-v* series"
      - "RELEASING.md"
      - "scripts/release-rulesets.sh"
    confidence: 0.75
  - statement: "block/buzz's live Release tag ruleset (id 14378754, target 'tag', enforcement 'active') has conditions.ref_name.include equal to exactly `~ALL, refs/tags/v*, refs/tags/relay-v*, refs/tags/mobile-v*, refs/tags/chart-v*, refs/tags/push-chart-v*, refs/tags/sprig-v*`, with rules creation/deletion/non_fast_forward/update and an empty exclude list -- desktop-v* has no named pattern of its own in this list; scripts/release-rulesets.sh's own require_release_tag_ruleset check only ever asserts that refs/tags/mobile-v* is present in that include list, and asserts nothing about desktop-v*."
    entry_class: FACT
    evidence:
      - "scripts/release-rulesets.sh:26-45"
      - "gh_api(endpoint='repos/block/buzz/rulesets/14378754') -> conditions.ref_name.include: ['~ALL','refs/tags/v*','refs/tags/relay-v*','refs/tags/mobile-v*','refs/tags/chart-v*','refs/tags/push-chart-v*','refs/tags/sprig-v*'], rules: creation,deletion,non_fast_forward,update, exclude: [], enforcement: active"
  - statement: "RELEASING.md's own Prerequisites section states: 'Release tag ruleset 14378754 active for `desktop-v*` and `mobile-v*`, with creation, update, deletion, and non-fast-forward protections and `buzz-release-bot` as its sole always-bypass actor.'"
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "RELEASING.md's prose therefore names desktop-v* as one of the ruleset's two protected patterns, but the ruleset's own conditions carry no refs/tags/desktop-v* entry; desktop-v* tags are protected only because the blanket `~ALL` entry matches every tag ref, not because of a pattern naming them. RELEASING.md's claim and the ruleset's measured configuration describe the same protection outcome for desktop-v* today, but disagree about the mechanism -- a named pattern versus the wildcard catch-all -- and RELEASING.md does not mention the wildcard or the other four named patterns (v*, chart-v*, push-chart-v*, sprig-v*) at all."
    entry_class: INFERENCE
    evidence:
      - "gh_api(endpoint='repos/block/buzz/rulesets/14378754') -> ref_name.include has no refs/tags/desktop-v* entry, but does have '~ALL'"
      - "RELEASING.md"
    confidence: 0.9
  - statement: "The Release tag ruleset (14378754) lives on block/buzz (upstream); querying rulesets on this fork, launchpad-26/buzz, returns an empty list -- this fork carries no equivalent tag-protection ruleset of its own."
    entry_class: FACT
    evidence:
      - "gh_api(endpoint='repos/launchpad-26/buzz/rulesets') -> []"
      - "gh_api(endpoint='repos/block/buzz/rulesets') -> [Default (13596885), Mobile Release Branches (19321162), Release (14378754)]"
  - statement: "This fork's own docker.yml (distinct from upstream's) builds and publishes ghcr.io/launchpad-26/buzz from relay-v*.*.* tags on this repository, and the merged corpus node architecture-containers-relay records the same fact and the same distinction from upstream's ghcr.io/block/buzz image."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml:1-10"
      - "launchpad/docs/corpus/architecture/containers/relay.md:103"
  - statement: "Three merged corpus container nodes already state a tag-format fact for their own lane as part of describing that container: architecture-containers-desktop states the desktop-v<version> format and its Buildkite consumer; architecture-containers-mobile states the mobile-vX.Y.Z-rc.N format, its publisher script, and the per-platform-candidate-number behavior; architecture-containers-relay states the relay-v*.*.* trigger and this fork's own image distinct from upstream's."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/desktop.md:89"
      - "launchpad/docs/corpus/architecture/containers/mobile.md:81"
      - "launchpad/docs/corpus/architecture/containers/relay.md:103"
  - statement: "Three rolling, non-versioned pointer tags/releases were observed on block/buzz's tag list -- sprig-latest, sprout-agent-bundle-latest, sprout-desktop-latest -- none matching any release-tag pattern in this node's table; sprig.yml's own header separately confirms sprig-latest is a 'rolling' release updated on every push to main, distinct from its versioned sprig-v* release."
    entry_class: FACT
    evidence:
      - "gh_api(endpoint='repos/block/buzz/tags', paginate=true) -> sprig-latest, sprout-agent-bundle-latest, sprout-desktop-latest present alongside the versioned series"
      - ".github/workflows/sprig.yml:14-20"
  - statement: "A tag named mobile-v0.0.0-ruleset-smoke.20260720214945 was observed on block/buzz's tag list. It matches no producer script, workflow trigger, or documented scheme found by this node -- grepping the repository for 'ruleset-smoke' returns no results -- so it is recorded here as an unexplained artifact, not as evidence of a sixth naming scheme."
    entry_class: FACT
    evidence:
      - "gh_api(endpoint='repos/block/buzz/tags', paginate=true) -> mobile-v0.0.0-ruleset-smoke.20260720214945 present"
      - "grep_repository(pattern='ruleset-smoke') -> no matches"
  - statement: "Issue #1299 requires that this document does not duplicate #1292/#1293/#1294's procedure content and instead documents the tag naming scheme(s), and that a tag scheme must not be invented -- only recorded with evidence, with gaps named."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1299 dispatch instructions"
  - statement: "At the time this node was drafted, issues #1292, #1293 and #1294 (the desktop-candidate, desktop-release and mobile-candidate procedure tasks under the same releases/ directory) were all still open, and launchpad/docs/corpus/releases/ did not yet exist on origin/launchpad -- so this node declares no relationships toward them and cannot rely on their content having landed."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "gh issue view 1292/1293/1294 --json state, checked 2026-09-02"
---

# Release tags: reference

This node catalogues every git tag naming scheme this repository's release
automation creates or reacts to for candidate and release artifacts, what each
scheme's version syntax is, what creates a tag in that scheme, what it
triggers, and how (or whether) the upstream tag-protection ruleset covers it.
It is linked from the per-lane container nodes
(`architecture-containers-desktop`, `architecture-containers-mobile`,
`architecture-containers-relay`, `layers-compute-sprig-runtime`), each of
which states its own lane's tag format as one fact among many about that
container; this node is the place those facts are gathered, compared, and
checked against each other and against the live ruleset. It does not describe
*how* to run a release end to end — that is `RELEASING.md`'s job today, and
`launchpad/docs/corpus/releases/desktop-candidate.md`,
`desktop-release.md` and `mobile-candidate.md`'s job once those tasks land.

## Tag naming schemes

| Pattern | Version syntax | Created by | Triggers / publishes | Ruleset coverage |
|---|---|---|---|---|
| `desktop-v<version>` (e.g. `desktop-v0.5.18`) | `X.Y.Z` with optional free-form `-suffix`, matched by `^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$` and the trigger glob `desktop-v[0-9]*` | `auto-tag-on-release-pr-merge.yml`, on merge of a `version-bump/<v>` branch to `main`; tagged at the exact PR head SHA after `scripts/verify-desktop-release-merge.sh` passes | `release.yml` — packaged desktop app (macOS/Windows/Linux) | Covered only by the ruleset's blanket `~ALL` entry; no `refs/tags/desktop-v*` pattern is named |
| `relay-v<version>` (e.g. `relay-v0.2.1`) | same regex as desktop-v; trigger glob `relay-v[0-9]*` | same workflow, `relay-release/<v>` branch merge; tagged at the merge commit | `docker.yml` — relay container image (`ghcr.io/launchpad-26/buzz` on this fork; `ghcr.io/block/buzz` upstream) | Named pattern `refs/tags/relay-v*` |
| `chart-v<version>` (e.g. `chart-v0.x.x`) | same regex; trigger glob `chart-v[0-9]*` | same workflow, either a `chart-release/<v>` branch merge, or automatically on any merged PR whose diff bumps `deploy/charts/buzz/Chart.yaml`'s `version`; tagged at the merge commit | `helm-chart.yml` — main Helm chart, published as an OCI artifact | Named pattern `refs/tags/chart-v*` |
| `push-chart-v<version>` (e.g. `push-chart-v0.2.0`) | same regex; trigger glob `push-chart-v[0-9]*` | same workflow, `push-chart-release/<v>` branch merge; tagged at the merge commit | `push-gateway-helm-chart.yml` — the `deploy/charts/buzz-push-gateway` chart, to `ghcr.io/block/buzz/charts` | Named pattern `refs/tags/push-chart-v*` |
| `mobile-v<version>-rc.<N>` (e.g. `mobile-v0.5.0-rc.3`) | version is strict clean semver `X.Y.Z` (`^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$`, no leading zeros, no operator-supplied suffix); `N` is an integer auto-incremented from existing remote `mobile-v<version>-rc.*` tags | `scripts/mobile-release.sh candidate X.Y.Z`, pushed directly (not via PR merge) by the `buzz-release-bot` App, at the exact current `origin/main` commit; never moves an existing candidate | Private Buzz mobile Buildkite pipeline via an exact `mobile_ref`; no GitHub Release, no stable alias, immutable | Named pattern `refs/tags/mobile-v*` |
| `sprig-v<version>` (e.g. sprig's own crate version `0.1.0`) | semver, digit-led per the `sprig-v[0-9]*` (image) / `sprig-v*` (binary) trigger globs | **Unverified** — no script, Justfile recipe, or workflow step creating this tag was found; assumed manual `git tag && git push` | `sprig.yml` (static-musl tarball release) and `sprig-image.yml` (multi-arch OCI image `ghcr.io/block/buzz-sprig`) | Named pattern `refs/tags/sprig-v*` |
| `v<version>` (bare, e.g. `v0.5.2`) — **historical, superseded** | plain `X.Y.Z` | No longer created; superseded by `desktop-v<version>` starting at `desktop-v0.5.3` | Historically the desktop release lane, before the rename | Named pattern `refs/tags/v*` remains in the ruleset |
| `desktop/v<version>-rcN` (slash form, e.g. `desktop/v0.1.0-rc12`) — **historical, superseded** | `X.Y.Z-rcN` | No longer created; the earliest observed desktop pre-release scheme, predating the bare `v*` series | Historically an early desktop pre-release | No named pattern; would fall under `~ALL` only |

**Not release-tag schemes**, excluded from the table above: `sprig-latest`,
`sprout-agent-bundle-latest` and `sprout-desktop-latest` are rolling pointer
tags/releases that move to track `main` rather than naming one immutable
version — `sprig.yml`'s own header confirms `sprig-latest` updates on every
push to `main`. A further tag, `mobile-v0.0.0-ruleset-smoke.20260720214945`,
was observed but matches no producer or documented scheme; it is recorded
under *Scope and omissions* as an unresolved anomaly, not as a seventh scheme.

## Boundary

This node does not describe:
- **How to run a release end to end** for any lane — that is `RELEASING.md`
  today, and the not-yet-landed `desktop-candidate.md` / `desktop-release.md`
  / `mobile-candidate.md` procedure nodes (issues #1292–#1294) once merged.
- **Why each lane versions independently**, or the architectural reasoning
  for per-container release cadence — that belongs to the container nodes
  this one is `references`d from.
- **Repository rulesets in general** — only the one Release tag ruleset
  bearing on these tag patterns is in scope here.
- **Any node-specific exclusion**: the rolling `-latest` tags/releases and the
  one unexplained smoke-test tag, both named above.

## Relationships

- references: architecture-containers-desktop
- references: architecture-containers-mobile
- references: architecture-containers-relay
- references: layers-compute-sprig-runtime

Each target already states, as one fact among several about its own
container, the tag format this node catalogues in full; the edge points a
reader from this catalogue to the architectural context for *why* that
lane's artifact exists, without this node repeating that context. At the
recorded revision, no edge was declared toward `desktop-candidate.md`,
`desktop-release.md` or `mobile-candidate.md`: none of the three existed yet
on `origin/launchpad`, confirmed by `ls launchpad/docs/corpus/releases/`
rather than assumed. All three have since landed in this same integration,
so the natural edges now resolve. They are not added here: wiring them in
under the pressure of a pre-merge fix pass risks the same kind of error this
fix pass exists to catch. Adding them belongs to a dedicated pass across the
whole `development`/`governance`/`releases` shelf once all 37 nodes are
stable.

## Note on Definition of Done

Issue `#1299`'s Definition of Done carries the same four tail bullets found
verbatim on its `releases/` siblings #1292–#1294 — "states goal, prerequisites
and allowed environment/scope," "provides ordered steps that are executable
and project-specific," "defines success verification and rollback/cleanup
where relevant," "links authoritative commands/config rather than giving
generic advice." That checklist describes a **procedure** node — the shape
`#1292`–`#1294` actually need, since each documents one step-by-step release
flow. This issue's own subject — the tag naming scheme(s) this repository
uses — has no steps to order and no rollback to define: it is a lookup fact
(what does a tag named X mean, what created it, what does it trigger), the
same shape `corpus-template-reference` describes as *"technical descriptions
of the machinery and how to operate it"* rather than task instruction. This
node is built against the **reference** template's required sections —
reference description, structured entries, boundary, relationships, scope and
omissions — above, on the same reasoning `corpus-template-reference` itself
gives for departing from a copied-over checklist that does not fit the
document's actual shape.

## Scope and omissions

**This node covers** the git tag naming schemes this repository's release
automation creates or reacts to: their version syntax, what creates each one,
what it triggers, and each scheme's coverage under the live upstream tag
ruleset, including two historical schemes and the drift found between
`RELEASING.md`'s prose and the ruleset's measured configuration.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The desktop release procedure end to end | `releases/desktop-candidate.md`, `releases/desktop-release.md` |
| The mobile candidate procedure end to end | `releases/mobile-candidate.md` |
| The relay, chart and push-chart release procedures end to end | `RELEASING.md` |
| Container-level architectural context for each lane | `architecture-containers-desktop`, `architecture-containers-mobile`, `architecture-containers-relay`, `layers-compute-sprig-runtime` |
| Whether `RELEASING.md`'s ruleset-prerequisites text should be corrected to match the measured `~ALL`-plus-five-named-patterns configuration | Not filed by this node; a documentation-accuracy fix, not a corpus-content gap |

**Expected but not verified when this node was written:**

- **What actually creates a `sprig-v*` tag.** No script, recipe or workflow
  step doing so was found in this repository; the mechanism is assumed
  manual and is recorded as unverified in the table above.
- **What created `mobile-v0.0.0-ruleset-smoke.20260720214945`.** No producer
  or documented purpose was found for this tag; it is recorded as an
  unexplained anomaly rather than folded into any scheme above.
- **The exact commit or PR that renamed the desktop lane from bare `v*` to
  `desktop-v*`.** This node establishes the boundary is at `desktop-v0.5.3`
  (that tag exists, `desktop-v0.5.0`–`.2` do not, and ADR-0041 corroborates
  `desktop-v0.5.3` as real) but did not locate the workflow-history commit
  that made the switch.
- **Whether the ruleset's `refs/tags/v*` and `refs/tags/desktop/v*`-shaped
  coverage is deliberate historical-tag protection or leftover configuration**
  — this node reports the include list as measured and does not speculate
  about ruleset authoring intent beyond what `RELEASING.md` and
  `scripts/release-rulesets.sh` state.
