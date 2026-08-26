# Does the pending 67-commit drop build, and how many semantic conflicts does it hold

**Title:** The current drop, performed for real: four textual conflicts, one semantic break, and a refuted hazard
**Summary:** Performed the merge in a throwaway worktree. Four textual conflicts, exactly as `merge-tree` predicted, all resolvable. Found **one semantic conflict `merge-tree` cannot see**: upstream deleted a binding the fork's own fix still uses, 28 lines apart, so git merged both cleanly and the desktop crate failed to compile. Crucially, **the obvious "upstream wins" resolution compiles and silently reintroduces the bug the fork fixed.** `cargo check --workspace --locked` and the desktop crate both pass after resolution. Separately **refutes ADR-0022's headline counter-example**: the `bin/.lefthookrc` hazard does not materialise — the merged tree resolves lefthook to 2.1.10, not 2.1.3.
**Tags:** `upstream-sync` `vendor-drop` `conflict-resolution` `adr-0022` `prd-273` `semantic-conflict`
**Established:** 2026-08-22 · **Answers:** [#360](https://github.com/launchpad-26/buzz/issues/360) · **Parent:** [#273](https://github.com/launchpad-26/buzz/issues/273)

---

## Finding

The drop is **tractable, and its most dangerous case is invisible to every mechanism #273 proposes.**

| | Result |
|---|---|
| Textual conflicts | **4** — `.github/workflows/ci.yml`, `Cargo.lock`, `managed_agents/runtime.rs`, `lefthook.yml` |
| All four resolvable | Yes, in about an hour, and three of the four mechanically |
| **Semantic conflicts** | **1** — a compile error in an *auto-merged* hunk |
| `cargo check --workspace --locked` | **Passes**, 0 errors |
| `cargo check` desktop crate | **Passes** after resolution |
| Merge size | 912 files, +96,604 / −20,479 |
| `bin/.lefthookrc` hazard | **Does not materialise** — refuted empirically |

The semantic conflict is the whole story, and it is worth stating precisely because it is the best evidence #273 has for its own design.

Upstream rewrote `start_managed_agent_process`, **deleting** the `let relay_url = {…}` binding and replacing it with `bound_runtime_key(record, workspace_relay)`. The fork's divergence (`975e6d444`, "dial the configured relay") **uses** `relay_url` 28 lines further down. Git merged both hunks without complaint, producing:

```
error[E0425]: cannot find value `relay_url` in this scope
   --> src/managed_agents/runtime.rs:717:55
```

**Now the part that matters.** The tempting resolution is upstream's line, `&key.relay_url`. It compiles. And it is wrong, because `ManagedAgentRuntimeKey::new` normalises:

```
desktop/src-tauri/src/managed_agents/runtime_types.rs:22
    relay_url: buzz_core_pkg::relay::normalize_relay_url(relay_url)
```

`key.relay_url` is the loopback-normalised identity — which is exactly the bug `975e6d444` fixed. **Upstream has not fixed it; upstream restructured the code around it.** So "take upstream, it compiles" reintroduces a fixed bug, silently, with a green build.

The correct resolution re-expresses the fork's fix in upstream's new API:

```rust
// Dial the configured relay, not `key.relay_url` (the loopback-normalized
// identity that `ManagedAgentRuntimeKey::new` produces). See the note in
// `spawn_agent_child`. Recomputed from the caller's bound workspace relay,
// which is the same input `bound_runtime_key` keys on.
let relay_url =
    crate::relay::effective_agent_relay_url(&record.relay_url, workspace_relay.as_str());
let mut process = spawn_agent_child(app, record, &relay_url, false, owner_hex)?;
```

---

## Evidence

### The merge, and its four conflicts

```
$ git worktree add -f --detach <throwaway> launchpad/launchpad
$ git -c rerere.enabled=false merge --no-ff --no-commit upstream/main
Auto-merging .github/workflows/ci.yml
CONFLICT (content): Merge conflict in .github/workflows/ci.yml
Auto-merging AGENTS.md
Auto-merging Cargo.lock
CONFLICT (content): Merge conflict in Cargo.lock
Auto-merging Justfile
Auto-merging crates/buzz-cli/src/lib.rs
Auto-merging desktop/src-tauri/src/managed_agents/restore.rs
Auto-merging desktop/src-tauri/src/managed_agents/runtime.rs
CONFLICT (content): Merge conflict in desktop/src-tauri/src/managed_agents/runtime.rs
Auto-merging lefthook.yml
CONFLICT (content): Merge conflict in lefthook.yml
Automatic merge failed; fix conflicts and then commit the result.
```

Exactly the four `merge-tree` predicted. `AGENTS.md`, `Justfile`, `buzz-cli/src/lib.rs` and `restore.rs` auto-merged.

### Resolution 1 — `lefthook.yml`: theirs, then re-apply ours

The conflict confirms the first sweep's §0.3 analysis. Our side is one `run:` line plus its comment; upstream's side adds two whole new lanes:

```
<<<<<<< HEAD
      # launchpad-26/buzz#15: the upstream script assumes origin/main is the PR
      # base, which is wrong for this fork …
      run: ./launchpad/scripts/check-branch-skew.sh
=======
      run: ./scripts/check-branch-skew.sh
    push-head-scope:
      …
      run: ./scripts/check-push-head-scope.sh
    file-size-check:
      …
      run: just file-size-check
>>>>>>> upstream/main
```

Resolution: keep our `run:` line and its comment, **and** take both of upstream's new lanes. `merge=ours` would have discarded `push-head-scope` and `file-size-check` entirely — which is precisely the harm §0.3 predicted, now demonstrated on the real conflict.

### Resolution 2 — `ci.yml`: upstream supersedes one of ours, not both

```
<<<<<<< HEAD
      - name: File size ratchet unit tests
        run: node --test scripts/check-file-sizes-core.test.mjs
      - name: Changed-paths filter contract
        run: scripts/test-ci-changed-paths-filter.sh
=======
      - name: File size policy
        run: just file-size-check
>>>>>>> upstream/main
```

Upstream's `just file-size-check` supersedes our ad-hoc ratchet test; our `Changed-paths filter contract` step has no upstream counterpart and must survive. Resolution: take upstream's step, keep ours. Both `scripts/test-ci-changed-paths-filter.sh` and the `file-size-check` recipe exist in the merged tree, so both steps are live.

### Resolution 3 — `Cargo.lock`: one hunk, take the higher

```
<<<<<<< HEAD
version = "0.4.18"
=======
version = "0.4.16"
>>>>>>> upstream/main
```

A single conflict region: h2. Ours is the RUSTSEC-2026-0258 bump, upstream independently went to 0.4.16. Kept 0.4.18. `cargo check --locked` then succeeded, so the lockfile is internally consistent — no regeneration needed.

### Resolution 4 — `runtime.rs`: code motion, ported by hand

The fork extracted three functions into `runtime/summary.rs` for the file-size ratchet; upstream edited them in place. The conflict spans lines 73–354. Resolution: keep the fork's `mod summary;` block, then port upstream's four edits into `summary.rs`:

```
  ported: teams parameter added
  ported: removed redundant load_global_agent_config
  ported: use passed global_config
  ported: removed per-record load_teams
  ported: owner_only_access_build() argument
```

No mechanism helps here. This is what escalation is for.

### The build

```
$ cargo check --workspace --locked
    Checking buzz-relay v0.2.1 …
    Checking buzz-admin v0.1.0 …
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 6m 48s
```

Zero errors across all 30 workspace crates. **But the desktop crate is excluded from the root workspace**, and that is where the conflict lived:

```
$ cargo check --manifest-path desktop/src-tauri/Cargo.toml --all-targets
error[E0425]: cannot find value `relay_url` in this scope
   --> src/managed_agents/runtime.rs:717:55
error: could not compile `buzz-desktop` (lib) due to 1 previous error
```

After the port:

```
$ CARGO_INCREMENTAL=0 cargo check --manifest-path desktop/src-tauri/Cargo.toml
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 1m 17s
```

One prerequisite worth recording: the desktop build first fails with `resource path 'binaries/buzz-acp-x86_64-apple-darwin' doesn't exist` until `just _ensure-sidecar-stubs` has run. Anyone verifying a drop locally will hit this and it looks like a merge failure.

### The `bin/.lefthookrc` hazard is refuted

ADR-0022 and #296 both carry this as the worked counter-example: upstream's new `bin/.lefthookrc` allegedly pins `LEFTHOOK_BIN` to lefthook **2.1.3**, the version ADR-0017 records as crashing every first push here, so a clean merge reintroduces #196.

**It does not.** `.lefthookrc` does not hardcode a version — it resolves a symlink:

```
$ cat bin/.lefthookrc
…
  if [ -x "$_lefthook_root/bin/lefthook" ]; then
    LEFTHOOK_BIN="$_lefthook_root/bin/lefthook"
    export LEFTHOOK_BIN
  fi
```

Only its *comment* mentions 2.1.3. The fork points that symlink at its own pin, and upstream did not touch it:

```
$ ls -l bin/lefthook
lrwxr-xr-x  bin/lefthook -> .lefthook-2.1.10.pkg

$ git diff --name-only f8692fa9b upstream/main -- bin/
bin/.lefthookrc
```

Tested by resolving it exactly as the hook dispatcher does, in the merged tree:

```
$ ( . ./bin/.lefthookrc; echo "LEFTHOOK_BIN=$LEFTHOOK_BIN"; "$LEFTHOOK_BIN" version )
LEFTHOOK_BIN=<worktree>/bin/lefthook
2.1.10
```

**2.1.10 runs. The hazard does not materialise.** The `.lefthookrc` mechanism is in fact *protective* — it makes the hook self-pinning to whatever the fork's symlink names, which is what ADR-0017 wants.

---

## What this means for #273

**The clean-merge-but-wrong class is real, and it is not the file ADR-0022 says it is.** That record's counter-example is wrong on the facts; the genuine instance is the `relay_url` deletion, and it is worse in a way that matters. `.lefthookrc` was alleged to break a contributor's push — loud, local, quickly diagnosed. The `relay_url` case is a **silently wrong resolution that compiles**: it does not break the build, it makes managed agents dial the loopback-normalised relay instead of the configured one. Nothing in CI would catch it. Only someone who knows why `975e6d444` exists would.

That should replace `.lefthookrc` in ADR-0022's bad-consequence section, and it strengthens rather than weakens the record's honesty: the hole it declares open is real, it just picked the wrong illustration.

**#296's boundary now has a calibrated hard case.** "How far may the agent resolve before escalating" has a concrete answer for at least this shape: **an agent must not resolve a conflict where the fork's side is a bug fix and upstream has restructured the surrounding code.** The resolution required reading `975e6d444`'s intent, finding `normalize_relay_url` two files away, and knowing that upstream's compiling alternative was wrong. Three of the four conflicts here are mechanical; the fourth is not, and the auto-merged fifth is the dangerous one.

**`merge-tree` is not a sufficient pre-flight, and every figure derived from it understates risk.** The "4 conflicts" number is correct and complete for *textual* conflicts and missed the only defect that would have shipped. Any drop report that reports conflict count without a build has reported the easy half.

**The `git diff --name-only` intersection would have caught it, though.** `runtime.rs` is in the 8-file both-sides-touched set. So the contested-surface computation is the right pre-flight signal; it is `merge-tree`'s *conflict* output that is insufficient. Worth distinguishing, because #306 could easily specify the weaker one.

**Practical note for whoever takes this drop:** the four resolutions above are correct and tested to `cargo check`. They can be reused. The `runtime.rs` port is the only one needing judgement.

---

## Confidence and limits

**High confidence** on the conflict set, the resolutions, the semantic break and its correct fix, and the lefthook refutation — all pasted command output from a real merge in a real worktree.

**Not verified — and this is a genuine gap in the answer.** **I did not run the test suites.** `cargo test` on the desktop crate failed to build `aws-lc-sys` because the machine ran out of disk (`No space left on device`, 659 MiB free on a 418 GiB volume, of which my own build artifacts were 3.8 GiB). So:

- `cargo check` proves it **compiles**. It does not prove it **behaves**.
- The `managed_agents` test suite — which PR #216 recorded as 123/123 passing, and which is the suite most likely to cover the `relay_url` path — was **not run**. Upstream added `runtime/spawn_key.rs` with regression tests specifically about spawn-key derivation, and those are exactly the tests that would judge my resolution. They remain unrun.
- `just test-unit`, `just ci`, the desktop E2E suites, mobile tests and the web build were all not run.

Anyone relying on this document should treat "the drop builds" as established and "the drop is correct" as open. Re-running `cargo test --manifest-path desktop/src-tauri/Cargo.toml --lib managed_agents` on a machine with ~10 GiB free would close most of it.

**Also not checked.** I did not review the other 904 auto-merged files for further instances of the same class — I found one by compiling, and a compiler only finds the ones that break the build. A second `relay_url`-shaped defect that happens to still typecheck would not have surfaced. I did not commit the merge or push anything; the worktree was removed after the run, so the resolutions survive only as the diffs quoted above. I did not test whether `git rerere` would have recorded these resolutions usefully — that is #367. I have no VPS access and it was not relevant.
