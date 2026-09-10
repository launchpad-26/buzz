# Issue #1290 — document platforms/web/repository-browser

## ALREADY TRUE

- Repository revision: `22078443c0988e9e4149a9856195ac1f4599c96b` (origin/launchpad
  tip at worktree creation).
- `launchpad/docs/corpus/platforms/` does not exist yet on `origin/launchpad` —
  this is the first node under that prefix. No `type: platforms` node exists to
  copy conventions from directly; per the batch orchestrator's note, sibling
  in-flight tasks in this Feature have settled on `type: platforms` for
  `platforms/**` documents, borrowing `component.md`'s section shape (purpose,
  responsibility/interface, dependencies, boundary, relationships, scope and
  omissions) since no platforms-specific template exists.
- The container-level node `architecture-containers-web`
  (`launchpad/docs/corpus/architecture/containers/web.md`, `status: draft`,
  merged on `origin/launchpad`) already documents the whole `web` container:
  both its features (invite landing and git repository browser) at a high
  level, its inbound/outbound interfaces, deployment/data/security
  implications. It does **not** go component-level on the repository browser's
  own internal structure (routes, hooks, UI components, blob-classification
  rules, sandboxing model) — that is this task's job. This new node will
  `references` that container node rather than duplicate its content.
- No existing corpus node documents `web/src/features/repos/**` at
  component/feature level (confirmed by grepping the corpus tree for
  "repository-browser", "RepositoryBrowser", "repo-browser" — the only hits
  are the two prose mentions inside `architecture/containers/web.md`).
- `launchpad/docs/corpus/platforms/web/repository-browser.md` does not exist.

## STEP 1 — Confirm scope and gather routes/hooks evidence

Read `web/src/app/routes/{index,repos,repos.$repoId,repos.$repoId.blob.$}.tsx`
and `web/src/features/repos/{use-repos,use-repo-refs,use-repo-context,
use-git-browse,git-client}.ts`. Confirm: repo discovery is NIP-34 kind:30617
(`crates/buzz-core/src/kind.rs:605`), refs/HEAD via kind:30618
(`crates/buzz-core/src/kind.rs:607`), and that `/repos` is a redirect to `/`
(the real listing route), not a duplicate page.

**Done when:** every route file and every hook file has been opened and its
real behavior (not assumed behavior) is recorded as a citable claim.

## STEP 2 — Gather UI-component and security evidence

Read `RepoDetailPage.tsx`, `RepoBlobViewer.tsx`, `RepoTreeSection.tsx`,
`RepoCommitsSection.tsx`, `RepoRefsSection.tsx`, `ReposPage.tsx`. Record the
blob-classification caps (`TEXT_PREVIEW_LIMIT_BYTES`,
`IMAGE_PREVIEW_LIMIT_BYTES`), the deliberate SVG-as-text exclusion, the
sandboxed-iframe `allow-scripts`-only (no `allow-same-origin`) HTML "Run"
path, and the known limitation that sub-tree (nested folder) navigation is
deferred — `RepoTreeSection.tsx` renders folders as non-clickable
(`aria-disabled="true"`) by design, not a bug.

**Done when:** every substantive UI claim has a real file:line citation, and
the deferred-subtree-navigation limitation is captured for the Boundary /
Scope-and-omissions sections rather than silently omitted.

## STEP 3 — Draft the node

Write `launchpad/docs/corpus/platforms/web/repository-browser.md` with
`id: platforms-web-repository-browser`, `type: platforms`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, reviewer]`. Body follows
`component.md`'s shape: purpose/scope, responsibility, public
interface/routes table, dependencies (isomorphic-git, lightning-fs,
react-markdown, remark-gfm, NIP-98 auth), boundary (not the container node,
not the git smart-HTTP server side, not admin-web), relationships
(`references: architecture-containers-web` — confirmed present on
`origin/launchpad`), scope and omissions (nested-directory browsing, HEAD-sha
spoofing TODO, no line numbers in text view).

**Done when:** every DoD bullet in issue #1290 is satisfied and every evidence
entry cites a file actually opened in Steps 1–2.

## STEP 4 — Validate: no new FAILs

Run `python3 launchpad/project-intelligence/corpus/validate.py`, note the
pre-existing FAIL set, then temporarily move the new file out, re-run, confirm
the FAIL set is identical, and restore the file.

**Done when:** the new file contributes zero new FAIL lines.

## STEP 5 — Earn the commit gate and verify

Run the corpus unittest suite as its own sole Bash call, then stage + commit
(`git commit -s`) as a second, separate call. Re-read the diff against the
DoD checklist and re-open every cited file/line once more before reporting.

**Done when:** the commit exists locally with a real SHA, or the two-call
gate has been retried exactly once and still refused (BLOCKED per the
orchestrator's finding #7).

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` — zero new FAILs.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` — `OK`, as the sole content of its own Bash call.
- Every evidence citation opened and read, not guessed.
- `references: architecture-containers-web` resolves against `origin/launchpad`.

## OPEN

- Whether a future `platforms` template will reshape this node's section
  order — none exists yet, so this node is built against `component.md`'s
  shape per the batch's settled (but not yet schema-enforced) convention.

## LEFT OUT

- Documenting the git smart-HTTP server side (`crates/buzz-relay`'s
  `git_router`) — owned by the container node and by any future
  implementation-reference node for that crate.
- Documenting `admin-web` — a separate, undocumented bundle.
- Re-deriving the whole `web` container's deployment/security posture —
  already covered by `architecture-containers-web`, referenced rather than
  restated.
