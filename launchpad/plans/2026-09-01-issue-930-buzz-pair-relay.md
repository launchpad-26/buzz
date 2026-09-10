Issue #930 — task: document implementation/crates/buzz-pair-relay.md
Stated size: no `Size` line -> single-document corpus task -> cap: 5 steps.

ALREADY TRUE  (verified against git, not notes)
  On branch `task/930-buzz-pair-relay`, based on `origin/launchpad` at
    `76a0a4ebb` ("Merge pull request #1994 from launchpad-26/rqa/restreader-changed-files"),
    working tree clean.
  `launchpad/docs/corpus/implementation/` does not exist yet on `origin/launchpad` --
    this is the first node under `implementation/`.
  `launchpad/docs/corpus/templates/implementation-reference.md` is merged and
    prescribes: a realization statement, a Target section (file path/ADR id/NIP
    document/corpus id -- state plainly if the target has no corpus node yet), an
    Implementation surface table, a Divergences section, a Verification section,
    Relationships, and Scope and omissions.
  `crates/buzz-pair-relay/Cargo.toml` describes the crate as "Ephemeral sidecar
    relay for NIP-AB device pairing handshakes"; its only source files are
    `src/lib.rs` (the relay itself, `run_server`/`Relay`/`http_service`/
    `handle_conn`), `src/main.rs` (the `buzz-pair-relay` binary entry point) and
    `tests/integration.rs` (51 `#[tokio::test]` cases, matching the count the
    2026-08-18 ecosystem audit records at `launchpad/docs/audits/audit-2026-08-18-
    full-ecosystem.md:80`).
  The spec it realizes is `crates/buzz-core/src/pairing/NIP-AB.md` (NOT
    `docs/nips/NIP-AB.md`, which does not exist -- confirmed by `ls docs/nips/`).
    That file carries no corpus node id (`git ls-tree -r --name-only HEAD --
    launchpad/docs/corpus` lists no node about it), so per `AGENTS.md` no
    `implements` edge may be declared; the target is named by its real path in
    prose instead.
  NIP-AB.md itself defines the "pairing relay" role narrowly (line 55: "Any
    NIP-01 compliant relay used to route pairing events... Relays do not need any
    special handling for this kind -- standard NIP-01 event routing is
    sufficient", line 125) -- so `buzz-pair-relay`'s extensive hardening (rate
    limits, session/delivery caps, single-filter-per-connection, exactly-one-
    subscriber-per-`#p`, structural NIP-44 envelope checks, Schnorr signature
    verification, freshness window) is additive strictness beyond the spec's
    stated minimum, not a gap against it -- a genuine, citable divergence-that-
    isn't-drift for the Divergences section.
  `crates/buzz-pair-relay/src/lib.rs`'s module doc says "Session cap -- at most 6
    accepted EVENTs per connection", but `events_attempted` (incremented at
    lib.rs:810, checked at lib.rs:784) counts every signature-verified attempt
    regardless of delivery outcome, per the code comment at lib.rs:809 ("Count all
    valid+sig-verified attempts toward the session cap") -- a second, narrower
    divergence between the crate's own doc comment and its own code, independently
    corroborated by the 2026-08-18 audit's Low-severity findings table
    (`launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md:242`).
  `crates/buzz-pair-relay/Cargo.toml` has no dependency on `buzz-core`; `KIND_PAIR
    = 24134` (lib.rs:63) duplicates `buzz_core::kind::KIND_PAIRING`
    (`crates/buzz-core/src/kind.rs:465`) as an independent literal rather than an
    import.
  Existing merged corpus nodes that genuinely discuss `buzz-pair-relay` as
    supporting context (verified by opening each, not by title match):
    `architecture-context-nostr-network` (protocol-network positioning, cites
    `crates/buzz-pair-relay/src/lib.rs` directly), `architecture-deployment-
    single-relay` (Dockerfile build inclusion), `architecture-deployment-
    kubernetes` (`pairingRelay.*` chart section), `architecture-containers-mobile`
    (the client counterpart, `PairingSocket`). All four are real `references`
    targets per `relationships.schema.json`'s directionality ("source cites target
    as supporting context; no ownership or currency dependency implied").
    `architecture-containers-relay` is NOT a fit -- `buzz-pair-relay` is
    explicitly a separate binary/process, not part of `buzz-relay`'s own
    container, per `nostr-network.md`'s own text and the Helm chart's separate
    Deployment.
  No test-strategy or verification-type corpus node exists yet to `references`
    for the Verification section; it cites the test file directly instead, as the
    template allows ("or 'none' if that is the honest answer").

STEP 1  [independent]  Gather evidence: read `crates/buzz-pair-relay/{Cargo.toml,
        src/lib.rs, src/main.rs, tests/integration.rs}`, `crates/buzz-core/src/
        pairing/NIP-AB.md`, `crates/buzz-core/src/kind.rs:458-469`,
        `crates/buzz-relay/src/handlers/ingest.rs:1802-1816` (cross-reference to
        `validate_nip44_content`), `Dockerfile:80,87,179,186`, `deploy/charts/
        buzz/templates/pairing-relay.yaml`, `deploy/charts/buzz/values.yaml:106`,
        and the four `references` target nodes above. Already done in this
        session -- STEP 1 is recorded complete at plan-write time.
        done when: every claim in the drafted document cites a path actually
        opened above, and no claim rests on inference presented as fact.

STEP 2  [needs 1]  ← RUNS HERE  Write `launchpad/docs/corpus/implementation/
        crates/buzz-pair-relay.md`: schema-valid front matter (`id:
        implementation-crates-buzz-pair-relay`, `type: implementation`, `status:
        draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`,
        `relationships: [references x4 as above]`) plus a body carrying the
        template's seven required sections (Realization statement, Target,
        Implementation surface, Divergences, Verification, Relationships, Scope
        and omissions), satisfying issue #930's Definition of Done bullets
        (implementation responsibility stated, what it does NOT own stated,
        public entry points/dependencies named, owned source paths and
        representative tests linked, no restated domain semantics that belong to
        NIP-AB.md itself).
        done when: the file exists, front matter parses, and every template
        section and every DoD bullet has a corresponding, evidenced passage.

STEP 3  [needs 2]  Validate: `python3 launchpad/project-intelligence/corpus/
        validate.py` must exit 0. If nonzero, diff against the pre-existing
        `origin/launchpad` baseline (`git stash` the new file and re-run) to
        confirm any remaining failures are the ~21 unrelated pre-existing ones,
        not new ones this node introduced.
        done when: the command exits 0, or exits nonzero with only pre-existing
        baseline failures (confirmed by the stash diff) and none from the new
        file.

STEP 4  [needs 3]  Earn the commit gate: run `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole
        command in its own tool call, confirm `OK`, then in a separate call `git
        add` the document and this plan and `git commit -s`.
        done when: the unittest run reports `OK` and `git log -1` shows the new
        commit with a `Signed-off-by:` trailer. No push, no PR -- this batch's
        integration phase handles that later.

PARALLEL  None. Single target file, strictly sequential steps.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` (must exit
          0 for this node, this session). `python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"` (must report
          `OK`) is the commit-gate stamp. `corpus-review` if reachable in-session;
          otherwise a documented careful self-review against issue #930's DoD,
          line by line.

BUDGET    STEP 2. The hard part is stating precisely what `buzz-pair-relay` does
          and does NOT realize of NIP-AB: it is the transport/relay component
          only (REQ/EVENT/CLOSE routing, kind 24134, sig verification, dedup,
          rate limiting) -- the actual pairing session state machine (offer/
          accept/sas-confirm/payload/complete, ECDH, HKDF, SAS) lives in
          `buzz-core/src/pairing/` and `buzz-pairing-cli`, not in this crate, and
          the Implementation surface table must not imply otherwise.

OPEN      Whether `buzz-pairing-cli` (issue #931, same batch, unmerged) should be
          named as a `references` target -- it is not yet a corpus node, so no
          edge can be declared regardless; the Target/Scope sections instead name
          the crate by its real path and note the sibling relationship in prose.

LEFT OUT  Editing `launchpad/docs/corpus/AGENTS.md`, the template, or any other
          existing corpus node. An `implements` edge to NIP-AB.md -- it has no
          corpus node id yet, so none is declared, per `AGENTS.md`'s explicit
          "an edge to a nonexistent id is a hard validation error, not a soft
          placeholder." Documenting `buzz-pairing-cli` in depth -- that is
          issue #931's own node, kept separate to preserve one-concept-per-node.
          Resolving the M23 loopback-vs-Helm-chart divergence noted in the
          2026-08-18 audit -- that is a deployment-topology question owned by
          the `architecture/deployment/*` nodes, out of scope for a node whose
          target is the NIP-AB protocol, not the chart.
