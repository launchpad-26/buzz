---
id: layers-security-secret-management
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
  - statement: ".env.example (local development) declares several secret-shaped variables with dev-only, non-functional values: DATABASE_URL (which embeds a Postgres password), PGPASSWORD, REDIS_URL, TYPESENSE_API_KEY, BUZZ_S3_ACCESS_KEY, and BUZZ_S3_SECRET_KEY."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "A repository-wide search for TYPESENSE_API_KEY across every .rs, .toml, .yml and .yaml file found zero consumers -- the variable is declared in .env.example and nowhere read by any Rust source in the workspace, consistent with AGENTS.md's own crate table describing buzz-search as 'Postgres FTS full-text search' rather than a Typesense integration."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='TYPESENSE_API_KEY', scope='**/*.rs;**/*.toml;**/*.yml;**/*.yaml') -> 0 matches outside .env.example, at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
      - "AGENTS.md"
  - statement: "crates/buzz-relay/src/config.rs's Config::from_env loads DATABASE_URL and REDIS_URL via std::env::var, falling back to dev-only default values (including a literal postgres://buzz:buzz_dev@localhost:5432/buzz connection string) embedded directly in the source when the variable is unset."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "The relay's Config struct derives Debug and Clone and stores database_url as a plain, unwrapped String -- no Secret/Zeroizing wrapper type or custom redacting Debug implementation is used for it or for any other field on the struct."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "crates/buzz-media/src/config.rs's MediaConfig, which holds S3 credentials for media and Git/CAS object storage, likewise derives Debug and stores s3_access_key and s3_secret_key as plain Strings with no redaction wrapper."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/config.rs"
  - statement: "crates/buzz-relay/src/main.rs's startup log, immediately after Config::from_env succeeds, names only a fixed set of non-secret fields as structured tracing arguments -- bind_addr, relay_url, health_port, metrics_port, max_frame_bytes, audit_enabled -- rather than formatting the whole Config value with {:?} or {:#?}; database_url, and every other credential-shaped field, is absent from that log call."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "A repository-wide search for a Debug-formatted dump of the relay's or media crate's config value (patterns matching '{:?}' or '{:#?}' next to a config-named binding) across crates/buzz-relay/src and crates/buzz-media/src found no such call site."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='\\{:\\??#?\\}\",? *config', scope='crates/buzz-relay/src/**/*.rs;crates/buzz-media/src/**/*.rs') -> 0 matches, at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "crates/buzz-push-gateway/src/config.rs loads its Apple Push Notification signing key as a filesystem path -- apns_key_path: PathBuf, sourced from the required env var BUZZ_PUSH_APNS_KEY_PATH -- rather than embedding the key material itself in an environment variable value."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/config.rs"
  - statement: "The same module loads two independent keyrings, grant_keys and token_keys, by parsing BUZZ_PUSH_GRANT_KEYS and BUZZ_PUSH_TOKEN_KEYS as comma-separated id:base64-encoded-key pairs through a shared parse_keyring helper, and its own doc comment states the token-custody keyring 'MUST NOT be reused for externally presented delivery capabilities' -- a purpose separation enforced by convention in the doc comment, not by the type system."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/config.rs"
  - statement: "deploy/compose/.env.example ships every secret-shaped production variable as a literal CHANGE_ME_* placeholder -- BUZZ_RELAY_PRIVATE_KEY, BUZZ_GIT_HOOK_HMAC_SECRET, POSTGRES_PASSWORD, REDIS_PASSWORD, BUZZ_S3_ACCESS_KEY, and BUZZ_S3_SECRET_KEY -- alongside RELAY_OWNER_PUBKEY, a non-secret public value also left as a CHANGE_ME placeholder pending operator input."
    entry_class: FACT
    evidence:
      - "deploy/compose/.env.example"
  - statement: "deploy/compose/compose.yml enforces the presence of these secrets structurally through Compose's ${VAR:?message} syntax on POSTGRES_PASSWORD, REDIS_PASSWORD, BUZZ_S3_ACCESS_KEY, and BUZZ_S3_SECRET_KEY across the relay, postgres, redis, and minio/minio-init service definitions, so Compose refuses to start any of those services at all if the corresponding variable is unset."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
  - statement: "deploy/compose/README.md states that RELAY_OWNER_PUBKEY is intentionally not prefixed with BUZZ_, distinguishing it in naming convention from every secret-shaped variable in the same file, which does carry a BUZZ_ or other domain-specific prefix."
    entry_class: FACT
    evidence:
      - "deploy/compose/README.md"
  - statement: "deploy/charts/buzz/templates/secret-chart.yaml renders a Kubernetes Secret only when secrets.existingSecret is not set, autogenerating BUZZ_RELAY_PRIVATE_KEY, BUZZ_GIT_HOOK_HMAC_SECRET, and in-cluster datastore credentials via randAlphaNum, persisting them across upgrades through a Helm lookup against the existing Secret; the template's own comment states this path is 'Not GitOps-safe -- ArgoCD/Flux users should provide secrets.existingSecret instead.'"
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/secret-chart.yaml"
  - statement: "SECURITY.md's only secret-handling section, 'Desktop Secret Storage -- OS Keyring,' documents storage of nsec identity private keys in the desktop app's OS keyring; no section of SECURITY.md addresses relay-operator or deployment-time secrets (database credentials, object-storage keys, push-notification signing keys, or Kubernetes/Compose secret provisioning)."
    entry_class: FACT
    evidence:
      - "SECURITY.md"
  - statement: "crates/git-sign-nostr/src/lib.rs, which signs Git objects with an identity private key, deliberately bypasses nostr::Keys (described in its own module documentation as caching non-zeroizable copies) and instead parses raw key material into a zeroize::Zeroizing<String> wrapper, with a load_key function that zeroizes intermediate buffers on every early-return path; no comparably defensive handling exists anywhere in the relay's or media crate's own secret-loading code, which stores every credential as a plain String for the lifetime of the process."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs"
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-media/src/config.rs"
  - statement: "The absence of a Secret/Zeroizing wrapper on the relay's and media crate's config structs, combined with the startup log's selective (non-Debug) field list, is read as an intentional choice to keep secrets out of routine logging rather than an oversight -- the log call would have been simpler to write as a single {:?} dump of the whole Config, and the narrower field list was written instead."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/config.rs"
    confidence: 0.6
  - statement: "This node scopes itself to secrets other than identity private keys -- relay operator env vars, database credentials, API keys for third-party services, and Kubernetes Secrets in the deploy path -- and treats #1110/#1112 as the separate task covering identity private keys; issue #1175's own body states neither the exclusion nor the #1110/#1112 attribution, which comes from the author's planning analysis for this task instead (not shipped as a repo artifact)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "corpus-batch-author agent, task #1175 planning pass"
relationships:
  - type: references
    target: architecture-deployment-kubernetes
  - type: references
    target: architecture-deployment-docker-compose
---

# Secret management

The credential values a Buzz relay operator or deployment must supply and
protect -- database and cache passwords, object-storage keys, third-party
API and signing keys, and their Kubernetes/Compose provisioning -- as
distinct from the Nostr identity private keys covered elsewhere in this
corpus.

## Definition

A **secret**, in this node's scope, is an operator-supplied credential value
that some Buzz service process reads at startup or runtime and that grants
access to a resource or a third-party service, but that is **not** a
human, agent, or CI principal's Nostr identity private key (`nsec`). It is
read from the process environment (`std::env::var`, or a config crate's
equivalent over parsed environment maps), and takes one of four shapes
observed across the codebase:

1. **A raw scalar value**, embedded directly in an environment variable --
   a Postgres or Redis password, an S3 access or secret key.
2. **A split access/secret pair** -- two variables that together form one
   credential, as with `BUZZ_S3_ACCESS_KEY`/`BUZZ_S3_SECRET_KEY`.
3. **A filesystem-path reference** -- the environment variable names a file
   Buzz reads at runtime rather than carrying the secret itself, as with
   the push gateway's `BUZZ_PUSH_APNS_KEY_PATH`.
4. **A base64-encoded keyring** -- a comma-separated list of `id:key`
   pairs decoded into an in-memory keyring, as with the push gateway's
   `BUZZ_PUSH_GRANT_KEYS`/`BUZZ_PUSH_TOKEN_KEYS`.

**What it is not.** A secret in this sense is narrower than "any
security-relevant environment variable." `RELAY_OWNER_PUBKEY`, the APNs key
ID, team ID, and topic are all operator-supplied configuration that sits
right beside real secrets in the same files, and none of them is one: each
is a public or non-sensitive identifier, safe to log or paste, that merely
happens to be adjacent in naming and location. `deploy/compose/.env.example`
draws exactly this line in practice -- see *Boundary* below.

## Use cases

- **Configuring a local development relay.** `.env.example`'s secret-shaped
  values are dev-only placeholders (`buzz_dev`, `buzz_dev_secret`) that work
  out of the box with `docker compose up` and carry no protection
  expectation.
- **Provisioning a production Docker Compose deployment.**
  `deploy/compose/.env.example` ships every real secret as a `CHANGE_ME_*`
  placeholder the operator must replace, and `compose.yml` refuses to start
  the services that need them until the corresponding variable is set.
- **Provisioning a production Kubernetes deployment.** An operator either
  supplies a pre-created `Secret` via `secrets.existingSecret`, or accepts
  the chart's own autogenerated `Secret`, which is explicitly documented as
  unsafe for GitOps.
- **Provisioning push-notification credentials.** The push gateway needs an
  Apple-issued `.p8` signing key on disk, plus two independently-purposed
  keyrings for grant and token custody -- a different shape from the
  relay's own scalar-valued secrets.

## Comparison: the four loading shapes

| Shape | Example variable(s) | Where |
|---|---|---|
| Raw scalar | `POSTGRES_PASSWORD`, `REDIS_PASSWORD`, embedded in `DATABASE_URL` | `crates/buzz-relay/src/config.rs` |
| Split access/secret pair | `BUZZ_S3_ACCESS_KEY` / `BUZZ_S3_SECRET_KEY` | `crates/buzz-relay/src/config.rs`, `crates/buzz-media/src/config.rs` |
| Filesystem-path reference | `BUZZ_PUSH_APNS_KEY_PATH` | `crates/buzz-push-gateway/src/config.rs` |
| Base64-encoded keyring | `BUZZ_PUSH_GRANT_KEYS`, `BUZZ_PUSH_TOKEN_KEYS` | `crates/buzz-push-gateway/src/config.rs` |

None of the four shapes is treated as canonical elsewhere in the codebase; a
given service's own needs (a single connection string versus a rotating
signing keyring) appear to have decided the shape independently, service by
service.

## What is, and is not, protected once loaded

**Nothing wraps a secret value once it is in memory, on the relay or media
side.** `crates/buzz-relay/src/config.rs`'s `Config` and `crates/buzz-media/
src/config.rs`'s `MediaConfig` both `#[derive(Debug)]` and store every
credential field as a plain `String`, for the process's whole lifetime. This
is a real difference from how this repository treats an *identity* private
key: `crates/git-sign-nostr/src/lib.rs` deliberately avoids `nostr::Keys`
(whose own documentation notes it caches non-zeroizable copies) and instead
parses key material into a `zeroize::Zeroizing<String>`, zeroizing
intermediate buffers on every return path. No comparably defensive pattern
exists for a database password or an S3 secret key.

**What does exist is a narrower, structural avoidance of logging them.**
`crates/buzz-relay/src/main.rs`'s startup log names a fixed set of
non-secret fields (`bind_addr`, `relay_url`, `health_port`, `metrics_port`,
`max_frame_bytes`, `audit_enabled`) rather than debug-formatting the whole
`Config` value, and no `{:?}`/`{:#?}` dump of either config struct was found
anywhere in the relay or media crate sources. Reading the selective field
list as a deliberate choice, rather than an oversight that simply never hit
a `{:?}` call, is this node's own inference, not a stated design decision
found in any source -- see the `INFERENCE` entry in the evidence ledger.

**A secret-shaped variable can also be declared and unused.**
`TYPESENSE_API_KEY` is set in `.env.example` and consumed nowhere in the
Rust workspace -- `buzz-search` is Postgres full-text search, not a
Typesense integration, per this repository's own crate table. It is named
here because "declared as a secret" and "actually gates access to
something live" are not the same claim, and conflating them would
overstate what any one variable's presence means.

## Structural enforcement at the deployment layer

Buzz's own deployment automation enforces secret *presence* -- not secret
*strength or freshness* -- at two different layers, each already documented
in its own corpus node (see *Related resources*):

- **Compose.** `deploy/compose/compose.yml` uses `${VAR:?message}` on
  `POSTGRES_PASSWORD`, `REDIS_PASSWORD`, `BUZZ_S3_ACCESS_KEY`, and
  `BUZZ_S3_SECRET_KEY`, so Compose itself refuses to start the services that
  need them if any is unset. `deploy/compose/run.sh` adds a second,
  script-level gate that refuses to run if `.env` still contains the literal
  string `CHANGE_ME`.
- **Kubernetes.** The Helm chart offers two mutually exclusive paths:
  `secrets.existingSecret`, which production/GitOps deploys must use, or
  the chart's own `templates/secret-chart.yaml`, which autogenerates values
  and is explicitly commented as unsafe under GitOps, because `helm
  template` (what ArgoCD/Flux render with) makes its persistence-via-`lookup`
  mechanism return empty on every sync.

This node does not restate either mechanism's full detail -- see
*Related resources*.

## Boundary

**Against identity private keys.** `BUZZ_PRIVATE_KEY` (the ACP harness's
per-agent signing key) and `BUZZ_RELAY_PRIVATE_KEY` (the relay's own posting
identity) are both `nsec`-format Nostr private keys, cryptographically and
in custody terms identical to any other identity private key this corpus
covers. Their cryptographic handling, formats, and desktop-side keyring
storage are explicitly out of scope for this node -- #1110/#1112
(`layers/identity/private-key.md`) is treated as the task that owns them.
That node is unmerged at this node's recorded revision, so no
`relationships` edge targets it; a future edit to this node, once it lands,
should add one.

**Against non-secret operator configuration.** `RELAY_OWNER_PUBKEY` and the
push gateway's `apns_key_id`/`apns_team_id`/`apns_topic` sit in the same
files as real secrets and share their operator-supplied, environment-variable
origin, but none of them is sensitive: a public key is meant to be shared,
and the Apple-issued identifiers are not credentials on their own.
`deploy/compose/README.md` states plainly that `RELAY_OWNER_PUBKEY` is
"intentionally not prefixed with `BUZZ_`," a naming signal this node reads
as marking it apart from the secret-shaped variables around it.

**Against transport security.** `SECURITY.md`'s "Transport Security" section
covers TLS termination and is a different concept from a credential value;
this node does not cover it.

## Related resources

- **Kubernetes deployment topology** (`architecture-deployment-kubernetes`)
  covers the chart's `secrets.existingSecret`/autogenerated-`Secret` split in
  full, including the specific fields each mechanism populates and the
  GitOps hazard in more depth than restated here.
- **Docker Compose deployment topology**
  (`architecture-deployment-docker-compose`) covers the `${VAR:?}` gate,
  `run.sh`'s `CHANGE_ME` guard, and the contrast with the root
  `docker-compose.yml`'s unprotected dev-only credentials in full.
- **Identity private key** (issue [#1112](https://github.com/launchpad-26/buzz/issues/1112),
  not yet merged) is this node's nearest boundary case, described above
  under *Boundary*.
- `SECURITY.md`'s "Desktop Secret Storage" section is the primary source for
  how this repository already treats one kind of secret (an identity
  private key) with a defensive custody pattern this node's subject
  currently lacks.

## Scope and omissions

**This node covers** what counts as an operator/deployment-time secret in
Buzz as distinct from an identity private key, the four loading shapes
observed in code, what happens (and does not happen) to a secret value once
it is loaded into memory, and the two structural presence-enforcement
mechanisms at the Compose and Kubernetes deployment layers.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Identity private key formats, custody, and desktop keyring storage | Issue [#1112](https://github.com/launchpad-26/buzz/issues/1112), `layers/identity/private-key.md` (unmerged) |
| The Kubernetes chart's full secrets mechanism, field by field | `architecture-deployment-kubernetes` |
| The Compose deployment's full secrets mechanism, field by field | `architecture-deployment-docker-compose` |
| Per-variable reference documentation of `.env.example` | `.env.example` and `deploy/compose/README.md` themselves, which are authoritative and not restated here |
| TLS/transport security | `SECURITY.md`, "Transport Security" |
| Secret rotation procedure end to end, for any of the four loading shapes | Not evidenced in this pass -- the Kubernetes node's own Backups section covers loss/recovery for `BUZZ_RELAY_PRIVATE_KEY` specifically, not rotation of database or object-storage credentials |
| Whether `buzz-acp`, `buzz-agent`, or `buzz-backend-kubernetes`'s own `config.rs` modules follow the same loading and (non-)redaction patterns documented here for the relay and media crates | Not read for this node; a future edit could extend the survey |

**Expected but not verified when this node was written:**

- **Whether any operator-facing documentation outside this corpus (a runbook,
  an internal wiki) already states a secret-rotation procedure.** This node's
  search was limited to this repository's own tracked files.
- **Whether `TYPESENSE_API_KEY`'s zero-consumer status reflects dead
  configuration that should be removed, or a integration that is planned but
  not yet wired up.** The grep search establishes the current absence of any
  consumer; it does not establish intent, and no issue was found on this
  pass naming a plan either way.
- **Whether `buzz-acp`'s or `buzz-agent`'s own configuration loading holds any
  secret-shaped values beyond the identity private key already covered
  elsewhere.** Not surveyed in this pass.
