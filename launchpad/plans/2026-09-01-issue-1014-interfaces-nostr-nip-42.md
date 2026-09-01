# Issue #1014 — interfaces/nostr/nip-42.md

Stated size: single corpus document, no runtime code change -> cap: 5 steps

ALREADY TRUE: `launchpad/docs/corpus/interfaces/` does not exist on `origin/launchpad`
(`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` lists no
`interfaces/` path), so the target file `launchpad/docs/corpus/interfaces/nostr/nip-42.md`
does not exist yet. `launchpad/docs/corpus/templates/interface.md` (unmerged draft, read
for structure only, not copied verbatim) defines the required sections for an
interface-shaped node and states its `type` is `interfaces-events` — the single enum
value `node.schema.json` reserves for the combined interface/event surface. No
`events-kinds-kind-22242-auth` node (issue #873) exists anywhere in the loaded corpus —
confirmed by grep — so it is not a valid `relationships` target yet.
`launchpad/docs/corpus/architecture/flows/websocket-authentication.md` (id
`architecture-flows-websocket-authentication`, type `architecture`) already exists,
merged, on `origin/launchpad`, and exhaustively documents Buzz's own NIP-42
implementation flow (state machine, ban/allowlist/membership gates, failure table) —
it IS a valid `relationships` target. Upstream NIP-42
(`nostr-protocol/nips@dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/42.md`, fetched this
session) states the two wire messages (`["AUTH","<challenge>"]` relay-to-client,
`["AUTH",<signed-event>]` client-to-relay), the two `OK`/`CLOSED` prefixes
(`auth-required:`, `restricted:`), a ~10-minute timestamp tolerance, and that a relay
"MUST treat all pubkeys as authenticated" across multiple AUTH messages on one
connection — a permissiveness Buzz's own implementation does not follow (its
state-machine allows exactly one successful AUTH per connection).

STEP 1  [independent] ← RUNS HERE Gather evidence beyond what is already recorded above: open `crates/buzz-auth/src/nip42.rs` (module doc + `verify_nip42_event`, already read this session), `crates/buzz-ws-client/src/message.rs` (`RelayMessage::Auth`, `build_auth_event`, already read), `crates/buzz-ws-client/src/connection.rs` (`AUTH_CHALLENGE_TIMEOUT_SECS`/`AUTH_OK_TIMEOUT_SECS`, already read), `crates/buzz-core/src/kind.rs`'s `KIND_AUTH` doc comment (already read), and confirm the `auth-required:`/`restricted:` prefixes actually appear verbatim in `crates/buzz-relay/src/handlers/{auth,event,req,count}.rs` (already grepped, confirmed present). Record any fact still needed for the Contract/versioning section that these sources do not already answer.
done when: every source above has been opened at least once this session and each
substantive claim planned for the node's body has a specific file/line or upstream-URL
citation ready to write into the evidence ledger.

STEP 2  [needs 1] Create `launchpad/docs/corpus/interfaces/nostr/nip-42.md` with
schema-valid front matter (`id: interfaces-nostr-nip-42`, `type: interfaces-events`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`, a
provenance `FACT` citing `commit <HEAD-sha>`, one `relationships` entry —
`references` targeting `architecture-flows-websocket-authentication`, since that node
already exists and resolves) and a body following the `templates/interface.md` shape:
Interface description (the NIP-42 AUTH message-level wire protocol between a Nostr
client and the Buzz relay), an Operations table (the two AUTH wire messages, the
`OK`/`CLOSED` response, each pointing at its defining code symbol or the upstream NIP),
Contract and stability (timestamp tolerance as Buzz's own ±60s stricter-than-spec
choice, the one-AUTH-per-connection restriction as a documented deviation from NIP-42's
stated multi-pubkey permissiveness, the `auth-required:`/`restricted:` prefix contract,
kind 22242 never being stored/broadcast), a Boundary paragraph naming what this node
does not cover (kind 22242's own tag/content wire shape — future `events-kinds-*`
node, issue #873, referenced by filename since it does not resolve yet; the full
Buzz-specific ban/allowlist/membership implementation flow — already owned by
`architecture-flows-websocket-authentication`, linked rather than restated), at least
one valid AUTH example and one failure example (wrong challenge or expired timestamp),
and a Scope-and-omissions section per `AGENTS.md`'s step 8.
done when: the file exists at that path with schema-required front-matter fields
present, a `relationships` entry that resolves against `origin/launchpad`, and every
Definition-of-done bullet from the issue body addressed in the text.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py` from
the repository root. Fix any FAIL line the new node causes (schema violation, broken
citation, unresolved relationship target) and re-run until exit status 0; UNVERIFIED
notices are acceptable. If a FAIL appears that is not caused by this new node, stop and
report it as a separate finding rather than editing around it. [needs 2]
done when: the command exits 0 and its output shows no FAIL line attributable to
`interfaces-nostr-nip-42`.

STEP 4  [needs 3] Run
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own tool call, to earn the pre-commit gate stamp. Confirm it
prints `OK`.
done when: the suite prints `OK` with no errors or failures.

STEP 5  [needs 4] In a separate tool call, stage exactly
`launchpad/docs/corpus/interfaces/nostr/nip-42.md` and this plan file, then
`git commit -s -m "docs(corpus): document NIP-42 interface (#1014)"`. Do not use
`--no-verify`; if the commit is rejected for a missing gate stamp, stop and report it
as a finding rather than routing around it.
done when: `git log -1` shows the new commit with a `Signed-off-by` trailer and
`git status` shows a clean tree relative to the two staged files.

PARALLEL: none — one file, one task, steps are strictly sequential (evidence before
drafting, draft before validation, validation before the gate, gate before commit).

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
must print `OK` before the commit is attempted. Cross-model final review and
`review-adjudicate` are out of scope for this single-document task and are deferred to
whatever batch/PR review process picks this commit up later.

BUDGET: small — one new Markdown file (~150-250 lines), no code changes, evidence
gathering already scoped to five source files already opened this session plus one
upstream NIP fetch already performed.

OPEN: Whether the `relationships` edge to `architecture-flows-websocket-authentication`
should be typed `references` (loose, "cites as supporting context") or `depends-on`
(this node's claims are meaningless without the flow node's implementation detail) is
a judgment call left to the drafting step and reviewable afterward — `references` is
the default chosen here because the interface node's subject (the wire-level AUTH
protocol) is conceptually prior to and independent of any one implementation's
internal state machine, even though in practice only one implementation exists.
Whether a future `events-kinds-kind-22242-auth` node (issue #873) should get
`references` or `depends-on` once merged is explicitly left to that later moment, per
the corpus's own rule that a target must resolve in the branch being merged into.

LEFT OUT: No restatement of `architecture-flows-websocket-authentication`'s
ban/allowlist/membership gate sequence, failure table, or trust-boundary analysis —
linked, not duplicated. No creation or edit of any second hand-authored canonical
corpus document (specifically not a kind-22242 event-kind node — that is issue #873's
task, separately scoped and on an unmerged branch). No change to
`crates/buzz-auth`, `crates/buzz-ws-client`, `crates/buzz-relay`, or any other runtime
code. No attempt to resolve the corpus's own unsettled per-type template standards
(`#1307`-`#1351`) — this node is written directly against `node.schema.json` and the
unmerged `templates/interface.md` draft read for structural guidance only, per
`AGENTS.md`'s "until the standards land" instruction.
