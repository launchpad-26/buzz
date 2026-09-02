# Issue #1006 — task: document interfaces/nostr/nip-01.md

Stated size: no Size line on the issue -> cap: 5 steps
(Set by the task prompt itself, which explicitly caps this plan at 5 steps; this is a
single corpus document, one of Feature #616's document tasks, following the same
one-document-per-task shape already used for #695, #696, #697, #698, #673 and the
corpus standards batch.)

Target file: `launchpad/docs/corpus/interfaces/nostr/nip-01.md`
Node id: `interfaces-nostr-nip-01` (assigned in the task prompt; permanent)
Branch: `task/1006-interfaces-nostr-nip-01`, based on `origin/launchpad`
Worktree: `/home/serina/Launchpad/buzz/__worktrees/task-1006-interfaces-nostr-nip-01`

---

ALREADY TRUE  (verified against git and by running the tools, not against notes)
-------------------------------------------------------------------------------

- `git rev-parse HEAD` in the worktree is `650354eab8d41ab6ce1a71de079a6c6d95c69052`,
  the tip of `origin/launchpad` at the moment the worktree was cut (`git worktree add`
  reported "HEAD is now at 650354eab8"). `git status --porcelain` was clean except this
  plan file and the target document at the point this plan was written.
- `launchpad/docs/corpus/interfaces/nostr/nip-01.md` did not exist before this task:
  `ls launchpad/docs/corpus/interfaces/` returned "No such file or directory" and
  `find launchpad/docs/corpus -name '*.md' -not -path '*/schema/*'` listed no
  `interfaces/` tree at all, only `AGENTS.md`, `README.md`, `architecture/**`,
  `standards/**` and `templates/**`.
- `gh issue view 1006` confirms the issue's own title and body name
  `launchpad/docs/corpus/interfaces/nostr/nip-01.md` and "nip 01" explicitly — the
  standard upstream Nostr NIP-01, not a buzz-specific NIP. No mismatch to block on.
- `launchpad/docs/corpus/templates/interface.md` (id `corpus-template-interface`) is
  merged on `origin/launchpad` and states that a node built from it carries
  `type: interfaces-events` — confirmed against `node.schema.json`'s 13-member enum,
  which has no `interface` value, only the combined `interfaces-events` member.
- `launchpad/docs/corpus/architecture/context/nostr-network.md`
  (id `architecture-context-nostr-network`) is merged on `origin/launchpad` and states
  "every action in Buzz is a Nostr NIP-01 wire-format signed event" — a genuine,
  citable connection, not a decorative one.
- The NIP-01 wire surface is implemented in `crates/buzz-relay/src/protocol.rs`
  (`ClientMessage`/`RelayMessage`), `crates/buzz-relay/src/handlers/{event,req,close}.rs`,
  `crates/buzz-core/src/{verification,filter,event}.rs`, and
  `crates/buzz-relay/src/handlers/ingest.rs` (verification call site, timestamp-drift
  check, duplicate-id idempotency at `was_inserted == false`). `nip11.rs` advertises
  NIP-01 (`SUPPORTED_NIPS` includes `1`) and the same `max_filters`/`max_subid_length`
  limits `protocol.rs` enforces. All read directly before drafting.
- `python3 launchpad/project-intelligence/corpus/validate.py` was not yet run against
  the drafted node when this plan was written; STEP 3 below is where that first
  happens and where any failure gets fixed.

Decisions taken before step 1 (each is a choice this plan makes, not a fact)

**`type: interfaces-events`.** `node.schema.json`'s enum has no bare `interface` value;
`corpus-template-interface` states explicitly that a node built from it carries this
combined value.

**`audiences: agent, developer, reviewer`.** Matches the template's own audiences and
every other corpus governance/interface-adjacent node read during evidence-gathering;
no reason surfaced to narrow or widen it for this node.

**`relationships`: `implements: corpus-template-interface` and
`references: architecture-context-nostr-network`.** Both ids were confirmed present on
`origin/launchpad` (this worktree's own tree, cut directly from it with no intervening
corpus commits) before the front matter was finalized. No edge to any event-kind node,
because none exists in the corpus yet — the template's own guidance treats that as a
follow-up once one merges, not an omission now.

**Scope boundary.** This node documents the NIP-01 message envelope only: `EVENT`,
`REQ`, `CLOSE`, `COUNT` (client to relay) and `EVENT`, `OK`, `EOSE`, `CLOSED`, `NOTICE`
(relay to client), plus the verification and filter-matching rules and the
authentication/size/count limits this relay's deployment layers on top of them. It does
not describe any single event kind's tag/content contract, NIP-42's own `AUTH`
handshake, or NIP-29 channel-scoping semantics — each is named as owned elsewhere in the
node's own *Boundary* and *Scope and omissions* sections.

---

STEP 1  Confirm the issue matches its target, and read the schema/template contract  [independent]  <- RUNS HERE
        Read issue #1006's title and body, confirm it names
        `launchpad/docs/corpus/interfaces/nostr/nip-01.md` and the standard NIP-01, and
        confirm the target file does not already exist. Read `node.schema.json` for the
        `type` enum and required fields, and `templates/interface.md` for the required
        section shape (Interface description, Operations, Contract and stability,
        Boundary, Relationships, Scope and omissions).
        done when: `gh issue view 1006 --repo launchpad-26/buzz --json title,body` names
        `nip-01.md`/NIP-01, and
        `ls launchpad/docs/corpus/interfaces/nostr/nip-01.md` reports "No such file or
        directory" (checked before STEP 2 writes it).

STEP 2  Gather evidence from the relay/core implementation and draft the node  [needs 1]
        Read `protocol.rs`, `handlers/{event,req,close}.rs`,
        `buzz-core/src/{verification,filter,event}.rs`, `handlers/ingest.rs` (the
        verification call site, the timestamp-drift check, the duplicate-id idempotency
        branch), and `nip11.rs` (advertised NIP list and limits). Write the front matter
        (id, type, status: draft, origin, audiences, evidence ledger, relationships) and
        the full body against `templates/interface.md`'s required sections, satisfying
        every bullet of issue #1006's Definition of done: inputs/messages,
        outputs/responses, error/rejection behavior, authentication/authorization,
        versioning/compatibility, ordering/idempotency, a link to the upstream NIP-01
        spec by way of the code that implements it, and one valid plus one failure
        example.
        done when: `launchpad/docs/corpus/interfaces/nostr/nip-01.md` exists with all six
        required template sections present
        (`grep -cE '^## (Operations|Contract and stability|Boundary|Relationships|Scope and omissions)$' launchpad/docs/corpus/interfaces/nostr/nip-01.md`
        returns 5) and at least one fenced example under an `### Examples` or equivalent
        heading (`grep -c 'Failure' launchpad/docs/corpus/interfaces/nostr/nip-01.md`
        returns at least 1).

STEP 3  Validate  [needs 2]
        Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix any FAIL
        line the new node causes and re-run until exit 0. A FAIL not caused by this new
        node is a finding to report, not something to silently patch around.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

STEP 4  Earn the commit gate and commit  [needs 3]
        Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        as the sole command in its own call and confirm it prints `OK`. Only then, in a
        separate call, `git add` this plan and the node and commit with `git commit -s`.
        done when: the unittest run prints `OK`, and `git log -1 --format=%H` on the
        branch names a commit whose tree contains both
        `launchpad/docs/corpus/interfaces/nostr/nip-01.md` and this plan file.

STEP 5  Self-review against the issue's own checklist  [needs 4]
        Re-read the committed diff line by line against issue #1006's Definition of done.
        Confirm every evidence entry actually supports its claim (open the cited source
        again, do not trust the earlier read). Confirm no second hand-authored canonical
        corpus document was created. Confirm `validate.py` still exits 0 after the commit.
        done when: `git show --stat HEAD` names exactly the node and the plan as the only
        non-mechanical files changed, and a second, independent
        `python3 launchpad/project-intelligence/corpus/validate.py` run (after the commit,
        not reused from STEP 3) exits 0.

---

PARALLEL  **Nothing here may run in parallel.** All five steps operate on the same single
          target file and its surrounding evidence gathering; STEP 2's ledger is the
          contract STEP 5 re-checks, and STEP 3/4 are strictly ordered gates. Run in one
          session, in order.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
          (STEP 3 and again in STEP 5). `python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK`
          before the commit gate accepts it (STEP 4). No PR is opened by this plan — the
          task prompt is explicit that this task ends at a commit on the task branch, not
          a pushed or opened pull request; batch integration and cross-model review are
          the batch owner's later pass, the same deferral pattern used by the corpus
          standards batch (#1314, #695-#698).

BUDGET    **STEP 2 is the step most likely to overrun.** Reading five-plus source files
          precisely enough to cite line-level behavior (verification, timestamp drift,
          duplicate-id idempotency, NIP-11 limit advertisement) takes longer than writing
          the front matter once the claims are gathered. STEP 1 is cheap by comparison —
          the issue body and the two governing schema/template files are short.

OPEN      - **Whether a `references` edge to `architecture-flows-websocket-authentication`,
            `architecture-flows-historical-query` or `architecture-flows-live-fanout`
            should also be declared.** This plan chose prose mentions in the node's
            *Boundary* and *Scope and omissions* sections instead, on the reasoning that
            an interface node's job is to say what boundary exists and who owns its
            shape, not to accumulate every architecturally-adjacent edge it could
            plausibly carry — but a reviewer may reasonably want one or more of these as
            typed edges instead of prose.
          - **Whether NIP-45 `COUNT`'s own handler exists and was simply not located**, or
            whether `COUNT` is parsed but never separately handled beyond the envelope.
            This plan's evidence-gathering did not locate a dedicated `handle_count`
            function; the node's *Scope and omissions* records this as unverified rather
            than asserting either way.

LEFT OUT  - **Any single Nostr event kind's tag/content contract.** Owned by a future
            event-kind corpus node (the sibling template to `corpus-template-interface`),
            not this one.
          - **NIP-42's `AUTH` challenge/response handshake mechanics.** Named and
            pointed at `architecture/flows/websocket-authentication.md` rather than
            described here.
          - **NIP-29 channel/group scoping (`h` tags, membership gating).** Named and
            pointed at `architecture/context/nostr-network.md` and this repository's
            root `AGENTS.md` rather than described here.
          - **Any edit to `node.schema.json`, `validate.py`, `AGENTS.md`, or any other
            existing corpus document.** Out of scope by the task prompt.
          - **Opening a pull request.** The task prompt is explicit that this task ends
            at a commit on the task branch.
