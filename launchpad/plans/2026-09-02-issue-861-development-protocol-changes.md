# Plan — issue #861: document `development/protocol-changes.md`

Target: `launchpad/docs/corpus/development/protocol-changes.md`
Shape: procedure node, modelled on `launchpad/docs/corpus/templates/procedure.md`
Front matter: `id: development-protocol-changes`, `type: development`,
`status: draft`, `origin: launchpad`
Branch: `task/861-development-protocol-changes`
Recorded revision: `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`

## ALREADY TRUE

- The worktree is on `origin/launchpad` at `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`;
  `git diff --stat origin/launchpad -- launchpad/docs/corpus` is empty, so the
  worktree corpus tree and the merge-target corpus tree are byte-identical.
- **The target file does not exist.** `launchpad/docs/corpus/development/` holds
  exactly four files: `build.md`, `debugging.md`, `hermit.md`, `prerequisites.md`.
  Verified by `ls launchpad/docs/corpus/development/`.
- **There is no `interfaces/` shelf in the corpus**, on `origin/launchpad` or in the
  worktree. `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus/interfaces`
  returns nothing. The dispatch brief's premise that a "large merged `interfaces/nostr/`
  shelf (nip-01, nip-29, nip-42, nip-50)" exists is **false at this revision**, so the
  node cannot link to it and must not claim it exists. The corpus has 229 `.md` files
  across `agents/`, `architecture/`, `capabilities/`, `development/`, `layers/`,
  `schema/`, `standards/`, `templates/` only.
- **There is no merged `development/event-kind-changes.md`** (#858's node), so the
  boundary against it is stated in prose, not as a relationship edge.
- 205 non-schema node ids exist on `origin/launchpad`; 48 carry a `corpus-` prefix.
  The `development/` shelf's own ids are `development-prerequisites`,
  `development-hermit`, `corpus-development-build`, `debugging` — the
  `<directory>-<stem>` form is the majority practice. `standards/naming.md` MUST 3
  (lines 165-175) literally prescribes a `corpus-` prefix. Following the dispatch
  instruction: `development-protocol-changes`, no issue filed, noted in the report.
- `crates/buzz-relay/src/protocol.rs` exists and is the NIP-01 message layer:
  `ClientMessage` (5 verbs), `ClientMessage::parse`, `RelayMessage` (7 formatters),
  with co-located unit tests.
- `crates/buzz-relay/src/nip11.rs` holds `SUPPORTED_NIPS`, `NIP_RELAY_MEMBERSHIP`,
  `RelayInfo::build`, `relay_limitation`, and a compile-time input fence
  `_RELAY_INFO_BUILD_STATIC_INPUT_FENCE`.
- `CONTRIBUTING.md` §"How to Add a New Event Kind" (L415-481) and §"How to Add a New
  API Endpoint" (L485-515) are the two existing authoritative procedures. The first is
  #858's subject; the second is adjacent to, but narrower than, this node.

## STEP 1 — finish evidence gathering

Confirm the remaining coordinates by opening the files: `connection.rs` dispatch,
`router.rs` route table, `api/bridge.rs`, the `buzz-ws-client` crate, the
`crates/buzz-test-client/tests/e2e_nostr_interop.rs` test names, the client-side
kind mirrors (`desktop/src/shared/constants/kinds.ts`,
`mobile/lib/shared/relay/nostr_models.dart`), and the `Justfile` recipes that gate
a protocol change. Record anything expected but not verifiable.

**done-when:** every claim the draft will make has a file I opened at this revision.

## STEP 2 — resolve relationship targets against `origin/launchpad`

For each candidate id, run `git show origin/launchpad:<path>` and read its `id`.
Candidates: `architecture-principles-nostr-first`,
`architecture-flows-http-event-submission`, `architecture-flows-event-ingestion`,
`architecture-flows-websocket-authentication`, `corpus-template-procedure`,
`development-prerequisites`, `development-hermit`.

**done-when:** every declared `relationships[].target` is a string I read out of a
file on `origin/launchpad`, not out of my worktree and not from memory.

## STEP 3 — draft the node

Procedure/how-to shape per `templates/procedure.md` §Required sections: one `#`
heading; Overview; Before you start; ordered task sequences (classify the change,
change the surface, keep the NIP-11 advertisement honest, verify, roll back);
See also; Boundary; Relationships; Scope and omissions. Provenance ledger: first
FACT records the revision; every substantive claim gets an entry; INFERENCE carries
`confidence`; TEAM_KNOWLEDGE carries `provided_by` and no `confidence`.
Spell "front matter" as two words. Under 1000 lines.

**done-when:** the body satisfies every DoD bullet including the procedure tail
(goal, prerequisites, scope; ordered executable project-specific steps; success
verification AND rollback; authoritative commands/config linked, not generic advice;
explicit scope-and-omissions).

## STEP 4 — validate and re-verify BEFORE committing

Run `python3 launchpad/project-intelligence/corpus/validate.py` (expect PASS), then
re-read the draft against the DoD line by line and re-open every citation.
`git commit --amend` is blocked by `git-safety.sh`, so this must be complete first.

**done-when:** validate.py exits 0 and every citation has been re-opened.

## STEP 5 — commit gate, then commit

Run the unittest suite bare and unpiped as its own sole command:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Confirm OK. Then in a separate call `git add` the document and this plan and
`git commit -s`. No `--no-verify`. Stop at the commit — no push, no PR.

**done-when:** one signed commit exists on `task/861-development-protocol-changes`.

## PARALLEL

Steps 1 and 2 are independent and were started together. Steps 3-5 are strictly
sequential.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` → exit 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  → OK, run bare and unpiped as its own command.
- Every `relationships[].target` resolves on `origin/launchpad`.
- Exactly one level-1 heading; document under 1000 lines.

## BUDGET

Five steps, one document, one plan, one commit. No code changes, no second corpus
document, no generated output.

## OPEN

- Whether `crates/buzz-relay/src/protocol.rs`'s `MAX_FILTERS_PER_REQ` / `MAX_SUB_ID_LENGTH`
  and `nip11.rs`'s `max_filters: Some(10)` / `max_subid_length: Some(256)` should be
  bound by a shared constant the way `max_limit` is bound to
  `buzz_db::DEFAULT_MAX_PAGE_LIMIT`. Grep shows no cross-reference and no test binding
  them. This is a real drift risk; it is **documented as a step in the node**, not
  fixed here, and is reported as a candidate issue rather than filed.
- Whether any automated check keeps the Rust kind registry in sync with the desktop
  TS and mobile Dart mirrors. To be answered in STEP 1; if none exists, the node says
  so as a gap rather than implying one.

## LEFT OUT

- Adding a new event **kind integer** — that is #858's `development/event-kind-changes.md`,
  which is not merged. Stated as a boundary, not folded in.
- Any change to product behaviour, relay code, or the NIP-11 document itself.
- Creating a second hand-authored corpus node, or an `interfaces/` shelf.
- Filing issues for findings (report them instead, per the dispatch instruction).
