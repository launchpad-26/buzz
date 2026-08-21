# Where a packaged desktop build's stdout and stderr go

**Title:** Destination and survivability of the packaged desktop app's stdout/stderr
**Summary:** On macOS a bundle launched by LaunchServices inherits `/dev/null` on both stdout and stderr, and the output reaches no system log — so all 402 `println!`/`eprintln!` sites in `desktop/src-tauri` write into nothing and no past launch is recoverable. Measured with a probe bundle on macOS 15.7.7. One genuinely retrievable log directory does exist and holds managed-agent subprocess output only, persisting with no expiry. Linux and Windows untested.
**Tags:** `observability` `desktop` `tauri` `macos` `logging` `retention`
**Reviewed:** 2026-08-22 · **Source:** `launchpad-26/buzz` at `678008ea4` · **Answers:** [#315](https://github.com/launchpad-26/buzz/issues/315)

---

## Finding

**On macOS: discarded outright.** A bundle launched the normal way — Finder, Dock, LaunchServices — inherits `/dev/null` on file descriptors 1 and 2, and the output does not reach the unified log either. The **402** `println!`/`eprintln!` call sites in `desktop/src-tauri/src` therefore write into `/dev/null` in a packaged build, and **no past launch's output is recoverable by any means.**

Two things qualify that, both material:

- **There is one real log directory, and nobody has been pointing at it.** `~/Library/Application Support/xyz.block.buzz.app/agents/logs/` holds **managed-agent subprocess** output — not the app's own. It persists across quits with no expiry that could be found: nine plain-text files, 96K, still present two days after they were written.
- **Live capture is one command away.** Relaunching from a terminal makes the app inherit the terminal's descriptors instead of `/dev/null`. That helps only for a fault someone can reproduce on demand, which is the opposite of the faults [#289](https://github.com/launchpad-26/buzz/issues/289) exists for.

**Linux and Windows were not tested** — see the last section, which states what is expectation rather than finding.

---

## Part 1 — What LaunchServices hands a bundle

No `Buzz.app` exists on the machine used, so the real product could not be launched. Instead the property that decides the answer was measured directly: what LaunchServices gives a `.app` bundle. The probe preserves its launch-time descriptors as fd 3 and 4 *before* touching them, so the measurement is not contaminated by its own redirection — a first attempt was, and was redone.

The probe bundle's executable:

```bash
#!/bin/bash
# Preserve the fds we were LAUNCHED with before touching them.
exec 3>&1 4>&2
OUT=".../scratchpad/probe-result2.txt"
echo "BUZZPROBE-STDOUT-MARKER-9f3a" >&3
echo "BUZZPROBE-STDERR-MARKER-9f3a" >&4
{
  echo "pid=$$  launched-by-LaunchServices"
  echo "--- lsof on the INHERITED fds (3=orig stdout, 4=orig stderr) ---"
  /usr/sbin/lsof -p $$ -a -d 0,3,4 2>&1
  echo "--- ppid chain ---"
  ps -o pid,ppid,comm -p $$ 2>&1
} > "$OUT" 2>&1
sleep 1
```

Launched with `open -a`. Result:

```
pid=6764  launched-by-LaunchServices
--- lsof on the INHERITED fds (3=orig stdout, 4=orig stderr) ---
COMMAND  PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
bash    6764 jeff    0r   CHR    3,2      0t0  316 /dev/null
bash    6764 jeff    3u   CHR    3,2     0t29  316 /dev/null
bash    6764 jeff    4u   CHR    3,2     0t29  316 /dev/null
--- ppid chain ---
  PID  PPID COMM
 6764     1 /bin/bash
```

`CHR 3,2` is `/dev/null`. Both inherited descriptors point at it. The offset `0t29` is the 29 bytes of the marker line — the write succeeded, into `/dev/null` specifically. Parent pid 1 (`launchd`) confirms the LaunchServices path rather than a shell.

Environment: `macOS 15.7.7 (24G720)`, from `sw_vers`.

## Part 2 — It is not in the unified log either

```
$ /usr/bin/log show --style compact --last 10m \
    --predicate 'eventMessage CONTAINS "BUZZPROBE" AND process != "log"'
Timestamp               Ty Process[PID:TID]

$ ... | grep -c BUZZPROBE
0
```

Two traps worth recording for whoever repeats this:

- `log` is a **zsh builtin**. It must be invoked as `/usr/bin/log`, or the shell reports `too many arguments`.
- `log show` records its own invocation, and the predicate string contains the marker. Without `process != "log"` the query matches itself twice and looks like a positive result.

## Part 3 — Nothing in the app redirects its own output

```
$ grep -n "plugin-log\|plugin_log" desktop/src-tauri/Cargo.toml desktop/src-tauri/src/lib.rs
(no output)

$ grep -rn "tracing_subscriber" desktop/src-tauri | wc -l
       0

$ grep -rn "eprintln!\|println!" desktop/src-tauri/src --include='*.rs' | wc -l
     402
```

No `tauri-plugin-log`, no `tracing` subscriber, 402 print sites. The 11 `tracing::` call sites in `desktop/src-tauri/src` are dropped for want of a subscriber; the 402 prints are dropped for want of a destination. Two different causes, one outcome.

There is also no console bridge from the webview:

```
$ grep -rn "invoke(\"log\|console.log = \|overrideConsole\|attachConsole" desktop/src --include='*.ts' --include='*.tsx'
(no output)
```

So the frontend's 193 `console.*` calls stay in the webview's own console — reachable only with an inspector attached, never on stdout, never on disk. **A Rust-side log file would not capture them.**

## Part 4 — The one thing that is retrievable, and its exact limit

`desktop/src-tauri/src/managed_agents/storage.rs` writes real files:

```rust
// storage.rs:35
pub fn managed_agents_base_dir(app: &AppHandle) -> Result<PathBuf, String> {
    let dir = app.path().app_data_dir()?.join("agents");
    ...
}
// storage.rs:49
fn managed_agents_logs_dir(app: &AppHandle) -> Result<PathBuf, String> {
    let dir = managed_agents_base_dir(app)?.join("logs");
    ...
}
// storage.rs:84
pub fn managed_agent_log_path(app: &AppHandle, pubkey: &str) -> Result<PathBuf, String> {
    Ok(managed_agents_logs_dir(app)?.join(format!("{pubkey}.log")))
}
```

With `"identifier": "xyz.block.buzz.app"` from `desktop/src-tauri/tauri.conf.json`, that resolves on macOS to `~/Library/Application Support/xyz.block.buzz.app/agents/logs/`. It exists with content on the machine used:

```
$ ls -1 "$D" | wc -l
       9
$ du -sh "$D"
 96K	/Users/jeff/Library/Application Support/xyz.block.buzz.app/agents/logs
$ ls -lt "$D" | head -3 | awk '{print $5, $6, $7, $8}'
19259 20 Aug 07:15
19260 20 Aug 07:15
$ ls ~/Library/Application\ Support/xyz.block.buzz.app/
agents
identity.migrated
templates
```

Nine plain-text files written on 20 August, still present on 22 August. **They survive the app quitting, with no retention policy found.** Their contents are deliberately not quoted here: this repository is public and agent logs are exactly where #289 expects secrets to be. The first line's shape alone is `=== starting Honey (7dca5db32f84ce915ab…`, i.e. plain-text narrative of an agent run.

**The limit.** These capture *piped child process* output, not the app's own — `managed_agents/backend.rs:91-93`:

```rust
    let mut child = cmd
        .stdin(std::process::Stdio::piped())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
```

The app captures the agent's stdout because it explicitly pipes it. Its own 402 print sites still go to the `/dev/null` it inherited.

## Part 5 — What a member could be told to do

**After the fact: nothing.** No instruction recovers a past launch's output on macOS, because it was never written anywhere.

**Live, to catch it next time** — quit the app and relaunch it from a terminal so it inherits the terminal's descriptors:

```
/Applications/Buzz.app/Contents/MacOS/Buzz
```

(`productName` is `Buzz`, version `0.5.15`, from `tauri.conf.json`.) A member could follow that unaided. It only helps for a reproducible fault, which is what [#313](https://github.com/launchpad-26/buzz/issues/313) is about and what the witnessed faults are not.

**For agent faults specifically**, this works today, unaided, after the fact:

```
open ~/Library/Application\ Support/xyz.block.buzz.app/agents/logs/
```

---

## What this means for #289

1. **Criterion 2 cannot be met by pointing at an existing local record.** On macOS there is no such record for the app's own output. The "guess retrievable and under-scope the work" branch is closed off — desktop work is needed.
2. **The cheapest first step is not a telemetry pipeline.** A `tracing` subscriber with a file writer, or `tauri-plugin-log`, would make all 402 existing print sites *and* the 11 dropped `tracing::` calls land somewhere retrievable on all three platforms — no collector, no network, no consent question. Smaller than instrumenting for export, independently useful, and a prerequisite for shipping anything.
3. **A location precedent already exists in-tree.** The managed-agent log directory shows where per-machine files are expected to live and that they persist. Desktop telemetry should probably sit beside it rather than invent a location.
4. **There is an unowned retention question, already live.** Nine plain-text agent log files persisted with no expiry, on a personal machine, before this PRD adds anything. That is criterion 6's problem arriving early and it is nobody's issue yet.
5. **The webview console is a separate gap from stdout**, needing a different mechanism. [#316](https://github.com/launchpad-26/buzz/issues/316) covers the frontend side.

---

## Confidence, and what was not checked

**High confidence for macOS**, from the run above — with one caveat stated because it matters: **the probe was a synthetic bundle, not `Buzz.app`.** No packaged Buzz build existed on the machine. What was measured is a property of how LaunchServices launches any bundle, which is why it should transfer — but a run against a real signed `Buzz.app` would remove the inference, and that is the cheapest thing that would strengthen this document.

**Platforms named as untested:**

- **Linux — not tested.** No Linux machine was available. *Expectation, not finding:* a `.desktop`-launched app's output lands in the systemd user journal (`journalctl --user`) on most current desktops, and nowhere at all under an older non-systemd session. The same probe settles it in minutes.
- **Windows — not tested.** *Expectation, not finding:* a GUI-subsystem binary has no attached console, so stdout writes go nowhere.

**Also not checked:** whether the real `Buzz.app` differs because of its bundle contents or entitlements; whether `just dev` / `pnpm tauri dev` behaves differently (it inherits the terminal, but this was not measured); whether any of the 402 print sites sit on paths a member actually hits during the witnessed faults; the retention behaviour of the agent log directory beyond observing two-day-old files; mobile, which is out of scope.
