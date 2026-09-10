---
id: implementation-crates-buzz-admin
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
relationships:
  - type: references
    target: architecture-context-buzz-platform
  - type: references
    target: architecture-context-relay-operator
evidence:
  - statement: "This node was authored and checked against repository revision 1ed55e980b0043f92d9c652e6a39a8e49345389c on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 1ed55e980b0043f92d9c652e6a39a8e49345389c"
  - statement: "buzz-admin is a Rust crate at crates/buzz-admin, described in its own manifest as 'Operator CLI for Buzz relay administration', producing a single binary (buzz-admin) from crates/buzz-admin/src/main.rs; its source tree is only two files, main.rs and deletions.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/Cargo.toml"
      - "crates/buzz-admin/src/main.rs"
      - "crates/buzz-admin/src/deletions.rs"
  - statement: "The Cli/Command clap enum in main.rs exposes exactly 7 top-level subcommands: add-member, remove-member, list-members, generate-key, migrate, product-feedback (with one nested subcommand, list), reconcile-channels, plus a deletions group that delegates entirely to buzz_deletion::Command."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "buzz-admin's Cargo.toml depends directly on buzz-db, buzz-deletion, buzz-core, buzz-auth, buzz-pubsub, buzz-search, buzz-audit, buzz-workflow, and buzz-media, plus nostr, tokio, clap, sqlx, deadpool-redis, and rustls; main.rs's own code, however, only calls into buzz-db (Db, DbConfig), buzz-core (kind constants, tenant helpers), buzz-pubsub (PubSubManager, EventTopic), and nostr directly -- buzz-auth, buzz-search, buzz-audit, buzz-workflow, and buzz-media are not referenced by name anywhere in main.rs or deletions.rs, so their presence in Cargo.toml is either exercised only through buzz-deletion's own dependency graph or is unused by this crate's own code."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/Cargo.toml"
      - "crates/buzz-admin/src/main.rs"
      - "crates/buzz-admin/src/deletions.rs"
  - statement: "architecture-containers-postgres.md (a merged corpus node) independently states that buzz-admin and buzz-deletion are the only crates besides buzz-relay that depend on buzz-db directly, and lists buzz-admin's Postgres access as 'via buzz_db::Db | Operator CLI administration' -- corroborating this node's own reading of main.rs's connect_db function."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
      - "crates/buzz-admin/src/main.rs"
  - statement: "deletions.rs is a thin adapter: it re-exports buzz_deletion::Command as DeletionsCommand and its run() function does nothing but call buzz_deletion::run(command).await; buzz-deletion's own Command enum (crates/buzz-deletion/src/lib.rs) exposes Submit, List, Inspect, Approve, Abort, Unblock, Run, Drain, and Sweep variants, plus a separate worker-only Command2-shaped Run/Drain pair for the continuous background worker."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/deletions.rs"
      - "crates/buzz-deletion/src/lib.rs"
  - statement: "The one automated test in this crate, deletions::tests::continuous_worker_command_is_not_exposed, asserts that Cli::try_parse_from([\"buzz-admin\", \"deletions\", \"worker\"]) fails to parse -- confirming buzz-admin's clap surface deliberately does not expose buzz-deletion's continuous background-worker subcommand, only its CLI-invoked lifecycle commands."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/deletions.rs"
  - statement: "main.rs's crate-level doc comment documents two behavioral invariants for member management: (1) the CLI intentionally emits only the kind:13534 membership-list snapshot, not kind:8000/8001 deltas, because publish_nip43_delta is in-process-only and a sidecar CLI call would store without pushing; (2) a custom_created_at = max(now, newest_existing_13534 + 1s) bump defeats same-second domination for serial CLI invocations but does not serialize concurrent buzz-admin processes -- run.sh's own serialization is named as the actual guard against parallel adds."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "publish_membership_list_with_bump signs and publishes a kind:13534 event carrying a NIP-70 '-' protected-event tag plus one 'member' tag per relay member, then calls db.replace_addressable_event and, only if the row was newly inserted, publishes to Redis via pubsub.publish_event with EventTopic::Global -- so a same-second duplicate that loses the domination race is stored idempotently but not re-broadcast."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "resolve_admin_tenant resolves the deployment's community from the RELAY_URL environment variable's host via buzz_core::tenant::relay_url_authority (not a plain Url::host_str() call), with an explanatory comment that this choice is deliberate: relay_url_authority preserves an explicit non-default port and IPv6 brackets the same way the relay's own startup community-seeding and live host-resolution do, so buzz-admin resolves the identical community a plain host_str() call would get wrong for a non-default port. An unmapped host fails closed with an error rather than falling back to a default community."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "reconcile_channels accepts an optional --channel UUID and an optional --relay-key hex string (falling back to BUZZ_RELAY_PRIVATE_KEY, then an ephemeral generated key with a printed warning); without --channel it does a full backfill emitting kind:39000, kind:39001 (KIND_NIP29_GROUP_ADMINS), and kind:39002 for every channel missing kind:39000; with --channel it is deliberately roster-only, replacing only kind:39002 for that one channel and leaving kind:39000/39001 untouched, per an inline comment explaining a targeted repair must not destroy canonical metadata or admin events."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "The security audit launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md rates as Blocker (BL1) that 'buzz-admin reconcile-channels --relay-key puts the relay's real signing key in argv', citing crates/buzz-admin/src/main.rs:89-95,461-483, and documents that argv is visible via ps aux, /proc/<pid>/cmdline, shell history, and log aggregators that capture command lines; the proposed fix is to remove the --relay-key flag entirely and require BUZZ_RELAY_PRIVATE_KEY only, mirroring connect_member_services's own existing env-only pattern."
    entry_class: FACT
    evidence:
      - "launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md"
  - statement: "At the recorded revision, ReconcileChannels's relay_key: Option<String> clap argument (documented '#[arg(long)]') is still present in main.rs, and reconcile_channels still resolves the signing key as relay_key_arg.or_else(BUZZ_RELAY_PRIVATE_KEY env lookup), so the BL1 finding is unresolved in current code -- it was not fixed by any change on this branch."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "ARCHITECTURE.md's 'buzz-admin -- Operator CLI' section names only 5 of the crate's 7 subcommand groups (add-member, remove-member, list-members, generate-key, reconcile-channels) and omits migrate, product-feedback, and deletions, which exist as Cmd variants in main.rs at this revision; ARCHITECTURE.md also states the binary is shipped in the relay Docker image and is 'the recommended way to manage relay membership in production', recommending ./run.sh add-member/remove-member/list-members in Compose deployments."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
      - "crates/buzz-admin/src/main.rs"
  - statement: "launchpad/deploy/runbooks/relay-build-list.md states buzz-admin 'has exactly seven commands -- add-member, remove-member, list-members, generate-key, migrate, product-feedback, reconcile-channels -- and none of them touch communities', supporting its own headline finding that no manual community-seeding command exists; this list itself omits the deletions subcommand group present in main.rs at this revision, so this runbook undercounts the surface by one command in the opposite direction from ARCHITECTURE.md's table, which omits three different ones (migrate, product-feedback, deletions)."
    entry_class: FACT
    evidence:
      - "launchpad/deploy/runbooks/relay-build-list.md"
  - statement: "NOSTR.md's 'CLI: Managing Members' section documents buzz-admin add-member/remove-member/list-members with a five-row exit-code table (0 success, 1 validation error, 2 not found, 3 cannot-remove-owner, 4 role mismatch, 5 DB/Redis/internal error) that matches main.rs's own Ok(0)/Ok(1)/.../Ok(5) return values in cmd_add_member and cmd_remove_member exactly."
    entry_class: FACT
    evidence:
      - "NOSTR.md"
      - "crates/buzz-admin/src/main.rs"
  - statement: "deploy/compose/run.sh's add-member, remove-member, and list-members cases shell out to docker compose exec relay /usr/local/bin/buzz-admin <subcommand>, confirming the binary is expected to run inside the already-deployed relay container rather than as a standalone host process in Compose deployments."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh"
  - statement: "The Dockerfile's builder stage compiles buzz-admin alongside buzz-relay and buzz-pair-relay in one cargo build --release --locked invocation (-p buzz-admin --bin buzz-admin among the three -p/--bin pairs), strips it in the stripped-binaries stage, and copies /usr/local/bin/buzz-admin into both the runtime and runtime-debug final images alongside buzz-relay -- so buzz-admin ships in every relay image build, not as an optional extra."
    entry_class: FACT
    evidence:
      - "Dockerfile"
  - statement: "Justfile's _ensure-migrations recipe runs cargo run -p buzz-admin -- migrate (not a direct call into buzz-db or buzz-relay) to apply pending SQL migrations and seed the local dev community, making buzz-admin migrate the local-dev entry point for schema setup independent of buzz-relay's own BUZZ_AUTO_MIGRATE-gated startup path documented in architecture-containers-postgres.md."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "TESTING.md's smoke-test sequence uses buzz-admin generate-key to mint the CLI identity used for every subsequent buzz command in the walkthrough, and separately in the ACP-harness recipe to mint a fresh agent identity; a later section states the companion script scripts/e2e-large-channel-roster.sh 'refuses debug binaries and refuses a buzz or buzz-admin resolved outside this checkout's target/release'."
    entry_class: FACT
    evidence:
      - "TESTING.md"
  - statement: "scripts/e2e-large-channel-roster.sh is a standalone bash script (not invoked from any file under .github/workflows/ or from the Justfile, confirmed by a repository-wide grep for its filename finding no hits outside itself) that calls buzz-admin generate-key and buzz-admin reconcile-channels --channel <uuid> to prove a channel member past the historical 1,000-row boundary survives an authoritative republish; it requires binaries resolved from this checkout's own target/release and a psql/jq toolchain, and is run manually, not in CI."
    entry_class: FACT
    evidence:
      - "scripts/e2e-large-channel-roster.sh"
      - "grep(pattern='e2e-large-channel-roster', path='.github/workflows/*;Justfile') -> no matches outside the script's own file"
  - statement: "launchpad/docs/Observability/current-state/coverage.md carries two buzz-admin rows, T04 ('Admin bootstrap and maintenance CLI' -- generate-key, migrate, reconcile-channels, tracked by launchpad-26/buzz#476) and T05 ('Admin lifecycle and feedback CLI' -- add-member, remove-member, list-members, product-feedback, deletions, tracked by #468) -- both marked 'Pending assessment' for 'component runtime signal behavior' as of the coverage document's own recorded source-registration commit."
    entry_class: FACT
    evidence:
      - "launchpad/docs/Observability/current-state/coverage.md"
  - statement: "docs/admin/README.md documents a 'Deployment moderation dashboard' activated by BUZZ_ADMIN_HOST, served from the existing relay process at /reports and /feedback routes -- a distinct, relay-hosted web surface (frontend directory admin-web/, per the Dockerfile's pnpm --filter buzz-admin-web build step) that is unrelated in code to the buzz-admin CLI crate this node documents, despite the name collision between 'admin-web' and 'buzz-admin'."
    entry_class: FACT
    evidence:
      - "docs/admin/README.md"
      - "Dockerfile"
  - statement: "architecture-context-buzz-platform.md and architecture-context-relay-operator.md (both merged corpus nodes) independently document buzz-admin's add-member/remove-member/list-members/generate-key/reconcile-channels subcommands from the human-operator's perspective and state the binary ships inside the relay's own Docker image at /usr/local/bin/buzz-admin -- both nodes list product-feedback and migrate as absent from their own enumeration, i.e. neither claims completeness over the full 7-subcommand surface this node documents from the code side."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/context/buzz-platform.md"
      - "launchpad/docs/corpus/architecture/context/relay-operator.md"
  - statement: "architecture-containers-cli.md's own Scope and omissions table states explicitly that buzz-admin ('the separate operator CLI for relay administration') is owned by 'buzz-admin's own container node (not yet written) -- not the same crate or audience as this one', confirming from a second independent corpus node that no architecture-containers-* node for buzz-admin itself is merged at this revision."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/cli.md"
  - statement: "No file under docs/nips/ in this repository documents NIP-43 (the relay-membership protocol whose kind constants main.rs's own comments and buzz-core/src/kind.rs reference by name); the KIND_NIP43_* constants and their doc comments in buzz-core/src/kind.rs are the only in-repository specification of that protocol's shape, so no corpus-node-bearing spec/decision/contract exists for buzz-admin to declare an implements edge toward."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "grep(pattern='NIP-43', path='docs/nips/*.md') -> no matches"
---

# `buzz-admin`: implementation reference

`crates/buzz-admin` (binary `buzz-admin`) is Buzz's out-of-band operator CLI for relay
administration. This node documents what the crate's own code does, since -- unlike a
crate realizing one documented NIP or ADR -- `buzz-admin` has no single spec/decision
document it implements; its target is the relay's own membership, channel-discovery, and
migration behavior as those are already defined in code (`buzz-core`'s kind registry,
`buzz-db`'s data-access layer, `buzz-relay`'s own tenant-resolution and migration-gate
logic), which `buzz-admin` mirrors from outside the relay process rather than reimplements.

## Target

There is no single external spec, ADR, or NIP document this crate realizes end to end, and
none is invented here. What `buzz-admin` operationally mirrors, concretely:

- **NIP-43-shaped relay membership** (`KIND_NIP43_MEMBERSHIP_LIST` = kind:13534, plus the
  member-added/removed/leave-request kind constants) -- defined only in
  `crates/buzz-core/src/kind.rs`'s doc comments; no `docs/nips/NIP-43.md` exists in this
  repository to point an `implements` edge at.
- **NIP-29 channel-discovery events** (kind:39000/39001/39002) -- the same kinds the relay
  itself emits at channel creation; `buzz-admin reconcile-channels` is a repair tool for
  when those are missing, not their primary source.
- **The relay's own tenant/community resolution contract** -- `buzz-admin` deliberately
  calls the same `buzz_core::tenant::relay_url_authority` helper the relay's startup
  seeding and live request handling use, rather than a plain `Url::host_str()`, so it
  resolves the identical community for a `RELAY_URL` carrying a non-default port.
- **`buzz-db`'s migration runner** (`Db::migrate`) -- `buzz-admin migrate` is one of two
  code paths that can apply pending SQL migrations, the other being `buzz-relay`'s own
  `BUZZ_AUTO_MIGRATE`-gated startup path (`launchpad/docs/corpus/architecture/containers/postgres.md`
  documents that path in depth; this node does not restate it).

Because none of these targets carries a corpus node id at this revision, no `implements`
edge is declared -- inventing one to a nonexistent id is a hard validation error, and
`architecture-containers-relay.md`/`-postgres.md` already establish the precedent of
naming a target in prose and omitting the edge until it exists.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `crates/buzz-admin/src/main.rs::Command` (clap enum) | The crate's whole subcommand surface: `AddMember`, `RemoveMember`, `ListMembers`, `GenerateKey`, `Migrate`, `ProductFeedback { List }`, `Deletions`, `ReconcileChannels` | 7 top-level groups; `ARCHITECTURE.md`'s own table names only 5, omitting `migrate`, `product-feedback`, and `deletions` (see *Divergences*) |
| `cmd_add_member` / `cmd_remove_member` / `cmd_list_members` | Relay membership CRUD against `buzz-db`'s `relay_members` table, gated by role validation (`member`/`admin` only, never `owner` via CLI) | Exit codes 0/1/2/3/4/5 match `NOSTR.md`'s documented table exactly |
| `publish_membership_list_with_bump` | Publishes the kind:13534 roster snapshot with a same-second-domination-defeating timestamp bump, tagged NIP-70 `-` (protected, no re-broadcast by third parties) | Publishes to Redis via `buzz-pubsub` only when the DB write was a genuine insert, not on a lost domination race |
| `resolve_admin_tenant` | Single-community-per-invocation tenant resolution from `RELAY_URL`'s host, via `relay_url_authority`, failing closed on an unmapped host | Deliberately no default tenant fallback |
| `reconcile_channels` | Full backfill (kind:39000/39001/39002) for channels missing discovery metadata, or a roster-only targeted repair (kind:39002 only) when `--channel` is given | `--relay-key` accepts the relay's signing key as a CLI flag -- see *Divergences* |
| `Command::Migrate` -> `db.migrate()` | Applies pending SQL migrations via `buzz-db`'s embedded migration runner | The `Justfile`'s local-dev `_ensure-migrations` recipe uses exactly this path, not the relay's own startup gate |
| `crates/buzz-admin/src/deletions.rs` | Thin delegation to `buzz_deletion::Command`/`run`, deliberately excluding the continuous background-worker subcommand from the CLI surface | Enforced by `continuous_worker_command_is_not_exposed`, the crate's only automated test |
| `Dockerfile` builder/runtime stages | Compiles and ships `/usr/local/bin/buzz-admin` inside every relay container image, alongside `buzz-relay` and `buzz-pair-relay` | Not an optional or separately-installed artifact |
| `deploy/compose/run.sh` | Wraps `docker compose exec relay buzz-admin <subcommand>` for `add-member`/`remove-member`/`list-members` | The documented, recommended production invocation path per `ARCHITECTURE.md` |

## Divergences

- **BL1 (Blocker, unresolved at this revision): `reconcile-channels --relay-key` puts the
  relay's real signing key in argv.** `launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md`
  rates this a Blocker: the flag is offered ahead of the `BUZZ_RELAY_PRIVATE_KEY`
  environment-variable fallback at the same call site, so a caller following the flag's own
  precedence exposes the relay's stable signing identity via `ps aux`, `/proc/<pid>/cmdline`,
  shell history, or any log aggregator that captures command lines. Checked directly against
  current `main.rs`: `relay_key: Option<String>` is still a `#[arg(long)]` on
  `ReconcileChannels`, and `reconcile_channels` still resolves it as
  `relay_key_arg.or_else(BUZZ_RELAY_PRIVATE_KEY env lookup)`. This is drift the audit already
  named, not something this node discovered independently, and it remains unfixed as of the
  recorded revision. Fixing it is out of this node's own scope (issue #917 excludes
  "changing runtime product behavior unless a separately linked implementation issue owns
  that change"); the audit document itself is the tracking artifact.
- **`ARCHITECTURE.md`'s subcommand table is incomplete, the same shape of drift found
  elsewhere in this corpus.** It names 5 of 7 subcommand groups, omitting `migrate`,
  `product-feedback`, and `deletions` -- both present as `Cmd` variants in `main.rs` at this
  revision. `launchpad/deploy/runbooks/relay-build-list.md` names all three of those (plus
  the other four), but itself omits `deletions` -- so two independent documents each
  undercount the same 7-subcommand surface by a different amount, rather than agreeing with
  each other on a smaller, stale total.
- **No divergence found between `main.rs`'s exit-code behavior and `NOSTR.md`'s documented
  table.** Checked directly: `cmd_add_member`/`cmd_remove_member`'s `Ok(0)`..`Ok(5)` returns
  match `NOSTR.md`'s five-row table exactly, for every code path read.

## Verification

No dedicated automated integration-test suite exists for `buzz-admin` at this revision.
What exists, concretely:

- **One automated unit test**: `deletions::tests::continuous_worker_command_is_not_exposed`,
  asserting the continuous-worker subcommand parses as an error through `buzz-admin`'s own
  clap surface.
- **One manual smoke-test sequence**, in `TESTING.md`: `buzz-admin generate-key` mints the
  identity used for the rest of the walkthrough; the ACP-harness recipe reuses it to mint a
  second agent identity.
- **One standalone, not-CI-wired scripted check**: `scripts/e2e-large-channel-roster.sh`,
  which drives `buzz-admin generate-key` and `buzz-admin reconcile-channels --channel` against
  a live relay/Postgres to prove a large-roster channel member survives an authoritative
  republish. Confirmed absent from every `.github/workflows/*` file and the `Justfile` by
  direct grep -- it is a manual reviewer tool, not a CI gate.
- **Two "Pending assessment" rows** in `launchpad/docs/Observability/current-state/coverage.md`
  (T04, T05), each naming the crate's subcommands and an open tracking issue (#476, #468) for
  future runtime-signal coverage that has not yet landed.

## Relationships

- references: architecture-context-buzz-platform
- references: architecture-context-relay-operator

Both targets are merged on `origin/launchpad` at the recorded revision and already cite
`buzz-admin`'s subcommand surface as supporting context from the human-operator's
perspective, independent of this node's own code-level reading -- exactly the "cites target
as supporting context, no ownership or currency dependency implied" directionality
`relationships.schema.json` defines for `references`. No `implements` edge is declared (see
*Target*, above). No `part-of` edge is declared: `buzz-admin` is a separate crate and binary
from both `buzz-relay` and `buzz-cli`, not a constituent section of either container, and
`architecture-containers-cli.md`'s own Scope table already states `buzz-admin` needs its
own, not-yet-written container node rather than being folded into `-cli`'s.

## Scope and omissions

**This node covers** `buzz-admin`'s implementation responsibility and boundary, its public
subcommand surface, its important dependencies and what of them its own code actually
exercises, its owned source paths and the one representative automated test, where it plugs
into deployment (`Dockerfile`, `deploy/compose/run.sh`) and local development (`Justfile`),
and the divergences found between the code and this repository's own documentation about it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `buzz-db`'s connection pooling, migration-runner internals, and schema contract | `launchpad/docs/corpus/architecture/containers/postgres.md` |
| `buzz-deletion`'s own durable deletion-lifecycle state machine (`Submit`/`List`/`Inspect`/`Approve`/`Abort`/`Unblock`/`Run`/`Drain`/`Sweep` and the continuous worker `buzz-admin` deliberately excludes) | `buzz-deletion`'s own implementation-reference node (not yet written) |
| `buzz-relay`'s own `BUZZ_AUTO_MIGRATE`-gated startup migration path, a separate code path from `buzz-admin migrate` | `launchpad/docs/corpus/architecture/containers/postgres.md` |
| The relay-hosted moderation web dashboard at `docs/admin/README.md` (`admin-web`), a different surface despite the name collision with this crate | `docs/admin/README.md` |
| `buzz-admin`'s own container-level responsibility/technology/ownership-boundary node (analogous to `architecture-containers-cli.md`/`-relay.md`/`-postgres.md`) | not yet written, per `architecture-containers-cli.md`'s own Scope table |
| Whether Block's internal deployment pipelines (`squareup/block-coder-tf-stacks`, `squareup/sprout-oss`) invoke `buzz-admin migrate`/`add-member`/`remove-member` in practice | outside this repository's visible source, not opened by this task, same boundary `architecture-containers-postgres.md` already draws |

**This node does not own fixing BL1** (the `--relay-key` argv-exposure finding) or filing a
new issue for it -- it is already tracked in
`launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md`, and issue #917 excludes
"changing runtime product behavior unless a separately linked implementation issue owns that
change."

**Expected but not verified when this node was written:**

- **Whether `buzz-auth`, `buzz-search`, `buzz-audit`, `buzz-workflow`, and `buzz-media`**
  (all direct `Cargo.toml` dependencies of `buzz-admin` with no call site found in `main.rs`
  or `deletions.rs`) are exercised transitively through `buzz-deletion`'s own dependency
  graph, or are simply unused by this crate today. `buzz-deletion`'s own source was not read
  deeply enough to settle this, and it is that crate's own implementation-reference node's
  question to answer, not this one's.
- **Whether `buzz-admin migrate`, run against a schema older than the replica-freezing
  fence trigger `architecture-containers-postgres.md` documents, exhibits the same
  fail-closed behavior `buzz-relay`'s own post-migration verification does.** `Db::migrate`
  itself was not traced past the call site in `main.rs`.
- **Live runtime behavior of any subcommand.** This node is a static-source reading; no
  `buzz-admin` binary was built or executed while authoring it, consistent with `T04`/`T05`'s
  own "Pending assessment" status in `launchpad/docs/Observability/current-state/coverage.md`.
