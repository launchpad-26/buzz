---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#300
decided_in: launchpad-26/buzz#300
supersedes: none
---

# ADR-0040 — Bootstrap merge drivers via `just`; do not ship a shared `rr-cache`

## Decision


**This record precedes its implementation.** None of the machinery below exists on
`launchpad` today: `.gitattributes` carries exactly one rule — `* text=auto eol=lf` — with
no `merge=` attribute anywhere, and the `Justfile` mentions neither `rerere` nor a merge
driver. This record names no implementing issue; #300 is the decision venue, not the build,
so the issue that makes these changes still has to be raised. The prose below states what
would be built, not what is there.

The decision: a hybrid of Options A and C — Option A's `just` bootstrap recipe, with
Option C's refusal to share the cache. Custom merge drivers and `rerere` **would be**
bootstrapped by a `just` recipe wired into the existing `just setup`, so every clone that
runs setup gets them. **Both halves are required and neither works alone**: the `merge=`
attribute mapping belongs in `.gitattributes` and ships with the repository, while the
driver *definition* git reads only from config, which is what the bootstrap installs. The
`rr-cache` **would not be** shared: each clone keeps a private cache, and the PRD criterion
"a conflict resolved once is not resolved again" is stated honestly as meaning "the same
person does not resolve the same conflict twice." A bootstrap-detection check **would
confirm** a clone has run setup, so the drivers are actually active rather than apparently
active. `rerere.autoUpdate` **would be pinned off** for drop merges, taking the position
`launchpad/Research/362-sub-file-decline-durability.md` recommends — *"do not enable
`rerere.autoUpdate` on drop merges. An unattended stale replay that stages itself is the
worst available outcome."*

## Context

`rerere` state lives in `.git/rr-cache/` (per-clone, never committed) and custom merge
drivers are defined in git config, not `.gitattributes` — `merge=ours` is inert until every
clone runs `git config merge.ours.driver true`. A `.gitattributes` shipped without the
bootstrap looks like it works and silently does not.

Rejected: sharing `rr-cache` via an orphan branch (A) or `actions/cache` (B). The machinery
grounds are that the branch is the most machinery of any option and requires the sync token
to write somewhere beyond the sync, while an Actions cache is evictable and best-effort.
**The stronger reason is correctness, and it is what settles it.**
`launchpad/Research/367-rerere-portability-and-fragility.md` measured five experiments
against the fork's real conflict and found that transport is not the obstacle — *"**The
`rr-cache` is portable** — copied into a fresh clone it replays, so every remedy #300
considers is viable"* — so what remains is trust. Its experiment 5 recorded a deliberately
wrong resolution and re-merged: *"The fork's position is dropped, the file looks clean, and
the only message is the same benign `Resolved … using previous resolution.`"* Its conclusion
for #300 is the reason not to share: "A *shared* cache is therefore higher-stakes than a
per-clone one: one stale or mistaken resolution can propagate to everyone and to CI." A
shared cache replays one person's resolution blind on someone else's merge, and a resolution
that was wrong the first time reapplies with no warning at all.

Rejected a git-hook/`includeIf` bootstrap (D) as deliberate subversion of git's design.
Rejected relying on built-in `union` (E) as wrong for nearly every file in the candidate
set.

## Consequences

- Drivers actually run for any clone that has run setup; a check flags clones that have
  not.
- Criterion 4 is recorded as per-machine, not per-repository — an honest narrowing the
  PRD cannot claim unqualified.
- Two people may still resolve the same conflict independently; nothing reports that it
  happened, which is the accepted cost of not sharing. That cost is bought deliberately: an
  unnoticed duplicate resolution is cheaper than a silently propagated wrong one.
- `rerere.autoUpdate` off means a replayed resolution sits unstaged, so `git status` shows
  it and a human has to look before it reaches a commit.

## Security implications

A merge driver is an arbitrary shell command git executes during a merge. Git does not
forbid a repository carrying the `merge=` attribute — `.gitattributes` is exactly where that
mapping belongs — but a repository cannot supply the driver *definition*, which git reads
only from config. That is the deliberate boundary: the repo may name a driver, only a local
config may say what it runs. So the bootstrap asks contributors to run an explicit, readable
command that installs an execution hook; `true` as the `ours` driver is trivially safe, and
the `rr-cache` — not shared here — contains source fragments that are not a disclosure
concern on a public fork.

## Supersedes

none

## Provenance

Drafted by an agent from #300's options. Jeffrey (@tucktuck101) made the decision on
2026-08-31 after reviewing all options with their positive and negative consequences —
including the operational narrowing that a fresh CI clone holds no `rr-cache`, so the
unattended job's only replay mechanism is human-authored merge drivers — and the agent's
recommendation of this hybrid; he accepted it by replying verbatim: **"agreed"**. Full
alternatives remain in #300. The correctness argument against
a shared cache and the `rerere.autoUpdate` position are quoted from
`launchpad/Research/367-rerere-portability-and-fragility.md` and
`launchpad/Research/362-sub-file-decline-durability.md` on `launchpad`; both label those
statements as their authors' recommendations to #300 rather than findings, and this record
adopts them as such.
