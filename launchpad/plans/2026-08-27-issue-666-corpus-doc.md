Issue #666 — task: document architecture/context/nostr-network.md
Stated size: no `Size` line -> cap: 4 steps (single hand-authored document, category: context)

ALREADY TRUE  (verified against git, not notes)
  On `origin/launchpad` tip a44cf52fc740ebebbdd671427480d14f0bce0115 (task/666-corpus-doc
    branched from it); `launchpad/docs/corpus/architecture/context/nostr-network.md` does
    not exist; `node.schema.json`, `standards/confidence.md`, `standards/decision-references.md`,
    `AGENTS.md` and `README.md` are merged, giving loaded node ids
    `corpus-standard-confidence`, `corpus-standard-decision-references`, `corpus-agents`,
    `corpus-readme` — none of which the nostr-network context is about, so no
    `relationships` edge resolves yet.

STEP 1  Gather evidence for the Nostr-network system boundary: read `NOSTR.md` (third-party
        client interop, community-as-host-domain boundary), `ARCHITECTURE.md` §1-2 (single
        relay of record, no relay-to-relay federation/gossip/replication, NIP-01 wire format,
        kind ranges), `crates/buzz-acp/README.md` (agent identity is a Nostr keypair),
        `crates/buzz-pair-relay/src/lib.rs` (NIP-AB device pairing sidecar), `crates/git-sign-nostr/README.md`
        and `crates/git-credential-nostr/README.md` (NIP-GS / NIP-98 git interop), and
        `crates/buzz-media/src/auth.rs` (Blossom BUD-11 media auth). Record anything the DoD
        implies but this pass could not verify (e.g. no evidence of live third-party-relay
        federation to confirm it is genuinely absent, not merely undocumented).
        done when: each source above has been opened and a one-line note taken naming the
        claim it will support.

STEP 2  [needs 1]  <- RUNS HERE  Write `launchpad/docs/corpus/architecture/context/nostr-network.md`:
        schema-valid front matter (`id: architecture-context-nostr-network`, `type: architecture`,
        `status: draft`, `origin: launchpad`, `audiences`, an `evidence` ledger whose first
        entry is the HEAD commit citation, no `relationships`), plus a body that (a) defines
        the system/actor boundary — Buzz-as-relay vs. the wider Nostr network, (b) names every
        directly relevant actor/system and its relationship to Buzz (third-party NIP-29/NIP-42
        clients, Buzz's own clients speaking the same wire protocol, AI agents via buzz-acp,
        the pairing sidecar, git-sign-nostr/git-credential-nostr, Blossom media, the upstream
        NIP spec repository), (c) a Mermaid diagram-as-code context view, (d) a scope section
        stating this stays at context level and does not descend into relay internals (owned
        by `ARCHITECTURE.md`) or per-NIP wire detail (owned by `NOSTR.md` and `docs/nips/`).
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 with the
        file present, and every actor named in (b) has a matching `evidence` entry.

STEP 3  [needs 2]  Self-audit the finished node against issue #666's DoD checklist line by
        line and the category-context tail (actor/relationship coverage, diagram present, no
        container/component descent), confirm every evidence entry's citation was actually
        opened in STEP 1, and confirm no second canonical document was created.
        done when: the audit is written inline in this session's notes (not committed) and
        `validate.py` still exits 0.

STEP 4  [needs 3]  Earn the verification stamp with the corpus unittest suite as the sole
        prior command, commit the plan + document, push, and open a draft PR.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        reports OK; `git commit -s` succeeds without a "no verification stamp" block; the
        branch is pushed; and `gh pr view` on the new PR shows `isDraft: true`.

PARALLEL  None. One target file, sequential steps.

GATES     Corpus validator (`validate.py`) and the corpus unittest suite, both run locally
          in this session. `review-adjudicate` and a cross-model final pass are explicitly
          deferred to the batch owner's morning review of the 47-issue overnight run — not
          run here, and the PR body says so rather than implying either ran.

BUDGET    STEP 2. The hard part is keeping the actor list at context altitude — naming who
          Buzz talks to and why, without drifting into how the relay implements the talking
          (that is `ARCHITECTURE.md`'s job, not this node's).

OPEN      Whether "the nostr network" as a title implies documenting live third-party relay
          federation. STEP 1's evidence (`ARCHITECTURE.md` §1: "no peer-to-peer event
          exchange, no gossip, no replication") says Buzz deliberately has none today — the
          node states that as the FACT it is, and the DoD's own boundary-definition bullet is
          satisfied by naming the absence, not by inventing a federation surface that does not
          exist. Left explicit in the document's body rather than silently resolved.

LEFT OUT  Any `relationships` edge — the four loaded ids are unrelated subjects; the first
          neighboring corpus node to land is the moment to revisit this, per AGENTS.md.
          Per-NIP wire-level detail (kind numbers, tag shapes, auth flows) — owned by
          `NOSTR.md`, `ARCHITECTURE.md` and `docs/nips/`; this node links them rather than
          duplicating them. Speculative future-state actors from `VISION_MESH.md` (peer
          compute sharing) — not part of today's verifiable Nostr-network boundary.
