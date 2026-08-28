Issue #1037 — task: document layers/authorization/moderation-authorization.md
Stated size: none stated  →  cap: 5 steps (single-document task under parent PRD #607)

Target file: `launchpad/docs/corpus/layers/authorization/moderation-authorization.md`
Node id: `layers-authorization-moderation-authorization` (assigned by the issue's own
  DoD path; permanent)
Base branch: `origin/launchpad`

ALREADY TRUE  (verified against git at 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, not notes)
  `git status --short` in this worktree reports clean before this plan file is added.
  `launchpad/docs/corpus/layers/` does not exist anywhere in the tree — this is the
    first node under `layers/` of any kind, so no sibling `layers-*` id exists yet and
    no `relationships[].target` can resolve to one.
  `launchpad/docs/corpus/templates/` has no `layers`-specific template; the closest
    types (`policy.md`, `invariant.md`, `concept.md`) are generic templates, not a
    `type: layers` template, so this node is written directly against
    `node.schema.json` per `AGENTS.md`'s "no per-type template yet" guidance.
  `crates/buzz-relay/src/handlers/moderation_authz.rs` is the single capability seam
    for every moderation authorization decision: `authorize_moderation_action` (async,
    resolves roles via `buzz_db::relay_members::get_relay_member` and
    `buzz_db::channel::get_member_role`) delegates to `decide_authority`, a pure
    function exhaustively unit-tested in the same file (7 tests, all passing logic
    inline — read, not run, for this doc).
  Roles: community role is `relay_members.role`, a `TEXT CHECK (role IN ('owner',
    'admin', 'member'))` column (`migrations/0001_initial_schema.sql:574-582`).
    Channel role is `channel_members.role`, a `member_role` Postgres ENUM with five
    values `('owner','admin','member','guest','bot')` (`migrations/0001_initial_schema.sql:30,132-145`),
    though `decide_authority` only ever matches `"owner"`/`"admin"` out of it.
  `decide_authority`'s policy, read directly from source: community owner holds every
    `ModerationAction` unconditionally; community admin holds every action except it
    is denied `Ban`/`Timeout` against a target whose community role is `owner` or
    `admin` (an `anyhow::bail!` guard); a non-community-role actor gets only
    `DeleteMessage`/`Kick` and only via a channel `owner`/`admin` role; everyone else
    is denied. `Unban`/`Untimeout`/`ResolveReport`/`ViewQueue` are unguarded at this
    seam for admins.
  Three call sites all route through `authorize_moderation_action` rather than any
    inline check: `crates/buzz-relay/src/handlers/moderation_commands.rs` (4 call
    sites, kinds 9040-9044 ban/timeout/etc.) and
    `crates/buzz-relay/src/api/bridge.rs:2171` (HTTP moderation-queue read, gated on
    `ModerationAction::ViewQueue`).
  `python3 launchpad/project-intelligence/corpus/validate.py` is the deterministic
    gate; `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
    -p "test_*.py"` is the commit-gate suite. Neither has run yet against this task's
    content.

STEP 1  Create the node file with schema-valid front matter          [independent]
        Create `launchpad/docs/corpus/layers/authorization/moderation-authorization.md`
        with front matter: `id: layers-authorization-moderation-authorization`,
        `type: layers`, `status: draft`, `origin: launchpad`,
        `audiences: [agent, developer, reviewer]`, and the single permitted
        commit-only FACT recording revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5.
        No `relationships` key — no other `layers` node exists to point at.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0
                   with the new file present, and `git cat-file -e
                   338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5` exits 0.

STEP 2  Write the one-sentence definition and the decision model     [needs 1] ← RUNS HERE
        Write a one-sentence definition of moderation authorization up front (per the
        issue DoD), then the decision model: the three `ModerationAuthority` outcomes
        (`CommunityOwner`, `CommunityAdmin`, `ChannelRole`), the `ModerationAction`
        capability grid, and the admin guard rail against actioning an owner/fellow
        admin. Add one `evidence` entry per substantive claim, classified honestly:
        the role/action mechanics read from `moderation_authz.rs` are FACT; the "single
        seam, not inline checks" design intent read from the module doc comment and the
        three call sites is FACT (it is stated, not inferred); anything reasoned beyond
        what the source states is INFERENCE with a confidence.
        done when: validator exits 0; every claim in the decision-model section has a
                   matching `evidence` entry, checked by reading the two side by side.

STEP 3  Write boundaries/non-goals and links to neighbors             [needs 2]
        State boundaries: this node covers *authorization* (who may act) only, not
        the command handlers' side effects (audit rows, notices, live disconnects —
        `moderation_commands.rs`), not channel *membership* gating for ordinary reads,
        and not the "no Moderator tier in v1" roadmap note (that is a product-roadmap
        fact, not an authorization contract, and stays out to avoid a second concept
        folded into this node). Link to the three source files
        (`moderation_authz.rs`, `moderation_commands.rs`, `bridge.rs`) as
        implementation, and the relay/channel migrations as the schema backing role
        values. No corpus `relationships` entries — nothing to point at (see ALREADY
        TRUE).
        done when: validator exits 0; the body names all three call sites and the two
                   role-storage locations by path.

STEP 4  Write a worked example                                        [needs 3]
        Add one small worked example from the unit tests already in
        `moderation_authz.rs` (e.g. an admin denied `Ban` against a fellow admin target,
        allowed against a plain member) to make the guard rail concrete, citing the
        specific test function it is drawn from. The example illustrates the one
        concept in this node; it must not introduce a second one (e.g. no digression
        into report-resolution's `resolve:*` audit-string vocabulary).
        done when: validator exits 0; the example cites the exact test function name it
                   is drawn from.

STEP 5  Audit against the DoD checklist and the corpus AGENTS.md      [needs 4]
        Re-read the finished node against every Definition-of-Done bullet in issue
        #1037 and against `AGENTS.md`'s "Creating a node" steps 6-9. Confirm: exactly
        one hand-authored file was created; every FACT's source was actually opened
        (re-open each cited path); INFERENCE entries carry `confidence` and no
        `provided_by`; no TEAM_KNOWLEDGE entries exist unless something is genuinely
        uncorroborated; the body defines the term, states boundaries, links neighbors,
        and uses the example only illustratively.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0;
                   `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
                   -p "test_*.py"` reports OK; every DoD checklist bullet is satisfied,
                   confirmed by re-reading the diff against the issue body line by line.

PARALLEL  None. All five steps edit the same single file; sequential regardless of how
          unrelated they look, per the same rule the #1307 sibling plan used.

GATES     This plan is self-reviewed (no `review-plan` invocation), per the batch
          task's instruction that verification here is self-review, not a
          cross-model or `review-code` pass — that is explicitly deferred to the
          batch owner's review before merge. The PR is opened as a draft to make
          that deferral visible rather than implicit.

OPEN      Whether `developer` belongs in `audiences`. Included here (unlike the
          #1307 standards-node precedent) because this node documents a *runtime
          authorization contract* relay engineers implementing new moderation actions
          need to read, not a corpus-authoring policy — its addressee set is wider.
          Revisable in a follow-up if a later `layers` template says otherwise.

LEFT OUT  Any `relationships` edges — no other `layers` node exists on `origin/launchpad`
          to point at; stated in the body with its reason.
          A second hand-authored corpus document — the issue's out-of-scope list and
          this node's own single-idea rule both forbid it.
          Any change to `moderation_authz.rs` or its callers — this is documentation
          of existing behavior, not a behavior change.
          Editing `launchpad/docs/corpus/AGENTS.md` or any generated index.
