Issue #1105 — task: document layers/identity/device-pairing.md
Stated size: no `Size` line -> cap: 4 steps (single hand-authored document, category: layers/identity concept)

ALREADY TRUE  (verified against git, not notes)
  On `origin/launchpad` tip 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 (task/1105-identity-device-pairing
    branched from it); `launchpad/docs/corpus/layers/identity/` does not exist at all yet, so
    `launchpad/docs/corpus/layers/identity/device-pairing.md` does not exist. `git ls-tree -r
    --name-only origin/launchpad -- launchpad/docs/corpus` (schema/ excluded) loads: `AGENTS.md`
    (`corpus-agents`), `README.md` (`corpus-readme`), every `architecture/**` node (containers,
    context, deployment, flows, principles — including `architecture-context-nostr-network`,
    `architecture-containers-mobile`, `architecture-deployment-multi-relay`, all three of which
    already discuss NIP-AB/`buzz-pair-relay` in passing), and every `standards/*.md` policy node.
    No `layers`-typed node exists yet, so this task is the first of its type. Sibling identity
    tasks #1102–#1114 (actor, agent-identity, community-identity, human-identity,
    identity-archive/-invariants/-recovery/-storage, keypair, private-key, public-key,
    relay-identity) are open but none has landed a node, so no `layers-identity-*` id is
    available as a `relationships` target yet.

STEP 1  Gather evidence for the NIP-AB device-pairing mechanism: read
        `crates/buzz-core/src/pairing/NIP-AB.md` (the spec: protocol goals, message flow,
        `kind:24134`, NIP-44 v2 encryption, SAS confirmation, size/freshness limits),
        `crates/buzz-core/src/pairing/{mod.rs,session.rs,types.rs,crypto.rs,qr.rs}` (the state
        machine, message types, HKDF derivations, QR URI codec), `crates/buzz-core/src/kind.rs`
        (`KIND_PAIRING = 24134`), `crates/buzz-pair-relay/src/lib.rs` and `src/main.rs` (the
        ephemeral, loopback-only, unauthenticated sidecar relay that forwards matched events —
        no persistence, no NIP-42, bounded resources), `crates/buzz-pairing-cli/src/main.rs` and
        `README.md` (the interop-testing CLI exercising the full source/target flow), and the
        already-merged corpus mentions in `architecture/context/nostr-network.md`,
        `architecture/containers/mobile.md` and `architecture/deployment/multi-relay.md` (so the
        new node complements rather than restates their existing NIP-AB claims). Record anything
        the DoD implies but this pass cannot verify (e.g. desktop/mobile pairing UI is out of
        this node's scope and owned by the container docs).
        done when: each source above has been opened and a one-line note taken naming the claim
        it will support.

STEP 2  [needs 1]  <- RUNS HERE  Write `launchpad/docs/corpus/layers/identity/device-pairing.md`:
        schema-valid front matter (`id: layers-identity-device-pairing`, `type: layers`,
        `status: draft`, `origin: launchpad`, `audiences: [agent, developer]`, an `evidence`
        ledger whose first entry is the HEAD commit citation, `relationships` with `references`
        edges to `architecture-context-nostr-network`, `architecture-containers-mobile` and
        `architecture-deployment-multi-relay` since all three exist on `origin/launchpad` and
        already discuss this exact mechanism from their own altitude). Body follows the
        concept-template shape referenced from `launchpad/docs/corpus/templates/concept.md`
        (no `layers`-specific template exists yet): a one-sentence definition of device pairing
        as the identity-layer concept, its boundary against `keypair`/`private-key` (the secret
        being transferred, not this task) and `identity-recovery` (recovering a lost key, not
        pairing a live one) once those land, the NIP-AB protocol shape (source/target roles,
        ephemeral pairing relay, SAS out-of-band confirmation, NIP-44 encrypted payload,
        single-use/no-persistence), a Mermaid sequence diagram authored inline, use cases (adding
        a second device to an existing identity; sharing an `nsec` or NIP-46 bunker string
        without the community relay ever seeing it in the clear), and a scope-and-omissions
        section naming what is deferred to the sibling identity nodes and to the container docs.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 with the
        file present, and every substantive claim in the body has a matching `evidence` entry.

STEP 3  [needs 2]  Self-audit the finished node against issue #1105's DoD checklist line by
        line and the concept-template's required sections (definition, boundary, links, use
        cases), confirm every evidence citation in STEP 1's list was actually opened and
        supports its claim, confirm the three `relationships` targets still resolve against
        `origin/launchpad` (re-run the `git ls-tree` check, not trust STEP 2's snapshot), and
        confirm no second canonical document was created.
        done when: the audit is written inline in this session's notes (not committed) and
        `validate.py` still exits 0.

STEP 4  [needs 3]  Earn the verification stamp with the corpus unittest suite as the sole prior
        command, commit the plan + document, push, and open a draft PR.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
        -p "test_*.py"` reports OK; `git commit -s` succeeds without a "no verification stamp"
        block; the branch is pushed; and `gh pr view` on the new PR shows `isDraft: true`.

PARALLEL  None. One target file, sequential steps.

GATES     Corpus validator (`validate.py`) and the corpus unittest suite, both run locally in
          this session. `review-adjudicate` and a cross-model final pass are explicitly deferred
          to the batch owner's review — not run here, and the PR body says so rather than
          implying either ran.

BUDGET    STEP 2. The hard part is keeping this node at concept altitude — what device pairing
          *is* and why it matters — without drifting into the wire-level tightening detail
          `buzz-pair-relay/src/lib.rs`'s own doc comments already enumerate (session caps, rate
          windows, dedup TTLs), which belongs to an implementation-layer node if one is ever
          filed, not this identity-layer concept node.

OPEN      Whether `type: layers` or `type: implementation` is the better fit for a node whose
          evidence leans heavily on two crates' source. Resolved toward `layers` because the
          issue's own file path (`layers/identity/device-pairing.md`) and its parent PRD's
          identity-and-security feature scope both place it there; the node's body stays at
          concept altitude rather than cataloguing the relay's tightenings to earn that placement
          honestly, per STEP 2's BUDGET note above.

LEFT OUT  Any `relationships` edge to a sibling `layers-identity-*` node (keypair, private-key,
          identity-recovery, etc.) — none of #1102–#1114 has landed a node on `origin/launchpad`
          yet, so no such id is available as a target; the boundary against those subjects is
          stated in prose instead, per `standards/linking.md`'s guidance for a real connection
          that does not yet resolve. Desktop/mobile pairing UI walkthroughs — owned by
          `architecture/containers/{desktop,mobile}.md` and the mobile `pairing/` feature code,
          linked rather than restated. The relay's specific hardening tightenings (rate limits,
          session caps, dedup TTLs) — implementation detail for a future implementation-layer
          node, not this concept node.
