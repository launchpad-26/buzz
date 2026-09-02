# Plan: issue #1289 — document platforms/web/relay-serving.md

## ALREADY TRUE

- Issue #1289 read (`gh issue view 1289`). Its DoD requires one hand-authored
  node at `launchpad/docs/corpus/platforms/web/relay-serving.md`, schema-valid
  front matter, evidence-cited claims, responsibility/interface/boundary,
  named dependencies/collaborators, links to source and tests, and
  component-level scope only (not the whole `web` platform).
- `launchpad/docs/corpus/architecture/containers/web.md`
  (`id: architecture-containers-web`, `type: architecture`, `status: draft`)
  already exists on `origin/launchpad` and documents the `web` container in
  full, including the exact relay-serving mechanism (`BUZZ_WEB_DIR`,
  `ServeDir` fallback, `should_serve_spa`, CORS ordering, Dockerfile/Justfile
  wiring). Per known finding #5, this task must not re-derive that content —
  it references that node instead of duplicating it.
- No `platforms/` directory and no `type: platforms` node exists yet on this
  branch or `origin/launchpad` (`grep -rl "type: platforms"` finds only enum
  mentions inside unrelated templates). Per known finding #4, `type: platforms`
  plus `component.md`'s section shape (responsibility / public interface /
  dependencies / boundary / relationships / scope-and-omissions) is the
  Feature-wide convention to follow, since no platforms-specific template
  exists yet.
- Sibling web-platform tasks in the same Feature: #1286 (application), #1287
  (authentication), #1288 (invite-ui), #1290 (repository-browser). None are
  merged yet (no PRs found for `platforms/web`), so no sibling `id` exists to
  `references` or be referenced by.
- Verified directly against the actual worktree files (not from `web.md`'s
  own claims, per known finding #6):
  - `crates/buzz-relay/src/config.rs` lines 1173–1191: `BUZZ_WEB_DIR` parsed,
    validated to contain `index.html`, logged; `BUZZ_SERVE_GIT_WEB_GUI`
    parsed as `"true"`/`"1"`, defaulting to `false`.
  - `crates/buzz-relay/src/router.rs` lines 145–207: the merged router's
    fallback service — admin host checked first (`is_admin_host`), then for
    the public bundle: `/assets/*` served via `ServeDir`, `should_serve_spa`
    gates SPA `index.html` fallback, else 404; CORS/metrics/trace layered
    over the whole merged router afterward.
  - `router.rs` lines 238–249: `is_invite_landing_path`, `is_git_web_gui_path`,
    `should_serve_spa` — the exact gating logic.
  - `router.rs` lines 304–389: `nip11_or_ws_handler` — the root path (`/`) is
    an explicit relay route, never reaching the SPA fallback; it serves
    `index.html` only when `serve_git_web_gui` is set and the client accepts
    `text/html` and no WebSocket upgrade occurred, else NIP-11 JSON.
  - `Dockerfile` lines 153, 159: `web/dist` copied to `/srv/buzz/web`,
    `ENV BUZZ_WEB_DIR=/srv/buzz/web` set by default in the shipped image.
  - `Justfile` lines 475–484: `relay-web` builds `web/dist` then runs
    `buzz-relay` with `BUZZ_WEB_DIR=./web/dist` in the same shell — no
    separate web server process.
  - Tests: `router.rs` `should_serve_spa`-family unit tests (lines 522–550);
    integration test `the_public_spa_is_untouched_by_the_admin_csp` (line
    677) exercising the public bundle's SPA/asset serving through
    `build_router` end-to-end; `config.rs` `defaults_are_valid` (line 1338)
    asserting `serve_git_web_gui` defaults to `false`.
- Current HEAD: `22078443c0988e9e4149a9856195ac1f4599c96b`.

## STEP 1 — Write front matter

`id: platforms-web-relay-serving`, `type: platforms`, `status: draft`,
`origin: launchpad`, `audiences: [developer, agent, operator]`. Evidence
ledger: one commit-citation FACT for provenance, FACT entries per verified
code/config/test/Dockerfile/Justfile claim above (each cited to the real
file, several with line numbers), one INFERENCE about why this node does not
restate `architecture-containers-web`'s content. `relationships: [{type:
references, target: architecture-containers-web}]` — confirmed to resolve
against `origin/launchpad`'s existing corpus tree.

## STEP 2 — Write the body

Sections: title/purpose, Responsibility (the relay-side mechanism that turns
the built `web/` bundle into HTTP responses), Public interface (path table:
`/assets/*`, `/invite/<code>`, `/`, `/repos*`, other → 404), Dependencies and
collaborators (depends on `web/dist` build output and `BUZZ_WEB_DIR`/
`BUZZ_SERVE_GIT_WEB_GUI` config; collaborates with the admin-bundle fallback
which it never falls through to), Boundary (explicitly not admin-web serving,
not the web app's own routes/features/client code, not deployment/staging —
each pointed at the owning node), Implementation paths, Relationships, Scope
and omissions (component-level exclusions + anything expected but not
verified, e.g. no direct config.rs test exercises the `BUZZ_WEB_DIR`
missing-`index.html` error path).

## STEP 3 — Validate: prove zero new FAILs

Run `python3 launchpad/project-intelligence/corpus/validate.py` with the new
file present; separately with it moved aside, to diff the FAIL set against
the known ~21–23 pre-existing failures. Restore the file afterward.

## STEP 4 — Earn the commit gate

Two separate Bash calls, in order: (a) the corpus unittest discover command
alone, confirming `OK`; (b) `git add` the two new files plus `git commit -s`.
Retry once on "COMMIT BLOCKED" per known finding #7; otherwise stop and
report BLOCKED.

## STEP 5 — Verify

Re-read the diff against every DoD bullet; re-open every cited file/line;
confirm the validate.py FAIL set is unchanged.

## GATES

- `validate.py` contributes zero new FAIL lines versus the pre-existing
  baseline.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` exits `OK`.
- Commit succeeds with a verification stamp (or BLOCKED is reported per
  finding #7).

## OPEN

- `architecture-containers-web`'s own `status` is `draft`, not `active` —
  referencing it is still valid (the schema only requires the target `id` to
  resolve, not any particular status), but a reader should know the container
  node it points to is itself unmerged-stable, not yet promoted.
- None of the sibling `platforms/web/*` tasks (#1286–#1288, #1290) are merged
  yet, so this node declares no relationship toward them; the first of them
  to land is the natural moment to add cross-links.

## LEFT OUT

- Admin-web bundle serving (separate host-gated bundle, separate directory,
  separate CSP) — already documented in `architecture-containers-web.md`'s
  admin-host branch; not this component's subject.
- The `web/` app's own routes, features, and client libraries (nostr client,
  git client, invite API) — owned by `architecture-containers-web.md` and by
  sibling tasks #1286 (application), #1287 (authentication), #1288
  (invite-ui), #1290 (repository-browser).
- Deployment/staging specifics (image build pipeline, cluster rollout) —
  owned by `squareup/sprout-oss` and `squareup/block-coder-tf-stacks`,
  outside this repository's corpus reach.
