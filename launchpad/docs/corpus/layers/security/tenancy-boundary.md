---
id: layers-security-tenancy-boundary
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "buzz-core's tenant.rs states, in its module doc under '## The fence': 'The whole multi-tenant safety story rests on one invariant from the formal model (conformance \"row zero\"): a request's community is resolved from the connection host by the server, never supplied or influenced by the client', and names TenantContext and CommunityId::from_uuid as the type-level expression of that invariant, explicitly calling the result 'a lint-and-review fence, not a compiler fence' because both are pub and a determined caller elsewhere could still call them."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "docs/multi-tenant-relay.md states the master isolation theorem, NI (Non-interference), as: 'For every reachable state and every B-scoped observation, the observed value is a function only of B-labeled state -- no high-labeled value flows into a low-labeled observation', with I1 through I5 named as the specific flows it rules out, each independently mutation-tested non-vacuous."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md"
  - statement: "The same document's System Model section names the threat this boundary exists to defend against explicitly as the confused-deputy hazard (citing Hardy 1988): 'the relay holds broad authority over a shared DB, and a client supplies an ambient name; if the relay acts on its broad authority under the client's name, the client escapes its community', and states the defense as capability discipline -- authority bound to the resolved object, never to a caller-supplied tag -- with the h tag modeled as adversary-controlled and proven not load-bearing (its own Theorem I2 / S1)."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md"
  - statement: "docs/multi-tenant-relay.md's Authorization soundness section states eight Tamarin-mechanized lemma families, S1 through S8: token confinement (S1), mint integrity (S2), signing-key non-confusion and containment (S3), audit-chain unforgeability and containment (S4), channel-less host confinement (S5), channel-bearing host/channel agreement (S6), NIP-43 admission confinement (S7), and open-community AUTH confinement (S8) -- and states its own Verification status paragraph: 'S1-S8 are machine-verified green on Tamarin 1.12.0 / Maude 3.5.1 -- the full selected run verifies all 32 lemmas in ~12s with zero analyzed failures', each paired with an exists-trace sanity lemma and a named mutation confirmed red (for example MUTATION_Use_Token_ChannelLess_Ignore_Host for S5, falsifying channelless_use_confined_to_host_community in a 13-step trace)."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md"
  - statement: "docs/spec/MultiTenantRelay.tla defines Safety as the conjunction of twelve invariants -- TypeOK, Inv_NonInterference, Inv_LabelPropagation, Inv_ReadConfinement, Inv_ResolutionFence, Inv_HostBindingFence, Inv_ChannelCommunityImmutable, Inv_AdmissionFence, Inv_AcceptedWritesPersist, Inv_MessageKeyUnique, Inv_NoTenantContextFailsClosed, Inv_ProjectionDerived, and Inv_SanitizedErrors."
    entry_class: FACT
    evidence:
      - "docs/spec/MultiTenantRelay.tla:1128-1141"
  - statement: "docs/multi-tenant-relay.md's Mechanized Verification section states that TLC, run against the finite core harness (2 communities x 4 channels, 2 message ids, 1 actor, 1 worker, 2 audit values, bounded observation set, with symmetry), 'completes exhaustively: Model checking completed. No error has been found. -- 472,530,528 states generated, 16,226,016 distinct, 0 left on queue, depth 13'."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md"
  - statement: "The same section records thirteen confirmed-red mutations (M1-M13) proving the invariants are non-vacuous, including M3 (a global id-uniqueness key instead of a community-scoped one) violating Safety at depth 3 with a cross-community existence-oracle leak, M8 (dropping the host/channel agreement fence) violating Inv_HostBindingFence by a 2-state trace, and M9 (re-keying admission from same-community to any-community) violating Inv_AdmissionFence on both a 5-state membership trace and a 4-state channel-less-read trace."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md"
  - statement: "docs/multi-tenant-relay.md's Isolation Boundary section names three declared, out-of-scope channel classes rather than treating the proof as unconditional: (C1) bandwidth-limited physical channels (buffer cache, autovacuum, planner statistics, connection-pool tail latency) -- 'We do not claim timing non-interference'; (C2) logical channels, each closed in-model or by a named axiom (the id-existence oracle, the constraint-violation error surface, the projection-rebuild path, and the unauthenticated NIP-11 surface); and (C3) historical writes surviving membership revocation -- 'We do not claim historical writes are revoked when a member is revoked.'"
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md"
  - statement: "docs/multi-tenant-relay.md's Scope and Non-Goals section states the proof deliberately does not cover liveness or performance, Postgres's own internal correctness (RLS enforcement, MVCC, ON CONFLICT semantics -- stated as axioms, not reproven), the cryptographic primitives (Schnorr/BIP-340, NIP-98 binding, hash second-preimage resistance -- the Tamarin model's equational theory, not reproven), and physical-resource isolation; it also names an explicit above-the-interface carve-out -- a client (multi-tenant UI, NIP-19 nevent share, screenshot, leaked log) that surfaces a user's own event ids from one community while the user is also a member of another is 'the client's obligation, not the relay's', closed at the interface only by the composite-index property (A-RLS-5)."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md"
  - statement: "At the recorded revision, crates/buzz-test-client/tests/conformance_multitenant.rs defines 18 #[tokio::test] functions (grep -c '#[tokio::test]'), of which 8 are stubbed via the file's own pending_lane(lane, obligation) -> ! helper, which calls todo!() and asserts nothing (grep -c 'pending_lane(' returns 9 lines, one of which is the helper's own fn definition); the file's own module doc states 'A row is todo!()-stubbed until the lane it depends on lands on the integration branch. The stub is intentional and load-bearing.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "grep -rl 'conformance_multitenant' across every file under .github/workflows/ and the repository Justfile returns no match, so neither the eight not-yet-implemented rows nor the ten already-implemented rows of that A/B isolation suite (including the passing row_zero_host_binding::unmapped_host_fails_closed_generically) run automatically anywhere in this repository's CI."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='conformance_multitenant', scope='.github/workflows/,Justfile') -> zero matches, verified 2026-08-28 against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "grep -rl for 'tlc2.TLC', 'tamarin-prover', 'MultiTenantRelay', and 'MultiTenantAuth' across every file under .github/workflows/ and the repository Justfile returns no match, so neither the TLA+ model checker nor the Tamarin prover is invoked by any automated pipeline in this repository; the exhaustive TLC run and the 32-lemma Tamarin run cited above are both artifacts of a manual, point-in-time invocation recorded in docs/multi-tenant-relay.md's own prose, not results a CI job reproduces."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='tlc2\\.TLC|tamarin-prover|MultiTenantRelay|MultiTenantAuth', scope='.github/workflows/,Justfile') -> zero matches, verified 2026-08-28 against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "docs/multi-tenant-relay.md's own Implementation Correspondence section, mapping the P-RESOLVE/I2 model obligation to code, states in its own words: 'Today there is no community layer; channel_id is the only locality' -- language that describes a pre-migration baseline the rest of the document's Abstract also uses ('Today a Buzz relay process is the security boundary ... The model proven here demotes the relay process to stateless compute and elevates a new community entity')."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md"
  - statement: "Because tenant.rs's own module doc (quoted above) names 'the formal model' as the direct source of the row-zero invariant it implements, and the three merged sibling nodes cite CommunityId, bind_community and TenantContext as already-shipped code enforcing exactly that invariant, the community-layer migration docs/multi-tenant-relay.md's Implementation Correspondence section frames as future work appears to have since landed in code; whether every one of that document's other Implementation Correspondence bullets (I1/I4's RLS backstop, C2.1's composite index, S3/S4's per-community signing key) was individually reconciled against the current shipped code, beyond the row-zero fence this node and its sibling nodes confirm, was not checked here."
    entry_class: INFERENCE
    evidence:
      - "docs/multi-tenant-relay.md"
      - "crates/buzz-core/src/tenant.rs"
    confidence: 0.55
  - statement: "Issue #1179's definition of done requires this node to state the invariant as one unambiguous property using MUST/MUST NOT only where normative, explain its scope, name enforcement points and observable failure behavior, and link at least one verification/conformance mechanism or explicitly record that verification is missing."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1179 definition of done"
  - statement: "Issue #1179 is dispatched as the security-taxonomy framing of the multi-tenant/community isolation boundary (what is at risk if it fails, what it must guarantee), deliberately distinct from the sibling task documenting the same boundary from the tenancy-taxonomy/mechanism angle (layers/tenancy/cross-community-isolation.md, issue #1188, not yet drafted at the recorded revision), and from the three already-merged architecture/principles nodes that own the runtime enforcement mechanism in detail."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "this task's own dispatch instructions, cross-checked against launchpad-26/buzz#1188 (open, no PR, node not present on origin/launchpad) and the three merged architecture/principles nodes cited in Relationships below"
relationships:
  - type: depends-on
    target: architecture-principles-community-is-security-boundary
  - type: depends-on
    target: architecture-principles-host-selects-community
  - type: references
    target: architecture-principles-fail-closed-boundaries
---

# Tenancy boundary: invariant

**No community's data, membership, audit record, or side effect may be observable,
forgeable, or actionable from a connection or request bound to a different
community, and no signal a client controls -- an `h` tag, a token's claimed
community, or a channel/host mismatch -- MUST ever cause the relay to act as
though it were bound to a different community than the one the server itself
resolved.** Stated in the formal model's own vocabulary: every reachable state's
observations satisfy non-interference (NI) with respect to community, and every
authorization decision is sound against a Dolev-Yao adversary that fully controls
the client side of the wire.

This is the same boundary the sibling node `architecture-principles-community-is-security-boundary`
documents from the runtime-code angle (the `bind_community` fence, the fail-closed
error shape, the enforcement-point table). This node states the guarantee itself
in security terms -- what the boundary must hold, what class of threat it defends
against, and what is proven versus merely implemented -- rather than re-deriving
that call-site table.

## Scope

**Applies to** every operation a resolved `TenantContext` can reach: reads (event
queries, direct-id/`#e`/`#a` lookups, channel-less feed/aux reads, search, audit
reads) and writes (event ingest, channel creation, membership admission and
revocation, workflow side effects, media, git, audit appends) across every
externally reachable surface -- WebSocket, the REST bridge, media, git smart HTTP,
webhooks, and the huddle audio path.

**Binds two independently-provable properties, not one:**

- **Isolation (non-interference).** For any two communities A and B, a B-scoped
  connection's observable outputs -- event content, EOSE cardinality, write
  acknowledgements, error messages, audit entries, the NIP-11 document -- are a
  function of B-labeled state alone. No A-labeled value is an input to anything B
  observes.
- **Authorization soundness.** No credential, signature, or forged event lets an
  actor cross a community boundary -- a token stamped for A never authorizes in B
  (S1), a channel-less operation over host A never authorizes for B even when a
  presented token claims B (S5), and a channel-bearing operation over host A on a
  B-owned channel is rejected rather than acted on as B (S6). This is the
  confused-deputy defense: the relay holds broad authority over one shared store,
  and the boundary's whole job is to stop that authority ever being exercised
  under a client-supplied name rather than the server-resolved one.

**Does not require every intermediate instruction to satisfy the boundary** --
only every externally-visible observation. A write that touches two rows under
one transaction may be momentarily inconsistent between statements without
violating the invariant, provided nothing outside the transaction observes the
intermediate state.

**Does not extend past the relay's own observational interface.** A client that
independently correlates its own ids across communities it belongs to (an NIP-19
share, a screenshot, a leaked log) is outside what the relay can close -- named
explicitly as the model's own above-the-interface carve-out, not an oversight.

## What the boundary must guarantee

Two theorem families state the guarantee precisely, and both are cited above from
`docs/multi-tenant-relay.md` directly rather than paraphrased from a summary:

1. **NI (non-interference), mechanized in TLA+.** I1 (read confinement) through I5
   (admission fence) are the specific flows NI rules out. `docs/spec/MultiTenantRelay.tla`'s
   `Safety` property conjoins twelve invariants -- type well-formedness,
   non-interference and label propagation themselves, read confinement, the
   resolution and host-binding fences, channel-immutability, the admission fence,
   write persistence and message-key uniqueness, the no-`TenantContext`-fails-open
   rule, projection derivation, and the sanitized-error alphabet.
2. **S1-S8 (authorization soundness), mechanized in Tamarin under a Dolev-Yao
   adversary.** Token confinement, mint integrity, signing-key non-confusion,
   audit-chain unforgeability, channel-less host confinement, channel-bearing
   host/channel agreement, NIP-43 admission confinement, and open-community AUTH
   confinement -- eight lemma families, 32 lemmas total.

## What is at risk if it fails

Grounded in the model's own mutation-testing evidence -- what a violation of each
theorem concretely produces, not what is merely assumed to be bad:

- **Cross-tenant read leak (NI / I1 violated).** One community's event content,
  membership, or audit entries become observable from a connection bound to
  another. The model's M3 mutation (a global `id`-uniqueness key instead of a
  community-scoped composite one) reopens exactly this as an existence-oracle
  leak, confirmed to violate `Safety` at depth 3.
- **Confused-deputy write or auth escalation (I2/S5/S6 violated).** A client
  presents a token, channel, or host combination that does not match its
  connection's resolved community, and the relay honors the client's claim
  instead of the server-resolved one. M8 (dropping the host/channel agreement
  fence) violates `Inv_HostBindingFence` in a 2-state trace; the Tamarin mutation
  `MUTATION_Use_Token_ChannelLess_Ignore_Host` falsifies S5's confinement lemma in
  a 13-step trace.
  This is the confused-deputy hazard named directly in the model's System Model
  section, and it is the sharpest security framing of this boundary: the relay's
  own broad authority, exercised under a client-supplied name.
- **Admission/membership bypass (I5/S7/S8 violated).** An actor admitted only to
  community B gains read or join capability in community A through a
  globally-scoped rather than community-scoped gate. M9 (re-keying admission from
  same-community to any-community) is confirmed to violate `Inv_AdmissionFence` on
  both a membership trace and an independent channel-less-read trace, proving the
  membership gate and the read gate are each independently load-bearing, not just
  one.
- **Signing-key or audit-chain cross-contamination (S3/S4 violated).** A
  compromised community's signing key or hash-chain state is used to forge or
  splice another community's system events or audit entries. S3 and S4's own
  containment lemmas state that compromise of one community's key or chain does
  not authorize forgery of, or a splice into, another's.
- **Token blast radius widening beyond one community (S1 violated).** A leaked or
  mis-scoped token authorizes in a community other than the one it was stamped
  for. S1's own text states the boundary honestly rather than overclaiming: "a
  leaked token authorizes within its own community (blast radius is not zero and
  we do not pretend otherwise) but never another."

**Explicitly not modeled as a violation of this boundary** -- named by the model
itself so a reader does not conflate a design choice with a defect: (C1) bandwidth
or timing side channels through shared physical resources; (C2) the four logical
channels the model closes by axiom rather than leaving open (id-existence oracle,
raw-error surface, projection rebuild, the unauthenticated NIP-11 document); and
(C3) a revoked member's historical writes, which retain their original community
label rather than being retroactively redacted. Each is a declared boundary of the
proof, not an unexamined gap.

## Enforcement today

Three tiers exist, and none of them alone gives continuous, automated assurance
that the boundary holds against the currently shipped code -- naming that
honestly is the point of this section.

1. **Runtime code: type-system, structural, and predicate tiers, owned by the
   sibling nodes.** `TenantContext`'s missing `Default`/`Deserialize`, `bind_community`'s
   fail-closed resolution, and the storage-layer requirement that a `CommunityId`
   exist before any scoped query can be built are documented in depth by
   `architecture-principles-community-is-security-boundary` and
   `architecture-principles-host-selects-community`; this node does not restate
   their enforcement-point tables. Both nodes independently record that this is a
   **lint-and-review fence, not a compiler fence** -- `TenantContext::resolved` and
   `CommunityId::from_uuid` are `pub`, so nothing but review stops a determined
   caller from misusing them. Observable failure behavior is deliberately
   generic and non-differential at the security-relevant boundary too: a
   caller who cannot get bound to a community and a caller whose cross-tenant
   override attempt is rejected both see a message no more specific than an
   unrelated ordinary failure would produce -- the sibling nodes' own
   *Observable failure behavior* sections give the exact strings; this node's
   point is that the security property (no differential response an attacker
   could use to enumerate hosts or communities) is itself part of what "sound"
   means for S1-S8 above, not a separate concern.
2. **Formal, machine-checked proof -- real, but not continuously re-run.**
   `docs/spec/MultiTenantRelay.tla`'s `Safety` property was checked exhaustively by
   TLC against a bounded core harness with zero errors found, and
   `docs/spec/MultiTenantAuth.spthy`'s 32 S1-S8 lemmas verify green under Tamarin.
   Both are genuine, reproducible results (the run commands are in
   `docs/multi-tenant-relay.md`'s own Mechanized Verification section) -- but
   neither `tlc2.TLC` nor `tamarin-prover` is invoked anywhere in this
   repository's CI or `Justfile` (independently confirmed above). A future code
   change that silently breaks the correspondence between the proof and the
   shipped implementation would not be caught by anything automated; only a human
   re-running the model checker would notice.
3. **Runtime end-to-end conformance suite -- partially built, and not run at
   all.** `crates/buzz-test-client/tests/conformance_multitenant.rs` is the suite
   designed to prove this boundary at the wire level against a live two-host
   relay. At the recorded revision, 8 of its 18 tests are `todo!()` stubs
   (independently counted above), and no `.github/workflows/` file or `Justfile`
   recipe references it at all -- so even the 10 implemented rows, passing or
   not, currently prove nothing about a deployed relay on every change.

**The honest summary.** The strongest evidence for this boundary is a real,
machine-verified formal proof; the weakest true tier for *keeping that proof
current* is convention-and-review, because nothing re-runs the model checker, and
the wire-level suite built to close that gap is itself incomplete and unwired
from CI.

## Boundary

This node does not describe:

- **The runtime enforcement mechanism's own call-site table** -- which functions
  call `bind_community`, in what order, with what exact error strings. That is
  `architecture-principles-community-is-security-boundary` and
  `architecture-principles-host-selects-community`'s canonical content, linked
  above rather than duplicated.
- **The general fail-closed pattern** this boundary is one instance of (DB-error
  handling at the pubkey-allowlist and ban-state gates, unrelated to tenancy) --
  see `architecture-principles-fail-closed-boundaries`.
- **The tenancy-taxonomy/mechanism framing of cross-community isolation** --
  `layers/tenancy/cross-community-isolation.md` (issue #1188) is dispatched as
  that sibling angle and does not exist on `origin/launchpad` at this node's
  recorded revision, so no relationship is declared to it.
- **The full residual-risk catalogue** beyond the one conformance-suite gap this
  node independently verified. `layers/security/residual-risks.md` (issue #1174)
  is dispatched for exactly that broader enumeration; its own PR (#1826) was open
  and unmerged at this node's recorded revision, so it is named here rather than
  cited or linked as a relationship target.
- **The full per-surface obligation table** (schema/index/Redis-key scoping for
  channels, search, pub/sub, media, git, audit) -- `docs/multi-tenant-conformance.md`
  owns that and is linked, not reproduced, by the sibling architecture nodes.
- **A rule about corpus document wording or a participant's obligations** -- this
  is a claim about Buzz's own runtime and proof state, true or false independent
  of any corpus document, not a normative-language or policy-shaped node.

## Relationships

- **`depends-on architecture-principles-community-is-security-boundary`.** This
  node's own security guarantee is stated in terms of the `bind_community` fence
  that node documents as enforced; if that node's claim about the fence stopped
  holding, this node's guarantee claim would stop holding with it.
- **`depends-on architecture-principles-host-selects-community`.** The same
  dependency for the row-zero host-selection mechanism specifically -- the
  server-side resolution step every isolation and authorization theorem cited
  above assumes is in place.
- **`references architecture-principles-fail-closed-boundaries`.** Supporting
  context, not a requirement: the tenancy fence is that node's flagship worked
  example of the broader fail-closed pattern, but this node's own claims do not
  depend on the other fail-closed gates (pubkey allowlist, ban-state) that node
  also documents.

Both `depends-on` targets and the `references` target were checked immediately
before finalizing this front matter (`git ls-tree -r --name-only origin/launchpad
-- launchpad/docs/corpus`, run against commit
338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5): all three ids are present. No edge is
declared to a `layers-tenancy-*` or `layers-security-residual-risks` id, because
neither exists on `origin/launchpad` at this revision.

## Scope and omissions

**This node covers** the tenancy boundary stated as a security invariant (isolation
plus authorization soundness), the threat classes it defends against with
mutation-testing evidence for each, what is formally proven and what is explicitly
declared out of scope by the proof itself, and an honest three-tier account of
enforcement today, including that the formal proof and the wire-level conformance
suite are each real but neither is continuously re-checked.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The runtime enforcement call-site table | `architecture-principles-community-is-security-boundary`, `architecture-principles-host-selects-community` |
| The general fail-closed pattern beyond this one instance | `architecture-principles-fail-closed-boundaries` |
| The tenancy-taxonomy/mechanism framing of the same boundary | `layers/tenancy/cross-community-isolation.md` (#1188, not yet drafted) |
| The full residual-risk catalogue | `layers/security/residual-risks.md` (#1174, PR #1826 open and unmerged at this revision) |
| The full per-surface obligation table | `docs/multi-tenant-conformance.md` |

**Expected but not verified when this node was written:**

- **Whether `docs/multi-tenant-relay.md`'s formal model has been reconciled
  against the current shipped code beyond the row-zero fence.** The document's
  own Implementation Correspondence section reads as a pre-migration snapshot in
  places ("Today there is no community layer"), while `tenant.rs`'s own doc
  comment names "the formal model" as the direct source of the invariant it
  implements and the sibling architecture nodes confirm that fence is shipped.
  Whether every other Implementation Correspondence bullet (the RLS backstop, the
  composite-index constraint, the per-community signing key) was individually
  re-checked against today's code is recorded above as an `INFERENCE`, not
  established as a `FACT`.
- **Whether the TLC and Tamarin runs cited in this node's ledger are current
  against the recorded revision.** Both were read from `docs/multi-tenant-relay.md`'s
  own prose, not re-executed for this node -- the run commands are recorded there
  and neither tool is available to invoke as part of this documentation task.
- **Whether any of the 10 non-stubbed rows in `conformance_multitenant.rs`
  currently pass against a live two-host relay.** No such relay was stood up for
  this node; the claim made above is narrower and independently confirmed: the
  suite, passing or not, never runs in this repository's CI.
- **Whether every row in `docs/multi-tenant-conformance.md`'s full obligation
  table beyond the row-zero fence and the identity-archive isolation obligation
  (which this node did not individually re-verify) is currently implemented.**
