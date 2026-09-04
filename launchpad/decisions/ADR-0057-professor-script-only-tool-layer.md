---
status: Accepted
date: 2026-09-03
issue: launchpad-26/buzz#2098
decided_in: launchpad-26/buzz#2098
supersedes: none
---

# ADR-0057 — The Professor's tool layer is script-only; MCP is retired

## Decision

The Professor's redesign (`launchpad/Research/the-professor-skill-suite-redesign.md`, PR #2097)
adopts a **script-only tool layer** — `tools/professor.py`, four subcommands, callable identically
via Bash from any harness — as the pack's long-term architecture. This retires MCP entirely: no
`.mcp.json`, no `mcp_config` field, no `mcp.run()` dispatch path. `tools/professor.py`'s four
subcommands (`check-page`, `screen-content`, `resolve-pin`, `path-exists-at`) replace
`tools/server.py`'s five MCP tools outright, in Phase 1's own commit — no transition period, no
compatibility shim.

This rejects the alternative in flight on a separate branch: issue #1402
(`chore/1402-professor-root-mcp`), which fixes one specific reachability bug — `draft-page`
cannot execute from a session that never registered the `professor-tools` MCP server — by adding
a CLI dispatch mode to `tools/server.py` **alongside** its existing MCP mode, keeping both live.
This document's tool layer is not an extension of that diff; it is a different, smaller shape for
the same underlying functions (`resolve-pin` and `path-exists-at` are thin ports of `server.py`'s
`resolve_pin`/`path_exists_at`, minus the `@mcp.tool()` decorator and the `mcp` import). What
happens procedurally to the `#1402` branch itself — land as a short-lived interim fix, get
redirected to build `professor.py` directly, or close in favor of Phase 1 — is left to whoever
owns #1402, not decided here; this ADR settles which tool-layer shape ships as the pack's
long-term architecture, not the fate of that specific branch.

## Context

The Professor currently drafts documentation for exactly one repo (`launchpad-26/handbook`), with
every tool call carrying that repo's name as a hardcoded constant in `tools/server.py`. Pointing
it at any other repo does nothing. Fixing that (the actual goal of the redesign) first requires
answering a narrower question the redesign's own diagnosis surfaced: once the portability fix
shrinks `professor-tools`' job down to two functions — resolving a pin or a path for a citation
*outside* the target repo — is that narrow a job still worth keeping an MCP server for at all?

What MCP still buys, honestly stated in the design doc's own §1a: a typed, schema-discoverable
tool call, and a transcript that records "this fact was fetched" as a structured tool-use block
rather than an ordinary shell command. That is a real property a plain script gives up.

What it costs to keep, also stated there: a dependency on the `mcp` Python package for two
functions that are otherwise a `gh api` call and error handling; a second execution path
(`mcp.run()` vs. argv dispatch) to keep in sync and test, for a registration mode that `#1402`'s
own investigation found **two of this fork's four target harnesses don't even use** (Codex and
Goose don't read a root `.mcp.json`); and a `.mcp.json` plus a `mcp_config` field in `plugin.json`
that need to stay correct and be explained, for a code path most of this fork's own harnesses
never take.

## Consequences

**Good.** The suite works identically from any harness via Bash, with no registration step —
directly closing the portability bug this whole redesign exists to fix, for the primary case
(most of the suite needs no network at all) and the narrow remaining network case (external
citations) alike.

**Good.** One execution path instead of two. Nothing to keep in sync between an MCP dispatch mode
and a CLI dispatch mode, and nothing to explain to a reader about why both exist.

**Bad, stated plainly.** The typed, schema-discoverable tool-call property MCP provided is gone.
A plain Bash subprocess call carries no structured record that "this fact was fetched" beyond
whatever the calling skill's own transcript captures. Anyone building on this pack should know
that tradeoff was made deliberately, not by default.

**Bad.** `#1402`'s literal bug (MCP not registered in a session) becomes moot once nothing
registers anything — but the broader concern behind it, reaching Professor's tooling from an
arbitrary session, resurfaces as a different, narrower problem this document did not originally
address: resolving `<pack-root>` when the session isn't inside this fork. That problem is answered
separately (`$PROFESSOR_PACK_ROOT`, recorded in the design doc's own Open Questions item 1), not by
this ADR.

## Security implications

Retiring MCP removes one registration surface (`.mcp.json`) a session could carry unintentionally,
and one dependency (`mcp` Python package) from the pack's supply chain. It does not change the
provenance/audit posture PRD #4 established for The Professor's underlying work — every citation
subcommand still runs locally except the two that were already network-shaped
(`resolve-pin`/`path-exists-at`), and those still take `repo` as an explicit argument, never a
hardcoded name.

## Provenance

Reported into `launchpad/Research/the-professor-skill-suite-redesign.md` as the launchpad-26
cohort's consensus, 2026-09-03, after the document's own diagnosis (§1, §1a) and two rounds of
adversarial review (a general-purpose subagent, and Codex CLI run twice). The cohort delegated
remaining open design decisions on this document to Serina McFall (she built the corpus docs and
most of the knowledge agent — most context on the team); this specific call — script-only over
`#1402`'s dual-mode approach — was the group's own consensus, not one of the items individually
delegated to her afterward. Recorded here, closing #2098, per `launchpad/AGENTS.md` rule 3 (an ADR
issue closes only once its decision is written to a document, not left in a closed issue alone).
