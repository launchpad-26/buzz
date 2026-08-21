# Which upstream paths can affect what this cohort actually operates

**Title:** The fork's operational surface, and the share of an upstream drop that can reach it
**Summary:** Establishes the deployed surface from the relay image build: three binaries drawn from 16 of the 30 workspace crates, plus the `web` and `admin-web` bundles and `migrations/`. Of the 796 upstream files in the current backlog, **19 can reach the deployed relay** — 2.4%. 575 are desktop, 110 mobile, 52 benchmarks. Adding the agent-execution tooling the cohort plans to run on contributors' machines raises the live count to 36. Records the consequence for ADR-0022: the affordability argument gets much stronger, but the risk concentrates, because one of the 19 is a new database migration.
**Tags:** `upstream-sync` `vendor-drop` `operational-surface` `relay` `deployment` `adr-0022`
**Established:** 2026-08-22 · **Answers:** [#355](https://github.com/launchpad-26/buzz/issues/355) · **Parent:** [#273](https://github.com/launchpad-26/buzz/issues/273)

**References are pinned.** Fork-side claims cite `launchpad-26/buzz` at
[`5d76799d6e44f2f76aa7bd78c5343d339af98f63`](https://github.com/launchpad-26/buzz/tree/5d76799d6e44f2f76aa7bd78c5343d339af98f63); upstream-side claims cite `block/buzz` at
[`025425591ed67518a63870316f1473ffd02dd520`](https://github.com/block/buzz/tree/025425591ed67518a63870316f1473ffd02dd520). Merge-base for every drop figure is `f8692fa9b52ddcfeb4b95fb4862109983509f131`.
Paths appearing inside fenced blocks are command *output* and are deliberately left unlinked — linking them would
misrepresent what the command printed.

---

## Finding

**19 of the 796 files in the current drop can reach the deployed relay. 737 cannot reach anything this fork runs.**

The operational surface is narrow and it is knowable exactly, because it is defined by a build rather than by opinion: the relay image builds three binaries and two static bundles, and the crate dependency closure of those binaries is 16 of the repository's 30 workspace crates.

| Tier | What it is | Files in the 796 |
|---|---|---|
| **Deployed** | Crate closure of `buzz-relay`, `buzz-admin`, `buzz-pair-relay`; `web/`; `admin-web/`; `migrations/`; build inputs | **19** |
| **Cohort tooling** | `buzz-cli`, `buzz-acp`, `buzz-agent`, `buzz-dev-mcp` — the agent-execution tree the cohort plans to run on contributors' machines | **17** |
| **Build and gate** | `Justfile`, `lefthook.yml`, `bin/.lefthookrc`, `scripts/*`, `.github/workflows/*`, `schema/`, `renovate.json` | **24** |
| **Inert for this fork** | `desktop/` 575, `mobile/` 110, `benchmarks/` 52, non-deployed crates 19 | **736** |

The two numbers that matter to #273 pull in opposite directions, and both should be said out loud:

- **ADR-0022's affordability argument is far stronger than the record claims.** It rests on 8 contested files out of 796. The better number is that 736 of the 796 cannot affect anything the cohort operates *at all*, contested or not. Adopting them unreviewed is close to free.
- **But the risk concentrates rather than disappearing.** One of the 19 live files is [`migrations/0032_channel_roster_snapshot_fence.sql`](https://github.com/block/buzz/blob/025425591ed67518a63870316f1473ffd02dd520/migrations/0032_channel_roster_snapshot_fence.sql) — a new schema migration that the relay **applies automatically on startup**. That is the highest-consequence single file in the entire drop, it is not in any ledger, it does not conflict, and under ADR-0022 it is adopted without anyone reading it.

---

## Evidence

### What the deployed image actually contains

```
$ grep -nE 'cargo build|COPY --from=(builder|web-builder)|pnpm -C' Dockerfile
70:RUN cargo build --release --locked -p buzz-relay --bin buzz-relay \
71:                                   -p buzz-admin --bin buzz-admin \
72:                                   -p buzz-pair-relay --bin buzz-pair-relay
119:RUN pnpm -C web build && pnpm -C admin-web build
145:COPY --from=web-builder /build/web/dist       /srv/buzz/web
146:COPY --from=web-builder /build/admin-web/dist /srv/buzz/admin-web
169:COPY --from=builder /build/target/release/buzz-relay /usr/local/bin/buzz-relay
```

Three binaries and two static bundles. `desktop/` and `mobile/` are never copied into the image.

### The crate closure is 16 of 30

```
$ for p in buzz-relay buzz-admin buzz-pair-relay; do
    cargo tree -p $p --edges normal,build --prefix none --no-dedupe | awk '{print $1}'; done \
  | sort -u | comm -12 - <(ls crates | sort)
buzz-admin buzz-audit buzz-auth buzz-conformance buzz-core buzz-datastore-tracing
buzz-db buzz-deletion buzz-media buzz-pair-relay buzz-pubsub buzz-relay
buzz-relay-mesh buzz-sdk buzz-search buzz-workflow
```

Fourteen workspace crates are **not** in the deployed image:

```
buzz-acp buzz-agent buzz-backend-kubernetes buzz-cli buzz-dev-mcp buzz-pairing-cli
buzz-persona buzz-push-gateway buzz-test-client buzz-voice buzz-ws-client
git-credential-nostr git-sign-nostr sprig
```

### The 796 classified against that boundary

```
   575  desktop
   110  mobile
    52  benchmarks
    19  crates (not in the deployed closure)
    16  crates (in the deployed closure)
    24  build/gate/ops and other root files
   ---
   796
```

The **19 files that can reach the deployed relay**, in full:

```
Cargo.lock
crates/buzz-core/src/lib.rs
crates/buzz-core/src/nip10.rs
crates/buzz-db/src/channel.rs
crates/buzz-db/src/lib.rs
crates/buzz-db/src/migration.rs
crates/buzz-media/src/error.rs
crates/buzz-media/src/validation.rs
crates/buzz-relay/src/handlers/identity_archive.rs
crates/buzz-relay/src/handlers/ingest.rs
crates/buzz-relay/src/handlers/side_effects.rs
crates/buzz-relay/src/main.rs
crates/buzz-relay/src/workflow_sink.rs
crates/buzz-workflow/src/action_sink.rs
crates/buzz-workflow/src/executor.rs
crates/buzz-workflow/src/lib.rs
crates/buzz-workflow/src/schema.rs
migrations/0032_channel_roster_snapshot_fence.sql
web/package.json
```

Note what is in there: the relay's **ingest handler**, its **side-effect handler**, the **workflow executor**, `buzz-db`'s **migration** module, and a **new SQL migration**. This is not a random 2.4% — it is the relay's hot path.

### The 24 build/gate/ops files, in full

```
.github/workflows/benchmark-harbor.yml
.github/workflows/ci.yml
.release/desktop-candidate.json
AGENTS.md
CHANGELOG.md
Cargo.lock
Justfile
bin/.lefthookrc
deploy/charts/buzz/README.md
lefthook.yml
migrations/0032_channel_roster_snapshot_fence.sql
renovate.json
schema/schema.sql
scripts/attach-schema-partitions.sql
scripts/buzz-adopt-prod-agents.sh
scripts/check-file-sizes-core.mjs
scripts/check-file-sizes-core.test.mjs
scripts/check-push-head-scope.sh
scripts/model-capabilities.json
scripts/normative-corpus.json
scripts/run-tests.sh
scripts/test-mobile-worktree-overrides.sh
test-fixtures/entity-links.json
web/package.json
```

`bin/.lefthookrc` is right there — the file ADR-0022 names as its own counter-example, arriving clean in this drop.

### The cohort-tooling tier is real, not hypothetical

[`launchpad/ARCHITECTURE.md:99`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/ARCHITECTURE.md#L99) records the agent execution tree as an upstream capability the cohort intends to use:

> Buzz can initiate an agent and run it as the `buzz-acp` → `buzz-agent` → `buzz-dev-mcp` process tree, carrying the production MCP toolset — shell, file tools, todo — with the `buzz` CLI on the shell's `PATH` — `IMPLEMENTED` upstream

and the cohort's own use of it as `OPEN` at [#43](https://github.com/launchpad-26/buzz/issues/43). Upstream touched those four crates 17 times in this drop:

```
$ grep '^crates/' /tmp/up796.txt | cut -d/ -f2 | sort | uniq -c | sort -rn
   7 buzz-acp
   6 buzz-cli
   5 buzz-relay
   4 buzz-workflow
   3 buzz-db
   2 buzz-media
   2 buzz-dev-mcp
   2 buzz-core
   2 buzz-agent
   1 buzz-test-client
   1 buzz-backend-kubernetes
```

So `buzz-cli` — which the cohort uses daily and which [`launchpad/AGENTS.md`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/AGENTS.md) treats as the agent-facing surface — is **not** in the deployed image but is squarely operational for this fork. A boundary drawn only at the container would miss it.

---

## What this means for #273

*Everything in this section is my recommendation as the author, not a finding. Nothing here carries a source reference, because no source endorses it — the evidence is above and the judgement is mine.*

**"Operational" needs three tiers in the ledger and the drop report, not one.** Deployed, cohort-tooling, and inert are different risk classes with different review costs, and collapsing them either overstates the risk of a desktop change or hides the risk of a migration.

**#306's report should lead with the 19, not with the 8.** The contested surface (8 files both sides touched) and the live surface (19 files that can affect the running relay) barely overlap — the intersection is `Cargo.lock` and the two `managed_agents` desktop files, and the desktop ones are inert. A report organised by "what did we both touch" puts a desktop file-size ratchet above a schema migration. Organised by "what can hurt the thing we run", the migration leads.

**ADR-0022's known hole is bigger than `bin/.lefthookrc`.** That record's counter-example is a developer-experience regression — #196, a failing first push. `migrations/0032_channel_roster_snapshot_fence.sql` is the same structural class — clean merge, not in the ledger, adopted unreviewed — with a materially worse blast radius, since the relay applies migrations on startup against a live database. Whether that changes the scope ruling is not for this document to say; that it should be on the record as an instance is.

**A cheap mechanical improvement falls out of this.** The three-tier classification is computable — `cargo tree` for the closure, `git diff --name-only` for the drop, a path map for the rest. Whatever #306 specifies, it can compute this tier split per drop without a model and without judgement, which makes it the cheapest useful thing the change agent could produce.

---

## Confidence and limits

**High confidence** on the deployed closure: it comes from `cargo tree` against the same three package names the [`Dockerfile`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/Dockerfile) builds, intersected with the workspace member list. The classification of the 796 is mechanical path matching, reproducible from the commands above.

**Not checked.** I did not build the image, so the closure is `cargo tree`'s answer rather than an observed artifact; a crate reachable only through a `dev-dependencies` edge or a `cfg`-gated path could differ, and I used `--edges normal,build` deliberately, which excludes dev-dependencies. I did not read the content of `migrations/0032_channel_roster_snapshot_fence.sql` or judge whether it is risky — only that a new migration is present and that migrations apply on startup, which the root [`AGENTS.md`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/AGENTS.md) states and I did not independently confirm against `buzz-db`'s startup path. **I have no access to the deployed VPS**, so I could not confirm what is actually running there, which image tag it carries, or whether it matches this branch; the surface described here is what the repository builds, not what is deployed. I did not establish whether any contributor runs the desktop or mobile app — [`launchpad/ENVIRONMENTS.md`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/ENVIRONMENTS.md) lists four environments and the desktop app is not one of them, and the relay serves a browser `web/` client, so I inferred the desktop app is not part of the cohort's operational path. That inference is the weakest claim in this document and a single sentence from a contributor would settle it.
