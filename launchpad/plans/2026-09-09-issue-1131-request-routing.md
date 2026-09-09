# Plan — issue #1131: document the request-routing flow

Issue: `launchpad-26/buzz#1131` (parent Feature #609)
Target: `launchpad/docs/corpus/layers/networking/request-routing.md`
Node id: `layers-networking-request-routing`
Template: `launchpad/docs/corpus/templates/flow.md` (FLOW node body; `type: layers`
per the batch brief's resolved decision 1)
Worktree: `__worktrees/task-1131-request-routing`, branch `task/1131-request-routing`
Base: `origin/launchpad` at `29ca9b189bd3f639ba09c972b57c70538c0860c6`

## Scoping decision (made before drafting)

Two things could be called "request routing" in this relay:

1. **HTTP route dispatch** — a byte stream on a listener becomes a matched axum
   route and a handler invocation (`crates/buzz-relay/src/router.rs`).
2. **In-band Nostr verb dispatch** — a parsed `ClientMessage` becomes an
   `EVENT`/`REQ`/`COUNT`/`CLOSE`/`AUTH` handler call
   (`crates/buzz-relay/src/connection.rs`, `crates/buzz-relay/src/protocol.rs`).

This node documents **(1)**. It is the routing that answers "how does an inbound
request reach its handler", it is where the content-negotiation branch in
`nip11_or_ws_handler` lives, and (2) is already the tail of merged flow nodes
(`architecture-flows-websocket-connection`, `architecture-flows-event-ingestion`,
`architecture-flows-historical-query`). (2) is named explicitly in the Boundary as
owned elsewhere, not restated.

## Steps

1. **Front matter.** Seven-field-max front matter against
   `launchpad/docs/corpus/schema/node.schema.json`: `id`, `type: layers`,
   `status: draft`, `origin: launchpad`, `audiences`, `evidence`, `relationships`.
   Exactly one commit-only `FACT` (the provenance entry, recording the real
   worktree HEAD, not the brief's stale SHA — verified with `git cat-file -e`).
   *Done when:* front matter carries no eighth field and every `FACT` cites a bare
   repo-relative path I opened in this session.

2. **Flow statement + Sequence.** Ordered steps from listener bind through
   `axum::serve`, the three `.layer()` wrappers, route-table match across the merged
   sub-routers, per-sub-router body limits, and into `nip11_or_ws_handler`'s
   four-way content-negotiation branch. Every step cited to
   `crates/buzz-relay/src/main.rs`, `crates/buzz-relay/src/router.rs`, or the
   sub-router module that composes it. Bare paths, no line numbers (#1459).
   *Done when:* no step is uncited and no step cites a file I did not open.

3. **Diagram + Outcome.** Mermaid `sequenceDiagram` whose participants match the
   prose actors and whose messages match the numbered steps. Outcome covers the
   success path plus at least three real rejection paths read from the code: the
   unmapped-host 404 in `nip11_or_ws_handler`, the shutting-down 503 on upgrade,
   and the non-loopback 403 from `require_localhost` on the git policy router.
   *Done when:* each failure branch cites the file that implements it.

4. **Boundary, Relationships, Scope and omissions.** Boundary names host
   resolution (#1126), the HTTP surface as a concept (#1127), connection admission
   (#1121) and the in-band Nostr verb dispatch as owned elsewhere. Relationships
   target only ids grepped out of the merged-id list — no #609 sibling.
   Scope and omissions carries both required halves: what is not covered and who
   owns it, and separately what I expected to verify and could not.
   *Done when:* every relationship target appears in the merged-id list.

5. **Validate, stamp, commit.** `python3 launchpad/project-intelligence/corpus/validate.py`
   exits 0; then the unittest stamp as a sole foreground command with a 600000ms
   timeout; then `git add` + `git commit -s` as a separate call.
   *Done when:* validator exits 0, the suite ends `OK`, and the commit lands.

## Out of scope

- Any second hand-authored corpus document.
- Restating host resolution, the HTTP surface concept, or connection admission.
- Runtime product behaviour changes; ADR resolution; unrelated cleanup.
- Pushing or opening a PR.
