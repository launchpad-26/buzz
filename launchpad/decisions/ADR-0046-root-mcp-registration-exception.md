---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#1415
decided_in: launchpad-26/buzz#1415
supersedes: none
---

# ADR-0046 — Root `.mcp.json` registration of `professor-tools` is a named §3 exception

## Decision

Choose Option B. `professor-tools` is registered repo-wide via a root `.mcp.json`
(`{ "mcpServers": { "professor-tools": { "command": "launchpad/agents/the-professor/tools/server.py" } } }`),
and root MCP server registration is recorded as a new, generic §3 exception covering a
plain root config file naming a `launchpad/`-relative script path — distinct from the
symlink-into-skill-dirs exception ADR-0030 grants. The `draft-page` skill is thereby both
discoverable and runnable from a generic root session.

The prior grant in conversation (Serina's approval in #1398) is recorded here durably.

This outcome was selected automatically under @tucktuck101's explicit approval for the
2026-08-25 ADR-clearing session. Jeff authorized automated selection of Low and
clear-Medium ADR outcomes; he did not personally select this individual outcome.

## Context

Without this, `draft-page` is discoverable from a root session but cannot execute — the
"visible but unusable" outcome #1398's own review called worse than not shipping. Every
`professor-tools` tool is read-only (contract text, a category list, a commit-SHA
resolution, a path-existence check, a provenance-gate check); none write, execute
arbitrary commands, or handle credentials. Claude Code gates any newly-registered MCP
server behind an approval prompt on first use, so no session silently inherits the
capability. `server.py` has no cwd-dependent paths.

Rejected: decline-and-remove (A, leaves the skill dead and reopens #1397's motivation),
and folding into ADR-0030 (C, the symlink exception does not cover a plain config file
naming a script path, and mixing them invites scope creep).

## Risk classification

**Clear Low (4/12), high confidence.** Blast radius 1; reversibility 1;
security/trust 1; data/state 0; contracts/dependencies 0; operations 1. No hard High-risk
trigger. Every session gains a larger *default* capability surface — but read-only,
approval-gated, and unblocking an otherwise-dead skill.

## Consequences

- `draft-page` becomes discoverable and runnable from any root session, closing the gap
  its own review named.
- The decision Serina made in conversation gets a durable, citable record.
- Every future root MCP registration will cite this record as precedent — the cost is
  borne by how disciplined the next one is.

## Security implications

This changes what every session opened in this repository can reach by default. The
exposure is bounded: all tools read-only against public or cohort-controlled sources, no
writes, no arbitrary command execution, no credential handling; the script only runs if a
session exercises the skill, and then passes through Claude Code's own MCP approval prompt.
The separate ✓ of `draft-page`'s execution gap (its five required tool calls) was the
reason for this registration and is resolved by it.

## Supersedes

none — extends ADR-0030's boundary handling without reopening it.

## Provenance

Selected and recorded by an agent under Jeff's explicit, session-only authorization
for lower-risk ADRs. Full alternatives remain in #1415.