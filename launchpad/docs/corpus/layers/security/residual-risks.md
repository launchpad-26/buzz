---
id: layers-security-residual-risks
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
  - statement: "docs/remote-agents.md's Scope and Non-Goals section states, verbatim, that the specification does not cover 'Malicious-provider containment': 'A provider binary receives the agent's nsec by design -- that is its job. The protocol bounds the desktop's exposure (discovery-only resolution, output caps, secret redaction, anti-secret config validation, an explicit UI trust warning) but cannot make a hostile provider safe. Choosing to run a provider is a trust decision the UI surfaces to the user; this document does not claim otherwise.'"
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "The same Non-Goals section separately states 'Substrate security' is out of scope: 'Kubernetes RBAC, namespace isolation, and secret encryption at rest are cluster-operator concerns. The Kubernetes binding states its residual exposure (§K8s Secrets) rather than claiming isolation it does not provide.'"
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "docs/remote-agents.md's Kubernetes-binding secrets section states its own residual exposure directly: 'Residual exposure, stated: any principal with pod-exec or secret-read in the namespace can read the nsec. This is the substrate-security boundary from §Non-Goals -- the namespace is the isolation unit, and users deploying to shared namespaces accept its ambient RBAC. The in-pod narrowing that sprig's dev-MCP shim performs (strips the key from its own env, re-materializes as a 0600 keyfile for the git helpers) limits accidental leakage into subprocess environments, not hostile cluster access.'"
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "crates/buzz-test-client/tests/conformance_multitenant.rs's own module doc states it 'mirrors the obligation table in docs/multi-tenant-conformance.md one row per module' and that the A/B isolation tests 'require a running multi-tenant relay with two host mappings, so they are #[ignore] by default and selected with --ignored'; the file's own doc comment further states 'A row is todo!()-stubbed until the lane it depends on lands on the integration branch.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "At the recorded revision, crates/buzz-test-client/tests/conformance_multitenant.rs defines 18 #[tokio::test] functions, of which 8 are stubbed via the file's own pending_lane(lane, obligation) -> ! helper (which calls todo!()) rather than asserting anything -- counted directly by grep, excluding the helper's own definition line."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "One of those 8 stubs is membership_allowlist::archive_in_a_does_not_affect_b, whose #[ignore]-annotated body is exactly `pending_lane(\"buzz-auth\", \"archived_identities (community_id, pubkey) -- A's archive invisible to B\")`, naming but not exercising the cross-community identity-archive isolation obligation."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "docs/multi-tenant-conformance.md's own obligation table lists 'Identity archive requests cannot hide/archive a key in another community' as the conformance obligation for the membership/allowlist/archived-identities row, matching the wording conformance_multitenant.rs's stub names -- the obligation is designed and documented, but the row that would prove it at the wire level is the unimplemented stub above, not this design table."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md"
  - statement: "No workflow file under .github/workflows/ and no Justfile recipe references conformance_multitenant or invokes crates/buzz-test-client/tests/conformance_multitenant.rs with --ignored -- checked directly by grepping every *.yml file in .github/workflows/ and the Justfile for both strings, in contrast to four other --ignored e2e test files (e2e_persona, e2e_relay, e2e_media, and others) that .github/workflows/ci.yml does invoke explicitly."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
      - "Justfile"
  - statement: "A materially narrower version of the same cross-community archive-isolation claim IS verified by a real, executing test: crates/buzz-db/src/store/archived_identities.rs's archived_identity_state_is_community_scoped (annotated #[ignore = \"requires Postgres\"], so it runs under the Postgres-gated integration suite rather than by default) archives one pubkey in two separately created communities and asserts each community's own archive state is unaffected by the other's archive/unarchive calls -- a database-layer unit test, not the wire-level conformance-suite row the stub above names."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/archived_identities.rs"
  - statement: "desktop/src-tauri/src/managed_agents/backend_tests.rs's provider-boundary tests (including provider_deploy_refuses_mismatch_before_sending_agent_secret, provider_deploy_uses_staged_bytes_after_same_inode_source_rewrite, and provider_deploy_uses_staged_bytes_after_source_pathname_replacement) each construct their own stub provider as a local shell script rather than invoking a real buzz-backend-* binary; every test function in the file is a plain #[test] or #[tokio::test] against that stub, not against a built provider crate."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend_tests.rs"
  - statement: "desktop/tests/e2e/where-to-run-config.spec.ts, the one e2e spec file that mentions a buzz-backend-* name at all, references it only as a mocked path literal (binaryPath: \"/mock/buzz-backend-kubernetes\") inside the E2E mock Tauri bridge, not a real invoked binary."
    entry_class: FACT
    evidence:
      - "desktop/tests/e2e/where-to-run-config.spec.ts"
  - statement: "No test file under crates/buzz-test-client/tests/ or desktop/tests/e2e/ invokes a real, built buzz-backend-* provider binary end to end against a live desktop-to-provider process boundary; provider-boundary coverage found in this repository is unit-level only (a stub shell-script provider in backend_tests.rs, or buzz-backend-kubernetes's own unit tests of its pure env-building function)."
    entry_class: INFERENCE
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend_tests.rs"
      - "desktop/tests/e2e/where-to-run-config.spec.ts"
    confidence: 0.7
  - statement: "Two entries in docs/remote-agents.md's own 'Known Defects (at 28ae6cd21)' section are stale as of this node's recorded revision and are therefore not cited here as open risks: defect 5 ('The deploy path never checks protocol_version') no longer holds, because desktop/src-tauri/src/managed_agents/backend.rs's provider_deploy stages the binary once via stage_provider, calls info, validates protocol_version via validate_provider_info, and only then calls deploy on the same staged path; and defect 3's 'Security follow-through' note ('env_secrets_from_request reads only agent.env_vars') no longer holds, because that function now collects values from agent.env_vars, agent.launch.env, and agent.launch.policy_env."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs"
  - statement: "Issue #1174's Definition of Done requires this node to record residual/accepted risks and open issues without presenting proposals as implemented controls, and states this node's job is distinct from the full threat catalogue owned by a separate task."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1174 definition of done"
  - statement: "Issue #1180 ('task: document layers/security/threat-model.md', open, parent PRD #607) is the corpus task that owns the full STRIDE threat catalogue for this same security surface; this node's own task instructions state its job is 'specifically the risks that remain AFTER mitigations ... not the full threat catalogue.'"
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1180 and the #1174 task brief"
relationships:
  - type: references
    target: architecture-principles-community-is-security-boundary
---

# Security residual risks

This node records the security risks that remain **after** Buzz's existing
mitigations — known verification gaps, and risks the project's own
specifications state it has deliberately chosen not to close — rather than
attempting a full attacker-perspective catalogue of the system. That
catalogue is issue #1180's job (`layers/security/threat-model.md`, parent PRD
#607, not yet drafted); this node exists specifically so a reader can find
"what's still open" without wading through a complete STRIDE table to find
it. Every risk below was re-verified directly against source in this repository
at the recorded revision, not copied from another corpus node's prose.

## Residual risks

| Risk | Kind | Why it is residual, not mitigated | Evidence |
|---|---|---|---|
| Multi-tenant A/B isolation conformance suite is unimplemented in part and never runs in CI | Verification gap | The obligation is designed and partially unit-tested, but the wire-level conformance suite that would prove it end to end neither runs automatically nor, for several rows, exists yet | `crates/buzz-test-client/tests/conformance_multitenant.rs`, `.github/workflows/ci.yml`, `Justfile` |
| Remote-agent provider-boundary protections are verified only at the unit level | Verification gap | Every enforced property (staged-artifact identity, protocol-version gate, secret redaction, reserved-key rule) is tested against a stub shell-script provider or a pure env-building function, never a real `buzz-backend-*` binary end to end | `desktop/src-tauri/src/managed_agents/backend_tests.rs` |
| A deployed provider binary is fully trusted with the agent's live key | Accepted risk (deliberately out of scope) | `docs/remote-agents.md` states its protocol "bounds the desktop's exposure ... but cannot make a hostile provider safe," and names this a user trust decision the UI surfaces, not a property the protocol claims | `docs/remote-agents.md` |
| Kubernetes substrate security (RBAC, namespace isolation, Secret encryption at rest) is a cluster-operator concern outside the protocol | Accepted risk (deliberately out of scope) | The spec states plainly that "any principal with pod-exec or secret-read in the namespace can read the nsec" and that "users deploying to shared namespaces accept its ambient RBAC" | `docs/remote-agents.md` |

### Multi-tenant A/B isolation conformance suite

`docs/multi-tenant-conformance.md`'s obligation table records, as a design
requirement, that "identity archive requests cannot hide/archive a key in
another community" — one row among several describing what an isolated,
multi-tenant relay must guarantee once two communities share one relay
process. `crates/buzz-test-client/tests/conformance_multitenant.rs` exists to
prove that design at the wire level, one executable test per obligation row.
At the recorded revision it defines 18 `#[tokio::test]` functions; 8 of them,
including `membership_allowlist::archive_in_a_does_not_affect_b`, are
stubbed with the file's own `pending_lane(lane, obligation) -> !` helper,
which calls `todo!()` and asserts nothing. The file's own module doc names
this as deliberate and temporary — "a row is `todo!()`-stubbed until the lane
it depends on lands on the integration branch" — but at this revision that
landing has not happened for these 8 rows.

Separately, and just as materially: **no CI workflow or `Justfile` recipe
runs this suite at all**, implemented rows included. The suite requires a
live two-host relay (`RELAY_URL_A`/`RELAY_URL_B`) and is gated behind
`--ignored`; `.github/workflows/ci.yml` explicitly invokes four other
`--ignored` test files (`e2e_persona`, `e2e_relay`, `e2e_media`, and others)
by name, but never `conformance_multitenant`. So even the 10 rows that *are*
implemented — including the real, passing
`row_zero_host_binding::unmapped_host_fails_closed_generically`, which
exercises the fail-closed host-binding behavior
`architecture-principles-community-is-security-boundary` (referenced by this
node) documents as enforced — currently prove nothing about the deployed
system unless a human runs them by hand.

The cross-community archive-isolation claim specifically **is** exercised,
narrowly, by a real test: `crates/buzz-db/src/store/archived_identities.rs`'s
`archived_identity_state_is_community_scoped` archives one pubkey in two
separate communities and asserts each community's state is unaffected by the
other's. That is a database-layer unit test gated on Postgres availability
(`#[ignore = "requires Postgres"]`, so it runs under the Postgres-backed
integration suite, unlike the conformance-suite stub), not the wire-level,
full-request-path proof the conformance suite was built to provide. The
residual risk is specifically the gap between "the database enforces this"
and "the whole request path, exercised end to end against a live two-host
relay, is proven to enforce this and is proven so on every change" — the
second claim is what remains open.

### Remote-agent provider boundary: unit-level verification only

`docs/remote-agents.md` documents several real, currently-enforced
protections at the desktop-to-provider boundary: a pre-secret negotiation
gate (resolve once, stage and hash the binary, check `protocol_version`
before sending the deploy request), a reserved-key rule that prevents a
provider-controlled environment map from spoofing agent identity, and output
redaction on every code path that could echo a secret back to the desktop.
`desktop/src-tauri/src/managed_agents/backend_tests.rs` pins each of these
with a passing test — but every one of those tests exercises a local stub
shell script standing in for a provider, not a real, built
`buzz-backend-*` binary. The one E2E spec that names a provider binary at
all, `desktop/tests/e2e/where-to-run-config.spec.ts`, references it only as
a mocked path string inside the Tauri mock bridge. No end-to-end test in
this repository drives a real provider binary through discovery, staging,
`info`, and `deploy` the way `conformance_multitenant.rs` is built (when it
runs) to drive a live relay. The properties are real and test-enforced at
the unit level; whether they hold when composed together against an actual
provider process is unverified.

### Accepted risk: a deployed provider is fully trusted with the agent's key

`docs/remote-agents.md`'s own Scope and Non-Goals section states this
directly rather than leaving it implicit: "malicious-provider containment"
is out of scope by design, because "a provider binary receives the agent's
nsec by design — that is its job." The protocol narrows what a compromised
or malicious provider can do to the *desktop* (discovery is restricted to a
resolved, staged, hashed binary; `provider_config` cannot carry secret-shaped
values; provider output is redacted before being surfaced) but does not, and
by its own stated scope cannot, prevent a provider that receives the key
from misusing it once it has it. The document names this explicitly as "a
trust decision the UI surfaces to the user" rather than a property the
protocol claims to hold. This node records it as an accepted risk, not a gap
to close.

### Accepted risk: Kubernetes substrate security is a cluster-operator concern

The same Non-Goals section places "Substrate security" — Kubernetes RBAC,
namespace isolation, and Secret encryption at rest — outside the protocol's
scope, deferring to the cluster operator. The Kubernetes binding section
states its own residual exposure without hedging: "any principal with
pod-exec or secret-read in the namespace can read the nsec," and "users
deploying to shared namespaces accept its ambient RBAC." An in-pod narrowing
step (the `sprig` dev-MCP shim strips the key from its own process
environment and re-materializes it as a 0600 keyfile for git helpers) limits
*accidental* leakage into subprocess environments, but the document is
explicit that this "limits accidental leakage ... not hostile cluster
access." This node records the same acceptance the specification already
states, rather than treating it as a newly discovered gap.

## Boundary

This node does not describe:

- **The full attacker-perspective threat catalogue** for the security layer —
  scope, trust boundaries, a Data Flow Diagram, and a complete STRIDE table
  are issue #1180's job (`layers/security/threat-model.md`), not this one.
- **Mitigations already fully verified by an executing test or a structural
  guarantee** — those are the *absence* of a residual risk, and are cited only
  as contrast (e.g. the `backend_tests.rs` unit coverage this node names as
  real but narrower than end-to-end).
- **A general security-control catalog or org-wide policy.** The two accepted
  risks here are specific, project-stated scope decisions in
  `docs/remote-agents.md`, not a general "what controls exist" inventory.
- **The remaining five entries in `docs/remote-agents.md`'s "Known Defects (at
  28ae6cd21)" section** beyond the two checked and found stale above. They
  were not re-verified for this node and are not repeated here as open risks;
  a reader who needs them should re-check that section against current code
  before trusting it, per the staleness this node already found on two of its
  eight entries.
- **Provider-boundary and identity-archive design detail** beyond what
  grounds the two risks above — `layers/security/provider-boundary.md`
  (#1171) and `layers/identity/identity-archive.md` (#1107) are open,
  unmerged PRs that own that detail; this node cites the same primary
  sources those PRs cite, independently re-verified, rather than depending on
  their unmerged text.

## Relationships

- `references`: `architecture-principles-community-is-security-boundary` —
  this node cites that principle's own fail-closed host-binding design as
  supporting context for the multi-tenant conformance-suite risk above
  (the real, passing `unmapped_host_fails_closed_generically` test exercises
  the same behavior that node documents as enforced), without this node's own
  claims about test coverage depending on that node's currency.

No `depends-on` or `implements` edge is declared. Checked before deciding
that rather than assuming it: at the recorded revision, `origin/launchpad`'s
corpus tree has no `layers/security/` subtree at all — this is the first node
there — and neither `layers-security-provider-boundary` (#1171) nor
`layers-identity-identity-archive` (#1107) exists on `origin/launchpad`, only
as open, unmerged PRs (#1822 and #1812). A `relationships[].target` naming
either id today would be a hard validation error against the branch this
merges into. No template named `residual-risks` exists to `implements`
either; this node is written directly against `node.schema.json` per
`AGENTS.md`'s own fallback instruction for a subject with no matching
template yet.

## Scope and omissions

**This node covers** four concrete, re-verified security residual risks at
the recorded revision: the multi-tenant A/B isolation conformance suite's
partial non-implementation and complete absence from CI, the
remote-agent provider boundary's unit-only verification, and the two risks
`docs/remote-agents.md` itself already states it has accepted (hostile-provider
containment and Kubernetes substrate security).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full STRIDE threat catalogue for this security surface | #1180 (`layers/security/threat-model.md`), not yet drafted |
| Provider-boundary design detail beyond the two verification-gap claims above | #1171 (`layers/security/provider-boundary.md`), open PR #1822 |
| Identity-archive design detail beyond the cross-community isolation claim above | #1107 (`layers/identity/identity-archive.md`), open PR #1812 |
| The remaining six entries in `docs/remote-agents.md`'s "Known Defects" section not checked here | Not yet a filed corpus task at time of writing |
| Cross-community isolation for surfaces other than identity archive (membership, allowlist, channels, search, media) | `docs/multi-tenant-conformance.md`'s own obligation table names these as separate rows; most are also `#[ignore]`d or stubbed in `conformance_multitenant.rs` but were not individually re-verified for this node |
| Whether landing CI coverage for `conformance_multitenant.rs`, or implementing its remaining stubs, is tracked as its own task | Not confirmed to be filed as a task at time of writing; not searched exhaustively |

**Expected but not verified when this node was written:**

- **Whether every one of `conformance_multitenant.rs`'s 10 non-stubbed tests
  currently passes against a live two-host relay** was not checked — no such
  relay was stood up for this node. The claim made above is narrower: that
  the suite, passing or not, never runs anywhere in this repository's CI.
- **Whether other corpus-relevant conformance obligations outside identity
  archive and host binding are similarly gapped** (membership, allowlist,
  channel scoping, search, media) was not individually re-verified row by
  row; `docs/multi-tenant-conformance.md`'s table and the file's own row
  count suggest a similar pattern, but each row was not opened and confirmed.
- **Whether the six "Known Defects" entries not checked here are still live**
  at the recorded revision is genuinely unknown — two of the eight entries
  checked (for the claims this node needed) turned out to be stale, which is
  itself a reason not to assume the rest are current without re-checking.
