---
id: agents-documentation-update
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
  - statement: "AGENTS.md's 'Updating a node' section lists six steps: confirm the change belongs in this node (else it is a new node); re-verify the claims being touched against sources at current HEAD; update the ledger in the same edit as the body; decide whether the recorded revision moves; leave the id alone; run the check."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "AGENTS.md's own 'Updating a node' section prefaces its revision-move guidance with: what the recorded revision means beyond the DoD-required minimum is 'working practice, not settled policy', and states directly that '#1321's [is] to settle' whether a recorded revision may stay put across an edit and what an author owes an untouched claim, adding 'Until it does, this document works to the rule below ... rather than dressing it up as a corpus-wide standard.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Issue #1321 (launchpad-26/buzz), the issue AGENTS.md names as the one that settles the revision-move question, is closed."
    entry_class: FACT
    evidence:
      - "gh_issue_view(repo='launchpad-26/buzz', issue=1321, fields=['state','closed']) -> {\"closed\": true, \"state\": \"CLOSED\"}"
  - statement: "standards/provenance.md states plainly that it is 'what AGENTS.md's \"Updating a node\" section currently defers to', that 'this document settles it', and that 'where the rule stated here differs from AGENTS.md's current text, AGENTS.md is the one that has drifted' -- so AGENTS.md's own unsettled-caveat prose is now stale relative to a later-merged, more authoritative source, exactly the situation AGENTS.md's own precedence rule (\"if this file and any of those disagree, they win\") anticipates for itself."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/provenance.md"
  - statement: "standards/provenance.md's MUST 1 requires the recorded-revision entry to move to a new HEAD only when every claim in the ledger -- not only the ones an edit touched -- is known to hold there; MUST 2 requires a claim an edit touches to be re-verified at current HEAD in that same edit regardless of whether the recorded-revision entry moves; MUST 3 allows an untouched claim to count as 'known to hold' only via full re-verification (route 1) or, when every one of that claim's citations is a bare path, file line or file range, a clean `git diff --name-only <recorded-sha> -- <normalized path>` for each one (route 2); MUST 4 requires the entry to stay unmoved if any claim satisfies neither route."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/provenance.md"
  - statement: "standards/provenance.md's MUST 3 route 2 is closed to a claim carrying even one citation that is a commit reference, a graph edge, a tool result, or either URL form validate.py recognises -- such a claim falls back to full re-verification (route 1) or the recorded revision does not move for it (MUST 4)."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/provenance.md"
  - statement: "validate.py's commit-citation pattern is `^commit\\s+[0-9a-fA-F]{7,40}\\b`, matched by shape only -- the checker never runs git against it and reports every match on the non-fatal UNVERIFIED channel, identically whether or not the entry is a node's recorded-revision entry."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "AGENTS.md's own documented command for establishing that a cited commit exists in this repository is `git cat-file -e <sha>`, run by a human -- validate.py never runs it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "templates/procedure.md requires a how-to-shaped corpus node to carry, at minimum: an Overview stating the task in one line; an optional Before you start section for prerequisites; one numbered task sequence per logical goal, action-verb steps capped near 8-10 and split into sub-tasks or a separate node if it grows past that; a See also section; a Boundary statement naming what the node does not cover (not reference, not tutorial, not concept/explanation, plus node-specific exclusions); a Relationships section; and a Scope and omissions section per AGENTS.md's own step 8."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "templates/procedure.md's own type-note states that the schema's `type` enum names the corpus surface a node documents, not its documentation form, and that a how-to-shaped node takes whichever `type` its subject matter's surface already calls for."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "The sibling node agents-invariants (launchpad/docs/corpus/agents/invariants.md, merged) carries type: agent on the stated reasoning that its subject is the same corpus surface AGENTS.md itself documents, distinct from the governance type used for the standards/ and templates/ subtrees -- the precedent this node's own type: agent choice follows, since this node's subject (updating an existing corpus node) is likewise the agents/ surface, not a standards- or template-track document."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/agents/invariants.md"
    confidence: 0.8
  - statement: "node.schema.json's evidenceEntry requires a FACT or INFERENCE entry to carry a non-empty evidence array, requires INFERENCE additionally to carry confidence, forbids confidence and provided_by on FACT, and requires TEAM_KNOWLEDGE to carry provided_by while forbidding confidence -- enforced by its allOf conditionals on entry_class."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "relationships.schema.json's implements entry states its own worked example as 'a template instance of a standard', and its references entry's directionality is 'source cites target as supporting context; no ownership or currency dependency implied'; depends-on's directionality is 'source requires target to be true/current for source's own claims to hold'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "Parent Feature #620 lists 32 child document tasks under agents/*.md and ingestion/*.md, with the stated outcome that 'Agents can deterministically navigate, evidence, draft, validate and maintain corpus nodes using documented procedures', and its Out of scope excludes implementation of the knowledge-crate runtime."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body"
  - statement: "Issue #646's own Definition of Done requires a how-to-shaped document: states goal, prerequisites and allowed environment/scope; provides ordered, executable, project-specific steps; defines success verification and rollback/cleanup where relevant; links authoritative commands/config rather than giving generic advice -- in addition to the standards-track boilerplate (schema-valid front matter, one independently maintainable idea, honest evidence classification, validate.py passing) shared with every other task under Feature #620."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#646 definition of done"
  - statement: "Sibling issue #645 is titled 'task: document agents/documentation-creation.md' and sibling issue #647 is titled 'task: document agents/documentation-validation.md'; neither issue's body content was read, and neither node exists on origin/launchpad at this node's authoring time, so this node's Boundary section names both by title only rather than by their (unwritten, unmerged) content."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#645, launchpad-26/buzz#647 (issue titles only)"
relationships:
  - type: implements
    target: corpus-template-procedure
  - type: depends-on
    target: corpus-agents
  - type: depends-on
    target: corpus-standard-provenance
  - type: references
    target: agents-invariants
---

# Updating an existing corpus node: how-to

Walks an agent (or a reviewer checking one) through updating an existing,
already-merged `launchpad/docs/corpus/` node in place -- re-verifying the claims an
edit touches, keeping the evidence ledger in sync with the body, and deciding
whether the node's recorded revision moves. Perform this when a change belongs in
a node that already exists, not when you are authoring a brand-new one.

## Before you start

- The node you intend to update already exists and is merged on the branch you are
  targeting (`origin/launchpad`, unless told otherwise) -- if it does not exist yet,
  see *See also*.
- You have a specific change in mind: a claim to correct, a new claim to add, a
  relationship to add or retarget, or similar -- not merely a feeling that the node
  "could be better."
- You have read `launchpad/docs/corpus/AGENTS.md` in full at least once; this guide
  assumes its vocabulary (front matter, evidence ledger, recorded revision) and does
  not redefine any of it.

## Update the node

1. **Confirm the change belongs in this node.** Ask whether you are adding detail
   about the idea this node already documents, or describing a second, independent
   idea. The second case is a new node, not an update -- stop here and see *See
   also* for the node-creation guide instead. (AGENTS.md's "Updating a node" step 1.)
2. **Re-verify every claim the edit touches, against its source at current `HEAD`
   (`git rev-parse HEAD`).** A claim whose source moved is not still a `FACT`
   because it used to be -- reopen the source, not the old evidence entry.
   (AGENTS.md step 2; `standards/provenance.md` MUST 2, which applies unconditionally
   regardless of what step 4 below decides about the recorded revision.)
3. **Update the evidence ledger in the same edit as the body.** Add an entry for
   every new claim; remove or rewrite the entry for any claim the edit deletes or
   changes. A ledger entry with no matching claim, or a claim with no matching
   entry, is the failure mode this step exists to prevent. (AGENTS.md step 3.)
4. **Decide whether the recorded-revision entry moves, using `standards/provenance.md`'s
   settled rule -- not the caveat still printed in `AGENTS.md`'s own "Updating a
   node" section.** That caveat names `#1321` as the issue that would settle this;
   `#1321` is closed, and `standards/provenance.md` is its output, stating of itself
   that it is what `AGENTS.md` "currently defers to" and that "where the rule stated
   here differs from AGENTS.md's current text, AGENTS.md is the one that has
   drifted." Apply `standards/provenance.md`'s MUST 1/3/4 directly:
   - Every claim in the ledger -- not only the ones this edit touched -- known to
     hold at `HEAD` → move the recorded-revision entry.
   - Some claims known to hold, and the rest independently confirmed to hold too →
     move it. Confirm, do not assume.
   - Nothing beyond the touched claims re-verified, and no independent confirmation
     for the rest → leave it.
   - For any *untouched* claim, "known to hold" is established only by
     re-verification (opening the source again) or, when every one of that claim's
     citations is a bare path, file line, or file range, a clean
     `git diff --name-only <recorded-sha> -- <normalized-path>` for each citation on
     it, once any `:line` or `:start-end` suffix is stripped before the path is
     passed. A claim carrying even one citation that is a commit reference, a graph
     edge, a tool result, or either URL form `validate.py` recognises cannot use the
     diff route at all for that claim.
   - If any claim in the ledger satisfies neither route, **the recorded-revision
     entry does not move.** This is always the safe default -- an unmoved entry
     under-claims currency the ledger may actually have; a moved one, done wrong,
     over-claims a check that was never made.
5. **Leave the `id` alone.** Always, with no exception. (AGENTS.md step 5;
   `agents-invariants` I3.)
6. **Run the deterministic check** from the repository root:

   ```bash
   python3 launchpad/project-intelligence/corpus/validate.py
   ```

   Exit status 0 is a pass; a non-zero exit names the node and the problem. This
   guide stops at running the command -- interpreting what it prints, and fixing
   what it names, is `agents/documentation-validation.md`'s territory (see
   *Boundary*).

## Success verification and rollback

**Verification.** `validate.py` exits 0, and a `git diff` of the node's front
matter shows the evidence ledger and the body's claims moved together -- no new
claim without a ledger entry, no ledger entry left behind by a deleted claim. If
the recorded-revision entry moved, step 4's chosen route (full re-verification, or
the diff route with its file-naming-only restriction) is what justified the move;
record which route was used in the commit or PR description, since the ledger
itself has no field for this and a reviewer otherwise has to redo the same
research from nothing.

**Rollback.** A corpus node lives in ordinary version control -- `git checkout --
<path>` (or reverting the commit, once merged) restores the node's prior text
exactly. There is no separate corpus-side rollback mechanism: `validate.py` checks
the tree it is pointed at, and reverting the file is sufficient to return that tree
to its previous validated state.

## See also

- `launchpad/docs/corpus/AGENTS.md` -- the full authoring/updating/retiring
  procedure this guide's numbered steps are drawn from, including creating a node
  and retiring one, both out of scope here.
- `launchpad/docs/corpus/standards/provenance.md` -- the settled rule behind step 4
  above; read it in full before applying MUST 3's diff route to a real edit.
- `launchpad/docs/corpus/agents/invariants.md` -- the citable I1-I10 invariants an
  update must not violate (id permanence, relationship resolution, schema shape,
  evidence honesty, retirement-by-status-change).
- `launchpad/docs/corpus/templates/procedure.md` -- the how-to template this node is
  built from, including the reference/tutorial/concept-explanation boundary
  restated below.

## Boundary

This node does not describe:

- **How to create a brand-new corpus node.** That is `agents/documentation-creation.md`
  (issue #645, not merged at this node's authoring time) -- named here by title
  only, since neither its body nor a merged version exists to link into or
  duplicate. This guide's *Before you start* section assumes the node you are
  editing already exists; if it does not, stop and use that guide instead.
- **How to run or interpret `validate.py`'s output.** That is
  `agents/documentation-validation.md` (issue #647, not merged at this node's
  authoring time) -- named here by title only, for the same reason as above. This
  guide's step 6 links the bare command as its final action and stops there.
- **Facts to look up rather than actions to perform** -- the front-matter contract's
  exact fields and enums, the six citation shapes, and what each one's checker
  verdict is. See `AGENTS.md` and `node.schema.json` for that; this guide instructs
  the update sequence, not the reference material behind it.
- **Acquiring the underlying skill from scratch, for a newcomer.** This guide is for
  a reader who already knows what a corpus node and an evidence ledger are (per
  *Before you start*) and wants to perform one task correctly -- not a tutorial. No
  corpus template for the tutorial form exists as of this node's authoring time.
- **Why the recorded-revision rule is shaped the way it is**, beyond citing it. That
  reasoning belongs to `standards/provenance.md` itself; this guide applies the
  rule, it does not re-argue it.

## Relationships

- **implements** `corpus-template-procedure` -- this node is a how-to-shaped
  instance of that template.
- **depends-on** `corpus-agents` -- this node's steps 1, 2, 3, 5 and 6 are drawn
  directly from `AGENTS.md`'s "Updating a node" section; if that section's
  procedure changes, this node's own claims about it stop holding.
- **depends-on** `corpus-standard-provenance` -- step 4 above is built entirely on
  that node's settled MUST 1/3/4 rule; if that rule changes, step 4 must change
  with it.
- **references** `agents-invariants` -- supporting context on the invariants an
  update must not violate (I3's id permanence, I5's relationship-target rule, I7's
  evidence-honesty rule), with no ownership or currency dependency implied in
  either direction.

## Scope and omissions

**This node covers** the ordered steps for updating an existing, already-merged
corpus node: confirming the change belongs there, re-verifying touched claims,
keeping the ledger and body in sync, deciding whether the recorded revision moves
(per `standards/provenance.md`'s settled rule rather than `AGENTS.md`'s own
now-stale unsettled caveat), leaving the `id` alone, and running the deterministic
check -- plus success verification and rollback for the update as a whole.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Creating a brand-new corpus node | `agents/documentation-creation.md` (#645, unmerged) |
| Running or interpreting `validate.py`'s findings | `agents/documentation-validation.md` (#647, unmerged) |
| Retiring a node (status change, not deletion) | `launchpad/docs/corpus/AGENTS.md`, "Retiring a node" |
| The front-matter contract itself, and the six citation shapes | `launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/schema/node.schema.json` |
| The full text and reasoning of the revision-move rule this guide applies | `launchpad/docs/corpus/standards/provenance.md` |
| The citable invariants an update must not violate | `launchpad/docs/corpus/agents/invariants.md` |
| Whether `AGENTS.md`'s own "Updating a node" prose will be edited to drop its now-stale `#1321` caveat | Not filed as a task anywhere found at this node's authoring time; a reader who wants this should open one rather than infer it is already tracked |

**Expected but not verified when this node was written:**

- **No real edit has yet been performed using step 4's revision-move decision as
  written here.** `standards/provenance.md`'s own worked example is a case of the
  entry staying unmoved (MUST 4); whether an edit that *does* satisfy MUST 1 and
  moves the entry forward reads as straightforward in practice, using this guide's
  wording, is untested.
- **Whether the other 30 sibling `agents/*.md` and `ingestion/*.md` tasks under
  Feature #620, once merged, will want a `references` or `depends-on` edge to this
  node** was not decided here -- none of them exist on `origin/launchpad` at this
  node's authoring time, so none is a valid relationship target (`AGENTS.md`'s own
  step 9).
- **Whether `agents/documentation-creation.md` (#645) and
  `agents/documentation-validation.md` (#647), once merged, draw their own
  boundaries against this node identically to how this node draws its boundary
  against their titles** was not checked -- neither had merged as of this writing,
  and only their issue titles, not their bodies, were read.
