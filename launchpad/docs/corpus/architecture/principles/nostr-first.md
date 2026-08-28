---
id: architecture-principles-nostr-first
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "AGENTS.md states that Buzz's primary API is NIP-29 over WebSocket, that the relay also exposes a narrow HTTP surface (NIP-11/NIP-05 metadata, POST /events, POST /query, POST /count, workflow webhooks at /hooks/{id}, Blossom media, git smart HTTP, git policy hooks, and health probes), and that these HTTP paths all preserve the same host-derived community boundary."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "AGENTS.md instructs that for new feature work, the operation should be modeled as a Nostr event (a new kind in buzz-core/src/kind.rs, with a handler in buzz-relay) rather than as a new endpoint-specific JSON API, reserving HTTP for things that genuinely need an HTTP-only surface: media upload/download (Blossom), webhooks, git smart HTTP, NIP-11/NIP-05 metadata, health checks, and the generic Nostr bridge endpoints (POST /events, POST /query, POST /count)."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "CONTRIBUTING.md's \"How to Add a New API Endpoint\" section states the same preference in the contributor-facing procedure: prefer a signed Nostr event and the existing WebSocket/POST /events ingest path over adding endpoint-specific JSON APIs, and lists the same narrow enumerated HTTP surface as the exception set."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "CONTRIBUTING.md's \"How to Add a New Event Kind\" section is the companion procedure: define the kind constant in buzz-core/src/kind.rs, define the payload type, register the required auth scope in crates/buzz-relay/src/handlers/ingest.rs's required_scope_for_kind(), and add a match arm in crates/buzz-relay/src/handlers/side_effects.rs's handle_side_effects() for post-storage side effects -- adding an HTTP bridge handler in crates/buzz-relay/src/api/ is called out there only as a fallback \"if the new kind also needs an HTTP bridge surface... that cannot practically use WebSocket\"."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "crates/buzz-relay/src/router.rs's build_router() function is the single place all HTTP routes for the relay's main listener are registered, and its own doc comment describes the router as carrying only: WebSocket (NIP-01), HTTP bridge (NIP-98), media (Blossom), git (smart HTTP), NIP-05, and health probes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "At this revision, build_router() registers routes beyond the set AGENTS.md and CONTRIBUTING.md enumerate as the narrow HTTP surface: /workflows/{workflow_id}/runs and its /approvals sub-path, /operator/communities and its archive/unarchive/availability/transfer variants, /api/invites and its policy/claim/accept-policy sub-paths, /moderation/reports, /moderation/audit, /moderation/restricted, /_mesh/demo/echo (config-gated, testbed-only), /huddle/{channel_id}/audio, and a config-gated /api/admin/v1 mount -- none of these are Nostr events; all are endpoint-specific HTTP JSON (or WebSocket-upgrade) APIs that predate or sit alongside this principle rather than being exceptions it names."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "ARCHITECTURE.md's own \"HTTP endpoints\" table (documenting the same router) omits every one of those additional routes -- it lists only /, /info, /.well-known/nostr.json, /health, /_liveness, /_readiness, /events, /query, /count, /hooks/{id}, /media/upload, /media/{sha256_ext}, the three git smart-HTTP paths, and /internal/git/policy -- so the repository's own architecture documentation has already drifted out of sync with the router it describes."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
      - "crates/buzz-relay/src/router.rs"
  - statement: "No CONTRIBUTING.md workflow section or test inside crates/buzz-relay/src/router.rs's own test module enumerates, counts, or otherwise bounds the router's route list, and no file under .github/workflows/ was found referencing router.rs or an HTTP-surface concept when the workflow directory was searched, so nothing mechanical would fail a build or CI run that added a new endpoint-specific HTTP JSON API outside the documented narrow surface."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "CONTRIBUTING.md"
    confidence: 0.6
  - statement: "CONTRIBUTING.md's \"PRs We're Unlikely to Merge\" section identifies \"Entirely new features with no prior discussion\" as a category maintainers close without a prior issue, which is the one recorded human-review friction point closest to catching an unjustified new HTTP endpoint, but it is a general PR-triage rule and does not name HTTP endpoints specifically."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
---

# Architecture principle: Nostr-first

## The invariant

New backend functionality in `buzz-relay` MUST be modeled as a signed Nostr
event -- a kind defined in `buzz-core/src/kind.rs` plus a relay-side handler
-- rather than as a new endpoint-specific HTTP JSON API, unless the
functionality genuinely requires an HTTP-only transport that a WebSocket
event cannot provide.

The relay's HTTP surface MUST stay narrow. `AGENTS.md` and `CONTRIBUTING.md`
both enumerate the same exception set as the only HTTP-only needs accepted
today: NIP-11/NIP-05 metadata, the generic Nostr bridge (`POST /events`,
`POST /query`, `POST /count`), workflow webhooks, Blossom media
upload/download, git smart HTTP, git policy hooks, and health probes. A new
general-purpose, endpoint-specific JSON API MUST NOT be added for
functionality a Nostr event could serve equally well.

## Scope

**Applies to** design and code-review decisions made when adding new
backend capability to `buzz-relay` -- specifically, the choice between
registering a new route in `crates/buzz-relay/src/router.rs` versus adding a
kind constant to `buzz-core/src/kind.rs` with a handler wired through
`crates/buzz-relay/src/handlers/ingest.rs` (`required_scope_for_kind()`) and
`crates/buzz-relay/src/handlers/side_effects.rs` (`handle_side_effects()`).
This is a design-time invariant about *new* work, not a claim that every
existing route already satisfies it -- see *Current surface* below for what
already sits outside the named exception set.

**Does not apply to** the desktop, mobile, or CLI clients' own outbound HTTP
calls to third parties, nor to the operational/deployment surfaces
documented in the other repositories listed in `AGENTS.md`'s Ecosystem
table.

## Enforcement points and observable failure behavior

**Enforcement point 1 -- contributor guidance.** `CONTRIBUTING.md`'s "How to
Add a New API Endpoint" section states the preference directly and is the
first document a human contributor is pointed to before adding a route.

**Enforcement point 2 -- agent instructions.** `AGENTS.md`'s "Prefer Nostr
events over new HTTP endpoints" note is loaded as governing instructions for
any agent working in this repository (per its own framing at the top of the
file).

**Enforcement point 3 -- PR review.** `CONTRIBUTING.md`'s "PRs We're Unlikely
to Merge" section names "Entirely new features with no prior discussion" as
a category maintainers close without a prior issue. An unjustified new HTTP
endpoint would most plausibly be caught here, but this rule is stated in
general terms and does not name HTTP endpoints or this principle
specifically.

**Observable failure behavior when violated: none automated today.** No
build fails, no test fails, and no CI check flags a PR that adds a new
endpoint-specific HTTP JSON API outside the named exception set. The only
consequence recorded anywhere in the repository is a human reviewer
declining to merge, or merging anyway. See *Verification* below for what was
checked to establish this.

## Verification

**No automated conformance mechanism exists for this invariant at this
revision.** This was checked, not assumed: `crates/buzz-relay/src/router.rs`
carries its own `#[cfg(test)] mod tests`, and none of its tests inspect or
bound the route list itself (they cover invite-path matching, git-web-GUI
path gating, and HTTP/WebSocket framing behavior instead); no
`.github/workflows/` file references `router.rs` or an "HTTP surface"
concept; and `CONTRIBUTING.md`'s own procedure for adding an endpoint
describes a manual review step, not a checked one. This is recorded as an
`INFERENCE` in the evidence ledger above, at medium confidence, because it
is an absence-of-evidence conclusion over a scope that was actually
searched rather than assumed clear.

**A concrete symptom of the gap already exists.** `ARCHITECTURE.md`'s own
"HTTP endpoints" table documents the same router `build_router()` builds,
and at this revision it is missing eleven of the routes `build_router()`
actually registers (see *Current surface*). Nothing caught that drift
before it happened, which is itself evidence for the `INFERENCE` above: if
even the documentation describing the router silently fell out of date,
there is no reason to expect an undocumented new endpoint would be caught
by anything other than a reviewer noticing.

## Current surface (as of this revision)

The exception set named by `AGENTS.md` and `CONTRIBUTING.md`, as actually
registered in `crates/buzz-relay/src/router.rs`'s `build_router()`:

| Named exception | Route(s) |
|---|---|
| NIP-11 / WebSocket upgrade | `GET /`, `GET /info` |
| NIP-05 identity | `GET /.well-known/nostr.json` |
| Health probes | `GET /health`, `GET /_liveness`, `GET /_readiness` |
| Nostr HTTP bridge | `POST /events`, `POST /query`, `POST /count` |
| Workflow webhooks | `POST /hooks/{id}` |
| Blossom media | `PUT /upload`, `PUT /media/upload`, `GET`/`HEAD /media/{sha256_ext}` |
| Git smart HTTP + policy | routes built by `api::git::git_router` / `git_policy_router` |

Routes registered in `build_router()` that are **not** covered by that
named exception set (present at this revision; not evaluated here for
whether each is individually justified -- that is a separate question from
whether the principle names them):

- `GET /workflows/{workflow_id}/runs`, `GET
  /workflows/{workflow_id}/runs/{run_id}/approvals`
- `GET`/`POST /operator/communities`, plus `.../archive`, `.../unarchive`,
  `.../availability`, `.../transfer`
- `POST /api/invites`, `GET /api/join-policy`, `GET
  /api/join-policy/terms`, `GET /api/join-policy/privacy`, `POST
  /api/invites/accept-policy`, `POST /api/invites/claim`
- `GET /moderation/reports`, `GET /moderation/audit`, `GET
  /moderation/restricted`
- `POST /_mesh/demo/echo` (404 unless `BUZZ_MESH=on` and
  `BUZZ_MESH_DEMO_ECHO=on`, per its own route comment)
- `GET /huddle/{channel_id}/audio`
- `/api/admin/v1/**` (nested only when `state.config.admin` is `Some`)

## Scope and omissions

**This document covers** the nostr-first design invariant itself: what it
asserts, where it is written down, what checks it, and what does not check
it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Why |
|---|---|
| Whether each route listed in *Current surface* as outside the named exception set is individually justified | That is a per-route product/architecture judgment, not a property of this principle, and evaluating eleven routes is a separate task from documenting the invariant that governs new ones |
| NIP-98 authentication mechanics on the bridge endpoints | A different, related concept; `ARCHITECTURE.md`'s Security Model section and its own future corpus node own it |
| The admin API's separate config-gating and host-routing rationale | Out of scope per this task's own "Out of scope" instruction; belongs to whichever node documents `crates/buzz-relay/src/api/admin/` |
| Any future automated check that could enforce this invariant | Not designed here; recorded above only as an observed absence |

**Expected but not verified when this node was written:** whether any
in-flight or planned PR already proposes closing the `ARCHITECTURE.md`
drift noted above, and whether `buzz-releases` or `sprout-oss` (the other
repositories in the Buzz ecosystem, per `AGENTS.md`'s Ecosystem table) apply
any HTTP-surface convention of their own. Neither was checked; both are
outside this repository's `launchpad/docs/corpus` scope as currently
constituted.

**No `relationships` in this node's front matter.** No other
`architecture`-typed corpus node is merged on `origin/launchpad` at this
revision (checked via `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus`), so there is nothing yet to point at. The first
sibling architecture node to merge is the moment to revisit this.
