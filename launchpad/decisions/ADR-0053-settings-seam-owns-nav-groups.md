---
status: Accepted
date: 2026-08-31
issue: launchpad-26/buzz#1940
decided_in: launchpad-26/buzz#1940
supersedes: none
amends: ADR-0051
---

# ADR-0053 — The Settings seam owns sidebar nav groups; SettingsView is not a second exception

## Decision

**Option A, selected by @benmitchell11 on 2026-08-31 in #1940.**

The registration seam granted by
[ADR-0051](ADR-0051-cohort-settings-registration-seam.md) also owns **sidebar
nav-group membership**. `settingsNavGroups` (the upstream hardcoded groups) and
the synthesis of cohort groups from each descriptor's `navGroup` live in
`desktop/src/features/settings/ui/SettingsPanels.tsx`.

`SettingsView.tsx` consumes that export. It is **not** a second §3 exception.
A one-time rewire of `SettingsView.tsx` to import `settingsNavGroups` and delete
its local list is the implementation of this seam for #551, not a standing grant
to keep editing that file.

Adding a second, third, or tenth cohort panel still costs zero further upstream
edits. The standing exception remains **one file**.

This rejects **option B** (name `SettingsView.tsx` as a second standing
exception) and **option C** (drop the sidebar item from #1935 and leave #551
incomplete).

The instruction, quoted verbatim: "go for a". Recorded by an agent under
[ADR-0052](ADR-0052-delegated-authority-and-feature-batching.md) delegated
authority; the agent did not select the option.

## Context

ADR-0051 listed four hardcoded registration sites in `SettingsPanels.tsx` and
granted a seam in that one file. It did not name a fifth site:
`settingsNavGroups` in `SettingsView.tsx`. A cohort section registered through
the seam renders (direct navigation) but never appears in the sidebar unless
that list grows or is synthesized.

#1935 implemented the seam and synthesized groups inside `SettingsView.tsx`.
That matched ADR-0051's *intent* (later panels cost zero further upstream edits)
and violated its *grant* (one file). Review requested changes. #551 is not done
without a sidebar entry.

## Consequences

- **`SettingsPanels.tsx` still carries one standing divergence.** It is larger
  than ADR-0051 described — it now also exports nav groups — and it still does
  not grow as cohort panels are added.
- **`SettingsView.tsx` is touched once** to import the export. Anyone reading
  §3 as "zero SettingsView edits ever" needs this record. After that rewire,
  further cohort panels must not edit it.
- **If upstream reshapes `settingsNavGroups` in place**, the conflict moves
  into `SettingsPanels.tsx` with the rest of the seam. Accepted; the alternative
  was a second standing file.
- **#1935 can finish** by moving synthesis into the granted file and shrinking
  its SettingsView hunk to the import rewire. Stale "#1503 pending" comments
  on that branch should cite this record and ADR-0051 as accepted.
- **§3 is amended in the same pull request** so the exception list and this
  record agree. The list stays closed.

## Security implications

No change to what a user can reach, read, or be authorised for. The options
differed only in which upstream React file owns the sidebar group list.

## Supersedes

none — amends ADR-0051 and the Desktop Settings registration seam bullet in
`launchpad/AGENTS.md` §3. Does not replace #1502.

## Provenance

Decided by @benmitchell11 on 2026-08-31 in the session that reviewed #1935 and
filed #1940. Quoted instruction: "go for a". This record was written by an
agent on that instruction; the agent did not select the option.
