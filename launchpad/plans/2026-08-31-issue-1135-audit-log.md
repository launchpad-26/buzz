Issue #1135 — task: document layers/observability/audit-log.md
Parent PRD #611. No `Size` line on the issue; the batch-run brief caps this single-document
task at 5 steps, so that is used as the declared cap rather than guessed per-step.

Stated size: no Size line on issue -> cap: 5 steps (batch-run instruction)

ALREADY TRUE
  `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md` are
  merged on `origin/launchpad` (HEAD ed133f4c5dbd546a67d963f11ffa630a4513b228), and
  `launchpad/docs/corpus/layers/observability/audit-log.md` does not exist yet (no
  `layers/` directory exists at all under `launchpad/docs/corpus` on `origin/launchpad` at
  this revision — checked directly). Two sibling `layers/observability/*.md` nodes
  (`logging.md` from #1139, `liveness.md` from #1138) are committed on their own
  not-yet-merged task branches (`task/1139-logging`, `task/1138-observability-liveness`),
  read directly from those branches via `git show` for front-matter-shape precedent —
  neither is reachable from this branch's history nor from `origin/launchpad`, so no
  `relationships` edge to either exists yet. Two existing merged corpus nodes do resolve
  and are legitimate relationship targets: `architecture-flows-event-ingestion` (already
  documents the `EventCreated` audit-channel enqueue in detail) and
  `architecture-principles-community-is-security-boundary` (the tenant-isolation principle
  the audit chain's `community_id`-first hashing enforces).

STEP 1  [independent]  Gather evidence directly from `crates/buzz-audit/src/{lib,hash,
        service,action,entry,error}.rs`, `migrations/0001_initial_schema.sql` (table DDL,
        `idx_audit_log_hash` unique index) and `migrations/0029_community_deletion.sql`
        (`attach_community_write_fence('audit_log')`), `crates/buzz-relay/src/state.rs`
        (bounded `mpsc` channel capacity 1000, single dedicated worker task, `.send().await`
        backpressure, `AuditShutdownHandle::drain`), `crates/buzz-relay/src/main.rs`
        (`BUZZ_AUDIT_ENABLED` wiring) and `crates/buzz-relay/src/config.rs` (`audit_enabled`
        field, default true, doc comment noting the separate `moderation_actions` trail is
        NOT controlled by this flag). Confirm via `grep -rn "AuditAction::" crates/` that
        only two of the enum's eleven variants (`EventCreated` in
        `crates/buzz-relay/src/handlers/event.rs`, `MediaUploaded` in
        `crates/buzz-relay/src/api/media.rs`) are ever constructed outside `buzz-audit`'s
        own crate, and via `grep -rn "verify_chain\|get_entries" crates/buzz-relay/src/`
        that both read-side methods are exercised only inside a `#[cfg(test)]` module in
        `event.rs`, with no production HTTP/CLI surface calling either today. Also record
        `docs/spec/MultiTenantRelay.tla`'s `auditHeads` variable (the per-community audit
        head this crate's own `lib.rs` doc comment cites) and rule out
        `launchpad/decisions/ADR-0008-security-audit-privilege.md` as unrelated (repo CI
        security-audit credentials, not this hash chain).
        done when: each source above has been opened directly and its relevant lines/behavior
        recorded, not assumed from a filename or doc comment alone.

STEP 2  [needs 1]  ← RUNS HERE  Write the node: front matter (`id: layers-observability-audit-log`,
        `type: layers`, `status: draft`, `origin: launchpad`, `audiences`, an `evidence`
        ledger with one entry per claim from STEP 1 classified FACT/INFERENCE/TEAM_KNOWLEDGE
        honestly, plus two `relationships` entries — `references` ->
        `architecture-flows-event-ingestion` and `depends-on` ->
        `architecture-principles-community-is-security-boundary`, both confirmed to resolve
        on `origin/launchpad` in STEP 1's evidence gathering) covering: definition (tamper-
        evident per-community SHA-256 hash chain over `audit_log`, scoped strictly to
        `buzz-audit`), boundaries/non-goals (explicitly excluding general application logging
        — #1139/#1144's territory — and the separate `moderation_actions` operator-action
        trail, which is a different table owned by `buzz-db`, not this crate), the actual
        write/read/verify mechanics from STEP 1, the async bounded-channel delivery design,
        and a scope-and-omissions section naming the two-of-eleven wired-actions gap and the
        no-production-read-surface gap as things found, not assumed away.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

STEP 3  [needs 2]  Re-run validate.py after any fix and iterate until clean; this step exists
        separately from STEP 2 because a first draft is not expected to pass on the first try
        given the citation-shape and evidence-class rules in `AGENTS.md`.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 with no
        further edits pending.

STEP 4  [needs 3]  Earn the verify-gate stamp and commit. Run the corpus unittest suite as the
        sole command in its own tool call, confirm `OK`, then commit in a separate call.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        reports `OK`, and `git commit -s -m "docs(corpus): document audit log (#1135)"` succeeds.

STEP 5  [needs 4]  Self-review: re-read the diff against issue #1135's DoD checklist line by
        line, confirm no second canonical document was created (`git show --stat HEAD` shows
        only the corpus doc + this plan file), confirm `validate.py` still exits 0.
        done when: every DoD bullet is checked off against the actual diff and `validate.py`
        exits 0 on a final run.

PARALLEL  None — one file, five sequential steps.

GATES     `validate.py` (STEP 2/3) and the corpus unittest suite (STEP 4), run locally in this
          worktree. No push, no PR — a separate integration step cherry-picks this commit into
          a shared batch PR, so `review-adjudicate` and cross-model final review are explicitly
          deferred to that later stage, not run here.

BUDGET    STEP 1 and STEP 2 together. The hard part is scoping a security/compliance-record
          concept honestly against general logging (#1139/#1144) and the separate
          `moderation_actions` operator-action trail, while accurately describing a real gap
          this task found rather than papering over it: only 2 of the 11 defined
          `AuditAction` variants have any production call site today, and the read-side
          (`verify_chain`/`get_entries`) has no caller outside a test module.

OPEN      Whether the nine unwired `AuditAction` variants (`EventDeleted`, `ChannelCreated`,
          `ChannelUpdated`, `ChannelDeleted`, `MemberAdded`, `MemberRemoved`, `AuthSuccess`,
          `AuthFailure`, `RateLimitExceeded`) are an intentional incremental rollout or an
          oversight is not this node's call — it records the gap as a FACT (grep-confirmed
          absence of call sites) without asserting a cause.

LEFT OUT  Any second authored document. General/umbrella application logging (#1139),
          structured-field logging schema (#1144), and datastore tracing policy macros
          (#1136) — named as siblings and excluded by scope, not folded in. The separate
          `moderation_actions` operator-action-log table (`buzz-db`) — a different system,
          only cross-referenced as a boundary, not documented here. Deciding whether the
          nine-unwired-actions gap or the no-read-surface gap should become its own
          implementation issue — that is a product decision for elsewhere, not this node's
          job.
