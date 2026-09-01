Issue #873 — task: document events/kinds/kind-22242-auth.md
Stated size: no `Size` label on #873 (labels: type:task, area:docs, by:agent)  →  cap: 5 steps (set by this task's own dispatch brief: "cap at 5 steps — this is a small single-document task")

ALREADY TRUE  (verified against git, not notes)
  Worktree `__worktrees/task-873-events-kinds-kind-22242-auth` is on branch
    `task/873-events-kinds-kind-22242-auth`, based on `origin/launchpad`,
    HEAD `a8b5021efb92264e724366d08b47b2a3839eb90a`, and the only change in the tree is the
    new, untracked `launchpad/docs/corpus/events/` directory (`git status --porcelain`).
  `launchpad/docs/corpus/events/` did NOT exist before this task — both `ls` and `find`
    returned "No such file or directory" against it on this base.
  `launchpad/docs/corpus/templates/event-kind.md` exists and is the template to write
    against; its own front matter states a real event-kind instance "would most plausibly
    take node.schema.json's interfaces-events type."
  `crates/buzz-core/src/kind.rs:77` defines `KIND_AUTH: u32 = 22242`, documented at line 76
    as "NIP-42 auth event -- never stored (carries bearer tokens)"; it is absent from
    `ALL_KINDS` (the registry array spanning lines 635-766).
  Four independent rejection sites already exist in code: `crates/buzz-relay/src/handlers/
    event.rs:670-678` and `crates/buzz-relay/src/handlers/ingest.rs:2182-2186` refuse a
    kind-22242 *submission*; `crates/buzz-db/src/store/event.rs:304-306` and `crates/
    buzz-db/src/runtime/mod.rs:924-926` refuse to *store* one (defense in depth).
  `crates/buzz-test-client/tests/e2e_relay.rs:844-871` has an `#[ignore]`d conformance test,
    `test_auth_event_kind_rejected`, requiring a live relay to run.
  Fetching `nostr-protocol/nips` at the commit this repo already pins elsewhere
    (`dabfcb2aaecf4fa374eda8b1232ab303a03f60ba`) confirms NIP-42 requires `kind: 22242` with
    `relay`+`challenge` tags and NIP-01 defines the ephemeral range as `20000 <= n < 30000` —
    both match `kind.rs`'s own constants with no drift found.
  Running `python3 launchpad/project-intelligence/corpus/validate.py` against this exact
    baseline with the new file temporarily moved aside already FAILs with 21 pre-existing
    errors, all in unrelated `architecture-*`/`corpus-template-*` nodes — reproduced by
    moving the new file back in and confirming the same 21 lines still appear unchanged.

STEP 1  [independent]  Gather evidence: read the issue body, `launchpad/docs/corpus/AGENTS.md`,
        `node.schema.json`, and `templates/event-kind.md`; locate kind 22242 across
        `buzz-core`, `buzz-auth`, `buzz-relay`, `buzz-db`, `buzz-ws-client`, `buzz-test-client`,
        and `docs/nips/NIP-AA.md`; fetch NIP-01 and NIP-42 at the pinned commit to check
        `kind.rs`'s ephemeral classification and the AUTH event's tag/OK-response
        requirements against the primary source rather than memory. ← RUNS HERE
        done when: `kind.rs`'s `is_ephemeral`/`EPHEMERAL_KIND_MIN`/`MAX` values, all four
        AUTH-rejection call sites, and the pinned NIP-01/NIP-42 text are each recorded with
        a `file:line` or commit-pinned URL citation usable in the evidence ledger.

STEP 2  [needs 1]  Write `launchpad/docs/corpus/events/kinds/kind-22242-auth.md`: schema-valid
        front matter (`id: events-kinds-kind-22242-auth`, `type: interfaces-events`,
        `status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer,
        operator]`, an `evidence` ledger citing STEP 1's findings, no `relationships` — no
        merged sibling node shares this subject) and a body covering the template's nine
        required sections (kind identity; referenced NIP; range/delivery classification;
        tag shape; content semantics; access control and storage model naming producers,
        consumers, authorization, persistence, fanout, search and audit treatment; worked
        example; versioning; relationships) plus a Scope and omissions section.
        done when: the file exists at that path with `id`/`type`/`status`/`origin`/
        `audiences`/`evidence` present and `relationships` absent from its front matter, and
        every one of #873's event-kind-specific DoD bullets (kind number/name and
        persistence class; required/optional tags and validation rules; producers/
        consumers/authorization/persistence/fanout/search/audit; NIP/spec plus handler/
        registry/conformance links) has a corresponding `##`-level section in the body.

STEP 3  [needs 2]  Run `python3 launchpad/project-intelligence/corpus/validate.py`; confirm
        it reports zero `FAIL` lines naming `events-kinds-kind-22242-auth`, tolerating only
        the 21 pre-existing baseline errors recorded in ALREADY TRUE, which belong to other,
        unrelated corpus nodes this task's own DoD forbids touching ("no ... second
        hand-authored canonical corpus document", "no broad while-here cleanup").
        done when: the validator's stderr, grepped for `events-kinds-kind-22242-auth`, shows
        only `UNVERIFIED` lines and no `FAIL` line; and re-running the identical command
        with the new file temporarily removed reproduces the same 21 pre-existing `FAIL`
        lines byte-for-byte, proving this node added none of them.

STEP 4  [needs 3]  Self-review the diff line by line against #873's own Definition-of-done
        checklist, re-opening every cited file/line to confirm it still supports the
        evidence-ledger claim it was cited for, and confirm no second hand-authored
        canonical document was created.
        done when: a written pass maps every DoD bullet to a body section or evidence
        entry; every FACT/INFERENCE citation is re-opened in this step (not merely reused
        from STEP 1) and still matches what the body says; and `git status --porcelain`
        under `launchpad/docs/corpus/` shows exactly one new `.md` file.

STEP 5  [needs 4]  Run the corpus unittest suite as the sole command in its own tool call to
        earn the verification stamp, confirm it prints `OK`, then commit the plan and the
        document together with `git commit -s`.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
        -p "test_*.py"` prints `OK` as the immediately-prior command with nothing else run
        alongside it, and `git log -1 --format=%B` on the resulting commit shows a
        `Signed-off-by:` trailer and references `#873`.

PARALLEL  None. STEP 2 writes the one target file; STEP 3 and STEP 4 both re-read and
          depend on that exact file; nothing here is dispatchable as a separate subagent.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit clean of any
          `FAIL` line naming this node's own id (STEP 3). `review-adjudicate` and the
          cross-model final review pass are deferred to the batch owner's later review per
          this task's own dispatch instructions — not run here. No PR is opened by this task
          (explicit instruction); the deliverable is a commit on the task branch only.

BUDGET    STEP 2 (the body) and STEP 3 (proving the pre-existing validator noise is not
          mine) are where the risk concentrates. The corpus has grown well past the four
          governance nodes the event-kind template's own evidence ledger described when it
          was written, so distinguishing "pre-existing corpus drift" from "an error this
          task introduced" needed an actual before/after `validate.py` comparison, not an
          assumption that a clean baseline exists.

OPEN      Whether the 21 pre-existing `validate.py` errors (in
          `architecture-containers-postgres`, `architecture-context-human-user`,
          `architecture-flows-event-ingestion`, `architecture-flows-workflow-execution`,
          `architecture-principles-community-is-security-boundary`,
          `corpus-template-data-entity`, `corpus-template-datastore`,
          `corpus-template-invariant`) should block this task's own gate. Planned handling:
          they do not — they reproduce identically with this node entirely absent from the
          tree, none names `events-kinds-kind-22242-auth`, and fixing them would mean
          materially editing other hand-authored canonical corpus documents, which #873's
          own Out of scope list forbids. Reported here rather than silently worked around;
          a separate task should own the fix.
          Whether NIP-AA's own recommended ±120-second freshness window for its credential
          (distinct from this kind's own ±60-second `TIMESTAMP_TOLERANCE_SECS` check) is
          enforced anywhere in code — not traced in this task; named as a gap in the
          document's own "Expected but not verified" section rather than guessed at either
          way.

LEFT OUT  Any `relationships` edge — the only nodes merged under `launchpad/docs/corpus`
          today besides governance/template/standards files are `architecture-*` and
          `corpus-template-*` nodes, none of which shares this node's subject (one specific
          Nostr event kind), so no edge would be substantive rather than a citation
          duplicate. A NIP-98 (kind 27235) sibling node, a NIP-OA/NIP-AA capability node,
          and a `buzz-cli`/`buzz-ws-client` interface node for the consumer-facing "how do I
          authenticate" operation — all named as future work in the document's own Scope
          and omissions table, none authored here. Fixing any of the 21 pre-existing corpus
          validation errors found in unrelated files. Editing
          `launchpad/docs/corpus/templates/event-kind.md`, even though this instance is the
          first to surface that its own evidence ledger's "exactly four validated content
          nodes" claim has since drifted — that template is not this task's document to
          edit.
