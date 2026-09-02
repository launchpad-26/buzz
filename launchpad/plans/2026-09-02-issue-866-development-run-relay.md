# Plan — issue #866: document `development/run-relay.md`

Target: `launchpad/docs/corpus/development/run-relay.md`
Shape: procedure node, modelled on `launchpad/docs/corpus/templates/procedure.md`
Front matter: `id: development-run-relay`, `type: development`, `status: draft`,
`origin: launchpad`
Revision: `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`
Branch: `task/866-development-run-relay`

## ALREADY TRUE

- The target file does not exist (`ls` at the recorded revision returns
  "No such file or directory"). This is a create, not an update.
- The worktree is isolated at `__worktrees/task-866-development-run-relay`, branched
  from `origin/launchpad`.
- `launchpad/docs/corpus/development/` already holds four merged nodes: `build.md`
  (`corpus-development-build`), `debugging.md` (`debugging`), `hermit.md`
  (`development-hermit`), `prerequisites.md` (`development-prerequisites`).
- The `<directory>-<stem>` id convention is settled (tracked at #2029); siblings
  `development-hermit` and `development-prerequisites` already follow it.
- The commands this node documents are all already committed and authoritative:
  `Justfile` recipes `bootstrap`, `setup`, `relay`, `relay-web`, `relay-release`,
  `down`, `ps`, `logs`, `_ensure-services`, `_ensure-migrations`; and
  `scripts/dev-setup.sh`, `scripts/ensure-local-relay-key.sh`.

## STEP 1 — Establish the boundary against merged neighbours

`architecture/deployment/local-development.md` is merged and already owns the compose
topology, network boundaries, persistence, the `_ensure-services` health-wait loop,
the migration mechanism, and the destructive `just reset` recovery path.
`development/debugging.md` is merged and already owns the `/health` and
`/_readiness` curl probes and `just logs` for diagnosis — and it restated
`just reset` without citing `local-development.md`, which is filed as defect #2030.

**Done when:** both nodes have been read in full, and this node's own verification
step is written from a source neither of them uses — the relay's own startup log
sequence in `crates/buzz-relay/src/main.rs` — with the curl probes deferred by link
rather than restated.

## STEP 2 — Verify every command from source, not from prose

Open and read: `Justfile` (`bootstrap`, `setup`, `relay`, `relay-web`,
`relay-release`, `down`, `ps`, `logs`, `_ensure-services`, `_ensure-migrations`),
`scripts/dev-setup.sh`, `scripts/dev-reset.sh`, `scripts/ensure-local-relay-key.sh`,
`.env.example`, `crates/buzz-relay/src/main.rs`, `crates/buzz-relay/src/router.rs`,
`crates/buzz-relay/src/config.rs`.

Two claims in the dispatch brief must be checked rather than repeated:

- "migrations auto-apply on relay startup" — `main.rs` gates `db.migrate()` behind
  `BUZZ_AUTO_MIGRATE`, which `.env.example` does not set. Verify and state the
  actual local mechanism (`_ensure-migrations`).
- "`/_readiness` + `/_liveness` are on a separate port" — `router.rs` registers both
  on the main app router *and* on `build_health_router`. Verify and state both.

**Done when:** every command and endpoint in the draft has a line-verified source,
and the two brief claims above are resolved against code.

## STEP 3 — Draft the node

Body follows the procedure template's required sections: overview, *Before you
start*, ordered action-verb steps capped near 8–10, success verification, stop and
cleanup, *See also*, *Boundary*, *Relationships*, *Scope and omissions*.

Front-matter ledger: first entry records revision
`aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90` as a commit citation. Every other FACT
cites a repository-relative path opened during STEP 2. INFERENCE entries carry
`confidence`; TEAM_KNOWLEDGE entries carry `provided_by` and no `confidence`.

Relationships (all four confirmed present on `origin/launchpad` via
`git grep -l "^id: <id>$" origin/launchpad`):
`implements: corpus-template-procedure`,
`references: architecture-deployment-local-development`,
`references: development-prerequisites`,
`references: layers-observability-health-checks`.

**Done when:** one level-1 heading directly after the front matter, under 1000
lines, no canonical content of a merged neighbour restated.

## STEP 4 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the worktree
root; require PASS. Then re-open every citation in the ledger and confirm the cited
file supports the statement above it — the validator checks path existence only, not
support.

**Done when:** validator reports PASS and every citation has been re-opened.

## STEP 5 — Gate, then commit

Run, bare and unpiped, as the sole command in its own call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
Confirm `OK`. Then `git add` the document and this plan, and `git commit -s`.
No `--no-verify`. No amend (blocked by `git-safety.sh`), so DoD re-verification
happens before the commit, not after.

**Done when:** unittest reports OK and one signed commit exists on this branch.

## PARALLEL

Steps 1 and 2 are independent reads and were gathered concurrently. Steps 3–5 are
strictly sequential.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` → PASS
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → OK
- Pre-commit hooks run unmodified.

## BUDGET

One hand-authored corpus document plus this plan. No generated indexes, no source
changes, no second corpus node.

## OPEN

- Whether the top-level `AGENTS.md` claim that `migrations/` are "auto-applied on
  relay startup" should be corrected is not this node's call.
  `architecture-deployment-local-development` already records the same discrepancy
  and reads it as production framing; this node states the local mechanism and links
  there rather than re-litigating it.
- Whether `debugging.md`'s restatement of `just reset` (#2030) gets fixed does not
  block this node, which avoids the same restatement.

## LEFT OUT

- Running the relay. The commands are documented from source; no `just setup`,
  `just relay` or `docker compose` was executed for this node, and that is disclosed
  in the node's own *Expected but not verified* section.
- Desktop (`just dev`), web (`just web`), admin (`just admin`) and mobile run
  procedures — separate surfaces, separate tasks.
- Deployed and staging relay operation — owned by the deployment nodes.
- Any edit to a merged neighbour node.
