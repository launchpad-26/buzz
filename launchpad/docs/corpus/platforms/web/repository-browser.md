---
id: platforms-web-repository-browser
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 22078443c0988e9e4149a9856195ac1f4599c96b."
    entry_class: FACT
    evidence:
      - "commit 22078443c0988e9e4149a9856195ac1f4599c96b"
  - statement: "The repository browser is one of two feature areas in the web/ container (the other is invite/); it lives under web/src/features/repos/ and is routed by TanStack Router file routes: `/` renders the repository list, `/repos` redirects to `/`, `/repos/$repoId` renders the repo detail page, and `/repos/$repoId/blob/$` renders a single file's blob viewer."
    entry_class: FACT
    evidence:
      - "web/src/app/routes/index.tsx"
      - "web/src/app/routes/repos.tsx"
      - "web/src/app/routes/repos.$repoId.tsx"
      - "web/src/app/routes/repos.$repoId.blob.$.tsx"
  - statement: "Repositories are discovered by querying kind:30617 (NIP-34 repository announcement, parameterized replaceable with the repo id as its d-tag) over the relay's Nostr WebSocket, deduplicated by (pubkey, kind, d-tag) keeping the most recent created_at, then mapped into a Repo object reading its name/description/clone/web/buzz-channel/p tags."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/use-repos.ts"
      - "crates/buzz-core/src/kind.rs:605"
  - statement: "Branches, tags and HEAD are discovered by querying kind:30618 (NIP-34 repository state) filtered to `#d: [repoId]`, parsing `refs/heads/*` and `refs/tags/*` tags, and resolving HEAD's SHA by matching its `ref: refs/heads/<name>` value against a `refs/heads/<name>` tag on the same or a later event."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/use-repo-refs.ts"
      - "crates/buzz-core/src/kind.rs:607"
  - statement: "A code comment in use-repo-refs.ts records an unresolved gap: refs are not filtered by the relay's own pubkey (authors), so a user holding ReposWrite permission could publish a spoofed kind:30618 event with fake branch/tag/HEAD data; the TODO says this will be fixed once the relay's own pubkey is exposed client-side."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/use-repo-refs.ts"
  - statement: "Once a repo's owner, name and a ref are known, use-git-browse.ts's useGitClone hook (backed by git-client.ts's ensureClone) performs a shallow (depth:1, singleBranch, noTags), IndexedDB-persisted clone via isomorphic-git, authenticating each request with a NIP-98 (kind:27235) Authorization header built from the exact clone URL `{relay}/git/<owner>/<repo>.git`; if a local clone already exists it fetches instead of re-cloning."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/use-git-browse.ts"
      - "web/src/features/repos/git-client.ts"
  - statement: "The relay-side git smart-HTTP transport this clone/fetch traffic terminates at is buzz-relay's own git_router, merged into the relay's HTTP router in crates/buzz-relay/src/router.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:49"
      - "crates/buzz-relay/src/router.rs:149"
  - statement: "Once cloned, three read-only git operations are exposed as React Query hooks: useGitTree (readTree, sorted directories-first then alphabetical), useGitLog (log, default depth 20), and useGitReadme (a case-insensitive search of the root tree for readme.md / readme / readme.rst / readme.txt, reading the first non-binary match)."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/use-git-browse.ts"
      - "web/src/features/repos/git-client.ts"
  - statement: "RepoTreeSection.tsx renders directory (tree) entries as visibly non-clickable (aria-disabled=\"true\"), with a code comment stating sub-tree navigation is deliberately deferred; only files at the root of the tree passed in are linkable to the blob viewer. This is a known, intentional scope limit, not a bug."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/ui/RepoTreeSection.tsx"
  - statement: "A single file's content is fetched via useGitBlob, which resolves the ref to an oid then calls readBlobView to classify the raw bytes into a BlobView discriminated union: image (by extension: png/jpg/jpeg/gif/webp/avif, capped at IMAGE_PREVIEW_LIMIT_BYTES = 10 MiB before falling back to too-large), binary (detected by a NUL byte in the first 512 bytes, no size cap, always offers download), markdown/html (by extension, decoded as UTF-8), or text (default UTF-8 decode), each below TEXT_PREVIEW_LIMIT_BYTES = 1 MiB before falling back to too-large. SVG is excluded from the image path by deliberate design (a code comment states SVG can carry active content) and is rendered via the text path instead."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/git-client.ts"
  - statement: "RepoBlobViewer.tsx's ViewerBody renders each BlobView kind with a matching UI: TextView (a <pre> block, no line numbers — a code comment states line numbers were deferred for v1), a Markdown component (react-markdown with remark-gfm) for markdown, ImageView (an <img> over a locally created and revoked object URL) for image, a download-only notice for binary and too-large, and either the raw source (TextView) or, once the user clicks Run, a rendered result for html."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/ui/RepoBlobViewer.tsx"
  - statement: "The html 'Run' path (useGitHtmlDoc / resolveHtmlAssets) inlines the HTML file's same-repo-relative <script src>, <link href> and <img src> targets as base64 data: URLs (walking `..`/`.` segments but refusing to escape the repo root), leaving absolute paths, protocol URLs, protocol-relative refs and fragments untouched, then renders the fully self-contained result inside a sandboxed <iframe> whose sandbox attribute is exactly \"allow-scripts\" — allow-same-origin is deliberately absent, per an inline security comment, so the frame's JS runs at an opaque null origin and cannot read the parent page's cookies, IndexedDB, localStorage, relay session or NIP-98 auth."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/git-client.ts"
      - "web/src/features/repos/ui/RepoBlobViewer.tsx"
  - statement: "RepoCommitsSection.tsx and RepoRefsSection.tsx are read-only presentational components: the former lists CommitInfo rows (message first line, author, relative time, short oid) from useGitLog with no interaction beyond scroll, and the latter renders HEAD/branch-count/tag-count badges from useRepoRefs with no interaction at all."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/ui/RepoCommitsSection.tsx"
      - "web/src/features/repos/ui/RepoRefsSection.tsx"
  - statement: "ReposPage.tsx (mounted at the site root, `/`) is the repository list/search/sort landing page, built from useRepos (the same kind:30617 query as use-repos.ts's fetchRepos), a text search input, a sort order (newest/oldest/name), and dedicated empty states for 'no matching repositories' (search yielded nothing) versus 'this community is empty' (no repos exist at all)."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/ui/ReposPage.tsx"
  - statement: "package.json names the exact browser-git dependency set this feature relies on: isomorphic-git ^1.38.3 (git operations), @isomorphic-git/lightning-fs ^4.6.2 (IndexedDB-backed virtual filesystem), react-markdown ^10.1.0 and remark-gfm ^4.0.1 (markdown rendering with GitHub-flavored-markdown extensions)."
    entry_class: FACT
    evidence:
      - "web/package.json"
  - statement: "Each repo's clone is persisted client-side under a per-repository IndexedDB database named `buzz-git-<owner>-<repoName>` (LightningFS's own scoping), so cloned objects and browsing state are local to one browser profile and not shared across repos or synchronized anywhere; this same fact is already recorded at container level in architecture-containers-web's Data implications section, restated here only as the concrete evidence this component-level node is built on, not as a new claim."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/git-client.ts"
  - statement: "The container-level node architecture-containers-web already documents the web container's responsibility (including both invite and repository-browser feature areas at a summary level), its inbound/outbound interfaces, and its deployment/data/security implications, including the relay-side BUZZ_SERVE_GIT_WEB_GUI gate that must be enabled for the /repos routes to be served at all."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/web.md"
  - statement: "At the recorded revision, architecture-containers-web is present in the corpus tree checked out from origin/launchpad, so a references relationship from this node toward it resolves."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/architecture/containers/web.md') -> present, at commit 22078443c0988e9e4149a9856195ac1f4599c96b"
  - statement: "No other corpus node on origin/launchpad documents web/src/features/repos/ at component or feature level; the only prior corpus mentions of 'repository-browser' are two prose references inside architecture-containers-web describing the relay-side serving gate, not this feature's internal structure."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='repository-browser', scope='launchpad/docs/corpus/**') -> 2 matches, both in launchpad/docs/corpus/architecture/containers/web.md, at commit 22078443c0988e9e4149a9856195ac1f4599c96b"
  - statement: "No platforms-specific corpus template exists yet, and no other type: platforms node is merged on origin/launchpad at the recorded revision; this node's body shape borrows component.md's section structure (purpose, responsibility, public interface, dependencies, boundary, relationships, scope and omissions) as the closest existing fit for a single feature-area's standalone documentation, per this Feature's own settled (not yet schema-enforced) convention for platforms/** documents."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/component.md"
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no platforms/ prefix present at commit 22078443c0988e9e4149a9856195ac1f4599c96b"
    confidence: 0.65
relationships:
  - type: references
    target: architecture-containers-web
---

# Web repository browser

The client-side, read-only Git repository browser inside the `web` container:
list, clone-and-browse, and view files/commits/refs for repositories hosted
via the relay's git smart-HTTP transport, entirely in the browser. This node
documents that feature area (`web/src/features/repos/`) at component level —
its routes, data flow, blob-classification rules, and the security boundary
around its one active-content path (HTML "Run"). It does not restate the
`web` container's own responsibility, technology stack, or deployment
posture — see *Boundary* below.

## Responsibility

Give a user a way to discover, browse, and read Git repositories the relay
hosts, without installing the desktop or mobile app and without exposing a
long-lived credential: every authenticated request signs a fresh NIP-98 event
with the user's own Nostr key. The feature is read-only — there is no
in-browser edit, commit, or push path.

## Public interface

| Route / hook | Kind | Contract | Evidence |
|---|---|---|---|
| `/` | route | Renders `ReposPage` — repository list, search, sort, empty states | `web/src/app/routes/index.tsx` |
| `/repos` | route | Redirects to `/` (not a second listing page) | `web/src/app/routes/repos.tsx` |
| `/repos/$repoId` | route | Renders `RepoDetailPage` — header, refs, code/commits tabs, clone URLs | `web/src/app/routes/repos.$repoId.tsx` |
| `/repos/$repoId/blob/$` | route | Renders `RepoBlobPage` — single file viewer | `web/src/app/routes/repos.$repoId.blob.$.tsx` |
| `useRepos` / `useRepo` | hook | Query kind:30617 repo announcements, dedup by (pubkey,kind,d-tag) | `web/src/features/repos/use-repos.ts` |
| `useRepoRefs` | hook | Query kind:30618 repo state, parse branches/tags/HEAD | `web/src/features/repos/use-repo-refs.ts` |
| `useRepoContext` | hook | Resolve `(owner, repoName, defaultRef)` for a repo id | `web/src/features/repos/use-repo-context.ts` |
| `useGitClone` | hook | Shallow clone/fetch into IndexedDB via isomorphic-git, NIP-98 auth | `web/src/features/repos/use-git-browse.ts`, `git-client.ts` |
| `useGitTree` / `useGitLog` / `useGitReadme` / `useGitBlob` / `useGitHtmlDoc` | hook | Read-only tree/log/readme/blob/HTML-asset-inlining queries over the clone | `web/src/features/repos/use-git-browse.ts` |

## Dependencies

**Depends on** (this feature requires these to run):

| Component | Why | Evidence |
|---|---|---|
| `isomorphic-git` (^1.38.3) | In-browser clone/fetch/log/readTree/readBlob | `web/package.json` |
| `@isomorphic-git/lightning-fs` (^4.6.2) | IndexedDB-backed virtual filesystem for the clone | `web/package.json` |
| `react-markdown` (^10.1.0) + `remark-gfm` (^4.0.1) | Markdown rendering with GFM extensions | `web/package.json` |
| Relay git smart-HTTP transport (`git_router`) | Serves the clone/fetch traffic this feature issues | `crates/buzz-relay/src/router.rs:49`, `:149` |
| `web/src/shared/lib/nip98.ts`, `relay-url.ts` | Builds the NIP-98 auth header and derives the relay base URL | `web/src/features/repos/git-client.ts` |

**Depended on by:** no other component in this repository requires this
feature to build or run; it is a leaf feature area within the `web`
container. (Checked: no other crate or package manifest names
`web/src/features/repos` as a dependency — there is no manifest mechanism by
which one could.)

## Boundary

This node does not describe:
- the `web` container's overall responsibility, technology stack, ownership
  boundary, or deployment/security posture as a whole — see
  `architecture-containers-web`, which this node `references`.
- the relay-side git smart-HTTP server implementation (`git_router`,
  `crates/buzz-relay`) — only that it is this feature's counterparty.
- the `invite/` feature area (the `web` container's other feature) or the
  separate `admin-web` bundle.
- write operations (commit, push, branch creation) — none exist in this
  feature; it is read-only by construction.

## Relationships

- references: architecture-containers-web

## Scope and omissions

**This node covers** the repository browser's routes, its NIP-34-based repo
and refs discovery, its clone/fetch flow over isomorphic-git with NIP-98
auth, its read-only tree/log/readme/blob operations, its blob-classification
and preview-size rules, and the sandboxing model behind its one
active-content ("Run" HTML) path.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `web` container as a whole (technology, deployment, security posture) | `architecture-containers-web` |
| The relay's git smart-HTTP transport implementation | Not yet documented in this corpus |
| NIP-34, NIP-98 as protocols in their own right | The Nostr NIPs themselves (https://github.com/nostr-protocol/nips) |
| The `invite/` feature area and `admin-web` bundle | Not yet documented in this corpus |

**Expected but not verified when this node was written:**

- **Nested-directory browsing is a known, deliberate scope limit, not
  verified against any tracking issue.** `RepoTreeSection.tsx` renders
  sub-directories as non-navigable by design; whether a follow-up issue
  exists to add drill-down navigation was not searched for.
- **The unresolved HEAD/ref-spoofing gap** (kind:30618 events not filtered to
  the relay's own pubkey) is recorded here as a fact about the code today,
  not evaluated for severity or checked against any tracking issue.
- **Whether any e2e test exercises the repository-browser routes beyond the
  home page's repositories section was not exhaustively checked** — only
  `web/tests/e2e/smoke.spec.ts`'s "home page shows repositories section" test
  was found by name; this node does not claim comprehensive E2E coverage.
