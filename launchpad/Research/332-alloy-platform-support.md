# Which platforms Grafana Alloy supports, and by what install method

**Title:** Grafana Alloy platform support matrix for the cohort's machines
**Summary:** Every *plausible* cohort platform is supported, including Intel macOS — Alloy v1.18.1 publishes `alloy-darwin-amd64`, the case #320 flagged as most likely to be missed. Each platform has a native package and a native keep-running mechanism: Homebrew to launchd on macOS, native packages to systemd on Linux, an installer to a Windows service. No container runtime is required anywhere. The worry behind the question does not bite. **The "plausible" qualifier is load-bearing: no cohort platform inventory exists** ([#320](https://github.com/launchpad-26/buzz/issues/320), [#417](https://github.com/launchpad-26/buzz/issues/417)), so this is coverage of an assumed macOS/Linux/Windows superset, not of a verified list.
**Tags:** `observability` `grafana-alloy` `platform-support` `macos` `install`
**Reviewed:** 2026-08-22 · **Answers:** [#332](https://github.com/launchpad-26/buzz/issues/332)

---

## Finding

**Every *plausible* cohort platform is supported, including the one most likely to be missed.**

<sub>Read the qualifier as doing real work, per [#417](https://github.com/launchpad-26/buzz/issues/417). **No cohort platform inventory exists anywhere in this repository**, so "every plausible platform" means the assumed macOS/Linux/Windows superset — not a list anyone has checked against. The Alloy half is verified from pinned release assets; the *cohort* half is an inference from [#320](https://github.com/launchpad-26/buzz/issues/320)'s single machine. Until that inventory exists the claim is not falsifiable, which is also why it should not be leaned on hard.</sub> Alloy v1.18.1 publishes an **`alloy-darwin-amd64`** binary — Intel Mac — which is exactly the exception [#320](https://github.com/launchpad-26/buzz/issues/320) flagged that a guessed inventory would drop.

Each platform has a native package and a native keep-running mechanism: **Homebrew → launchd**, **native packages → systemd**, **installer → Windows service**.

**The worry behind this question does not bite.** #320 recorded a live toolchain break on this cohort's Intel Mac — `pnpm 11.4.0: no source provided`. Alloy is not in that category: it ships the artifact.

---
## The support matrix, from the release assets

Not from a documentation page that might lag — from what the project actually publishes. `grafana/alloy` **v1.18.1**, released **2026-08-06**:

```
$ gh api repos/grafana/alloy/releases/latest --jq '.assets[].name' | grep -i darwin
alloy-darwin-amd64.zip
alloy-darwin-arm64.zip

$ gh api repos/grafana/alloy/releases/latest --jq '.assets[].name' | ... | sort -u
boringcrypto-linux-amd64
boringcrypto-linux-arm64
darwin-amd64
darwin-arm64
freebsd-amd64
installer-windows-amd64
linux-amd64
linux-arm64
linux-ppc64le
linux-s390x
windows-amd64
```

| Platform | Architectures | Supported install method | Kept running by |
|---|---|---|---|
| **macOS** | **amd64 (Intel)**, arm64 (Apple Silicon) | Homebrew | **launchd**, via `brew services` |
| **Linux** | amd64, arm64, ppc64le, s390x | Native OS packages; also Docker, Podman, Kubernetes, OpenShift, Ansible, Chef, Puppet | **systemd** |
| **Windows** | amd64 | Installer (`installer-windows-amd64`) | **Windows service** |
| FreeBSD | amd64 | Binary only — no curated install page | *(not stated)* |

### macOS, in detail — the platform the cohort is known to be on

```shell
brew tap grafana/grafana
brew install grafana/grafana/alloy
```

Homebrew is *the* supported method. Service management goes through Homebrew's launchd integration — `brew services restart grafana/grafana/alloy` — and the documentation states this *"ensures Alloy persists across reboots through macOS's native launchd system."*

One detail that matters for writing instructions the cohort can follow: the Homebrew prefix differs by architecture — `/usr/local` on Intel, `/opt/Homebrew` on Apple Silicon — so any path-bearing instruction must either use `brew --prefix` or be given twice.

**No container runtime is required on any of the three platforms.** Docker and Podman are options on Linux, not prerequisites anywhere.

---

## What this means for #289


> **Recommendations, not findings.** Everything in this section is my assessment as the author, not behaviour established by the evidence above. Per [ADR-0003]'s claim rule: a claim about how the system *behaves* carries a source reference; a claim about what the cohort *should do* is opinion, attributed. Nothing is both — so nothing below is cited as though it were established.
1. **The platform question is closed and it is not a blocker.** Every architecture the cohort could plausibly be running has a first-party binary and a native install path.
2. **Intel macOS is explicitly covered**, which retires the specific concern #320 raised — and does so by evidence rather than by assumption, since the cohort has already been bitten by a tool that dropped that architecture.
3. **The keep-running mechanism is native everywhere**, so "it stops when the laptop reboots" is not a failure mode anyone needs to design around.
4. **Instructions must be per-platform, not generic.** Three different service managers and two different Homebrew prefixes. A single "install Alloy" line in a runbook will not work for everyone.
5. **This does not answer what it costs.** Support is not footprint — that is [#333](https://github.com/launchpad-26/buzz/issues/333).

---

## Confidence and what is still unknown

**High confidence.** The architecture list comes from the release assets the project actually publishes, retrieved through the GitHub API, rather than from prose. The macOS commands and the launchd claim are quoted from Grafana's own install page.

**Not verified: I did not install Alloy on anything.** No `brew install` was run, no service was started, and no reboot was tested. "Persists across reboots" is Grafana's claim, not my observation.

**Also not checked:** whether the Homebrew tap carries the same version as the GitHub release, which can lag; whether the macOS build is signed or notarised, and therefore what Gatekeeper does on first run — a real question given [#319](https://github.com/launchpad-26/buzz/issues/319) found unsigned binaries are a live problem for this cohort, and one I did not investigate; whether `brew services` running as the logged-in user (rather than as a system daemon) limits what Alloy can read on a member's machine; the FreeBSD story beyond noting a binary exists with no curated page; and the minimum supported macOS and Windows versions, which I did not find.

## Sources

- [grafana/alloy releases (v1.18.1, 2026-08-06)](https://github.com/grafana/alloy/releases/latest) — the published platform/architecture assets
- [Install Grafana Alloy — Grafana documentation](https://grafana.com/docs/alloy/latest/set-up/install/) — the supported platform and method list
- [Install Grafana Alloy on macOS — Grafana documentation](https://grafana.com/docs/alloy/latest/set-up/install/macos/) — Homebrew commands, `brew services`, launchd, prefix difference
