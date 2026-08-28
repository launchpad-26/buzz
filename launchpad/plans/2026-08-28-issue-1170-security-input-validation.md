# Plan: issue #1170 — document layers/security/input-validation.md

## ALREADY TRUE

- Parent PRD #607 ("identity tenancy authentication authorization and security
  corpus exists", parent #602) lists #1170 as one of 56 child document tasks.
- `launchpad/docs/corpus/layers/` does not exist yet on disk — this is the
  first `layers`-typed node in the corpus. No `layers/security/*.md` siblings
  exist to link via `relationships`.
- `launchpad/docs/corpus/templates/` has no `layers.md` template; per the
  task brief, write directly against
  `launchpad/docs/corpus/schema/node.schema.json`.
- Confirmed `launchpad/docs/corpus/layers/security/input-validation.md` does
  not exist (`test -f` → not found).
- Repository HEAD in this worktree: `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`.
- Source evidence gathered via RepoQL:
  - `crates/buzz-core/src/verification.rs::verify_event` — Schnorr signature
    + event-ID hash verification, CPU-bound (`spawn_blocking`).
  - `crates/buzz-relay/src/handlers/ingest.rs::ingest_event` — the shared
    WS/HTTP ingest seam: kind gating → `verify_event` → timestamp drift
    (±900s) → content size (`MAX_EVENT_CONTENT_BYTES` = 256 KiB) → pubkey
    match → scope check → per-kind structural tag validation (e.g. exactly
    one `d`/`p` tag, per-field max lengths like `PROJECT_NAME_MAX_LEN`,
    `D_TAG_MAX_LEN` in `buzz-db/src/event.rs`, kind:40008 diff content capped
    at 60 KiB).
  - `crates/buzz-relay/src/protocol.rs::ClientMessage::parse` — WS frame
    shape validation (JSON array, typed `serde` deserialize into `nostr`
    crate's `Event`/`Filter`), `MAX_SUB_ID_LENGTH` (256) and
    `MAX_FILTERS_PER_REQ` (10).
  - `crates/buzz-relay/src/api/bridge.rs::submit_event`/`submit_event_authed`
    — HTTP bridge: NIP-98 auth first, then `serde_json::from_slice` into the
    same typed `Event`, then the same `ingest_event` seam.
  - `crates/buzz-relay/src/api/bridge.rs::workflow_webhook` — webhook body is
    optional untyped JSON, values coerced to strings into `webhook_fields`.

## STEP 1 — Confirm scope and re-check no duplicate exists

Done as part of ALREADY TRUE. No further action.

## STEP 2 — Draft the node

Write `launchpad/docs/corpus/layers/security/input-validation.md`:
front matter (`id: layers-security-input-validation`, `type: layers`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer,
reviewer]`, no `relationships` since no sibling node exists on disk yet) plus
a body that: defines input validation in one sentence, states the ingest
pipeline order with citations, states size/structural limits with citations,
states boundaries (excludes authorization/rate-limiting/media validation as
separate concerns), and links to the cited source files as
implementation/verification pointers (prose links, not `relationships`, since
no corpus nodes exist yet to target).

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` (expect exit
0) and re-open every cited file to confirm each evidence statement is
actually supported.

## STEP 4 — Commit gate

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as a lone command, confirm `OK`, then commit with `git commit -s`.

## STEP 5 — PR

Push the branch and open a draft PR closing #1170.

## GATES

- `validate.py` exits 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.
- Only one hand-authored file created:
  `launchpad/docs/corpus/layers/security/input-validation.md`.

## OPEN

- Whether a `layers.md` template lands later (#1307–#1351) that this node
  should be retrofitted to — not blocking; schema is authoritative today.

## LEFT OUT

- Media/Blossom upload validation (`buzz-media/src/validation.rs`) — a
  separate concern with its own likely corpus node; only referenced here as a
  boundary, not documented in depth.
- Authorization/scope enforcement — mentioned only where it interleaves with
  the validation order; the concept itself belongs to a security/authz node.
- Rate limiting / admission control (`enforce_http_admission`) — separate
  concern, boundary-noted only.
