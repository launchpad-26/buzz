# Launchpad relay deployment mapping changes

## Audience and purpose

This document is for human operators and automation agents from any provider.
It records exactly what changed in the Launchpad relay image publication and VPS
deployment path, and why each change was necessary.

For the procedure that operators should run, use
[`VPS-DEPLOYMENT-RUNBOOK.md`](VPS-DEPLOYMENT-RUNBOOK.md). The material under
[`archived/`](archived/) is historical evidence from a failed deployment method;
it is not an alternative runbook.

## Problem being corrected

The fork inherited an internally consistent upstream deployment path:

```text
block/buzz source
  -> .github/workflows/docker.yml on main
  -> ghcr.io/block/buzz
  -> BUZZ_IMAGE, defaulting to ghcr.io/block/buzz:main
  -> deploy/compose/run.sh
  -> relay container
```

That mapping was unsafe in `launchpad-26/buzz`. A VPS checkout did not build the
root `Dockerfile`; it consumed the prebuilt image selected by `BUZZ_IMAGE`.
Because Compose supplied `ghcr.io/block/buzz:main` when `BUZZ_IMAGE` was absent,
a Launchpad deployment could complete successfully while running upstream Block
code. Repository identity on disk therefore did not prove runtime identity.

The corrected path is:

```text
launchpad-26/buzz commit on launchpad
  -> .github/workflows/docker.yml
  -> root Dockerfile, runtime target
  -> ghcr.io/launchpad-26/buzz
  -> sha-<full-40-character-commit> tag and manifest digest
  -> deploy/compose/.env BUZZ_IMAGE
  -> launchpad/deploy/run.sh policy checks
  -> deploy/compose/run.sh orchestration
  -> deploy/compose/compose.yml relay service
  -> relay container
```

Every transition is now explicit. Normal VPS deployment still consumes a
prebuilt image and does not build the root `Dockerfile` locally.

## Exact file changes and rationale

### `.github/workflows/docker.yml`

<!-- markdownlint-disable MD013 -->

| Before | After | Why |
|---|---|---|
| Branch publication listened to `main`. | Branch publication listens to `launchpad`. | The fork's canonical source branch is `launchpad`; the workflow must build the commits that Launchpad actually merges. |
| `IMAGE_NAME` could fall back to `ghcr.io/block/buzz`. | `IMAGE_NAME` is fixed to `ghcr.io/launchpad-26/buzz`. | A missing repository variable must not redirect a Launchpad build into the upstream package namespace. |
| Commit tags used the short Git SHA. | Commit tags use `sha-` plus the full 40-character Git SHA. | The complete source revision is unambiguous and directly usable as a production pin. |
| OCI metadata did not explicitly identify the Launchpad source and revision. | Metadata sets `org.opencontainers.image.source=https://github.com/launchpad-26/buzz` and `org.opencontainers.image.revision=${{ github.sha }}`. | A pulled image can identify its source repository and exact Git commit without relying only on a moving tag. |
| Provenance examples verified ownership against `block`. | Examples verify against `launchpad-26`. | Attestation verification must use the organization that publishes the corrected image. |
| The inherited APNs push-gateway jobs still targeted `ghcr.io/block/buzz-push-gateway`. | Both gateway jobs run only when `github.repository == 'block/buzz'`. | Launchpad does not operate that separate service, and silently retargeting it would make an unsupported infrastructure decision. Keeping the inherited jobs conditional also reduces future upstream merge divergence. |

<!-- markdownlint-enable MD013 -->

The relay build remains multi-architecture (`linux/amd64` and `linux/arm64`).
Each architecture is pushed by digest, the merge job creates the multi-arch
manifest, and GitHub Actions attaches build-provenance attestations.

The resulting publication behavior is:

- a push to `launchpad` publishes `:launchpad`,
  `:sha-<full-40-character-commit>`, and corresponding `debug-` tags;
- a `relay-v*` tag retains the inherited semver tag family and stable-release
  `:latest` behavior;
- a pull request builds but does not publish an image;
- Block push-gateway jobs are skipped in `launchpad-26/buzz`.

The moving `:launchpad` tag is supplementary. It is not the recommended
production value.

### `Dockerfile`

The header and OCI source, URL, and documentation labels now point to
`https://github.com/launchpad-26/buzz` instead of `block/buzz`.

This change is metadata-only; the build stages and runtime contents are not
forked. The labels matter because they make image ownership and provenance
inspectable and associate the GHCR artifact with the repository that built it.
They do not remove upstream Apache-2.0 attribution or change runtime
dependencies.

### `deploy/compose/compose.yml`

The relay image expression changed from:

```yaml
image: ${BUZZ_IMAGE:-ghcr.io/block/buzz:main}
```

to:

```yaml
image: ${BUZZ_IMAGE:?BUZZ_IMAGE must be set to an immutable relay image}
```

The previous expression silently executed upstream code when the variable was
missing. The required-variable expression makes image selection fail closed and
uses Compose interpolation supported by the project's required Docker Compose
V2 version. It deliberately does not choose a default Launchpad tag either:
production image selection is an operator decision and must be reviewable.

### `deploy/compose/.env.example`

The example image changed from the moving upstream value
`ghcr.io/block/buzz:main` to the clearly incomplete Launchpad form:

```text
ghcr.io/launchpad-26/buzz:sha-CHANGE_ME_FULL_40_CHARACTER_GIT_COMMIT
```

The example teaches the correct namespace and immutable commit-tag format
without checking a real environment value or credential into Git. The local
`deploy/compose/.env` remains ignored and must contain the real deployment
configuration.

### `deploy/compose/README.md`

The canonical Compose documentation now explains that GitHub Actions builds the
image, the VPS consumes it through `BUZZ_IMAGE`, and normal Launchpad operations
start through the policy guard. It also records the distinct pull behavior of
`start`, `upgrade`, and `restart`, plus traceability and rollback commands.

This documentation was necessary because the old quick start made the upstream
image default look authoritative and did not expose the source-to-runtime gap.

### `launchpad/deploy/run.sh`

This is a new, thin policy guard. Before delegating, it:

1. requires Docker and Docker Compose V2;
2. requires Compose version 2.24.4 or newer;
3. requires the local, untracked `deploy/compose/.env`;
4. requires exactly one non-empty `BUZZ_IMAGE` assignment in that file;
5. rejects `ghcr.io/block/buzz`, including tags and digests;
6. rejects every namespace except `ghcr.io/launchpad-26/buzz`;
7. accepts a digest or full 40-character `sha-...` tag as immutable;
8. warns and rejects a floating tag unless
   `BUZZ_ALLOW_FLOATING_IMAGE=true` is deliberately set for development or
   testing;
9. exports the reviewed `.env` image so an ambient shell variable cannot
   replace it; and
10. delegates the requested operation to `deploy/compose/run.sh`.

The `check` command performs the policy checks and renders the canonical Compose
configuration without changing services. The override for floating tags never
permits an upstream Block image.

The guard contains no copied Compose lifecycle logic and owns no parallel
stack. That isolation gives Launchpad a strict image policy without maintaining
a fork of upstream orchestration.

### `launchpad/deploy/README.md` and `launchpad/deploy/AGENTS.md`

These files identify `launchpad/deploy/run.sh` as the active guard, preserve
`deploy/compose/run.sh` as the canonical runner, and mark everything under
`archived/` as non-executable historical material.

This boundary is explicit because the former experiment was based on the wrong
image-flow model. Retaining it as an apparent alternative would invite humans
or agents to reintroduce the same upstream-image failure.

## What intentionally did not change

- `deploy/compose/run.sh` remains the only Compose lifecycle implementation.
- `deploy/compose/compose.caddy.yml`, `compose.dev.yml`, and `Caddyfile` retain
  their upstream-compatible roles.
- The VPS still pulls a prebuilt image; it does not build the relay locally.
- Release-tag semantics remain inherited except that artifacts publish in the
  Launchpad namespace with full-SHA traceability.
- The Block APNs push-gateway implementation remains in the shared workflow but
  cannot execute in the Launchpad repository.
- Historical files under `launchpad/deploy/archived/` were not converted into
  a supported deployment path.

These choices minimize the conflict surface when merging future changes from
`block/buzz`. Likely conflict points are the four shared upstream files changed
for correctness: `.github/workflows/docker.yml`, `Dockerfile`,
`deploy/compose/compose.yml`, and `deploy/compose/README.md`. Launchpad policy
and operator guidance remain isolated under `launchpad/deploy/`.

## Failure behavior after the change

<!-- markdownlint-disable MD013 -->

| Scenario | Result |
|---|---|
| `BUZZ_IMAGE` missing from `.env` | Guard aborts; Compose also rejects the missing variable. |
| `BUZZ_IMAGE` empty or assigned more than once | Guard aborts. |
| `ghcr.io/block/buzz:main` or another Block relay reference | Guard aborts even if the floating-image override is set. |
| Full Launchpad commit tag | Accepted, for example `ghcr.io/launchpad-26/buzz:sha-<40-hex-commit>`. |
| Launchpad manifest digest | Accepted, for example `ghcr.io/launchpad-26/buzz@sha256:<64-hex-digest>`. |
| Moving Launchpad tag such as `:launchpad` | Warning followed by rejection in normal use; accepted only with the explicit development/testing override. |
| Direct use of canonical Compose with no `BUZZ_IMAGE` | Compose aborts instead of selecting Block Buzz. |

<!-- markdownlint-enable MD013 -->

## Source-to-runtime traceability

For a concrete source commit `GIT_COMMIT`, the workflow publishes:

```text
ghcr.io/launchpad-26/buzz:sha-GIT_COMMIT
```

The multi-arch manifest also has a `sha256:` digest. Production should place
the digest reference in `deploy/compose/.env`; the full-SHA tag is the fallback
immutable choice. The running image exposes
`org.opencontainers.image.revision=GIT_COMMIT`, while the workflow attestation
binds the manifest digest to the GitHub build. The runbook contains the exact
inspection commands.

## Validation boundary

Static validation can prove the workflow configuration, Compose failure mode,
guard behavior, YAML structure, shell syntax, and source-to-image mapping. It
cannot prove that GHCR accepted a publication or that a real VPS can pull the
package. After this change reaches `launchpad`, an operator must confirm a
successful Docker workflow run, the expected full-SHA tag and digest in
`ghcr.io/launchpad-26/buzz`, package visibility or authentication, attestation
verification, and a fresh VPS deployment before treating the live chain as
proven.
