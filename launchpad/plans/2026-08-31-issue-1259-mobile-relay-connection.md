# Plan: issue #1259 — document platforms/mobile/relay-connection.md

## ALREADY TRUE

- Issue #1259 (Feature #614) asks for exactly one hand-authored corpus node at
  `launchpad/docs/corpus/platforms/mobile/relay-connection.md`.
- `launchpad/docs/corpus/platforms/` does not exist yet on this branch or on
  `origin/launchpad` — this is the first `platforms/**` node in the corpus.
- `node.schema.json`'s `type` enum has no `platforms`-specific member beyond
  the literal `platforms` value itself; per prior-batch finding #4, sibling
  tasks in this Feature use `type: platforms` for `platforms/**` documents.
  No platforms-specific template exists in `launchpad/docs/corpus/templates/`.
- The closest fitting template is `architecture-component.md` (C4
  Component-diagram + arc42 §5 Building Block View shape): its "Required
  sections" and "Boundary" language matches this issue's DoD bullets
  ("well-defined interface/boundary", "names dependencies and collaborators",
  "component-level behavior, not the entire containing platform") almost
  verbatim. It is merged on `origin/launchpad`, so it can be followed
  directly (with `type: platforms` substituted per the Feature convention,
  not `type: architecture` as the template itself suggests for the
  architecture/ subtree).
- `architecture-containers-mobile` (id) already exists on `origin/launchpad`
  at `launchpad/docs/corpus/architecture/containers/mobile.md` and names
  `mobile/lib/shared/relay/` as the mobile container's relay implementation
  path — a confirmed `part-of` target.
- Sibling issue #1253 (`platforms/mobile/application-lifecycle.md`, not yet
  merged/existing on `origin/launchpad`) owns app-lifecycle-transition
  behavior (`AppLifecycleNotifier` in `app_lifecycle_provider.dart`, and the
  `onAppPaused`/`onAppResumed` call sites it drives). This node must not
  duplicate that — it covers the connection/auth/reconnect mechanics
  `RelaySessionNotifier` and `RelaySocket` implement themselves, referencing
  the lifecycle hook points only as collaborators, not documenting their
  internals.
- Real source read and understood at revision `131b02f989684117d9ab1dd426f1673fa638e523`:
  `mobile/lib/shared/relay/relay_socket.dart` (low-level WebSocket + NIP-42
  auth), `relay_session.dart` + `relay_session_auth.dart` (part file, NIP-98
  auth header for HTTP query) (`RelaySessionNotifier`: connect/reconnect
  orchestration, exponential backoff, subscription replay, CLOSED retry),
  `relay_session_types.dart` (`SessionStatus`, `SessionState`), `relay_provider.dart`
  (`RelayConfig`/`RelayConfigNotifier`, ws/http URL derivation), `relay_closed_policy.dart`
  (CLOSED message classification), `relay_rate_limit_gate.dart` (backpressure
  gate), `app_lifecycle_provider.dart` (lifecycle → session call sites, for
  the boundary only), `nostr_models.dart` (`EventKind.auth = 22242`).
  Tests found (not read line-by-line, cited as existence evidence for the
  gate): `mobile/test/shared/relay/relay_session_test.dart`,
  `relay_socket_liveness_test.dart`, `relay_closed_policy_test.dart`,
  `relay_rate_limit_gate_test.dart`, `relay_config_test.dart`.

## STEP 1 — Scaffold front matter by hand against node.schema.json

No `scaffold.py` template exists for `platforms`/component-style nodes with
the exact enum combination needed here, and the merged `architecture-component.md`
template's own worked convention (`type: architecture`) conflicts with the
Feature's settled `type: platforms` convention for this subtree — so front
matter is hand-authored directly against `node.schema.json`, borrowing the
*shape* (required sections, evidence expectations) from
`architecture-component.md`, not blocked on `scaffold_node`'s template
allow-list. `id: platforms-mobile-relay-connection`, `type: platforms`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer,
reviewer]`. One evidence entry per substantive claim below, each opened and
read directly (`FACT`), plus the provenance/revision entry.

## STEP 2 — Write the body per architecture-component.md's required sections

Purpose/scope paragraph naming the mobile container node it decomposes;
notation legend + Mermaid component diagram (sequence-ish: app -> RelaySocket
-> relay, with RelaySessionNotifier as orchestrator); building-block table
(RelaySocket, RelaySessionNotifier, RelayConfig/RelayConfigNotifier,
RelayClosedPolicy, RelayRateLimitGate, NIP-98 auth helper); boundary section
explicitly excluding #1253's lifecycle-transition scope, the container's
other subsystems (media, deep links, crypto), and code-level (per-method)
detail; relationships (`part-of: architecture-containers-mobile`); scope and
omissions section per AGENTS.md step 8.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py`, confirm no
new FAIL beyond the pre-existing baseline (verify by stashing the new file
and re-running).

## STEP 4 — Corpus unit tests + commit

Run the corpus test suite as its own, sole Bash call, then stage + commit
with `git commit -s`.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 and
  introduces zero new FAIL lines versus the clean-checkout baseline.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  reports `OK`, run as the sole content of its own Bash call.
- Every citation is a real file this session opened; every `FACT` claim was
  read directly, not assumed from the container-level node's prior claims.
- `relationships` target (`architecture-containers-mobile`) confirmed present
  on `origin/launchpad`'s corpus tree, not merely in this worktree.

## OPEN

- Whether `#1321`'s eventual provenance standard will require revisiting this
  node's revision-pinning practice — not resolved here, per AGENTS.md's own
  documented gap.
- Whether Mermaid can faithfully express C4 notation was not verified (same
  open item the architecture-component template itself flags); a
  plain-flowchart approximation is used instead.

## LEFT OUT

- Any second concept (e.g. a deep dive into `RelayClosedPolicy`'s retry
  backoff formula as its own node, or `RelayRateLimitGate`'s backpressure
  contract as its own node) — named in the Boundary section as a possible
  future task, not drafted here, and no `references` edge added since no such
  sibling node exists yet on `origin/launchpad`.
- App-lifecycle transition behavior itself (issue #1253's scope) — named as
  an explicit exclusion, not duplicated.
- Media upload/download, deep links, crypto, community storage — covered (or
  planned to be covered) by other `platforms/mobile/*` sibling tasks, not
  this one.
