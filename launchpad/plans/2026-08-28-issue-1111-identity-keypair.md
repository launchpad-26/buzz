Issue #1111 — task: document layers/identity/keypair.md
Stated size: no `Size` line on the issue -> cap: 5 steps (per dispatch brief;
single-documentation-file task).

ALREADY TRUE (verified against git and the worktree, not notes)
  - Worktree exists at __worktrees/task-1111-identity-keypair, branch
    task/1111-identity-keypair, HEAD == origin/launchpad ==
    338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 (git rev-parse confirms).
  - launchpad/docs/corpus/layers/identity/keypair.md does not exist yet in
    this worktree (ls reports "No such file or directory" for
    launchpad/docs/corpus/layers/ itself — the whole layers/ subtree is
    absent on origin/launchpad at this commit).
  - node.schema.json, AGENTS.md and templates/concept.md already read in
    full this session — front-matter contract, evidence-class rules, and
    the concept-node template (Diátaxis Explanation + Good Docs Concept
    template, required sections: Definition, optional Background/Visual
    aid/Comparison, Use cases, Related resources, Scope and omissions) are
    known, not assumed. This node is the pairing concept itself (the unit
    of identity), not the private-key or public-key half — those are
    sibling tasks #1112/#1113, unopened on disk in this worktree.
  - Source evidence already inspected and opened this session:
    - crates/buzz-admin/src/main.rs:78 (GenerateKey doc comment), :144-150
      (`buzz generate-key` subcommand: `Keys::generate()`, prints hex
      pubkey + secret, tells the operator to set BUZZ_PRIVATE_KEY).
    - crates/buzz-admin/src/main.rs:483-507 (relay keypair resolution:
      arg > env > ephemeral, force-republish path refuses an ephemeral key).
    - crates/buzz-cli/src/lib.rs:2026-2032 ("The keypair IS the identity —
      no tokens, no other auth." — `Keys::parse(BUZZ_PRIVATE_KEY)`).
    - crates/buzz-cli/src/client.rs:541-564 (`BuzzClient::new`/`keys()`
      holds the parsed `Keys` for the session).
    - crates/buzz-core/src/verification.rs:1-32 (`verify_event`: Schnorr
      signature + event-id-hash verification against `event.pubkey`).
    - crates/buzz-pair-relay/tests/integration.rs:89-100 (raw secp256k1
      keypair generation, x-only pubkey serialization — the layer `nostr`
      wraps).
    - Root Cargo.toml:72 (`nostr = { version = "0.44", ... }` workspace
      dependency all crates in the grep hit list consume via
      `{ workspace = true }`).
    - crates/buzz-core/src/kind.rs:4,8,10 and filter.rs:1 (NIP-01
      references already in-repo for event/kind shape, not keys
      specifically).
    - NIP-01 primary source (raw.githubusercontent.com/nostr-protocol/nips
      /master/01.md), fetched this session: "Each user has a keypair.
      Signatures, public key, and encodings are done according to the
      Schnorr signatures standard for the curve secp256k1" — the external,
      protocol-level definition Buzz's own code implements but does not
      restate in prose anywhere in-repo.

STEP 1  [independent] Confirm relationships question and the id/type choice
        in writing before drafting: enumerate origin/launchpad's corpus
        tree fresh (`git ls-tree -r --name-only origin/launchpad --
        launchpad/docs/corpus`) — expected to still show no layers/
        subtree and no sibling identity nodes — and record that `type:
        layers` is the correct node.schema.json enum value (the issue
        title's own path segment, matching PRD #607/#602's per-surface
        taxonomy) with no `relationships` entries because no target node
        exists yet.
        done when: the enumeration output and the id (`layers-identity-
        keypair`) are recorded as the first lines of Step 2's draft, not
        assumed from this plan's ALREADY TRUE section alone (that section
        predates any drafting).

STEP 2  [needs 1] Draft front matter and evidence ledger against
        templates/concept.md: id `layers-identity-keypair`, type `layers`,
        status `draft`, origin `launchpad`, audiences `agent`/`developer`/
        `reviewer`, a provenance FACT citing commit
        338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, and one evidence entry
        per substantive claim drawn from the ALREADY TRUE source list plus
        the NIP-01 fetch — classified honestly (FACT for opened
        code/spec, INFERENCE with confidence for reasoned claims such as
        "the keypair IS the identity" generalizing beyond buzz-cli's own
        comment, TEAM_KNOWLEDGE only if a claim rests on an issue/PR with
        no openable file).
        done when: every claim the body (Step 3) will make has a matching
        ledger entry, and every FACT/INFERENCE citation names a source
        actually opened this session (not a guessed path).

STEP 3  [needs 2] Write the body following templates/concept.md's required
        sections: Title + short intro, Definition (what a keypair is in
        Buzz — the secp256k1/Schnorr pair that IS an identity, no tokens
        involved — and its boundary against the private-key-only and
        public-key-only concepts owned by sibling tasks #1112/#1113),
        Use cases (CLI/admin auth, relay signing key, event
        verification), Related resources (prose links to the NIP-01
        source and to buzz-admin/buzz-cli, since no sibling corpus node
        exists yet to carry a typed `relationships` edge), and Scope and
        omissions (explicitly: this node does not cover private-key
        storage/handling or public-key-as-identifier mechanics — those
        are #1112/#1113 — and names anything expected but not verified,
        e.g. NIP-44/NIP-98 key-derived encryption is out of scope here).
        done when: launchpad/docs/corpus/layers/identity/keypair.md
        exists with complete front matter and body, and is the only
        hand-authored file changed.

STEP 4  [needs 3] Validate: run
        `python3 launchpad/project-intelligence/corpus/validate.py`
        (exit 0 required) and separately, as the sole command in its own
        tool call,
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        (OK required) — this is also the commit-gate stamp per the
        dispatch brief; do not touch any stamp file directly.
        done when: both commands are re-run after any fix and both pass
        clean in the same session as the final file content.

STEP 5  [needs 4] Self-review the finished diff against every DoD bullet
        in issue #1111 and re-open every cited source once more to
        confirm it actually supports its claim (not merely that the path
        resolves) — this is the self-review verification step, no
        `review-code` skill invoked per the dispatch brief. Then commit
        (`git commit -s`), push, and open the draft PR with the required
        body language (Closes #1111; validate.py + unittest suite passed;
        self-review only; "Draft — adjudicate/cross-model pass deferred
        to the batch owner's review before merge").
        done when: `gh pr create --draft ...` returns a PR URL, run as a
        lone Bash command with no `cd` prefix.

GATES   No `review-*` skill is invoked for this task — the dispatch brief
        specifies self-review only (Step 5), with adjudication and
        cross-model review explicitly deferred to the batch owner after
        this draft PR opens. validate.py and the corpus unittest suite
        (Step 4) are the only automated gates run here.
OPEN    Whether `references`-typed relationships to #1112/#1113 should be
        added once those sibling nodes merge is not this task's to
        decide — AGENTS.md step 9 requires a relationship target to exist
        on the branch being merged into, and neither sibling exists on
        origin/launchpad at this commit, so the answer today is none,
        revisited when a sibling lands.
LEFT OUT  Documenting private-key generation/storage/security specifics
        (owned by #1112) and public-key-as-identifier/verification
        specifics (owned by #1113) — both stay out of this node's
        Definition and are named explicitly in its Scope and omissions
        instead of being folded in, per AGENTS.md's "one node is one
        independently maintainable idea" rule. Also left out: NIP-44/
        NIP-98 encryption mechanics that consume a keypair's ECDH shared
        secret (buzz-sdk/src/nip_oa.rs) — related but a separate
        capability, not part of the keypair concept itself.
