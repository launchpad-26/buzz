---
id: agents-stale-documentation
type: agent
status: draft
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "AGENTS.md's 'Checking whether cited files moved' section documents `git diff --name-only <recorded-sha> -- <the normalized file paths in the ledger>` as the command that establishes whether a claim's cited files changed between the recorded revision and HEAD, and states plainly that only three of six citation shapes -- bare path, file line, file range -- are reachable this way; graph edge, tool result, commit and the two URL forms validate.py recognises are not, and a position suffix (`:line` or `:start-end`) must be stripped before the path is passed or git resolves nothing."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "validate.py's only invocation of git anywhere in the module is `subprocess.run([\"git\", \"rev-parse\", \"--show-toplevel\"], ...)` inside `repo_root()`, used solely to resolve the repository root; no function in the file calls `git diff` or anything comparable, and no function reads a node's recorded-revision evidence entry as distinct from any other entry. The module's only notion of a commit citation is the shape-matching regex `_COMMIT_CITATION_RE = re.compile(r\"^commit\\s+[0-9a-fA-F]{7,40}\\b\")`, and every match is reported on the non-fatal UNVERIFIED channel identically, whether or not it is the entry recording the node's checked revision."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "node.schema.json's `status` enum has exactly five members -- draft, active, deprecated, retired, flagged -- none of which names a stale or evidence-has-drifted state, and no other property anywhere in the schema records a citation's currency or the outcome of any staleness check."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "standards/provenance.md's MUST 3 states that an untouched claim counts as 'known to hold', for the purpose of deciding whether the recorded-revision entry may move, only via full re-verification (route 1) or a clean, normalized `git diff --name-only <recorded-sha> -- <path>` (route 2) -- and route 2 is available only when every citation on that claim is a bare path, file line or file range; a claim carrying even one citation of the other four shapes falls back to route 1 or the entry does not move."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/provenance.md"
  - statement: "standards/provenance.md's own rule is stated entirely in terms of an edit already underway -- MUST 2 binds 'a claim touched by an edit', and MUST 1/3/4 decide whether that same edit may move the recorded-revision entry once the touched claims are handled. No MUST in that document names a trigger for checking a merged node that nobody is currently editing; the document settles what an author owes the ledger mid-edit, not whether or when a node should be looked at again in the first place."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/standards/provenance.md"
    confidence: 0.8
  - statement: "standards/deprecation.md opens by stating 'Nothing on this page is enforced. A retired node with stale inbound edges validates exactly like a healthy one, and no check anywhere distinguishes deprecated from retired,' and its MUST list governs an author's deliberate decision that a node's subject 'is no longer the corpus's answer' (retired) or 'is on its way out' (deprecated) -- a status the author chooses to set, not a drift discovered independently of any edit to that node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/deprecation.md"
  - statement: "standards/deprecation.md's own SHOULD list states, verbatim: 'Re-verify a deprecated node's claims, or say plainly that they were not re-verified. Deprecation is not permission for the ledger to go quietly stale.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/deprecation.md"
  - statement: "templates/policy.md's P1 requires a policy-shaped node to carry six sections -- Scope and authority, MUST, SHOULD, Enforcement, Exceptions and escalation, Scope and omissions -- in that relative order, none reordered among themselves or silently empty, with additional sections permitted between them; P10 requires the H1 to be `# Policy: <subject>` unless a narrower family template states its own convention."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/policy.md"
  - statement: "relationships.schema.json's worked directionality for depends-on is 'source requires target to be true/current for source's own claims to hold'; for references, 'source cites target as supporting context; no ownership or currency dependency implied'; and for implements, its own worked example is 'a template instance of a standard'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "No file named stale.py, stale-documentation.md, or any other stale-prefixed path exists anywhere under launchpad/project-intelligence/corpus/ or launchpad/docs/corpus/ at this node's recorded revision, and git ls-tree of origin/launchpad's corpus tree confirms corpus-agents, corpus-standard-provenance, corpus-standard-deprecation, corpus-template-policy and agents-invariants are the only relevant nodes merged, with no agents/*.md or ingestion/*.md sibling besides agents/invariants.md present."
    entry_class: FACT
    evidence:
      - "find(launchpad/project-intelligence/corpus, launchpad/docs/corpus, iname='*stale*') -> no results"
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, agents/invariants.md, architecture/**, capabilities/**, layers/**, development/**, schema/**, standards/*.md, templates/*.md, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "Issue #556 ('task: extend staleness detection to canonical documentation corpus nodes'), open at this node's authoring time, requires its own automated output to name the affected node's id, the changed source/evidence, and old/new revision information, and requires that unavailable evidence be treated as unestablished rather than fresh; its Impacted components name `launchpad/project-intelligence/corpus/stale.py`, which does not exist yet."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#556 definition of done and impacted components"
  - statement: "Issue #651's own Definition of Done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define an enforcement/checks and exception/escalation process, and link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#651 definition of done"
  - statement: "Parent Feature #620 lists 32 child document tasks under agents/*.md and ingestion/*.md with the stated outcome 'Agents can deterministically navigate, evidence, draft, validate and maintain corpus nodes using documented procedures,' and its Out of scope excludes implementation of the knowledge-crate runtime -- this node's subject is agent-facing policy about when a node counts as stale, not the detection tooling itself."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: depends-on
    target: corpus-standard-provenance
  - type: implements
    target: corpus-template-policy
  - type: references
    target: corpus-standard-deprecation
---

# Policy: staleness in corpus documentation

This node states when a merged `launchpad/docs/corpus/` node counts as **stale-suspect**
-- its cited evidence has drifted since the revision recorded in its ledger, or a claim
resting on evidence nothing can re-check has gone unverified for long enough that
treating it as current would be a guess -- and what MUST happen once that is true.
It exists because the corpus already documents what a recorded revision *means*
(`standards/provenance.md`) and what happens when an author deliberately decides a
node's subject is gone (`standards/deprecation.md`), but nothing says what happens when
**nobody is editing the node at all** and its citations have simply moved underneath it.
That gap is this node's subject.

## Scope and authority

**This node governs** the moment a corpus node's claims can no longer be assumed
current absent a fresh check: what makes a node stale-suspect, who is expected to
notice, what a finding MUST contain, and what MUST NOT be assumed about a claim the
check cannot reach. **It does not govern** what to do once staleness is confirmed and
someone sits down to fix it -- deciding whether the recorded revision moves is
`standards/provenance.md`'s MUST 1-4, and the update procedure itself is
`agents/documentation-update.md`'s territory (issue #646, unmerged at this node's
authoring time, so it is not a valid relationship target here -- see *Scope and
omissions*). It also does not govern automating any of this into a script or CI check:
that is issue #556's, tracked as unbuilt in the evidence ledger above.

**Its authority is derived, not original.** The detection technique this node names as
MUST 1 below is `AGENTS.md`'s own documented command, not invented here. The route
classification of which citation shapes that command can and cannot reach is
`standards/provenance.md`'s MUST 3, reused rather than restated from scratch. Where
this node and either of those disagree, **they win** -- this one has drifted and should
be fixed, the same precedence rule `AGENTS.md` states for itself and every node that
depends on it inherits.

| For | Read |
|---|---|
| The diff technique this node's MUST 1 applies | `launchpad/docs/corpus/AGENTS.md`, "Checking whether cited files moved" |
| What a node's recorded revision means, and when an author mid-edit may move it | `launchpad/docs/corpus/standards/provenance.md` |
| Deliberately deprecating or retiring a node whose subject is gone | `launchpad/docs/corpus/standards/deprecation.md` |
| The general policy-node shape this document instantiates | `launchpad/docs/corpus/templates/policy.md` |
| Updating a node once a stale claim is confirmed | `launchpad/docs/corpus/AGENTS.md`, "Updating a node" (and `agents/documentation-update.md` once merged) |
| Automating detection into tooling/CI | Issue #556 (unbuilt at this writing) |

**Staleness is not deprecation, and not a provenance-entry decision.** A node can be
stale-suspect and still be exactly the right canonical answer to its subject -- it just
needs its claims re-opened, not a lifecycle change. A node can also be freshly
re-verified in every claim and still, correctly, get deprecated because its *subject*
is gone. The two axes are independent: staleness is about whether the ledger's claims
still hold; deprecation/retirement is about whether the subject is still wanted at all.
Conflating them would misdirect exactly the response each situation calls for.

## MUST

| # | Requirement |
|---|---|
| **MUST 1** | Before relying on an existing node's claim as still current -- declaring a new `depends-on`/`references` edge toward it, citing it as supporting evidence in another node, or re-touching it for an unrelated reason -- the relying party MUST run `AGENTS.md`'s check against every file-naming citation (bare path, file line, file range) the relied-on claim carries: `git diff --name-only <recorded-sha> -- <normalized path>`. This is the same command `standards/provenance.md` already documents for a different purpose (deciding whether an in-progress edit may move the recorded revision); this MUST is what names it as an obligation at the *moment of reliance* on an unedited node, not only at the moment of editing it. |
| **MUST 2** | A node is **stale-suspect** the moment either condition holds: (a) MUST 1's check returns nonempty output for any reachable citation on a claim being relied on -- the cited file changed since the recorded revision; or (b) a claim being relied on carries **any** citation of the four shapes the check cannot reach (commit reference, graph edge, tool result, either URL form validate.py recognises) -- alone or alongside file citations -- and nobody has re-opened that specific citation's source since the recorded revision. Condition (b) is deliberately not narrowed to claims resting *entirely* on unreachable shapes: `standards/provenance.md`'s MUST 3 disqualifies its diff route for a claim carrying even one such citation "alone or alongside file citations," and a claim with one clean file citation plus one never-reopened commit reference is exactly the shape that rule was written to catch -- a clean diff on the reachable half says nothing about the other half. Condition (a) is mechanically detectable today, by a human running the command; condition (b) is not detectable by any diff at all -- its currency is simply unknown, and unknown MUST NOT be read as fresh. |
| **MUST 3** | A stale-suspect finding MUST NOT be silently passed over by whoever produces it under MUST 1/2 -- a reviewer reading the node, an author about to cite it, or an agent about to depend on one of its claims. "Silently passed over" means neither of the two acceptable responses in MUST 5 happened: the finder neither fixed it in the same edit nor recorded it anywhere a future reader can find it. |
| **MUST 4** | A recorded stale-suspect finding MUST name: the node's `id`; which citation(s) triggered the finding (the changed path, under MUST 2(a), or the unreachable-shape claim's statement, under MUST 2(b)); the recorded revision the node claims to be checked against; and current `HEAD` at the time of finding. This is the same four-fact shape issue #556's own Definition of Done already requires of its (currently unbuilt) automated equivalent -- a manual finding is held to no lower a bar than the tooling one is designed to meet. |
| **MUST 5** | The two acceptable responses to a stale-suspect finding are: (a) re-verify the affected claim's source at current `HEAD` and correct the node in the same edit, following `standards/provenance.md`'s MUST 1-4 for whether the recorded-revision entry moves; or (b) record the finding per MUST 4, without touching the node's claims, when the finder is not the one positioned to fix it in that session. Finding staleness is not, by itself, authorization to edit the node's claims without following (a)'s re-verification rule -- "detect" and "fix" are not the same act, and MUST 3 is satisfied by either response alone. |
| **MUST 6** | A node's `status` being `deprecated` or `retired` does NOT exempt it from MUST 1-5. `standards/deprecation.md`'s own SHOULD already expects a deprecated node's claims to be re-verified or explicitly marked unre-verified; a retired node's body still makes a claim about what replaced it (or that nothing did), and that claim can go stale exactly like any other. |

## SHOULD

| # | Guidance |
|---|---|
| **SHOULD 1** | Prefer fixing a stale-suspect finding in the same edit (MUST 5(a)) over filing it separately (MUST 5(b)) when the fix is small and the finder already has the context open. A deferred finding costs a second person the same research the finder already did once. |
| **SHOULD 2** | A reviewer who notices a stale-suspect condition while reviewing an unrelated change SHOULD flag or block that specific finding rather than let the unrelated change merge around it silently -- the same posture `ADR-0028` already assigns to review as this corpus's general enforcement mechanism. |
| **SHOULD 3** | When one drifted source is cited by several nodes, file one finding naming every affected node's `id` (per MUST 4) rather than one finding per node -- the underlying drift is a single event, and separate, disconnected findings make it harder for whoever fixes them to see that. |
| **SHOULD 4** | Do not describe a node that passed MUST 1's check as "verified current." A clean, normalized diff on the reachable citations narrows what is unknown; it does not confirm the claim itself still holds, and `standards/provenance.md` makes exactly this distinction for the same command applied to the same citation shapes. |

## Enforcement

**Nothing in this corpus runs any of MUST 1-6 automatically, for any node, ever, as of
this writing.** Verified directly rather than assumed: `validate.py`'s only git
invocation anywhere in the module is `subprocess.run(["git", "rev-parse",
"--show-toplevel"], ...)`, used once, to resolve the repository root. No function in
the file calls `git diff`, and no function distinguishes a node's recorded-revision
evidence entry from any other entry -- every commit-shaped citation is matched by the
same regex and reported on the same non-fatal `UNVERIFIED` channel. `node.schema.json`
has no `status` value, and no other field, that records whether a node has been
checked for drift. A node whose every citation has silently rotted validates exactly as
cleanly as one checked an hour ago.

**What a green `validate.py` run does NOT establish about staleness**, named here
because P6 requires this document to say so about itself:

| Not established | Consequence |
|---|---|
| That a cited file is unchanged since the node's recorded revision | A node citing a file rewritten yesterday validates identically to one citing an untouched file |
| That a claim resting on an unreachable citation shape (commit/graph-edge/tool-result/URL) still holds | Such a claim is never re-checked by any tool, structurally or otherwise |
| That a filed stale-suspect finding (MUST 4) was ever acted on | A node can merge, and merge again, with an open finding against it that nothing surfaces |
| That `deprecated`/`retired` status implies the node was re-verified before that status was set | Schema enum membership is the only check either value receives |

**Enforcement today is entirely review**, the same posture `standards/deprecation.md`
and `templates/policy.md` both already state for their own unenforced halves: MUST 1-6
depend on a human running the command and a human (or reviewer) choosing not to look
away from what it returns. Issue #556 proposes automating MUST 1/2's detection step
into `corpus/stale.py`; until it lands, this section's table is the accurate one.

## Exceptions and escalation

**There is no exemption from MUST 1 when relying on a node's claim.** The command is
one line; skipping it is a choice to rely on a claim without checking it, not an
edge case this document carves out.

**MUST 2(b)'s unreachable-shape claims are not an exception -- they are the harder
case MUST 2 is written to name.** A claim carrying even one commit reference, graph
edge, tool result, or URL citation -- whether or not it also carries file citations --
has no diff to run for that part of it at all. That is not a gap in this policy; it is
`standards/provenance.md`'s own MUST 3 boundary (a route closed by even one such
citation, "alone or alongside file citations"), reused here rather than relitigated,
and the correct response is MUST 5's route (a) (re-verify) precisely because route (b)
(diff) was never available for that part of the claim.

**A disputed call about whether a citation was "the claim being relied on" under
MUST 1** is a judgement, not an exception: the relying party records the tension in
the pull request, and the reviewer decides. A repeated disagreement is filed as an
issue against this node, per this corpus's standing convention for a rule two people
read differently.

**A source that drifts often enough to make MUST 1 impractical on every reliance**
(a frequently-rewritten file cited by many nodes) escalates to parent Feature #620 or
to issue #556 -- batching detection or building tooling is out of this node's scope,
which states the policy, not an efficient implementation of it.

**`status: flagged` is unrelated and is not a substitute for any of this.** It names
`ADR-0029`'s unresolved contradiction between two authoritative sources of the same
claim type -- a different situation from a citation that has simply moved. Do not use
one to signal the other.

## Scope and omissions

**This node covers** what makes a merged corpus node stale-suspect (a diff-detectable
drift in a reachable citation, or an unreachable-shape claim of unknown currency), who
is expected to notice and when, what a recorded finding must contain, what MUST NOT be
assumed about a claim nothing can check, and what a green `validate.py` run does not
establish about any of it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Whether a node's recorded-revision entry moves once a stale-suspect claim is re-verified | `launchpad/docs/corpus/standards/provenance.md` (MUST 1-4) |
| The full step-by-step procedure for updating an existing, already-merged node | `launchpad/docs/corpus/AGENTS.md`, "Updating a node", and `agents/documentation-update.md` (#646, unmerged at this node's authoring time) |
| Deliberately deprecating or retiring a node whose subject is gone | `launchpad/docs/corpus/standards/deprecation.md` |
| Automating MUST 1/2's detection into a script or CI check | Issue #556, `launchpad/project-intelligence/corpus/stale.py` (does not exist at this writing) |
| Generating a corpus-wide index of open stale-suspect findings | Issue #904, `launchpad/docs/corpus/generated/stale-docs.md` (unbuilt) |
| Verifying a citation's line number against the file it names, independent of staleness | Issue #1459 |
| Whether a per-claim (rather than whole-ledger) revision field should be added to the schema, which would let a node be "partly stale" in a way the schema can express | Not filed as a task anywhere found; a reader who wants this should open one rather than infer support for it here |

**This node's own relationships.** Declared: `depends-on: corpus-agents` -- MUST 1's
detection technique is drawn directly from that node's text; if that section's command
changes, this node's own claim about it stops holding. `depends-on:
corpus-standard-provenance` -- this node's route classification in MUST 2 reuses that
node's MUST 3 verbatim rather than re-deriving it; a change there changes what counts
as stale-suspect here. `implements: corpus-template-policy` -- this is a policy-shaped
instance of that template. `references: corpus-standard-deprecation` -- cited as the
neighboring, easily-conflated policy this node explicitly distinguishes itself from
(*Scope and authority* above); no ownership or currency dependency is implied in either
direction, which is exactly what `references`'s directionality states. All four targets
were confirmed present on `origin/launchpad` at this node's recorded revision via
`git ls-tree`, per `AGENTS.md` step 9. **No edge to any other sibling `agents/*.md` or
`ingestion/*.md` task under parent Feature #620**, including `agents/documentation-
update.md` (#646) and `agents/invariants.md`'s other unmerged siblings: `#646` is not
merged at this node's authoring time and is therefore not a valid relationship target,
and `agents-invariants` itself, while merged, states no claim this node's own MUSTs
depend on (its I1-I10 are structural invariants about authoring a node, not about
detecting drift in one already merged) -- so no `references` edge to it is added here
either, per this node's own MUST-that-declared-relationships-must-be-genuine
discipline rather than added for completeness.

**Expected but not verified when this node was written:**

- **No real stale-suspect finding has ever been filed against a merged corpus node
  using this document's MUST 4 shape.** Every MUST above is written against the
  mechanism (`git diff --name-only`, the four unreachable citation shapes) rather than
  against a finding anyone has actually produced and acted on.
- **Whether issue #556, once built, supersedes any part of MUST 1/2 or merely
  automates them, is not decided here.** #556 is a tooling task with no corpus-node
  `id` of its own at this writing, so it cannot be a relationship target regardless of
  how that question resolves.
- **Whether `agents/documentation-update.md` (#646), once merged, declares a
  relationship back toward this node** is that node's own edit to make, not something
  decided here -- it does not exist on `origin/launchpad` at this node's authoring
  time.
- **Whether MUST 1's obligation ("before relying on a node's claim") is proportionate
  in practice, versus so broad it gets skipped in practice, was not tested against a
  real review or a real new-node draft.** It is stated at the scope this document
  judged correct, not one exercised end to end.
