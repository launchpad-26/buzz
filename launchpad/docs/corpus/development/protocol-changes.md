---
id: development-protocol-changes
type: development
status: draft
origin: launchpad
audiences:
  - developer
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "crates/buzz-relay/src/protocol.rs is the relay's NIP-01 client/relay message layer: it declares ClientMessage with exactly five variants (Event, Req, Close, Count, Auth), parses a raw frame in ClientMessage::parse by matching the first array element against the literals EVENT, REQ, COUNT, CLOSE and AUTH, and rejects anything else through a catch-all arm returning RelayError::InvalidMessage(\"unknown message type\")."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "The same file declares RelayMessage as a namespace struct with seven associated functions that each return a JSON string: auth_challenge, event, notice, eose, ok, closed and count -- so every relay-to-client frame shape the relay can emit is defined in one place."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "crates/buzz-relay/src/connection.rs is where a parsed ClientMessage is dispatched: handle_text_message calls ClientMessage::parse, answers a parse failure with RelayMessage::notice, and then matches the five variants; the AUTH challenge frame is emitted from handle_active_connection before any client frame is read."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "crates/buzz-relay/src/protocol.rs enforces two advertised wire limits in the parser itself, as private module constants MAX_SUB_ID_LENGTH = 256 and MAX_FILTERS_PER_REQ = 10, applied to both the REQ and the COUNT arms."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "crates/buzz-relay/src/nip11.rs declares SUPPORTED_NIPS as the sorted list [1, 2, 10, 11, 16, 17, 23, 25, 29, 33, 38, 42, 50, 56], holds NIP-43 out of that static list as NIP_RELAY_MEMBERSHIP, and appends it in RelayInfo::build only when advertise_nip43 is true -- guarded by a debug_assert requiring relay_self to be Some, because NIP-43 events are verified against the NIP-11 self field."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "nip11.rs carries unit tests that pin the advertisement's shape rather than only its contents: supported_nips_are_sorted asserts the constant equals its own sorted copy, nip43_not_in_static_supported_nips asserts NIP-43 is absent from the static list, and build_nip43_without_self_panics_in_debug asserts the debug_assert fires."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "Un-numbered Buzz protocol extensions are advertised through a separate supported_extensions string array rather than through supported_nips: RelayInfo::build seeds it with \"nip-er\", pushes \"buzz-gif\" when a GIF provider is configured, and nip11_document pushes \"nip-pl\" when push delivery is configured."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "The advertised max_limit is bound to buzz_db::DEFAULT_MAX_PAGE_LIMIT, the same constant the REQ path clamps to, and relay_limitation's own doc comment states this is so \"the advertised ceiling and the enforced one cannot drift\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "That anti-drift binding covers max_limit only: relay_limitation writes max_filters: Some(10) and max_subid_length: Some(256) as bare integer literals, and a grep for MAX_FILTERS_PER_REQ and MAX_SUB_ID_LENGTH across crates/ returns hits in crates/buzz-relay/src/protocol.rs alone, so no constant and no test binds the enforced limits to the advertised ones."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
      - "crates/buzz-relay/src/protocol.rs"
      - "grep(pattern='MAX_FILTERS_PER_REQ|MAX_SUB_ID_LENGTH|max_subid_length|max_filters', path='crates/', include='*.rs') -> only crates/buzz-relay/src/protocol.rs defines or reads the two enforcement constants; crates/buzz-relay/src/nip11.rs lines 91, 95, 133 and 135 mention the advertised fields as literals, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "The advertised-versus-enforced limit divergence this node warns about has already happened once in this repository: commit 23f0c26b1ceba8e07bf3c160a1e08c7bda82ccd9, \"fix(relay): align NIP-11 max_limit with REQ ceiling\", records that the NIP-11 document advertised limitation.max_limit of 10,000 while the effective WebSocket REQ page ceiling was 1,000 -- \"a 10x lie\" in which a trusting client \"silently receives 1,000\" and reads the short page as exhaustion, dropping up to 9,000 events with no error; the fix touched crates/buzz-relay/src/nip11.rs among four other files and produced the DEFAULT_MAX_PAGE_LIMIT binding that exists today."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
      - "commit 23f0c26b1ceba8e07bf3c160a1e08c7bda82ccd9"
  - statement: "This repository checkout is shallow, so its Git history is partial: git rev-parse --is-shallow-repository reports true, and git log for crates/buzz-relay/src/protocol.rs returns only two commits."
    entry_class: FACT
    evidence:
      - "git_rev_parse(--is-shallow-repository) -> true; git_log(paths=['crates/buzz-relay/src/protocol.rs']) -> 73cc31cc5, d99ad131f only, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "nip11.rs ends with a const function-pointer binding named _RELAY_INFO_BUILD_STATIC_INPUT_FENCE whose declared purpose is that adding a &Db, &AppState, search handle or any other unscoped input to RelayInfo::build stops the function pointer's type from matching and makes the file fail to compile."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "crates/buzz-relay/src/router.rs is the route table: it serves the NIP-11 document and the WebSocket upgrade from the same content-negotiated GET / handler, the same document again at GET /info, NIP-05 at GET /.well-known/nostr.json, and the three generic Nostr bridge endpoints POST /events, POST /query and POST /count, all handled in crates/buzz-relay/src/api/bridge.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "Buzz defines no Filter type of its own: crates/buzz-core/src/filter.rs imports nostr::Filter and supplies only the matching functions filters_match (OR across filters) and filter_match_one (AND within one filter, including NIP-01 id prefix matching), so filter parsing is whatever serde produces for the upstream nostr crate's type."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/filter.rs"
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "crates/buzz-core/src/verification.rs owns verify_event, which recomputes the event id via EventId::new before checking the Schnorr signature, and whose module documentation states it is CPU-bound and must be called through tokio::task::spawn_blocking in async contexts."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/verification.rs"
  - statement: "The same wire vocabulary is implemented four more times outside crates/buzz-relay/src/protocol.rs: crates/buzz-ws-client/src/message.rs parses EVENT, OK, EOSE, CLOSED, NOTICE, AUTH and COUNT; desktop/src/shared/api/relayClientSession.ts branches on AUTH, EVENT, OK, EOSE, CLOSED and NOTICE; mobile/lib/shared/relay/relay_session.dart switches on EVENT, EOSE, CLOSED and OK with AUTH handled separately in mobile/lib/shared/relay/relay_socket.dart; and crates/buzz-pair-relay/src/lib.rs re-implements the protocol independently, matching only REQ, EVENT and CLOSE."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/message.rs"
      - "desktop/src/shared/api/relayClientSession.ts"
      - "mobile/lib/shared/relay/relay_session.dart"
      - "mobile/lib/shared/relay/relay_socket.dart"
      - "crates/buzz-pair-relay/src/lib.rs"
  - statement: "crates/buzz-pair-relay/src/lib.rs contains no reference to buzz_relay or ClientMessage, confirming it is an independent implementation of the wire protocol rather than a consumer of the relay's message layer."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/lib.rs"
      - "grep(pattern='buzz_relay|ClientMessage', path='crates/buzz-pair-relay/src/lib.rs') -> no matches, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "Buzz-defined protocol extensions are specified as Markdown drafts under docs/nips/, which holds 22 such documents; NIP-ER.md is the specification behind the \"nip-er\" entry in supported_extensions and opens with the status line \"`draft` `optional` `relay`\" followed by a Motivation section."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-ER.md"
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "CONTRIBUTING.md documents two adjacent procedures with their own numbered steps: \"How to Add a New Event Kind\", which starts at buzz-core/src/kind.rs, and \"How to Add a New API Endpoint\", which opens by directing the reader to prefer a signed Nostr event and the existing ingest path and enumerates the narrow HTTP surface the relay intentionally exposes."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "CONTRIBUTING.md's Architecture Overview states \"Event kinds are the only switch\" and that adding a new feature means defining a new kind, with \"No breaking changes to existing clients\"."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "No lane in the Justfile or in .github/workflows/ci.yml executes the unit tests in crates/buzz-relay/src/protocol.rs or crates/buzz-relay/src/nip11.rs: just test-unit's only buzz-relay step is `cargo nextest run -p buzz-relay --lib` filtered by `-E 'test(/^api::admin::/) ...'`, and every package(buzz-relay) filter in ci.yml selects api::admin::tests, api::invites::tests or handlers::relay_admin::tests. ci.yml does build them, via `cargo nextest archive ... -p buzz-relay --lib`, but no run step selects them."
    entry_class: FACT
    evidence:
      - "Justfile"
      - ".github/workflows/ci.yml"
      - "grep(pattern='p buzz-relay|package\\(buzz-relay\\)', path='.github/workflows/') -> ci.yml lines 379, 383, 747, 759, 797, 814, 839, 853, 1094; the four -E filters at 747, 759, 797, 814 and the two at 839, 853 name only api::invites::tests, handlers::relay_admin::tests and api::admin::tests, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "The Justfile states the reason such enumeration is necessary in its own comments: \"nothing in CI runs `cargo test --workspace`\" and \"workspace membership alone buys clippy/check, not a single executed test\", and separately records that `just test-unit` did not enumerate `buzz-relay --lib` until the admin lane was added, so those tests \"ran in no lane and a red one could ship green\"."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "just check runs fmt-check, clippy, desktop-check, desktop-tauri-fmt-check, desktop-tauri-clippy, web-check, mobile-check, security-review-check and file-size-check -- static checks only, no Rust test execution -- and just ci is `check test-unit desktop-test desktop-build desktop-tauri-check desktop-tauri-test web-build mobile-test`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "crates/buzz-test-client/tests/e2e_nostr_interop.rs is the protocol interoperability suite, carrying tests named for the NIP each exercises -- test_nip50_search_returns_results_and_eose, test_nip50_search_mixed_filters_rejected, test_nip10_thread_reply_creates_metadata, test_nip17_gift_wrap_accepted, test_historical_req_dedup_preserves_or_semantics, test_empty_kinds_returns_zero_events and the NIP-DV third-party rejection set among others -- and .github/workflows/ci.yml runs it with `cargo test -p buzz-test-client --test e2e_nostr_interop -- --ignored --nocapture` in a Postgres-backed job."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs"
      - ".github/workflows/ci.yml"
  - statement: "`just test` does not execute the Nostr interop suite: the file carries 26 #[ignore] attributes against 25 #[tokio::test] functions and no un-ignored #[test], while just test and just test-integration both delegate to scripts/run-tests.sh, whose integration path runs `cargo test --test '*' -- --nocapture` and which contains no --ignored flag anywhere -- so the suite is compiled and skipped locally, and only the ci.yml invocation and an explicit --ignored run execute it."
    entry_class: FACT
    evidence:
      - "scripts/run-tests.sh"
      - "Justfile"
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs"
      - "grep(pattern='ignored', path='scripts/run-tests.sh') -> one comment-only hit at line 97, no --ignored flag on any cargo invocation; grep -c '#[ignore]' e2e_nostr_interop.rs -> 26; grep -c '#[tokio::test]' -> 25; grep -c '#[test]' -> 0, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "scripts/start-relay-for-tests.sh and scripts/start-isolated-test-relay.sh both exist and are executable, so a reader running the interop suite locally has a documented bring-up path that does not require just relay."
    entry_class: FACT
    evidence:
      - "scripts/start-relay-for-tests.sh"
      - "scripts/start-isolated-test-relay.sh"
  - statement: "No automated check keeps the Rust kind and protocol constants in sync with their desktop TypeScript and mobile Dart mirrors: a search for references to kinds.ts or nostr_models outside the TypeScript sources returns only desktop test imports and one hand-written comment at desktop/src-tauri/src/commands/channels/fetch.rs reading \"aligned with desktop/src/shared/constants/kinds.ts::CHANNEL_MESSAGE_EVENT_KINDS\"."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/channels/fetch.rs"
      - "grep(pattern='kinds.ts|nostr_models', include='*.rs,*.mjs,*.js,*.sh,Justfile') -> desktop/src/features/notifications/lib/sound.test.mjs, desktop/src/shared/constants/kinds.test.mjs, desktop/src/shared/api/presenceRelaySubscription.test.mjs and desktop/src-tauri/src/commands/channels/fetch.rs only, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "The repository does build cross-language drift guards when it decides to: the Justfile enumerates `cargo nextest run -p buzz-agent --lib` specifically because model_capabilities.rs embeds scripts/model-capabilities.json and scripts/normative-corpus.json via include_str! and replays the locked corpus, so \"a manifest edit that diverges Rust from the corpus\" cannot ship green."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "NOSTR.md is the repository's contract with third-party Nostr clients: it states Buzz speaks NIP-29 natively with NIP-42 authentication, that the NIP-28 compatibility proxy has been removed, and that \"The Nostr wire format does not grow a tenant tag\" -- the community is resolved from the host before AUTH, EVENT, REQ, REST, media, git, search or workflow traffic is handled."
    entry_class: FACT
    evidence:
      - "NOSTR.md"
  - statement: "Because ClientMessage::parse rejects an unrecognised verb with RelayError::InvalidMessage and connection.rs answers a parse failure with a NOTICE, a client that speaks a newly added verb to a relay that has not yet deployed it receives a NOTICE rather than a silent drop or a connection close -- so a verb addition degrades to a diagnosable error on old relays, whereas a new event kind is simply an event the old relay stores and ignores."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
      - "crates/buzz-relay/src/connection.rs"
      - "CONTRIBUTING.md"
    confidence: 0.85
  - statement: "Adding a NIP number to SUPPORTED_NIPS is a client-visible promise that is harder to withdraw than the code that implements it, because clients read supported_nips to decide which requests to make and the desktop pairing probe already keys off one such entry -- so an advertisement that outruns the implementation misroutes clients rather than merely failing their requests."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
    confidence: 0.8
  - statement: "Issue #861's definition of done requires that the document state goal, prerequisites and allowed environment/scope, provide ordered executable project-specific steps, define success verification and rollback/cleanup where relevant, and link authoritative commands and configuration rather than giving generic advice."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#861 definition of done"
  - statement: "Issue #861's definition of done requires that the document represent one independently maintainable knowledge node, and that any newly discovered second concept, contract or procedure be filed as a separate task rather than folded into this document."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#861 definition of done"
  - statement: "The sibling node development/event-kind-changes.md is owned by issue #858 and is not merged; launchpad/docs/corpus/development/ on origin/launchpad contains exactly build.md, debugging.md, hermit.md and prerequisites.md, so the boundary against it is stated in prose and cannot be declared as a relationship edge."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/build.md"
      - "launchpad/docs/corpus/development/debugging.md"
      - "launchpad/docs/corpus/development/hermit.md"
      - "launchpad/docs/corpus/development/prerequisites.md"
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/development') -> build.md, debugging.md, hermit.md, prerequisites.md, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "The corpus has no interfaces/ subtree at all: git ls-tree of origin/launchpad under launchpad/docs/corpus/interfaces returns nothing, and the 229 Markdown files present live under agents/, architecture/, capabilities/, development/, layers/, schema/, standards/ and templates/ only -- so there is no merged NIP reference shelf for this node to defer canonical protocol content to."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/interfaces') -> empty; git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> 229 .md files under agents/, architecture/, capabilities/, development/, layers/, schema/, standards/, templates/, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "Every relationship target this node declares was read out of origin/launchpad rather than out of the working tree: corpus-template-procedure, architecture-principles-nostr-first, architecture-flows-http-event-submission, architecture-flows-websocket-authentication and development-prerequisites."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
      - "launchpad/docs/corpus/architecture/principles/nostr-first.md"
      - "launchpad/docs/corpus/architecture/flows/http-event-submission.md"
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
      - "git_show(ref='origin/launchpad', paths=['launchpad/docs/corpus/templates/procedure.md', 'launchpad/docs/corpus/architecture/principles/nostr-first.md', 'launchpad/docs/corpus/architecture/flows/http-event-submission.md', 'launchpad/docs/corpus/architecture/flows/websocket-authentication.md', 'launchpad/docs/corpus/development/prerequisites.md']) -> ids corpus-template-procedure, architecture-principles-nostr-first, architecture-flows-http-event-submission, architecture-flows-websocket-authentication, development-prerequisites, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "launchpad/docs/corpus/templates/procedure.md states that a node built from it should declare implements targeting corpus-template-procedure once that template is merged, because relationships.schema.json names \"a template instance of a standard\" as the implements type's own worked example."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
relationships:
  - type: implements
    target: corpus-template-procedure
  - type: references
    target: architecture-principles-nostr-first
  - type: references
    target: architecture-flows-http-event-submission
  - type: references
    target: architecture-flows-websocket-authentication
  - type: references
    target: development-prerequisites
---

# Change the Buzz wire protocol: how-to

How to change the shape of what Buzz speaks on the wire — the Nostr message
vocabulary, the set of NIPs the relay claims to support, the advertised limits, and
the narrow HTTP bridge that mirrors them. Perform this when a change cannot be
expressed as a new event kind, because the wire protocol is the one surface in Buzz
where "add a kind" is not the answer.

## Before you start

- **A working Rust toolchain through Hermit.** Activate it first
  (`. ./bin/activate-hermit`) so `./bin` leads `PATH`; see
  `launchpad/docs/corpus/development/prerequisites.md` for the tool set and
  `launchpad/docs/corpus/development/hermit.md` for the activation contract.
- **A relay you can run, and Postgres and Redis behind it.** Several verification
  steps below need a live relay. `just relay` starts one at `ws://localhost:3000`
  for hand-driven checks; `./scripts/start-relay-for-tests.sh` and
  `./scripts/start-isolated-test-relay.sh` are the bring-up paths for the test
  suites.
- **Read the constraint before you design against it.** `CONTRIBUTING.md`'s
  *Architecture Overview* states "Event kinds are the only switch" and that adding a
  feature means defining a new kind, with "No breaking changes to existing clients".
  A wire-protocol change is the deliberate exception to that sentence, not an
  oversight in it.
- **Know which repository this is.** These steps change Buzz itself and belong at
  `block/buzz`. This corpus documents them; it is not where the change lands.

**Scope of this how-to.** It covers the four surfaces that make up the wire
protocol: the NIP-01 message vocabulary in `crates/buzz-relay/src/protocol.rs`, the
NIP-11 capability advertisement in `crates/buzz-relay/src/nip11.rs`, the filter and
limit semantics enforced across `crates/buzz-core/src/filter.rs` and the parser, and
the generic HTTP bridge registered in `crates/buzz-relay/src/router.rs`. It does not
cover adding a kind integer — see *Boundary*.

## 1. Classify the change before touching any code

Most changes that feel like protocol changes are not. Work down this list and stop at
the first match.

1. **Can the operation be a new event kind?** If yes, stop here. `CONTRIBUTING.md`
   §*How to Add a New Event Kind* is the procedure, starting at
   `crates/buzz-core/src/kind.rs`. A new kind reaches old relays as an event they
   store and ignore; a new verb does not.
2. **Does it only need an HTTP shape?** Read `CONTRIBUTING.md` §*How to Add a New API
   Endpoint* first — it opens by telling you to prefer a signed Nostr event and the
   existing ingest path, and enumerates the narrow surface the relay intentionally
   exposes. Adding to `crates/buzz-relay/src/router.rs` is the exception, not the
   default.
3. **Is it a new Buzz-defined extension?** Write the specification first, as a
   Markdown draft under `docs/nips/`. That directory holds 22 such documents;
   `docs/nips/NIP-ER.md` is a worked example, opening with the status line
   `` `draft` `optional` `relay` `` and a Motivation section before any wire detail.
   The draft is what the `supported_extensions` string later points at.
4. **Is it a change to an existing NIP's semantics?** Then it is a change to how
   `crates/buzz-core/src/filter.rs`, `crates/buzz-relay/src/handlers/` or
   `crates/buzz-core/src/verification.rs` behave, and the advertisement in
   `nip11.rs` may already be correct. Skip to task 4.
5. **Only if none of the above fits** are you adding or changing a wire verb.
   Continue to task 2.

One structural constraint applies to every branch. `NOSTR.md` states that "The Nostr
wire format does not grow a tenant tag": the community is resolved from the request
host before AUTH, EVENT, REQ, REST, media, git, search or workflow traffic is
handled. A protocol change that wants to carry a community identifier on the wire is
working against that contract and needs a decision, not an implementation.

## 2. Change the message vocabulary

All of the following live in `crates/buzz-relay/src/protocol.rs` unless noted.

1. **Add the variant to `ClientMessage`.** It currently has exactly five: `Event`,
   `Req`, `Close`, `Count` (NIP-45) and `Auth` (NIP-42).
2. **Add the parse arm in `ClientMessage::parse`.** The function matches the first
   array element against the literals `EVENT`, `REQ`, `COUNT`, `CLOSE` and `AUTH`;
   anything else falls to a catch-all returning
   `RelayError::InvalidMessage("unknown message type: …")`. That catch-all is why a
   new verb is a *diagnosable* incompatibility rather than a silent one — a client
   speaking it to an undeployed relay gets a `NOTICE` back, because
   `handle_text_message` in `crates/buzz-relay/src/connection.rs` answers a parse
   failure with `RelayMessage::notice`.
3. **Validate in the parser, not the handler,** if the new verb carries a
   subscription id or filters. The existing arms enforce `MAX_SUB_ID_LENGTH` (256)
   and `MAX_FILTERS_PER_REQ` (10) before any handler is reached.
4. **Add the outgoing formatter to `RelayMessage`** if the relay answers with a new
   frame shape. `RelayMessage` is a namespace struct, not a data enum: each of its
   seven functions — `auth_challenge`, `event`, `notice`, `eose`, `ok`, `closed`,
   `count` — returns a JSON string. Keeping the new shape here rather than inlining
   `serde_json::json!` at the emission site is what keeps the emitted vocabulary
   enumerable.
5. **Wire the dispatch arm** in `handle_text_message`
   (`crates/buzz-relay/src/connection.rs`). Decide deliberately whether the new verb
   is awaited inline, as `Auth` and `Close` are, or spawned behind the handler
   semaphore, as `Event`, `Req` and `Count` are.
6. **Decide whether it passes the admission gate.** `enforce_ws_admission` in the
   same file applies the pre-dispatch rate limit to `Event`, `Req` and `Count` only.
   A new verb that does work must be added to it or it is unmetered.
7. **Add unit tests to the `mod tests` block at the bottom of `protocol.rs`.** The
   existing tests are table-driven over both directions: `parse_valid_messages`,
   `parse_invalid_messages` (which pins the unknown-verb rejection),
   `parse_req_too_many_filters_is_rejected`,
   `parse_req_exactly_max_filters_is_accepted`, and `format_relay_messages`.
8. **Update `crates/buzz-ws-client/src/message.rs` in the same change** if the relay
   can now emit the new frame. That crate is the Rust client's independent parser of
   the same vocabulary — see task 4.

## 3. Keep the NIP-11 advertisement honest

The relay's capability document is built in `crates/buzz-relay/src/nip11.rs` and
served two ways from `crates/buzz-relay/src/router.rs`: content-negotiated on
`GET /`, which is also the WebSocket upgrade route, and unconditionally at
`GET /info`.

1. **For a numbered NIP, add the integer to `SUPPORTED_NIPS`** — currently
   `[1, 2, 10, 11, 16, 17, 23, 25, 29, 33, 38, 42, 50, 56]`. Keep it sorted; the
   `supported_nips_are_sorted` test asserts the constant equals its own sorted copy.
2. **For an un-numbered Buzz extension, push a string to `supported_extensions`
   instead.** `RelayInfo::build` seeds that array with `"nip-er"` and pushes
   `"buzz-gif"` when a GIF provider is configured; `nip11_document` pushes
   `"nip-pl"` when push delivery is configured. The string must correspond to a
   draft in `docs/nips/`.
3. **If support is conditional on configuration, follow the NIP-43 pattern rather
   than the static list.** `NIP_RELAY_MEMBERSHIP` is deliberately held out of
   `SUPPORTED_NIPS` and appended inside `RelayInfo::build` only when
   `advertise_nip43` is true, guarded by a `debug_assert` requiring `relay_self` to
   be `Some` because NIP-43 events are verified against the NIP-11 `self` field.
   Three tests pin that shape: `nip43_not_in_static_supported_nips`,
   `build_open_relay_stable_key_advertises_self_but_not_nip43`, and
   `build_nip43_without_self_panics_in_debug`. Advertise capability the relay has,
   not capability the code contains.
4. **If you changed an enforced limit, change the advertised one too — and check
   whether anything binds them.** Only one of the three is bound: `max_limit` reads
   `buzz_db::DEFAULT_MAX_PAGE_LIMIT`, and `relay_limitation`'s doc comment states
   this is so "the advertised ceiling and the enforced one cannot drift". The other
   two are bare literals — `max_filters: Some(10)` and `max_subid_length: Some(256)`
   — while enforcement lives in `protocol.rs`'s private `MAX_FILTERS_PER_REQ` and
   `MAX_SUB_ID_LENGTH`. Nothing references those two constants outside
   `protocol.rs`, so changing one number and not the other compiles, passes, and
   ships a relay that lies about itself. Change both, in the same edit.

   This is not hypothetical. Commit `23f0c26b1` — *fix(relay): align NIP-11
   max_limit with REQ ceiling* — records that the document once advertised
   `max_limit: 10_000` against an effective REQ ceiling of `1_000`, which its own
   message calls "a 10x lie": a client that trusted the advertisement asked for
   10,000 events, "silently receives 1,000", and read the short page as
   exhaustion, dropping up to 9,000 events with no error and no continuation
   signal. That fix is where the `DEFAULT_MAX_PAGE_LIMIT` binding came from. The
   other two limits have not had their equivalent yet.
5. **Do not widen `RelayInfo::build`'s inputs.** The file ends with a const function
   pointer, `_RELAY_INFO_BUILD_STATIC_INPUT_FENCE`, bound to `build`'s exact
   signature; adding a `&Db`, an `&AppState`, a search handle or any other unscoped
   input stops the types matching and fails the file to compile. Pass a pre-derived
   scalar instead, the way `nip11_document` already passes the host-scoped workspace
   icon.
6. **Add the assertion for your NIP** alongside the existing ones —
   `supported_nips_includes_nip23_and_nip33`, `…_nip38`, `…_nip56` — so a later
   refactor of the constant cannot quietly drop it.

## 4. Update every other implementation of the same vocabulary

There is no single shared definition of the wire vocabulary. Five implementations
parse or emit it, and a protocol change is not finished until each has been visited
and each visit has an answer, including "no change needed".

| Implementation | File | Verbs it handles today |
|---|---|---|
| Relay (authoritative) | `crates/buzz-relay/src/protocol.rs` | EVENT, REQ, CLOSE, COUNT, AUTH in; seven out |
| Rust client | `crates/buzz-ws-client/src/message.rs` | EVENT, OK, EOSE, CLOSED, NOTICE, AUTH, COUNT |
| Desktop | `desktop/src/shared/api/relayClientSession.ts` | AUTH, EVENT, OK, EOSE, CLOSED, NOTICE |
| Mobile | `mobile/lib/shared/relay/relay_session.dart` | EVENT, EOSE, CLOSED, OK (AUTH in `relay_socket.dart`) |
| Pairing sidecar | `crates/buzz-pair-relay/src/lib.rs` | REQ, EVENT, CLOSE only — no AUTH, no COUNT |

1. **Start from the relay** and work outward; it is the only one whose behaviour is
   normative.
2. **Treat the pairing sidecar as a separate relay, not a client.**
   `crates/buzz-pair-relay/src/lib.rs` re-implements the protocol from scratch — it
   contains no reference to `buzz_relay` or `ClientMessage` — with its own
   serializers and its own allowlist validators for filters and events. A change to
   the shared vocabulary may or may not apply to it; decide, and say which.
3. **Check the mobile split.** `relay_session.dart` handles four verbs and
   `relay_socket.dart` handles `AUTH`. A new verb has two candidate homes there.
4. **Expect no tool to catch a miss.** Nothing in the repository binds the Rust
   constants to the TypeScript and Dart mirrors: the only cross-reference is a
   hand-written comment in `desktop/src-tauri/src/commands/channels/fetch.rs` reading
   "aligned with `desktop/src/shared/constants/kinds.ts::CHANNEL_MESSAGE_EVENT_KINDS`".
   The repository does build such guards when it chooses to — `buzz-agent`'s
   `model_capabilities.rs` embeds its JSON manifests with `include_str!` and replays
   a locked corpus so "a manifest edit that diverges Rust from the corpus" cannot
   ship green — so the absence here is a gap, not a design.
5. **If the change touches event validity rather than framing,** the shared
   primitives are in `buzz-core`: `verify_event` in
   `crates/buzz-core/src/verification.rs` (which recomputes the event id before
   checking the Schnorr signature, and whose module docs require calling it through
   `tokio::task::spawn_blocking`), and `filters_match` / `filter_match_one` in
   `crates/buzz-core/src/filter.rs`. Note that Buzz defines no `Filter` type of its
   own — it uses `nostr::Filter` and supplies only the matching logic, so filter
   *parsing* changes are upstream changes, not Buzz changes.

## 5. Verify the change

Run these in order. The first step is the one most likely to be skipped and the one
most likely to matter.

1. **Run the protocol unit tests explicitly, because no gate will.**

   ```bash
   cargo test -p buzz-relay --lib protocol::
   cargo test -p buzz-relay --lib nip11::
   ```

   `just test-unit`'s only `buzz-relay` step is
   `cargo nextest run -p buzz-relay --lib` filtered with
   `-E 'test(/^api::admin::/) …'`, and every `package(buzz-relay)` filter in
   `.github/workflows/ci.yml` selects `api::admin::tests`, `api::invites::tests` or
   `handlers::relay_admin::tests`. CI *builds* the rest — `cargo nextest archive …
   -p buzz-relay --lib` — but no run step selects them. The Justfile says why in its
   own comments: "nothing in CI runs `cargo test --workspace`", and "workspace
   membership alone buys clippy/check, not a single executed test". It also records
   that this exact gap once let a red test ship green.
2. **Run the static gate.** `just check` — formatting, clippy across the workspace
   and Tauri, the desktop and web and mobile checks, and the file-size ratchet. It
   executes no Rust tests.
3. **Run the infra-free unit gate.** `just test-unit`.
4. **Run the interop suite explicitly — `just test` does not run it.** With a relay
   up (`./scripts/start-relay-for-tests.sh`, or
   `./scripts/start-isolated-test-relay.sh`):

   ```bash
   cargo test -p buzz-test-client --test e2e_nostr_interop -- --ignored --nocapture
   ```

   The `--ignored` flag is not optional. Every test in
   `crates/buzz-test-client/tests/e2e_nostr_interop.rs` carries `#[ignore]`, and
   `scripts/run-tests.sh` — which is all `just test` and `just test-integration`
   run — invokes `cargo test --test '*'` without `--ignored` anywhere in the file.
   So `just test` compiles this suite and executes none of it. Its tests are named
   for the NIP each exercises: `test_nip50_search_returns_results_and_eose`,
   `test_nip50_search_mixed_filters_rejected`,
   `test_nip10_thread_reply_creates_metadata`, `test_nip17_gift_wrap_accepted`,
   `test_historical_req_dedup_preserves_or_semantics`,
   `test_empty_kinds_returns_zero_events`, and the NIP-DV third-party rejection set.
   `.github/workflows/ci.yml` runs the whole file with that same `--ignored`
   invocation in a Postgres-backed job, so a test added here does reach CI — add one
   if the change has an observable-over-the-wire result.
5. **Read the advertisement back off a running relay.** Start it with `just relay`,
   then:

   ```bash
   curl -s -H 'Accept: application/nostr+json' http://localhost:3000/ | jq '.supported_nips, .supported_extensions, .limitation'
   curl -s http://localhost:3000/info | jq '.supported_nips'
   ```

   Both routes must agree — they are served from the same `nip11_document` builder
   precisely so they cannot drift, and confirming it is how you learn whether your
   edit landed in `build` or only in one caller.
6. **Exercise the verb itself.** A unit test proves the parser accepts a string; only
   a live connection proves the relay answers. Connect a client, send the frame, and
   read the response. `launchpad/docs/corpus/development/debugging.md` covers raising
   the relay's log verbosity and localizing a symptom.
7. **Run the full gate before opening the pull request.** `just ci` — which is
   `check test-unit desktop-test desktop-build desktop-tauri-check
   desktop-tauri-test web-build mobile-test`. It does **not** include `just test`,
   and `just test` in turn does not include the `#[ignore]`d protocol suites, so
   steps 1 and 4 above stay your responsibility even after a green `just ci`.

## 6. Roll back and clean up

1. **Revert the code with `git revert`,** not by hand-editing back. A protocol change
   spans five implementations plus an advertisement, and a partial manual reversion
   reproduces exactly the drift task 4 exists to prevent.
2. **Un-advertise first if the change already shipped.** Removing an entry from
   `SUPPORTED_NIPS` or `supported_extensions` is the urgent half: clients read the
   advertisement to decide which requests to make, so an advertisement that outruns
   the implementation misroutes them rather than merely failing them. Code that
   nothing advertises is inert; an advertisement with no code behind it is not.
3. **Leave the kind registry alone.** If the abandoned work also claimed a kind
   integer in `crates/buzz-core/src/kind.rs`, releasing that integer for reuse is
   #858's subject, not this one. Reverting a verb is cheap; reusing a kind number is
   not.
4. **Reset local relay state if the experiment persisted events.** See
   `launchpad/docs/corpus/development/debugging.md`, which owns the safe reset
   procedure.
5. **Re-run `just check` and step 1 of task 5 after the revert.** A revert is a
   change; the gate that did not run for the change did not run for the revert
   either.

## See also

- `launchpad/docs/corpus/architecture/principles/nostr-first.md` — why "model it as
  an event kind" is the default that task 1 makes you argue against.
- `launchpad/docs/corpus/architecture/flows/http-event-submission.md` — what
  `POST /events` does with a submitted event, for changes that touch the HTTP bridge.
- `launchpad/docs/corpus/architecture/flows/websocket-authentication.md` — the NIP-42
  handshake this procedure's AUTH steps sit inside.
- `launchpad/docs/corpus/development/prerequisites.md` and
  `launchpad/docs/corpus/development/hermit.md` — the toolchain the *Before you
  start* section assumes.
- `launchpad/docs/corpus/development/build.md` — building the workspace, which every
  verification step above depends on.
- `launchpad/docs/corpus/development/debugging.md` — log verbosity, reachability
  checks, and the safe local-state reset that task 6 defers to.
- `CONTRIBUTING.md` §*How to Add a New Event Kind* and §*How to Add a New API
  Endpoint* — the two authoritative procedures task 1 routes to.
- `NOSTR.md` — the third-party-client contract any wire change is measured against.
- `docs/nips/` — the 22 Buzz-defined protocol drafts, and the form a new one takes.

## Boundary

This node does not describe:

- **Adding or changing an event kind integer.** That is a different procedure with a
  different starting file (`crates/buzz-core/src/kind.rs`) and a different failure
  mode: a new kind is invisible to old relays, a new verb is rejected by them. It is
  owned by issue #858's `development/event-kind-changes.md`, which is not merged —
  `launchpad/docs/corpus/development/` on `origin/launchpad` holds only `build.md`,
  `debugging.md`, `hermit.md` and `prerequisites.md`. Until it lands, `CONTRIBUTING.md`
  §*How to Add a New Event Kind* is the authority.
- **Facts about individual NIPs, to be looked up rather than acted on** — what NIP-29
  requires of a group metadata event, what NIP-42's `relay` tag must contain, what
  NIP-50's `search` filter means. Those are reference-shaped. The corpus has no
  `interfaces/` subtree at this revision, so there is no NIP reference shelf to link
  to; the primary sources are the upstream NIPs at
  <https://github.com/nostr-protocol/nips> and, for Buzz-defined extensions,
  `docs/nips/`.
- **How to acquire the underlying skill from scratch.** This assumes a reader who can
  already build and run the relay and read Rust. A newcomer's path through Nostr,
  Buzz's architecture and the Rust workspace is a tutorial, a form the corpus has no
  template for.
- **Why the architecture is nostr-first, or why the relay is the source of truth.**
  Those are explanation-shaped and already have nodes:
  `architecture/principles/nostr-first.md` and
  `architecture/principles/relay-is-source-of-truth.md`.
- **Operating a deployed relay through a protocol change** — rollout ordering across
  a fleet, client-version compatibility windows, or what an operator does when a
  relay advertises a NIP its peers do not. That is operations-shaped and has no owner
  named here.

## Relationships

- `implements: corpus-template-procedure` — this node is a how-to-shaped instance of
  that template, which names "a template instance of a standard" as the `implements`
  type's own worked example and asks instances to declare it once the template is
  merged. It is merged.
- `references: architecture-principles-nostr-first` — task 1 is that principle
  applied as a decision gate; the principle node owns the reasoning.
- `references: architecture-flows-http-event-submission` — the bridge endpoints this
  procedure can change are described end-to-end there.
- `references: architecture-flows-websocket-authentication` — the NIP-42 exchange the
  AUTH-related steps operate inside.
- `references: development-prerequisites` — the toolchain contract *Before you start*
  assumes rather than restates.

Every target declared in this node's front matter was read out of `origin/launchpad`
with `git show`, not out of the authoring worktree. Two edges were considered and deliberately not declared:
`architecture-flows-event-ingestion` resolves but describes what happens *after* a
frame is parsed, which is the kind pipeline rather than the wire surface; and
`development/event-kind-changes.md` is the node this one most needs to point at, and
at the recorded revision it did not exist yet, so the boundary against it was prose
only. It has since landed in this same integration, so the natural edge now resolves;
it is not added here, since wiring it in under the pressure of a pre-merge fix pass
risks the same kind of error this fix pass exists to catch. Adding it belongs to a
dedicated pass across the whole `development`/`governance`/`releases` shelf once all
37 nodes are stable.

## Scope and omissions

**This node covers** how a contributor changes Buzz's wire protocol: deciding whether
a change is a protocol change at all, editing the message vocabulary in
`crates/buzz-relay/src/protocol.rs` and its dispatch in `connection.rs`, keeping the
NIP-11 advertisement in `nip11.rs` truthful and its conditional-advertisement
pattern intact, propagating the change to the four other implementations of the same
vocabulary, verifying it against the gates that exist and the ones that do not, and
rolling it back.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Adding or changing an event kind integer | `#858`, `development/event-kind-changes.md`, not merged; `CONTRIBUTING.md` until it lands |
| Per-NIP reference material (fields, tags, semantics) | upstream <https://github.com/nostr-protocol/nips>; `docs/nips/` for Buzz-defined drafts. No corpus `interfaces/` shelf exists at this revision |
| Why Buzz is nostr-first | `launchpad/docs/corpus/architecture/principles/nostr-first.md` |
| Building and running the workspace | `launchpad/docs/corpus/development/build.md`, `.../prerequisites.md`, `.../hermit.md` |
| Diagnosing a misbehaving local relay, and safe local-state reset | `launchpad/docs/corpus/development/debugging.md` |
| Rolling a protocol change out across deployed relays | no corpus node found to own this |
| The multi-tenant conformance harness and its trace schema | `crates/buzz-conformance/`, `crates/buzz-relay/src/conformance/`; no corpus node |

**Expected but not verified when this node was written:**

- **No step in this procedure was executed.** The commands in task 5 are read out of
  the `Justfile`, `.github/workflows/ci.yml` and `crates/buzz-relay/src/router.rs` at
  the recorded revision; none was run, no relay was started, and no `curl` was
  issued. `launchpad/docs/corpus/templates/procedure.md`'s evidence expectations ask
  for steps cited to having been executed where practical, and this node does not
  meet that bar. Every claim here is a claim about what the repository says it does.
- **The claim that no gate runs `protocol::tests` or `nip11::tests` was established
  by reading filters, not by running them.** It rests on the `-E` expressions in
  `Justfile`'s `test-unit` recipe and every `package(buzz-relay)` filter in
  `.github/workflows/ci.yml`, all of which name `api::admin`, `api::invites` or
  `handlers::relay_admin`. A nextest filter expression was not evaluated to confirm
  it excludes what it appears to exclude, and no CI run was inspected.
- **Whether the unbound `max_filters` and `max_subid_length` literals have actually
  drifted from `protocol.rs`'s constants was checked at this revision only** — both
  read 10 and 256 today. That they agree now is not evidence that anything keeps them
  agreeing; the grep establishing that nothing does is recorded in the provenance
  ledger above.
- **The five client implementations were confirmed to parse the verbs listed, not to
  handle them equivalently.** The table in task 4 was built from the verb literals
  each file branches on. Semantic differences behind those branches — what desktop
  does with a `CLOSED` that mobile does not — were not compared.
- **`crates/buzz-pair-relay/src/lib.rs` was confirmed independent by absence.** It
  contains no `buzz_relay` or `ClientMessage` reference, which establishes that it
  does not consume the relay's message layer; it does not establish that its wire
  behaviour is otherwise identical, and the two were not diffed frame by frame.
- **Git history was consulted, but from a shallow checkout.**
  `git rev-parse --is-shallow-repository` reports `true`, and
  `git log -- crates/buzz-relay/src/protocol.rs` returns two commits. The
  `max_limit` precedent cited in task 3 was found this way and its commit message
  read in full; any earlier rationale for the message vocabulary itself is beyond
  this checkout's reach and was not retrieved from the remote.
- **Whether `standards/naming.md`'s identifier rule and this node's `id` agree was
  not resolved here.** That standard's third MUST prescribes a `corpus-` prefix,
  while the measured practice across the corpus's content nodes — including the
  sibling `development-prerequisites` and `development-hermit` — is
  `<directory>-<stem>`. This node follows the sibling practice. The tension is real
  and belongs to whoever owns the identifier standard; it is named here rather than
  resolved.
