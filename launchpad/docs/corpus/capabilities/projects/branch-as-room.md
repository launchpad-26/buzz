---
id: capabilities-projects-branch-as-room
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
  - statement: "VISION_PROJECTS.md's 'Branches as Channels' section states the intended design in these terms: 'When you create a branch, Buzz creates a channel. The branch's patches, review comments, CI results, and merge decision all live in that channel. When the branch merges, the channel archives.'"
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:77-97"
  - statement: "VISION_PROJECTS.md's own Status table marks 'Project binding (kind:30617 + `buzz-` tags)' as '📋 Designed', distinct from the rows marked '✅ Ships today' (Channels/forums/DMs/canvases, workflow engine, MCP+ACP harness, Blossom media, git hosting) -- the mechanism the branch-as-channel vision depends on is not itself marked shipped."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:245-259"
  - statement: "The relay resolves exactly one channel binding per repository: `resolve_repo_binding` reads the *first* `buzz-channel` tag on a repo's kind:30617 announcement and returns a fail-closed tri-state (`NotBound` / `Bound(Uuid)` / `Broken`) over that single tag -- there is no per-branch tag or per-branch binding structure in this resolver."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/binding.rs:32-58"
  - statement: "Desktop's branch-operation error handling treats 'no channel binding' as a single repository-wide condition: `isNoChannelBindingError` matches the relay's `no_channel_binding` denial token, and the resulting dialog copy tells the user to bind the whole repository to one channel with `buzz repos bind --id <repo> --channel <channel-uuid>` -- there is no per-branch variant of this remediation."
    entry_class: FACT
    evidence:
      - "desktop/src/features/projects/lib/projectBranchErrors.ts:1-35"
  - statement: "`buildRepositoryChannelBindingTemplate` constructs the kind:30617 event template that carries a repository's `buzz-channel` tag, taking a single `channelId` for the whole `repository` -- confirming the desktop client also models the binding as one channel per repository, not one per branch."
    entry_class: FACT
    evidence:
      - "desktop/src/features/projects/projectRepositoryCreation.ts:98-115"
  - statement: "The already-merged corpus node `architecture-flows-git-push` documents this same repo-level channel-binding authorization model for the git push flow, including that the default permission matrix requires only `Member` to create or fast-forward a branch ref, with no channel created or altered as part of that operation."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/git-push.md"
  - statement: "No code path in `crates/` creates a channel as a side effect of a git branch being created or pushed. A grep of every `create_channel`/`create_channel_with_id` call site outside test modules finds two production callers -- generic NIP-29 `create_group` event handling (`handle_create_group`) and its h-tag pre-creation counterpart in event ingestion -- and neither is reached from the git branch-create (`create_project_remote_branch`) or git-push transport code paths, which contain no channel-creation call at all."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "desktop/src-tauri/src/commands/project_git_branches.rs"
    confidence: 0.85
  - statement: "No merge or branch commit in this repository's git history implements or removes a per-branch, automatic channel-creation feature; branch names containing 'channel' in the log (e.g. 'projects-channel-first-pt1-agent-cli') are development branches for the repository-level project-channel binding feature described above, not a per-git-branch room feature."
    entry_class: INFERENCE
    evidence:
      - "git_log_all_grep(pattern='branch.*channel|channel.*branch|branch.*room|room.*branch', case_insensitive=true, ref='cad6c375fdcc590158c1456c9fc7875f0f84a844') -> matches are either unrelated channel-feature merge commits or 'projects-channel-first-*' development-branch merges, run 2026-08-31"
    confidence: 0.75
relationships:
  - type: part-of
    target: capabilities-projects-project
  - type: references
    target: architecture-flows-git-push
  - type: implements
    target: corpus-template-capability
---

# Branch as room: capability

A **branch as room** is the envisioned capability, described in VISION_PROJECTS.md's
"Branches as Channels" section, that creating a git branch in a Buzz project would
automatically create a dedicated channel for it -- a "room" holding the branch's
patches, CI results, review comments, and merge decision as one continuous
conversation, which then archives when the branch merges. The stated payoff is that
the channel *is* the pull request, the CI dashboard, and the discussion thread, so a
contributor or agent working a branch never tab-switches between separate tools.

## Maturity

**Designed, not implemented, as of this revision.** VISION_PROJECTS.md's own Status
table marks "Project binding (kind:30617 + `buzz-` tags)" -- the mechanism this
capability would need -- as "📋 Designed", not "✅ Ships today". What the codebase
implements today is a coarser, already-shipped mechanism: exactly one channel bound
to an *entire repository*, via a single `buzz-channel` tag on that repository's
kind:30617 announcement, resolved fail-closed by `resolve_repo_binding`. Every
branch in that repository shares that one channel; the relay contains no per-branch
tag, table, or binding structure, and no call site creates a channel as a side
effect of a branch being created or pushed (see the evidence ledger's `INFERENCE`
entries for the two production channel-creation call sites, both generic NIP-29
group creation, neither reachable from branch-create or git-push code). Nothing
found in this repository's git history shows this capability having existed
previously and been removed.

## Boundary

This node does not describe:
- **How a repository-level channel binding is built or authorized.** That is
  already documented by the architecture flow node for git push
  (`architecture-flows-git-push`), which this node `references` rather than
  restating; branch-ref permission levels, the fail-closed `NotBound`/`Bound`/
  `Broken` resolution, and the CAS-based push path all live there.
- **The interface(s) a project or repository binding is exposed through** (CLI
  subcommands, HTTP routes) -- no interface-typed corpus node exists yet to
  reference.
- **The step-by-step flow of one push/review/merge interaction** -- no flow-typed
  corpus node for this exists yet to reference.
- **How the running system is operated** (deployment, monitoring, incident
  response) -- out of scope for a capability node regardless of maturity.
- **The already-implemented, repository-wide channel-binding capability itself**
  (binding one whole repository, or one whole multi-repo project, to a single
  channel). That is a distinct, already-shipped capability with its own
  maturity and its own corpus node under this same `capabilities/projects/`
  family -- this node covers only the finer-grained, per-branch "room" idea,
  which does not exist in the codebase today.

## Relationships

- `references: architecture-flows-git-push` -- the merged architecture node
  documenting the git-push flow and the repository-level channel-binding
  authorization model this envisioned capability would build on top of.
- `implements: corpus-template-capability` -- this node follows that template's
  required sections (Capability statement, Maturity, Boundary, Relationships,
  Scope and omissions).
- No `references` or `part-of` edge is declared toward a project-channel,
  project-repository, or overall project capability node: none of those is
  merged on `origin/launchpad` at the recorded revision, so none is a valid
  relationship target yet (`AGENTS.md`'s own rule: check the merge target, not
  an unmerged sibling's worktree).

## Scope and omissions

**This node covers** what the "branch as room" capability is envisioned to be per
VISION_PROJECTS.md, its current maturity (designed only; the repository-level
channel binding it would extend already ships, but no per-branch channel-creation
code exists), and its boundary against the architecture flow that implements the
capability it would sit on top of.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How a repository-level (not per-branch) channel binding works | `architecture-flows-git-push` |
| The overall project capability (grouping repositories, project-level identity) | a separate, not-yet-merged capability node |
| The project-channel and project-repository binding capabilities | separate, not-yet-merged capability nodes |
| Any future implementation plan or timeline for per-branch rooms | not tracked in this corpus at this revision |

**Expected but not verified when this node was written:**
- **Whether a GitHub issue or roadmap item formally tracks future implementation**
  of per-branch channel automation was not exhaustively searched (only git commit
  history and the current source tree were checked); an open issue proposing this
  work may exist without this node's evidence ledger reflecting it.
- **Whether any Buzz client (desktop, mobile, CLI) has UI or copy anticipating a
  future per-branch channel** (for example, a disabled control or a "coming soon"
  label) was not searched for; only the active binding/error-handling code paths
  were inspected.
