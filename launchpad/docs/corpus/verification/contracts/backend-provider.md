---
id: verification-contracts-backend-provider
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "docs/remote-agents.md states the desktop-to-provider pre-secret negotiation gate as normative: the deploy path must resolve the provider id once, stage the resolved binary, invoke info on the staged artifact, validate an explicit, supported protocol_version, and only then invoke deploy on the same staged artifact -- and states that a missing protocol_version is an error, never presumed to be 1, because there is no deployed provider population to grandfather."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:334-359"
      - "docs/remote-agents.md:387-409"
  - statement: "docs/remote-agents.md's Conformance section states, as one of the mandatory test cases for L2 (provider) conformance, that 'an incompatible or absent protocol_version MUST be rejected before any request carrying private_key_nsec is sent', and names this specifically as one of the review-found failure modes a conformance suite must cover."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1516-1526"
  - statement: "The desktop enforces this gate in code: PROVIDER_PROTOCOL_VERSION is a constant equal to 1, validate_provider_info rejects an info response whose protocol_version field is absent or not equal to that constant, and provider_deploy calls validate_provider_info on the staged binary's info response before it ever constructs or sends the deploy request that carries the agent's private_key_nsec."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs:11"
      - "desktop/src-tauri/src/managed_agents/backend.rs:13-65"
      - "desktop/src-tauri/src/managed_agents/backend.rs:509-533"
  - statement: "The desktop's protocol_version enforcement (validate_provider_info) takes only a generic serde_json::Value and branches on no field but protocol_version/ok/name/version/description/config_schema -- it contains no branch on provider identity or substrate -- and the two tests that exercise the gate (provider_deploy_requires_an_explicit_integer_protocol_version, provider_deploy_refuses_mismatch_before_sending_agent_secret) drive it through an arbitrary POSIX shell script stand-in (write_test_provider), not the shipped buzz-backend-kubernetes binary, so the enforcement side is written and tested as an implementation-agnostic gate rather than one coupled to any one provider's own code."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend.rs:13-65"
      - "desktop/src-tauri/src/managed_agents/backend_tests.rs:138-142"
      - "desktop/src-tauri/src/managed_agents/backend_tests.rs:300-317"
  - statement: "provider_deploy_requires_an_explicit_integer_protocol_version asserts that an info response with no protocol_version field at all causes provider_deploy to return an error containing 'missing integer protocol_version', and provider_deploy_refuses_mismatch_before_sending_agent_secret asserts that an info response declaring protocol_version 2 causes provider_deploy to return an error naming 'protocol version 2', that the provider's deploy operation is never invoked (a marker file the fake provider's deploy branch would create is asserted absent), and that the agent's nsec passed into the call never appears in the returned error string."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend_tests.rs:300-317"
      - "desktop/src-tauri/src/managed_agents/backend_tests.rs:273-298"
  - statement: "Running `cargo test --lib managed_agents::backend::tests -- --test-threads=1` from desktop/src-tauri in this worktree at the recorded revision passed all 26 tests in that module, including provider_deploy_requires_an_explicit_integer_protocol_version and provider_deploy_refuses_mismatch_before_sending_agent_secret, with 0 failures."
    entry_class: FACT
    evidence:
      - "cargo_test(--lib managed_agents::backend::tests -- --test-threads=1, cwd=desktop/src-tauri) -> running 26 tests ... test result: ok. 26 passed; 0 failed; 0 ignored"
  - statement: "buzz-backend-kubernetes, the repository's one shipped conforming backend provider, declares a PROTOCOL_VERSION constant equal to 1 and returns it as protocol_version in its info response; info_response_carries_the_contract_fields drives the actually-built provider binary over a real stdin/stdout pipe (not an in-process call) and asserts info[\"protocol_version\"] == 1 on the parsed response."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/wire.rs:11"
      - "crates/buzz-backend-kubernetes/src/wire.rs:128-140"
      - "crates/buzz-backend-kubernetes/tests/wire_fixtures.rs:97-125"
  - statement: "Running `cargo test -p buzz-backend-kubernetes --test wire_fixtures` in this worktree at the recorded revision passed all 4 tests in that file, including info_response_carries_the_contract_fields, with 0 failures."
    entry_class: FACT
    evidence:
      - "cargo_test(-p buzz-backend-kubernetes --test wire_fixtures) -> running 4 tests ... test result: ok. 4 passed; 0 failed; 0 ignored"
  - statement: "Neither provider_deploy_requires_an_explicit_integer_protocol_version, provider_deploy_refuses_mismatch_before_sending_agent_secret, nor info_response_carries_the_contract_fields carries a #[ignore] attribute or any infrastructure-gated cfg beyond provider_deploy_requires_an_explicit_integer_protocol_version and provider_deploy_refuses_mismatch_before_sending_agent_secret being #[cfg(unix)] (they spawn a POSIX shell script)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/backend_tests.rs:300-301"
      - "desktop/src-tauri/src/managed_agents/backend_tests.rs:273-274"
      - "crates/buzz-backend-kubernetes/tests/wire_fixtures.rs:97-98"
  - statement: "The desktop-side test module runs in CI unconditionally (subject only to a path filter on desktop/rust changes, not to an ignore flag or live infrastructure): the desktop-core job's 'Desktop Tauri tests' step runs `just desktop-tauri-test`, which is `cd desktop/src-tauri && cargo test --workspace`, and that job's if-condition gates on desktop/rust path changes, matching CI's own paths-filter."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:148-153"
      - ".github/workflows/ci.yml:213-217"
      - "Justfile:223-225"
  - statement: "The kubernetes-provider-side test runs in CI unconditionally under the same kind of path filter: the unit-tests job's 'Unit tests' step runs `just test-unit`, whose body explicitly enumerates `cargo nextest run -p buzz-backend-kubernetes` (a plain `cargo test --workspace` at the repository root does not reach this crate's tests, which is why the recipe calls it out by name), and `cargo nextest run -p <crate>` runs every test target in that crate, including the tests/wire_fixtures.rs integration binary, not only --lib."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:125-142"
      - "Justfile:349-352"
  - statement: "docs/remote-agents.md's own 'Known Defects (at 28ae6cd21)' section still lists, as Known Defect 5, that 'the deploy path never checks protocol_version'; the already-merged sibling corpus node layers-compute-backend-provider establishes that this is stale documentation rather than current behavior, because the staging-and-negotiation gate this node's obligation describes was added in a later commit that postdates the pinned defect list and was never folded back into it."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1636-1641"
      - "launchpad/docs/corpus/layers/compute/backend-provider.md"
  - statement: "This node's task (#1358) requires the obligation to be stated as one precise, testable sentence describing what any backend provider implementation must guarantee to be conformant, requires naming the verifying test(s) exactly, requires an honestly stated enforcement status, and requires a limits section naming what the verifying tests do and do not prove; those structural requirements come from the test-contract template (launchpad/docs/corpus/templates/test-contract.md), which this node follows."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1358 definition of done, applying launchpad/docs/corpus/templates/test-contract.md's Required sections"
relationships:
  - type: implements
    target: corpus-template-test-contract
  - type: references
    target: layers-compute-backend-provider
  - type: references
    target: layers-compute-provider-model
  - type: references
    target: layers-compute-kubernetes-provider
---

# Backend provider protocol-version gate — test contract

## Purpose and boundary

This node documents exactly one testable obligation of Buzz's backend-provider
protocol (`docs/remote-agents.md`): the desktop's pre-secret negotiation gate on
a provider's declared `protocol_version`. It covers that obligation only — not
the staging/same-bytes identity guarantee the same gate also provides, not
`provider_config`'s secret-key rejection, and not the Kubernetes binding's
reconciliation loop. Those are distinct, separately testable obligations; see
*Scope and omissions*.

## Obligation

> A backend provider's `info` response MUST declare an explicit integer
> `protocol_version` equal to the value the desktop currently supports (`1`);
> the desktop MUST reject the provider — and MUST NOT construct or send a
> `deploy` request, which carries the agent's private key
> (`private_key_nsec`) — whenever `protocol_version` is absent, non-integer,
> or does not equal that value.

This is `docs/remote-agents.md`'s own normative language, restated as one
sentence: an incompatible or absent `protocol_version` must be rejected before
any request carrying `private_key_nsec` is sent. It binds both sides of the
protocol — a conformant provider declares its version truthfully; a
conformant desktop enforces the check before secrets cross the boundary — but
this node's verifying tests (below) exercise the desktop's enforcement
directly, and the one shipped provider's compliance with the declaration half.

## Verifying test(s)

- `desktop/src-tauri/src/managed_agents/backend_tests.rs` —
  `managed_agents::backend::tests::provider_deploy_requires_an_explicit_integer_protocol_version`
  — asserts that an `info` response carrying no `protocol_version` field at
  all causes `provider_deploy` to fail with an error containing "missing
  integer protocol_version", before any `deploy` request is built.
- `desktop/src-tauri/src/managed_agents/backend_tests.rs` —
  `managed_agents::backend::tests::provider_deploy_refuses_mismatch_before_sending_agent_secret`
  — asserts that an `info` response declaring `protocol_version: 2` causes
  `provider_deploy` to fail with an error naming "protocol version 2", that
  the fake provider's `deploy` branch (which would leave a marker file) is
  never reached, and that the agent's `nsec` passed into the call never
  appears in the returned error string.
- `crates/buzz-backend-kubernetes/tests/wire_fixtures.rs` —
  `info_response_carries_the_contract_fields` — drives the actually-built
  `buzz-backend-kubernetes` binary over a real stdin/stdout pipe and asserts
  its `info` response's `protocol_version` field equals `1`, i.e. that the
  repository's one shipped provider satisfies the declaration half of the
  obligation.

Both desktop-side tests exercise the enforcement half against a generic
POSIX-shell stand-in provider (`write_test_provider`), not against
`buzz-backend-kubernetes` — `validate_provider_info`, the function under test,
takes a plain JSON value and branches on no provider-specific field, so the
enforcement side is verified as implementation-agnostic rather than coupled
to the one real provider that happens to exist in this repository.

## How to run it

The desktop crate's build script requires sidecar binary stubs to exist
before it will compile at all (`resource path
"binaries/buzz-acp-<target-triple>" doesn't exist` otherwise); create them
first, or use the `just` recipe that does it automatically:

```bash
just _ensure-sidecar-stubs   # or: just desktop-tauri-test, which depends on it

cd desktop/src-tauri
cargo test --lib managed_agents::backend::tests::provider_deploy_requires_an_explicit_integer_protocol_version
cargo test --lib managed_agents::backend::tests::provider_deploy_refuses_mismatch_before_sending_agent_secret
```

These two tests spawn a real child process per case and are `#[cfg(unix)]`
only; on Windows CI (`windows-rust`) `cargo test --manifest-path
desktop/src-tauri/Cargo.toml` still compiles them out rather than running
them.

```bash
cargo test -p buzz-backend-kubernetes --test wire_fixtures info_response_carries_the_contract_fields
```

This second command needs no cluster: the binary is invoked with
`KUBECONFIG` pointed at a nonexistent path, and `info` never contacts a
cluster.

## Current enforcement status

**Verified.** All three tests exist, run unconditionally in CI with no
`#[ignore]` and no live-infrastructure dependency, and passed when actually
executed against this node's recorded revision (see the ledger's two
tool-result entries). The desktop-side tests run in CI as part of the
`desktop-core` job's "Desktop Tauri tests" step (`just desktop-tauri-test`);
the kubernetes-provider-side test runs in CI as part of the `unit-tests` job's
"Unit tests" step (`just test-unit`, which explicitly enumerates `cargo
nextest run -p buzz-backend-kubernetes` because nothing else in CI runs a
plain `cargo test --workspace` at the repository root). Both jobs are gated
only by a path filter on desktop/rust changes, matching CI's own
paths-filter, not by an infrastructure or ignore condition.

## Limits

What these tests establish, and no more:

- **They prove the desktop rejects two specific malformed declarations**: a
  wholly absent `protocol_version`, and an explicit integer value (`2`) that
  does not match. They do not carry a dedicated case for a declared but
  non-integer value (e.g. `protocol_version: "1"` as a string, or a float) —
  `validate_provider_info`'s `.as_u64()` coercion takes the same "missing"
  branch for that input by construction, but no named test pins that specific
  shape.
- **They prove the enforcement side is implementation-agnostic**, because the
  stand-in provider is an arbitrary shell script, not because a second real
  `buzz-backend-<id>` binary besides `buzz-backend-kubernetes` was located and
  tested against this gate. No such second binary was found in this
  repository at the recorded revision.
- **`info_response_carries_the_contract_fields` proves the one shipped
  provider declares the correct value**, not that a provider could ever
  legitimately declare a different one and be accepted, and not that a future
  protocol version bump on the desktop side would be handled gracefully —
  that is a migration scenario this obligation's tests do not exercise.
- **They do not prove the staging/same-bytes guarantee** that the same
  pre-secret gate also provides (that `deploy` runs the exact bytes that
  answered `info`) — that is a related but distinct obligation, covered by
  different tests in the same file (`provider_deploy_negotiates_and_deploys_the_same_staged_bytes`
  and the two `..._uses_staged_bytes_after_..._rewrite`/`..._replacement`
  tests), out of scope for this node.
- **A parallel-execution note, not a defect finding.** Running the desktop
  module's tests with this environment's default thread count
  (`--test-threads=4`, several threads each spawning shell-script providers
  into `/tmp`) produced one transient `Text file busy (os error 26)` spawn
  failure in `provider_deploy_requires_an_explicit_integer_protocol_version`,
  which did not reproduce on a `--test-threads=1` rerun (used for the FACT
  above). This looks like filesystem contention specific to this sandboxed
  worktree rather than a defect in the obligation being tested, and was not
  investigated further; whether GitHub Actions' own runners exhibit it under
  their default thread count was not checked here.

## Scope and omissions

**This node covers** the protocol-version pre-secret negotiation gate only,
as one obligation binding both a conformant provider (declare truthfully) and
the desktop (enforce before sending secrets), the three tests that verify it,
how to run them, and their honestly-stated enforcement status.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The staging/same-bytes identity guarantee of the same pre-secret gate | `docs/remote-agents.md` §Discovery; tested by `provider_deploy_negotiates_and_deploys_the_same_staged_bytes` and the two staged-bytes-after-rewrite/replacement tests in the same file — not filed as its own corpus task as of this writing |
| `provider_config`'s secret-shaped-key rejection (I2) | `docs/remote-agents.md` §Provider Protocol; `validate_provider_config` and its own tests in `backend_tests.rs` — not filed as its own corpus task as of this writing |
| The full [L1]/[L2]/[L3] conformance lists beyond this one [L2] item | `docs/remote-agents.md` §Conformance |
| The Kubernetes binding's reconciliation-loop obligations (I4) | `layers-compute-kubernetes-provider`; `docs/remote-agents.md` §Deploy State Machine |
| What a backend provider is, as a concept | `layers-compute-backend-provider` |
| The provider model's full abstract contract | `layers-compute-provider-model` |
| Whether any third-party, non-Kubernetes `buzz-backend-<id>` binary exists and conforms | Not established; none was located in this repository at the recorded revision |

**Expected but not verified when this node was written:**

- **Whether CI's own default-threaded test run is subject to the same
  transient spawn race** noted in *Limits* was not checked — only a local
  `--test-threads=1` run was used as this node's passing-test evidence.
- **Whether `cargo nextest run -p buzz-backend-kubernetes`, as CI actually
  invokes it, produces the same result as the plain `cargo test -p
  buzz-backend-kubernetes --test wire_fixtures` run performed here** was
  assumed rather than checked directly — `cargo-nextest` was not available in
  this authoring environment.
- **Whether a declared-but-non-integer `protocol_version` (a string, a
  float) is exercised by any test** was checked and found absent, named above
  as a limit rather than silently left out.
