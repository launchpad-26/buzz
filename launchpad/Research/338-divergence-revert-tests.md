---
description: Whether any existing test fails if each of the nine product-code divergences is reverted — none does. Two are guarded by the Windows clippy job, two are genuinely unprotected, and the rest only trip the compiler because a single-file revert is inconsistent.
tags: [testing, divergence, upstream, criterion-4, rust, research, issue-338]
---

# Does any existing test fail if a product-code divergence is reverted?

## Finding

**No divergence is protected by a test that survives its own revert.**

That sentence is the whole finding, and the reason is structural. Rust's convention puts unit tests
in a `#[cfg(test)] mod tests` block *inside the file they test*. Two of the nine divergences did
arrive with tests — `pack.rs` added four, `resolve.rs` added one — but those tests live in the
diverging file, so **reverting the file deletes its own guard**. Nothing fails; the assertion
simply stops existing.

What protection does exist is the **compiler**, not the test suite, and it splits three ways:

| Files | Revert outcome | Actually protected by |
|---|---|---|
| `shell.rs`, `lifecycle.rs` | unused imports on Windows | the `windows-rust` clippy job — **real protection** |
| `pack.rs`, `lib.rs`, `runtime.rs`, `runtime/summary.rs` | compile error | an artefact of reverting *one* file — a consistent merge would not trip it |
| `restore.rs`, `runtime_commands.rs` | compiles and passes silently | **nothing** |

The two in that last row are the real targets for #290's criterion 4, and they are the two that
change behaviour.

## Method

For each file, revert it to the upstream merge-base
(`f8692fa9b52ddcfeb4b95fb4862109983509f131`, 2026-08-17) and run the owning crate's tests:

```bash
cp "$file" /tmp/keep.bak
git show $MB:$file > "$file"
cargo test -p "$pkg"
cp /tmp/keep.bak "$file"
```

Two files were run this way. The remaining seven were analysed from their diffs and from what
references them; those verdicts are reasoned, not executed, and are marked as such below.

## The two executed reverts

### `crates/buzz-persona/src/resolve.rs` — nothing fails

The divergence adds `Serialize` derives to five types plus one test:

```
+use serde::Serialize;
-#[derive(Debug, Clone)]
+#[derive(Debug, Clone, Serialize)]
...
+    #[test]
+    fn resolved_pack_serializes_to_json_with_expected_fields() {
```

Reverted, the crate builds and every test passes:

```
$ cargo test -p buzz-persona          # with resolve.rs reverted to merge-base
test defaults_merge_persona_overrides ... ok
test resolve_full_pipeline ... ok
test full_pipeline_load_and_validate ... ok

test result: ok. 13 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.01s
EXIT=0
```

**13 passed, 0 failed.** The test that would have caught this went away with the code it was
guarding. This is the clearest possible demonstration of the structural problem.

### `crates/buzz-cli/src/commands/pack.rs` — compile error, for the wrong reason

Reverted, the crate does not build:

```
     |
  52 | pub fn cmd_inspect(path: &str) -> Result<(), CliError> {
     |        ^^^^^^^^^^^
help: remove the extra argument
     |
2022 -             PackCmd::Inspect { path, format } => commands::pack::cmd_inspect(path, format),
2022 +             PackCmd::Inspect { path, format } => commands::pack::cmd_inspect(path),
     |

For more information about this error, try `rustc --explain E0061`.
error: could not compile `buzz-cli` (lib) due to 1 previous error
```

This looks like protection and is not. `lib.rs` — a *different* diverged file, left at the fork's
version — still passes `format`, so the arity no longer matches. The compiler caught an
**inconsistent** state that I created. An upstream merge reverting the `#239` work would revert
`lib.rs` and `pack.rs` together, the arity would agree again, and nothing would object. The four
tests `pack.rs` added would be gone along with the masking code they assert.

## The seven reasoned verdicts

### `crates/buzz-cli/src/lib.rs` — symmetric to the above

Adds the `PackInspectFormat` enum and the `--format` argument. Reverting it alone breaks the build
from the other side (`pack.rs` would expect two arguments). Zero tests added. Same conclusion: the
compile error is a partial-revert artefact.

### `buzz-terminal/src/shell.rs` and `lifecycle.rs` — genuinely protected, by clippy

Both divergences are purely `#[cfg(unix)]` guards:

```
+#[cfg(unix)]
 use std::io;
 use std::time::Duration;
+#[cfg(unix)]
 use std::time::Instant;
+#[cfg(unix)]
 use portable_pty::Child;
+#[cfg(unix)]
 const POLL_INTERVAL: Duration = Duration::from_millis(5);
```

These make the crate compile cleanly on Windows. Remove them and those imports become unused in a
Windows build — and the `windows-rust` job runs clippy with warnings denied
(`.github/workflows/ci.yml`):

```yaml
      - name: Clippy (workspace)
        run: cargo clippy --workspace --all-targets --target $env:TARGET -- -D warnings
```

An unused import is a warning; `-D warnings` makes it an error. **These two divergences are
protected, and by something stronger than a test** — a compile-time check that cannot be
accidentally deleted, on a platform CI actually builds. Criterion 4's wording ("carries a test
that fails if a merge reverts it") would score these as unprotected, which would be wrong.

Not executed: I did not run a Windows build. The reasoning is from what the `cfg(unix)` attributes
guard and from clippy's documented treatment of unused imports.

### `managed_agents/restore.rs` and `runtime_commands.rs` — unprotected

These are the important ones. Both make the same one-line behavioural change:

```
-    let mut process = spawn_agent_child(&app, record, &key.relay_url, lazy, owner.as_deref())?;
+    // Dial the configured relay, not `key.relay_url` (the loopback-normalized
+    // identity). See the note in `spawn_agent_child`.
+    let mut process = spawn_agent_child(&app, record, &relay_url, lazy, owner.as_deref())?;
```

A real behaviour fix — which relay a managed agent dials — with **no test added** and no test
elsewhere asserting it. Searching the whole `managed_agents` tree for test code touching
`relay_url` finds only snapshot tests asserting the *opposite* concern, that the value must not
leak into a snapshot:

```
agent_snapshot_tests.rs:21:   relay_url: "wss://relay.example.com".to_string(),  // MUST NOT appear in snapshot
agent_snapshot_tests.rs:361:  fn secret_exclusion_relay_url_absent() {
```

Both types are the same, so reverting compiles cleanly. A merge that reverts these silently
restores the bug the comment describes, and every check stays green.

### `managed_agents/runtime.rs` and `runtime/summary.rs` — an extraction, untested either side

The pair I flagged as refactor-shaped when filing #338 is exactly that: 280 lines leave
`runtime.rs`, 283 arrive in a new `runtime/summary.rs`, and `runtime.rs` re-exports them:

```
desktop/src-tauri/src/managed_agents/runtime.rs:74:pub use summary::build_managed_agent_summary;
desktop/src-tauri/src/managed_agents/runtime.rs:75:pub(crate) use summary::workspace_pair_key;
desktop/src-tauri/src/managed_agents/runtime.rs:77:pub(crate) use summary::{persona_drift_state, resolve_workspace_pair_key};
```

Test functions in `runtime.rs`: **0 before the change, 0 after.** In `summary.rs`: **0**. The
extracted functions are called from production code (`discovery.rs`, `readiness.rs`,
`commands/agents.rs` and others) but the only mention of `build_managed_agent_summary` anywhere in
test code is a comment:

```
desktop/src-tauri/src/managed_agents/types/tests.rs:741:  // Both fields derive from one vector in `build_managed_agent_summary`;
```

So there is no behaviour here to protect with a test that is not already unprotected upstream.
Deleting `summary.rs` breaks the `pub use`, which is again a partial-revert artefact.

## What this changes for #290

**Criterion 4 needs rewording, and the reason is worth stating precisely.** "Every deliberate
divergence carries a test that fails if a merge reverts it" cannot be satisfied by a test in the
diverging file, because Rust puts unit tests there by default and the revert takes them with it.
A guard for a divergence has to live **outside the file it guards** — a different module, an
integration test under `tests/`, or a non-test mechanism entirely.

**The work is much smaller than nine files.** Two divergences (`shell.rs`, `lifecycle.rs`) are
already protected, better than a test would manage. Four (`pack.rs`, `lib.rs`, `runtime.rs`,
`summary.rs`) have no distinct behaviour a regression test could assert that the compiler would
not already catch on a consistent revert — though that claim deserves a second opinion, since
"the compiler will catch it" is exactly the assumption that fails when a merge is consistent.
**Two (`restore.rs`, `runtime_commands.rs`) are genuinely exposed**, and they are one line each.
A single test asserting that a managed agent dials the configured relay rather than
`key.relay_url` would close the real gap.

**Criterion 4 should also admit non-test guards.** The `windows-rust` clippy job protects two
divergences at compile time, which is stronger and cheaper than a test. A register that only
counts tests would under-report the fork's actual safety and push effort toward writing tests for
things the compiler already holds.

## Confidence and what was not checked

**High confidence, executed:** the `resolve.rs` revert (13 passed, 0 failed) and the `pack.rs`
revert (E0061). Both outputs pasted above; both files restored and the working tree verified clean
afterwards.

**Reasoned, not executed — treat as belief:**

- **`shell.rs` / `lifecycle.rs` being protected by the Windows job.** I did not run a Windows or
  cross-target build. The claim rests on what the `cfg(unix)` attributes guard plus `-D warnings`
  in the job definition. Cheap to confirm: `cargo clippy --target x86_64-pc-windows-msvc` with
  those attributes removed.
- **`lib.rs`, `restore.rs`, `runtime_commands.rs`, `runtime.rs`, `summary.rs`** were not reverted
  and tested. The `restore.rs` / `runtime_commands.rs` verdict is the one I would most want
  executed, because it is the one the recommendation rests on — although it is also the
  best-supported, since the types are identical and no test mentions the behaviour.
- **A *consistent* revert was never tested.** Every compile error here came from reverting one
  file while its counterpart stayed. Reverting `pack.rs` and `lib.rs` *together* — the realistic
  merge scenario — was not attempted, and it is the scenario that matters. I expect it compiles
  and passes; that expectation is the load-bearing untested claim in this document.

**Also not checked:** whether these nine are the right nine (that is #339's question — permanent
divergence versus work in flight, and a converging file should not get a regression test at all);
whether `desktop/src-tauri`'s own test suite has integration tests outside `src/` that touch these
paths; and anything about the non-product divergences (the other 33 of the 42 changed upstream
files).
