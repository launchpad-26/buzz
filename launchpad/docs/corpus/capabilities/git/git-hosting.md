---
id: capabilities-git-git-hosting
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "Buzz's relay implements the git Smart HTTP protocol over three routes: `GET /git/{owner}/{repo}/info/refs?service={svc}` (ref advertisement), `POST /git/{owner}/{repo}/git-upload-pack` (clone/fetch) and `POST /git/{owner}/{repo}/git-receive-pack` (push), with NIP-98 signed-event authentication required on every route and no anonymous/public-repo access for v1."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "A repository is announced and identified by a NIP-34 kind:30617 (`KIND_GIT_REPO_ANNOUNCEMENT`) parameterized-replaceable event, and the relay derives and publishes a kind:30618 (`KIND_GIT_REPO_STATE`) event recording each repo's current ref state after a successful push."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The git-hosting module is organized as `crates/buzz-relay/src/api/git/{transport,hook,policy,cas_publish,manifest,manifest_event,store,binding,hydrate,pack_cache}.rs` — Smart HTTP transport, pre-receive hook injection, an HMAC-authenticated internal policy callback, and object-store CAS publish — per the module's own doc comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/mod.rs"
  - statement: "VISION_PROJECTS.md's own Status table marks \"Git hosting (smart HTTP + NIP-34)\" as \"Ships today,\" the same product-level status marker this node's Maturity section relies on."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:256"
  - statement: "`buzz-cli` exposes repository operations (for example fetching a caller's own kind:30617 repo announcement by `d`-tag repo id) as agent-facing subcommands, distinct from the git wire protocol itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/repos.rs"
  - statement: "The web client hosts a repository browser (repo list, tree, blob, commits, refs and README views) under `web/src/features/repos/`, reading repository content through the same relay-hosted git data rather than a separate storage system."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/ui/ReposPage.tsx"
      - "web/src/features/repos/ui/RepoTreeSection.tsx"
      - "web/src/features/repos/git-client.ts"
  - statement: "The end-to-end suite's `git_clone_push_fetch_force_roundtrip` and `git_concurrent_push_one_wins_and_repo_recovers` tests exercise clone, push, force-push, tag-push and concurrent-push-conflict behavior against a live relay and MinIO, but both are `#[ignore]`-gated behind a live relay, MinIO and `git`, so this node's verification claim rests on reading the test code, not on an executed run in this task."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_git.rs"
  - statement: "`architecture-flows-git-push` already documents, at the level of one HTTP request-response pair, the transport authentication (NIP-98), relay-membership gate (NIP-43), pre-receive policy callback, ref-update authorization matrix, and object-store CAS publish that a `git push` goes through — this capability node deliberately does not restate any of that sequence, citing the flow node instead."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/git-push.md"
  - statement: "Sibling corpus-authoring issues #746 (git-object-storage), #747 (git-signing), #748 (nostr-git-authentication), #749 (patch), #750 (repository-announcement), #751 (repository-browser), #752 (repository), and #753 (smart-http) were opened under the same parent Feature #613 to cover slices of git hosting more specific than this capability-level overview node; none were confirmed merged to `origin/launchpad`'s corpus tree at the recorded revision, so this node names them as boundary subjects rather than declaring relationship edges to unmerged ids."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz issue #745 dispatch instructions (batch run for Feature #613), naming sibling issues #746-#753"
relationships:
  - type: references
    target: architecture-flows-git-push
  - type: implements
    target: corpus-template-capability
---

# Git hosting: capability

Buzz hosts git repositories directly. An agent or developer can `git clone` and
`git push` a repository over standard git Smart HTTP against a Buzz relay, using
their existing Nostr identity for authentication instead of a separate git
credential — the same identity that authenticates every other Buzz surface. A
repository's existence and identity are themselves signed Nostr events (NIP-34),
so a Buzz-hosted repo is discoverable and its ref state independently verifiable
by anything that can read the relay's event stream, not only by git itself.

## Maturity

**Shipped.** VISION_PROJECTS.md's own Status table marks "Git hosting (smart
HTTP + NIP-34)" as "Ships today" (`VISION_PROJECTS.md:256`), and the relay's
`crates/buzz-relay/src/api/git/` module implements the three Smart HTTP routes
(`info/refs`, `git-upload-pack`, `git-receive-pack`) end to end, including
authentication, pre-receive authorization, and object-store publish. The
end-to-end suite (`crates/buzz-test-client/tests/e2e_git.rs`) exercises clone,
push, force-push, tag-push and concurrent-push-conflict scenarios against a
live relay and MinIO, though those tests are `#[ignore]`-gated and were read
rather than executed while authoring this node.

## Boundary

This node does not describe:
- **How a push is authenticated and authorized, step by step.** That is
  `architecture-flows-git-push`'s subject: NIP-98 transport signing, the NIP-43
  relay-membership gate, the pre-receive policy callback, and the ref-update
  authorization matrix. This node cites that flow rather than restating it.
- **How repository content is durably stored.** Object-store CAS layout, pack
  and manifest formats, and pointer semantics are `crates/buzz-relay/src/api/git/{cas_publish,manifest,store}.rs`'s
  territory — the subject of sibling issue #746 (git-object-storage), not yet a
  merged corpus node.
- **Signing individual git objects with a Nostr key (NIP-GS).** That is an
  independent, optional concern (`crates/git-sign-nostr`) from hosting the repo
  itself, distinct from the NIP-98 transport authentication this capability
  relies on — the subject of sibling issue #747 (git-signing).
- **The precise Nostr-credential authentication mechanics** (`git-credential-nostr`,
  the NIP-98/NIP-43 gate as its own contract) beyond what is needed to state
  that git hosting authenticates via Nostr identity — the subject of sibling
  issue #748 (nostr-git-authentication).
- **Patches, pull requests, and issues as Nostr events** (kind:1617 patch,
  kind:1618/1619 pull request, kind:1621 issue) — VISION_PROJECTS.md's own
  Status table lists several of these as "Designed" rather than shipped, and
  they are the subject of sibling issue #749 (patch) and related forge-layer
  work, not this node.
- **The repository-browser UI and the repository-announcement event's own
  field-level contract** — `web/src/features/repos/`'s tree/blob/commit views
  and the kind:30617 announcement's tag vocabulary are the subject of sibling
  issues #751 (repository-browser) and #750 (repository-announcement).
- **The smart-HTTP wire protocol's own route-level contract** (request/response
  shapes, headers, status codes as an interface in its own right) — the subject
  of sibling issue #753 (smart-http), which this node cites at the capability
  level (three routes exist, NIP-98-gated) without documenting as an interface.
- **How the running relay is operated** (deployment, monitoring, incident
  response for the git-hosting subsystem) — a corpus `operations` concern, not
  this node's.

## Relationships

- references: architecture-flows-git-push — the authenticated push transport
  flow this capability relies on, already documented step by step.
- implements: corpus-template-capability — this node follows that template's
  required sections (Capability statement, Maturity, Boundary, Relationships,
  Scope and omissions).

## Scope and omissions

**This node covers** what the git-hosting capability is — clone/push over
Smart HTTP with Nostr-identity authentication and NIP-34 repository
announcement/state events — and its current maturity, at the product level a
stakeholder would recognize, without restating how it is built, authenticated
step by step, stored, signed, or exposed through the CLI/web/protocol
interfaces layered on top of it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Step-by-step push authentication and authorization | `architecture-flows-git-push` (merged) |
| Object-store CAS, manifest and pack storage internals | Sibling issue #746 (git-object-storage), not yet a merged corpus node |
| NIP-GS commit/tag object signing | Sibling issue #747 (git-signing), not yet a merged corpus node |
| Nostr-identity git-credential mechanics as their own contract | Sibling issue #748 (nostr-git-authentication), not yet a merged corpus node |
| Patches, pull requests, issues as Nostr events (forge layer) | Sibling issue #749 (patch) and related forge-layer work; several marked "Designed" rather than shipped in VISION_PROJECTS.md |
| Repository-announcement event's field-level contract | Sibling issue #750 (repository-announcement), not yet a merged corpus node |
| Repository-browser UI | Sibling issue #751 (repository-browser), not yet a merged corpus node |
| The `repository` concept/entity itself, independent of hosting it | Sibling issue #752 (repository), not yet a merged corpus node |
| The Smart HTTP wire protocol as its own interface contract | Sibling issue #753 (smart-http), not yet a merged corpus node |
| How the relay's git-hosting subsystem is operated | The `operations` corpus surface |
| The front-matter contract itself, and creating/updating/retiring a node procedurally | `node.schema.json`, `AGENTS.md` |

**Expected but not verified when this node was written:**

- **Neither end-to-end git test was executed.** `git_clone_push_fetch_force_roundtrip`
  and `git_concurrent_push_one_wins_and_repo_recovers` in
  `crates/buzz-test-client/tests/e2e_git.rs` are both `#[ignore]`-gated behind a
  live relay, MinIO and `git`; this node's shipped-maturity claim rests on
  reading the production code paths and the tests' assertions, not on a passing
  run performed in this task.
- **The web repository browser's runtime behavior was not exercised.** Only the
  presence of the relevant source files under `web/src/features/repos/` was
  confirmed by inspection; no build or manual click-through was performed.
- **`buzz-cli`'s full `repos` subcommand surface was not enumerated.** Only
  `fetch_own_repo_announcement` was read directly, as evidence that
  agent-facing repo operations exist in the CLI distinct from the git wire
  protocol; the complete subcommand set was not catalogued here.
