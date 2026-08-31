---
id: capabilities-git-repository-browser
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
  - statement: "The `web/` browser client browses a repo entirely client-side: it shallow-clones the repo into an IndexedDB-backed virtual filesystem via isomorphic-git, then reads the tree, blobs, log and README from that local clone rather than from any relay JSON/REST endpoint."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/git-client.ts"
      - "web/src/features/repos/use-git-browse.ts"
  - statement: "Three routes implement the browsing surface: `/repos` (repo list), `/repos/$repoId` (repo detail — tabs, tree, README, refs, clone URLs), and `/repos/$repoId/blob/$` (single-file viewer)."
    entry_class: FACT
    evidence:
      - "web/src/app/routes.ts"
  - statement: "`RepoDetailPage` renders a Code/Commits tab bar over `RepoTreeSection` (file tree) and `RepoReadmeSection` (rendered README) for Code, and `RepoCommitsSection` (recent commit log) for Commits, alongside a `RepoRefsSection` (branches/tags/HEAD) and a list of clone URLs, all above the fold on the same page."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/ui/RepoDetailPage.tsx"
  - statement: "The relay's git smart-HTTP surface the client clones/fetches against exposes exactly `GET /git/{owner}/{repo}/info/refs`, `POST /git/{owner}/{repo}/git-upload-pack`, and `POST /git/{owner}/{repo}/git-receive-pack`, per that module's own doc comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:4-6"
  - statement: "`ensureClone` — the sole entry point every browsing hook depends on — only ever calls isomorphic-git's `clone` or `fetch`; the web client's `git-client.ts` never calls `git-receive-pack` or otherwise writes to a repo, making this capability, as implemented in `web/`, read-only browsing rather than a push/write surface."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/git-client.ts:68-116"
  - statement: "Every git HTTP request the browser makes carries a NIP-98 signed `Authorization: Nostr <event>` header built fresh per request from the caller's Nostr key, matching the authentication scheme `architecture-flows-git-push` documents for the write path."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/git-client.ts:43-62"
  - statement: "Server-side, `authorize_git_read` gates every git read behind the repo's `buzz-channel` binding and the caller's resolved channel-membership role, fails closed on a missing/deleted announcement, an invalid owner, a missing or malformed binding, a non-member, or any database error, and deliberately grants the repo's own announcing owner no bypass — an owner removed from the bound channel loses read access exactly like anyone else."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:450-474"
  - statement: "Every denial from the read gate returns the same generic 404 (\"repository not found\") as a nonexistent repo, with one narrow carve-out: a never-bound repo's own announcing author gets a 404 whose body explains how to bind it, since only that author can rebind a `d`-tag-keyed kind:30617 announcement; a broken (ambiguous) binding stays generic even for the author."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:461-524"
  - statement: "Repo metadata and ref state are read over the relay's Nostr WebSocket rather than any HTTP REST endpoint: repo listing/detail comes from kind:30617 announcement events and branch/tag/HEAD state from kind:30618 ref-state events, the same two kinds `architecture-flows-git-push` documents on the write side."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/use-repos.ts"
      - "web/src/features/repos/use-repo-refs.ts"
  - statement: "A blob is classified before rendering: raster images (`png`/`jpg`/`jpeg`/`gif`/`webp`/`avif`, by extension) preview inline up to a 10 MiB cap; anything else is checked for a NUL byte in its first 512 bytes to detect binary; surviving text is capped at 1 MiB for inline preview; anything over either cap renders as `too-large` with a download fallback instead of being fetched again — the underlying IndexedDB clone always holds the full bytes regardless of the display cap."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/git-client.ts:166-288"
  - statement: "SVG is deliberately excluded from the raster-image path and rendered through the text path instead, because an SVG can carry active content that an `<img>` tag would execute in some contexts."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/git-client.ts:178-189"
  - statement: "Markdown files render through `react-markdown` with the `remark-gfm` plugin; every other text file renders as plain monospace text inside a `<pre>` with no syntax highlighter."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/ui/RepoBlobViewer.tsx:112-121"
      - "web/src/features/repos/ui/RepoBlobViewer.tsx:182-187"
  - statement: "An HTML file is shown as source by default; an explicit \"Run\" action inlines same-repo relative script/link/image references as `data:` URLs and renders the result inside an iframe sandboxed with `allow-scripts` only — `allow-same-origin` is deliberately never added, so a pushed HTML file's script cannot read the parent page's cookies, IndexedDB, localStorage, relay session, or NIP-98 auth even though it renders on the same document origin."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/ui/RepoBlobViewer.tsx:145-168"
      - "web/src/features/repos/git-client.ts:291-396"
  - statement: "Directory drill-down is not implemented: a tree entry of type `\"tree\"` renders as a non-clickable row (`aria-disabled=\"true\"`) rather than a link, so the browser currently only lists a single directory level (the ref's root) per page rather than letting a reader navigate into subfolders."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/ui/RepoTreeSection.tsx:14-26"
  - statement: "A development-only `?preview=repositories` query flag swaps every hook's data for fixtures from `mock-repos.ts`, bypassing the relay entirely; it is gated by `import.meta.env.DEV` and is not reachable in a production build."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/mock-repos.ts"
      - "web/src/features/repos/ui/RepoDetailPage.tsx:188-191"
  - statement: "The only automated test coverage of this capability's UI is `web/tests/e2e/smoke.spec.ts`, which asserts the home page shows the text \"Repositories\"; no Playwright or unit test exercises the tree, blob viewer, commit list, or README rendering paths."
    entry_class: FACT
    evidence:
      - "web/tests/e2e/smoke.spec.ts:10-14"
  - statement: "The routes, components and hooks implementing this capability are wired into the app's live route tree and call the relay's production git-smart-HTTP and Nostr-event surfaces directly, with no feature flag gating them beyond the dev-only mock-preview toggle — the capability is shipped, not designed-but-unbuilt or behind an experiment flag."
    entry_class: FACT
    evidence:
      - "web/src/app/routes.ts"
      - "web/src/features/repos/ui/RepoDetailPage.tsx"
      - "web/src/features/repos/git-client.ts"
  - statement: "VISION_PROJECTS.md's own Status table marks \"Git hosting (smart HTTP + NIP-34)\" as \"Ships today\", the broader capability this browsing UI is one surface of."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:256"
---

# Repository browser: capability

Buzz lets a member read a repository announced on the relay from an ordinary
browser tab, with no git client or CLI installed: browse the file tree and
README at the repo's default branch, open and preview an individual file, and
review recent commit history and the repo's branches/tags/HEAD — all gated by
the same channel membership that governs the repo's `git push` side.

## Maturity

**Shipped.** `/repos`, `/repos/$repoId` and `/repos/$repoId/blob/$` are live
routes in the web app's route tree, backed by components (`RepoDetailPage`,
`RepoTreeSection`, `RepoBlobViewer`, `RepoCommitsSection`, `RepoReadmeSection`,
`RepoRefsSection`) that call the relay's real git-smart-HTTP and Nostr-event
surfaces — not a stub or an experiment flag. The only conditional bypass is a
`DEV`-only `?preview=repositories` mock mode, unreachable in a production
build. VISION_PROJECTS.md's Status table separately marks the broader "Git
hosting (smart HTTP + NIP-34)" capability this browsing UI is one surface of
as "Ships today."

One concrete limitation is part of today's shipped shape rather than a
maturity gap: sub-directory navigation is not implemented. A folder in the
tree view renders as a disabled row, so a reader currently sees only the
repo's root tree per page, not an arbitrary path into it.

## Boundary

This node does not describe:
- **How it is built** — the client-side isomorphic-git/IndexedDB clone
  mechanics, the relay's git-smart-HTTP transport, and the read-authorization
  gate's implementation live in `web/src/features/repos/git-client.ts` and
  `crates/buzz-relay/src/api/git/transport.rs`; the container that hosts the
  web client is `architecture-containers-web`. This node cites those as
  evidence of the capability's existence and behavior, not as its own subject.
- **The interface it is exposed through** — the git-smart-HTTP route group
  (`info/refs`, `git-upload-pack`, `git-receive-pack`) and the Nostr event
  kinds (30617, 30618) it reads are a protocol surface; no dedicated interface
  node for that surface exists yet in the corpus at this revision.
- **The step-by-step flow through it** — no flow node narrating the
  clone-then-render sequence a browsing session takes exists yet; the closest
  documented flow, `architecture-flows-git-push`, covers the write
  (`git push`) side of the same repo, sharing only the NIP-98 authentication
  scheme and the repo/tenant resolution with this capability.
- **How it is operated** — deployment, monitoring, or incident response for
  the relay's git surface is a separate, undocumented concern at this
  revision.
- **Write access** — as implemented in `web/`, this capability is read-only;
  pushing to a repo is a distinct capability exercised through the CLI or
  desktop client, gated by the pre-receive hook and policy endpoint
  `architecture-flows-git-push` documents, not by anything in `web/`.

## Relationships

- references: architecture-containers-web
- references: architecture-flows-git-push

## Scope and omissions

**This node covers** what the repository-browser capability lets a member do
(browse a repo's tree, README, an individual file's contents, and its commit
and ref history from an ordinary browser tab), its current maturity and one
concrete built-in limitation (no directory drill-down), the read-only
boundary against the write/push capability, the file-classification and
preview-cap rules the blob viewer applies, the sandboxing rule the HTML
"Run" feature depends on for safety, and the read-authorization gate's
fail-closed shape as observed from the relay side.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the capability is built (isomorphic-git/IndexedDB client, relay git-smart-HTTP transport, read-authorization gate internals) | `architecture-containers-web`; `crates/buzz-relay/src/api/git/transport.rs` |
| The protocol/interface surface it is exposed through (git-smart-HTTP routes, kind:30617/30618) | No interface node exists yet for this surface |
| The step-by-step flow a browsing session takes | No flow node exists yet for this capability; `architecture-flows-git-push` covers only the write side |
| How the relay's git surface is operated | Not documented at this revision |
| The write/push capability (`git push`, pre-receive hook, policy gate) | `architecture-flows-git-push` |

**Expected but not verified when this node was written:**

- **No automated test exercises the browsing UI's actual behavior.** The only
  test found, `web/tests/e2e/smoke.spec.ts`, checks that the home page shows
  the text "Repositories" and does not open a repo, a file, or the commit
  list. Every behavioral claim about the tree, blob viewer, README rendering,
  or commit list above is sourced from reading the component and hook code,
  not from an executed test asserting it.
- **The relay-side read-authorization gate (`authorize_git_read`) was read,
  not exercised.** Its fail-closed behavior is described from the function
  body and its own doc comment, not from a passing integration test observed
  in this task.
- **Whether any other automated coverage exists outside `web/` and
  `crates/buzz-relay/src/api/git/` for this specific browsing surface** (for
  example a desktop-side equivalent) was not searched for; this node's claims
  are scoped to what `web/` and the relay's git-read gate do.
