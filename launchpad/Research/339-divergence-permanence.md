---
description: Which of the nine product-code divergences are permanent and which are meant to converge — none is a disagreement with upstream, eight are upstreamable fixes nobody has offered, and one pair is scaffolding created by the merge process itself.
tags: [divergence, upstream, convergence, ledger, criterion-4, research, issue-339]
---

# Which product-code divergences are permanent, and which are meant to converge?

## Finding

**None of the nine is a disagreement with upstream — and that breaks the model the divergence
ledger is being built on.**

ADR-0021 (open in #308) defines divergence as a case where "the cohort disagrees with upstream's
implementation", to be recorded as "a row in the ledger stating the fork's standing position and
the mechanism that enforces it". **Not one of the nine files fits that description.** What is
actually there:

| Files | What it is | Would converge? |
|---|---|---|
| `pack.rs`, `lib.rs`, `resolve.rs` | a cohort **feature** on upstream code (`--format json`, for #239's projector) | yes, if offered |
| `shell.rs`, `lifecycle.rs` | an upstream **portability bug fix** (`cfg(unix)` guards) | yes, clearly |
| `restore.rs`, `runtime_commands.rs` | an upstream **behaviour bug fix** (dial the configured relay) | yes, clearly |
| `runtime.rs`, `runtime/summary.rs` | **scaffolding the merge itself forced** — a file split to satisfy upstream's own line-count ratchet | no — and it will recur |

So the classification #339 asked for does not come out nine ways. It comes out two:

- **Eight files are convergent in principle and permanent in practice.** Every one is a fix or
  feature upstream would plausibly take. None has been offered, and `launchpad/AGENTS.md` §3
  records why: the cohort is *"not currently sending fixes upstream."*
- **One pair is genuinely permanent**, and is not a position about the product at all.

## Provenance

Four commits produced all nine files. Read from `git log` between the merge-base
`f8692fa9b52ddcfeb4b95fb4862109983509f131` (2026-08-17) and `launchpad`:

```
pack.rs, lib.rs, resolve.rs
  f36d10f9c Serina McFall | feat(launchpad): add --format json to buzz pack inspect (#239 STEP 1) (#257)

lifecycle.rs, shell.rs
  35cab546a Ben Mitchell  | fix(desktop): gate buzz-terminal's unix-only imports and const on cfg(unix)

restore.rs, runtime_commands.rs
  975e6d444 joshuavial    | dial the configured relay when spawning managed agents

runtime.rs, runtime/summary.rs
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
pair #338 found to be **entirely unprotected** — it compiles and passes if reverted, so it is the
one place where "permanent or converging" has an immediate practical consequence.

### 4. `runtime.rs` / `summary.rs` — the merge created this, not a design view

This is the one that is genuinely permanent, and the causal chain is worth following because it
predicts recurrence.

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

**Nobody chose this divergence.** It is an artefact of a file sitting four lines below a hard
ceiling in a repository that two parties are both adding to. It is permanent because reverting it
re-breaks the ratchet, and it is **structurally recurrent**: any upstream file near its limit will
do the same thing on a future drop. That is a cost of the merge-based posture ADR-0021 adopts, and
it is not in ADR-0021's list of consequences.

## What this changes for #290 and #273

**The ledger needs a column the ADRs do not describe.** ADR-0021's row is "standing position plus
enforcing mechanism", which presumes disagreement. Eight of these nine need a different field —
something like *offered upstream: no; would converge if accepted* — and the ninth needs *artefact
of the merge process*. Recording all nine as "standing positions" would be inaccurate in a way
that matters, because it implies a deliberate product view the cohort has never taken.

**Criterion 4's scope shrinks again.** #338 already narrowed the genuinely unprotected set to two
files. This narrows the *should-be-protected* set further: a regression test is only clearly
correct for divergence the cohort intends to keep. For the eight convergent files, a test asserting
the fork's version would **fire on the merge that resolves the divergence** and report convergence
as a regression. For `runtime.rs`/`summary.rs`, a test is the wrong instrument entirely — the
ratchet already enforces it.

**Which leaves, once again, `restore.rs` and `runtime_commands.rs`** as the only place where
criterion 4 is unambiguously right: upstreamable, unoffered, unprotected, and behavioural.

**A prior question surfaces.** Eight of nine divergences would disappear if the cohort offered
them upstream. `launchpad/AGENTS.md` §3 states the cohort does not, and ADR-0017 gives the
reasoning for one specific case (the lefthook pin), not a general policy. Whether *these* eight
should be offered is a decision nobody has taken, and it dominates criterion 4's cost: eight
regression tests, or eight pull requests to `block/buzz`.

## Confidence and what was not checked

**High confidence:** the four introducing commits and their authors (`git log`), the diff content
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
