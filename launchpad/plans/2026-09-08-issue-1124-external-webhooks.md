# Plan — issue #1124: document `layers/networking/external-webhooks.md`

Issue: launchpad-26/buzz#1124 (Feature #609, protocol and networking layer corpus)
Base: `origin/launchpad` @ `96782d1035f5bcb878edaa4b75b95ccc85ef4ce0`
Branch: `task/1124-external-webhooks`
Target: `launchpad/docs/corpus/layers/networking/external-webhooks.md`
Node id: `layers-networking-external-webhooks`
Template: `launchpad/docs/corpus/templates/concept.md`

## ALREADY TRUE

- `launchpad/docs/corpus/layers/networking/` does not exist yet. Existing `layers/`
  subtrees are `compute`, `configuration`, `data`, `lifecycle`, `observability`.
- Two webhook nodes are already merged on `origin/launchpad` and were read in full:
  - `capabilities/workflows/webhook-trigger.md` (`capabilities-workflows-webhook-trigger`)
    owns the `POST /hooks/{id}` **handler** — its eight ordered preconditions, secret
    lifecycle at save time, and every rejection status.
  - `capabilities/workflows/webhook-action.md` (`capabilities-workflows-webhook-action`)
    owns the `call_webhook` **action** — elevated authority, `check_ssrf`, DNS pinning,
    the write fence, the two stable failure codes.
  - Neither describes the *network surface* properties: the middleware stack the route
    sits under, the 1 MiB request-body limit, CORS, the Host-derived community binding
    as a networking property, or the absence of request-rate control. `webhook-trigger`
    explicitly records "Rate limiting or abuse protection on `/hooks/{id}` was not
    checked" as an unverified gap.
- Sources read directly at the base revision:
  - `crates/buzz-relay/src/router.rs` — `/hooks/{id}` registered on `api_router`;
    `RequestBodyLimitLayer::new(1024 * 1024)` on that router; `track_metrics`,
    `http_trace_layer()` and `build_cors_layer(...)` applied over the merged router;
    `build_cors_layer` is permissive when `cors_origins` is empty.
  - `crates/buzz-relay/src/api/bridge.rs` — `workflow_webhook`, its no-user-auth doc
    comment, its `Host`-header bind, its header-then-query secret read. No rate-limiter
    call anywhere in the handler.
  - `crates/buzz-relay/src/tenant.rs` — `bind_community` row-zero fail-closed binding.
  - `crates/buzz-workflow/src/executor.rs` — `call_webhook_impl`: 10 s client timeout,
    `no_proxy()`, redirects disabled, DNS pinned via `.resolve()`, 1 MiB response cap,
    no signing header, no retry.
  - `desktop/src/features/workflows/ui/WorkflowWebhookSecretDialog.tsx` and
    `desktop/src-tauri/src/relay.rs` — the published URL is
    `<relay http base>/hooks/<workflow id>`, derived from the relay URL by swapping
    `ws`/`wss` for `http`/`https`, i.e. the same authority that binds the community.
  - Rate limiters exist for media upload, invite claim, GIF search and connection
    admission (`api/media.rs`, `api/invites.rs`, `api/gifs.rs`, `connection.rs`) —
    none for `/hooks/{id}`.
- Legal relationship targets confirmed present in the merged-id index:
  `capabilities-workflows-webhook-trigger`, `capabilities-workflows-webhook-action`,
  `architecture-principles-host-selects-community`, `architecture-principles-nostr-first`,
  `architecture-containers-relay`, `verification-contracts-http`.

## STEP 1 — create the file with schema-valid front matter

Write `launchpad/docs/corpus/layers/networking/external-webhooks.md` with
`id: layers-networking-external-webhooks`, `type: layers`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, operator]`, one commit-only
provenance FACT for `96782d1035f5bcb878edaa4b75b95ccc85ef4ce0`, and one entry per
substantive claim classified FACT / INFERENCE / TEAM_KNOWLEDGE per the schema's
conditional rules. Citations are bare repo-relative paths; issue-only sources are
`TEAM_KNOWLEDGE` with `provided_by`.

Done when: front matter carries exactly the seven permitted fields and every entry
obeys the FACT/INFERENCE/TEAM_KNOWLEDGE field rules.

## STEP 2 — write the body to the concept template's required sections

Title + intro, **Definition** (one sentence first), a Mermaid visual aid, Background,
Use cases, a Comparison table (inbound vs outbound network properties), an explicit
**Boundary** section naming what the two merged workflow nodes own, and **Scope and
omissions** carrying both required halves.

Done when: every required section from `templates/concept.md` is present, and the
Boundary section names `capabilities-workflows-webhook-trigger` and
`capabilities-workflows-webhook-action` by id with what each owns.

## STEP 3 — add typed relationships

Six `references` edges, each verified against the merged-id index before writing.
No edge to any sibling node from Feature #609.

Done when: each target string appears in the merged-id index.

## STEP 4 — validate

`python3 launchpad/project-intelligence/corpus/validate.py`

Done when: exit 0.

## STEP 5 — stamp and commit

`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as a lone command; confirm `OK`; then, as a separate call,
`git add` + `git commit -s -m "docs(corpus): document external webhooks (#1124)"`.

Done when: the commit exists on `task/1124-external-webhooks`.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
- The corpus unittest suite reports `OK` before any commit.
- No push, no PR.
- Exactly one hand-authored corpus document changed.

## BUDGET

Five steps, one new corpus file, one new plan file. No code change.

## OPEN

- Whether a `layers/networking/` `README` or index is expected alongside the first
  node in that subtree. No such file exists in any other `layers/` subtree at the base
  revision, so none is created here.

## LEFT OUT

- Re-deriving the `POST /hooks/{id}` handler's precondition order or the
  `call_webhook` SSRF mechanics — both are already canonical elsewhere and are linked,
  not restated.
- Any change to runtime behaviour, including filing or fixing the absent rate limit on
  `/hooks/{id}`. This node records the observation; the fix is not this task's.
- A second corpus node for the relay's HTTP middleware stack as a whole (see the
  report's candidate follow-up).
