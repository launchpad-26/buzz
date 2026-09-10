# Issue #1009 — task: document interfaces/nostr/nip-11.md

Parent PRD #616. Single-document corpus task. Issue body carries no `Size` line;
capped per the dispatching task's own instruction (cap 5 steps).

Stated size: not stated on issue -> cap: 5 steps

ALREADY TRUE
  `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md` and
  `launchpad/docs/corpus/templates/interface.md` (id `corpus-template-interface`, type
  `interfaces-events`'s home template) are merged on `origin/launchpad` at
  650354eab8d41ab6ce1a71de079a6c6d95c69052. `launchpad/docs/corpus/interfaces/` does not
  exist yet in this repository — no directory, no sibling node. The relay's NIP-11
  implementation (`crates/buzz-relay/src/nip11.rs`, wired in `crates/buzz-relay/src/router.rs`
  at `GET /` content-negotiated and `GET /info` unconditional) already exists and is
  covered by unit tests in `nip11.rs` itself and integration coverage in
  `crates/buzz-test-client/tests/e2e_relay.rs::test_nip11_relay_info` and
  `crates/buzz-test-client/tests/conformance_multitenant.rs::nip11_relay_info` (both
  `#[ignore]`d live-relay tests, not run by this task). `architecture-containers-relay` is
  a merged node this new node may cite via `part-of`.

STEP 1  [independent]  ← RUNS HERE  Gather evidence directly from source: read
        `crates/buzz-relay/src/nip11.rs` in full (RelayInfo struct, `SUPPORTED_NIPS`,
        `RelayInfo::build`, `relay_info_handler`, `nip11_document`, `relay_limitation`,
        `push_descriptor`, `workspace_icon_for_host`, `nip11_facts`, the static-input fence)
        and `crates/buzz-relay/src/router.rs`'s `nip11_or_ws_handler` (content negotiation,
        the `/info` route, CORS layering, the fail-open-for-NIP-11/fail-closed-for-WS
        split). Cross-check against `crates/buzz-test-client/tests/e2e_relay.rs::test_nip11_relay_info`
        and `conformance_multitenant.rs`'s `nip11_relay_info` module (enumeration-oracle
        proof, unmapped-host 200) and `row_zero_host_binding` (unmapped-host 404 on the
        *other* door). Fetch upstream NIP-11 itself
        (`https://raw.githubusercontent.com/nostr-protocol/nips/<pinned-sha>/11.md`) to cite
        the spec's own field list, CORS requirement and `limitation` block, and record the
        pinned commit SHA actually fetched.
        done when: every claim planned for STEP 2's evidence ledger has a specific file,
        symbol, test name, or pinned upstream URL identified, and the pinned NIP-11 commit
        SHA is recorded.

STEP 2  [needs 1]  Write `launchpad/docs/corpus/interfaces/nostr/nip-11.md`: front matter
        (`id: interfaces-nostr-nip-11`, `type: interfaces-events`, `status: draft`,
        `origin: launchpad`, `audiences: [agent, developer, reviewer]`, a commit-citation
        provenance entry for 650354eab8d41ab6ce1a71de079a6c6d95c69052, `relationships:
        [{type: implements, target: corpus-template-interface}, {type: part-of, target:
        architecture-containers-relay}]` — both targets confirmed present on
        `origin/launchpad`). Body follows the interface template's required sections:
        Interface description, an Operations table (`GET /` content-negotiated,
        `GET /info` unconditional — both point at `nip11.rs`/`router.rs` symbols, never
        restating the JSON shape), Contract and stability (auth-free/host-agnostic reads,
        the enumeration-oracle non-goal, `auth_required: true` reflecting the *WebSocket*
        auth requirement not the document read itself, versioning via `CARGO_PKG_VERSION`,
        Buzz-specific extensions — `push`, `pairing_relay_url`, `admin_api`, `gif`, `self`,
        `supported_extensions` — named as non-upstream fields), a valid example (a real
        served JSON shape from `nip11.rs`'s own test fixtures) and a failure/edge example
        (the unmapped-host case: NIP-11 itself still returns 200 with the static document,
        while the *other* door — WS upgrade / non-`nostr+json` request — 404s; cite
        `conformance_multitenant.rs` for both halves so the document does not overclaim a
        NIP-11-specific rejection path that does not exist), a Boundary section (does not
        restate any single event kind's wire contract; does not catalogue every field
        parameter-by-parameter), and Scope and omissions (what is not covered, plus
        anything from STEP 1 expected but not verified).
        done when: the file exists at the exact target path with schema-required fields
        present and every Definition-of-done bullet from the issue's own checklist
        addressed by name in the body.

STEP 3  [needs 2]  Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
        worktree root; fix any FAIL line the new node itself causes and re-run until exit 0.
        done when: the command exits 0 (UNVERIFIED notices permitted, no FAIL lines
        attributable to the new node).

STEP 4  [needs 3]  Run the corpus unittest suite as the sole command in its own tool call to
        earn the commit gate stamp, then in a separate call stage and commit exactly the new
        node file and this plan file with `git commit -s`.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        prints `OK`, and the subsequent `git commit -s` succeeds (gate stamp found, commit
        created).

STEP 5  [needs 4]  Self-review the diff against the issue's Definition-of-done checklist
        line by line; confirm every evidence entry's citation actually supports its
        statement; confirm `validate.py` still exits 0; confirm no second hand-authored
        canonical corpus document was created.
        done when: each DoD bullet is confirmed satisfied or explicitly flagged as a
        finding, and `validate.py` re-run still exits 0.

PARALLEL  None — one new file, five sequential steps, no independent work to fan out.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 (STEP 3,
          re-checked STEP 5). `python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK`
          before the commit (STEP 4) — this is the commit-gate stamp; if the commit is
          rejected for a missing stamp, that is reported as a finding, not routed around.
          `review-adjudicate` and any cross-model final review are out of scope for this
          single-document task, per the dispatching instructions (no PR is opened here).

BUDGET    STEP 2 is the bulk of the work: one interface node, evidence already gathered in
          STEP 1 from a single well-contained module (`nip11.rs`, ~700 lines) plus its two
          call sites in `router.rs` and its two test suites. No code changes, no second
          document, no batch fan-out.

OPEN      Whether `implements: corpus-template-interface` or `references` is the corpus-wide
          convention for a node's optional self-link to its own template is explicitly
          unsettled per the template's own *Expected but not verified* section — this plan
          follows the template's own stated preference (`implements`) rather than inventing
          a third answer. Whether `part-of: architecture-containers-relay` is the right
          granularity (versus no relationship at all, since NIP-11 is one HTTP surface among
          several the relay container hosts) is a judgment call made in STEP 2 and open to a
          reviewer's correction — both directions are schema-legal, and omitting it remains
          available if STEP 2's drafting finds the edge does not hold up.

LEFT OUT  Any relationship to a Nostr event-kind node (`#1337`'s template) — NIP-11 is a
          document-fetch interface, not an event-kind wire contract, and no event-kind
          instance nodes are merged yet regardless. Any change to `nip11.rs`, `router.rs`,
          or the two `#[ignore]`d live-relay test suites — this task documents existing,
          already-tested behavior and owns no runtime change. Any second corpus node (e.g.
          a NIP-05 or NIP-98 sibling) even though `router.rs` wires them alongside NIP-11 —
          those are separate corpus tasks. Opening a PR, merging, or pushing — out of scope
          per the dispatching instructions.
