# Issue #1041 — layers/compute/backend-provider.md

Stated size: dispatch prompt caps this task at a single small document -> cap: 5 steps

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md`
and `launchpad/docs/corpus/templates/concept.md` are merged on `origin/launchpad`
(`338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`). `launchpad/docs/corpus/layers/compute/backend-provider.md`
does not exist yet (confirmed with `test -f`). No `type: layers` node exists anywhere in the merged
corpus yet, so no relationship target of that type is available; the one plausible target,
`architecture-containers-agent-runtime` (`type: architecture`), is merged and already discusses
backend providers in its own body. `docs/remote-agents.md` (a formal spec, `status: draft` per its
own header) is the primary source for the concept; it is pinned to commit `28ae6cd21`, which is an
ancestor of `HEAD`. `desktop/src-tauri/src/managed_agents/backend.rs` and
`crates/buzz-backend-kubernetes/` are the concrete implementation and the one shipped conforming
provider.

STEP 1 [independent] — Gather evidence. Re-confirm (already read once this session, re-verify at
commit time): `docs/remote-agents.md` (System Model, Launchers, I1-I5 invariants, Provider Protocol
`info`/`deploy`), `desktop/src-tauri/src/managed_agents/backend.rs` (discovery, staging/digest gate,
`invoke_provider`, `validate_provider_config`, `redact_secrets_with`), `desktop/src-tauri/src/managed_agents/types.rs`
(`BackendKind` enum: `Local` | `Provider { id, config }`), `desktop/src-tauri/src/commands/agent_providers.rs`
(`discover_backend_providers`, `probe_backend_provider` Tauri commands), and
`crates/buzz-backend-kubernetes/src/main.rs` (the one shipped provider, its relay-mesh refusal
tests). Confirm via `git log -S "fn stage_provider"` and `git merge-base --is-ancestor` that the
pre-secret staging gate (commit `6530b58a6`) postdates the spec's pinned commit `28ae6cd21`, so the
spec's own "Known Defect 5" (gate not implemented) is stale against current code — record this as a
documentation-drift note rather than silently repeating the stale claim. Confirm the "provider"
name collision: `agent.provider` (LLM/model provider, e.g. `anthropic`, `relay-mesh`) is a distinct
field from a backend provider's `id` (`desktop/src-tauri/src/managed_agents/types.rs` — three
`pub provider: Option<String>` sites vs. `BackendKind::Provider { id, .. }`) — this is the
disambiguation the concept template requires in its Definition section. done when: every citation
used in STEP 2's evidence ledger has been opened directly in this worktree at `HEAD`, and the
staging-gate ordering claim is confirmed by the two git commands above.

STEP 2 [needs 1] — Write the document at `launchpad/docs/corpus/layers/compute/backend-provider.md`
using `templates/concept.md`'s required sections (Definition; optional visual aid/Background; Use
cases; optional Comparison; Related resources; Scope and omissions). Front matter: id
`layers-compute-backend-provider`, type `layers`, status `draft`, origin `launchpad`, audiences
`[agent, developer, operator, reviewer]`, one evidence entry per substantive claim classified
FACT/INFERENCE/TEAM_KNOWLEDGE per `AGENTS.md`'s rules, a commit-citation provenance entry for
`HEAD`, and the documentation-drift finding from STEP 1 stated explicitly in the body (not silently
omitted or silently "corrected" in the spec). `relationships`: a single `references` edge to
`architecture-containers-agent-runtime` (confirmed merged on `origin/launchpad` in ALREADY TRUE) —
justified in the body rather than asserted bare. ← RUNS HERE. done when: the file exists, contains
a Definition, a boundary/non-goals statement disambiguating "backend provider" from "LLM provider",
a Use cases section, a Related-resources/relationships section, and a Scope-and-omissions section
naming both what is out of scope and what STEP 1 could not verify.

STEP 3 [needs 2] — Validate. Run `python3 launchpad/project-intelligence/corpus/validate.py` from
the repo root; fix any reported error (schema violation, bad citation shape, unresolved relationship
target) and re-run until it exits 0. done when: the command's own exit code is 0.

STEP 4 [needs 3] — Self-review the diff against issue #1041's DoD checklist line by line (one hand-
authored document only; schema-valid front matter; one independently maintainable idea; no folded-in
second concept; FACT/INFERENCE/TEAM_KNOWLEDGE not conflated; links instead of duplicated content;
checked against the recorded HEAD; validator clean; term defined in one sentence; boundaries/non-
goals stated; related concepts linked; examples that don't introduce a second concept). done when:
each DoD bullet has been checked against the actual file content and the check is recorded in the
final report, not merely asserted.

STEP 5 [needs 3] — Earn the verify-gate stamp as the sole prior command
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`,
confirm `OK`), then in a separate tool call `git commit -s -m "docs(corpus): document backend
provider (#1041)"`. Do not push and do not open a PR (batch-integration process owns that).
done when: the unittest run reports `OK` and a subsequent `git log -1` on the worktree branch shows
the new commit with the corpus document staged.

PARALLEL: none — single document, single task, no independent sub-work to fan out.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must
report `OK` to earn the commit hook's verification stamp. `review-adjudicate` and the cross-model
final review pass are deferred to the batch owner's later integration review — not run in this task.

BUDGET: small — one document, no runtime/product code changes, no test changes; evidence gathering
scoped to `docs/remote-agents.md`, `desktop/src-tauri/src/managed_agents/{backend,types}.rs`,
`desktop/src-tauri/src/commands/agent_providers.rs`, and `crates/buzz-backend-kubernetes/src/main.rs`
plus two targeted `git log`/`git merge-base` checks.

OPEN: whether `references` is the right relationship type toward
`architecture-containers-agent-runtime`, versus omitting relationships entirely as the sibling corpus
docs (`corpus-standard-atomicity`, `architecture-containers-agent-runtime` itself) did when no
sibling node existed — resolved in STEP 2 by using `references` since a real, merged, on-topic
target now exists (unlike those earlier nodes' moment), but the call is recorded here for a reviewer
to override. Whether the Known-Defect-5 documentation-drift finding belongs only in this node's body
or also warrants its own follow-up issue against `docs/remote-agents.md` is left to the final report,
not decided by this plan.

LEFT OUT: no edit to `docs/remote-agents.md` itself (fixing the stale Known Defect 5 claim there is
separate documentation work, not owned by this task); no second corpus node for the LLM-provider
concept even though the name collision is documented (that concept, if it needs its own node, is a
separate task per the atomicity standard); no code change to `backend.rs`,
`buzz-backend-kubernetes`, or any Tauri command; no push, no PR — this commit stays local on
`task/1041-backend-provider` for later batch integration.
