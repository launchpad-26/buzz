# Issue #1003 — interfaces/nostr/buzz-nips/nip-pma.md

Stated size: not stated as a Size line in the issue body  →  cap: 4 steps
(the issue is a single corpus-plan-generated document task — one file, no code
— with an eleven-bullet definition of done; treated as small per the plan-issue
skill's own table, since no Size line exists to ask about beyond this checklist).

ALREADY TRUE  (verified against git, not notes)
  `docs/nips/NIP-PMA.md` exists at repo root and is the authoritative spec text
  (confirmed by reading it in full: kind 30179, owner-encrypted aggregate,
  `draft` status, "Relays MUST reject this kind until ... deployed").
  `launchpad/docs/corpus/interfaces/` does not exist in this worktree or on
  `origin/launchpad` — the target file and its parent directories do not exist yet.
  `launchpad/docs/corpus/templates/interface.md` (id `corpus-template-interface`)
  IS merged on `origin/launchpad`, contradicting the task brief's claim that "no
  template exists yet" — it is used below as structural guidance (required
  sections: interface description, operations, contract and stability, boundary,
  relationships, scope and omissions), not copied verbatim, and its own id is a
  valid `implements` relationship target because it is actually present in the
  loaded corpus.
  `node.schema.json`'s `type` enum has no `interface` value; the correct
  interface-shaped value is `interfaces-events` (confirmed by reading the enum
  and by `templates/interface.md`'s own "A note on `type`" section).
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` lists no
  other `interfaces/` or event-kind instance node — only `architecture/*`,
  `standards/*`, `templates/*`, `schema/*` — so `corpus-template-interface` is the
  only legitimate `relationships` target for this node today.
  `crates/buzz-core/src/kind.rs` defines `KIND_PRIVATE_MANAGED_AGENT = 30179` and
  lists it in `AUTHOR_ONLY_KINDS`; `crates/buzz-core/src/private_managed_agent.rs`
  (1134 lines) implements the full envelope/payload codec (`validate_envelope`,
  `build_event`, `validate_and_decrypt`, `validate_payload`) with unit tests
  including a valid round-trip (`owner_self_round_trip_binds_outer_and_inner`)
  and a failure case (`wrong_owner_and_tampering_fail_closed`).
  `crates/buzz-relay/src/handlers/ingest.rs` currently classifies kind 30179 as an
  ordinary owner-scoped (`Scope::UsersWrite`, global-only, non-channel) write —
  no dedicated ingest-time rejection branch for it was found anywhere in
  `crates/buzz-relay/`, which sits in tension with the spec's own "Relays MUST
  reject this kind" line; `crates/buzz-relay/CHANGELOG.md` records
  "feat(relay): accept kind:30179 private managed-agent events at ingest" (PR
  #5133), and `migrations/0033_private_managed_agent_fts.sql` +
  `crates/buzz-db/src/runtime/migration.rs` (migration index 32/version 33)
  confirm kind 30179 is excluded from FTS tokenization, matching the spec's
  deployment-order step 2 requirement.

STEP 1  Re-confirm every citation target above still resolves.      [independent]
        Record exact line ranges for: `docs/nips/NIP-PMA.md` (whole file),
        `crates/buzz-core/src/kind.rs` (KIND_PRIVATE_MANAGED_AGENT doc comment +
        AUTHOR_ONLY_KINDS), `crates/buzz-core/src/private_managed_agent.rs`
        (module doc, `Envelope`/`Payload`/`State` structs, `validate_envelope`,
        `build_event`, `validate_and_decrypt`, the two named tests),
        `crates/buzz-relay/src/handlers/ingest.rs` (`required_scope_for_kind`
        match arm, the h-tag-scoping exemption list, the
        `private_managed_agent_kind_is_owner_scoped_global_user_data` test),
        `crates/buzz-relay/src/handlers/req.rs` (`AUTHOR_ONLY_KINDS` read-gating
        at the two cited line numbers), `migrations/0033_private_managed_agent_fts.sql`,
        and `crates/buzz-relay/CHANGELOG.md`.
        done when: each path above has been opened in this worktree and its cited
        line range verified to contain the claimed text.

STEP 2  [needs 1] Write `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-pma.md`
        with front matter (`id: interfaces-nostr-buzz-nips-nip-pma`,
        `type: interfaces-events`, `status: draft` — matching the spec's own
        `draft` status — `origin: launchpad`, `audiences: [agent, developer,
        reviewer]`, `relationships: [{type: implements, target:
        corpus-template-interface}]`) and a body covering, per the issue's DoD:
        the signed outer envelope and NIP-44 v2 decrypted payload as
        inputs/messages; the built/signed event as the output; the codec's
        `Error` variants as rejection behavior; author-only read gating via
        `AUTHOR_ONLY_KINDS` plus owner-derived NIP-44 self-encryption as
        authn/authz; the `FORMAT`/`VERSION` constants and the CAS
        generation/`prev` chain as versioning and ordering/idempotency; a link to
        `docs/nips/NIP-PMA.md` as the authoritative spec; the
        `owner_self_round_trip_binds_outer_and_inner` test as the valid example
        and `wrong_owner_and_tampering_fail_closed` as the failure example; and a
        boundary/scope-and-omissions section that honestly reports the
        ingest-accepts-today vs. spec-says-MUST-reject tension as an unresolved
        gap rather than silently resolving it either way.          [needs 1]
        done when: the file exists, every DoD bullet in the issue body is
        addressed by a labeled section, and every FACT/INFERENCE evidence entry
        cites a path opened in STEP 1.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`
        from the repository root; fix any reported FAIL (not UNVERIFIED) and
        re-run until it exits 0.                              ← RUNS HERE
        done when: the command's exit status is 0 and its output names no FAIL
        for the new node.

STEP 4  [needs 3] Run `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole
        command in its own tool call and confirm it prints `OK`; only then, in a
        separate call, `git add` the new document plus this plan file and run
        `git commit -s -m "docs(corpus): document Buzz NIP-PMA interface (#1003)"`.
        Do not touch any stamp file directly and do not pass `--no-verify`.
                                                                     [needs 3]
        done when: the unittest command's last line is `OK` and `git log -1
        --name-only` on the resulting commit lists both the new document and
        this plan file.

PARALLEL: none — one document, one plan file, no independent work streams, and
the four steps are a strict evidence → draft → validate → commit chain.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
clean (UNVERIFIED notices are non-fatal and acceptable; any FAIL is not).
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` must print `OK` before the commit is attempted — that is the earned
gate stamp the commit-msg/pre-commit hooks check for. `review-adjudicate` and any
cross-model final review pass are out of scope for this single-document task and
are deferred to whatever batch/PR review process consumes this branch.

BUDGET: small — one corpus document (~150-250 lines), no runtime code changes,
no new tests. Evidence gathering is scoped to the seven files already identified
in ALREADY TRUE / STEP 1; no additional exploratory search is expected.

OPEN: whether the ingest-accepts-kind-30179-today-despite-the-spec's-"MUST
reject" tension found in STEP 1 should become its own tracked implementation or
spec-correction issue is not decided here — the issue's own "Out of scope" list
excludes "changing runtime product behavior unless a separately linked
implementation issue owns that change," so this plan reports the gap in the
node's body rather than filing or resolving it. Whether future sibling
`buzz-nips/*` interface nodes should cross-`references` each other once more of
them merge is left for whichever later pass adds the second sibling node, per
`AGENTS.md`'s own guidance to check the merge-base branch before adding an edge.

LEFT OUT: no `relationships` entry pointing at any other `buzz-nips/*` node —
none are merged on `origin/launchpad` yet, and `AGENTS.md` treats an unresolved
target as a hard validation error. No attempt to reconcile or fix the
spec-vs-ingest discrepancy in either `docs/nips/NIP-PMA.md` or the relay code —
reported as an honest, cited gap only, per this task's explicit out-of-scope
list. No coverage of the Desktop `ManagedAgentRecord` field-classification
fixture the spec itself says "does not yet depend on the Desktop type" for — out
of scope for an interface node describing the wire/relay contract, not the
desktop implementation.
