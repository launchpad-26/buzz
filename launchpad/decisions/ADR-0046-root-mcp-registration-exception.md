---
status: Proposed
date: 2026-08-25
issue: launchpad-26/buzz#1415
decided_in: launchpad-26/buzz#1415
supersedes: none
---

# ADR-0046 — Root `.mcp.json` registration of `professor-tools` is a named §3 exception

## Decision

**Not yet settled by a human.** This record is `Proposed`, not `Accepted`.
`launchpad/AGENTS.md` §5.1 reserves the choice for a human and #1415's *Decision outcome*
is still blank. When a human states the outcome in #1415, this record's `status` becomes
`Accepted`.

The proposed option is B. `professor-tools` is registered repo-wide via a root `.mcp.json`:

```json
{ "mcpServers": { "professor-tools": { "command": "launchpad/agents/the-professor/tools/server.py" } } }
```

**The exception is scoped to one named path: `.mcp.json` at the repository root.** It is
not a generic exception for "root MCP registration", and it is not a category. Every other
§3 exception names its files — `bin/lefthook` and `bin/.lefthook-*.pkg`; the five
deployment-provenance files — and a category-shaped grant would reopen the closed list by
the back door, which is what §3's *"The list itself is closed"* exists to prevent. A second
root MCP server added to that same file is covered; a different root config file, or a
different mechanism, is not, and needs its own record.

§3's exception list is amended in this same pull request so the two documents do not
disagree, per AGENTS.md's own instruction that *"Where the two disagree, **this file
wins**; fix the drift rather than living with it."* This would be the **fifth** exception
in §3 as it currently stands. Note that #1441 (ADR-0045, cohort crates) proposes another
fifth exception against the same list; whichever merges second will need to re-place its
bullet.

**The file does not exist yet.** There is no root `.mcp.json` on `launchpad`, and this
record does not add one — it decides that adding one is permitted. Pull request #1398 is
the change that would land it, and it is still open. So `draft-page` is not yet runnable
from a root session; it becomes runnable when #1398 merges under this record's permission.
Earlier drafts of this record asserted the registration as present fact, which it was not.

The prior grant in conversation (Serina's approval in #1398) is recorded here durably, and
is the reason this option is put forward rather than decline-and-remove.

## Context

Without this, `draft-page` is discoverable from a root session but cannot execute — the
"visible but unusable" outcome #1398's own review called worse than not shipping. Every
`professor-tools` tool is read-only (contract text, a category list, a commit-SHA
resolution, a path-existence check, a provenance-gate check); none write, execute
arbitrary commands, or handle credentials. Claude Code gates any newly-registered MCP
server behind an approval prompt on first use, so no session silently inherits the
capability. `server.py` has no cwd-dependent paths.

Rejected: decline-and-remove (A, leaves the skill dead and reopens #1397's motivation),
and folding into the symlink exception proposed in ADR-0030 (C, a symlink exception does
not cover a plain config file naming a script path, and mixing them invites scope creep).

**ADR-0030 is not accepted yet.** It is proposed in open pull request #1405; `launchpad`
currently holds ADR-0001 through ADR-0029. This record therefore does not build on
ADR-0030 and does not depend on it — the two are adjacent boundary questions that should
cite each other once both are settled, and if ADR-0030 is withdrawn nothing here changes.
Earlier drafts referred to ADR-0030's exception in the present tense as though it existed.

## Consequences

- Once #1398 merges, `draft-page` becomes discoverable and runnable from any root session,
  closing the gap its own review named.
- The decision Serina made in conversation gets a durable, citable record.
- §3 gains a fifth named exception, scoped to `.mcp.json` alone.
- A future root MCP registration in the same file is covered; anything broader will cite
  this record as precedent, and the cost is borne by how disciplined the next one is. The
  path-scoping above is what keeps that cost bounded.
- Until #1398 lands, this record permits something that has not happened, which is why it
  is written in permission rather than assertion.

## Security implications

This changes what every session opened in this repository can reach by default, once the
file exists. The exposure is bounded: all tools read-only against public or
cohort-controlled sources, no writes, no arbitrary command execution, no credential
handling; the script only runs if a session exercises the skill, and then passes through
Claude Code's own MCP approval prompt. `draft-page`'s execution gap — its five required
tool calls, none of which can run without a registered server — was the reason for this
registration and is resolved by it.

## Supersedes

none

## Amends

`launchpad/AGENTS.md` §3, by adding the root `.mcp.json` as a named exception. The
underlying closed-list rule — that any further exception needs its own ADR — is untouched.

## Provenance

Drafted by an agent from #1415's options; the decision itself is pending a human, as
stated at the top of *Decision*. Serina's grant in #1398 covers the registration this
record proposes to permit, not the §3 exception, which is #1415's question. Full
alternatives remain in #1415.
