---
id: operations-runbooks-linux-rendering
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
  - statement: "docs/linux-rendering-troubleshooting.md is a troubleshooting guide covering the most common Linux rendering failures for both the AppImage distribution and native `deb`/`rpm` package installs, organized as a symptom-to-fix table followed by one detailed section per failure mode: a COLRv1 color-emoji font assertion abort (AppImage-only, fixed by upgrading to v0.5.2+), a blank-window dmabuf renderer incompatibility (NVIDIA GPUs or AppImage installs), a blank window on unrecognised hardware with no crash output, and an AMD RDNA4 transparent-window/graphical-corruption case."
    entry_class: FACT
    evidence:
      - "docs/linux-rendering-troubleshooting.md"
  - statement: "docs/linux-rendering-troubleshooting.md states that WebKitGTK's dmabuf zero-copy buffer path is incompatible with some GPU/driver/compositor combinations, that the WebKit child process silently fails to paint as a result, and that Buzz has shipped an automatic fix since the release containing pull request #3271 (v0.5.1) that sets `WEBKIT_DMABUF_RENDERER_FORCE_SHM=1` when it detects an NVIDIA GPU (PCI vendor ID `0x10de` under `/sys/class/drm`) or AppImage packaging, later updated by issue #3654 to stop recommending `WEBKIT_DISABLE_DMABUF_RENDERER=1` because that variable empties WebKit's transport mode and SIGSEGVs on current WebKitGTK (2.52+) the first time compositing is needed."
    entry_class: FACT
    evidence:
      - "docs/linux-rendering-troubleshooting.md"
  - statement: "docs/linux-rendering-troubleshooting.md documents a `--safe-rendering` CLI flag that forces both `WEBKIT_DMABUF_RENDERER_FORCE_SHM=1` and `WEBKIT_DISABLE_COMPOSITING_MODE=1` for one launch, states it is not remembered between runs, and states that Buzz refuses to start and prints exactly which variable conflicts if a WebKit environment variable is already set in the environment at the same time `--safe-rendering` is passed."
    entry_class: FACT
    evidence:
      - "docs/linux-rendering-troubleshooting.md"
  - statement: "docs/linux-rendering-troubleshooting.md's AMD RDNA4 section recommends setting `GDK_BACKEND=x11`, `WEBKIT_DMABUF_RENDERER_FORCE_SHM=1` and `WEBKIT_SKIA_ENABLE_CPU_RENDERING=1` together for RX 9000-series GPUs on the `radv` driver, and states this workaround has not been re-verified on RDNA4 hardware since the FORCE_SHM swap replaced the reporter's original `WEBKIT_DISABLE_DMABUF_RENDERER=1` recipe, asking readers who can to re-confirm it, with a dedicated RDNA4 detection fix tracked separately in issue #2643."
    entry_class: FACT
    evidence:
      - "docs/linux-rendering-troubleshooting.md"
  - statement: "desktop/src-tauri/src/webkit_rendering.rs's module documentation states that WebKit reads each of its rendering environment variables exactly once per process, so the choice of what to set must be made before anything initializes, with no runtime toggle and no second chance later in the same process — this is why the module decides from cheap preflight signals (an NVIDIA GPU, or AppImage packaging) instead of reacting to an observed crash."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/webkit_rendering.rs"
  - statement: "desktop/src-tauri/src/webkit_rendering.rs's `plan()` function implements this precedence: if the user has already set any of the three variables this module owns (`WEBKIT_DMABUF_RENDERER_FORCE_SHM`, `WEBKIT_DISABLE_DMABUF_RENDERER`, `WEBKIT_DISABLE_COMPOSITING_MODE`) in the environment, the heuristic stands down entirely and either leaves the environment alone (logging a warning if `WEBKIT_DISABLE_DMABUF_RENDERER` is set to anything other than `0`) or, if `--safe-rendering` was also passed, refuses to start with a diagnostic naming the conflicting variable; otherwise `--safe-rendering` applies `WEBKIT_DMABUF_RENDERER_FORCE_SHM=1` and `WEBKIT_DISABLE_COMPOSITING_MODE=1` for that launch, and failing that, an NVIDIA GPU (detected by reading `device/vendor` under every entry of `/sys/class/drm` for PCI vendor ID `0x10de`, case-insensitively) or the `APPIMAGE` environment variable being set applies `WEBKIT_DMABUF_RENDERER_FORCE_SHM=1` alone."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/webkit_rendering.rs"
  - statement: "desktop/src-tauri/src/main.rs calls `buzz_lib::webkit_rendering::apply()` only when compiled for `target_os = \"linux\"`, before calling `buzz_lib::run()`, and if `apply()` returns an `Err` it prints the diagnostic to stderr and exits the process with status 1 rather than starting the app in a state that silently ignored what the user asked for; the call site's own comment states this is the only point in the process where `std::env::set_var` is sound, because the process is still single-threaded and no GTK object yet exists."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/main.rs"
  - statement: "desktop/src-tauri/src/webkit_rendering/tests.rs unit-tests the detection heuristic directly against constructed argv, environment and DRM-tree fixtures (never the real process environment): an NVIDIA vendor ID applies `WEBKIT_DMABUF_RENDERER_FORCE_SHM`, a hybrid GPU with an NVIDIA device among others still counts, vendor-ID matching is case-insensitive, and an `APPIMAGE` environment variable applies the same fix even with no NVIDIA GPU present."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/webkit_rendering/tests.rs"
  - statement: "The desktop job in .github/workflows/ci.yml runs on `ubuntu-latest`, installs `libwebkit2gtk-4.1-dev` and related Tauri system libraries, and runs `just desktop-test`, `just desktop-build`, `just desktop-tauri-clippy`, `just desktop-tauri-check` and `just desktop-tauri-test` for every pull request that touches desktop or Rust paths (or every push) — so this fork's own CI builds and tests the Linux desktop app, including the `webkit_rendering` module's unit tests, on every relevant PR."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: ".github/workflows/linux-canary.yml (which produces an unsigned Linux `.deb` and `.AppImage`) and .github/workflows/release.yml (the signed release pipeline) both gate their build jobs with `if: github.repository == 'block/buzz'`, so neither workflow builds a distributable Linux desktop package when run in this fork, `launchpad-26/buzz`."
    entry_class: FACT
    evidence:
      - ".github/workflows/linux-canary.yml"
      - ".github/workflows/release.yml"
  - statement: "launchpad/README.md states this fork operates Buzz rather than developing it — \"The relay, desktop app and mobile app in this repo are upstream's product. Our work is deploying that product, running it for rhizomorph, documenting it, and automating the pipeline around it\" — and launchpad/AGENTS.md's repo-purpose comparison names \"Ansible, CI/CD, docs, relay config\" as this fork's typical change, contrasted with \"Rust crates, desktop React, mobile Flutter\" as upstream's."
    entry_class: FACT
    evidence:
      - "launchpad/README.md"
      - "launchpad/AGENTS.md"
  - statement: "AGENTS.md (repository root) states that genuine product bugs in Buzz still belong at block/buzz/issues, and separately that launchpad/README.md and launchpad/AGENTS.md govern deployment, infrastructure, documentation, upstream tracking and issue/PR filing for this fork."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "CONTRIBUTING.md's \"Linux: Tauri system libraries\" section states that Hermit pins language toolchains but not system libraries, that on Linux the desktop app's Rust crates link against GTK and WebKitGTK, and lists the exact `apt-get install` package set (build-essential, curl, file, libasound2-dev, libayatana-appindicator3-dev, libgtk-3-dev, librsvg2-dev, libssl-dev, libwebkit2gtk-4.1-dev, libxdo-dev, patchelf, wget) needed before `just ci` or any `just desktop-tauri-*` recipe will build, stating this is the same list CI installs."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "AGENTS.md (repository root) documents `just dev` as the command that starts \"the full Tauri app with native shell\" for local development, distinct from `just desktop-dev`, which runs the web-only frontend dev server; running `just dev` on a Linux host is what would exercise the WebKitGTK rendering path this node documents."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "Because this fork's own CI builds and unit-tests the Linux desktop app's WebKit rendering module on every relevant pull request, but no workflow in this fork produces or ships a distributable Linux desktop package, the person most likely to hit this failure inside this fork's own operations is a developer or agent running `just dev`/`just desktop-tauri-*` on a Linux host during development, or an operator supporting an end user of upstream's own officially released Buzz Desktop Linux build — not a user of a package this fork built and distributed itself."
    entry_class: INFERENCE
    evidence:
      - ".github/workflows/ci.yml"
      - ".github/workflows/linux-canary.yml"
      - ".github/workflows/release.yml"
      - "launchpad/README.md"
    confidence: 0.75
  - statement: "This node was written using launchpad/docs/corpus/templates/runbook.md, which was already merged on origin/launchpad at the recorded revision and directs a runbook node to state a trigger, severity and impact, diagnosis, mitigation and resolution, and escalation, each traceable to the Google SRE Workbook's playbook definition, plus a scope-and-omissions section."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/runbook.md"
relationships:
  - type: implements
    target: corpus-template-runbook
  - type: references
    target: layers-lifecycle-startup
  - type: references
    target: development-prerequisites
---

# Runbook: Buzz Desktop fails to render on Linux (WebKitGTK)

What to do when Buzz Desktop launches on a Linux host but the window is
blank, transparent, or the process crashes during startup rather than
showing the app.

## Scope and authority

**This node covers** the Linux-specific WebKitGTK rendering failures this
repository already documents and has already shipped code against: a blank
or transparent window with no crash output, a dmabuf-related `SIGSEGV`, and
the AppImage-specific `colrv1_configure_skpaint` assertion abort. It follows
`launchpad/docs/corpus/templates/runbook.md`'s required sections and
declares `implements` against it.

**One trigger, several root causes, deliberately.** The template scopes a
runbook to "one alert or failure condition," and the trigger here is one
condition — Buzz Desktop fails to render on a Linux host — with several
documented root causes (dmabuf incompatibility, an AppImage-only font ABI
mismatch, an AMD RDNA4-specific case) rather than one. This mirrors
`docs/linux-rendering-troubleshooting.md` itself, which treats all of them
as one guide keyed to one user-visible symptom family, and a reader who
hits a blank Linux window has no way to know which root cause applies until
they diagnose it — splitting this into separate per-cause runbooks would
force that same reader to guess which node to open first. If a root cause
here grows enough independent detail to outweigh sharing one trigger, that
is a reason to split it later, not a reason this node is wrong now.

**This fork does not build or distribute a Linux desktop package.** Buzz
Desktop is upstream's product; this fork's own CI (`.github/workflows/ci.yml`)
builds and unit-tests the desktop app's Rust crates on `ubuntu-latest` for
every relevant pull request, but the workflows that produce a distributable
`.AppImage`/`.deb` or a signed release are gated to run only when
`github.repository == 'block/buzz'` and never execute in
`launchpad-26/buzz`. So the failure this node documents is one this fork's
own CI can reproduce and has test coverage for, but it is not a service this
fork operates end-to-end for external users the way the relay is. See
*Scope and omissions* for what that means for who this runbook is actually
for.

## Trigger

A reader arrives here because Buzz Desktop, launched on a Linux host, does
one of the following instead of showing the normal UI:

- **Blank or transparent window, no crash output at all.** The process is
  running (visible in `ps aux`), but nothing renders.
- **Blank or transparent window followed by a crash.** Either a `SIGSEGV`
  (often when switching workspaces) or, on the AppImage distribution only, a
  `SIGABRT` with `colrv1_configure_skpaint` and an `Assertion '__n <
  this->size()' failed` message in the terminal output.
- **Graphical corruption or a transparent window on AMD RDNA4 hardware**
  (RX 9000 series) specifically.

There is no automated alert for this condition — it surfaces as a user or
developer report, or as a CI/local-dev failure while running `just dev` on a
Linux host. `docs/linux-rendering-troubleshooting.md`'s own symptom table is
the authoritative quick-reference for matching a specific symptom to a
specific cause; this node narrates the same material in the runbook
template's shape and adds this fork's own operating-scope context around
it.

## Severity and impact

**User-facing impact is total for the affected session:** the app does not
render at all, so the user cannot do anything with it until the workaround
is applied or a fixed build is installed. It is not data-destructive — no
report of data loss accompanies any of the four documented cases — and it
is host-specific: the same build renders correctly on most Linux hosts and
on macOS/Windows, so it does not indicate a defect in the app's own logic
reachable from every platform.

**Scope inside this fork.** Because this fork does not ship its own Linux
desktop build (see *Scope and authority*), the failure has two different
possible audiences with two different responses:

1. A developer or agent inside this fork hits it running `just dev` or a
   `just desktop-tauri-*` recipe on a Linux workstation — this is a local
   development blocker, not a user-facing incident.
2. Someone reports it against upstream's officially released Buzz Desktop —
   this is a product bug in Buzz itself, and per `AGENTS.md`, genuine
   product bugs belong at block/buzz/issues, not in this fork's own tracker.

## Prerequisites

Before diagnosing, confirm:

- **The host is genuinely Linux**, not WSL rendering to a Windows X server
  or similar — the fixes below assume a native Linux GPU/driver/compositor
  stack.
- **The build being run is recent.** The AppImage COLRv1 crash (see
  *Diagnosis*) is fixed outright in v0.5.2+; confirm the version before
  applying any workaround for it.
- **Terminal access to the process's stdout/stderr.** Every fix below is
  verified by reading the `buzz-desktop: ...` line the rendering module
  prints at startup (see `desktop/src-tauri/src/webkit_rendering.rs`'s
  `apply()`), so launching from a terminal rather than a desktop-icon
  double-click is necessary to diagnose or verify anything here.
- **To build or run locally in this fork**, the Linux Tauri system
  libraries CONTRIBUTING.md's "Linux: Tauri system libraries" section lists
  (`libgtk-3-dev`, `libwebkit2gtk-4.1-dev`, and the rest of that package
  set) must already be installed — a missing library produces a
  `pkg-config` build failure distinct from anything in this node, not a
  rendering failure at runtime.

## Diagnosis

Work through these in order; each one distinguishes the condition from the
others documented here.

1. **Is there a crash, or just a blank window?** Run the app from a
   terminal and capture output (`./Buzz_*.AppImage 2>&1 | tee
   buzz-crash.log`, or the equivalent native binary). No crash output at
   all points to the dmabuf blank-window case (step 3, below); a `SIGABRT`
   mentioning `colrv1_configure_skpaint` points to the AppImage COLRv1 case
   (step 2); a `SIGSEGV`, especially right after switching workspaces,
   points to the dmabuf case having actually crashed rather than just gone
   blank.
2. **Is this the AppImage distribution, and does the crash mention
   `colrv1_configure_skpaint`?** This is AppImage-only: native `.deb`/`.rpm`
   packages use the system WebKit, whose FreeType ABI does not have the
   struct-layout mismatch that causes it. Check the AppImage version — this
   is fixed outright at v0.5.2+.
3. **Is the GPU NVIDIA, or is this an AppImage on any GPU?** Read the
   `buzz-desktop: ...` line the process prints at startup — the rendering
   module logs its own decision (`WEBKIT_DMABUF_RENDERER_FORCE_SHM=1 —
   NVIDIA GPU` or `..., AppImage`, or `WebKit rendering left as-is — no
   NVIDIA GPU and not an AppImage`). If it already applied the fix and the
   window is still blank, the automatic heuristic did not cover this
   machine's actual driver/compositor combination.
4. **Is the GPU an AMD RDNA4 card (RX 9000 series) on the `radv` driver?**
   That combination has its own documented failure (transparent
   window/graphical corruption) with a separate three-variable workaround —
   the general dmabuf fix alone is not verified sufficient there.
5. **Check whether a WebKit variable is already set in the environment.**
   `env | grep WEBKIT_` — if any of `WEBKIT_DMABUF_RENDERER_FORCE_SHM`,
   `WEBKIT_DISABLE_DMABUF_RENDERER` or `WEBKIT_DISABLE_COMPOSITING_MODE` is
   already set, the automatic heuristic stands down entirely and whatever
   is set is the only thing in effect — this explains an automatic fix
   *not* applying even on hardware the heuristic would otherwise catch.

## Mitigation and resolution

Try these in order; each is more invasive than the last.

1. **AppImage COLRv1 crash: upgrade.** This is the one case with a real
   fix rather than a workaround — upgrade to the AppImage v0.5.2+, built
   against `ubuntu:24.04` with a matching FreeType ABI. If upgrading is not
   immediately possible, the fontconfig override in
   `docs/linux-rendering-troubleshooting.md` (rejecting color-format fonts)
   is the documented interim workaround; on Ubuntu 22.04 LTS or Debian 12,
   the native `.deb`/`.rpm` package is unaffected and is the more direct
   fix than the fontconfig override.
2. **Blank window, dmabuf case: let the automatic heuristic run, or force
   it.** If step 5 of *Diagnosis* found no WebKit variable already set,
   the automatic NVIDIA/AppImage detection should already have applied
   `WEBKIT_DMABUF_RENDERER_FORCE_SHM=1` — confirm via the startup log line.
   If the window is still blank on hardware the heuristic does not
   recognise, pass `--safe-rendering` for one launch (`./Buzz_*.AppImage
   --safe-rendering` or `buzz-desktop --safe-rendering`), which forces both
   `WEBKIT_DMABUF_RENDERER_FORCE_SHM=1` and
   `WEBKIT_DISABLE_COMPOSITING_MODE=1`. If that resolves it, make it
   permanent by exporting `WEBKIT_DMABUF_RENDERER_FORCE_SHM=1` in your
   shell profile rather than passing the flag every launch.
3. **Do not set `WEBKIT_DISABLE_DMABUF_RENDERER=1`.** On current
   WebKitGTK (2.52+) this empties the transport mode entirely and SIGSEGVs
   the first time compositing is needed, rather than falling back to shared
   memory the way it once did. If this variable is already set to anything
   other than `0` in the environment, unset it before trying step 2 above —
   the automatic heuristic will not override a user-set value, per
   *Diagnosis* step 5.
4. **AMD RDNA4 transparent window: the three-variable workaround.** Export
   `GDK_BACKEND=x11`, `WEBKIT_DMABUF_RENDERER_FORCE_SHM=1` and
   `WEBKIT_SKIA_ENABLE_CPU_RENDERING=1` together before launching. This
   recipe is documented as not re-verified since the FORCE_SHM swap
   replaced the originally reported `WEBKIT_DISABLE_DMABUF_RENDERER=1`
   variant, so treat it as the best currently-documented option rather than
   a confirmed fix for every RDNA4 host.
5. **If a variable conflict is reported.** If `--safe-rendering` is passed
   while a WebKit variable is already set, the process refuses to start and
   prints exactly which variable conflicts and what to do — either unset
   the named variable and retry, or drop the flag and keep the existing
   environment. That message, not guesswork, names the exact variable to
   change.

## Verification of recovery

- **Read the startup log line.** A successful automatic or forced fix
  prints `buzz-desktop: <VAR>=1 [, <VAR2>=1] — <reason>` to stderr before
  the window appears; confirm the variable you expected is the one listed.
- **Confirm the window actually renders**, including after a workspace
  switch (the dmabuf SIGSEGV in particular tends to appear on switching
  workspaces rather than at first paint) — a fix that only prevents the
  initial blank window but not a later crash under the same root cause is
  not fully verified yet.
- **For the AppImage COLRv1 case**, confirm the running build's version is
  v0.5.2 or later (rather than confirming a workaround took effect) — the
  fix here is a shipped build, not an environment variable.

## Escalation

- **If none of the documented cases match**, capture terminal output
  (`... 2>&1 | tee buzz-crash.log`) and check for a core dump
  (`coredumpctl list`, then `coredumpctl info <PID>`) before escalating —
  `docs/linux-rendering-troubleshooting.md`'s own "Diagnosing an
  unrecognised crash" section asks for exactly this plus distro, GPU and
  driver version.
- **A genuine defect in Buzz's own rendering code or its WebKitGTK
  workaround module belongs at block/buzz/issues**, per this repository's
  root `AGENTS.md` — this fork does not own or fix that code, and filing it
  here would send it to the wrong tracker.
- **A failure specific to this fork's own CI** (for example, the `desktop`
  job in `.github/workflows/ci.yml` failing on a rendering-adjacent test on
  a runner) is this fork's own concern and is filed against this
  repository in the ordinary way `launchpad/README.md` describes, not
  against upstream.
- **There is no rollback step distinct from the mitigations above.** None
  of the documented fixes changes persistent state outside the current
  shell's environment variables or the installed package version, so
  "rolling back" is unsetting the exported variables or reverting to the
  previously installed build.

## Evidence to preserve

- The full terminal output of the failing launch (`tee buzz-crash.log`,
  above), including the `buzz-desktop: ...` startup log line if one was
  printed.
- `coredumpctl info <PID>` output if a core dump exists.
- The distribution and exact version installed (AppImage version, or
  `deb`/`rpm` package version), the GPU vendor and model, and the driver in
  use (proprietary NVIDIA vs. nouveau; `radv` vs. `amdgpu` for AMD).
- Whether any `WEBKIT_*` or `GDK_BACKEND` variable was already set in the
  environment before any workaround was tried (per *Diagnosis* step 5) —
  this distinguishes "the automatic heuristic didn't fire" from "a manual
  override is masking it."

No credential, token or secret is ever involved in diagnosing or fixing
this condition; nothing in this runbook requires linking a dashboard or
copying a credential.

## Scope and omissions

**This node does not cover, and who owns what it does not cover:**

| Not covered here | Owned by |
|---|---|
| Non-Linux rendering issues (macOS, Windows) | Not documented in this repository as a comparable class of problem at the recorded revision; no corpus node exists for it |
| Fixing a genuine defect in `desktop/src-tauri/src/webkit_rendering.rs` itself, or in WebKitGTK | Upstream, at block/buzz/issues, per this repository's root `AGENTS.md` |
| Building and shipping a Linux desktop package from this fork | Not done by this fork at all — see *Scope and authority* |
| The desktop app's general architecture and startup sequence beyond the Linux rendering workaround | `layers-lifecycle-startup` (references relationship, above) |
| The full Linux build-time system-library prerequisite list | `development-prerequisites` (references relationship, above) |
| Alerting or dashboard configuration for this condition | None exists in this repository — there is no automated alert for a desktop rendering failure; see *Trigger* |

**Expected but not verified when this node was written:**

- **No live reproduction was attempted.** Every claim above about symptoms,
  root causes and fixes rests on reading
  `docs/linux-rendering-troubleshooting.md` and
  `desktop/src-tauri/src/webkit_rendering.rs` (plus its tests), not on
  triggering any of the four failure modes on real Linux hardware during
  this task. The unit tests in `webkit_rendering/tests.rs` exercise the
  decision logic against constructed fixtures, not a real GPU or a real
  WebKitGTK process.
- **Whether this fork's `desktop` CI job has ever actually hit one of
  these rendering failures on its `ubuntu-latest` runner was not
  checked.** GitHub-hosted `ubuntu-latest` runners typically have no GPU at
  all, so it is plausible the automatic heuristic's `Leave` branch (no
  NVIDIA GPU, not an AppImage) is the only path CI ever exercises for the
  detection logic itself, while the unit tests cover the other branches
  synthetically — this was not confirmed against a CI run's actual log
  output.
- **Whether upstream's `docs/linux-rendering-troubleshooting.md` has moved
  since the recorded revision** (new GPUs, new WebKitGTK versions, a
  resolution to the still-open AMD RDNA4 re-verification ask) was not
  checked against anything newer than this node's recorded commit.
- **Whether any rhizomorph user actually runs Buzz Desktop on Linux at
  all** was not established — `launchpad/README.md` describes this fork as
  operating Buzz "for rhizomorph" without specifying which client platforms
  rhizomorph's users use, so the severity claims in *Severity and impact*
  are general statements about the failure's nature, not a claim about how
  many people this fork's own operations would actually affect.
