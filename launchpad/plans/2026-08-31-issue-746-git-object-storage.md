# Plan: issue #746 — document capabilities/git/git-object-storage.md

Parent: #613 (corpus batch). Worktree: `__worktrees/task-746-git-object-storage`,
branch `task/746-git-object-storage`. Local commit only — no push, no PR (a later
integration phase assembles one Feature-wide PR).

## ALREADY TRUE

- `launchpad/docs/corpus/templates/capability.md` is merged on `origin/launchpad`
  and gives this node's required sections, boundary rules, and relationship
  guidance — no template-absent fallback needed.
- No `launchpad/docs/corpus/capabilities/` directory exists yet on
  `origin/launchpad`; this is the first `type: capabilities` instance node.
- Two architecture nodes already merged on `origin/launchpad` directly cover
  adjacent ground and are valid `references` targets:
  `architecture-containers-object-storage` (the S3 container both Blossom media
  and git object storage share) and `architecture-flows-git-push` (the
  transport/auth flow around one push, which treats the CAS *outcome* as a black
  box).
- `docs/git-on-object-storage.md` is a full formal specification (axioms,
  theorems, TLA+ model, code-correspondence table) for exactly this capability —
  the primary source, not something to re-derive independently.
- Sibling tasks #745 (git-hosting, broader capability) and #753 (smart-http,
  transport) are both still OPEN — no risk of double-authoring their scope, and
  neither exists yet as a corpus node to link to.
- VISION_PROJECTS.md's Status table marks "Git hosting (smart HTTP + NIP-34)" as
  "Ships today" — the maturity citation the template requires.

## STEP 1 — Confirm scope boundary against siblings and existing nodes

Read #746/#745/#753's issue bodies (done) and the two existing architecture
nodes above in full (done) to fix the boundary: this node states *that* git
content is durably, content-addressed, CAS-published on object storage and
*why that's safe* (citing the formal spec), not *how the container is wired*
(object-storage.md's job) or *how a push is authenticated* (git-push.md's job)
or *how the CLI/HTTP surface commands it* (smart-http/git-hosting's job, not yet
drafted).

Done when: a one-paragraph capability statement and boundary list are drafted
that don't restate either existing node's content.

## STEP 2 — Verify the object-storage mechanics directly

Read `crates/buzz-relay/src/api/git/store.rs` (content-addressing, CAS
primitives, conformance probe), `crates/buzz-relay/src/api/git/manifest.rs`
(manifest schema, bounds, pointer key), and `crates/buzz-relay/src/main.rs`
(fail-closed probe-at-startup wiring) myself rather than trusting the
already-written container node's paraphrase.

Done when: every FACT claim about content-addressing, the manifest schema, the
pointer CAS, and the conformance gate cites a source this task opened directly.

## STEP 3 — Draft the node

Write `launchpad/docs/corpus/capabilities/git/git-object-storage.md` against
`node.schema.json` and the capability template's required sections (Capability
statement, Maturity, Boundary, Relationships, Scope and omissions). Classify
every claim; `TEAM_KNOWLEDGE` only for anything sourced from an issue/PR/brief.
Add `references` relationships to `architecture-containers-object-storage` and
`architecture-flows-git-push` (both confirmed present at the recorded revision
on `origin/launchpad`).

Done when: the file exists with schema-required front matter and no
schema-forbidden fields.

## STEP 4 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo
root. Confirm exit 0 and zero *new* FAIL entries beyond the 21 pre-existing
ones tracked in issue #1951.

Done when: the validator run is captured and shows no new failures attributable
to the new file.

## STEP 5 — Gate, commit, self-review

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` as the sole command in its own tool call; confirm `OK`. Then, in
a separate call, `git add` the new doc + this plan and `git commit -s`. Re-read
the diff against #746's DoD checklist line by line, re-open every cited source,
confirm no second canonical document was created, and confirm no new
`validate.py` FAIL entries. Do not push, do not open a PR.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0, zero new
  FAIL entries.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` prints `OK`.

## BUDGET

One document (~250-350 lines), one plan file, one commit. No code changes.

## OPEN

- Whether `architecture-flows-git-push`'s eventual `relationships` back-edge to
  this node should be added later — out of scope for this task (its own
  `AGENTS.md` rule: don't edit a merged sibling node just to add a return edge
  from here).

## LEFT OUT

- Any claim about `#745` (git-hosting) or `#753` (smart-http) content, since
  neither is drafted yet.
- Re-deriving the TLA+ proof or the conformance-probe algorithm's internals —
  cited to `docs/git-on-object-storage.md` and `store.rs`, not restated.
- The Blossom/media half of the shared object-storage container — already
  `architecture-containers-object-storage`'s subject, referenced not repeated.
