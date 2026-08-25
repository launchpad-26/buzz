---
status: Accepted
date: 2026-08-26
issue: launchpad-26/buzz#294
decided_in: launchpad-26/buzz#294
supersedes: none
---

# ADR-0047 — Standing positions for fork divergences are recorded in a durable ledger

## Decision

The fork maintains a versioned divergence ledger for every upstream-owned file it
modifies or deletes. The ledger is the authoritative record of the fork's standing
position during vendor drops.

The ledger lives at `launchpad/upstream-intel/divergence-ledger.yml`: a single
YAML document, one mapping per row, keyed by the upstream path. No such file
exists yet, and neither does `launchpad/upstream-intel/` — §3 of
`launchpad/AGENTS.md` reserves that directory for "upstream tracking tooling",
which is what the ledger is, and §3 requires everything cohort-specific to live
under `launchpad/`. The format is YAML rather than prose or Markdown because
ADR-0022 states that "The scope is computed, not curated by hand: the contested
surface is the intersection of the divergence ledger's rows with the files
upstream changed in the drop" — a computed intersection needs rows a program can
read without parsing prose.

Each row MUST state the path, classification, position, enforcement mechanism,
rationale or `unrecorded`, security relevance, and a termination condition where
applicable.

Default positions are:

- Cohort-owned material: fork wins.
- Upstream product code and build tooling: upstream wins.
- Generated lockfiles: regenerate; do not preserve either side mechanically.

Exceptions override these defaults:

- The five deployment-provenance files accepted in ADR-0005 retain their fork
  position.
- The pinned binaries accepted in ADR-0017 use newest wins.
- The product-code paths surveyed in #339 are **unrecorded** pending a decision.
  #339 is a `type:task`, not a decision venue — §4.1 of `launchpad/AGENTS.md`
  states that "An ADR is never a work item" — and its output records evidence
  rather than a position. `launchpad/Research/339-divergence-permanence.md`
  found that "The commit history does not identify any of the nine as a
  disagreement with upstream, but author intent was not confirmed", and warned
  that "`runtime.rs` demonstrates why provenance must be recorded by change, not
  only by file: one path can contain both", and that "Recording all nine paths
  as "standing positions" would imply a deliberate product view the cohort has
  never taken". Rows for these paths carry `unrecorded` as their rationale, and a
  later decision on them MAY record provenance at sub-file rather than per-path
  granularity.

Permitted enforcement mechanisms are transforming merge driver, per-path merge
assignment, post-merge assertion, recorded `rerere` replay, and explicit
escalation. Every security-relevant automatic-fork-win row MUST require review on
every vendor drop.

`rerere.autoUpdate` MUST remain disabled for vendor-drop merges.

A converging row MUST include a deterministic upstream-status check and MUST be
removed once upstream has incorporated the equivalent change. That removal is
tracked by a GitHub issue, not by the file: under §2 of `launchpad/AGENTS.md`,
"Stable knowledge belongs in a document. Active work becomes a GitHub issue." The
row states the position that holds today; retiring it is active work and belongs
in the issue tracker, which keeps the ledger documentation rather than a work
tracker.

This outcome was selected by @tucktuck101 in the 2026-08-26 ADR-clearing session.

## Context

The fork adopts upstream through vendor-drop merges while retaining selected,
recorded divergences. ADR-0021 makes the recorded decline the durable mechanism;
ADR-0022 limits drop review to the intersection of upstream-touched files and
ledger rows. A fork-modified upstream file without a ledger row can therefore
avoid adjudication entirely.

A binary fork/upstream flag is insufficient. ADR-0017 requires newest wins for
its pinned binaries, while some divergences apply only to a portion of a file.
The ledger must record both the intended position and a mechanism capable of
enforcing it.

The number of undocumented product-code paths is itself unresolved. #294's body
states "Eight of the undocumented are product code", while
`launchpad/Research/339-divergence-permanence.md` counts nine. This record does
not settle that discrepancy, and does not need to: those paths are unrecorded
either way, and the count is a question for whichever decision records them.

## Consequences

- Every new modification or deletion of an upstream-owned file receives a
  recorded position before it can become an unreviewed divergence.
- The vendor-drop process can compute its contested surface from the ledger.
- Defaults reduce ambiguity for future rows; explicit exceptions preserve
  accepted cohort positions.
- Security-relevant automatic preservation remains visible on every drop rather
  than masking upstream security fixes.
- Converging divergences do not become permanent by inertia.
- **The implementation work this decision creates is not yet filed, and must be.**
  It comprises: creating `launchpad/upstream-intel/divergence-ledger.yml` and
  populating its initial rows; installing the merge drivers and per-path merge
  assignments the enforcement mechanisms require; disabling `rerere.autoUpdate`
  for vendor-drop merges; and wiring the per-drop review of every
  security-relevant automatic-fork-win row. §4.1 of `launchpad/AGENTS.md`
  requires that "Work a decision creates is filed separately afterwards and
  linked back"; at the time of writing no issue exists for any of it.
- The product-code paths surveyed in #339 stay outside the ledger until a
  decision records them, so ADR-0022's contested surface does not yet cover
  them.

## Security implications

Automatic fork wins can retain an outdated dependency, hook binary, deployment
image configuration, or other security-sensitive content despite a later upstream
fix. The ledger therefore marks security relevance explicitly and requires
per-drop review for every security-relevant automatic-fork-win row.

Disabling `rerere.autoUpdate` prevents a replayed resolution from being staged
silently. Recorded `rerere` remains a labour-saving replay mechanism, not an
unreviewed authority to update the merge result.

Because the per-drop security review is not yet filed as work, the ledger's
security-relevance field is currently a recorded requirement with no implemented
enforcement behind it.

## Supersedes

none — this operationalizes ADR-0021 and ADR-0022 without changing either
accepted decision.
