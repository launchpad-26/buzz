---
id: governance-compatibility-policy
type: governance
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "The repository's clearest compatibility rule is stated in CONTRIBUTING.md's Architecture Overview as prose: 'Event kinds are the only switch. Every action in the system -- a message, a reaction, a workflow step, a canvas update -- is a Nostr event with a kind integer. Adding a new feature means defining a new kind. No breaking changes to existing clients.'"
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "The same rule is restated in two other top-level documents in different words: ARCHITECTURE.md says 'New feature = new kind number = zero breaking changes to existing clients', and VISION.md says 'New message type? New kind integer. Zero breaking changes.'"
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
      - "VISION.md"
  - statement: "The only test in kind.rs bearing on kind-number stability is no_duplicate_kind_values, which inserts every element of ALL_KINDS into a HashSet and asserts no duplicate; it proves no two entries of that array share a value and proves nothing about whether an existing kind number is ever changed, removed or reused."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "ALL_KINDS is documented as 'All registered kind constants -- used for duplicate detection and iteration', but three declared constants are absent from it -- KIND_AUTH (22242), KIND_NOSTR_IDENTITY_BINDING (24243) and KIND_PUSH_LEASE (30350) -- so the duplicate check does not cover them; each is documented in kind.rs as ephemeral or never stored, though KIND_BLOSSOM_AUTH (24242) is likewise documented as 'not stored' and is present in the array."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "declared_kind_constants_absent_from_all_kinds(file='crates/buzz-core/src/kind.rs', revision='aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90') -> KIND_AUTH, KIND_NOSTR_IDENTITY_BINDING, KIND_PUSH_LEASE; 129 declared constants, 126 array entries"
  - statement: "The kind registry exists in three hand-maintained copies -- crates/buzz-core/src/kind.rs (129 declared constants), desktop/src/shared/constants/kinds.ts, and mobile/lib/shared/relay/nostr_models.dart -- and the only stated coupling is a Dart doc comment reading 'Keep in sync with `desktop/src/shared/constants/kinds.ts`'."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/nostr_models.dart"
      - "desktop/src/shared/constants/kinds.ts"
      - "crates/buzz-core/src/kind.rs"
  - statement: "No check in the repository compares the Rust, TypeScript and Dart kind registries against each other: a search across .mjs, .js, .ts, .rs, .dart, the Justfile and .github/workflows for a sync, drift, parity or check reference to kind.rs, kinds.ts or nostr_models returns only that Dart comment, and Justfile's aggregate `check` recipe lists fmt-check, clippy, desktop-check, desktop-tauri-fmt-check, desktop-tauri-clippy, web-check, mobile-check, security-review-check and file-size-check with no kind-registry lane among them."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "mobile/lib/shared/relay/nostr_models.dart"
  - statement: "The relay's advertised NIP surface is the static list SUPPORTED_NIPS = &[1, 2, 10, 11, 16, 17, 23, 25, 29, 33, 38, 42, 50, 56] in nip11.rs, with NIP-43 held out of the static list and appended by RelayInfo::build only when membership enforcement is enabled and a stable signing key exists."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "The tests over SUPPORTED_NIPS pin individual memberships (23 and 33, 38, 56), assert the list is sorted, and assert NIP-43 is absent from the static list; no test asserts the list's full contents, so removing an entry that is not individually pinned -- 1, 2, 10, 11, 16, 17, 25, 29, 42 or 50 -- breaks no test in that module."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "Forward-compatibility rules in this repository are written per-specification rather than centrally: NIP-AP states 'Unknown fields MUST be ignored by readers (forward compatibility)', NIP-AM requires readers to ignore unknown fields, NIP-RS says unknown top-level keys SHOULD be ignored and carries its own Backwards Compatibility section, and NIP-AO requires clients to ignore events with unrecognized `frame` values."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AP.md"
      - "docs/nips/NIP-AM.md"
      - "docs/nips/NIP-RS.md"
      - "docs/nips/NIP-AO.md"
  - statement: "The mesh wire contract is the one surface in the repository declared frozen in its own source: crates/buzz-relay-mesh/src/wire.rs opens 'The mesh wire contract -- FROZEN surface', carries ALPN = b\"buzz/mesh/1\" with the note that 'Version bumps get a new ALPN so old and new pods never half-speak to each other during a rolling deploy', and defines WIRE_VERSION: u8 = 1 as the first byte of every frame with receivers required to reject unknown versions loudly."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/wire.rs"
  - statement: "The mesh wire contract names its own enforcement as a social one: 'Changes here require a post in the mesh thread before the edit'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/wire.rs"
  - statement: "The broker protocol explicitly declines a compatibility affordance rather than granting one: BROKER_PROTOCOL_VERSION is 1 and its doc comment states 'There is no \"absent means 1\" compatibility rule: the protocol is unshipped, so protocolVersion is required and an unknown value is rejected outright.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/broker/mod.rs"
  - statement: "The NIP-AB pairing protocol takes the opposite approach for the same kind of field, defaulting its `v` parameter to 1 when absent, expressly for backward compatibility."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md"
  - statement: "The relay's generic Nostr HTTP bridge endpoints carry no version segment; the only versioned HTTP paths found in buzz-relay are the admin API under /api/admin/v1/ and the external push-gateway delivery URL /v1/deliveries/apns, which is an outbound URL the relay calls rather than a surface it serves."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/auth.rs"
      - "crates/buzz-relay/src/config.rs"
  - statement: "The buzz-cli exit-code contract is implemented once, in exit_code in crates/buzz-cli/src/error.rs, which maps Usage and NotFound to 1, Network and DeliveryUnknown to 2, Relay{status} to 3 when the status is 401 or 403 and to 2 otherwise, Auth and Key to 3, Conflict to 5, and Other to 4."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
  - statement: "No test asserts that mapping: a search for the identifier exit_code across crates/ and desktop/src-tauri/src finds it in buzz-cli only at its definition in error.rs and its single call site in lib.rs, with the other matches belonging to buzz-persona's unrelated Report::exit_code and to last_exit_code process-status fields."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
      - "crates/buzz-cli/src/lib.rs"
      - "grep_identifier(name='exit_code', scope='crates/ and desktop/src-tauri/src', include='*.rs', revision='aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90') -> no test asserts buzz_cli::error::exit_code; the buzz-cli matches are its definition in error.rs and its single call site in lib.rs, and every other match is buzz-persona's Report::exit_code or a last_exit_code process-status field"
  - statement: "The repository's own 2026-08-18 ecosystem audit already recorded this as finding M7: 'buzz-cli's documented exit-code contract has zero direct test coverage ... no test asserts each CliError variant maps to its documented exit code (0/1/2/3/4/5) -- a future reordering would compile and pass every existing test while silently breaking the contract agent harnesses branch on.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md"
  - statement: "The exit-code contract is restated in four hand-maintained prose copies that disagree about code 1: error.rs's own doc comment says '1=user/not-found', desktop/src-tauri/src/managed_agents/nest_skill.md says '1 = input/not-found', while AGENTS.md says '1=input error' and crates/buzz-cli/README.md says '1=user error' -- the latter two omitting the NotFound case the code maps to 1."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
      - "desktop/src-tauri/src/managed_agents/nest_skill.md"
      - "AGENTS.md"
      - "crates/buzz-cli/README.md"
  - statement: "A second binary in the same repository, buzz-admin, documents an incompatible exit-code scheme under the same vocabulary in NOSTR.md -- 1 validation error, 2 not found, 3 cannot remove relay owner, 4 role mismatch, 5 DB/Redis/internal error -- so 'exit code 5' means a write conflict in buzz-cli and an internal error in buzz-admin."
    entry_class: FACT
    evidence:
      - "NOSTR.md"
      - "crates/buzz-cli/src/error.rs"
  - statement: "The workspace declares [workspace.package] version = \"0.1.0\", but not every member inherits it: crates/buzz-relay/Cargo.toml sets version = \"0.2.1\" literally, and crates/buzz-persona, crates/sprig and examples/countdown-bot each hardcode \"0.1.0\" rather than using version.workspace = true."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
      - "crates/buzz-relay/Cargo.toml"
      - "crates/buzz-persona/Cargo.toml"
      - "crates/sprig/Cargo.toml"
      - "examples/countdown-bot/Cargo.toml"
  - statement: "Two workspace members set publish = false -- crates/git-sign-nostr, annotated 'internal workspace tool, not published to crates.io', and examples/countdown-bot -- and no other member manifest sets the key in either direction."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/Cargo.toml"
      - "examples/countdown-bot/Cargo.toml"
  - statement: "No workflow in .github/workflows runs an API-compatibility tool such as cargo-semver-checks or cargo-public-api; every match for 'semver' across those workflows is a release-time check that a supplied version string parses as semver, or a docker/metadata-action tag pattern."
    entry_class: FACT
    evidence:
      - ".github/workflows/release.yml"
      - ".github/workflows/docker.yml"
      - ".github/workflows/signed-macos-canary.yml"
      - ".github/workflows/helm-chart.yml"
  - statement: "RELEASING.md states that the three release lanes 'version independently', and names one version authority per lane: desktop/package.json and its synchronized manifests for desktop, crates/buzz-relay/Cargo.toml for the relay, and the exact mobile-vX.Y.Z-rc.N remote tag for mobile."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "The desktop app's package.json and src-tauri/Cargo.toml both carry version 0.5.20, while mobile/pubspec.yaml carries the placeholder 0.0.0+1, consistent with RELEASING.md deriving the mobile version from the release tag rather than the manifest."
    entry_class: FACT
    evidence:
      - "desktop/package.json"
      - "desktop/src-tauri/Cargo.toml"
      - "mobile/pubspec.yaml"
      - "RELEASING.md"
  - statement: "RELEASING.md contains no occurrence of the words semver, semantic version, major or minor, so it prescribes no meaning for a version-number increment on any of the three lanes; the one compatibility statement it does make is about a build platform, that the Linux release job builds inside an ubuntu:22.04 container 'for broad GLIBC compatibility'."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "The migrations directory holds 40 .sql files and no down migration of any kind, and they are embedded into the binary by a single static sqlx::migrate!(\"../../migrations\") in buzz-db's migration runner."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
      - "count_migration_files(dir='migrations/', revision='aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90') -> 40 .sql files, 0 filenames containing 'down' in any case"
  - statement: "Migration immutability is treated as binding in buzz-db's own tests, which state that 0007 and 0008 'may already be recorded by a running relay and their sqlx checksums are immutable' and refuse to fold later migrations into 0001 because 'folding would change 0001's checksum and break brownfield' deployments."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "The repository's 2026-08-18 ecosystem audit records 'no down-migration convention anywhere' as deliberate, describing it as a forward-only policy, and classifies it among findings that are accepted rather than defects."
    entry_class: FACT
    evidence:
      - "launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md"
  - statement: "The one explicitly written, dated compatibility policy in the repository governs the corpus schema rather than the product: launchpad/docs/corpus/schema/COMPATIBILITY.md declares that removing a field, removing an enum value or narrowing a type is breaking, requires in the same pull request a dated history entry and a re-validation pass of every existing corpus node, and states that additive changes are not breaking."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/COMPATIBILITY.md"
  - statement: "crates/buzz-conformance is a trace-replay checker for the TLA+ specification docs/spec/MultiTenantRelay.tla and describes itself as not a proof -- 'Trace conformance only checks executions you ran' -- so despite its name it establishes nothing about compatibility between versions."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/lib.rs"
  - statement: "Nothing automated checks a corpus node's prose: validate.py's _load_frontmatter splits a node's text on the frontmatter delimiter into a variable named _body that appears exactly once in the whole module -- at that split -- and the function returns only the parsed frontmatter, so the body is discarded before any check runs."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The corpus already carries a node for the additive-kinds principle, architecture-principles-event-driven-extension, citing the same CONTRIBUTING.md sentence, so this node links to it rather than restating the principle."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/event-driven-extension.md"
  - statement: "The corpus already carries a node for the CLI container, architecture-containers-cli, which records the CliError-to-exit-code mapping as part of describing that container."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/cli.md"
  - statement: "This repository already binds itself to RFC 2119's requirement-level definitions in its own specifications: docs/nips/NIP-DV.md and docs/nips/NIP-PL.md each state 'This document uses MUST, MUST NOT, SHOULD, SHOULD NOT, MAY, and RECOMMENDED as defined in RFC 2119.'"
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-DV.md"
      - "docs/nips/NIP-PL.md"
  - statement: "Issue #908's definition of done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and an exception/escalation process, and link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#908 definition of done"
  - statement: "Issue #908's definition of done requires that the node represent one independently maintainable knowledge node and that any newly discovered second concept be filed as a separate task rather than folded in."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#908 definition of done"
  - statement: "Sibling issue #911 owns launchpad/docs/corpus/governance/deprecation-policy.md, covering how a surface is removed, which is why this node is scoped to what is guaranteed while a surface exists."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#908 task assignment naming #911 as the sibling boundary"
  - statement: "This repository has no single compatibility policy: what exists is one prose principle covering event kinds, one written policy scoped to the corpus schema, and a set of per-surface conventions stated in source doc comments, with no document that states a compatibility guarantee across surfaces."
    entry_class: INFERENCE
    evidence:
      - "CONTRIBUTING.md"
      - "RELEASING.md"
      - "launchpad/docs/corpus/schema/COMPATIBILITY.md"
      - "crates/buzz-relay-mesh/src/wire.rs"
      - "crates/buzz-sdk/src/broker/mod.rs"
    confidence: 0.8
  - statement: "The additive-kinds principle is a design property of the dispatch mechanism rather than an enforced guarantee: nothing in the repository prevents an existing kind's number, tag shape or content schema from changing, and the only mechanical check in kind.rs is a duplicate-value assertion over a hand-maintained array."
    entry_class: INFERENCE
    evidence:
      - "CONTRIBUTING.md"
      - "crates/buzz-core/src/kind.rs"
    confidence: 0.85
  - statement: "A guarantee restated in prose copies with no single generating source is the shape most likely to drift, which is what the four disagreeing copies of the CLI exit-code contract and the three hand-maintained kind registries both exhibit."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-cli/src/error.rs"
      - "AGENTS.md"
      - "crates/buzz-cli/README.md"
      - "desktop/src-tauri/src/managed_agents/nest_skill.md"
      - "mobile/lib/shared/relay/nostr_models.dart"
    confidence: 0.75
relationships:
  - type: depends-on
    target: corpus-agents
  - type: references
    target: architecture-principles-event-driven-extension
  - type: references
    target: architecture-containers-cli
---

# Policy: compatibility

What this repository guarantees about a surface staying usable across changes,
which surfaces carry such a guarantee, and what actually enforces each one. It
is written for anyone about to change a shared surface — an event kind, a wire
format, a CLI contract, a schema, a migration — and for a reviewer deciding
whether a change is safe.

**The ground truth first, because it changes how everything below reads: there
is no repository-wide compatibility policy.** What exists is one prose principle
about event kinds, one written and dated policy scoped to the documentation
corpus schema, and a scattering of per-surface conventions stated in source doc
comments. Several surfaces carry no rule at all. This node records what is
there, with evidence, and names the absences as gaps. **It does not invent a
policy to fill them** — proposing one is a decision for the people who own those
surfaces, not a side effect of documenting them.

## Scope and authority

**This node governs** how a compatibility guarantee is described, evidenced and
reviewed in this repository: which surfaces are known to carry one, what each
one actually promises, what enforces it, and what a person changing such a
surface must establish before the change lands. It covers what is guaranteed
about a surface **while it exists**.

**It does not cover** how a surface is removed once it is no longer wanted —
deprecation windows, migration paths, sunset notices. That is sibling
`governance/deprecation-policy.md` (#911). It also does not cover product
behaviour on any surface, which the capability and interface nodes own, nor the
corpus's own node lifecycle, which `corpus-standard-deprecation` owns.

**Its authority is derived, and thinner than it looks.** This node has no
authority to create a compatibility guarantee. Its MUST section binds only the
*documentation and review* of compatibility claims — authority the corpus
already holds through `AGENTS.md` and the review that gates every corpus change.
Where a MUST below reads like a rule about code, read it again: each one is a
rule about what an author must establish or state, not a promise the product
makes.

**Precedence.** Where this node and the source it cites disagree, **the source
wins** and this node has drifted. Where it and an accepted ADR disagree about
authorized behaviour, **the ADR wins**. Where it and a surface's own
specification disagree about that surface — a NIP under `docs/nips/`, the mesh
wire contract, `COMPATIBILITY.md` for the corpus schema — **the specification
wins**, because it is the more specific rule written with the surface in front
of it.

| For | Read |
|---|---|
| The additive-kinds design principle itself | `architecture-principles-event-driven-extension` |
| How to add an event kind, step by step | `CONTRIBUTING.md` § How to Add a New Event Kind |
| The CLI's own container description and error mapping | `architecture-containers-cli` |
| The corpus schema's compatibility rule | `launchpad/docs/corpus/schema/COMPATIBILITY.md` |
| Per-NIP forward-compatibility rules | the individual specification under `docs/nips/` |
| The mesh wire contract | `crates/buzz-relay-mesh/src/wire.rs` |
| Release lanes and version authorities | `RELEASING.md` |
| Creating, updating and retiring a corpus node | `launchpad/docs/corpus/AGENTS.md` |

## Industry model this node adapts

**RFC 2119** supplies the requirement-level vocabulary used below: **MUST** is an
absolute requirement, **SHOULD** permits departure only when the implications are
understood and weighed, **MAY** marks something truly optional. This repository
already binds itself to those definitions in its own specifications —
`docs/nips/NIP-DV.md` and `docs/nips/NIP-PL.md` each carry a Terminology section
stating so — and this node means the same thing by the same words rather than
inventing a corpus-local reading.

The **surface-by-surface** framing below, rather than a single global rule, is
not a stylistic choice: it is what the evidence forced. A document asserting one
compatibility policy over this repository would have to be written past the fact
that its surfaces disagree with each other — one is frozen, one is versioned by
a leading byte, one explicitly refuses a default-version rule that a sibling
protocol explicitly grants, and most have no rule at all.

## What is guaranteed, surface by surface

Each row states the guarantee **as its own source states it**, then what was
found when the enforcement was opened. Read the third column as the load-bearing
one.

### Nostr event kinds

**Stated guarantee.** `CONTRIBUTING.md`: *"Event kinds are the only switch. Every
action in the system — a message, a reaction, a workflow step, a canvas update —
is a Nostr event with a kind integer. Adding a new feature means defining a new
kind. No breaking changes to existing clients."* `ARCHITECTURE.md` and
`VISION.md` restate it as "zero breaking changes to existing clients."

**What that sentence actually promises.** That *adding* a feature does not break
existing clients, because the addition takes a new kind number rather than
altering an existing one. It is a statement about the shape of the extension
mechanism. It is **not** a promise that an existing kind's number, tag shape, or
content schema will not change — no source says that, and this node does not
extrapolate one.

**Enforcement — opened, not assumed.** `crates/buzz-core/src/kind.rs` carries one
test bearing on kind stability, `no_duplicate_kind_values`, which inserts every
element of `ALL_KINDS` into a `HashSet` and asserts no duplicate. It proves that
two entries of that array do not share a value. It does not run when a kind
number is *changed*, because changing one leaves the array as unique as it was.

Its coverage is also narrower than its own documentation implies. `ALL_KINDS` is
annotated *"All registered kind constants"*, but three declared constants are
absent from it — `KIND_AUTH` (22242), `KIND_NOSTR_IDENTITY_BINDING` (24243) and
`KIND_PUSH_LEASE` (30350). Each is documented as ephemeral or never stored, which
makes the omission explicable; it is not consistent, since `KIND_BLOSSOM_AUTH`
(24242) is documented as "not stored" too and is in the array. A new kind added
to the module but not to `ALL_KINDS` is unchecked.

**Three copies, one comment.** The registry exists in Rust
(`crates/buzz-core/src/kind.rs`, 129 declared constants), TypeScript
(`desktop/src/shared/constants/kinds.ts`) and Dart
(`mobile/lib/shared/relay/nostr_models.dart`). The only stated coupling is the
Dart doc comment *"Keep in sync with `desktop/src/shared/constants/kinds.ts`"*.
No check compares them: a search across the JS/TS/Rust/Dart sources, the
`Justfile` and `.github/workflows/` for a sync, drift, parity or check reference
to any of the three files returns that comment and nothing else, and `Justfile`'s
aggregate `check` recipe has no kind-registry lane.

### Wire protocol and the NIP surface

**Stated guarantee.** None repository-wide. What exists is **capability
advertisement**: the relay serves NIP-11 with
`SUPPORTED_NIPS = &[1, 2, 10, 11, 16, 17, 23, 25, 29, 33, 38, 42, 50, 56]`, plus
NIP-43 appended at runtime only when membership enforcement is enabled and a
stable signing key exists. A client learns what a relay speaks by asking, rather
than by relying on a version promise.

**Enforcement.** The tests in `nip11.rs` pin *individual* memberships — 23 and
33, 38, 56 — assert the list is sorted, and assert NIP-43 stays out of the static
list. **No test asserts the list's full contents**, so silently dropping an entry
that is not individually pinned (1, 2, 10, 11, 16, 17, 25, 29, 42, 50) breaks no
test in that module.

**Per-specification rules.** Forward compatibility is written per-NIP, not
centrally, and the individual specifications are where the real requirements
live: `NIP-AP` requires readers to ignore unknown fields, `NIP-AM` the same,
`NIP-RS` says unknown top-level keys SHOULD be ignored and carries its own
Backwards Compatibility section, `NIP-AO` requires clients to ignore events with
unrecognized `frame` values.

**Two protocols in this repository take opposite positions on the same question,
each deliberately.** The broker protocol states *"There is no 'absent means 1'
compatibility rule: the protocol is unshipped, so `protocolVersion` is required
and an unknown value is rejected outright."* NIP-AB pairing defaults its `v`
parameter to 1 when absent, expressly for backward compatibility. Both are
reasoned; neither is derived from a shared policy, because there is none.

### The mesh wire contract

**The one surface declared frozen in its own source.**
`crates/buzz-relay-mesh/src/wire.rs` opens *"The mesh wire contract — FROZEN
surface"*, carries `ALPN = b"buzz/mesh/1"` with the note that *"Version bumps get
a new ALPN so old and new pods never half-speak to each other during a rolling
deploy"*, and defines `WIRE_VERSION: u8 = 1` as the first byte of every frame,
with receivers required to reject unknown versions loudly rather than guess.

**Enforcement is explicitly social**, and the file says so: *"Changes here
require a post in the mesh thread before the edit."* The versioned ALPN is the
mechanical part — it prevents a mismatched pair from connecting at all — and it
protects against half-speaking, not against someone changing a frame layout
without bumping the version.

### The relay's HTTP surface

**No stated guarantee, and no version segment.** The generic Nostr bridge
endpoints carry no version in their paths. The only versioned HTTP paths found in
`buzz-relay` are the admin API under `/api/admin/v1/` and the outbound
push-gateway delivery URL `/v1/deliveries/apns`, which is a URL the relay *calls*
rather than a surface it serves. This is a gap, recorded as one below.

### The `buzz-cli` output and exit-code contract

**Stated guarantee.** Reads return the canonical signed event fields, writes
return `{event_id, accepted, message}`, and the process exit code carries the
outcome class. This is the contract agent harnesses branch on.

**Implementation.** One function, `exit_code` in `crates/buzz-cli/src/error.rs`:
`Usage` and `NotFound` → 1; `Network` and `DeliveryUnknown` → 2;
`Relay { status }` → 3 for 401/403 and 2 otherwise; `Auth` and `Key` → 3;
`Conflict` → 5; `Other` → 4.

**Enforcement: none.** Searching `crates/` and `desktop/src-tauri/src` for the
identifier `exit_code` finds it in `buzz-cli` only at its definition and its one
call site; every other match is `buzz-persona`'s unrelated `Report::exit_code` or
a `last_exit_code` process-status field. **No test asserts any variant's mapping.**
This is not a new discovery — the repository's own 2026-08-18 ecosystem audit
recorded it as finding M7: *"a future reordering would compile and pass every
existing test while silently breaking the contract agent harnesses branch on."*

**And the prose copies have already drifted.** Four hand-maintained copies
disagree about code 1:

| Copy | Says of code 1 |
|---|---|
| `crates/buzz-cli/src/error.rs` doc comment | `1=user/not-found` |
| `desktop/src-tauri/src/managed_agents/nest_skill.md` | `1 = input/not-found` |
| `AGENTS.md` | `1=input error` |
| `crates/buzz-cli/README.md` | `1=user error` |

The last two omit the `NotFound` case the code maps to 1. A caller reading either
one and treating exit 1 as "my arguments were wrong" will mishandle a
successfully-formed request for something that does not exist.

**A second, incompatible scheme shares the vocabulary.** `buzz-admin`'s exit
codes, documented in `NOSTR.md`, are 1 validation error, 2 not found, 3 cannot
remove relay owner, 4 role mismatch, 5 DB/Redis/internal error. So "exit code 5"
means *write conflict* from `buzz-cli` and *internal error* from `buzz-admin`,
in the same repository.

### Rust crate versions

**No guarantee, and the versions do not mean what a reader would assume.** The
workspace declares `[workspace.package] version = "0.1.0"`, but **not every
member inherits it**: `crates/buzz-relay` sets `version = "0.2.1"` literally —
and it is the relay lane's release version authority — while `buzz-persona`,
`sprig` and `examples/countdown-bot` each hardcode `"0.1.0"` rather than using
`version.workspace = true`. A change to the workspace version would move most
crates and silently leave those four behind.

**Publication.** Two members set `publish = false`: `crates/git-sign-nostr`
(annotated *"internal workspace tool, not published to crates.io"*) and
`examples/countdown-bot`. No other member manifest sets the key in either
direction, so the remaining crates are publishable by default — which is a
default, not a decision anyone recorded.

**No API-compatibility tooling runs anywhere.** No workflow in
`.github/workflows/` runs `cargo-semver-checks`, `cargo-public-api`, or any
equivalent. Every `semver` match across those workflows is a release-time check
that a supplied *version string parses*, or a `docker/metadata-action` tag
pattern. Nothing checks whether a public API changed.

### Desktop and mobile app versions

**Independent lanes, no cross-lane guarantee.** `RELEASING.md` states plainly
that the three release lanes *"version independently"*, and names one authority
each: `desktop/package.json` and its synchronized manifests for desktop,
`crates/buzz-relay/Cargo.toml` for the relay, and the exact
`mobile-vX.Y.Z-rc.N` remote tag for mobile. Desktop currently reads 0.5.20 in
both `package.json` and `src-tauri/Cargo.toml`; `mobile/pubspec.yaml` reads the
placeholder `0.0.0+1`, consistent with the mobile version being injected from the
tag.

**`RELEASING.md` prescribes no meaning for an increment.** It contains no
occurrence of *semver*, *semantic version*, *major* or *minor*. A desktop bump
from 0.5.20 to 0.6.0 asserts nothing about compatibility, because no document
says it does. The one compatibility statement `RELEASING.md` does make is about a
build platform: the Linux release job builds inside an `ubuntu:22.04` container
*"for broad GLIBC compatibility"*.

**No minimum-supported-version anywhere.** No relay declares a minimum client
version and no client declares a minimum relay version. Version skew is handled,
where it is handled at all, by NIP-11 capability advertisement.

### Database migrations

**Forward-only, and this one is genuinely enforced.** `migrations/` holds 40
`.sql` files and **no down migration of any kind**. They are embedded by a single
`sqlx::migrate!("../../migrations")` in `buzz-db`'s migration runner, which means
an applied migration's checksum is recorded in the database.

`buzz-db`'s own tests treat that immutability as binding rather than incidental:
they state that 0007 and 0008 *"may already be recorded by a running relay and
their sqlx checksums are immutable"*, and repeatedly refuse to fold a later
migration into 0001 because *"folding would change 0001's checksum and break
brownfield"* deployments. The repository's 2026-08-18 audit records the absence
of a down-migration convention as deliberate — a forward-only policy — and
classifies it among accepted findings rather than defects.

**The gap is documentary, not mechanical.** The rule is real and the checksum
enforces it, but it is written only in code comments and one audit line. No
contributor-facing document states "migrations are forward-only and an applied
migration is never edited."

### The documentation corpus schema

**The one explicitly written, dated compatibility policy in the repository** —
and it governs documentation, not the product.
`launchpad/docs/corpus/schema/COMPATIBILITY.md` declares that removing a field,
removing an enum value, or narrowing a type is breaking; that a breaking change
requires, *in the same pull request*, a dated history entry and a re-validation
pass of every existing corpus node; and that additive changes are not breaking.
It is worth reading as a model for what a compatibility policy on a product
surface would look like, precisely because nothing on a product surface has one.

### One thing that is not a compatibility mechanism

`crates/buzz-conformance` sounds like one and is not. It is a trace-replay
checker for the TLA+ specification `docs/spec/MultiTenantRelay.tla`, and its own
module documentation says it is *not* a proof: *"Trace conformance only checks
executions you ran."* It establishes nothing about compatibility between
versions. It is named here so a reader scanning the crate list does not mistake
it for the guarantee they were looking for.

## MUST

These bind an author documenting or changing a compatibility surface, and the
reviewer of that change. They are identified C1–C8 and stable once published.

| # | Requirement |
|---|---|
| **C1** | A claim that a surface carries a compatibility guarantee MUST cite the source that states it. "It has always worked that way" is not a source. Nothing enforces this beyond review. |
| **C2** | A claim that a guarantee is **enforced** MUST name the test, schema, lint or workflow that enforces it, and that artifact MUST have been opened. Restating another document's assertion of enforcement does not satisfy this — six such assertions were falsified while this node was written. |
| **C3** | Where a guarantee is documented but nothing enforces it, the node MUST say so in those words. "Documented but unenforced" is the most useful thing a compatibility document can record, and omitting it converts a known risk into a false assurance. |
| **C4** | A statement of what a check proves MUST be bounded by what the check actually inspects. `no_duplicate_kind_values` proves no duplicate *within* `ALL_KINDS`; writing it up as "kind numbers are protected" overstates it by more than it states. |
| **C5** | A contract restated in more than one place MUST have its copies enumerated, and any disagreement between them recorded rather than silently reconciled to whichever copy the author read first. |
| **C6** | A change to a surface documented here MUST update this node in the same pull request, or state why the change leaves the guarantee unaltered. Nothing detects a stale entry; this is a reviewer's obligation. |
| **C7** | This node MUST NOT create a compatibility guarantee. Where no rule exists, it records the absence as a named gap and, per C8, routes the decision. Documenting a surface is not authority over it. |
| **C8** | A gap that needs a decision MUST be routed to the people who own the surface, as an issue naming the surface and what is undecided — not resolved inside this node. |

## SHOULD

| # | Guidance |
|---|---|
| **D1** | A compatibility guarantee SHOULD be generated from one source rather than restated. Every drifted contract found here — four exit-code copies, three kind registries — has the same shape: hand-maintained duplicates with no generating source. |
| **D2** | A surface whose contract external callers branch on SHOULD carry a test pinning that contract. The CLI exit-code mapping is the worked counter-example, and its own repository's audit flagged it more than six months before this node was written. |
| **D3** | Where two surfaces in this repository take opposite positions on the same compatibility question, both SHOULD state their reasoning locally. The broker protocol and NIP-AB pairing already do; neither defers to a shared rule, because none exists. |
| **D4** | A version number SHOULD NOT be cited as evidence of a compatibility guarantee in this repository unless a document says what an increment means. `RELEASING.md` says nothing, so a version bump here carries no such claim. |
| **D5** | An enforcement claim SHOULD name what the check does *not* cover alongside what it does. A reader who knows only the covered case will assume the rest. |

## Enforcement

**Nothing automated enforces any requirement on this page.** `validate.py`'s
`_load_frontmatter` splits a node on the front-matter delimiter and discards the
body into a variable no other function reads, for every node in every directory.
The prose above — every MUST, every SHOULD, every enforcement claim — is never
passed to any check.

**What the corpus validator does check** is structural and front-matter-only: that
the schema fields are present and well-formed, that a cited repository path
resolves to a real file, and that every `relationships[].target` names a node the
run loaded. It runs in CI on every change under `launchpad/docs/corpus/`.

**What a green validation run does not establish about this node:**

| Not established | Consequence |
|---|---|
| That a cited file supports the statement above it | A FACT citing a real file that says nothing on the subject passes cleanly |
| That the six required sections are present or ordered | A one-section node validates |
| That MUST and SHOULD are separated | A single mixed list validates |
| That any surface described here still behaves as described | The node ages silently; only C6, held by a reviewer, catches it |
| That a claimed enforcement mechanism exists | The enforcement table is prose, and prose is discarded before checking |
| That the compatibility guarantees themselves hold | This node describes the repository; it does not test it |

**Enforcement of the guarantees themselves is uneven, and that unevenness is the
node's main finding.** Summarised from the surface sections above, each entry
opened:

| Surface | Mechanical enforcement found |
|---|---|
| DB migrations, forward-only | **Yes** — sqlx records an applied migration's checksum; `buzz-db`'s tests treat 0001/0007/0008 as unfoldable for that reason |
| Mesh wire version skew | **Partial** — the versioned ALPN prevents mismatched pods connecting; nothing checks that a frame-layout change bumps it |
| Event-kind uniqueness | **Partial** — one duplicate-value test over a hand-maintained array that omits three declared constants |
| Relay NIP advertisement | **Partial** — four individual memberships and sortedness pinned; the list's full contents are not |
| Corpus schema | **Partial** — the written rule is real and the re-validation pass is runnable, but no check enforces that the history entry was added |
| CLI exit codes | **None** — flagged by the repository's own audit as M7 |
| Cross-language kind registries | **None** — one prose "keep in sync" comment |
| Rust crate API surface | **None** — no `cargo-semver-checks` or equivalent in any workflow |
| Relay HTTP surface | **None** — no version segment, no stated rule |
| App version semantics | **None** — `RELEASING.md` prescribes no meaning for an increment |

## Exceptions and escalation

**There is no exemption from C1–C3.** An undocumented or unverified compatibility
claim is worse than an absent one, because a reader acts on it. If the source
cannot be found, the honest entry is "no rule found for this surface," which is a
finding and not a failure.

**A SHOULD is departed from in the open.** D1–D5 are guidance; depart from one
and say which, and why, in the section it would have applied to.

**Where this node and a surface's own specification disagree, the specification
wins and this node is wrong** — open an issue against this node rather than
editing the specification to match. This node has no standing to change a surface
it merely describes.

**A gap needing a decision is escalated, never resolved here.** Per C8, file an
issue against the surface's owner naming the surface, the missing guarantee, and
what a decision would settle. Candidates visible from this node's evidence and
deliberately left open: whether the relay's unversioned HTTP surface needs a
compatibility statement; whether the CLI exit-code mapping should be pinned by a
test and generated into its four prose copies; whether the three kind registries
should be generated from `kind.rs`; whether crate versions should carry semantic
meaning or the publishable-by-default state should be made explicit; and whether
the forward-only migration rule should be written down somewhere a contributor
reads.

**A disputed application of C1–C8 is a judgement, not an exception.** The author
records the tension in the pull request and the reviewer decides. If they cannot
agree, the disagreement is filed against this node — a rule two people read
differently is a defect in the rule.

**`status: flagged` is not the escape hatch.** It means what ADR-0029 says it
means: two same-claim-type authoritative sources in conflict, unresolved by a
human. It is not a way to ship an unverified compatibility claim.

## Scope and omissions

**This node covers** which surfaces in this repository carry a compatibility
guarantee, what each guarantee says in its own source's words, what mechanically
enforces it, and the requirements binding anyone who documents or changes such a
surface.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How a surface is deprecated and removed — windows, migration paths, sunset notices | `governance/deprecation-policy.md` |
| The additive-kinds design principle itself, and why the architecture is shaped that way | `architecture-principles-event-driven-extension` |
| The CLI container's full description, including its error mapping in context | `architecture-containers-cli` |
| Retiring a **corpus node**, which is a different subject from product compatibility | `corpus-standard-deprecation` |
| What any individual NIP guarantees | that specification, under `docs/nips/` |
| Whether any of the gaps above *should* be closed, and how | the surface owners, via C8 |
| The security implications of an unversioned surface | not covered anywhere found; not this node's subject |

**On the sibling boundary with #911.** The split is "guaranteed while it exists"
versus "how it is removed." A statement that an event kind is never removed would
belong here; a statement of how long a removed kind's number stays retired would
belong there. Where a source states both in one breath, this node quotes the
guarantee half and leaves the removal half to #911 rather than splitting the
quotation.

**Expected but not verified when this node was written:**

- **No CI run has exercised this node.** All validator evidence is local to this
  worktree.
- **sqlx's checksum-rejection behaviour was not executed.** The immutability of an
  applied migration is asserted here from `buzz-db`'s own test comments and from
  the presence of `sqlx::migrate!`, not from observing a modified migration being
  rejected against a live database. The repository's belief in the rule is
  evidenced; the mechanism's behaviour is taken from the crate's documented
  contract.
- **The three kind registries were not diffed entry-by-entry.** That no automated
  check compares them is established; whether they *currently* agree is not, and
  a drift audit is a separate piece of work with its own likely findings.
- **The `exit_code` search covered `crates/` and `desktop/src-tauri/src`.** A test
  living outside both — in `web/`, `mobile/`, or a shell script — would not have
  been found. The repository's own audit reaching the same conclusion
  independently is corroboration, not proof.
- **Whether the relay's unversioned HTTP surface is a deliberate choice** is
  unknown. No decision record was found either way, and its absence is recorded
  as a gap rather than read as an omission.
- **Upstream `block/buzz`'s intent was not consulted.** Every source cited here is
  in this checkout. Whether upstream maintainers hold an unwritten compatibility
  policy is outside what this node can establish, and would be
  `TEAM_KNOWLEDGE` from them rather than a fact from the tree.
