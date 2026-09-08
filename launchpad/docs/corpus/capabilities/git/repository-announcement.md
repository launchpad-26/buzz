---
id: capabilities-git-repository-announcement
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "`KIND_GIT_REPO_ANNOUNCEMENT` is 30617, documented as NIP-34's repository announcement, and is asserted (via a compile-time `const _: () = assert!(...)`) to fall inside the parameterized-replaceable kind range, meaning a second announcement from the same author with the same `d` tag replaces the first rather than creating a new event."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The relay's kind:30617 handler (`handle_git_repo_announcement_inner`) requires a `d` tag, validates it against `[a-zA-Z0-9._-]{1,64}` with no leading dot and no `..`, then either confirms an existing same-owner reservation (idempotent re-announce) or atomically reserves the name in Postgres for a new owner after checking a per-pubkey quota; a name already held by a different owner is rejected as a collision. No bare git repository is created on disk at announcement time -- the relay holds no persistent per-repo disk state, and reads/writes hydrate an ephemeral repo from object storage per request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "The SDK builder `build_repo_announcement` (and its metadata-preserving counterpart `build_repo_announcement_with_tags`) constructs the kind:30617 event client-side, validating the same repo-id shape (`check_repo_id`, shared with `GitRepoCoord` so a hand-built `a`-tag coordinate can't carry an invalid `d`-tag) plus length limits on `name` (128), `description` (1024), up to 5 `clone` URLs, an `http(s)://` `web` URL, and up to 10 `ws(s)://` `relays`."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "The name registry is a Postgres table (`git_repo_names`, accessed via `buzz-db`'s `reserve_repo_name`/`repo_name_owner`/`count_repos_for_owner`/`release_repo_name`) keyed `(community_id, repo_id)`, using `INSERT ... ON CONFLICT DO NOTHING` so concurrent announcements for the same name can't both win; `git_repo.rs`'s own module doc states this makes the relay stateless (no local per-repo filesystem state, no shared ReadWriteMany volume needed), and the kind:30617 handler's comments state this specifically replaced a prior v1 local-disk `.names/` index."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/git_repo.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "A fresh (non-re-announce) claim seeds an empty-manifest pointer in object storage (`seed_manifest_pointer`, strict create-only) so the repo becomes clone-able, and only a genuinely fresh claim is rolled back (name released) if that seed fails; a same-owner re-announce instead calls the tolerant `ensure_manifest_pointer`, which never overwrites a pointer a prior push already established."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "Only a fresh reservation additionally emits a derived kind:30618 (NIP-34 repository state) event over the seeded empty manifest, built by the pure function `manifest_event`'s ref-state builder; a re-announce does not re-emit it, because a replaceable kind:30618 emitted after a real push would shadow the pushed refs under NIP-16 latest-wins ordering."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
      - "crates/buzz-relay/src/api/git/manifest_event.rs"
  - statement: "The per-pubkey repo count limit is configurable via `BUZZ_GIT_MAX_REPOS_PER_PUBKEY`, defaulting to 100 when unset."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "The first `buzz-channel` tag on a kind:30617 announcement -- not any subsequent duplicate, even a well-formed one -- IS the repo's git ACL: both the read gate and the push policy endpoint authorize against membership in that bound channel, and a malformed or missing first tag resolves fail-closed (`RepoBinding::Broken`/`NotBound`) rather than falling through to a later, possibly-attacker-appended, valid tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/binding.rs"
  - statement: "VISION_PROJECTS.md's own product-status table marks \"Git hosting (smart HTTP + NIP-34)\" as \"Ships today\", and the e2e suite in `buzz-test-client` announces a repo with a raw kind:30617 event (bound to a test channel via `buzz-channel`) as a precondition for exercising git push/pull against the relay -- both consistent with repository announcement being shipped, not merely designed."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:256"
      - "crates/buzz-test-client/tests/e2e_git.rs"
  - statement: "At the recorded revision, no `capabilities/` directory exists anywhere in the corpus tree merged on `origin/launchpad`, so this node is not a duplicate of any existing canonical document, and `architecture-containers-relay`, `architecture-containers-postgres`, `architecture-containers-object-storage` and `architecture-flows-git-push` are the only architecture-family ids merged there that this node's `references` could legitimately target."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/**, schema/**, standards/**, templates/** ; no capabilities/ entry, run against commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
relationships:
  - type: part-of
    target: capabilities-git-git-hosting
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-containers-postgres
  - type: references
    target: architecture-containers-object-storage
  - type: references
    target: architecture-flows-git-push
---

# Repository announcement: capability

Buzz lets a pubkey claim and describe a git repository by publishing one signed
Nostr event: a NIP-34 kind:30617 "repository announcement". Publishing it is
how a repo comes into existence on a Buzz relay -- there is no separate
"create repo" HTTP call. The announcement names the repo (its `d` tag is the
permanent identifier), optionally carries a human-readable name, description,
clone URLs, a web URL and relay hints, and -- distinctively for Buzz -- binds
the repo to a channel via a `buzz-channel` tag, which becomes the repo's
access-control boundary for every subsequent read and push. Publishing the
same `d` tag again from the same key updates the announcement in place
(it is a parameterized-replaceable event); publishing it from a different key
is rejected as a name collision.

## Maturity

**Shipped.** VISION_PROJECTS.md's own product-status table lists "Git hosting
(smart HTTP + NIP-34)" as "Ships today" (`VISION_PROJECTS.md:256`), and the
capability is implemented end-to-end: the kind:30617 handler in
`crates/buzz-relay/src/handlers/side_effects.rs`, the client-side event
builders in `crates/buzz-sdk/src/builders.rs`, the Postgres name registry in
`crates/buzz-db/src/store/git_repo.rs`, and e2e coverage in
`crates/buzz-test-client/tests/e2e_git.rs` that announces a repo as the
precondition for every push/pull scenario it exercises.

## Boundary

This node does not describe:
- **How the relay, Postgres and object storage are built** -- their
  responsibilities, technology choices and deployment shape are the
  architecture family's territory. See `architecture-containers-relay`,
  `architecture-containers-postgres` and `architecture-containers-object-storage`.
- **The interface(s) this capability is exposed through** -- the CLI
  subcommand or SDK call an agent or client actually invokes to publish an
  announcement. No interface-type corpus node is merged yet for this subject.
- **The step-by-step flow of a git push** -- what happens after a repo already
  exists, when a client pushes commits through the pre-receive hook and policy
  endpoint. That is `architecture-flows-git-push`, already merged and
  `references`d below rather than restated here.
- **How the running system is operated** -- deployment, monitoring, incident
  response for git hosting is the `operations` corpus surface, not this node.
- **The wire-level smart-HTTP transport or the object-storage manifest
  format** -- both are separate capability/architecture subjects (tracked as
  sibling batch tasks: smart-http, git-object-storage) that this node cites by
  reference, not by re-description.

## Relationships

- references: `architecture-containers-relay` -- the relay hosts the kind:30617
  handler that reserves the name and seeds the manifest pointer.
- references: `architecture-containers-postgres` -- `buzz-db`'s `git_repo_names`
  table is the atomic name registry an announcement claims a row in.
- references: `architecture-containers-object-storage` -- the empty-manifest
  pointer an announcement seeds (or, on re-announce, ensures) lives in object
  storage, making the repo clone-able without any persistent local disk state.
- references: `architecture-flows-git-push` -- the flow a repo enters once an
  announcement has made it exist; this node does not repeat that flow's steps.

## Scope and omissions

**This node covers** what a kind:30617 repository announcement is, what
publishing one causes the relay to do (name reservation, idempotent
re-announce vs. cross-owner collision, per-pubkey quota, empty-manifest
seeding, the derived one-time kind:30618 emission), and the fact that the
announcement's `buzz-channel` tag is the repo's access-control binding, not
merely descriptive metadata.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the relay, Postgres and object storage containers are built | `architecture-containers-relay` / `architecture-containers-postgres` / `architecture-containers-object-storage` |
| The step-by-step git push flow once a repo exists | `architecture-flows-git-push` |
| The CLI/SDK interface surface used to publish an announcement | not yet a merged interface-type corpus node |
| The wire-level smart-HTTP transport | tracked separately (smart-http capability, not yet merged) |
| The object-storage manifest's on-disk/on-S3 format | tracked separately (git-object-storage capability, not yet merged) |
| How the running system is operated (deployment, monitoring, incident response) | the `operations` corpus surface |

**Expected but not verified when this node was written:**
- **No architecture-family node yet documents the `buzz-channel`
  read-gate/push-policy authorization path in detail** (SEC-005, the read
  gate; `policy::hook_callback`, the push policy endpoint). This node cites
  `crates/buzz-relay/src/api/git/binding.rs` directly for the ACL claim rather
  than pointing at a corpus node, because none exists yet to reference.
- **The push-side pre-receive hook and HMAC policy callback** were read only
  far enough to confirm they consume the `buzz-channel` binding this node
  describes; their own mechanics belong to `architecture-flows-git-push` and
  were not re-verified here beyond that boundary.
