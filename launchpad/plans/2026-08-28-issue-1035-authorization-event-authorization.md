Issue #1035 — task: document layers/authorization/event-authorization.md
Stated size: no `Size` line on the issue -> cap: 5 steps (single-documentation-file
task, corpus-author skill's own procedure already sequences the work).

ALREADY TRUE (verified against git and the worktree, not notes)
  - Worktree exists at __worktrees/task-1035-authorization-event-authorization,
    branch task/1035-authorization-event-authorization, HEAD ==
    338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 == origin/launchpad (git rev-parse
    confirms).
  - launchpad/docs/corpus/layers/ does not exist yet anywhere under the corpus
    root (find confirms) — this will be the first `layers`-typed node and the
    first document under `layers/authorization/`.
  - launchpad/docs/corpus/templates/concept.md exists and is merged (present
    in this worktree, which is HEAD == origin/launchpad). Its DoD-matching
    vocabulary ("defines the term in one sentence", "states boundaries/
    non-goals", "links the concept to related concepts", "uses examples only
    to clarify the concept") is a direct match for issue #1035's own DoD
    checklist bullets, so the concept template governs this node's shape.
  - node.schema.json, AGENTS.md, schema/README.md, templates/concept.md, and
    standards/identifiers.md (id rules) already read in full this session.
  - No manifest.py row exists for this task (grepped; none found) — the
    primary task brief supplies id/type/status directly instead, so that
    brief is treated as the row-equivalent per the corpus-author skill.
  - Source evidence already read this session: crates/buzz-relay/src/handlers/
    ingest.rs (required_scope_for_kind, requires_h_channel_scope,
    is_global_only_kind, extract_channel_id, check_channel_membership,
    check_token_channel_access, ingest_event/ingest_event_inner's auth
    sequence lines ~1881-2340), crates/buzz-auth/src/scope.rs (Scope enum +
    NIP-42 doc comment), crates/buzz-core/src/verification.rs (verify_event).
    crates/buzz-auth/src/access.rs (ChannelAccessChecker/check_write_access)
    was read and confirmed by grep to have no callers under crates/ outside
    its own crate — it is NOT wired into the ingest write path, so it is
    named as an explicit non-covered sibling rather than folded in.
  - Four candidate `references` relationship targets confirmed present on
    origin/launchpad (git ls-tree): architecture-flows-event-ingestion,
    architecture-principles-community-is-security-boundary,
    architecture-principles-fail-closed-boundaries,
    architecture-principles-signed-events. Each skimmed for topical fit.

STEP 1  [independent] Finalize the evidence ledger's claim list from the
        sources already read: per-kind scope requirement (required_scope_
        for_kind + auth.scopes()), pubkey/principal identity match (with the
        NIP-59 gift-wrap exception), h-tag channel-scoping rules (requires_
        h_channel_scope vs is_global_only_kind), token-channel restriction
        (check_token_channel_access + the channel-scoped-token-cannot-
        publish-global-events rule), channel membership + open-channel
        fallback (check_channel_membership), the per-kind membership-skip
        list, the durable ban/timeout write-block backstop and its fail-
        closed DB-error handling, and the NIP-42/NIP-98 auth-context shape
        (IngestAuth::Nip42/Http).
        done when: every claim above is classified FACT (all are directly
        visible in opened source, no INFERENCE needed) with a bare-path
        citation into ingest.rs, scope.rs, or verification.rs.

STEP 2  [needs 1] Write the front matter: id: layers-authorization-event-
        authorization, type: layers, status: draft, origin: upstream
        (documents block/buzz product behavior, not a launchpad-process
        concern), audiences: [agent, developer, reviewer], the commit-
        citation provenance FACT, the Step 1 evidence array, and four
        `references` relationships to the confirmed targets above.
        done when: front matter is schema-shaped (checked by eye against
        node.schema.json's required/forbidden field rules per class).

STEP 3  [needs 2] Write the body against templates/concept.md's required
        sections: intro paragraph, Definition (what "event authorization"
        means at the relay's ingest seam, distinct from authentication),
        a Mermaid sequence diagram of the check order, Background (why the
        checks are ordered/layered this way — verify -> identity match ->
        scope -> ban/timeout -> channel resolution -> token/membership),
        Use cases, boundary/non-goals against authentication (signed-events
        principle) and against read-path access (buzz-auth/access.rs,
        explicitly named as out of scope), and the required Scope and
        omissions section (two distinct parts: what isn't covered, and what
        was expected but not verified — e.g. read-path ChannelAccessChecker
        wiring, per-kind command-handler-local authorization inside
        validate_admin_event/handle_command).
        done when: launchpad/docs/corpus/layers/authorization/event-
        authorization.md exists with complete front matter and body.

STEP 4  [needs 3] Validate.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py`
        exits 0, AND `python3 -m unittest discover -s launchpad/project-
        intelligence/corpus/tests -p "test_*.py"` (run as the sole command in
        its own tool call, per the commit-gate requirement) prints OK.

STEP 5  [needs 4] Re-read the diff against every DoD bullet in #1035, commit
        (`git commit -s`), push, and open the PR as a draft with the required
        body statements (Closes #1035; validate.py + unittest both passed;
        self-review only, no review-code skill invoked; the deferred-
        cross-model-review sentence).
        done when: `gh pr create --draft ...` returns a PR URL, run as a lone
        Bash command with no `cd` prefix.

GATES     No automated review-* skill is invoked in this task per the
          orchestrating brief — verification is self-review (Step 5's re-read
          against the DoD), explicitly stated as such in the PR body. The
          commit-gate suite (Step 4's unittest discover) is the only
          mechanical gate this task's brief requires before commit.
OPEN      Whether `origin: upstream` vs `origin: launchpad` is the durably
          correct choice for a node documenting relay authorization behavior
          is this task's own judgment call, not settled by any standard read
          this session (standards/*.md were not read in full given the 5-step
          cap) — reasoned from ADR-0003's origin-prefix meaning (content
          about the underlying product vs. about the launchpad/cohort
          process) and left explicit here rather than assumed silently.
LEFT OUT  Reading every standards/*.md document in full (8,130 lines total) —
          AGENTS.md is explicit that it is the current governing procedure
          and that per-type standards are "somewhere in #1307-#1351", not
          required reading for every authoring task; identifiers.md was
          read for the id-permanence rule only. Documenting the read-path
          channel-access mechanism (buzz-auth/access.rs) as its own concept
          — confirmed unused by the ingest write path, named as a gap in the
          new node's own scope section rather than drafted here, since a
          second concept discovered while writing must be filed as its own
          task, not folded in.
