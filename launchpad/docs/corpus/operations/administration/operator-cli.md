---
id: operations-administration-operator-cli
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "buzz-admin is a Rust binary crate at crates/buzz-admin, described in its own manifest as the 'Operator CLI for Buzz relay administration'."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/Cargo.toml"
  - statement: "The buzz-admin binary is built with `cargo build --release --locked -p buzz-admin --bin buzz-admin` inside the repository's root Dockerfile, then stripped and copied to /usr/local/bin/buzz-admin in both the normal (stripped) and debug (unstripped) relay runtime image stages, alongside buzz-relay and buzz-pair-relay."
    entry_class: FACT
    evidence:
      - "Dockerfile"
  - statement: "The repository's Justfile builds and runs buzz-admin locally as `cargo run -p buzz-admin -- migrate` in the `_ensure-migrations` recipe, which the `just setup` chain depends on to apply pending database migrations before the local dev relay is expected to run."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "TESTING.md's live-testing runbook builds buzz-admin together with buzz-relay and buzz-cli via `cargo build --release -p buzz-relay -p buzz-cli -p buzz-admin`, then adds `target/release` to PATH so the plain `buzz-admin` command resolves to that release binary for the rest of the runbook."
    entry_class: FACT
    evidence:
      - "TESTING.md"
  - statement: "buzz-admin's clap Command enum has eight subcommands: AddMember, RemoveMember, ListMembers, GenerateKey, Migrate, ProductFeedback (with a nested List subcommand), Deletions (delegating to buzz-deletion's own Command enum), and ReconcileChannels."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "main() installs the ring rustls CryptoProvider before doing anything else, with a comment stating this mirrors buzz-relay's own startup and is required because the workspace's Redis TLS feature compiles both aws-lc-rs and ring transitively, so rustls cannot auto-select a provider and would otherwise panic on the first rediss:// (TLS) Redis connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "connect_db() reads DATABASE_URL, defaulting to postgres://buzz:buzz_dev@localhost:5432/buzz when unset, and every subcommand that touches the database calls it; connect_member_services() additionally reads REDIS_URL (default redis://localhost:6379) and requires BUZZ_RELAY_PRIVATE_KEY to be set, returning an explicit error naming both if it is missing, because AddMember and RemoveMember sign a relay-authored kind:13534 event and cannot proceed without a stable relay signing key."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: ".env.example documents DATABASE_URL as postgres://buzz:buzz_dev@localhost:5432/buzz, REDIS_URL as redis://localhost:6379, RELAY_URL as ws://localhost:3000, and BUZZ_RELAY_PRIVATE_KEY as a commented-out 32-byte hex private key -- the same four variables buzz-admin's own connection helpers read."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "resolve_admin_tenant() reads RELAY_URL (default ws://localhost:3000), derives its authority via buzz_core::tenant::relay_url_authority (host plus any non-default port, preserving IPv6 brackets) rather than a plain URL host_str(), and looks that authority up against the durable communities table; an unmapped host is a hard error rather than a default-community fallback, and the function's own doc comment states this is deliberate -- buzz-admin is single-community per invocation, sharing whatever community the relay it is pointed at has already seeded, with no cross-community sweep."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "AddMember and RemoveMember each accept a --pubkey (bech32 npub or 64-character hex, parsed by nostr::PublicKey::parse and normalized to lowercase hex) and validate --role against exactly 'member' or 'admin'; passing role 'owner' is explicitly rejected with a message directing the operator to the RELAY_OWNER_PUBKEY config instead, and RemoveMember additionally supports an optional --role guard that only removes the member if their current role matches."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "After a successful DB write, both AddMember and RemoveMember call publish_membership_list_with_bump, which reads every current relay member, builds a NIP-70-protected kind:13534 addressable event (a '-' tag plus one ['member', pubkey, role] tag per member) signed with the relay's own key, sets its created_at to max(now, latest_existing_13534 + 1 second) to defeat same-second domination on repeated invocations, and -- only if replace_addressable_event actually inserted a new row -- publishes it to Redis on the community's global topic so already-connected live clients see the updated roster without reconnecting."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "A failure of publish_membership_list_with_bump after a successful database write is reported to stderr as a warning ('member added/removed to/from DB but list publish failed') and does not change the process exit code, so the membership change itself has already taken effect in the database even when the live-roster broadcast fails."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "run()'s Result<i32> return value is mapped straight to the process exit code in main(), and cmd_add_member/cmd_remove_member return distinct codes per outcome: 0 success, 1 a validation error (bad role or unparseable pubkey), 2 remove-member on a pubkey that is not a member, 3 attempting to remove the relay owner, 4 a --role guard mismatch on remove-member, and 5 a database write failure; any error surfacing through the top-level Result (for example, RELAY_URL host not mapped to a community) is caught in main(), printed to stderr as 'error: {e}', and exits 5."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "NOSTR.md documents the identical exit-code table (0 success, 1 validation error, 2 not found, 3 cannot remove relay owner, 4 role mismatch, 5 DB/Redis/internal error) for the add-member/remove-member/list-members flow, alongside DATABASE_URL, REDIS_URL, and BUZZ_RELAY_PRIVATE_KEY as the required environment variables for member management, and states these commands can also be reached over NIP-43 admin events (kind:9030/9031/9032) as a WebSocket-native alternative to the CLI."
    entry_class: FACT
    evidence:
      - "NOSTR.md"
  - statement: "list-members prints one line per relay member -- pubkey, role, the pubkey of whoever added them (or '-' if unrecorded), and an ISO-8601-shaped created_at timestamp -- as fixed-width plain text, and prints '(no relay members)' rather than an empty table when the community has none."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "cmd_list_members opens a fresh database connection via connect_db() and queries list_relay_members on every invocation with no in-process or on-disk cache, and buzz-admin's Command enum has no subcommand whose purpose is to undo or revert a prior add-member/remove-member -- the only way to reverse a membership change is running the inverse subcommand with the same --pubkey."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "generate-key prints a freshly generated Nostr keypair's hex public key and displayed secret key to stdout, followed by a one-line instruction to set BUZZ_PRIVATE_KEY to the secret key; it touches no database, Redis connection, or relay, unlike every other buzz-admin subcommand except pack-free -- it is the one subcommand connect_db()/connect_member_services() are never called for."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "TESTING.md's smoke-test sequence captures generate-key's stdout with awk to extract 'Secret key:' and 'Public key:' fields into BUZZ_PRIVATE_KEY and a $PUBKEY shell variable, the identity buzz-cli then uses to create a channel and send a message against the same local relay."
    entry_class: FACT
    evidence:
      - "TESTING.md"
  - statement: "migrate calls connect_db() then Db::migrate(), printing 'Database migrations complete.' on success; deploy/compose/README.md documents running `buzz-admin migrate` (or setting BUZZ_AUTO_MIGRATE=true) before starting the relay when bootstrapping a fresh database in a Compose deployment, noting that auto-migration additionally requires an image with embedded SQLx migrations."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
      - "deploy/compose/README.md"
  - statement: "reconcile-channels backfills missing NIP-29 channel-discovery events (kind:39000 metadata, kind:39001 admins, kind:39002 members) for channels that have none, or, when passed --channel <uuid>, force-republishes only that one channel's kind:39002 member snapshot while leaving its kind:39000/39001 metadata and admin events untouched; a targeted --channel repair requires an explicit --relay-key or BUZZ_RELAY_PRIVATE_KEY and refuses to run without one, while the untargeted backfill falls back to an ephemeral, unverifiable-after-restart key with an explicit warning if neither is supplied."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "ARCHITECTURE.md's buzz-admin subcommand table independently describes add-member, remove-member, list-members, generate-key, and reconcile-channels with one-line summaries consistent with main.rs's own doc comments, and states the buzz-admin binary is shipped in the relay Docker image at /usr/local/bin/buzz-admin as the recommended way to manage relay membership in production."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
  - statement: "In a Docker Compose deployment, deploy/compose/run.sh wraps buzz-admin's member-management subcommands as `docker compose exec relay /usr/local/bin/buzz-admin add-member --pubkey <arg> [extra args]`, `remove-member` likewise, and `list-members` with no extra arguments, so an operator can run `./run.sh add-member <npub-or-hex> [--role member|admin]` instead of invoking `docker compose exec` directly."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh"
  - statement: "NOSTR.md's usage section shows the same operation two ways: through run.sh (`./run.sh add-member npub1abc...`, `./run.sh remove-member npub1abc... --role member`, `./run.sh list-members`) and by invoking buzz-admin directly inside the container (`docker compose exec relay buzz-admin add-member --pubkey npub1abc...`), documenting the wrapper as the Compose-deployment convenience path and the direct invocation as the underlying mechanism it wraps."
    entry_class: FACT
    evidence:
      - "NOSTR.md"
  - statement: "product-feedback list queries feedback across every community rather than the single community resolve_admin_tenant() would select, accepts a --limit (default 100, clamped 1-1000 by clap's own value_parser), and prints the result as pretty-printed JSON -- the one subcommand in the enum whose own doc comment ('Inspect deployment-wide Buzz product feedback') states it is deliberately not community-scoped."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "deletions delegates its entire subcommand surface to buzz_deletion::run, re-exporting buzz-deletion's own Command enum (Submit, List, Inspect, Approve, Abort, Unblock, Run, Drain, Sweep) rather than defining a second one, and a unit test in the same file asserts that a `worker` subcommand -- present on buzz-deletion's own continuous-loop entry point but not part of its CLI Command enum -- is not reachable through buzz-admin's argument parser."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/deletions.rs"
  - statement: "buzz-deletion's own module doc describes it as the 'Shared durable whole-community deletion engine and store adapters', and its Command enum's variants each carry an operator-facing doc comment: Submit persists a deletion request and freezes its initial cross-store inventory, List lists requests as JSON, Inspect shows one request's approval/checkpoint/error history, Approve explicitly approves a frozen inventory digest, Abort terminally cancels before irreversible deletion begins, Unblock resumes a blocked request after remediation, Run claims and runs one request to terminal/blocked, Drain runs the whole currently-runnable queue once and exits, and Sweep records observational bucket-taxonomy evidence independent of any single community's deletion."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs"
  - statement: "architecture-containers-cli (the container node for buzz-cli, a separate crate at crates/buzz-cli) explicitly lists buzz-admin as out of its own scope, naming it 'the separate operator CLI for relay administration' and stating it is 'not the same crate or audience' as buzz-cli, with buzz-admin's own container node marked not yet written at that node's own recorded revision."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/cli.md"
  - statement: "capabilities-communities-community-members documents relay-wide membership as a NIP-43 roster (the relay_members table, keyed by community_id and pubkey, role constrained to owner/admin/member) distinct from NIP-29 per-channel membership, changeable either through the relay's own admin-event kinds (9030/9031/9032, requiring NIP-42 authentication as owner or admin) or, per that node's own text, through 'buzz-admin, run directly against the database rather than through the relay's own authorization path' -- the same roster and the same three-role model this operator-CLI node's add-member/remove-member/list-members task manipulates via a different entry point."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/capabilities/communities/community-members.md"
  - statement: "This node was written using launchpad/docs/corpus/templates/procedure.md, which was already merged on origin/launchpad at the recorded revision and directs a how-to-shaped node to open with an Overview, an optional Before you start, one numbered task sequence per logical goal, a See also section, an explicit Boundary statement, Relationships, and a Scope and omissions section distinguishing what the node does not cover from what was expected but could not be verified."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
relationships:
  - type: references
    target: architecture-containers-cli
  - type: references
    target: capabilities-communities-community-members
  - type: implements
    target: corpus-template-procedure
---

# Operating `buzz-admin`: the relay operator CLI

How an operator builds `buzz-admin`, points it at a relay's database and
Redis, and runs its subcommands to manage relay membership and other
administrative tasks. Not `buzz-cli` — see *Boundary* below.

## Before you start

- A checkout of this repository, with Rust available (`. ./bin/activate-hermit`
  activates the pinned toolchain) to build from source, **or** access to a
  running relay container that already ships `/usr/local/bin/buzz-admin`.
- Network access to the Postgres and Redis instances the target relay uses —
  `buzz-admin` talks to them directly, not through the relay process.
- For any subcommand that changes relay membership (`add-member`,
  `remove-member`), the relay's own signing key (`BUZZ_RELAY_PRIVATE_KEY`),
  because the membership roster it publishes is a relay-signed Nostr event.
- Which community you intend to operate on, expressed as that community's
  `RELAY_URL` — `buzz-admin` is single-community per invocation and resolves
  its target from that URL's host, never from a default.

## Build or locate the binary

1. From the repository root, build it directly: `cargo build --release -p
   buzz-admin`. The binary lands at `target/release/buzz-admin`; add that
   directory to `PATH` for the rest of a session, or invoke it by full path.
2. Alternatively, if you are operating a relay already running from this
   repository's Docker image, the binary is already present at
   `/usr/local/bin/buzz-admin` inside the container — the same release build
   the image's relay process runs, stripped in the default image and left
   unstripped in the `debug-*` tags for profiling.
3. In a Docker Compose deployment, skip the binary entirely for the member-
   management subcommands and use `./run.sh` from `deploy/compose/` — see
   *Manage relay membership* below.

## Point it at a database, Redis, and a community

1. Set `DATABASE_URL` to the target Postgres connection string. Every
   subcommand that touches the database reads it, defaulting to
   `postgres://buzz:buzz_dev@localhost:5432/buzz` when unset — a default meant
   for local development, not a production target.
2. Set `REDIS_URL` (default `redis://localhost:6379`) if you are running
   `add-member` or `remove-member` — those are the only subcommands that open
   a Redis pub/sub connection, because publishing the updated membership
   roster to already-connected clients goes over Redis, not the database.
3. Set `RELAY_URL` to the relay you intend to operate on (default
   `ws://localhost:3000`). `buzz-admin` derives the community to operate on
   from this URL's host and looks that host up against the durable
   communities table; an unmapped host is a hard error, not a fallback to
   some default community. This is what makes `buzz-admin` single-community
   per invocation: point it at a different `RELAY_URL` to operate on a
   different community, and expect an explicit failure rather than silent
   cross-community effects if the relay named has not started and seeded its
   community yet.
4. Set `BUZZ_RELAY_PRIVATE_KEY` to the relay's own signing key before running
   `add-member` or `remove-member`. Both fail immediately, with a message
   naming this variable, if it is unset — the CLI signs a relay-authored
   event and cannot substitute an ephemeral key for that purpose the way
   `reconcile-channels`' untargeted backfill can.

## Manage relay membership

1. To add a pubkey, run `buzz-admin add-member --pubkey <npub-or-hex>
   [--role member|admin]` (role defaults to `member`; `owner` is rejected —
   change `RELAY_OWNER_PUBKEY` and restart the relay instead). In a Compose
   deployment, `./run.sh add-member <npub-or-hex> [--role member|admin]` is
   the equivalent, running the same command inside the relay container.
2. To remove a pubkey, run `buzz-admin remove-member --pubkey <npub-or-hex>
   [--role <role>]` (the optional `--role` only removes the member if their
   current role matches — omit it to remove regardless of role). The relay
   owner cannot be removed this way. `./run.sh remove-member <npub-or-hex>
   [--role member|admin]` is the Compose equivalent.
3. To see the current roster, run `buzz-admin list-members` (or `./run.sh
   list-members`). Output is a fixed-width text table of pubkey, role, who
   added them, and when; an empty community prints `(no relay members)`.
4. Check the exit code if scripting this: `0` success, `1` a bad `--role` or
   unparseable pubkey, `2` remove-member on a pubkey that is not a member,
   `3` an attempt to remove the relay owner, `4` a `--role` guard mismatch on
   remove-member, `5` a database or Redis failure. A `5` after `add-member`
   or `remove-member` may still mean the roster itself was updated in the
   database but the live-client broadcast failed — the command prints a
   `warning:` line (not an `error:` line) in exactly that case, distinct from
   a hard failure before the database write happened at all.
5. Verify the change by running `list-members` again and confirming the
   pubkey's row (or its absence) — the printed roster is read fresh from the
   database on every invocation, not cached. To roll back an accidental
   `add-member` or `remove-member`, run the inverse command with the same
   `--pubkey`: each roster event `publish_membership_list_with_bump` signs is
   a full-membership snapshot (not a delta), so a corrective `remove-member`
   or `add-member` fully replaces what the mistaken command published, with
   no separate cleanup step. There is no `buzz-admin` command that reverts a
   membership change automatically — the inverse subcommand is the rollback.
6. As a WebSocket-native alternative to any of the above, an already-
   authenticated owner or admin can send NIP-43 admin events directly
   (kind:9030 add, kind:9031 remove, kind:9032 change role) instead of
   invoking the CLI — useful when the operator already holds an authenticated
   relay connection and does not want a separate database/Redis credential.

## Other administrative subcommands

These exist and are safe to run per their own `--help` text, but this guide
does not walk through them step by step — read the source cited below before
depending on their exact behavior:

- `buzz-admin generate-key` — mints a fresh Nostr keypair and prints it;
  touches no database or Redis connection. Useful for bootstrapping an
  identity to sign with, or for a disposable test identity.
- `buzz-admin migrate` — applies pending database migrations. Run this (or
  set `BUZZ_AUTO_MIGRATE=true` on an image with embedded migrations) before
  first starting a relay against a fresh database.
- `buzz-admin reconcile-channels [--channel <uuid>] [--relay-key <hex>]` —
  backfills missing NIP-29 channel-discovery events, or force-republishes one
  channel's member snapshot when `--channel` is given. A targeted
  `--channel` repair requires an explicit relay key (`--relay-key` or
  `BUZZ_RELAY_PRIVATE_KEY`); the untargeted backfill will proceed with a
  warning and an ephemeral key if neither is set.
- `buzz-admin product-feedback list [--limit N]` — prints deployment-wide
  product feedback as JSON, deliberately across every community rather than
  the one `RELAY_URL` would select.
- `buzz-admin deletions <subcommand>` — the durable whole-community deletion
  control plane (`submit`, `list`, `inspect`, `approve`, `abort`, `unblock`,
  `run`, `drain`, `sweep`), delegated in full to the `buzz-deletion` crate.
  This is a large, separately evolving subsystem in its own right; see
  *Boundary* below.

## See also

- `launchpad/docs/corpus/architecture/containers/cli.md` — the container node
  for `buzz-cli`, the agent-facing CLI this node is not about.
- `launchpad/docs/corpus/capabilities/communities/community-members.md` — the
  concept behind the relay-membership roster `add-member`/`remove-member`/
  `list-members` operate on, including its data model and the WebSocket
  admin-event alternative.

## Boundary

This node does not describe:
- **`buzz-cli`, the agent-first CLI.** It is a different crate
  (`crates/buzz-cli`, binary `buzz`), for a different audience (AI agents and
  developers scripting against a relay's public event surface over HTTP/WS),
  authenticating with a NIP-98-signed HTTP request rather than direct
  database/Redis access. `buzz-admin` never signs an authenticated relay
  request at all — every write it makes goes straight to the database
  (and, for membership, to Redis), bypassing the relay's own authorization
  path entirely. See `architecture-containers-cli` for `buzz-cli`'s own
  shape.
- **The full `buzz-admin deletions` workflow.** Its nine subcommands, lease
  and checkpoint model, and cross-store (Postgres/S3) inventory-freezing
  behavior are `buzz-deletion`'s own subject and are not walked through here
  beyond the one-line pointers above — see *Scope and omissions*.
- **How to acquire the underlying skills from scratch** — how Nostr keys,
  NIP-43, or NIP-29 channel discovery work conceptually. This assumes an
  operator who already knows what a relay membership roster is and wants to
  change it; for the concept itself, see
  `capabilities-communities-community-members`.
- **Why `buzz-admin` is a separate binary from the relay it operates on**, or
  any other design rationale — this is a how-to, not an explanation node.

## Relationships

- **`references architecture-containers-cli`** — cited above throughout
  *Boundary* to distinguish `buzz-admin` from `buzz-cli` without restating
  that node's content.
- **`capabilities-communities-community-members`** — the relay-membership
  concept `add-member`/`remove-member`/`list-members` act on; this node
  assumes that background rather than re-deriving the NIP-43 data model.
- **`implements corpus-template-procedure`** — this node is an instance of
  that template's How-to form.

## Scope and omissions

**This node covers** building `buzz-admin` from source or locating the
prebuilt binary shipped in the relay Docker image, the environment variables
that connect it to a database, Redis, and a target relay/community, the full
`add-member`/`remove-member`/`list-members` membership-management task
(including exit codes and the Compose `run.sh` wrapper), and a short,
non-exhaustive pointer to its remaining subcommands.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `buzz-cli`, the agent-facing CLI, and its own build/auth/interface shape | `architecture-containers-cli` |
| The NIP-43 relay-membership data model and its WebSocket admin-event path | `capabilities-communities-community-members` |
| The `buzz-admin deletions` control plane in full — its nine subcommands, lease/checkpoint model, and cross-store inventory freezing | No corpus node yet; `crates/buzz-deletion/src/lib.rs` is the source. Whether this deserves its own procedure or capability node is left open, named in the batch dispatch report for this task rather than decided here, per this Feature's "one node, one idea" rule |
| `product-feedback`'s own data model and what a deployment does with the feedback it returns | No corpus node yet |
| The relay-side authorization and storage `buzz-admin` bypasses by writing to the database directly | `buzz-relay`, `buzz-auth`, `buzz-db` (their own container nodes, not yet written) |
| Provisioning the Postgres/Redis/relay infrastructure `buzz-admin` connects to | Deployment-layer corpus nodes (not yet written) |

**Expected but not verified when this node was written:**

- **No subcommand was actually executed against a live relay, database, or
  Redis instance while drafting this node.** Every behavioral claim above is
  read from `crates/buzz-admin/src/main.rs` and `crates/buzz-deletion/src/
  lib.rs`'s source and doc comments, or from `NOSTR.md`/`ARCHITECTURE.md`/
  `TESTING.md`'s own worked examples, not from a command actually run and
  observed during authoring. The Good Docs Project's How-to discipline (cited
  in `corpus-template-procedure`) asks for exactly this kind of execution
  before publishing; it was not done here.
- **Whether every `buzz-deletion` `Command` variant's behavior matches this
  node's one-line summary in practice** — only the enum's own doc comments
  were read, not its full execution against a live deletion request.
- **Whether a production operator would ever set `BUZZ_RELAY_PRIVATE_KEY`
  and reach `buzz-admin` from outside the relay's own container** — every
  documented usage in this repository (`NOSTR.md`, `ARCHITECTURE.md`,
  `deploy/compose/run.sh`) runs it via `docker compose exec relay
  buzz-admin ...` or `cargo run`/`cargo build` locally; no deployment
  material describing a standalone, out-of-container `buzz-admin` install
  was found.
