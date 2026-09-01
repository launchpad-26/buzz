# Plan: issue #1199 — corpus node `operations-databases-object-storage`

Issue #1199 states no explicit "Size" line in its body.
Stated size: not stated in issue body -> cap: 5 steps (the brief's own stated max for one document).

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`,
`launchpad/docs/corpus/AGENTS.md`, and `launchpad/docs/corpus/templates/reference.md`
are merged on `origin/launchpad`. `launchpad/docs/corpus/architecture/containers/object-storage.md`
(id `architecture-containers-object-storage`, status `draft`) already exists on this
worktree's branch history and documents the *architecture* container — technology,
ownership boundary, interfaces, deployment/data/security implications. No
`launchpad/docs/corpus/operations/` subtree exists yet anywhere in the corpus (`ls`
confirms `operations/` is absent), and
`launchpad/docs/corpus/operations/databases/object-storage.md` does not exist. No
`operations`-typed node exists anywhere in the 204-id merge-target inventory at
`<SCRATCH>/existing-node-ids.txt` — this is the first. Confirmed via `git rev-parse
HEAD` = `473205a7457b208455f188847bfb27b01aa83cac`.

STEP 1 [independent] — Gather evidence. Open `crates/buzz-media/src/{config.rs,
storage.rs,error.rs,bucket_index.rs,lib.rs}`, `crates/buzz-relay/src/{config.rs,
router.rs,storage_sweep.rs,api/media.rs}`, `crates/buzz-deletion/src/lib.rs`,
`.env.example`, `docker-compose.yml`, `deploy/charts/buzz/README.md`,
`ARCHITECTURE.md`, and the existing container-level object-storage node. Record the
`BUZZ_S3_*`/`BUZZ_MAX_*`/`BUZZ_MEDIA_*` env surface and its parse-time defaults; the
`MediaError` → HTTP-status mapping; the `/_readiness` probe's checked dependencies;
the storage-sweep's cold/warm-cache behavior; and the retention touchpoint in
`buzz-deletion`.
done when: every source file listed above has been opened in this session and its
relevant facts noted for step 2's citations.

STEP 2 [needs 1] — Write front matter (id `operations-databases-object-storage`,
type `operations`, status `draft`, origin `launchpad`, audiences `operator`+
`developer`, no `relationships` — the only plausible target,
`architecture-containers-object-storage`, is itself `status: draft` and its presence
on `origin/launchpad` cannot be confirmed from this worktree) and the body per
`templates/reference.md`'s required sections: reference description, structured
entries (config-surface table, key-taxonomy table), boundary statement, relationships
section (empty, explained), scope-and-omissions with the two distinct sub-parts
AGENTS.md step 8 requires.
done when: `launchpad/docs/corpus/operations/databases/object-storage.md` exists,
its front matter parses as YAML, and every claim in its evidence ledger cites a
source opened in STEP 1.

STEP 3 [needs 2] — Validate.
done when: `python3 launchpad/project-intelligence/corpus/validate.py` run from the
repo root exits 0.

STEP 4 [needs 3] — Earn the commit gate and commit. Run
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as the sole command in its own Bash call and confirm `OK`; then, in a
separate call, `git add -A && git commit -s -m "docs(corpus): ... (#1199)"`. RUNS HERE.
done when: the unittest run reports `OK` and `git log -1` on this branch shows the new
commit with a `Signed-off-by` trailer.

PARALLEL: none — one file plus its plan, one worktree, no fan-out.

GATES: `validate.py` exit 0 before commit. The unittest discovery command run alone,
in its own tool call, immediately before `git commit -s`, to earn the verification
stamp. No push, no PR — this batch's orchestrator integrates sibling branches later.

BUDGET: one hand-authored corpus document (~250-320 lines) plus this plan file. No
code changes. No generated-index regeneration (none exist to regenerate at this
revision).

OPEN: whether `architecture-containers-object-storage` is merged to `origin/launchpad`
by the time this node's sibling PR is reviewed is unknown at drafting time — its own
front matter records `status: draft`, and this task cannot confirm its presence on
the real merge branch from inside an unpushed worktree. The document links to it in
body prose (permitted per AGENTS.md/linking standard even when a `relationships[]`
edge is deferred) rather than adding an edge that might not resolve in CI.

LEFT OUT: the Blossom/BUD-11 auth protocol's full semantics (owned by the media
container node and `crates/buzz-media/src/auth.rs`); the git-on-object-storage
safety proof (`docs/git-on-object-storage.md`); the whole-community durable deletion
engine's staged-lease protocol in `crates/buzz-deletion` — mentioned only as the
retention touchpoint for object-storage keys, not documented in depth (a second
concept, out of this task's scope); a runbook for diagnosing an unreachable object
store (that is issue #1223's territory, a sibling of the failure-mode node #1218);
any code or config change.
