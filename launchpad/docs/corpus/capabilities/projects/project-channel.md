---
id: capabilities-projects-project-channel
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
  - statement: "A Buzz project is a NIP-MP `kind:30621` addressable event, and it MAY carry a single `buzz-channel` tag naming the UUID of the channel where the project's discussion lives; the field is metadata only, interpreted by clients rather than enforced by relay authorization."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-MP.md:81"
      - "docs/nips/NIP-MP.md:93"
      - "docs/nips/NIP-MP.md:139"
      - "crates/buzz-core/src/kind.rs:625-632"
  - statement: "`buzz projects create` requires `--channel` when no `--repo` member is given ('channel-first' creation); in that path it creates the project's default repository bound to that same channel via the repository's own `buzz-channel` tag, so the project event and its default repository agree on the home channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/projects.rs:380-385"
      - "crates/buzz-cli/src/commands/projects.rs:436-445"
      - "crates/buzz-cli/src/commands/projects.rs:722-750"
  - statement: "Reusing an already-existing default repository for channel-first creation requires that repository's `buzz-channel` to already match the requested home channel, enforced by `require_repo_channel_binding`."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/project_channel.rs:1-6"
      - "crates/buzz-cli/src/commands/projects.rs:730-731"
  - statement: "A project's home channel can be resolved in the other direction: `fetch_projects_for_channel` queries `kind:30621` events by a `#buzz-channel` tag filter, and both the query and its tag-matching helper are covered by unit tests that construct a channel UUID and assert the match logic directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/projects.rs:114-151"
      - "crates/buzz-cli/src/commands/projects.rs:1013-1101"
  - statement: "A project's `buzz-channel` reference cannot widen or narrow git push authorization: the relay's pre-receive hook policy resolves a pusher's channel role from the repository's own `buzz-channel` binding on its `kind:30617` announcement, never from a project's, so linking a project to a channel is inert for push authorization."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-MP.md:139"
      - "crates/buzz-relay/src/api/git/policy.rs:1-12"
  - statement: "Beyond the single home channel, an agent can request an additional channel scoped to a project via `buzz projects add-channel --home-channel <uuid> --name <name> [--description] [--visibility open|private] [--ttl] [--template]`; the CLI encrypts this as an owner-only observer-frame request and does not create any channel itself — the printed response states the channel is not created until the owner approves it in Buzz Desktop."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:1337-1358"
      - "crates/buzz-cli/src/commands/projects.rs:35-76"
      - "crates/buzz-cli/src/agent_management.rs:218-253"
  - statement: "The owner-review request contract (`project_channel_request`, action `create`, fields `homeChannelId`/`name`/`description`/`visibility`/`ttlSeconds`/`templateName`) is exercised end-to-end by a dedicated unit test that decrypts the built event with the owner's key and asserts every field, and is independently re-parsed by the desktop client's own narrow validator."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/agent_management.rs:344-372"
      - "desktop/src/features/projects/projectChannelRequest.ts:1-16"
  - statement: "On the desktop side, `useProjectChannelRequests` resolves which project owns the request's home channel, refuses approval from anyone but that project's owner, and on approval calls `addProjectChannel`, which creates a real channel, applies any named channel template, and republishes the project event linking the new channel — a full request-to-creation loop, not a stub."
    entry_class: FACT
    evidence:
      - "desktop/src/features/projects/useProjectChannelRequests.ts:103-169"
      - "desktop/src/features/projects/useAddProjectChannel.ts:31-172"
  - statement: "Channels added through the owner-review flow are recorded as repeatable `buzz-related-channel` tags on the project event, a desktop client convention distinct from the single `buzz-channel` home-channel tag; NIP-MP requires unrecognized tags to be ignored rather than rejected, so this convention rides on top of the NIP without a NIP change, and the desktop client caps the count at 64 extra channels."
    entry_class: FACT
    evidence:
      - "desktop/src/features/projects/projectModels.ts:34-40"
      - "desktop/src/features/projects/projectModels.ts:129-133"
      - "desktop/src/features/projects/projectChannelCreation.ts:11-71"
      - "docs/nips/NIP-MP.md:98"
  - statement: "Root VISION_PROJECTS.md's own narrative describes a *different* channel-creation surface at the branch level -- 'When you create a branch, Buzz creates a channel' whose patches, review comments, CI results and merge decision live in it and which archives when the branch merges -- and states that workflow configuration defined at the project level is 'inherited by every branch channel automatically,' treating the branch channel as a derived per-branch surface rather than the project's own top-level discussion channel."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:3"
      - "VISION_PROJECTS.md:81"
      - "VISION_PROJECTS.md:158"
  - statement: "Neither NIP-MP.md nor the `buzz projects`/`buzz projects add-channel` CLI code was found to auto-create a project's home channel at project-creation time when `--channel` is omitted; channel-first creation instead requires the caller to pass an existing channel UUID, which is only checked for UUID syntax, not for existence on the relay, before being written into the project (and default repository) tags."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-cli/src/commands/projects.rs:399-401"
      - "crates/buzz-cli/src/validate.rs:23-26"
      - "crates/buzz-sdk/src/builders.rs:2260-2265"
    confidence: 0.75
relationships:
  - type: part-of
    target: capabilities-projects-project
---

# Project channel: capability

A Buzz project (a named, owner-signed grouping of one or more git
repositories, NIP-MP `kind:30621`) can be bound to one **home channel** — the
top-level Buzz channel where the project's own discussion, and by convention
its default repository's activity, lives. A caller creating a project either
supplies an existing channel as that home (`--channel <uuid>`, required when
no `--repo` is given) or points the project at repositories that already carry
their own channel bindings. Once a project has a home channel, its owner (a
human, or an agent acting through the owner-review flow below) can also
request additional channels scoped to that same project — for example a
release-planning or docs channel alongside the main one — without disturbing
the single home-channel reference. This capability is what makes a project a
navigable *place* with one or more channels attached to it, distinct from the
ephemeral per-branch channels a push spawns and from the repository membership
that decides which git repos belong to the project at all.

## Maturity

**Shipped**, on both the CLI/relay side and the desktop client side.

- The home-channel binding is implemented in the NIP-MP event shape
  (`buzz-channel` tag), enforced for cardinality and length at relay ingest,
  and exercised by `buzz projects create --channel` and by the
  `fetch_projects_for_channel` lookup, which unit tests exercise directly.
- The additional-channel request flow is implemented end to end: the CLI
  builds and encrypts an owner-only `project_channel_request` observer frame
  (`buzz projects add-channel`), a dedicated unit test asserts its exact
  wire shape, and the desktop client both parses that request with its own
  independent validator and drives it through an approval dialog into a real
  channel-creation call (`useProjectChannelRequests`, `useAddProjectChannel`),
  recording the result as a `buzz-related-channel` tag on the project.

Nothing found during this node's research suggests either half is only
designed or in progress — both have production code paths and passing unit
tests, not merely a schema or a design document.

## Boundary

This node does not describe:

- **How a project is built** — the containers and components (relay,
  `buzz-cli`, `buzz-relay` git-hosting, the desktop app) that implement any of
  this. No architecture node for those exists in the corpus yet.
- **The interface(s) a project channel is exposed through** — the exact
  `buzz projects`/`buzz channels` CLI surface, the desktop React components,
  or the relay's HTTP/WebSocket routes. No interface node for those exists in
  the corpus yet.
- **The step-by-step flow through project-channel creation or the
  owner-review approval** — the sequence a caller or reviewer actually walks.
  No flow node for that exists in the corpus yet.
- **How the running system is operated** (deployment, monitoring, incident
  response) — out of scope for a capability node.
- **Per-branch channels** ("branch-as-room"): the channel Buzz creates
  automatically for a branch's push activity, which archives when the branch
  merges. That is a different, per-branch surface from this project-level
  home channel — see `VISION_PROJECTS.md`'s own narrative, cited above.
- **Project-repository membership**: which git repositories (`kind:30617`
  announcements) belong to a project via `a` tags, and the authority rules
  around adding/removing them. That is a separate concept from which channel
  the project's discussion lives in.
- **The overall "project" capability** (naming, description, visibility,
  deletion, cross-owner membership) beyond the channel-binding facet this
  node documents.

## Relationships

None declared. No architecture, interface or flow node documenting projects,
channels, or git hosting is merged on `origin/launchpad` at the revision this
node was checked against — confirmed by enumerating
`launchpad/docs/corpus/**/*.md`'s current node ids, none of which is
project-, channel-, or NIP-MP-shaped subject matter. The natural nodes to
`references` (an architecture node for the relay's project/channel handling,
an interface node for the `buzz projects` CLI surface, or the flow node for
the owner-review approval) are not yet drafted; adding those edges is future
work once such nodes exist, not a gap in this one.

## Scope and omissions

**This node covers** what a Buzz project's home-channel binding is (the
`buzz-channel` tag on its `kind:30621` event and, for channel-first creation,
on its default repository), how it is set and looked up, why it carries no
authorization weight, and the separate, additive `buzz-related-channel`
mechanism by which a project owner can attach further channels to a project
through an agent-drafted, owner-approved request.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the project/channel capability is built (containers, components) | a future architecture node (not yet drafted) |
| The `buzz projects`/`buzz channels` CLI and desktop UI surfaces | a future interface node (not yet drafted) |
| The step-by-step owner-review approval flow | a future flow node (not yet drafted) |
| Per-branch channels ("branch-as-room") | issue #809 (not yet drafted) |
| Project-repository membership (the `a`-tag member list) | issue #811 (not yet drafted) |
| The project capability overall (naming, visibility, deletion) | issue #812 (not yet drafted) |
| How the running system is operated | the `operations` corpus surface |

**Expected but not verified when this node was written:**

- **Whether a relay-side existence check on the `--channel` UUID is planned.**
  Today only UUID syntax is validated before the value is written into a
  project's (and its default repository's) tags — see the `INFERENCE` entry
  above. Whether this is a deliberate NIP-MP design choice (clients already
  MUST render an unresolvable `buzz-channel` gracefully) or a gap to close
  later was not settled by anything this node could cite, so it is recorded
  as an inference rather than a fact either way.
- **Whether `buzz-related-channel` will be formalized into NIP-MP itself.**
  It is currently a desktop-client-only convention riding on NIP-MP's
  "ignore unrecognized tags" rule. No issue or ADR discussing promoting it
  into the NIP's own tag table was found during this node's research.
- **No live end-to-end run was performed.** This node's Maturity claims rest
  on reading the CLI, SDK, relay-policy and desktop source and their existing
  unit tests, not on invoking `buzz projects create --channel` or the
  desktop approval dialog against a running relay during this task.
