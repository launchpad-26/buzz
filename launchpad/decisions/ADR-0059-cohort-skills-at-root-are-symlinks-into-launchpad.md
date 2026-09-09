---
status: Accepted
date: 2026-09-10
issue: launchpad-26/buzz#2154
decided_in: launchpad-26/buzz#2154
supersedes: none
---

# ADR-0059 — A cohort skill at the repository root is a symlink; its canonical file lives under `launchpad/`

## Decision

The seven cohort skills currently sitting in `.claude/skills/` as **original files** move to
canonical files under `launchpad/skills/<name>/`, each leaving a **relative symlink** at its root
location:

`agentic-debugging` · `corpus-author` · `corpus-batch-author` · `corpus-maintain` ·
`corpus-plan` · `corpus-review` · `review-final`

This applies ADR-0030's existing shape rather than inventing one. **It also states explicitly
what ADR-0030 left implicit:** ADR-0030's Decision names the canonical file as
`launchpad/agents/<pack>/skills/<skill>/SKILL.md` — persona-pack skills. These seven are
organization skills, which `launchpad/AGENTS.md` §3 places in `launchpad/skills/`
(*"where the `launchpad-26` GitHub organization keeps its reusable skills"*). The symlink
exception covers **both** locations. That is a minimal, deliberate clarification of ADR-0030's
scope, not a re-decision of it, and not a new entry on §3's closed list.

§3's exception list is not widened. No skill authored directly at root, with no canonical copy
under `launchpad/`, is permitted after this.

## Context

`launchpad/AGENTS.md` §3 states that everything cohort-specific lives under `launchpad/`, that
upstream owns everything else, and that its exception list *"is closed; any further exception
needs its own ADR."* Seven cohort-authored skills contradict that today. Verified against
`origin/launchpad` at `28043220b`:

```
.claude/skills/  — mode 100644, no canonical copy under launchpad/
    agentic-debugging  corpus-author  corpus-batch-author  corpus-maintain
    corpus-plan        corpus-review  review-final

.claude/skills/  — mode 120000 (symlinks, already compliant)
    desktop-screenshot -> ../../../desktop/src-tauri/src/managed_agents/screenshot_skill.md
    sprout-cli         -> ../../../desktop/src-tauri/src/managed_agents/nest_skill.md
```

The two compliant entries are not precedent for the seven: they point at `desktop/`, which is
upstream-owned, so registering them at root moves nothing across the boundary. ADR-0030 exists
precisely because a *cohort* file is the case that precedent did not cover.

**This was deliberate at the time, not carelessness, and that is why it is a decision rather
than a bug.** #629's own Impacted components names `.claude/skills/corpus-author/` as the
destination, and the same shape shipped through #628, #630, #631 and the batch-author commit —
each a filed, reviewed, merged pull request. The dates matter: `agentic-debugging` and
`review-final` landed 2026-08-18, before ADR-0030 was accepted on 2026-08-25; but
`corpus-author`, `corpus-plan` and `corpus-review` landed 2026-08-27, `corpus-batch-author` on
2026-08-28 and `corpus-maintain` on 2026-09-03 — all after. A rule contradicted seven times in
the open is either the wrong rule or an unenforced one.

It is the second. Nothing detects this shape: `adr_boundary_check.py` compares ADR-0005's file
table against §3 and checks those files carry Launchpad values, and nothing more. Seven
instances accumulated without a single check going red.

## Decision drivers

- §3's boundary exists to keep merges from `block/buzz` (~3,800 files, merged regularly)
  mechanical. Cohort originals outside `launchpad/` are exactly what turns a routine merge into
  manual conflict resolution.
- ADR-0030 already settled that the symlink shape is acceptable and is explicitly generic —
  *"this decision covers the pattern, not just the instance that raised it."* Migrating needs no
  new boundary concession; widening §3 would.
- A symlink cannot drift from its target, so the divergence risk that killed PR #1398's literal
  copy does not return.
- Stated by Serina when deciding: *"option A makes the most sense as that is how my own skills
  are used in my personal repos via symlinks."* The chosen shape is the one already in habitual
  use, which makes it the least likely to be quietly undone.

## Considered options

1. **Migrate to the ADR-0030 symlink shape.** **Chosen.** Costs one migration pull request plus
   path fixups.
2. **Widen §3 with a new exception** for cohort skills authored directly in root skill
   directories. Rejected: cheapest now, but it spends the closed list's credibility to avoid a
   single mechanical PR, and turns "everything cohort-specific lives under `launchpad/`" into a
   rule with a large carve-out.
3. **Leave as is and record the divergence.** Rejected: §3 keeps asserting something untrue, and
   a reviewer gets no way to tell a permitted root skill from a violation.

## Consequences

**Good.** Cohort content returns inside `launchpad/`; only pointers sit outside it. §3 becomes
true again without its exception list growing.

**Good.** `launchpad/skills/` becomes the single place to look for an organization skill, which
is what §3 already tells a reader to expect.

**Bad, and it must be handled rather than discovered.** `review-final` is not a single file — it
ships `check-ledger.sh`, `verdict.sh`, `test-check-ledger.sh` and `test-verdict.sh` beside its
`SKILL.md`. The migration decides directory-symlink versus one-symlink-per-file and states why;
a directory symlink still satisfies ADR-0030's *"a relative symlink whose target resolves into
`launchpad/`"*.

**Bad, and load-bearing.** Those two `.sh` files are the review gate. If the executable bit does
not survive the move, `verdict.sh` and `check-ledger.sh` stop being runnable and the gate breaks
silently. The migration asserts mode `100755` afterwards rather than trusting `git mv`.

**Neutral.** Only `.claude/skills/` is in scope; all seven live there and nowhere else. The
migration does not add `.agents/`, `.codex/` or `.goose/` entries. If a harness needs them that
is a separate, stated choice.

## What this does not settle

- **The migration itself**, which is filed separately. This ADR decides the shape; it moves no
  files.
- **A guard.** Nothing detects a cohort original at root today, which is the root cause of the
  drift this ADR corrects. A check that fails when a root skill entry is a regular file whose
  content has no canonical copy under `launchpad/` would close the class. Naming it here so the
  gap is recorded; specifying and building it is not this decision's scope.

## Security implications

No credential, permission or exposure change. `launchpad-26/buzz` is public and all seven files
are already committed and readable; a symlink discloses exactly what the original did.

One operational risk is worth stating plainly: `review-final`'s scripts are part of the review
gate, and a migration that breaks their executable bit or their relative path resolution would
disable a control rather than merely move it. That is a correctness requirement on the
migration, not a reason to decline the decision — and it is why the executable-mode assertion is
named as a consequence above rather than left to the implementer's memory.

## Provenance

Decided by Serina McFall, 2026-09-10, from three options in #2154.

The issue was filed 2026-09-09 while auditing PRD #2099's issue tree — the seven root originals
surfaced as a by-product of checking whether ADR-0030 already covered the Professor's own
root-registration need (#1397, under Feature #2151). It was deliberately kept separate from
#2153, which records ADR-0030's exception in §3 and is in review as PR #2156. The two are halves
of the same gap and must not contradict each other on landing: #2156's bullet currently states
the exception does not cover a skill authored at root with no canonical copy, and points at
#2154 as open. Once the migration lands, no such skill remains, and that sentence should be
revisited rather than left describing a closed question.
