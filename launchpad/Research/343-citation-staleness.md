---
description: Whether existing controls detect when a cohort document's citations to upstream files become stale — the handbook design does, but a document in this repository is outside that mechanism.
tags: [documentation, upstream, citations, staleness, handbook, research, issue-343]
---

# How is a testing document's citation to upstream kept current?

All repository references below were checked at
`5d76799d6e44f2f76aa7bd78c5343d339af98f63`.

## Finding

The accepted handbook design specifies a mechanical, git-based staleness detector that can track
files in upstream repositories. It applies to pages in the separate `launchpad-26/handbook`
repository because those pages carry the provenance frontmatter and appear in the published page
index. A methodology document committed only under `launchpad/` in this repository does not satisfy
that input contract and is therefore **not covered** by either specified detection path.

This establishes the design boundary, not the operating state. I did not inspect the private
handbook repository and did not verify that its scheduled job or published index exists and runs.

## What each decision record contributes

| Record | Mechanism | Does it cover an upstream citation changing? |
|---|---|---|
| ADR-0003 | Every handbook page records each source's `repo`, `ref`, full commit SHA, and paths; references link to the pinned SHA. | **Yes, as the input contract.** A `block/buzz` source is representable. It detects nothing by itself. |
| ADR-0004 | A scheduled job fetches each source ref, fails if the pin is not its ancestor, then runs `git log <pin>..<head> -- <paths>`. Non-empty output flags the page. | **Yes, mechanically.** A change to a cited upstream path produces a flag; movement is detected, not semantic invalidity. |
| ADR-0010 | Upstream-intelligence may read the handbook's published page index and flag affected handbook pages without reproducing private source details. | **Yes, as an additional handbook-only signal.** It depends on the page being in the published index and does not replace ADR-0004. |
| ADR-0015 | Every handbook page is agent-drafted, provenance-gated, and human-reviewed; v1 has a 100% human-review floor. | **Only at authoring/reverification time.** Review can judge whether a moved source invalidates a claim, but it is not the movement detector. |

ADR-0001 fixes the scope: the handbook lives in a dedicated private repository and is published to
an organisation-restricted site. That is why a page in `launchpad-26/buzz` is not automatically a
handbook page merely because it follows similar markdown conventions.

## How ADR-0004 would fire

For a handbook page citing `desktop/playwright.config.ts` in `block/buzz`, ADR-0003 supplies:

```yaml
repo: block/buzz
ref: main
commit: <full 40-character pin>
paths:
  - desktop/playwright.config.ts
```

ADR-0004 then specifies the equivalent of:

```bash
git fetch origin main
git merge-base --is-ancestor "$commit" FETCH_HEAD || exit 1
git log --oneline "$commit"..FETCH_HEAD -- desktop/playwright.config.ts
```

If the path moved after the pin, the final command is non-empty and the page is listed for review.
If history diverged, the ancestor check fails closed instead of allowing `git log A..B` to return an
empty false negative. A flag means “the cited file moved”; a human or agent must still decide
whether the page's claim changed.

## Why a document in this repository is outside it

Both specified paths are keyed on handbook inventory:

1. ADR-0004 iterates `sources[]` attached to handbook pages and emits a handbook page report plus
   a page-to-sources index.
2. ADR-0010 consumes that published page index and names the affected handbook page.

No decision record says either mechanism scans arbitrary markdown in `launchpad-26/buzz`, and this
repository does not publish those documents into the handbook index. A methodology document placed
only here therefore has pinned links for reproducibility but no specified owner that advances or
rechecks them when upstream changes.

## Available options if the document remains here

These are options, not a decision:

- **Put the authoritative document in the handbook.** It inherits the specified provenance,
  staleness, and 100% v1 review controls, at the cost of org-restricted visibility.
- **Add this repository to the same provenance/index pipeline.** This preserves public placement but
  requires extending a handbook-scoped contract and maintaining CI or scheduled-job integration.
- **Add a narrower periodic upstream-diff review.** Record the pinned commit and paths, then report
  when those paths move. This is mechanically small but creates a second staleness mechanism to own.
- **Accept manual reverification.** Keep full-SHA citations and state that they are unmonitored. This
  costs no automation but knowingly allows silent staleness between reviews.
- **Use two artifacts.** Keep the monitored source in the handbook and a short public pointer here.
  This improves reach but creates an alignment obligation between the pointer and authoritative page.

Choosing among them determines placement, visibility, review policy, and ongoing ownership. Under
`launchpad/AGENTS.md` §4, that is an ADR decision rather than a choice for this research note.

## Security boundary

ADR-0010 permits a flag to name the handbook page but forbids reproducing its private source repo,
path, or pinned commit into a channel with different membership. Any extension of the mechanism must
preserve that rule. It matters because the handbook index includes private repositories even though
the example `block/buzz` source is public.

## Confidence and what was not checked

**High confidence in the specified scope.** ADR-0003 defines the page inputs, ADR-0004 defines the
git comparison, ADR-0010 defines the second index-driven signal, ADR-0015 defines the review floor,
and ADR-0001 locates the corpus in a separate repository.

**Not verified:**

- Whether ADR-0004's scheduled job has been implemented or currently runs.
- Whether the published handbook page index exists and matches ADR-0003's contract.
- Whether any current handbook page cites `block/buzz` or another external repository.
- The contents of the private `launchpad-26/handbook` repository.
- The job's actual schedule and maximum staleness interval.
- Any implementation under `.github/workflows/`; this answer establishes what the accepted records
  specify, not that the specification shipped.

## Sources

- `launchpad/decisions/ADR-0001-handbook-repository-location-and-publication-target.md`
- `launchpad/decisions/ADR-0003-handbook-page-provenance-contract.md`
- `launchpad/decisions/ADR-0004-handbook-staleness-detection-mechanism.md`
- `launchpad/decisions/ADR-0010-upstream-intel-handbook-staleness-link.md`
- `launchpad/decisions/ADR-0015-handbook-page-authoring-mode.md`
