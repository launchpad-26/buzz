---
status: Accepted
date: 2026-08-27
issue: launchpad-26/buzz#1502
decided_in: launchpad-26/buzz#1502
supersedes: none
---

# ADR-0051 — Cohort Settings sections register through a seam, not per-panel edits

## Decision

**Option B, selected by @serina-mcfall on 2026-08-27 in #1502.**

A cohort-authored Settings section is registered through a **registration seam** added once
to `desktop/src/features/settings/ui/SettingsPanels.tsx`. The cohort's own section
descriptors and components live under `launchpad/`, and appending one is an additive
fork-owned change that touches no upstream file.

The seam is a **single bounded divergence** in one upstream file, granted as a named §3
exception by this record. Adding a second, third or tenth cohort panel after it costs zero
further upstream edits — which is the property the decision was made for.

This rejects **option A** (edit the four registration sites in place for every panel),
**option C** (surface cohort help outside Settings entirely), and **option D** (send the
seam to `block/buzz` first and wait).

## Context

#551's definition-of-done item 2 requires a Settings entry for the knowledge crate, and
#524 needs the same for the telemetry-profiles crate. Neither could execute, because
`launchpad/AGENTS.md` §3 closes its exception list with *"any further exception needs its
own ADR"* — and registering a Settings section needs one.

**There is no seam today.** At `origin/launchpad`, registration is four hardcoded sites in
`SettingsPanels.tsx`:

| Site | What |
|---|---|
| `:82-98` | the `SettingsSection` union — 16 string literals |
| `:102-119` | `SETTINGS_SECTION_VALUES`, backing the `isSettingsSection` type guard |
| `:151` | `settingsSections: SettingsSectionDescriptor[]` — nav label and `LucideIcon` |
| `:819` | the `renderSettingsSection` switch |

`SettingsSectionDescriptor.featureGate` is not an alternative: it gates the visibility of an
**already-registered** section. Nor is "another feature's card appears in Settings" a seam —
`CommunityMembersSettingsCard`, `LocalArchiveSettingsCard` and `MeshComputeSettingsCard` are
direct imports plus the same four edits.

The four sites are type-coupled: `renderSettingsSection`'s `default` branch asserts
`const exhaustiveCheck: never = section`, so widening the union without adding a case is a
compile error. That makes option A safe against silent drift, and does nothing about its
merge cost.

**Two measurements decided it.**

*This would have been the fork's first edit to upstream's React source.* Every existing
desktop divergence is Rust under `src-tauri/`:

```
$ git diff --name-only --diff-filter=M upstream/main...origin/launchpad -- desktop/
desktop/src-tauri/crates/buzz-terminal/src/lifecycle.rs
desktop/src-tauri/crates/buzz-terminal/src/shell.rs
desktop/src-tauri/src/managed_agents/restore.rs
desktop/src-tauri/src/managed_agents/runtime.rs
desktop/src-tauri/src/managed_agents/runtime_commands.rs
```

*And the file upstream keeps reshaping is the one option A would edit repeatedly.*
`SettingsPanels.tsx` is 883 lines with 51 commits, including
`43e53fc34 Standardize settings section layout (#5855)` and
`cd2aa5c12 Add glass appearance and cohesive settings (#5478)` — both of which restructured
the exact arrays. Compare #307's measurement that edits to existing upstream files *"are the
entire conflict surface"*, with 4 of 27 such files conflicting across 67 upstream commits.

A per-panel divergence in four hunks of that file grows with every cohort surface and pays
on every sync. A one-time seam pays once.

## Consequences

- **`SettingsPanels.tsx` carries one standing divergence.** It is visible, bounded, and does
  not grow as cohort panels are added.
- **Every future cohort Settings panel is additive**, lives under `launchpad/`, and needs no
  ADR and no upstream edit. That is the same generic-exception shape `ADR-0030` (#1401) used
  for root skill registration, deliberately followed here.
- **The union type has to widen** to admit registry-supplied keys alongside the 16 literals,
  without losing the exhaustiveness guarantee for upstream's own sections. This is the real
  design cost of the option and it lands on #551, not on this record.
- **The seam can still conflict.** If upstream restructures the registry itself, the
  divergence conflicts like any other in-place edit — one file instead of four hunks, but not
  zero. Accepted knowingly; option D was the only zero-conflict choice and it costs schedule
  control.
- **The seam is a plausible upstream contribution.** Nothing here commits to sending it, and
  option D was rejected as a *precondition*, not as a later possibility. If it is ever
  accepted upstream, this exception retires rather than being amended.
- **§3 gains a seventh named exception**, amended in this same pull request so the two
  documents do not disagree. Owed a row in the divergence ledger once `ADR-0047` (#294)
  provides one; the ledger does not exist yet.
- **`launchpad/scripts/adr_boundary_check.py` cannot see this divergence.** It validates only
  `ADR-0005`'s deployment-file list against §3, so nothing mechanically detects the seam being
  widened past what this record grants. Recorded rather than solved; #1499 carries the wider
  gap.

## Security implications

No security, trust, or authority consequence. The options differed in where a UI section is
registered and how the fork diverges from upstream's frontend, not in what any user can
reach, read, or be authorised for. The knowledge crate's own exposure is governed by PRD #4's
security section and is unchanged by where its entry point is declared. Every source cited is
a public `launchpad-26/buzz` or `block/buzz` file, read read-only.

## Supersedes

none

## Amends

`launchpad/AGENTS.md` §3, by adding the `SettingsPanels.tsx` registration seam as a named
exception. This extends `#13:decision-2`'s list of two `.github/` exceptions in the same way
`ADR-0045` did; the underlying closed-list rule — that any further exception needs its own
ADR — is untouched.

## Related

- **`ADR-0045` (#1409)** — cohort Rust crates under `launchpad/crates/`. Same closed-§3
  question, different artifact class: a build manifest rather than a UI registry. #1409
  required adjacent boundary ADRs to cite each other rather than merge, and left the Settings
  question as unresolved evidence; this record closes that item.
- **`ADR-0043`** — prefer a fork-owned override to an in-place edit. The reason option B
  exists and option A was disfavoured. Noted honestly: `ADR-0043` is itself `status: Proposed`
  (#1499), so this record relies on an unratified ADR for that preference. The measurements
  above stand on their own regardless.
- **`ADR-0030` (#1401)** — precedent for granting a generic exception to a mechanism rather
  than to the instance that raised it.
- **#307** — in-place edit versus fork-owned override, with the conflict-surface
  measurements cited above. Still open; its outcome does not change this decision, which
  chooses the override side it favours.

## Provenance

Drafted and decided the same day. The four registration sites, the exhaustiveness check, the
absent seam, the `desktop/src` divergence result and the churn counts were each read from
`origin/launchpad` rather than recalled; the option set and its costs are #1502's. @serina-mcfall
selected option B from the four presented there; the agent recorded that selection and did not
make it.

**Not verified:** no seam was implemented or compiled as part of this record, so the claim that
the union can widen without losing exhaustiveness for upstream's own sections is a design
expectation, not a measured result. It is #551's to demonstrate. Option C's own open question —
whether a cohort-owned route could exist without an upstream edit — was never settled, because
the option was rejected for other reasons.
