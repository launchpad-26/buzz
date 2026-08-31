---
id: capabilities-projects-project
type: capabilities
status: draft
origin: upstream
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "NIP-MP defines kind:30621, an addressable 'project' event: a signed, named grouping of NIP-34 repository announcements (kind:30617), where a project may span repositories owned by different pubkeys and one repository may belong to several projects."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-MP.md:13"
  - statement: "A project is metadata only: its signer gains no authority over any member repository -- no edit, no delete, no push, no administration. Membership is an assertion about grouping, not a grant of permission, and push policy always reads the member repository's own kind:30617 event, never the project's."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-MP.md:15"
      - "docs/nips/NIP-MP.md:135"
  - statement: "A project with no member repositories is valid and MUST be rendered as an empty container rather than hidden or treated as malformed; this is the natural state after removing a project's last member."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-MP.md:147"
  - statement: "Deleting a project (NIP-09 kind:5 naming the project coordinate) deletes only the kind:30621 event; member repositories, their refs, channels and protections all survive, and each falls back to rendering as an implicit single-repository card unless another listing-eligible project still claims it. There is no cascade in either direction: deleting a member repository does not modify the project, it only leaves a coordinate that no longer resolves."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-MP.md:159"
      - "docs/nips/NIP-MP.md:167"
  - statement: "The relay's ingest pipeline enforces kind:30621's structural envelope (exactly one non-empty d tag, at most 64 member a tags with no duplicates, each a canonical 30617:<owner>:<repo-d> coordinate, bounded singleton metadata tags) in validate_project_envelope, and buzz-core assigns KIND_PROJECT the value 30621."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1609"
      - "crates/buzz-relay/src/handlers/ingest.rs:1524"
      - "crates/buzz-core/src/kind.rs:632"
  - statement: "The relay's project-envelope validation has a dedicated unit test suite exercising the d-cardinality, member-cap, member-tag-arity, member-coordinate-malformed, member-duplicate and metadata rules against a fixture oracle."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:4974"
  - statement: "buzz-sdk provides typed builders for the project event (build_project, build_project_with_tags, ProjectMemberCoord, validate_project_envelope) that CLI and other Rust callers use to construct and validate kind:30621 events before submission."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:2001"
      - "crates/buzz-sdk/src/builders.rs:2097"
      - "crates/buzz-sdk/src/builders.rs:2223"
      - "crates/buzz-sdk/src/builders.rs:2239"
  - statement: "buzz-cli exposes a full `projects` subcommand group -- create, get, list, add-repo, remove-repo, update (name/description/visibility), add-channel, delete -- implemented as a read-modify-write pattern over the caller's own live kind:30621 head."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:1284"
      - "crates/buzz-cli/src/commands/projects.rs:1"
  - statement: "The desktop app has a dedicated projects feature module covering project creation, deletion, repository attach/detach, ownership control, channel binding, and sidebar/collection rendering, with unit test coverage for each of those behaviors."
    entry_class: FACT
    evidence:
      - "desktop/src/features/projects/projectCreation.ts"
      - "desktop/src/features/projects/projectDeletion.ts"
      - "desktop/src/features/projects/useAddProjectRepository.ts"
      - "desktop/src/features/projects/projectOwnerControl.ts"
      - "desktop/src/features/projects/lib/projectCollection.ts"
  - statement: "VISION_PROJECTS.md's own Status table marks 'Multi-repo projects (kind:30621, NIP-MP)' as 'Designed' rather than shipped, which is stale relative to the merged, tested relay validation, SDK builders, CLI subcommand group and desktop feature module cited above; per AGENTS.md's evidence-precedence rule, executable evidence outranks documentation for how the system currently behaves, so this node's maturity claim rests on the code and not on that status line."
    entry_class: INFERENCE
    evidence:
      - "VISION_PROJECTS.md:255"
      - "crates/buzz-relay/src/handlers/ingest.rs:1609"
      - "crates/buzz-cli/src/lib.rs:1284"
    confidence: 0.85
  - statement: "Relay processing enforces at most 64 member `a` tags on a kind:30621 event, counting every tag rather than distinct coordinates, so that parse cost cannot scale with a duplicate-heavy tag list."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-MP.md:175"
  - statement: "Sibling corpus tasks #809 (branch-as-room), #810 (project-channel) and #811 (project-repository) merged together with this node as part of Feature #613's batch integration; each now carries a references edge from this node plus a reciprocal part-of edge back to it."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#812 dispatch instructions, cross-referencing #809/#810/#811 issue state"
  - statement: "At this node's recorded revision, the corpus tree on origin/launchpad contains no capability-, interface- or architecture-shaped node this document could reference without duplicating its content; the tree holds only meta/process nodes (AGENTS.md, README.md, standards/*, architecture/*, templates/*) and no prior capability instance."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/capability.md"
relationships:
  - type: references
    target: capabilities-projects-project-repository
  - type: references
    target: capabilities-projects-project-channel
  - type: references
    target: capabilities-projects-branch-as-room
---

# Project: capability

Buzz lets a signer group any set of git repositories -- including repositories
owned by other people -- into a single named, addressable **project**, so that
"the platform" (a relay, a desktop app, and a mobile app, each its own
repository) renders and is discussed as one thing instead of three unrelated
cards. A project is a `kind:30621` event ([NIP-MP](../../../../../docs/nips/NIP-MP.md)):
it names a set of member repositories by coordinate, carries its own display
name, description, and optional channel/visibility metadata, and is owned and
editable only by the pubkey that signed it. Grouping repositories across
owners is the one forge semantic per-repository tags cannot express -- Alice
cannot enroll Bob's repository into a group by editing a tag on an event only
Bob can sign -- and `kind:30621` exists to make that possible with one signer
holding all the group's own state in one replaceable event.

A user or agent creates a project (`buzz projects create <slug>`), adds or
removes member repositories owned by themselves or anyone else
(`add-repo`/`remove-repo`), updates its name, description or visibility
(`update`), lists and inspects projects (`list`/`get`), and deletes the
project container itself (`delete`) without touching any member repository.
Desktop surfaces the same capability as a projects feature module: creation,
deletion, membership management, ownership control, and sidebar rendering.

## Maturity

**Shipped.** The relay validates the full `kind:30621` structural envelope at
ingest (`validate_project_envelope`: exactly one non-empty `d` tag, at most 64
member `a` tags with no duplicates, each a canonical
`30617:<owner>:<repo-d>` coordinate, bounded singleton metadata), backed by a
fixture-driven unit test suite. `buzz-sdk` provides typed builders
(`build_project`, `build_project_with_tags`, `ProjectMemberCoord`) that both
`buzz-cli` and other Rust callers use. `buzz-cli` exposes a complete
`projects` subcommand group (`create`, `get`, `list`, `add-repo`,
`remove-repo`, `update`, `add-channel`, `delete`) implemented as a
read-modify-write cycle against the caller's own live head. The desktop app
has a dedicated `desktop/src/features/projects/` module with unit-tested
creation, deletion, repository attach/detach, ownership-control, and
sidebar/collection code.

`VISION_PROJECTS.md`'s own Status table still marks this row "📋 Designed,"
which is stale against that evidence -- the vision document describes where
the product is going, and drifts from what has since shipped. This claim
follows the corpus's own rule that executable evidence outranks documentation
for current behavior, not the status marker.

## Boundary

This node does not describe:
- **How a branch becomes a channel ("branch-as-room").** That per-branch
  conversation mechanic is a distinct capability, tracked as its own corpus
  task (issue #809), not part of what makes something a *project*.
- **The mechanics of a project's channel binding** (`buzz-channel` tag
  resolution, creation/adoption of the linked channel). That is issue #810's
  own scope; this node only notes that a project *may* carry a
  `buzz-channel` reference as metadata with no authority implication.
- **The mechanics of attaching/detaching a member repository** (coordinate
  parsing, ownership-independent add/remove flow in detail). That is issue
  #811's own scope; this node only states that membership exists and confers
  no authority.
- **How the relay, desktop, CLI, or SDK are built** (containers, components,
  technology choices). That is the architecture family's territory, not yet
  represented by a merged corpus node to reference.
- **The CLI or HTTP interface surface in full** (flag-by-flag command
  reference). That belongs to an interface-shaped node, not yet drafted.
- **The step-by-step flow of creating or joining a project.** That is a
  flow-shaped concern, not yet drafted as a corpus node.
- **How the running system is operated** (deployment, monitoring, incident
  response for project data). That is the `operations` corpus surface.

## Relationships

- `references`: `capabilities-projects-branch-as-room`,
  `capabilities-projects-project-channel`, `capabilities-projects-project-repository`
  (#809, #810, #811) -- added once Feature #613's whole batch merged together and all
  three siblings became valid, checkable relationship targets. Each sibling carries a
  reciprocal `part-of` edge back to this node.

Still open: `references` edges toward an architecture node for the relay/desktop
implementation and an interface node for the CLI/HTTP surface -- neither exists as a
merged corpus node yet.

## Scope and omissions

**This node covers** what the "project" capability is: a named,
signer-authored, addressable grouping of git repositories across owners
(`kind:30621`/NIP-MP), what a project's signer can and cannot do to it and
its members, the zero-member and deletion edge cases, and where the
capability currently stands (shipped, with citations to the relay, SDK, CLI
and desktop code that implement it).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Branch-as-channel conversation mechanic | issue #809 |
| Project-channel binding mechanics | issue #810 |
| Project-repository attach/detach mechanics | issue #811 |
| How the relay/desktop/CLI/SDK are built (containers, components) | the architecture family (not yet drafted) |
| The CLI/HTTP interface surface in full | an interface-shaped node (not yet drafted) |
| The step-by-step flow of creating or joining a project | a flow-shaped node (not yet drafted) |
| How the running system is operated | the `operations` corpus surface |

**Expected but not verified when this node was written:**
- **No end-to-end run of `buzz projects create`/`add-repo`/`delete` against a
  live relay was performed for this node.** The maturity claim rests on
  reading the relay's ingest validation, its unit tests, the SDK builders,
  the CLI command definitions, and the desktop feature module's source --
  not on exercising the full write path live.
- **The mobile app was not checked for project support.** No search for
  `KIND_PROJECT`/`30621` in `mobile/lib` was run while drafting this node,
  so mobile's coverage of this capability, if any, is unverified here.
- **NIP-OA owner-delete for projects** (the relay-side extension letting a
  human delete a project published by an agent they own) is documented in
  NIP-MP itself but was not independently verified against the relay's
  deletion-handling code for this node; it is cited from the specification
  only.
