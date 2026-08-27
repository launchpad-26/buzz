# Plan: issue #663 — corpus doc `architecture/context/buzz-platform.md`

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` is merged and authoritative on
`origin/launchpad` (tip `a44cf52fc740ebebbdd671427480d14f0bce0115`); `launchpad/docs/corpus/AGENTS.md`
says explicitly to write against the schema with no per-type template; the target file
`launchpad/docs/corpus/architecture/context/buzz-platform.md` does not exist yet.

STEP 1 — Gather evidence: read `ARCHITECTURE.md` (system diagram, crate reference, infra
services, security model), `README.md`, `VISION.md`, `CONTRIBUTING.md`'s Ecosystem section,
`docker-compose.yml`, `.env.example`, and `ls crates/` / `ls desktop mobile web` to ground every
actor/system claim in something actually opened. **RUNS HERE.**

STEP 2 — Write front matter (id `architecture-context-buzz-platform`, type `architecture`,
status `draft`, origin `launchpad`, audiences chosen for who reads a system-context doc, one
`references` relationship to the confirmed-merged `corpus-agents` node) and a body satisfying
the issue's DoD: system boundary, every directly relevant actor/system and its relationship to
Buzz, a diagram-as-code (Mermaid) context diagram, no container/component implementation
detail.

STEP 3 — Validate: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
against the full corpus tree including the new file.

STEP 4 — Commit (plan + doc together) and open a draft PR against `launchpad`.

PARALLEL: none — single file, single worktree.

GATES: `validate.py` must exit 0 locally before commit; the corpus unittest suite
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`)
earns the commit verification stamp. `review-adjudicate` and the cross-model final-review pass
are explicitly deferred to the batch owner's morning review — not run in this task.

BUDGET: single document, one sitting — no multi-hour build expected.

OPEN: the issue's own DoD does not say whether `audiences` should include `operator` for a
context-level document that names infra (Postgres/Redis/MinIO/Keycloak) it does not describe
how to run — left as the author's judgement, called out in the node's own scope section rather
than resolved silently. Also open: `docker-compose.yml` provisions a `keycloak` service with no
Rust code referencing it, and `.env.example` sets `TYPESENSE_API_KEY`/`TYPESENSE_URL` though
`buzz-relay`'s own source says the Typesense-backed search worker was removed in favor of
Postgres FTS — both are recorded as verified gaps in the node body rather than guessed at.

LEFT OUT: no second canonical document, no template creation (none exists yet per AGENTS.md),
no changes to generated indexes. One `references` relationship was added (to `corpus-agents`,
confirmed merged on `origin/launchpad`) rather than omitting all relationships, per AGENTS.md's
own warning against a blanket "nothing to point at" justification once a target exists.

NOTE (operational): the Read/Write/Edit tools available to this session are NOT sandboxed to
this worktree the way Bash is — an early draft of this plan and the target document were first
written with an absolute `/home/serina/Launchpad/buzz/...` path and landed in the *main*
checkout instead of the worktree. Caught before commit, both stray files were removed from the
main checkout (`rm`, no `git` operation on that tree), and everything was rewritten under
`/home/serina/Launchpad/buzz/.claude/worktrees/wf_14803447-b4d-12/...`. Recorded here as a real
finding for whoever reviews this batch: this pattern likely bit other worktree tasks in the same
run.
