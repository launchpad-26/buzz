---
description: Which of the nine product-code divergences appear permanent or convergent from their history — runtime.rs contains both an upstreamable behaviour fix and merge-created scaffolding, and author intent was not confirmed.
tags: [divergence, upstream, convergence, ledger, criterion-4, research, issue-339]
---

# Which product-code divergences are permanent, and which are meant to converge?

## Finding

**The commit history does not identify any of the nine as a disagreement with upstream, but author
intent was not confirmed. That still exposes a gap in the model the divergence ledger is being
built on.**

ADR-0021 (open in #308) defines divergence as a case where "the cohort disagrees with upstream's
implementation", to be recorded as "a row in the ledger stating the fork's standing position and
the mechanism that enforces it". **None of the inspected commit messages frames its change that
way.** What the diffs and history show is:

| Files | What it is | Would converge? |
|---|---|---|
| `pack.rs`, `lib.rs`, `resolve.rs` | a cohort **feature** on upstream code (`--format json`, for #239's projector) | yes, if offered |
| `shell.rs`, `lifecycle.rs` | an upstream **portability bug fix** (`cfg(unix)` guards) | yes, clearly |
| `restore.rs`, `runtime_commands.rs` | an upstream **behaviour bug fix** (dial the configured relay) | yes, clearly |
| `runtime.rs` | **mixed provenance** — configured-relay behaviour fix plus a later extraction forced by the line-count ratchet | behaviour would converge if offered; extraction will recur |
| `runtime/summary.rs` | **scaffolding the merge itself forced** — a file split to satisfy upstream's own line-count ratchet | no — and it will recur |

So the classification #339 asked for does not come out cleanly by file. Most changes appear
convergent from their commits, `summary.rs` is merge scaffolding, and `runtime.rs` contains both.

- **The behavioural and feature changes appear convergent in principle and remain permanent in
  practice.** They are changes upstream might plausibly take, but the authors were not asked.
- **The extraction is genuinely permanent**, and is not a position about the product at all.

## Provenance

Four substantive commits plus the upstream-sync merge produced the nine files. Read from `git log` between the merge-base
`f8692fa9b52ddcfeb4b95fb4862109983509f131` (2026-08-17) and `launchpad`:

```
pack.rs, lib.rs, resolve.rs
  f36d10f9c Serina McFall | feat(launchpad): add --format json to buzz pack inspect (#239 STEP 1) (#257)

lifecycle.rs, shell.rs
  35cab546a Ben Mitchell  | fix(desktop): gate buzz-terminal's unix-only imports and const on cfg(unix)

restore.rs, runtime_commands.rs
  975e6d444 joshuavial    | dial the configured relay when spawning managed agents

runtime.rs
  975e6d444 joshuavial    | dial the configured relay when spawning managed agents
  523fb9ad9 Serina Mcfall | chore: sync launchpad with upstream block/buzz main
  43366affa Serina Mcfall | fix(desktop): keep managed_agents/runtime.rs under the file-size ratchet

runtime/summary.rs
  43366affa Serina Mcfall | fix(desktop): keep managed_agents/runtime.rs under the file-size ratchet
```

Three authors. Each cluster has a different character, and the differences matter more than the
file count.

## The four clusters

### 1. `--format json` — a cohort feature that happens to live in upstream code

`#239` is a cohort task under PRD #4: a projector that resolves The Professor's persona pack into
a runnable `buzz-acp`/goose configuration. To do that it needs machine-readable pack output, so
STEP 1 added `buzz pack inspect --format json` — which meant touching `buzz-cli` and
`buzz-persona`.

The code itself is generic. `lib.rs` adds a `PackInspectFormat` enum, `resolve.rs` adds `Serialize`
derives, `pack.rs` adds masking so the JSON path does not print MCP `env` values or `args`. Its own
comment shows it was written with upstream's conventions in mind, not as a local hack.

**Convergent in principle.** Nothing about it is fork-specific. But the *motivation* is: upstream
has no projector and no reason to want one, so the feature would have to be offered on its own
merits.

### 2. `cfg(unix)` guards — an upstream bug

The whole divergence is attribute additions:

```
+#[cfg(unix)]
 use std::io;
+#[cfg(unix)]
 use std::time::Instant;
+#[cfg(unix)]
 use portable_pty::Child;
+#[cfg(unix)]
 const POLL_INTERVAL: Duration = Duration::from_millis(5);
```

This is a defect in `block/buzz`: unix-only imports were not gated, so a Windows build warns on
unused imports, and upstream's own `windows-rust` job denies warnings. **Unambiguously
upstreamable** — it is a fix to upstream's code for a platform upstream builds. The only reason it
is divergence rather than a contribution is that nobody sent it.

### 3. Dialing the configured relay — also an upstream bug

```
-    spawn_agent_child(&app, record, &key.relay_url, lazy, owner.as_deref())?
+    // Dial the configured relay, not `key.relay_url` (the loopback-normalized identity).
+    spawn_agent_child(&app, record, &relay_url, lazy, owner.as_deref())?
```

A correctness fix with a stated reason. Same conclusion: upstreamable, unoffered. This is also the
behaviour #338 found to be **unprotected across three files**, including its implementation in
`runtime.rs`, so this is where "permanent or converging" has an immediate practical consequence.

### 4. `runtime.rs` / `summary.rs` — mixed behaviour and merge-created scaffolding

The extraction is genuinely permanent, but `runtime.rs` also carries the configured-relay
behaviour fix from `975e6d444`. The causal chain for the extraction is still worth following
because it predicts recurrence.

`desktop/scripts/check-file-sizes.mjs` sets a **1000-line ceiling** for `src-tauri/src/**/*.rs`:

```javascript
const MAX_LINES = 1000;
  { root: "src-tauri/src", extensions: new Set([".rs"]), maxLines: MAX_LINES },
```

The ratchet is **upstream's**, present at the merge-base, and its rule is *"Keep new files at or
below the limit; files already over it may not grow."*

Line counts for `runtime.rs` along the history:

```
 996 lines  <- f8692fa9b  (the merge-base — upstream)
 994 lines  <- 975e6d444  dial the configured relay        (fork, pre-sync)
1007 lines  <- 523fb9ad9  chore: sync launchpad with upstream block/buzz main
 742 lines  <- 43366affa  keep managed_agents/runtime.rs under the file-size ratchet
```

`523fb9ad9` is a merge (`parents=115c329f5 f8692fa9b`). Combining upstream's additions with the
fork's left the file at **1007 lines — over upstream's own 1000-line limit** — so the fork's CI
tripped, and the fix was to extract 283 lines into `runtime/summary.rs`.

**Nobody chose the extraction divergence.** It is an artefact of a file sitting four lines below a hard
ceiling in a repository that two parties are both adding to. It is permanent because reverting it
re-breaks the ratchet, and it is **structurally recurrent**: any upstream file near its limit will
do the same thing on a future drop. That is a cost of the merge-based posture ADR-0021 adopts, and
it is not in ADR-0021's list of consequences.

## What this changes for #290 and #273

**The ledger needs a column the ADRs do not describe.** ADR-0021's row is "standing position plus
enforcing mechanism", which presumes disagreement. The behavioural changes appear to need a field
like *offered upstream: no; would converge if accepted*, while the extraction needs *artefact of
the merge process*. `runtime.rs` demonstrates why provenance must be recorded by change, not only
by file: one path can contain both. Recording all nine paths as "standing positions" would imply a
deliberate product view the cohort has never taken.

**Criterion 4's scope is three behavioural files.** #338 identifies `runtime.rs`, `restore.rs`, and
`runtime_commands.rs` as the genuinely unprotected set. A regression test is only clearly
correct for divergence the cohort intends to keep. For convergent changes, a test asserting
the fork's version would **fire on the merge that resolves the divergence** and report convergence
as a regression. For the extraction portion of `runtime.rs`/`summary.rs`, a test is the wrong
instrument entirely — the ratchet already enforces it.

**Which leaves `runtime.rs`, `restore.rs`, and `runtime_commands.rs`** as the place where criterion
4 is unambiguously right: upstreamable, unoffered, unprotected, and behavioural. The primary
assertion target is `spawn_agent_child` in `runtime.rs`.

**A prior question surfaces.** The feature and behaviour divergences could disappear if upstream
accepted them. `launchpad/AGENTS.md` §3 states the cohort does not currently send fixes upstream,
and ADR-0017 gives the reasoning for one specific case (the lefthook pin), not a general policy.
Whether these changes should be offered is a decision nobody has taken; author confirmation and
upstream review would be needed before treating convergence as established.

## Confidence and what was not checked

**High confidence:** the introducing commits and their authors (`git log`), the diff content
of each cluster, the 1000-line ceiling and the ratchet's rule (both read from source), the
`runtime.rs` line counts at each commit, and that `523fb9ad9` is a merge. All local and
re-derivable.

**Not checked — and this is the load-bearing gap:**

- **I did not ask the authors.** #339 asked for classification "sourced from the commits that
  introduced each change and from whoever wrote them". I did the first half only. The three people
  who can confirm intent are **Serina McFall** (clusters 1 and 4), **Ben Mitchell** (cluster 2) and
  **joshuavial** (cluster 3). Every "would converge" verdict above is my reading of the code and
  commit message, not a stated intention.
- **Whether any of these was already offered upstream.** I did not search `block/buzz`'s pull
  requests — the GitHub GraphQL quota was exhausted while this was being written, and a REST search
  across another repository's pull requests was not attempted. If Ben Mitchell's `cfg(unix)` fix is
  already an open upstream PR, cluster 2's classification changes from "unoffered" to "in flight",
  which is a materially different answer.
- **Whether upstream would accept them.** "Upstreamable" here means "generic, not fork-specific".
  It is not a prediction about `block/buzz`'s review.
- **The other 33 changed upstream files.** This covers only the nine product-code files. The
  process/meta and build/tooling divergences may well contain genuine standing disagreements — the
  lefthook pin in ADR-0017 is exactly that shape — which would mean the ledger's model fits them
  even though it does not fit these.
- **Whether the ratchet will actually recur.** I argue it is structural; I did not enumerate how
  many other `src-tauri/src` files sit close to 1000 lines, which would turn that from an argument
  into a measurement.
