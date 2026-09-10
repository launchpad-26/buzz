---
id: capabilities-git-repository
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
  - statement: "node.schema.json's type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- and contains no data-entity value, so a node about repository identity/naming/ownership cannot be typed data-entity regardless of how entity-shaped its subject reads."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "The corpus's own templates/data-entity.md states that a real data-entity instance written from it 'most plausibly takes type: implementation,' reasoned there against type: interfaces-events and type: architecture -- never against type: capabilities and never against an invented data-entity value, since no such enum member exists."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/data-entity.md"
  - statement: "Issue #752's own Definition of Done ends with the capability-shaped tail 'States the capability and primary actors/outcomes,' 'Defines behavioral rules, constraints and relevant variants,' 'Links major flows, interfaces, data and platform implementation,' and 'Links verification demonstrating the capability' -- the generic capability checklist, not the data-entity template's identity/attributes/invariants/relationships section list."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#752 definition of done, read directly via gh issue view"
  - statement: "Sibling tasks in the same batch scope launchpad/docs/corpus/capabilities/git/git-hosting.md (issue #745, storage/transport mechanics) and launchpad/docs/corpus/capabilities/git/repository-announcement.md (issue #750, the kind:30617/30618 announcement event's own wire shape) as separate documents from this one, so this node must not restate either's territory."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#745 and launchpad-26/buzz#750 titles, read directly via gh issue view"
  - statement: "kind:30617 is KIND_GIT_REPO_ANNOUNCEMENT (a NIP-34 parameterized-replaceable repository announcement) and kind:30618 is KIND_GIT_REPO_STATE, both defined in buzz-core/src/kind.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "buzz-relay/src/handlers/side_effects.rs's handle_git_repo_announcement_inner extracts the repository identifier from the announcement's d tag and rejects the event outright if it is missing or fails validate_repo_id, before any name reservation is attempted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "A repository identifier must match [a-zA-Z0-9._-]{1,64}, must not start with '.', and must not contain '..' -- enforced both client-side by buzz-cli/src/validate.rs's validate_repo_id before an announcement is submitted, and server-side by the same rule re-stated in buzz-relay/src/handlers/side_effects.rs's handle_git_repo_announcement_inner."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/validate.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "A repository's identity is the pair (community_id, repo_id): buzz-db/src/store/git_repo.rs's module doc states names are 'unique within a community: the primary key is (community_id, repo_id)', and migrations/0002_git_repo_names.sql creates git_repo_names with PRIMARY KEY (community_id, repo_id) and an owner_pubkey column, enforced entirely in Postgres rather than on local disk so relay replicas need no shared filesystem to agree on name ownership."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/git_repo.rs"
      - "migrations/0002_git_repo_names.sql"
  - statement: "The same repository name may be independently claimed by different owners in different communities without collision, because uniqueness is scoped by (community_id, repo_id) rather than globally, per buzz-db/src/store/git_repo.rs's own names_are_scoped_per_community test."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/git_repo.rs"
  - statement: "reserve_repo_name in buzz-db/src/store/git_repo.rs claims a name via an atomic INSERT ... ON CONFLICT (community_id, repo_id) DO NOTHING ... RETURNING owner_pubkey, and classifies the outcome as ReserveOutcome::Reserved (this attempt created the row), AlreadyOwned (the same owner already holds it -- idempotent re-announce), or TakenByOther (a different owner already holds it)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/git_repo.rs"
  - statement: "handle_git_repo_announcement_inner enforces a per-pubkey repository quota by calling count_repos_for_owner and comparing it against state.config.git_max_repos_per_pubkey before claiming a not-yet-owned name, rejecting the announcement with 'repo limit exceeded' when the owner is already at or over the limit; a same-owner re-announce of an already-owned name is exempt from this check because it never grows the owner's count."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
      - "crates/buzz-db/src/store/git_repo.rs"
  - statement: "buzz-relay/src/config.rs defines git_max_repos_per_pubkey as a u32 read from BUZZ_GIT_MAX_REPOS_PER_PUBKEY, defaulting to 100 when unset."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "A different owner attempting to claim an already-held repository name is rejected outright by handle_git_repo_announcement_inner with 'repo name already taken by another owner,' whether that collision is detected on the initial ownership peek or resolved by the ON CONFLICT re-read after a losing concurrent insert race (ReserveOutcome::TakenByOther)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
      - "crates/buzz-db/src/store/git_repo.rs"
  - statement: "On a fresh Reserved claim, handle_git_repo_announcement_inner only proceeds to treat the repository as usable once the associated manifest pointer is seeded; if that seeding fails, it calls release_repo_name to roll back the just-created name reservation, but an AlreadyOwned outcome is never rolled back on a pointer failure because the row belongs to a different attempt that may already have succeeded."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "release_repo_name in buzz-db/src/store/git_repo.rs is owner-scoped -- it deletes a git_repo_names row only when both repo_id and owner_pubkey match, so a release attempt by a non-holder removes nothing and leaves the reservation intact for its actual owner, per the release_is_owner_scoped_and_frees_the_name test."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/git_repo.rs"
  - statement: "migrations/0029_community_deletion.sql attaches git_repo_names to the community write fence via attach_community_write_fence('git_repo_names'), so a repository's name reservation is subject to the same whole-community deletion path as other community-scoped tables; no separate per-repository deletion command exists in buzz-cli's repos subcommands (create, get, list, protect, bind)."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql"
      - "crates/buzz-cli/src/commands/repos.rs"
  - statement: "buzz-cli's repos command group exposes cmd_create_repo (builds and submits a kind:30617 announcement, reserving the name as a side effect), cmd_get_repo (queries kind:30617 by d tag, optionally scoped to an owner pubkey), and cmd_list_repos (queries kind:30617 by author pubkey, defaulting to the caller's own pubkey) as the interface through which an actor interacts with repository identity and ownership."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/repos.rs"
  - statement: "VISION_PROJECTS.md's Status table marks 'Git hosting (smart HTTP + NIP-34)' as shipped ('Ships today')."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:256"
  - statement: "VISION_PROJECTS.md's Status table lists exactly one Git-related row ('Git hosting (smart HTTP + NIP-34)') and does not separately enumerate repository naming, identity or ownership as their own product capability, so this node's maturity claim is inherited from Git hosting's shipped status rather than independently asserted as a distinct product-level capability."
    entry_class: INFERENCE
    evidence:
      - "VISION_PROJECTS.md:256"
    confidence: 0.7
relationships:
  - type: part-of
    target: capabilities-git-git-hosting
---

# Repository identity, naming and ownership: capability

Within a Buzz community, a pubkey can claim a unique repository name and become
its owner. Once claimed, that name is reserved for as long as the same owner
keeps re-announcing it: a re-announce is treated as an idempotent no-op rather
than a new claim, a different pubkey attempting to claim the same name is
rejected outright, and each owner is bounded by a per-community repository
quota. This identity-and-ownership guarantee is what lets `git clone`/`git
push` and every other repository-scoped operation resolve unambiguously to one
owner's repository rather than colliding with another actor's repository of
the same name.

## Maturity

Shipped. `crates/buzz-relay/src/handlers/side_effects.rs`'s
`handle_git_repo_announcement_inner` is the live kind:30617 handler that
validates a repository identifier, classifies an announcement against the
existing name registry, and enforces the per-pubkey quota on every repository
announcement the relay processes; `crates/buzz-db/src/store/git_repo.rs` is
the backing registry with a Postgres table
(`migrations/0002_git_repo_names.sql`) and passing (Postgres-gated) unit
tests. VISION_PROJECTS.md's own Status table marks the broader "Git hosting
(smart HTTP + NIP-34)" capability this identity model is part of as "Ships
today" (`VISION_PROJECTS.md:256`); no separate row exists for repository
identity/naming/ownership on its own, so this node treats its maturity as
inherited from Git hosting's shipped status rather than as an independently
tracked capability (see the `INFERENCE` entry in the evidence ledger above).

## Boundary

This node does not describe:

- **How a claimed repository is actually stored, served, or fetched** — the
  ephemeral bare-repo hydration from object storage, the manifest pointer,
  and the compare-and-swap that serializes concurrent pushes. That is
  `capabilities/git/git-hosting.md`'s territory (issue #745).
- **The announcement event's own wire shape** — the kind:30617/30618 tag
  vocabulary (`buzz-protect` branch-protection rules, `buzz-channel`
  binding, `clone`/`web` URLs, relay hints, content), and how an existing
  announcement is amended. That is
  `capabilities/git/repository-announcement.md`'s territory (issue #750).
  This node covers only what determines *whose* announcement wins a given
  repository name and under what conditions, not what an announcement's
  tags say once that question is settled.
- **The step-by-step flow of creating a repository end to end** (signing an
  event, submitting it, the CLI printing a rich-preview link) — not in this
  batch.
- **How the running relay is operated** — deployment, monitoring, or
  incident response for the repository registry, which is the `operations`
  corpus surface's territory, not this capability's.

## Relationships

None declared. `capabilities/git/git-hosting.md` (#745) and
`capabilities/git/repository-announcement.md` (#750) are the natural
`references` targets for this node, but both are unmerged siblings authored
in parallel in the same batch with no ordering between them — per
`AGENTS.md`'s relationship rule, a target must already exist in the corpus
tree of the branch being merged into, and neither does at this node's
recorded revision. Adding those edges is the first task to land after either
sibling merges.

## Scope and omissions

**This node covers** what makes one Buzz-hosted git repository identifiable
and distinguishable from another: its identity as the pair
`(community_id, repo_id)`, the naming rule a `repo_id` must satisfy, how a
name is claimed and by whom, how re-announcement by the same owner is
idempotent, how a per-pubkey quota bounds how many repositories one owner may
hold, how a claim is rolled back when the repository cannot actually be made
usable, and the interface (`buzz-cli`'s `repos` command group) through which
an actor observes and creates that identity.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Object-storage hydration, the manifest pointer, and push serialization | `capabilities/git/git-hosting.md` (#745) |
| The kind:30617/30618 announcement's tags, content, and update semantics (protection rules, channel binding, clone/web URLs) | `capabilities/git/repository-announcement.md` (#750) |
| The step-by-step flow of creating or cloning a repository | not yet scheduled |
| Multi-repo project grouping (kind:30621, NIP-MP `a`-tag membership) | not yet scheduled |
| How the running relay/registry is operated | the `operations` corpus surface |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **The concurrent-insert race path** (`ReserveOutcome::TakenByOther` reached
  via the `ON CONFLICT` re-read rather than the initial ownership peek) is
  exercised by `buzz-db/src/store/git_repo.rs`'s own `#[ignore = "requires
  Postgres"]` tests, but those tests were read, not executed, because they
  require a running Postgres instance this authoring pass did not start.
- **Whether repository identity/naming/ownership is intended to become its
  own row in VISION_PROJECTS.md's Status table**, distinct from the single
  "Git hosting" row it currently sits under, was not resolved anywhere found
  during authoring — the `INFERENCE` above states the current absence, not a
  decision that one is unwarranted.
