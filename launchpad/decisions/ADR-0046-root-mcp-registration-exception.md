---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#1415
decided_in: launchpad-26/buzz#1415
supersedes: none
---

# ADR-0046 — Root `.mcp.json` registration of `professor-tools` is a named §3 exception

## Decision

Option B. Registering `professor-tools` repo-wide via a root `.mcp.json` is permitted —
the file does not exist yet and this record does not add it (see below):

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

§3's exception list already carries this bullet — it was amended in pull request #1442,
the same pull request that merged this record, per AGENTS.md's own instruction that
*"Where the two disagree, **this file wins**; fix the drift rather than living with it."*
Between that merge and this acceptance, `AGENTS.md` §3 named an exception whose
authorising record was still `Proposed`; accepting this record closes that gap.

**The file does not exist yet, and the change that would have added it was declined.**
There is no root `.mcp.json` on `launchpad`, and this record does not add one — it decides
that adding one is permitted. Pull request #1398 was the change that would have landed it;
it was **closed unmerged with changes requested** on 2026-08-26, so `draft-page` is still
not runnable from a root session. This record's permission stands and outlives that
particular pull request: a future change may add the file under it without a new ADR.
Earlier drafts of this record asserted the registration as present fact, which it was not,
and later drafts described #1398 as still open, which it no longer is.

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

**ADR-0030 is accepted.** It merged in pull request #1405 on 2026-08-26, after the draft
of this record was written. This record still does not build on ADR-0030 and does not
depend on it — the two are adjacent boundary questions, and nothing here changes on
ADR-0030's account. Earlier drafts referred to its exception in the present tense before
it existed, then described it as unaccepted after it did; both are corrected here.

## Consequences

- `draft-page` is still not runnable from a root session. #1398 was declined, so the
  permission this record grants is unexercised until some future change adds the file.
- Every session opened in this repository gains reach to a tool that holds a GitHub
  credential and writes local files. That is a real widening of the default surface, not a
  read-only convenience.
- The decision Serina made in conversation gets a durable, citable record.
- §3 gains a fifth named exception, scoped to `.mcp.json` alone.
- A future root MCP registration in the same file is covered; anything broader will cite
  this record as precedent, and the cost is borne by how disciplined the next one is. The
  path-scoping above is what keeps that cost bounded.
- Until a root `.mcp.json` exists, this record permits something that has not happened,
  which is why it is written in permission rather than assertion.

## Security implications

This changes what every session opened in this repository can reach by default, once the
file exists, and the surface is **not** read-only. An earlier revision of this record
claimed every tool was read-only with no writes and no credential handling. That is false:
`launchpad/agents/the-professor/tools/server.py` obtains a GitHub authentication credential
and passes it into a subprocess environment (around lines 378-399), and writes draft
content to a local file (around line 438).

What the exposure actually is, stated accurately: the server reads public or
cohort-controlled sources; it holds a GitHub credential for the duration of a call, which
it does not print; it writes only to paths it creates for draft output; it executes no
caller-supplied command. The script runs only if a session exercises the skill, and then
passes through Claude Code's own MCP approval prompt. That is a narrower surface than an
arbitrary-execution server, and a wider one than "read-only" — anyone weighing this
exception should weigh the credential, not the sanitised version. `draft-page`'s execution gap — its five required
tool calls, none of which can run without a registered server — was the reason for this
registration and is resolved by it.

## Supersedes

none

## Amends

`launchpad/AGENTS.md` §3, by adding the root `.mcp.json` as a named exception. The
underlying closed-list rule — that any further exception needs its own ADR — is untouched.

## Provenance

Drafted by an agent from #1415's options. The outcome was selected by an agent under
@tucktuck101's authorisation for the 2026-08-25 ADR-clearing session, recorded in
[#1415's comment of 2026-08-25](https://github.com/launchpad-26/buzz/issues/1415#issuecomment-5409048575).

**Agent-exercised under delegated authority.** Initiating human: @tucktuck101
(Jeffrey Taylor Robertson). He confirmed the authorisation on 2026-09-03 when asked
directly whether he had given it — *"Yeah, I did"* — and ruled on the general principle
in the same session:

> If I gave an agent permission to make decisions, then it should have been allowed to
> make the decisions. Outside of that, it should not.

and, on records left in this state:

> if it's got an eighty hour record, it's being decided and it shouldn't be fucking
> around anymore and the issue should be moved on. Once a PR is closed, the issue itself
> should move to closed. It doesn't matter about how it got there other than the idea
> that a human can give an agent the authority to basically fill out a fucking form on
> their behalf.

A review on the original PR reverted this record to `Proposed` on the grounds that no
human had selected the outcome. That premise was wrong: the authorising human had, and
has now confirmed it. Serina's grant in #1398 covers the registration this record permits,
not the §3 exception, which is #1415's question. Full alternatives remain in #1415.
