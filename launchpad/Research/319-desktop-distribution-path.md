# Whether this fork can build and distribute its own desktop client

**Title:** Desktop client distribution capability in `launchpad-26/buzz`
**Summary:** Every workflow in this repository that builds a desktop bundle is hard-gated `if: github.repository == 'block/buzz'`, the fork holds zero Actions secrets, and the macOS signature comes from Block's OIDC-federated internal codesigning service rather than a certificate a secret could carry. No path exists today. A path is nonetheless available without touching any upstream file: a new `launchpad-*.yml` workflow producing unsigned artifacts, at the cost of Gatekeeper friction and no auto-update.
**Tags:** `observability` `desktop` `distribution` `ci` `codesigning` `gatekeeper`
**Reviewed:** 2026-08-22 · **Source:** `launchpad-26/buzz` at `678008ea4` · **Answers:** [#319](https://github.com/launchpad-26/buzz/issues/319)

---

## Finding

**No path exists today.** Every desktop-bundling workflow is gated to `block/buzz`, and the fork holds zero Actions secrets. The macOS signature is not a certificate the cohort could be given — it is Block's OIDC-federated internal codesigning service.

**"No path exists" is not "no path is possible", and the distinction is cheap.** The gates disable *upstream's* workflows; they do not stop this fork adding its own. A new `launchpad-*.yml` workflow could produce an unsigned desktop bundle **without touching a single upstream file**. So this is a Gatekeeper-and-trust problem, not a permissions one.

---
## The evidence

### 1. Every desktop-bundling workflow is gated to upstream

```
$ grep -n "github.repository ==" .github/workflows/*.yml
.github/workflows/desktop-release-cache-proof.yml:14:    if: github.repository == 'block/buzz'
.github/workflows/desktop-release-cache-proof.yml:68:    if: github.repository == 'block/buzz'
.github/workflows/desktop-release-cache-proof.yml:120:    if: github.repository == 'block/buzz'
.github/workflows/docker.yml:351:    if: github.repository == 'block/buzz'
.github/workflows/docker.yml:429:    if: github.repository == 'block/buzz' && github.event_name != 'pull_request'
.github/workflows/linux-canary.yml:22:    if: github.repository == 'block/buzz'
.github/workflows/macos-intel-canary.yml:15:    if: github.repository == 'block/buzz'
.github/workflows/signed-macos-canary.yml:15:    if: github.repository == 'block/buzz'
.github/workflows/windows-canary.yml:19:    if: github.repository == 'block/buzz'
.github/workflows/release.yml:17:    if: github.repository == 'block/buzz'
.github/workflows/release.yml:54:    if: github.repository == 'block/buzz'
.github/workflows/release.yml:267:    if: github.repository == 'block/buzz'
.github/workflows/release.yml:428:    if: github.repository == 'block/buzz'
.github/workflows/promote-oss-desktop-release.yml:21:    if: github.repository == 'block/buzz'
```

`release.yml` (four gated jobs), all four canaries, the cache-proof workflow and the promotion workflow. In `launchpad-26/buzz` every one of these is inert — the jobs are skipped, not failed, so nothing even reports.

Per-workflow, for the record:

| Workflow | What it does here |
|---|---|
| `release.yml` | Builds and publishes the desktop release. **All four jobs gated — never runs.** |
| `signed-macos-canary.yml`, `macos-intel-canary.yml`, `windows-canary.yml`, `linux-canary.yml` | Platform build canaries. **Gated — never run.** |
| `desktop-release-cache-proof.yml` | **Gated — never runs.** |
| `promote-oss-desktop-release.yml` | Promotes a version to auto-update. **Gated — never runs.** |
| `desktop-release-candidate.yml` | **Ungated**, but it only *validates* a `version-bump/` PR via `scripts/desktop_release.py validate`. Builds nothing. |
| `ci.yml` | **Ungated**, and its desktop job runs `just desktop-build` |

### 2. `ci.yml` does not build an app either

```
$ grep -n "^desktop-build" -A4 Justfile
134:desktop-build:
135-    cd {{desktop_dir}} && pnpm build
```

`pnpm build` is the Vite frontend build. No `tauri build`, no bundle. And none of `ci.yml`'s five `upload-artifact` steps carries an app — they are `desktop-e2e-artifacts` (playwright reports), `desktop-smoke-e2e-artifacts-*`, `desktop-e2e-relay` (a relay binary), `desktop-e2e-integration-artifacts-*` and `backend-integration-relay-log`.

So there is no artifact anywhere in this repository that a member could download and run.

### 3. The fork holds no secrets, and the signature is not a secret anyway

```
$ gh api repos/launchpad-26/buzz/actions/secrets
{"total_count":0,"secrets":[]}
```

A successful call returning zero — not a permissions error.

More importantly, the macOS signature could not be supplied by a secret even if the cohort had one. `release.yml:168-184`:

```yaml
      id-token: write # required by block/apple-codesign-action for OIDC
      ...
        uses: block/apple-codesign-action@679535d1ab7c5a7c18e6f9afcba3464512cc3dde # v1.1.0
        with:
          osx-codesign-role: ${{ secrets.OSX_CODESIGN_ROLE }}
          codesign-s3-bucket: ${{ secrets.CODESIGN_S3_BUCKET }}
```

Signing happens through **Block's internal codesigning service, federated by OIDC** to a Block-controlled role. This matches what [#318](https://github.com/launchpad-26/buzz/issues/318) observed on the installed app: `Authority=Developer ID Application: Block, Inc. (EYF346PHUG)`. That is Block's Apple Developer identity. The cohort cannot obtain it, cannot be delegated it through a repository secret, and should not try.

### 4. What a member would actually face

A locally-built bundle (`cargo tauri build`) would be unsigned or ad-hoc signed. On macOS that means:

- The `.app` carries a quarantine attribute after any transfer, so Gatekeeper refuses it with *"Buzz.app is damaged and can't be opened"* or *"cannot be opened because the developer cannot be verified"*, depending on signature state.
- The member's workaround is right-click → Open, or `xattr -d com.apple.quarantine /Applications/Buzz.app`. **Asking cohort members to strip quarantine from a binary is a security-posture decision, not a support instruction** — it is exactly the habit an attacker relies on.

Auto-update would simply not function, and cleanly so:

```json
    "updater": {
      "endpoints": []
    },
```

The tracked config carries no endpoint and no pubkey — those are injected at release time. A fork build therefore has no updater endpoint at all. That is worth knowing in both directions: no auto-update, and also **no risk of a fork build silently updating itself back to Block's build**.

### 5. Whether a path requires upstream changes — the useful part

Two routes, and they differ exactly where it matters for [#273](https://github.com/launchpad-26/buzz/issues/273):

**Route A — un-gate upstream's workflows.** Edit `if: github.repository == 'block/buzz'` in `release.yml` and the canaries. This touches upstream files that are otherwise clean, adds them to the conflict surface on every sync, and inherits jobs that expect Block's signing service. **Poor value, real cost.**

**Route B — add a `launchpad-*.yml` workflow that runs `tauri build`.** `launchpad/AGENTS.md` §3 already reserves that namespace: *"New workflows go in `.github/workflows/` (GitHub requires it) and must be named `launchpad-*.yml` so they never collide with upstream's."* **This touches no upstream file and adds nothing to the divergence register.**

So the honest answer to the DoD's divergence question is: **a distribution path need not increase the fork's divergence at all.** What it costs instead is unsigned artifacts and the Gatekeeper conversation in §4.

---

## What this means for #289

1. **Criterion 1 has a hard dependency nobody has costed.** With [#318](https://github.com/launchpad-26/buzz/issues/318): the fork ships nothing, the one installed app observed is Block-signed upstream, and no workflow here can produce a replacement. "Telemetry from every participating desktop client" needs this solved first, or restating.
2. **The cheap version of criterion 1 is available immediately and should be named separately.** Members who run `just dev` from a worktree get instrumented builds with no distribution work at all. That is a real subset of "participating clients" and it costs nothing.
3. **If the cohort does want distribution, Route B is the shape** — a `launchpad-*.yml` workflow, unsigned artifacts, no divergence cost. Someone still has to decide whether asking members to bypass Gatekeeper is acceptable. That is a security decision for a human, and given #289 already notes that Alloy on personal machines was accepted as a condition of participation, it belongs in the same conversation.
4. **Nothing in this is a blocker for the relay side**, which remains configuration rather than construction.

---

## Confidence and what is still unknown

**High confidence.** Every claim is a direct read of a tracked file or a successful API call, quoted above. The gating, the empty secret list, the `just desktop-build` definition, the artifact names, the OIDC signing action and the empty updater endpoints are all facts about the repository as it stands at `678008ea4`.

**Not verified — no workflow was run.** I did not dispatch `release.yml` or any canary to observe a skip, and I did not attempt a local `cargo tauri build`, so the Gatekeeper behaviour in §4 is the documented macOS behaviour for unsigned bundles rather than something I reproduced. Anyone who wants that nailed down can build locally and try to open the result on a second machine.

**Also not checked:** `scripts/desktop_release.py`, which `desktop-release-candidate.yml` calls — I read the workflow, not the script, so there may be capability inside it I have not seen; whether `squareup/buzz-releases` could be pointed at this fork, which is a question about a repository I cannot read; whether Windows or Linux distribution is easier than macOS, which is likely (no notarisation on Linux; Windows SmartScreen is a reputation warning rather than a block) but which I did not investigate; whether GitHub Releases on the fork would need any permission the cohort lacks; and whether an unsigned build would even pass the `egress_guard` and other tests, which I did not run.
