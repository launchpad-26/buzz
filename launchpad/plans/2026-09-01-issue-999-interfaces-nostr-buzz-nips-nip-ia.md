# Plan: issue #999 — interfaces/nostr/buzz-nips/nip-ia.md

Issue: launchpad-26/buzz#999 (task under parent PRD/Feature #616)
Stated size: issue does not carry a Size line; task brief caps this plan at 5 steps -> cap: 5 steps

ALREADY TRUE

- `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-ia.md` does not exist on this
  branch or on `origin/launchpad` (confirmed with `test -f` before this plan was written).
  No `interfaces/` subtree exists under `launchpad/docs/corpus/` at all yet.
- The authoritative spec, `docs/nips/NIP-IA.md` (581 lines), is fully read: three event
  families (`kind:9035`/`9036` requests, `kind:8002`/`8003` deltas, `kind:13535`
  snapshot), request-borne and published-profile-attestation owner paths, test vectors,
  invalid-case tables.
- The implementation is confirmed in code, not assumed from the spec alone:
  - `crates/buzz-core/src/kind.rs:406-417` declares the five kind constants
    (`KIND_IA_ARCHIVE_REQUEST=9035`, `KIND_IA_UNARCHIVE_REQUEST=9036`,
    `KIND_IA_ARCHIVED=8002`, `KIND_IA_UNARCHIVED=8003`, `KIND_IA_ARCHIVED_LIST=13535`).
  - `crates/buzz-relay/src/handlers/identity_archive.rs` implements the relay-side
    request handler: freshness window (`enforce_freshness`, ±120s, matching the spec's
    RECOMMENDED value), single-`p`-tag/single-`-`-tag enforcement, `replaced-by`
    validation, and `determine_consent_path` (self / admin / owner).
  - Buzz's owner-of-agent implementation (`verify_owner_consent`,
    `identity_archive.rs:236-283`) requires **both** a request-borne `auth` tag on the
    9035/9036 event **and** a matching `auth` tag on the target's live `kind:0` — the
    spec frames these as two *interchangeable* paths, either sufficient alone; the code
    requires both. This is a real, cited divergence worth documenting, not a spec
    restatement.
  - `crates/buzz-relay/src/handlers/side_effects.rs` publishes the relay-signed
    `kind:8002`/`8003` deltas (`publish_nipia_archived`/`publish_nipia_unarchived`,
    ~line 3628/3656) and the `kind:13535` snapshot
    (`publish_nipia_archival_list`, ~line 3378), with a retry loop against
    concurrent-mutation races.
  - `crates/buzz-db/src/store/archived_identities.rs` persists archive state
    **community-scoped** (`(community_id, pubkey)`), not literally relay-global —
    Buzz's multi-tenant model maps the spec's "relay" onto "community" (per
    `docs/multi-tenant-conformance.md:45` and
    `crates/buzz-test-client/tests/conformance_multitenant.rs:900-911`, which is an
    `#[ignore]`d pending lane, not a currently-passing test).
  - `crates/buzz-cli/src/lib.rs:299-360` and `crates/buzz-cli/src/commands/agents.rs`
    expose `buzz agents archive|unarchive|archived` as the agent-facing surface, with
    `fetch_archived_snapshot`/`verify_archived_event` (`agents.rs:406-470`) implementing
    the client-side NIP-11-`self`-signature verification the spec requires.
  - `crates/buzz-sdk/src/builders.rs:1922-1963` builds the two request event kinds;
    `crates/buzz-sdk/src/nip_oa.rs` implements the NIP-OA `auth`-tag verification the
    owner path reuses.
- `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum has 13 members and no
  literal `interface` value; `interfaces-events` is the combined value for both
  interface- and event-kind-shaped nodes (confirmed against
  `launchpad/docs/corpus/templates/interface.md`'s own "A note on `type`" section,
  which cites parent Feature #602 for this).
- `launchpad/docs/corpus/templates/interface.md` (id `corpus-template-interface`,
  status `active`) gives the required body shape: Interface description, Operations
  table, Contract and stability, Boundary, Relationships, Scope and omissions. No
  interface-shaped instance node exists yet anywhere in the corpus — this will be the
  first.
- 100% of merged corpus nodes (checked: `AGENTS.md`, `README.md`, every
  `architecture/**`, `templates/**` node) use `origin: launchpad`; none use `upstream`,
  `cohort`, or `supporting`. This plan follows that unanimous precedent rather than
  re-deriving a novel origin classification from ADR-0003's per-claim prose (which
  governs handbook pages, a different artifact, not this schema's per-node field).
- Valid relationship targets confirmed present on `origin/launchpad` right now:
  `corpus-template-interface` (the template itself) and
  `architecture-principles-community-is-security-boundary` (the principle this node's
  community-scoping fact directly instantiates). No sibling `buzz-nips` node
  (nip-oa, nip-dv, nip-43) exists yet, so none is a valid relationship target.

STEP 1 — Draft the corpus node [independent]

Write `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-ia.md` with front matter
(`id: interfaces-nostr-buzz-nips-nip-ia`, `type: interfaces-events`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, operator, reviewer]`) and a body
following `corpus-template-interface`'s required sections: Interface description,
Operations table (each row citing a code symbol, not restating the wire format from
memory), Contract and stability (freshness window, idempotency, versioning per the
spec's replaceable-event rule), Boundary (this is not a single event-kind node — it
`references` the kinds, and it does not restate NIP-OA's own contract), Relationships
(`implements: corpus-template-interface`, `references:
architecture-principles-community-is-security-boundary`), Scope and omissions
(including the owner-of-agent both-paths-required divergence and the `#[ignore]`d
conformance test as named gaps). One valid example (self-archive after rotation) and
one failure example (self-unarchive rejected while banned, or a missing-`p`-tag
rejection) from the spec's own §Examples/§Invalid Cases, cross-checked against the
handler code's rejection paths.

<!-- RUNS HERE -->

done when: the file exists, every evidence entry cites a source actually opened during
this plan's research (no citation added without a matching `ALREADY TRUE`/read-log
entry), and no sentence restates the NIP-IA wire format without a citation to
`kind.rs`, `identity_archive.rs`, or `side_effects.rs`.

STEP 2 — Validate structurally [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root.

done when: the command exits 0 with no `FAIL` lines attributable to the new node
(pre-existing `UNVERIFIED` notices on other nodes are not this task's problem; a new
`FAIL` on an unrelated node is a finding to report, not to silently fix).

STEP 3 — Earn the commit gate [needs 2]

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`

done when: the command prints `OK`.

STEP 4 — Commit [needs 3]

In a separate tool call from Step 3's test run:
<!-- COPY -->
```
git add launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-ia.md launchpad/plans/2026-09-01-issue-999-interfaces-nostr-buzz-nips-nip-ia.md
git commit -s -m "docs(corpus): document Buzz NIP-IA interface (#999)"
```

done when: `git log -1` shows the new commit on
`task/999-interfaces-nostr-buzz-nips-nip-ia` with a `Signed-off-by` trailer, and the
commit was not forced through with `--no-verify`. If the commit is rejected for a
missing gate stamp, that is a finding to report, not something to route around.

STEP 5 — Self-review against the issue's DoD [needs 4]

Re-read the diff line by line against issue #999's Definition-of-done checklist (inputs/
messages, outputs/responses, error/rejection behavior, auth, versioning, ordering/
idempotency, spec link, valid + failure example, exactly-one-canonical-doc, evidence
discipline). Re-run `validate.py` once more to confirm it still exits 0 after any
last-minute edit.

done when: every DoD bullet is matched to a specific section/sentence in the drafted
node, and `validate.py`'s final run in this step exits 0.

PARALLEL

None of these steps are parallelizable against each other — Steps 2-5 each need the
previous step's artifact (the drafted file, then its passing validation, then its
gate-earning test run, then its commit). Step 1 itself has no dependency on anything
this plan produces, hence `[independent]`.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 (Step 2).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  must print `OK` before the commit is attempted (Step 3), run alone in its own tool
  call so its exit status is unambiguous.
- The pre-commit/pre-push hooks that fire on `git commit -s` are not to be bypassed
  with `--no-verify`; a rejection is reported, not routed around.

BUDGET

One node (~150-250 lines of Markdown), one plan file. No code changes, no test changes,
no second hand-authored canonical corpus document. Estimated 1 focused pass; this is a
documentation task with a hard single-file scope already stated in the issue's own
"Impacted components" list.

OPEN

- Whether Buzz's owner-of-agent implementation requiring *both* proof paths (rather
  than the spec's interchangeable either/or) is an intentional hardening decision or an
  unnoticed implementation gap is not this task's to resolve — the node documents the
  divergence as an observed `FACT` with citations, and does not editorialize about
  which behavior is "correct."
- Whether `conformance_multitenant.rs`'s `#[ignore]`d
  `archive_in_a_does_not_affect_b` pending lane should block calling the
  community-scoping claim a settled `FACT` versus an `INFERENCE` is a judgment call
  made during drafting (Step 1), not decided in advance here — the underlying
  `(community_id, pubkey)` schema and query-filter code are real and inspectable
  regardless of that test's pending status.

LEFT OUT

- No relationship to a nip-oa/nip-dv/nip-43 corpus node is added, because none is
  merged to `origin/launchpad` yet — adding one now would be a hard validation error
  the moment this branch's node is checked against the real merge target, per
  `AGENTS.md`'s own warning about exactly this trap.
- No change to `docs/nips/NIP-IA.md`, any `crates/` source, or any test file — this is
  a documentation-only corpus node, and the issue's own "Out of scope" list forbids
  runtime behavior changes.
- No second canonical corpus document (e.g. a standalone event-kind node for 9035/9036)
  is created; those kinds are covered here by reference/citation, not duplicated into a
  second node, per the issue's DoD bullet on atomicity.
