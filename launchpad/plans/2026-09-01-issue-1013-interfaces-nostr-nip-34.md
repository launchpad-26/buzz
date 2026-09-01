Issue: #1013 — task: document interfaces/nostr/nip-34.md (parent Feature #616)
Stated size: issue carries no explicit Size line -> cap: 5 steps

ALREADY TRUE

- The target file `launchpad/docs/corpus/interfaces/nostr/nip-34.md` does not
  exist yet on `origin/launchpad` (nor anywhere in this worktree) — confirmed
  by `ls launchpad/docs/corpus/interfaces/` returning "No such file or
  directory" at HEAD `650354eab8d41ab6ce1a71de079a6c6d95c69052`.
- `node.schema.json`'s `type` enum has 13 members and the interface-shaped one
  is the single hyphenated value `interfaces-events` (not a separate
  `interface`/`interfaces` value) — confirmed by reading
  `launchpad/docs/corpus/schema/node.schema.json` directly.
- A corpus template for interface-shaped nodes already exists at
  `launchpad/docs/corpus/templates/interface.md` (`corpus-template-interface`,
  `type: governance`) and prescribes required sections: Interface
  description, Operations, Contract and stability, Boundary, Relationships,
  Scope and omissions. This plan builds the node to that template's shape.
- Sibling node `interfaces-http-git` (issue #980, "document
  interfaces/http/git.md") is **not merged** — `gh issue view 980` shows
  `state: OPEN` — so it cannot be a `relationships` target yet. Per the
  issue's own instruction and the template's own relationship rules, this
  node will mention it by filename/prose only, not as a schema
  `relationships` edge.
- Buzz genuinely implements a substantial slice of NIP-34's own event model,
  not merely the git-smart-HTTP transport layer, verified by direct code
  read:
  - `crates/buzz-core/src/kind.rs:604-623` defines all the NIP-34 kinds Buzz
    uses: `30617` (repo announcement), `30618` (repo state),
    `1617` (patch), `1618`/`1619` (PR/PR-update), `1621` (issue),
    `1630-1633` (status open/merged/closed/draft).
  - `crates/buzz-sdk/src/builders.rs:838-1600` has typed builder functions
    for each of those kinds (`build_repo_announcement`, `build_git_patch`,
    a PR/PR-update pair, `build_git_issue`, a status builder), each with its
    own field validation — not just a passthrough wire encoder.
  - `crates/buzz-relay/src/api/git/manifest_event.rs` builds and signs the
    `kind:30618` ref-state event from the object-store manifest on every
    push, including the NIP-34-mandated `"ref: <head>"` HEAD-tag wrapping
    (asserted by its own test `head_tag_always_wraps_with_ref_prefix`).
  - `crates/buzz-relay/src/handlers/side_effects.rs:2595-2670`
    (`handle_git_repo_announcement`) reserves the repo name and seeds the
    manifest pointer as a stateful side effect of storing a `kind:30617`
    event — this is server-side event-driven behavior, not transport.
  - `crates/buzz-relay/src/handlers/ingest.rs:529,533-540` gates git kinds
    through the relay's scope system (`Scope::ReposWrite` for
    announcement/state, `Scope::MessagesWrite` for patch/PR/issue/status)
    the same way every other Nostr write is authorized — confirming these
    are first-class relay-side event kinds, not opaque payloads.
  - `crates/buzz-cli/src/lib.rs:1149-1730` exposes `repos`, `patches`, `pr`,
    `issues` subcommands that build/sign/submit these exact kinds.
  This rules out "transport-only" as this node's finding; the actual finding
  (Step 3) is narrower: which parts of NIP-34 Buzz implements vs. defers.
- `docs/nips/NIP-GS.md` and `crates/git-sign-nostr` implement NIP-GS
  (commit/tag signing with Nostr keys, "adds commit-level signatures to
  NIP-34 workflows" per `NIP-GS.md:844`) and `crates/git-credential-nostr`
  implements NIP-98 (HTTP auth) for git's credential helper — both are
  related to, but distinct protocols from, NIP-34's own event contract, and
  belong in this node's Boundary section rather than its Operations table.

STEP 1 — Confirm remaining evidence gaps before drafting [independent]

Read the handful of sources not yet opened that the Operations/Contract
sections need: `crates/buzz-sdk/src/builders.rs` lines 1080-1600 (issue,
status, PR, PR-update builders' exact field validation), the OK-message
error-prefix convention already found in `ingest.rs` (`invalid:`,
`restricted:`, `error:`, `duplicate:`), and `crates/buzz-core/src/git_perms.rs`
(`ProtectionRule.require_patch`, kind:30617 `buzz-protect` tag) for the
patch-workflow authorization story.

done when: every Operations-table row and every Contract-and-stability claim
in the drafted node (Step 2) cites a source that was actually opened in this
step or in the research already logged under ALREADY TRUE — no row cites a
file this plan has not read.

STEP 2 — Draft the node [needs 1]  <- RUNS HERE

Write `launchpad/docs/corpus/interfaces/nostr/nip-34.md` following
`templates/interface.md`'s required sections (Interface description,
Operations, Contract and stability, Boundary, Relationships, Scope and
omissions), front matter `type: interfaces-events`, `status: draft`,
`origin: launchpad`, evidence entries classed FACT/INFERENCE/TEAM_KNOWLEDGE
per `node.schema.json`'s `allOf` rules. No `relationships` entry targeting
`interfaces-http-git` (unresolvable, per ALREADY TRUE) — prose-mention
`interfaces/http/git.md` by filename instead. Include at least one valid
example (a successful `kind:30617` announcement → `kind:30618` state
transition) and one failure example (an OK-accepted event whose side effect
still fails, e.g. a colliding repo name, so the client sees `accepted: true`
with no git-hosting name reserved — the seam found in `ingest.rs:3200-3211`
and `side_effects.rs`'s `ReserveOutcome` collision path).

done when: the file exists at the target path, is valid YAML+Markdown, and
`python3 launchpad/project-intelligence/corpus/validate.py` reports no FAIL
line attributable to this new node (pre-existing FAILs, if any, are reported
as a separate finding per the task instructions, not silently absorbed here).

STEP 3 — State the transport-vs-event-model finding explicitly [needs 2]

Add (or confirm already present in Step 2's draft) an explicit paragraph
answering the issue's own implicit question: does Buzz implement NIP-34's
event model, or only the git-smart-HTTP transport? Ground the answer in Step
1/2's citations rather than assuming either extreme — the accurate finding is
that Buzz implements a real subset of NIP-34's event-level contract
(repo announcement/state, patch, PR/PR-update, issue, the four status kinds,
with relay-side side effects keyed off them) while some of NIP-34's
optional/extended surface (e.g. the `maintainers` tag, full third-party
interop testing) is not emitted or is out of this node's verified scope —
name the specific gaps found, don't round to "yes" or "no."

done when: the node's own prose states this finding in one identifiable
paragraph or section, each sub-claim in it citing a Step 1/2 source.

STEP 4 — Validate and run the corpus test suite [needs 2]

Run `python3 launchpad/project-intelligence/corpus/validate.py` (must exit 0)
and `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` (must print `OK`) as two separate commands.

done when: both commands are run and both pass (validate.py exit 0, unittest
prints `OK`); any FAIL/failure not caused by this node's own new file is
recorded as a fresh finding rather than fixed silently.

STEP 5 — Self-review against the issue's Definition of Done [needs 4]

Re-read the drafted node against every checklist line in issue #1013's body
(schema-valid front matter, one independently maintainable node, evidence
traceability, links without duplication, inputs/outputs/errors,
auth/versioning/ordering, spec link, valid+failure examples). Confirm no
second hand-authored canonical corpus document was created.

done when: every DoD checklist line has been checked against the actual diff
text, and the commit (git add + `git commit -s`) referencing this file and
this plan has been made — or, if the commit gate rejects it, that rejection
is reported verbatim as a finding rather than routed around.

PARALLEL

Steps 1 and 2-5 are effectively sequential (each STEP's "needs" chain covers
this) — there is no independent parallel branch in a single-file, single-node
task this size. Step 1's sub-reads (builders.rs, git_perms.rs, ingest.rs OK
messages) may happen in any order relative to each other.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
  (Step 4).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK` (Step 4), run as its own isolated command
  before any commit, per the task's explicit instruction.
- The pre-commit/gate stamp check on `git commit -s` (Step 5) — if it rejects
  the commit, that is reported as a finding, not bypassed with `--no-verify`
  or a hand-authored stamp file.

BUDGET

One drafting pass (Step 2), one validation pass (Step 4), one self-review
pass (Step 5). Two additional read-only research passes are folded into Step
1 rather than split into their own steps, since they gate nothing but the
citations Step 2 needs. No rework loop is budgeted beyond fixing whatever
`validate.py` or the unittest run reports — if either fails for a reason
unrelated to this node, that is reported as a finding (task instructions),
not iterated on inside this plan.

OPEN

- Whether Buzz's `maintainers`-tag gap (noted in `docs/nips/NIP-MP.md:217`:
  "Buzz's own announcement builder does not emit it today") is a genuine
  product gap worth a follow-up issue, or an intentional scope decision — not
  decided here; this plan only requires that the node's Step 3 finding name
  the gap, not resolve whether it should be closed.
- Whether the `accepted: true` + failed-side-effect seam identified in Step 2
  (a colliding/invalid repo name is stored as a valid Nostr event but its
  git-hosting reservation silently fails server-side) warrants its own bug
  issue — this plan documents it as a Contract-and-stability finding in the
  corpus node; filing a separate issue is left to whoever reads that finding
  next, consistent with "blockers get fixed, everything else gets a ticket."

LEFT OUT

- Rewriting or duplicating `interfaces/http/git.md` (issue #980, unmerged) —
  out of scope per the task's own explicit instruction; this node
  prose-mentions it by filename only.
- A field-by-field, parameter-by-parameter catalogue of every builder's
  validation rule in `buzz-sdk/src/builders.rs` — the interface template's
  own *Boundary* section explicitly excludes reference-depth cataloguing
  (`#1346`/`#1532`'s territory); this node names the operations and cites the
  builders, it does not restate every validation branch.
- Deciding whether `implements` or `references` is the right relationship
  type for this node's optional self-link to `corpus-template-interface` —
  the template itself says both are schema-legal and unsettled; this plan
  will pick `references` toward any `interfaces-events` neighbors that do
  resolve and skip the optional self-link entirely rather than adjudicate an
  unrelated open question.
- Filing the `maintainers`-tag or accepted/side-effect-failure gaps as new
  GitHub issues — named in OPEN above, left to a human/later pass per the
  task's own scope (this is a documentation task, not an implementation or
  triage task).
