---
status: Accepted
date: 2026-08-18
issue: launchpad-26/buzz#193
decided_in: launchpad-26/buzz#193
supersedes: none
---

# ADR-0017 — Hermit lefthook pin becomes a fourth upstream-boundary exception

## Decision

**Add a fourth documented exception**, scoped to exactly `bin/lefthook` and
`bin/.lefthook-*.pkg`, to `launchpad/AGENTS.md` §3's "never rename upstream files" rule.

PR #192 fixes a real bug (#196): this fork's default branch is named `launchpad`, colliding with
the top-level `launchpad/` directory, so Hermit-pinned lefthook 2.1.3's `@{push}`-unavailable
fallback crashes every pre-push command with an ambiguous-argument error on any branch's first
push. The fix bumps the Hermit pin to 2.1.10, which renames `bin/.lefthook-2.1.3.pkg` and modifies
`bin/lefthook` — both also tracked by `block/buzz`, and neither on the exception list as filed.

## Context

Two options were seriously considered (a third, broadening the exception to any Hermit-pinned
tool, was rejected outright as reopening the exact upstream-merge friction the boundary rule
exists to prevent):

1. Add the exception, unblocking every contributor's first push immediately.
2. Hold the fork's fix until `block/buzz` accepts the same bump upstream.

Option 2 was weighed differently than when #193 was first filed: the same bump was briefly
opened upstream as block/buzz#6180, then closed — the cohort is not sending PRs upstream at the
moment. That removed the forcing function that would have made option 2 temporary. Holding the
fix would mean every contributor keeps hitting the crash (or keeps typing `--no-verify`, quietly
losing local/CI check parity) indefinitely, with nothing driving a resolution — a worse steady
state than a documented, narrow exception, not a safer one.

The exception's actual cost is bounded: `bin/lefthook` and `bin/.lefthook-*.pkg` are two symlinks
whose content is a version string. A future `block/buzz` merge touching either conflicts on one
line, resolved by taking whichever version is newer — not the wholesale-restructuring conflict
the boundary rule was written against. Codex (`codex review`) independently reproduced the crash
and confirmed lefthook 2.1.10 fixes it and that no other change (a `lefthook.yml` workaround, a
regression test) was needed, before this boundary question was the only thing left open.

## Consequences

**Good.** Unblocks every contributor's first-push pre-push hooks immediately, without waiting on
an upstream review cycle that isn't currently happening. The exception is narrow — exactly two
files, both symlinks — not a blanket carve-out for future tool bumps.

**Bad, stated honestly.** `AGENTS.md` §3's exception list, which read "closed" with three
entries, grows to four; the next contributor reading it sees a boundary that has already moved
once. This is a **standing** divergence, not a temporary one: every future merge from
`block/buzz` touching `bin/lefthook` or `bin/.lefthook-*.pkg` conflicts on this one symlink pair
and needs manual resolution, recurring until upstream independently catches up or the cohort
resumes sending fixes upstream — neither of which this decision commits to.

## Security implications

Lefthook executes shell commands defined in `lefthook.yml` as part of every commit and push — a
compromised release would be a real supply-chain concern. That risk exists at whichever version
is pinned, not created by this exception; Hermit's package channel resolves and verifies the
release artifact the same way regardless of version. No new trust boundary, execution privilege,
or data exposure follows from adding this exception.

## Provenance

Decided by @serina-mcfall directly in conversation on 2026-08-18, after asking for and receiving
a recommendation (option 1, for the reasons in Context above) against the three options drafted
in #193.
