---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#1401
decided_in: launchpad-26/buzz#1401
supersedes: none
---

# ADR-0030 — Root skill-registration dirs may symlink into `launchpad/`

## Decision

Root skill-registration directories — `.agents/skills/`, `.claude/skills/`, `.codex/skills/`,
`.goose/skills/` — may contain a relative symlink whose target resolves into `launchpad/`.
This is a new, generic named exception to `launchpad/AGENTS.md` §3 ("Everything
cohort-specific lives under `launchpad/`"), not a one-off precedent scoped to a single skill.

A cohort-authored skill made discoverable this way must be a **symlink, never a copy**, of
its canonical file under `launchpad/agents/<pack>/skills/<skill>/SKILL.md`. The cohort content
itself never leaves `launchpad/`; only a filesystem pointer sits at root, in the same
mechanism `desktop-screenshot` and `sprout-cli` already use for upstream-owned files.

`draft-page` (PR #1398, closing #1397) is the first skill to use this exception. No future
cohort skill under `launchpad/agents/` needs its own ADR to be made discoverable at root the
same way — this decision covers the pattern, not just the instance that raised it.

## Context

PR #1398 copied `launchpad/agents/the-professor/skills/draft-page/SKILL.md` — cohort-authored
content — into `.agents/skills/draft-page/SKILL.md` at the repository root, so a generic
Claude Code session could discover it without running The Professor's persona pack. Review
found two problems entangled in one PR: `.agents/skills/` is not a directory Claude Code
reads (only `.claude/skills/` is, confirmed against `agentic-debugging` and `review-final`),
and a literal copy of cohort content sitting outside `launchpad/` reads as a §3 violation,
since §3's exception list is closed and named per-file.

The existing root-level skills looked like precedent but were not: `desktop-screenshot` and
`sprout-cli` are relative symlinks into `desktop/src-tauri/src/managed_agents/*.md`, which is
already upstream-owned content. Registering an upstream file at root moves nothing across the
boundary. `draft-page`'s canonical file is genuinely cohort material under `launchpad/`, which
is the one shape the existing precedent didn't cover — hence this ADR.

Four options were considered. A (symlink, settle it by example, no §3 change) and B (symlink,
and write the exception into §3) both fix the immediate PR the same way; they differ only in
whether the boundary call becomes a written rule or stays an implicit precedent. B was chosen
because §3's exception list already exists precisely so this kind of question gets decided
once and recorded, not re-argued per skill — and persona packs under `launchpad/agents/` are
expected to keep producing skills that want the same root discoverability `draft-page` wanted.
C (don't register cohort skills at root at all) was rejected as reopening #1397's whole
motivation without a competing design. D (keep the literal copy, name it as a per-skill
exception) was rejected as the weakest option: it does nothing about the copy's divergence
risk and grows the closed exception list one entry per skill, indefinitely.

## Consequences

**Good.** Cohort content stays entirely under `launchpad/`, matching §3's actual purpose —
protecting merges from `block/buzz` — without the merge-cleanliness cost that a literal copy
outside `launchpad/` would eventually create.

**Good.** A symlink cannot go stale relative to its target, so the divergence-risk finding
raised against PR #1398's original copy closes as a side effect of this decision rather than
needing a separate fix.

**Good.** Future cohort skills that want root discoverability apply this exception directly;
nobody needs to file a fresh ADR to re-ask the same boundary question.

**Bad.** §3's closed exception list now includes a *generic* pattern rather than only named
files, which is a small shift in how that list is read — a reviewer checking a future PR
against §3 needs to recognise "root skill dir symlinking into `launchpad/`" as pre-approved
rather than expecting every exception to name a specific file.

**Bad, unresolved by this decision.** A generic root session that discovers a cohort skill
this way still cannot necessarily execute it — `draft-page` itself hard-requires
`professor-tools` MCP calls that are not registered outside The Professor's own plugin. That
gap is functional, not a boundary question, and is tracked separately from this ADR.

## Security implications

This decision does not change what is committed or who can read it. `launchpad-26/buzz` is
already public, and a symlink discloses the same content a literal copy would — content that
was already public at its canonical `launchpad/agents/` path. A symlink carries no execution
or credential surface of its own; it is filesystem-level path indirection resolved by whatever
reads it. If a future change registers additional tooling (such as an MCP server) at root to
make a newly-discoverable skill executable, that change carries its own security review for
whatever access it grants a generic session — separately from this decision, which is scoped
to discoverability only.

## Provenance

Decided by Serina McFall in conversation on 2026-08-25, after an agent-drafted
recommendation.

**Her call:** Option B — symlink into `launchpad/`, with a generic named exception written
into `launchpad/AGENTS.md` §3 — over A (same symlink, left as unwritten precedent), C (revert,
don't register cohort skills at root), and D (keep the copy, name it as a per-skill
exception).

**The recommendation:** drafted by an AI agent (Claude Sonnet 5) on 2026-08-25, on the
reasoning that §3's boundary exists to protect upstream merge cleanliness, a symlink pointing
into `launchpad/` doesn't threaten that, and that writing the exception once removes a
question future cohort skills would otherwise re-raise individually. The agent drafted the
recommendation; Serina reached the same option after being asked for her own read, and
confirmed it.
