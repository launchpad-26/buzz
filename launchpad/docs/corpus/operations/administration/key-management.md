---
id: operations-administration-key-management
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "buzz-admin's `GenerateKey` subcommand generates a new Nostr keypair with `nostr::Keys::generate()`, prints the public key and secret key to stdout, and tells the operator to set `BUZZ_PRIVATE_KEY` to the printed secret key to use that identity; it performs no persistence of its own — it only prints."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "The `just bootstrap` recipe copies `.env.example` to `.env` on first run (if `.env` does not already exist) and then always runs `./scripts/ensure-local-relay-key.sh .env`, which is idempotent: if `BUZZ_RELAY_PRIVATE_KEY` is already set and non-empty in the target file it only `chmod 600`s the file and exits, and otherwise generates a fresh random 32-byte value validated against the secp256k1 curve order, writes it into `BUZZ_RELAY_PRIVATE_KEY=<value>` in the file (replacing an existing commented/blank line or appending one), and sets the file's permissions to `0600`."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "scripts/ensure-local-relay-key.sh"
  - statement: "`.env.example` documents `BUZZ_RELAY_PRIVATE_KEY` as the relay's \"Stable relay signing key (required)\", notes that `just bootstrap` generates a random key into the gitignored `.env` file, and instructs the operator to \"Preserve that value across restarts and backups\" — the variable itself is left commented out in the template, since the bootstrap script is what actually populates it."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "`crates/buzz-relay/src/main.rs` requires `BUZZ_RELAY_PRIVATE_KEY` unconditionally: `relay_keypair_from_config` is called at line 156, immediately after `Config::from_env()` and before any conditional branch, and returns the error \"BUZZ_RELAY_PRIVATE_KEY must be set. Run `just bootstrap` for local development or configure a stable 32-byte hex private key.\" whenever the value is absent. A second check further down (line 260) returns \"BUZZ_RELAY_PRIVATE_KEY is required when BUZZ_REQUIRE_RELAY_MEMBERSHIP=true. NIP-43 events signed with an ephemeral key become unverifiable after restart.\" — but that branch can only be reached once the unconditional check has already passed, so it never fires in practice and the NIP-43 message is not the error an operator with no key actually sees."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:38-45"
      - "crates/buzz-relay/src/main.rs:156"
      - "crates/buzz-relay/src/main.rs:260-265"
  - statement: "`crates/buzz-relay/src/main.rs` calls `Config::from_env()` exactly once, at process startup, and contains no `SIGHUP` handler, admin reload endpoint, or other mechanism that re-reads `Config` after startup — confirmed by inspecting the file for both call sites and any reload-related code, finding none besides the one startup call."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "Changing `BUZZ_RELAY_PRIVATE_KEY`, `BUZZ_PRIVATE_KEY`, `RELAY_OWNER_PUBKEY`, or `RELAY_OPERATOR_PUBKEYS` to take effect on the relay therefore requires editing the stored value and restarting the relay process — there is no dynamic-reload or rotation command for any of them, a direct consequence of the one-time `Config::from_env()` call recorded above."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/main.rs"
    confidence: 0.9
  - statement: "`.env.example`'s ACP section documents `BUZZ_PRIVATE_KEY` as \"Nostr private key (hex or bech32). REQUIRED — identifies the agent on the relay\", accepted as a 32-byte hex string or an `nsec1…` bech32-encoded value, and separately records that `BUZZ_ACP_PRIVATE_KEY` is a legacy alias for the same variable."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "`crates/buzz-relay/src/config.rs` parses `RELAY_OWNER_PUBKEY` (trimmed, lowercased) and, when the resulting string is non-empty, requires it to be exactly 64 lowercase hex characters; a non-empty value that fails that check produces a `ConfigError::InvalidValue` that propagates out of `Config::from_env()` via `?`, so relay startup fails rather than silently discarding the malformed value — the code's own comment states this is deliberate: \"a malformed value is a startup error because this key can serve as the break-glass operator root when RELAY_OPERATOR_PUBKEYS is empty.\" An unset or empty `RELAY_OWNER_PUBKEY` is filtered out before this check and is not itself an error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "`crates/buzz-relay/src/config.rs` parses `RELAY_OPERATOR_PUBKEYS` as a comma-separated list, trimming and lowercasing each entry, skipping empty entries, deduplicating repeated pubkeys, and returning a hard `ConfigError::InvalidValue` for any non-empty entry that is not exactly 64 hex characters — unlike an unset or malformed `RELAY_OWNER_PUBKEY`'s narrower empty-string exemption, any present-but-invalid entry here fails startup."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "`buzz-admin`'s `AddMember` subcommand rejects `--role owner` outright (\"role 'owner' cannot be set via CLI — use RELAY_OWNER_PUBKEY config\"), and its `RemoveMember` subcommand refuses to remove the pubkey configured as `RELAY_OWNER_PUBKEY`, printing \"cannot remove relay owner: <pubkey>\\nTo change the owner, update RELAY_OWNER_PUBKEY and restart.\" — the CLI itself names the config-edit-and-restart path as the way to change which pubkey owns the relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "`crates/git-sign-nostr/README.md` documents the setup for Nostr-based git commit/tag signing as five `git config` commands (`gpg.format x509`, `gpg.x509.program <path>`, `commit.gpgsign true`, `tag.gpgsign true`, `user.signingkey <hex-pubkey>`) plus exporting a private key, and states the key-loading priority as `NOSTR_PRIVATE_KEY` environment variable, then `BUZZ_PRIVATE_KEY` environment variable, then a keyfile at the path named by `git config nostr.keyfile`; `crates/git-sign-nostr/src/lib.rs`'s `load_key()` function implements exactly that three-step priority order, and removes each environment variable it reads from the process environment immediately afterward to shrink the exposure window."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/README.md"
      - "crates/git-sign-nostr/src/lib.rs"
  - statement: "`crates/git-sign-nostr/src/lib.rs`'s keyfile path (`open_keyfile`, used by `read_keyfile_secure`) rejects a keyfile that is a symlink (`O_NOFOLLOW`), rejects one that is not a regular file, rejects one whose permission bits set any of the group/other read/write/execute bits (`mode & 0o177 != 0`, i.e. anything looser than `0600`/`0400`), and rejects one not owned by the current process's UID — all before reading its contents."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs"
  - statement: "`crates/git-credential-nostr/README.md` documents installing the helper with `cargo install --path crates/git-credential-nostr`, then registering it and enabling per-path credentials with `git config --global credential.helper nostr` and `git config --global credential.useHttpPath true`, then storing an `nsec1…` value in a keyfile created with `chmod 600` and pointing `git config --global nostr.keyfile <path>` at it; for CI/CD it documents setting `$NOSTR_PRIVATE_KEY` instead, stating the env var \"takes precedence over `nostr.keyfile` and avoids touching the filesystem\" — `crates/git-credential-nostr/src/lib.rs`'s `load_key()` checks `NOSTR_PRIVATE_KEY` first and only falls back to the git-config keyfile path when it is absent or empty, matching that documented precedence."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/README.md"
      - "crates/git-credential-nostr/src/lib.rs"
  - statement: "`crates/git-credential-nostr/src/lib.rs`'s `check_keyfile_permissions` rejects a keyfile whose mode has any group or other bit set (`mode & 0o177 != 0`) with \"insecure permissions (expected 0600)\", matching the README's own Troubleshooting table entry for that exact error message and its fix (`chmod 600 ~/.nostr/key`)."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/src/lib.rs"
      - "crates/git-credential-nostr/README.md"
  - statement: "This repository's `.gitignore` excludes `.env`, `.env.local`, `.env.*.local`, `identity.key`, `**/identity.key`, and `*.key` from version control, so a `.env` file populated by `ensure-local-relay-key.sh` and a keyfile named per either git-signing tool's convention are both excluded from commits by the repository's own ignore rules rather than by any convention this node introduces."
    entry_class: FACT
    evidence:
      - ".gitignore"
  - statement: "`.env.example` documents no `nostr.keyfile`-equivalent environment variable anywhere in the file — that setting is exclusively a `git config` value in both `git-sign-nostr` and `git-credential-nostr`, never an environment variable name, which is why the git-signing keyfile setup steps in this node use `git config`, not `.env`."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "The ACP harness's owner-only `!rotate` control command, documented in `crates/buzz-acp/README.md` as rotating \"the ACP session for that channel\" so \"the next queued/received event starts a fresh session,\" and implemented in `crates/buzz-acp/src/lib.rs`/`src/pool.rs` as invalidating and recreating an in-memory agent session, does not touch any cryptographic key, keypair, or credential anywhere in its implementation — it is unrelated to the key-management procedures this node documents despite the shared word \"rotate.\""
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md"
      - "crates/buzz-acp/src/lib.rs"
  - statement: "This node was written using launchpad/docs/corpus/templates/procedure.md, which was already merged on origin/launchpad at the recorded revision and directs a how-to-shaped node to carry an Overview, an optional Before you start, one numbered task sequence per logical goal, a See also section, an explicit Boundary statement, Relationships, and a Scope and omissions section covering both what the node excludes and what it expected to verify and could not."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
relationships:
  - type: references
    target: layers-configuration-secrets
  - type: references
    target: architecture-deployment-kubernetes
  - type: implements
    target: corpus-template-procedure
---

# Managing Buzz's Nostr keys: how-to

How an operator generates, configures, and designates the Nostr keypairs a
Buzz deployment uses — the relay's own signing identity, an agent or CLI
identity, the relay owner and operator roster, and the keys used to sign git
commits/tags and authenticate git pushes over HTTP — and what to do (and what
tooling does not exist) when one of those keys needs to change.

## Before you start

- A checked-out copy of this repository, with the Hermit toolchain available
  if you intend to run `just` recipes (`. ./bin/activate-hermit`).
- For any task below that talks to a running relay or its database
  (`buzz-admin`'s membership commands), a reachable Postgres and, for
  membership publication, Redis — the same services `just setup` provisions
  for local development.
- Comfort reading a 64-character hex string: Nostr keys and pubkeys in this
  repository are 32-byte values, printed and configured as lowercase hex
  (private keys may also be entered as `nsec1…` bech32; public keys as
  `npub1…` in some tools), never as anything shorter.

## Generate a new Nostr keypair

Use this whenever a task below calls for "a new keypair" — it is the one
generic key-generation path this repository provides; nothing downstream
cares how the pair was produced, only that the resulting hex values are used
correctly.

1. Run `cargo run -p buzz-admin -- generate-key` (or the built binary,
   `buzz-admin generate-key`).
2. Read the printed `Public key:` and `Secret key:` lines. The command only
   prints these two values — it does not write them anywhere, register them
   with a relay, or persist them in any file.
3. Copy the secret key into whichever configuration variable the task that
   sent you here names, and clear your terminal scrollback/history afterward
   if it may be shared or logged. The command performs no redaction of its
   own output.

## Provision the relay's own signing key (`BUZZ_RELAY_PRIVATE_KEY`)

The relay signs NIP-43 membership rosters and other relay-authored events
with one stable keypair. Losing track of this key, or letting it regenerate
on every restart, makes those addressable events unverifiable across a
restart.

1. For local development, run `just bootstrap` (or any recipe that depends on
   it, such as `just setup`, `just relay`, or `just dev`). On first run this
   copies `.env.example` to `.env`, then runs
   `./scripts/ensure-local-relay-key.sh .env`, which generates a fresh
   32-byte key, writes it into `.env` as `BUZZ_RELAY_PRIVATE_KEY=<hex>`, and
   sets the file's permissions to `0600`.
2. Re-running `just bootstrap` (or any recipe depending on it) is safe: the
   script detects an existing non-empty `BUZZ_RELAY_PRIVATE_KEY` in `.env` and
   leaves it untouched, only re-asserting the `0600` permission bit.
3. For a non-local deployment, generate a keypair yourself (see *Generate a
   new Nostr keypair* above) and set the printed secret key as
   `BUZZ_RELAY_PRIVATE_KEY` in whatever configuration mechanism your
   deployment uses to reach the relay's process environment — this repository
   does not itself provide a production secret store; see *Boundary* below.
4. Preserve that value across restarts and backups. If it is lost, **no relay
   starts at all** — the key is required unconditionally, not only under
   `BUZZ_REQUIRE_RELAY_MEMBERSHIP=true`. If it is *changed*, the relay starts,
   but its previously published NIP-43 membership events and other relay-signed
   addressable events remain on disk while no longer verifying as coming from
   the same relay identity.
5. Restart the relay process to pick up a newly set or changed value — the
   relay reads its full configuration exactly once, at startup, and has no
   mechanism to reload it while running.
6. Verify: confirm `BUZZ_RELAY_PRIVATE_KEY=<64 hex chars>` is present in the
   file you set it in, then start the relay and confirm it does not exit with
   the "BUZZ_RELAY_PRIVATE_KEY must be set" startup error described above.

## Generate an agent or CLI identity key (`BUZZ_PRIVATE_KEY`)

Every ACP-harnessed agent and every `buzz` CLI invocation that signs an event
needs its own Nostr identity, set as `BUZZ_PRIVATE_KEY` in that process's
environment.

1. Generate a new keypair (see *Generate a new Nostr keypair* above).
2. Set the printed secret key as `BUZZ_PRIVATE_KEY` in the environment of the
   agent process, CLI invocation, or ACP harness configuration that will use
   it. The legacy variable name `BUZZ_ACP_PRIVATE_KEY` is still accepted for
   the same purpose, but `BUZZ_PRIVATE_KEY` is the name to write going
   forward.
3. If this identity should be recognized as a relay member (rather than
   rejected by membership enforcement), add its public key to the relay's
   membership list — see *Add the identity to the relay's membership and
   operator roster* below.
4. To change an agent's identity later, generate a fresh keypair and update
   the stored `BUZZ_PRIVATE_KEY` value, then restart the agent process — there
   is no in-place rotation of a running identity's key.

## Designate the relay owner and operators

`RELAY_OWNER_PUBKEY` and `RELAY_OPERATOR_PUBKEYS` name **public** keys only —
they identify who administers the relay, not a signing identity the relay
itself uses.

1. Obtain the 64-character hex public key of the person or identity who
   should own or operate this relay deployment (from `buzz-admin generate-key`
   above, or from an existing identity's already-known public key — never
   its secret key).
2. Set `RELAY_OWNER_PUBKEY` to that value for the relay's single owner. An
   unset value is not an error by itself, but a malformed non-empty value
   (anything other than exactly 64 lowercase hex characters) fails the
   relay's startup outright, precisely because this key can serve as the
   break-glass operator root when `RELAY_OPERATOR_PUBKEYS` is empty.
3. Optionally set `RELAY_OPERATOR_PUBKEYS` to a comma-separated list of
   additional 64-character hex pubkeys who should also have operator access.
   Every entry is validated the same way; one bad entry fails startup rather
   than being silently dropped, and duplicate entries are silently
   deduplicated.
4. Restart the relay to pick up either change.
5. To change the owner later, update `RELAY_OWNER_PUBKEY` to the new pubkey
   and restart — `buzz-admin`'s own membership commands refuse to help here on
   purpose: `AddMember --role owner` is rejected, and `RemoveMember` on the
   current owner's pubkey is refused with a message pointing back at this
   same config-and-restart step.

## Add the identity to the relay's membership and operator roster

Distinct from designating the relay's *owner*: this adds an ordinary member
or admin pubkey to the relay's own membership list (used for NIP-43
enforcement when `BUZZ_REQUIRE_RELAY_MEMBERSHIP=true`), which does not
require a restart.

1. Ensure `BUZZ_RELAY_PRIVATE_KEY` and `DATABASE_URL` are set in the
   environment `buzz-admin` runs in — the CLI signs the published membership
   roster with the relay's own key and needs a database connection.
2. Run `buzz-admin add-member --pubkey <hex-or-npub> --role member` (or
   `--role admin`). `--role owner` is rejected; use the owner-designation
   steps above instead.
3. Run `buzz-admin list-members` to confirm the addition.
4. To remove a member, run `buzz-admin remove-member --pubkey <hex-or-npub>`,
   optionally with `--role <role>` to only remove if the current role
   matches.

## Configure a git signing key (`git-sign-nostr`)

Sign git commits and tags with a Nostr keypair using this repository's
`git-sign-nostr` NIP-GS signing program.

1. Build or install `git-sign-nostr` (`cargo build --release -p
   git-sign-nostr`, or `cargo install --path crates/git-sign-nostr`).
2. Configure git to invoke it: `git config gpg.format x509`,
   `git config gpg.x509.program /path/to/git-sign-nostr`,
   `git config commit.gpgsign true`, `git config tag.gpgsign true`, and
   `git config user.signingkey <hex-pubkey>` (the *public* key of the
   identity that will sign).
3. Make the matching private key available by one of three mechanisms, in
   the priority order the program itself uses: the `NOSTR_PRIVATE_KEY`
   environment variable, the `BUZZ_PRIVATE_KEY` environment variable, or a
   keyfile whose path is set via `git config nostr.keyfile <path>`.
4. If using a keyfile, create it with permissions no looser than `0600` and
   owned by your own user — the program refuses to read a keyfile that is a
   symlink, is not a regular file, has any group/other permission bit set, or
   is owned by a different user.
5. Verify with `git commit -m "signed with nostr"` followed by
   `git verify-commit HEAD`.

## Configure a git credential key (`git-credential-nostr`)

Authenticate `git push`/`pull`/`clone` over HTTP against a Buzz git server
using this repository's `git-credential-nostr` NIP-98 credential helper,
without a password.

1. Requires git 2.46 or newer (the credential protocol's `authtype`
   capability). Install the helper: `cargo install --path
   crates/git-credential-nostr`.
2. Register it and enable per-path credentials:
   `git config --global credential.helper nostr` and
   `git config --global credential.useHttpPath true`.
3. Store your `nsec1…` private key in a keyfile with restrictive
   permissions — `mkdir -p ~/.nostr && echo "nsec1..." > ~/.nostr/key &&
   chmod 600 ~/.nostr/key` — and point git at it:
   `git config --global nostr.keyfile ~/.nostr/key`.
4. Use git normally (`git clone`, `git push`, `git fetch`) against the Buzz
   git server; the helper activates automatically when the server challenges
   with a `WWW-Authenticate: Nostr` header.
5. For CI/CD, set the `$NOSTR_PRIVATE_KEY` environment variable instead of a
   keyfile — it takes precedence over `nostr.keyfile` and avoids writing a
   key to disk at all.

## Change a key that is already in use

There is no rotation command for any key this node covers — no `buzz-admin
rotate-key`, no relay endpoint, and no config-reload path. (The ACP harness's
`!rotate` owner command exists, but it rotates an in-memory agent session,
not a cryptographic key — checked directly against its implementation and
found unrelated to anything in this node.) Every key change is the same
three-step shape:

1. Generate a new keypair, or obtain the new pubkey you are designating.
2. Update the stored configuration value (`.env`, your deployment's
   environment configuration, or `git config`, depending on which key).
3. Restart the process that reads it: the relay for
   `BUZZ_RELAY_PRIVATE_KEY`/`RELAY_OWNER_PUBKEY`/`RELAY_OPERATOR_PUBKEYS`, the
   agent/CLI process for `BUZZ_PRIVATE_KEY` — git-signing and
   git-credential-key changes take effect on the next git invocation with no
   process to restart, since both tools are re-invoked fresh by git each
   time.

Changing `BUZZ_RELAY_PRIVATE_KEY` specifically has a consequence beyond the
restart itself: events the relay previously signed with the old key (its
NIP-43 membership rosters and other relay-authored addressable events) remain
on disk but can no longer be verified as coming from the relay's new
identity.

## See also

- `launchpad/docs/corpus/layers/configuration/secrets.md` — the broader
  secret-shaped configuration catalog this node's `BUZZ_RELAY_PRIVATE_KEY` and
  `BUZZ_PRIVATE_KEY` steps are a procedural subset of; read it for
  type/default/required details this node does not repeat.
- `launchpad/docs/corpus/architecture/deployment/kubernetes.md` — the
  Kubernetes Helm chart's own secret-provisioning mechanism
  (`secrets.existingSecret`, the autogenerated secret chart) for a remote
  relay deployment, at deployment-topology altitude rather than this node's
  operator-procedure altitude.
- `crates/git-sign-nostr/README.md` and `crates/git-credential-nostr/README.md`
  — the full, tool-specific setup and troubleshooting documentation this
  node's git-signing and git-credential sections summarize into the shape of
  this node's other tasks.

## Boundary

This node does not describe: how to look up a key variable's type, default
value, or required-ness in the abstract — that reference table lives in
`layers-configuration-secrets`, not here. How to acquire the underlying
cryptography or Nostr key-format concepts from scratch for a newcomer — no
tutorial exists for that in this corpus. Why any of these keys exist, or how
the pieces relate conceptually (for example, why NIP-43 needs a stable relay
identity at all) — that is `layers-configuration-secrets`' and, for the wire
protocol itself, NIP-43's own concern, not this how-to's. Provisioning a
Kubernetes-hosted relay's secrets end-to-end, including the chart's own
generated `Secret` object — `architecture-deployment-kubernetes`'s subject.
Authorizing an already-known pubkey for the DB-managed `relay_operators`
roster surfaced through the private admin dashboard's API
(`crates/buzz-relay/src/api/admin/`) — that is an authorization procedure
layered on top of pubkeys this node already covers generating and
designating, not a key-management operation itself, and this node does not
describe it.

## Relationships

- references: `layers-configuration-secrets` — this node's relay-key and
  agent-key steps are a procedural subset of that node's broader
  secret-configuration catalog; loose coupling, since this node's steps stay
  correct even if that node's table gains or loses unrelated rows.
- references: `architecture-deployment-kubernetes` — named above as the owner
  of Kubernetes-specific secret provisioning, which this node explicitly
  does not cover.
- implements: `corpus-template-procedure` — this node is a how-to-shaped
  instance of that template.

## Scope and omissions

**This node covers** generating a Nostr keypair with `buzz-admin
generate-key`; provisioning and preserving the relay's own signing key
(`BUZZ_RELAY_PRIVATE_KEY`) via `just bootstrap`/`scripts/ensure-local-relay-
key.sh` or manually; generating an agent/CLI identity key (`BUZZ_PRIVATE_
KEY`); designating the relay owner and operator pubkeys (`RELAY_OWNER_
PUBKEY`, `RELAY_OPERATOR_PUBKEYS`) and adding a pubkey to the relay's
membership roster via `buzz-admin`; configuring `git-sign-nostr` and
`git-credential-nostr` to sign commits/tags and authenticate git HTTP
operations with a Nostr key; and what actually happens (config-edit-plus-
restart, with no dedicated rotation tooling) when any of these keys needs to
change.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full secret-configuration catalog (types, defaults, required-ness, non-key secrets like `BUZZ_GIT_HOOK_HMAC_SECRET` or `BUZZ_S3_SECRET_KEY`) | `layers-configuration-secrets` |
| Kubernetes-hosted secret provisioning for a remote relay deployment | `architecture-deployment-kubernetes` |
| Authorizing a pubkey through the DB-managed `relay_operators` admin-dashboard roster | no corpus node found covering this at the time of writing |
| The NIP-43, NIP-GS, and NIP-98 wire protocols these keys are used with | no corpus node found covering these NIPs at the time of writing |
| Front-matter contract, evidence classification, and corpus authoring procedure generally | `launchpad/docs/corpus/AGENTS.md` and the corpus standards |

**Expected but not verified when this node was written:**

- **No production (non-local) deployment configuration in this repository was
  found that shows how `BUZZ_RELAY_PRIVATE_KEY` is actually supplied outside
  local development's `.env` file.** `docker-compose.yml` and the Kubernetes
  Helm chart both exist in this repository, but this node's evidence search
  was scoped to the key-generation and key-designation tooling itself
  (`buzz-admin`, the bootstrap script, the relay's own config parsing), not to
  every deployment target's secret-injection mechanism — `architecture-
  deployment-kubernetes` is linked above as the node that covers the
  Kubernetes case specifically.
- **Whether Block's private `sprout-backend-blox` desktop backend provider
  (named in the root `AGENTS.md`'s ecosystem table, not present in this
  checkout) has its own key-provisioning path for a spawned agent's
  `BUZZ_PRIVATE_KEY`** was not checked — out of reach of this checkout.
- **Whether any corpus node already exists covering the `relay_operators`
  admin-dashboard authorization surface** was checked only by listing this
  corpus's existing files (`launchpad/docs/corpus/capabilities/moderation/`
  and `launchpad/docs/corpus/operations/` at the time of writing); none was
  found, but a moderation- or administration-surface node authored after this
  one was not ruled out.
- **None of the commands in this node's task sequences were actually executed
  against a running relay, database, or built `buzz-admin`/`git-sign-nostr`/
  `git-credential-nostr` binary.** Every step above is grounded in reading the
  source that implements it (cited in the evidence ledger), not in exercising
  the workflow end-to-end — the stronger discipline this node's own template
  (`corpus-template-procedure`) asks for where practical. `cargo` was not
  reachable in this authoring environment without a longer toolchain
  bootstrap than this task's evidence-gathering step budgeted for.
- **This node's exact CLI invocation strings for `buzz-admin` subcommands and
  flags (`generate-key`, `add-member --pubkey ... --role ...`, and so on)
  follow `clap`'s default kebab-case rendering of the Rust enum variant and
  field names actually read in `crates/buzz-admin/src/main.rs` (`GenerateKey`,
  `AddMember { pubkey, role }`, and so on), rather than being confirmed
  against a built binary's own `--help` output.** No `#[command(rename_all =
  ...)]` override was found on any of the relevant `enum`/`struct`
  declarations, which is the one thing that would change this, but the
  absence of an override was checked by reading the file, not by running
  `buzz-admin --help`.

Back to the corpus root: [`launchpad/docs/corpus/README.md`](../../README.md).
