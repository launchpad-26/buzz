---
id: layers-configuration-secrets
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
  - statement: "This repository's .gitignore excludes .env, .env.local and .env.*.local (and identity.key, **/identity.key, *.key) from version control, while .env.example — a template carrying placeholder/dev-only values only — is committed at the repository root; the root AGENTS.md's Getting Started section instructs `cp .env.example .env` as the first setup step."
    entry_class: FACT
    evidence:
      - ".gitignore"
      - ".env.example"
      - "AGENTS.md"
  - statement: "crates/buzz-relay/src/config.rs reads DATABASE_URL via std::env::var, falling back when unset to a hardcoded local Postgres connection string carrying the same dev-only credential .env.example documents; the fallback line carries a `sadscan:disable np.postgres.1` annotation, meaning the codebase's own secret scanner already treats this literal as a known, intentionally-committed dev placeholder rather than a live secret."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "PGPASSWORD, PGHOST, PGUSER and PGDATABASE (the discrete libpq-convention Postgres variables .env.example also documents) are not read anywhere in this repository's Rust source (crates/) or in docker-compose.yml; they exist for external Postgres client tooling (e.g. psql, Adminer) rather than being consumed by buzz-relay's own configuration loader, which reads only DATABASE_URL / READ_DATABASE_URL."
    entry_class: FACT
    evidence:
      - "grep_pg_discrete_vars(crates/**/*.rs, docker-compose.yml) -> no matches for PGPASSWORD, PGHOST, PGUSER, PGDATABASE, at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
      - "crates/buzz-relay/src/config.rs"
  - statement: ".env.example documents TYPESENSE_API_KEY and TYPESENSE_URL under a 'Typesense (search)' heading, but no Rust source under crates/ reads either variable; the root AGENTS.md's repo-structure table instead describes buzz-search as 'Postgres FTS full-text search', consistent with Typesense not being the search backend this repository's code actually uses."
    entry_class: FACT
    evidence:
      - "grep_typesense(**/*.rs, **/*.yaml, **/*.yml) -> no matches outside .env.example, at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
      - ".env.example"
      - "AGENTS.md"
  - statement: "BUZZ_RELAY_PRIVATE_KEY is read once via std::env::var in Config::from_env (config.rs:709) as an Option — absent is not itself an error at the config layer. buzz-relay/src/main.rs then branches on it: if BUZZ_REQUIRE_RELAY_MEMBERSHIP=true and the key is absent, startup returns an error before any DB mutation ('NIP-43 events signed with an ephemeral key become unverifiable after restart'); otherwise, if BUZZ_REQUIRE_AUTH_TOKEN=false, the relay falls back to a hardcoded, publicly-visible dev keypair (a constant literal in source, logged with a warning) so that addressable events replace correctly across dev restarts; if BUZZ_REQUIRE_AUTH_TOKEN=true and the key is still absent, the relay panics with 'BUZZ_RELAY_PRIVATE_KEY must be set when BUZZ_REQUIRE_AUTH_TOKEN=true'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-relay/src/main.rs"
  - statement: "BUZZ_S3_ACCESS_KEY and BUZZ_S3_SECRET_KEY are read via std::env::var in crates/buzz-relay/src/config.rs (lines 739 and 741); crates/buzz-deletion/src/lib.rs reads the same two variable names via a required_env helper (lines 565-566) that returns an error rather than a default when either is unset, and its own test helpers fall back to BUZZ_TEST_S3_ACCESS_KEY / BUZZ_TEST_S3_SECRET_KEY before the production names."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-deletion/src/lib.rs"
  - statement: "BUZZ_GIT_HOOK_HMAC_SECRET is read via std::env::var in config.rs (line 856); when unset, the relay generates a random 32-byte secret at process startup ('Generate a random secret if not configured (dev mode)', config.rs:858) rather than falling back to any fixed literal. When it IS set, config.rs (lines 982-984) rejects any value shorter than 32 characters (16 bytes hex) with a validation error, and the code comment states this check 'only fires when someone sets BUZZ_GIT_HOOK_HMAC_SECRET to a weak value.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "crates/buzz-relay/src/main.rs calls Config::from_env() exactly once, at process startup (line 142); no SIGHUP handler, config-reload endpoint, or other reload mechanism referencing Config was found anywhere in crates/buzz-relay/src/*.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "grep_reload(crates/buzz-relay/src/*.rs) -> no matches for SIGHUP or reload, exit 0, at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "BUZZ_PRIVATE_KEY is the required identity variable for buzz-acp and the buzz CLI (documented in .env.example's ACP section as 'REQUIRED — identifies the agent on the relay'); crates/buzz-test-client/src/main.rs reads it via std::env::var and calls .expect('invalid BUZZ_PRIVATE_KEY') on parse failure; crates/buzz-agent/src/mcp.rs allowlists BUZZ_PRIVATE_KEY (and BUZZ_RELAY_URL, BUZZ_AUTH_TAG) into spawned MCP subprocess environments, while NOSTR_PRIVATE_KEY is deliberately excluded from that same allowlist because dev-mcp writes it to a keyfile and then removes it from its own process environment so children never see it."
    entry_class: FACT
    evidence:
      - ".env.example"
      - "crates/buzz-test-client/src/main.rs"
      - "crates/buzz-agent/src/mcp.rs"
  - statement: ".env.example's 'Legacy aliases' section states BUZZ_ACP_PRIVATE_KEY is accepted for backward compatibility but that BUZZ_PRIVATE_KEY is the preferred canonical name — the only documented rename/deprecation among the secret-shaped variables this node covers."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "crates/buzz-backend-kubernetes/src/env.rs's AUTHORITATIVE_KEYS constant lists BUZZ_PRIVATE_KEY, NOSTR_PRIVATE_KEY, BUZZ_AUTH_TAG and BUZZ_RELAY_URL among the keys the authoritative (deploy-payload) tier owns and clears before writing its own values, so a lower-precedence tier can never supply these where the authoritative tier is silent; the same file defines MAX_SECRET_BYTES = 1024 * 1024 (Kubernetes' own MaxSecretSize cap, enforced provider-side so an oversized env surfaces as a named error rather than an apiserver rejection mid-deploy) and an is_posix_env_key validator ([A-Za-z_][A-Za-z0-9_]*) that is stricter than Kubernetes' own looser IsConfigMapKey rule, closing a kubelet-version-dependent divergence in how an invalid env name is handled (silently filtered through v1.29, injected verbatim from v1.30 per KEP-4369)."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/env.rs"
  - statement: "crates/buzz-backend-kubernetes/src/pod.rs's build_secret function constructs one Kubernetes Secret per deploy attempt, keyed by the resolved environment (including BUZZ_PRIVATE_KEY) as string_data, with immutable: true set on the object — a Secret is written once per attempt and never updated in place, which lets a pod's envFrom reference be treated as an atomic binding to that exact payload."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/pod.rs"
  - statement: "crates/buzz-backend-kubernetes/src/gc.rs's ORPHAN_SECRET_MIN_AGE_SECS is twice OPERATION_DEADLINE_SECS (600s), so an unreferenced Secret is only GC-eligible once it is older than 1200s; a Secret referenced by any of the identity's own pods (including a not-yet-started one) is protected, and orphan-Secret GC is skipped entirely — not merely deferred to local time — whenever the apiserver's HTTP Date header is absent or unparseable, because a fast-clocked desktop-hosted provider would otherwise deterministically classify every in-flight Secret as expired on every pass."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/gc.rs"
  - statement: "docs/remote-agents.md's invariant I2 ('No secrets in configuration') requires that provider_config — the persisted, schema-rendered, UI-visible settings object — never carry secrets, enforced by validation: a flat object, scalar values only, at most 20 fields, at most 64KB, and any field whose key word-splits to contain secret|password|token|key|credential is rejected outright (a name-based lint with accepted false positives, e.g. ssh_key_path). Per that same section, secrets flow exclusively inside the deploy request payload (private_key_nsec, auth_tag, env_vars), which the desktop never persists and never renders, and cluster credentials for a provider MUST come from ambient substrate config (e.g. kubeconfig resolution), never from provider_config."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "docs/remote-agents.md's 'Pre-secret negotiation gate (normative)' states that, as of commit 28ae6cd21, provider_deploy invokes deploy directly with no check that the binary answering info is the same binary receiving the nsec (its own Known Defect 5); it specifies the deploy path MUST resolve the provider id once, copy the resolved candidate into a desktop-owned, private, non-writable staging file while computing its digest, invoke info on that staged artifact, validate an explicit supported protocol_version, invoke deploy on the SAME staged artifact, and delete it afterward — and states explicitly that path-plus-metadata comparison (dev/inode, size, mtime) is NOT an acceptable substitute, because it can miss an in-place content rewrite or a check-then-exec pathname swap."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "docs/remote-agents.md states that every value from a deploy request's env_vars (matched longest-first, minimum length 4) and every nsec1…/sprt_tok_… token is redacted from everything the provider emits (stderr, error strings, the response object) before it is stored in the desktop's persisted last_error or logged, because the provider legitimately holds secrets during deploy and must not be allowed to leak them back through its own error output."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "desktop/src-tauri/src/secret_store.rs documents that the desktop stores the human user's own nsec (and other secrets) as a single JSON blob under one OS keychain entry — not per-key entries — and states in its own module doc comment that the store is 'deliberately NOT on any env-read path': BUZZ_PRIVATE_KEY resolution for harnessed agents and CI is handled upstream by a separate env short-circuit and child-process env injection, and adding an env tier to the keyring store 'would duplicate that precedence and create a divergent-behavior trap.' The module doc also states that when the system-keyring compile-time feature is off, SecretStore is unusable and callers fall back to their own 0o600 file storage."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/secret_store.rs"
  - statement: "desktop/src-tauri/src/managed_agents/env_vars.rs states that a reserved set of env var keys — covering Buzz's identity, secrets, security gates, and control-plane values — is rejected at save time by validation and stripped from persisted overrides at runtime, while behavior knobs remain freely overridable; a sibling is_well_formed_env_key check requires a POSIX-shaped key ([A-Za-z_][A-Za-z0-9_]*), documented as closing a bypass where a key string like 'BUZZ_AUTH_TAG=x' passed to Command::env would be interpreted by getenv as reserved-key BUZZ_AUTH_TAG holding the forged value 'x=forged'."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/env_vars.rs"
  - statement: "docs/remote-agents.md's normative env-merge rule states that a provider materializing env_vars into a substrate object (e.g. a Kubernetes Secret) MUST likewise never let a user-supplied key collide with or reconstruct a reserved key, extending the same POSIX-shaped-name discipline the desktop's local-spawn path enforces to the remote-deploy path."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "crates/buzz-agent/src/mcp.rs's own code comment describes BUZZ_AUTH_TAG as 'a non-secret signed ownership attestation needed by portable owner-scoped CLI operations'; separately, crates/buzz-cli/src/lib.rs declares the BUZZ_AUTH_TAG clap argument with hide_env_values = true, so the CLI's own --help output does not echo a configured tag's value even though the code elsewhere treats it as non-secret."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/mcp.rs"
      - "crates/buzz-cli/src/lib.rs"
  - statement: "launchpad/AGENT_PR_TEMPLATE.md's Verification checklist (line 82) includes the unchecked box 'No secrets, keys, tokens or hostnames were added to tracked files', applied to every agent-authored pull request including one adding a corpus node."
    entry_class: FACT
    evidence:
      - "launchpad/AGENT_PR_TEMPLATE.md"
  - statement: "launchpad/docs/corpus/architecture/deployment/kubernetes.md (id architecture-deployment-kubernetes, merged on origin/launchpad) already documents the Helm chart's own secrets mechanism — secrets.existingSecret for production/GitOps and the chart's autogenerated templates/secret-chart.yaml for the relay private key, git-hook HMAC secret, and in-cluster DB/Redis/MinIO credentials — at Kubernetes-deployment-topology altitude, distinct from this node's configuration-catalog altitude covering BUZZ_PRIVATE_KEY handling, the pre-secret staging gate, and buzz-backend-kubernetes's per-attempt Secret lifecycle."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/kubernetes.md"
  - statement: "Because the relay's hardcoded dev keypair (used only when BUZZ_REQUIRE_AUTH_TOKEN=false) and the git-hook HMAC secret's random-per-boot fallback both regenerate on every process restart rather than persisting, a production deployment that leaves either variable unset gets a working relay but loses cross-restart identity stability for whatever that secret backs (NIP-43 addressable-event replacement identity for the relay key; git pre-receive hook callback verification for the HMAC secret) — this is a reasoned consequence of the two code facts above, not a claim either source states in those words."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-relay/src/main.rs"
    confidence: 0.8
  - statement: "Applying the Twelve-Factor litmus test ('whether the codebase could be made open source at any moment, without compromising any credentials') to the S3 variable group in .env.example: BUZZ_S3_ACCESS_KEY and BUZZ_S3_SECRET_KEY fail the test and are configuration secrets, while BUZZ_S3_ENDPOINT, BUZZ_S3_BUCKET, BUZZ_S3_REGION and BUZZ_S3_ADDRESSING_STYLE pass it — an endpoint URL, bucket name, region string, and addressing-style enum are not credential material even though they sit in the same .env.example section and share the BUZZ_S3_ prefix."
    entry_class: INFERENCE
    evidence:
      - ".env.example"
      - "crates/buzz-relay/src/config.rs"
    confidence: 0.9
  - statement: "This task (launchpad-26/buzz#1058) was dispatched as one worker in a batch run against Feature #611, alongside sibling configuration-catalog tasks #1051-#1057 and #1059 covering other configuration surfaces, and sibling task #1041 (backend-provider) covering docs/remote-agents.md's provider protocol for the Kubernetes deploy path in depth; none of those sibling nodes are merged on origin/launchpad at the recorded revision, so none is declared as a relationships target here."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "task brief dispatching launchpad-26/buzz#1058 as part of the Feature #611 batch run"
relationships:
  - type: references
    target: architecture-deployment-kubernetes
  - type: implements
    target: corpus-template-configuration
---

# Buzz: secret configuration

This node catalogues the **secret-shaped configuration surface** of Buzz's own
code — environment variables that carry credential material (private keys, HMAC
secrets, object-storage keys, database passwords) and the mechanisms that
create, transport, store, and garbage-collect them, across the relay
(`crates/buzz-relay`), the ACP harness and CLI (`crates/buzz-acp`,
`crates/buzz-cli`, `crates/buzz-agent`), the desktop app's local secret store
(`desktop/src-tauri`), and the Kubernetes remote-agent backend provider
(`crates/buzz-backend-kubernetes`) together with the protocol that provider
implements (`docs/remote-agents.md`). It applies to every deploy target these
components run in — local development (`.env`), the desktop app's managed local
and remote agents, and a Kubernetes-hosted remote agent — since a secret
variable's *handling* (never its value) does not vary by deploy target the way
a non-secret setting's value does.

## Settings

| Variable | Type | Default | Required | Secret | Effect |
|---|---|---|---|---|---|
| `DATABASE_URL` | Postgres connection string (embeds password) | `postgres://buzz:buzz_dev@localhost:5432/buzz` (dev-only placeholder, flagged `sadscan:disable` in source) | no (has a dev default) | yes | The relay's write-plane credential for the canonical event store; production deployments must override the default. |
| `BUZZ_RELAY_PRIVATE_KEY` | 32-byte hex Nostr private key | none | conditional — required when `BUZZ_REQUIRE_RELAY_MEMBERSHIP=true` or `BUZZ_REQUIRE_AUTH_TOKEN=true`; otherwise falls back to a hardcoded dev keypair | yes | Stable relay identity for NIP-43 membership signing and addressable-event replacement; absent + `BUZZ_REQUIRE_AUTH_TOKEN=true` panics at startup, absent + `BUZZ_REQUIRE_RELAY_MEMBERSHIP=true` returns a startup error, absent + neither uses a hardcoded, logged dev keypair. |
| `BUZZ_S3_ACCESS_KEY` | Object-storage access key ID | none | effectively yes wherever media/git-on-object-storage is used | yes | Read access-key half of the S3-compatible credential (`buzz-deletion` requires it via `required_env`, erroring rather than defaulting). |
| `BUZZ_S3_SECRET_KEY` | Object-storage secret key | none | effectively yes wherever media/git-on-object-storage is used | yes | Secret half of the same S3-compatible credential. |
| `BUZZ_GIT_HOOK_HMAC_SECRET` | HMAC secret (hex, ≥32 chars if set) | random 32-byte value generated fresh per process start if unset | no (has a generated default) | yes | Authenticates git pre-receive hook callbacks to the relay; a value shorter than 32 characters is a hard config-validation error. |
| `BUZZ_PRIVATE_KEY` | Nostr private key (hex or `nsec1…`) | none | yes, for any ACP-harnessed agent or CLI operation that signs | yes | Identifies the agent process on the relay; `buzz-test-client` panics on an invalid value, and it is one of the few identity variables explicitly allowlisted into spawned MCP subprocess environments (unlike `NOSTR_PRIVATE_KEY`, which is deliberately kept out of that allowlist). |
| `BUZZ_AUTH_TAG` | Signed NIP-OA ownership-attestation JSON | none | no | no | A signed attestation of ownership, not a credential value in itself — the code's own comment calls it "non-secret" — but the CLI still declares it with `hide_env_values = true` so `--help` does not echo a configured value. |

Two adjacent surfaces are deliberately **not** rows above, and are named here
rather than silently omitted: `TYPESENSE_API_KEY`/`TYPESENSE_URL` appear in
`.env.example` under a "Typesense (search)" heading, but no Rust source in this
repository reads either variable — `buzz-search` is Postgres-FTS-based per the
root `AGENTS.md`, so this looks like a stale template entry rather than a live
secret this repository's code consumes (a candidate follow-up, not something
this node resolves). `PGPASSWORD`/`PGHOST`/`PGUSER`/`PGDATABASE` are libpq
convention variables for external Postgres tooling (`psql`, Adminer); the
relay's own loader reads only `DATABASE_URL`/`READ_DATABASE_URL`, so these are
out of Buzz's own configuration surface even though they are credential-shaped
and appear in the same `.env.example` block.

## Litmus test

Every row above is genuinely deploy-varying per the Twelve-Factor litmus test —
"whether the codebase could be made open source at any moment, without
compromising any credentials." Two exclusions considered and left out because
they fail that test in the *other* direction — they never vary between
deploys, or vary but carry no credential:

- `BUZZ_S3_ENDPOINT`, `BUZZ_S3_BUCKET`, `BUZZ_S3_REGION`,
  `BUZZ_S3_ADDRESSING_STYLE` — deploy-varying, but not credential material; they
  belong in a general S3/media configuration node, not this one.
- `BUZZ_AUTH_TAG` — included above (it is genuinely part of Buzz's identity
  configuration surface and a reader looking for "is this a secret" needs the
  answer) but marked `Secret: no`, since it is a signature over public data
  rather than key material whose disclosure compromises anything.

## Secrets discipline

No row above quotes a live credential value. Where a variable has a
placeholder default, the table and the evidence ledger cite the source location
of that placeholder (`.env.example`, or the specific `config.rs` fallback line)
rather than reproducing the literal string, even where that literal is itself
a checked-in, publicly-known dev-only placeholder (e.g. `DATABASE_URL`'s
default, which the codebase's own scanner suppression comment already treats
as non-sensitive). `BUZZ_RELAY_PRIVATE_KEY`'s dev fallback is a hardcoded
constant *in this repository's source*, not a generated secret — it is named
above only as "a hardcoded dev keypair," never reproduced, consistent with
this discipline even though the value is not actually sensitive.

## Restart and reload behavior

Every variable in the table above is read exactly once, at process startup:
`buzz-relay`'s `Config::from_env()` is called a single time from `main()`, and
no reload mechanism (SIGHUP handler, admin endpoint, or similar) referencing
`Config` exists in the relay's source. Changing any secret in this table
therefore requires a process restart — there is no dynamic-reload path for the
relay's own configuration. On the Kubernetes remote-agent path specifically,
"restart" takes the shape of a new deploy attempt: `buzz-backend-kubernetes`'s
`build_secret` marks each per-attempt `Secret` `immutable: true`, so an agent's
`BUZZ_PRIVATE_KEY` (and the rest of the authoritative-tier environment) cannot
be changed in place on a running pod — a new generation, new `Secret`, and new
pod are required.

## Boundary

This node does not describe:

- **The parsing/validation implementation in depth.** `crates/buzz-relay/src/
  config.rs`'s full 87-call-site `Config` struct, its non-secret fields, and
  its complete validation rules belong to an `implementation` node describing
  `Config::from_env`, should one be authored; this node cites specific
  call sites only where they back a secret-shaped claim.
- **A wire contract or event-kind shape.** `BUZZ_AUTH_TAG` carries a NIP-OA
  attestation whose wire shape is a separate `interfaces-events` concern, not
  restated here.
- **Non-secret deployment-topology configuration** (replica counts, ingress,
  network policy, and the rest of the Helm chart's values) — that is
  `architecture-deployment-kubernetes`'s subject at deployment-topology
  altitude; this node covers the same underlying mechanisms (the chart's
  `secrets.existingSecret` / `secret-chart.yaml`) only insofar as they overlap
  with secret handling, and defers to that node rather than repeating its
  content.
- **`docs/remote-agents.md`'s full provider protocol** — the pre-secret
  staging gate, invariant I2, and the redaction rule are summarized here only
  to the depth needed to describe secret handling; the wire-level `info`/
  `deploy` request-response contract, the five system-model principals, and
  the protocol's other four invariants (I1, I3, I4, I5) are sibling task
  #1041's subject, not this node's.
- **Whether the pre-secret staging gate described above is actually
  implemented today.** `docs/remote-agents.md` itself states it as normative
  and names its own absence at commit `28ae6cd21` as Known Defect 5; this node
  reports that gap as documented, and does not re-verify implementation status
  against the current relay codebase, since the gate lives in the desktop's
  provider-invocation path, outside this node's grep-verified evidence.
- **Any node-specific exclusion beyond the above** — none found.

## Relationships

- **references** → `architecture-deployment-kubernetes` — the merged node
  documenting the Kubernetes Helm chart's deployment topology, including its
  own `secrets.existingSecret` / `secret-chart.yaml` mechanism at a different
  altitude (deployment topology, not this node's configuration catalog). Loose
  coupling per `relationships.schema.json`'s directionality for `references`
  ("source cites target as supporting context; no ownership or currency
  dependency implied") — this node's claims stay accurate even if that node's
  chart-topology detail is later revised.
- **implements** → `corpus-template-configuration` — this node is an instance
  of that template, per `relationships.schema.json`'s own worked example for
  `implements` ("a template instance of a standard").
- **Checked and not declared:** no relationship to any of sibling tasks
  #1051-#1057, #1059 (other configuration surfaces) or #1041 (the
  `docs/remote-agents.md` provider protocol in depth) — all are open, unmerged
  draft PRs at the recorded revision, and `AGENTS.md` step 9 requires resolving
  targets against `origin/launchpad`, not this worktree.

## Scope and omissions

**This node covers** the secret-shaped subset of Buzz's own configuration
surface: which environment variables carry credential material under the
Twelve-Factor litmus test, their type/default/required/effect per the settings
table above, whether each is restart-required (all are, on the relay path) or
tied to a Kubernetes deploy generation (on the remote-agent path), the
mechanisms that create and transport a secret value (env var read, MCP
subprocess env allowlisting, the Kubernetes per-attempt Secret, the desktop OS
keyring blob store), the mechanisms that keep a secret out of places it should
never reach (`docs/remote-agents.md`'s I2 `provider_config` validation, the
pre-secret staging gate, provider-output redaction, the desktop's reserved-key
stripping and POSIX-key validation), and the one documented compatibility
rename among these variables (`BUZZ_ACP_PRIVATE_KEY` → `BUZZ_PRIVATE_KEY`).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Non-secret deployment-topology configuration for the Kubernetes chart | `architecture-deployment-kubernetes`, merged |
| `docs/remote-agents.md`'s full provider protocol (system model, all five invariants, wire contract) | sibling task #1041 (backend-provider), not yet merged |
| Other configuration surfaces (non-secret relay settings, rate limits, ACP harness behavior knobs, etc.) | sibling tasks #1051-#1057, #1059, not yet merged |
| `crates/buzz-relay/src/config.rs`'s full field-by-field contract (87 call sites) | corpus's `implementation` surface, no specific node found for it |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **Whether `docs/remote-agents.md`'s pre-secret staging gate is implemented
  in the current desktop codebase was not checked.** The document itself
  names its own absence at commit `28ae6cd21` as Known Defect 5; this node's
  evidence for the gate is the specification's normative text, not a read of
  `desktop/src-tauri`'s actual provider-invocation call path.
- **Whether `TYPESENSE_API_KEY`/`TYPESENSE_URL` are genuinely dead
  configuration, or read by code outside `crates/` (a script, a CI job, an
  external tool) that this node's search did not cover**, was not fully
  resolved — flagged above as a candidate follow-up rather than asserted as
  fact.
- **Whether every deploy target that consumes `BUZZ_S3_ACCESS_KEY` /
  `BUZZ_S3_SECRET_KEY` was enumerated.** This node confirmed two consumers
  (`buzz-relay`, `buzz-deletion`); other crates under `crates/` were not
  individually grepped for the same two variable names.
- **Whether Block's private `sprout-backend-blox` desktop backend provider
  (referenced by the root `AGENTS.md`'s ecosystem table, not present in this
  checkout) handles `BUZZ_PRIVATE_KEY` the same way `buzz-backend-kubernetes`
  does.** Out of reach of this checkout; not claimed either way.

Back to the corpus root: [`launchpad/docs/corpus/README.md`](../../../README.md).
