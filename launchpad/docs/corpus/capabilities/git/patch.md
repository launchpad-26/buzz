---
id: capabilities-git-patch
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
  - statement: "kind:1617 is defined as \"NIP-34: Patch (git format-patch output)\", alongside kind:1618 (pull request), kind:1619 (PR update), kind:1621 (issue), and kind:1630/1631/1632/1633 (status: open/applied-merged/closed/draft), all in the same NIP-34 custom-kind block."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "buzz_sdk::build_git_patch constructs a kind:1617 event: content is the verbatim `git format-patch` output (never truncated), rejected if empty or over a 60KB size bound; it tags `a` (repo coordinate, kind:30617), `p` (repo owner, plus any additional recipients), and optionally `r` (earliest-unique-commit), `e` (reply-to, for series/revisions), `t` (\"root\" or \"root-revision\" — mutually exclusive), `commit`, `parent-commit`, `commit-pgp-sig`, and `committer`."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "The 60KB bound and empty-content rejection are exercised by unit tests: git_patch_rejects_oversized_content asserts a 60*1024+1 byte patch returns SdkError::ContentTooLarge, and git_patch_rejects_empty_content/git_patch_rejects_whitespace_only_content assert empty and whitespace-only content are rejected before that check even runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "A patch cannot be marked both --root and --root-revision simultaneously; build_git_patch returns SdkError::InvalidInput if both are set, and this is covered by git_patch_rejects_root_and_root_revision_together."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "buzz_sdk::build_git_status constructs a kind:1630/1631/1632/1633 event (open/merged-resolved/closed/draft) tagging the root patch/issue/PR event as `[\"e\", root, \"\", \"root\"]`, optionally the accepted revision root as a `reply` e-tag, plus `p` recipients and an `a` repo-coordinate tag; the merged/resolved status additionally supports `q` tags (applied patch references, each `<id>[:<relay-url>[:<pubkey>]]`), a merge-commit id, and applied-as-commit ids -- and build_git_status returns SdkError::InvalidInput if any of those three are supplied on a non-merged status."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "The buzz-cli exposes this capability as `buzz patches send|get|list|status`: `send` builds and submits a kind:1617 patch from a `git format-patch` file or stdin; `get` fetches a single patch by event id; `list` queries kind:1617 events scoped to a repo's `a`-tag coordinate, optionally filtered by author; `status` builds and submits a kind:1630-1633 status event against a root patch/issue/PR, accepting `open`, `merged`/`resolved` (the CLI treats these as synonyms for the same underlying kind:1631), `closed`, or `draft`."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/patches.rs"
      - "crates/buzz-cli/src/lib.rs"
  - statement: "The relay's ingest authorization gate maps kind:1617 (patch) and every NIP-34 status/PR/issue kind to the MessagesWrite scope, the same scope regular stream messages require -- there is no dedicated git-patch scope."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:528-540"
  - statement: "kind:1617 (and every other NIP-34 git kind) is a global-only kind: the ingest pipeline always sets channel_id = NULL for it, because these events are scoped by their `a` tag (repo coordinate) rather than by NIP-29 `h` (channel) tags -- a stray `h` tag on a patch event is retained on the signed event but does not channel-scope it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:621"
  - statement: "A repository branch can carry a `require-patch` protection rule (parsed from a `buzz-protect` tag on the repo's kind:30617 announcement); when set, `evaluate_ref_update` denies every direct ref update to that ref -- create, fast-forward, non-fast-forward, and delete alike -- with the reason \"direct push denied: require-patch is set, submit a NIP-34 patch\", regardless of the pusher's role."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/git_perms.rs"
  - statement: "No relay code path applies a patch's diff to a repository or performs any automated merge; the only mechanism that changes a protected ref's contents is the existing git-receive-pack push flow (see architecture-flows-git-push), so accepting a patch is necessarily a manual maintainer action (apply it out-of-band, push the result) followed by a kind:1631 status event recording which commit(s) it became -- confirmed by an exhaustive search of crates/**/*.rs for `apply_patch`, `git am`, and `format-patch` finding no relay-side application logic, only the SDK/CLI's own `format-patch` doc comments."
    entry_class: FACT
    evidence:
      - "grep_recursive('apply_patch|git am|format-patch', path='crates/**/*.rs') -> only comment/doc references in buzz-core/src/kind.rs, buzz-sdk/src/builders.rs, buzz-cli/src/lib.rs; no relay-side application code, run against commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "VISION_PROJECTS.md frames patches as first-class, channel-native review objects -- \"Bug report to merged patch. One place\" -- and shows a worked example where a branch channel accumulates a kind:1617 patch, a revised kind:1617 patch v2, and eventual merge, treating `Patches (kind:1617)` as the artifact its illustrative review agent examines."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:5"
      - "VISION_PROJECTS.md:81"
      - "VISION_PROJECTS.md:88"
      - "VISION_PROJECTS.md:90"
      - "VISION_PROJECTS.md:216"
  - statement: "This capability is shipped, not merely designed: the event kinds, SDK builders, CLI subcommands, ingest authorization, and branch-protection enforcement described above are all present in mainline crate source at the recorded revision, with passing unit tests for the SDK builders' validation rules."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-sdk/src/builders.rs"
      - "crates/buzz-cli/src/commands/patches.rs"
      - "crates/buzz-core/src/git_perms.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
    confidence: 0.85
  - statement: "No dedicated end-to-end test exercises the full patch lifecycle (send a patch, apply require-patch, submit a status event) against a running relay; the only patch-adjacent reference in crates/buzz-test-client/tests/ is an unrelated mention inside conformance_multitenant.rs, and coverage otherwise consists of buzz-sdk's own unit tests for the builder functions."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "launchpad/docs/corpus/architecture/flows/git-push.md documents the smart-HTTP git-push flow, not the patch capability; it is a sibling/alternative contribution path (direct push through git-receive-pack) rather than an architecture node that realizes this capability, so this node does not declare a relationships edge to it."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/flows/git-push.md"
    confidence: 0.8
relationships:
  - type: part-of
    target: capabilities-git-git-hosting
---

# Patch submission: capability

Buzz lets a contributor propose a change to a git repository as a signed,
reviewable Nostr event — a **patch** (NIP-34 kind:1617, carrying the verbatim
output of `git format-patch`) — instead of requiring push access to the
repository. A patch is addressed to a specific repo (via its `a`-tag
coordinate to the repo's kind:30617 announcement) and to the repo owner (and
any additional recipients), can be chained into a series or a revision of a
series, and can carry the exact commit metadata (commit id, parent commit,
committer identity, PGP signature) needed to reconstruct the resulting
commit. A separate **status** event (kind:1630/1631/1632/1633 — open, applied/
merged, closed, draft) records what happened to a patch, a patch series, an
issue, or a pull request, including — for the merged case — which patch(es)
were applied, the resulting merge commit, and the commit ids the change
became. A repository owner can additionally require this path: a
`require-patch` branch-protection rule on a ref blocks every direct push to
it, so the only way to change that ref's contents is a maintainer applying an
accepted patch out-of-band.

## Maturity

**Shipped.** kind:1617 and the surrounding NIP-34 kinds are defined in
`crates/buzz-core/src/kind.rs`. `buzz_sdk::build_git_patch` and
`buzz_sdk::build_git_status` construct and validate these events (size
bounds, mutually-exclusive flags, hex/id validation), each covered by passing
unit tests in `crates/buzz-sdk/src/builders.rs`. `buzz patches send|get|list|status`
in `crates/buzz-cli` exposes the full lifecycle to a human or agent caller.
The relay authorizes kind:1617 and the status/PR/issue kinds under the
`MessagesWrite` scope and stores them as global (repo-scoped, not
channel-scoped) events (`crates/buzz-relay/src/handlers/ingest.rs`). The
`require-patch` branch-protection rule is enforced server-side in
`crates/buzz-core/src/git_perms.rs`'s `evaluate_ref_update`, unconditionally
blocking direct ref updates — create, fast-forward, non-fast-forward, and
delete alike — on a protected ref regardless of the caller's role.

**What is not automated.** No relay code path applies a patch's diff to a
repository. Accepting a patch is a manual maintainer action: apply it
out-of-band (e.g. `git am`) and push the result through the ordinary
git-receive-pack flow, then publish a kind:1631 status event recording the
outcome. This was confirmed by searching the codebase for patch-application
logic (`apply_patch`, `git am`, `format-patch`) and finding only documentation
comments in the SDK and CLI, no execution path. `require-patch` therefore
governs *who may change the ref directly*, not an automated patch-application
pipeline.

## Boundary

This node does not describe:
- how git hosting itself is built — the smart-HTTP transport, hook, and
  object-store mechanics that a patch is eventually applied through belong to
  the push flow, not this capability (see
  `launchpad/docs/corpus/architecture/flows/git-push.md`; no `references` edge
  is declared here because that node documents a sibling/alternative
  contribution path, not this capability's own realization).
- the CLI's full command-line surface as its own interface contract (flags,
  exit codes, output shapes) — that belongs to an interface node once one
  exists for `buzz-cli` (`#1342`'s template family), not yet present in the
  corpus.
- the step-by-step sequence a patch goes through from submission to merge —
  that is a flow node's territory (comparable to `architecture-flows-git-push`
  but for patches), not drafted in this batch.
- how the running relay is operated, deployed, or monitored — the
  `operations` corpus surface, unrelated to what this capability lets a user
  do.

## Relationships

None declared. No architecture, interface, or capability node presently
merged on `origin/launchpad` realizes or exposes this specific capability:
`architecture-flows-git-push` documents the alternative direct-push path, not
this one, and no interface node exists yet for `buzz-cli` or the relay's
NIP-34 event surface. The first patch-flow or CLI-interface node to merge is
the right moment to add a `references` edge back here.

## Scope and omissions

**This node covers** what the patch-submission capability lets a user or
agent do: submitting a patch as a signed Nostr event, chaining patches into
series/revisions, recording status (open/merged/closed/draft) including which
patches were applied and to what commit, the `require-patch` enforcement that
can make this the only path to change a ref, and the CLI surface that exposes
all of it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How git hosting (push, hooks, object storage) is built | `launchpad/docs/corpus/architecture/flows/git-push.md` |
| The `buzz-cli` interface contract itself | an interface node (`#1342` template family), not yet drafted |
| The step-by-step flow from patch submission to merge | a flow node, not yet drafted |
| How the running relay is operated | the `operations` corpus surface |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**
- **No running-relay verification was performed.** Every claim above is
  grounded in source code and unit tests read directly; no live relay was
  started to submit a patch, apply `require-patch`, or publish a status event
  end-to-end, because no such end-to-end test exists in
  `crates/buzz-test-client/tests/` to run.
- **Whether any downstream tooling (e.g. gitworkshop.dev-style clients,
  ngit-cli) currently interoperates with Buzz's specific patch event shape**
  was not checked — this node describes what Buzz's own code emits and
  enforces, not interop with the wider NIP-34 ecosystem.
