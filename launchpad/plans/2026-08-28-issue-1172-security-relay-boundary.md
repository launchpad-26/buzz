# Plan: issue #1172 — document layers/security/relay-boundary.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`; `launchpad/docs/corpus/layers/security/relay-boundary.md` does not yet exist (confirmed: `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` lists no `layers/` subtree at all — this is the first `type: layers` node). No `layers`- or `security`-typed sibling exists to link via `relationships`, but two topically adjacent `architecture`/`principles` nodes are merged: `architecture-principles-community-is-security-boundary.md` (host→community resolution, the step immediately *after* this node's network-edge admission) and `architecture-principles-fail-closed-boundaries.md` (the general fail-closed pattern this node's shutdown-refusal and size-limit behavior instantiates).

STEP 1 — Gather evidence for the relay's network-edge admission surface, scoped to what happens *before* auth/community resolution: `router.rs` (`build_router`, `nip11_or_ws_handler`, `limit_relay_websocket`, `build_health_router`, `build_cors_layer`, the two `RequestBodyLimitLayer`s), `config.rs` (`DEFAULT_MAX_FRAME_BYTES`), `main.rs`'s `serve` (TCP/UDS listener binding, `into_make_service_with_connect_info::<SocketAddr>`, graceful-drain refusal), and `buzz-auth::rate_limit`'s `RateLimiter::check_ip_connection` contract plus its `buzz-pubsub::RedisRateLimiter` implementation. RUNS HERE.

STEP 2 — Confirm the IP-connection-limit gap precisely: grep every crate for `check_ip_connection` call sites and for an `ip_connections`/`ip_conn` config field. Record the exact result (implemented in two places, called nowhere outside its own test stub, no config knob exists) as an explicit, evidenced gap rather than an assumption. RUNS HERE.

STEP 3 — Write front matter (id `layers-security-relay-boundary`, type `layers`, status `draft`, origin `launchpad`, `references` relationships to the two nodes named above) and body stating the invariant as one MUST/MUST-NOT property: which network-edge properties the relay enforces on every inbound connection *before* any auth or host→community resolution runs (body-size caps, WS frame/message-size caps, peer-IP source, unauthenticated-surface boundaries), scope, enforcement points, observable failure behavior, and verification — including the IP-connection-limit gap from STEP 2 named honestly rather than omitted.

STEP 4 — Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until exit 0.

STEP 5 — Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own call, confirm `OK`, then commit (plan + doc) and open a draft PR against `launchpad`.

PARALLEL: none — single file, single author.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. The corpus unittest suite must report `OK` before commit. `review-adjudicate` and the cross-model review pass are deferred to the batch owner's review of PRD #607's batch, not run here.

BUDGET: single session, no rebuild loops beyond validator fix-ups.

OPEN: the issue's DoD asks for "typed relationships appropriate to the node." Two exist and are added as `references` (network-edge admission precedes host binding; shares the fail-closed shape with the general principle). Whether a future `layers/security/` sibling should instead carry a stronger relationship type (e.g. `depends-on`) once more `layers`-typed nodes land is left to that later node, per `AGENTS.md`'s guidance to check what exists rather than assume permanence.

LEFT OUT: this node does not catalogue every relay HTTP route or every auth/authorization gate (that is `architecture-principles-fail-closed-boundaries.md`'s and the eventual per-surface obligation table's job); it states the network-edge admission properties enforced ahead of auth/community resolution, names their enforcement points, and records the unwired IP-connection-limit as an explicit gap rather than implying it is enforced.
