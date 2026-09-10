# Plan — issue #1121: corpus node for connection admission

Issue: `launchpad-26/buzz#1121` (Feature #609, protocol and networking layer corpus)
Target: `launchpad/docs/corpus/layers/networking/connection-admission.md`
Node id: `layers-networking-connection-admission`
Template: `launchpad/docs/corpus/templates/concept.md`
Base revision: `96782d1035f5bcb878edaa4b75b95ccc85ef4ce0` (`origin/launchpad`)

## ALREADY TRUE

- The worktree is on `task/1121-connection-admission` off `origin/launchpad` at the
  base revision above; `git rev-parse HEAD` confirms it.
- `launchpad/docs/corpus/layers/networking/` does not exist yet — this task creates
  the directory as well as the file.
- The relay has a module literally named `crates/buzz-relay/src/admission.rs`, and it
  is **not** connection admission: it is a per-principal rate-limit helper
  (`check_principal`, `ws_admission_budget`) used for in-band traffic. The node must
  disambiguate this name collision rather than cite it as the subject's home.
- The real admission decisions were read at source:
  - `crates/buzz-relay/src/router.rs` `nip11_or_ws_handler` — admin-host
    short-circuit, NIP-11 content negotiation, `tenant::bind_community` before the
    upgrade, `shutting_down` 503, `limit_relay_websocket` frame caps.
  - `crates/buzz-relay/src/tenant.rs` — `bind_community`, `BindError`, the
    empty-host fence, and the `redteam_attack2` tests.
  - `crates/buzz-relay/src/state.rs` — `run_registered_community_connection`
    (community-active gate) and `conn_semaphore: Semaphore::new(max_connections)`.
  - `crates/buzz-relay/src/connection.rs` — `handle_active_connection`'s
    `try_acquire_owned`, `AUTH_TIMEOUT`, `AuthState`.
  - `crates/buzz-relay/src/audio/handler.rs` — the second door on the *same*
    semaphore, checked pre-upgrade with a visible 503.
  - `crates/buzz-relay/src/config.rs` — `BUZZ_MAX_CONNECTIONS` default 10_000,
    `max_frame_bytes`.
  - `crates/buzz-auth/src/rate_limit.rs` — `check_ip_connection` and
    `LimitType::IpConnections`; a repo-wide grep finds no production call site.
  - `crates/buzz-test-client/tests/conformance_multitenant.rs` —
    `unmapped_host_fails_closed_generically`, which is `#[ignore]`d.
- Neighbouring merged nodes that already own adjacent ground and must be linked, not
  restated: `architecture-flows-websocket-connection` (the ordered lifecycle),
  `architecture-flows-websocket-authentication`,
  `architecture-principles-host-selects-community`,
  `architecture-principles-fail-closed-boundaries`,
  `layers-configuration-relay-configuration`, `implementation-crates-buzz-relay`,
  `verification-contracts-websocket`, `layers-data-redis-ttl-policy` (which already
  records the unwired `check_ip_connection`). Each id was confirmed present in the
  merged-id index.

## STEP 1 — write the front matter

Seven permitted fields only. `type: layers`, `status: draft`, `origin: launchpad`,
`id: layers-networking-connection-admission`, audiences `agent`/`developer`/`operator`
(operator earns its place: `BUZZ_MAX_CONNECTIONS` and the drain behaviour are
operational knobs). Evidence ledger: exactly one commit-only FACT for provenance,
every other FACT citing a bare repo-relative path I opened, INFERENCE entries carrying
`confidence`, and TEAM_KNOWLEDGE only for the issue's own definition of done.

**Done when:** front matter parses and carries no eighth field.

## STEP 2 — write the body against the concept template's required sections

Title + intro, **Definition** (with its explicit not-this scope), Mermaid visual aid,
Background, Use cases, Comparison (the two doors), Related resources via typed
relationships, and **Scope and omissions**.

**Done when:** every required section from `templates/concept.md` is present and the
body contains no numbered operating procedure and no exhaustive parameter table.

## STEP 3 — relationships

Only ids verified in the merged-id index; no sibling node from Feature #609.

**Done when:** every `relationships[].target` was grepped out of
`corpus-merged-ids.txt` before being written.

## STEP 4 — validate

`python3 launchpad/project-intelligence/corpus/validate.py`

**Done when:** exit 0, no new UNVERIFIED-only FACT.

## STEP 5 — stamp, commit, self-review

`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as its own sole command, then `git add` + `git commit -s` separately, then re-read the
diff against the issue's DoD line by line.

**Done when:** the unittest run prints `OK`, the commit exists, and each DoD bullet has
been checked against the diff.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
- The corpus unittest suite prints `OK` (verify-gate stamp).
- Exactly one hand-authored corpus document changed; the plan file is the only other
  new file.

## BUDGET

5 steps. One new corpus document, one plan document. No code changes.

## OPEN

- Whether the asymmetry between the two doors (relay drops the socket silently
  post-upgrade; audio returns a visible 503 pre-upgrade, and does not consult
  `shutting_down`) is intended or an oversight. The node records the asymmetry as
  observed behaviour and does not rule on it.

## LEFT OUT

- The NIP-42 authentication handshake and its ban/allowlist/membership gates — owned
  by `architecture-flows-websocket-authentication`.
- The ordered connection lifecycle narrative — owned by
  `architecture-flows-websocket-connection`.
- The admin-authority host concept (`is_admin_host` compares the raw `Host` header
  exactly, without the normalization `bind_community` applies) — a second concept,
  reported as a candidate follow-up task rather than folded in.
- Any change to runtime behaviour.
