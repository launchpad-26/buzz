---
id: capabilities-projects-project-repository
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "Buzz defines kind:30621 (KIND_PROJECT) as a NIP-MP addressable project event: a named grouping of kind:30617 NIP-34 repository announcements, addressed by (pubkey, 30621, d); the signer gains no authority over any member repository, since push policy reads only the member's own announcement."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:625-632"
      - "docs/nips/NIP-MP.md:41-54"
  - statement: "A project binds to a member repository by an `a` tag on the project's kind:30621 event holding the coordinate `30617:<owner-hex>:<repo-d>` -- the repository's own kind:30617 event carries no pointer back to any project, and a repository may be a member of zero, one, or several projects simultaneously with no exclusivity."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-MP.md:42-43"
      - "docs/nips/NIP-MP.md:108-126"
      - "docs/nips/NIP-MP.md:153-155"
  - statement: "buzz-sdk's ProjectMemberCoord::parse_full parses and validates a full `30617:<owner>:<repo-d>` coordinate: it requires the literal kind segment `30617`, a 64-character lowercase-hex owner (uppercase rejected, never normalized), and a non-empty repo-d taken verbatim from splitting on only the first two colons."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:2001-2067"
  - statement: "The relay validates a kind:30621 envelope at ingest through validate_project_envelope, enforcing (among other rules named in NIP-MP) a cap of 64 member `a` tags, per-tag arity, and rejection of malformed or duplicate member coordinates before the event is stored."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1609"
      - "docs/nips/NIP-MP.md:169-184"
  - statement: "buzz-cli's `buzz projects` command group is the agent-facing surface for binding and unbinding a repository from a project: `create --repo` accepts member coordinates at creation, and `add-repo` / `remove-repo` mutate an existing project's membership by a read-modify-write against the caller's own live kind:30621 head, re-validating the full envelope before submission."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/projects.rs:94-105"
      - "crates/buzz-cli/src/commands/projects.rs:170-227"
      - "crates/buzz-cli/src/commands/projects.rs:509-519"
      - "crates/buzz-cli/src/commands/projects.rs:521-582"
  - statement: "The `--repo` argument to `buzz projects create` / `add-repo` / `remove-repo` accepts either a bare Buzz-hosted repo id (expanded to a full coordinate with the caller as owner) or a full `30617:<owner>:<repo-d>` coordinate naming any owner, which is what lets a project bind repositories owned by different pubkeys."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/projects.rs:78-105"
  - statement: "NIP-MP states that the project signer's authority over a member repository is none -- no edit, delete, push, or administration, and no ability to change the member's own metadata or protections -- and that git push policy reads only the repository's own kind:30617, never a project, so a project binding cannot widen or narrow push access to a repository."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-MP.md:130-139"
      - "docs/nips/NIP-MP.md:322"
  - statement: "Removing the last repository from a project, or deleting a project (NIP-09 kind:5 at the project coordinate), does not affect member repositories: their kind:30617 events, refs, channels, and protections survive, and a member falls back to rendering as its own implicit card."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-MP.md:147-167"
  - statement: "End-to-end coverage against a live relay exists for cross-owner project membership, owner-scoped replacement, and project deletion sparing member repositories: test_project_publish_and_query_returns_cross_owner_members, test_project_same_d_under_two_authors_are_independent, and test_project_tombstone_deletes_coordinate_and_spares_members."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_project.rs:155"
      - "crates/buzz-test-client/tests/e2e_project.rs:250"
      - "crates/buzz-test-client/tests/e2e_project.rs:309"
  - statement: "VISION_PROJECTS.md's own Status table marks both \"Project binding (kind:30617 + buzz- tags)\" and \"Multi-repo projects (kind:30621, NIP-MP)\" as \"Designed\" rather than \"Ships today\", at the revision this node records -- the product-level maturity marker lags the working, tested code and relay validation described above."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:254-255"
  - statement: "Issue #811's own Definition of Done requires this node to state the capability and primary actors/outcomes, define behavioral rules, constraints and variants, and link major flows, interfaces, data and platform implementation and verification -- the acceptance bar this node is built against."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#811 definition of done"
---

# Project repository: capability

A Buzz project (`kind:30621`, NIP-MP) can bind to one or more git repositories
(`kind:30617` NIP-34 announcements) as its members, so a human or agent can group
repositories that belong to the same piece of work -- for example a relay, a desktop
app, and a mobile app that together make up "the platform" -- into a single named
container, even when those repositories are owned by different keys. A member
repository keeps its own identity, ownership, refs, channel binding, and push
protections; joining or leaving a project changes nothing about the repository event
itself, only the project's own membership list.

## Maturity

**Implemented and tested, though the product's own vision document still marks it
"Designed."** The binding is fully specified (`docs/nips/NIP-MP.md`), the event kind
is registered (`KIND_PROJECT = 30621`, `crates/buzz-core/src/kind.rs:632`), the relay
enforces the envelope's validation rules at ingest
(`validate_project_envelope`, `crates/buzz-relay/src/handlers/ingest.rs:1609`), and
`buzz-cli` exposes the agent-facing write path (`buzz projects create --repo`,
`add-repo`, `remove-repo`, `crates/buzz-cli/src/commands/projects.rs`). End-to-end
tests exercise cross-owner membership, owner-scoped replacement, and deletion sparing
members against a live relay (`crates/buzz-test-client/tests/e2e_project.rs`).
Despite that, `VISION_PROJECTS.md`'s own Status table (lines 254-255) still marks
both "Project binding" and "Multi-repo projects" as "📋 Designed" rather than
"✅ Ships today" -- this node reports both facts rather than picking one, since they
answer different questions (what the code currently does, versus how the product's
own roadmap document currently classifies it) per this corpus's evidence-precedence
rule for claims about current behavior versus claims about product status.

## Boundary

This node does not describe:
- **How the capability is built** -- the relay's ingest pipeline, the CLI's
  read-modify-write mechanics beyond the citations above, or the `buzz-sdk` builder
  internals. No architecture node exists yet under this corpus to link to.
- **The interface(s) the capability is exposed through** -- the full `buzz projects`
  and `buzz repos` command surfaces, or the relay's `/events`/`/query` HTTP bridge.
  No interface node exists yet under this corpus to link to.
- **The step-by-step flow through this capability** -- the sequence of calls an agent
  or human makes to create a project and attach a repository. No flow node exists yet
  under this corpus to link to.
- **How the running system is operated** -- deployment, monitoring, or incident
  response for the relay that hosts this event kind.
- **The project channel binding** (`buzz-channel` on `kind:30621`, and the separate
  channel a repository's own `kind:30617` binds to) -- that is issue #810's subject,
  not this one's. This node covers repository membership only.
- **Branch-as-room** (a git branch's own channel/room binding) -- that is issue #809's
  subject.
- **The project capability as a whole** (creation, metadata, visibility, deletion) --
  that is issue #812's subject. This node is scoped narrowly to the repository-binding
  facet: how a project acquires, holds, and releases member repositories.

## Relationships

Declared: none. Checked: no `capabilities`, `architecture`, or `interfaces-events`
node exists yet under `launchpad/docs/corpus/` on `origin/launchpad`
(`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` at the
recorded revision lists only `AGENTS.md`, `README.md`, the `architecture/**` C4 nodes,
the `schema/` subtree, and `standards/**` -- none of them capability-shaped subject
matter this node would `references`, `implements`, or sit `part-of`). This is the
first node under `capabilities/projects/`; the natural moment to add `references`
edges to the sibling nodes for #809 (branch-as-room), #810 (project-channel), #812
(project) and to any future interface/architecture nodes covering the relay ingest
path or `buzz-cli` is once those nodes exist on the merge target.

## Scope and omissions

**This node covers** what a project's repository membership is, the event shapes and
tags involved (`kind:30621`'s `a` tags naming `kind:30617` coordinates), the coordinate
grammar and its validation at both the SDK and relay layers, the authority model (a
project grants no authority over a member repository, and push policy is read only
from the repository), multiple/zero membership, what happens to members when a
project's membership changes or the project itself is deleted, the CLI commands that
perform these mutations, and the gap between the code's demonstrated maturity and the
product vision document's own status marker.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| A project's channel binding (`buzz-channel`) | issue #810 |
| Branch-as-room (a git branch's own channel binding) | issue #809 |
| The project capability as a whole (creation, metadata, visibility, deletion) | issue #812 |
| How the relay's ingest pipeline is built (architecture) | not yet drafted under this corpus |
| The `buzz projects` / `buzz repos` command surfaces as interfaces | not yet drafted under this corpus |
| The step-by-step flow of creating a project and attaching a repository | not yet drafted under this corpus |
| Whether the project capability as rendered by clients (the fold, claim authority, listing eligibility) belongs in this node or a client-facing node | not settled by this task; see NIP-MP's own Client Behavior section for the full rules, not restated here |

**Expected but not verified when this node was written:**
- **No live desktop or web client rendering of project membership was exercised.**
  This node cites the specification (`docs/nips/NIP-MP.md`'s Client Behavior section)
  and the relay/CLI/SDK code, not a running desktop or web UI showing a multi-repo
  project.
- **`buzz projects create`'s full flag set beyond `--repo` (name, description,
  channel, visibility) was read but is out of this node's scope**, since those
  fields describe the project as a whole (issue #812's subject) rather than its
  repository membership specifically.
- **Whether VISION_PROJECTS.md's "Designed" marker has been updated since the
  recorded revision was not re-checked** -- this node states what the document said
  at the commit in its provenance entry, not a live read at review time.
