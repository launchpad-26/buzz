# Issue #919 — implementation/crates/buzz-audit.md

Stated size: one hand-authored corpus document, capped at 5 steps  ->  cap: 5 steps

ALREADY TRUE: `launchpad/docs/corpus/templates/implementation-reference.md`,
`launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/architecture/containers/relay.md` (id
`architecture-containers-relay`) are merged on `origin/launchpad`. No
`implementation/crates/` directory exists yet under `launchpad/docs/corpus` —
`buzz-audit.md` is the first node in it, and the first node built from the
implementation-reference template anywhere in the corpus. `crates/buzz-audit/`
(lib.rs, action.rs, entry.rs, error.rs, hash.rs, service.rs), the `audit_log` table
(`migrations/0001_initial_schema.sql`, fenced in `migrations/0029_community_deletion.sql`),
the "Audit log and observability" row of `docs/multi-tenant-conformance.md`, and the
`auditHeads` component of `docs/spec/MultiTenantRelay.tla` all already exist and were
read for this plan.

STEP 1  [independent] Confirm the crate's own surface and integration points already
read this session: `crates/buzz-audit/src/{lib,service,entry,hash,action,error}.rs`
(hash-chain design, per-community advisory lock, `AuditService::{log,verify_chain,
get_entries}`), `crates/buzz-relay/src/state.rs` (bounded `mpsc` audit worker,
`AppState::audit`/`audit_tx`, `AuditShutdownHandle`), `crates/buzz-relay/src/main.rs`
(audit pool construction gated on `config.audit_enabled`), `crates/buzz-relay/src/
config.rs` (`BUZZ_AUDIT_ENABLED`, default true, does not disable the separate
`moderation_actions` trail), `crates/buzz-relay/src/handlers/event.rs` (the two
audit-specific unit tests: `audit_records_caller_actor_not_relay_signer_for_relay_signed_event`,
`audit_chain_is_isolated_per_tenant_through_relay_ingest`), and `crates/buzz-test-client/
tests/conformance_multitenant.rs`'s `mod audit_log` (the doc-only conformance row
explaining audit has no client-reachable wire surface). Confirm `buzz-admin/Cargo.toml`
declares `buzz-audit` as a dependency with zero actual references in `buzz-admin/src/*.rs`
— a real, citable divergence between the conformance test's prose ("consumed by
buzz-admin") and current code. Record `git rev-parse HEAD` for the provenance citation.
done when: every file above has been opened in this session and the HEAD SHA is recorded.

STEP 2  [needs 1] Write `launchpad/docs/corpus/implementation/crates/buzz-audit.md`
against the template's required sections (Realization statement, Target, Implementation
surface, Divergences, Verification, Relationships, Scope and omissions). Front matter:
`id: implementation-crates-buzz-audit`, `type: implementation`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, reviewer]`, one `evidence` entry per
substantive claim (FACT for everything opened directly this session, INFERENCE with a
confidence for reasoned claims, TEAM_KNOWLEDGE with `provided_by` for anything sourced
only from the conformance test's own prose rather than independently re-derived code).
Target section names `docs/multi-tenant-conformance.md`'s "Audit log and observability"
row and `docs/spec/MultiTenantRelay.tla`'s `auditHeads` by path, not by a corpus node id
neither has yet. Relationships: `part-of: architecture-containers-relay` only (verified
merged; buzz-audit is an in-process subsystem the relay orchestrates on its own pool,
per relay.md's own text) — no `implements` edge, since neither target carries a corpus
node id. Scope and omissions names the `moderation_actions` trail, the audit table's own
schema/migration ownership, and the buzz-admin dependency-with-no-call-site as gaps
rather than silence. ← RUNS HERE
done when: the file exists, every DoD bullet from issue #919's body is satisfied, and
every citation in the evidence ledger points at a file actually opened in STEP 1.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py` from
the repository root; fix any reported error and re-run until it exits 0.
done when: the command's own exit status is 0.

STEP 4  [needs 3] Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own tool call to earn the commit
gate; confirm `OK`. Then, in a separate tool call, stage exactly the new corpus document
and this plan file and commit with `git commit -s -m "docs(corpus): add buzz-audit
implementation reference (#919)"`.
done when: the unittest run reports `OK` and `git log -1` on the worktree shows the new
commit containing only the two intended files, with no `git push` and no `gh pr create`
run afterward.

PARALLEL: none — one document, one dependent chain (evidence gathering, then drafting,
then validation, then the commit gate); each step needs the one before it.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before the
commit gate runs. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/
tests -p "test_*.py"` must report `OK` as the sole command in its own tool call,
immediately before the commit. `review-adjudicate` and cross-model final review are
deferred to the batch owner once all 37 sibling documents are integrated into the single
Feature-level draft PR — not run here.

BUDGET: small — one document, no code changes, evidence already gathered from roughly a
dozen files read directly (the six `buzz-audit` source files, three `buzz-relay` files,
one migration, one conformance doc, one TLA+ spec, one e2e conformance module).

OPEN: Whether the buzz-admin `Cargo.toml` dependency-with-no-call-site is itself worth a
separate issue (dead/premature dependency) is not this task's to decide — it is recorded
in the node as a divergence between the conformance test's prose and current code, and
left there. Whether `docs/multi-tenant-conformance.md` or `docs/spec/MultiTenantRelay.tla`
will get their own corpus node ids later (which would make a real `implements` edge
possible) is outside this task's scope to predict, same as `AGENTS.md`'s own open
question about ADRs/NIPs.

LEFT OUT: No `implements` relationship — neither target has a corpus node id, and
inventing one is a hard validation error per `AGENTS.md`. No relationship toward any
other `implementation/crates/*` sibling node, since none of the other 36 documents in
this batch run are merged on `origin/launchpad` at plan time. No attempt to add a
`references` edge to a verification/test-strategy node — `#1350`'s test-strategy template
is not merged. No change to `crates/buzz-audit/` itself, `docs/multi-tenant-
conformance.md`, or `docs/spec/MultiTenantRelay.tla` — this task documents them, it does
not edit them. No `git push` and no `gh pr create` — this batch integrates all 37
documents into one Feature-level draft PR later.
