---
id: corpus-standard-provenance
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 919886b4192df6251de50c547548ecae5d85afce."
    entry_class: FACT
    evidence:
      - "commit 919886b4192df6251de50c547548ecae5d85afce"
  - statement: "node.schema.json defines no revision or provenance field anywhere in a node's front matter: the seven top-level properties are id, type, status, origin, audiences, evidence and relationships, and an evidence entry's only fields are statement, entry_class, evidence, confidence and provided_by. No field records which revision a specific claim was checked against."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "AGENTS.md states directly that the evidence array is also the node's provenance ledger and that there is no separate provenance field, so the revision a node was checked against belongs there too, as a commit citation."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Every node in the corpus at this revision records its checked revision the same way: one evidence entry, class FACT, statement 'This node was authored and checked against repository revision <sha>', with a single citation of the form 'commit <sha>'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
      - "launchpad/docs/corpus/README.md"
  - statement: "validate.py recognises a citation of the shape 'commit <7-to-40-hex-chars>' as a commit reference and resolves it against this repository's object store: a commit that exists verifies ok, and one that does not is a hard error. Its contents are still never opened, so the citation establishes that the commit exists, never that it supports the statement above it."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "validate.py applies that same UNVERIFIED treatment to every commit-only FACT in a node identically, so nothing in the checker distinguishes the one evidence entry that records a node's checked revision from any other commit-cited claim in the same ledger; that distinction exists only by the authoring convention this document formalizes."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "AGENTS.md documents 'git cat-file -e <sha>' as the manual command that establishes a commit citation names a real revision in this repository -- run by a human, never by validate.py."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "node.schema.json requires an evidence entry's evidence field, where present, to be a non-empty array of strings, so one claim's citations may mix shapes -- for example a bare path alongside a commit reference -- within a single entry."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "AGENTS.md's documented method for checking whether a ledger's cited files moved is 'git diff --name-only <recorded-sha> -- <normalized paths>', and it states explicitly that only three of six citation shapes -- bare path, file line, file range -- are reachable this way; graph edge, tool result, commit and the two URL forms validate.py recognises are not, and must be normalized (position suffix stripped) before use."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "git_diff_name_only(0ffc1c9e4d875aab667c1ca5955f29984df0b18d, path='launchpad/docs/corpus/AGENTS.md') -> reports the file as changed"
    entry_class: FACT
    evidence:
      - "git_diff_name_only(0ffc1c9e4d875aab667c1ca5955f29984df0b18d, path='launchpad/docs/corpus/AGENTS.md') -> reports the file as changed"
      - "git_diff_name_only(0ffc1c9e4d875aab667c1ca5955f29984df0b18d, path='launchpad/docs/corpus/AGENTS.md:127') -> empty output, exit status 0, for the identical file"
  - statement: "git_diff_name_only(0ffc1c9e4d875aab667c1ca5955f29984df0b18d, path='launchpad/docs/corpus/schema/node.schema.json') -> empty output, confirming a genuinely unchanged file also reports empty, so the previous entry's positive signal is not solely an artifact of the malformed-pathspec failure mode"
    entry_class: FACT
    evidence:
      - "git_diff_name_only(0ffc1c9e4d875aab667c1ca5955f29984df0b18d, path='launchpad/docs/corpus/schema/node.schema.json') -> empty output"
  - statement: "In commit 919886b4192df6251de50c547548ecae5d85afce, this repository's own edit to AGENTS.md left that node's recorded revision unmoved at 0052f5a7820ca4ca261efa233feb8bb53858ade6 after a rebase onto a new base, established by running 'git diff --name-only' for nine normalized file-naming citations against the recorded revision and explicitly excluding the ledger's two non-file citations from that check, rather than either bumping the revision unchecked or re-verifying everything."
    entry_class: FACT
    evidence:
      - "commit 919886b4192df6251de50c547548ecae5d85afce"
  - statement: "Because node.schema.json defines no field that records which revision a specific evidence entry was checked against, the one recorded-revision citation a node carries is necessarily a claim about the state of the entire evidence ledger, not about any single entry in it."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.8
  - statement: "Moving the recorded-revision citation to a later revision without establishing that every claim in the ledger -- not only the ones an edit touched -- holds at that revision would let the untouched claims inherit a currency that was never checked, which is the same overclaiming the knowledge-agent contract's stated guarantee, 'no field asserts more than was established', is written to forbid for any other claim; a corpus evidence ledger is built on the identical FACT/INFERENCE/TEAM_KNOWLEDGE contract that guarantee governs."
    entry_class: INFERENCE
    evidence:
      - "launchpad/project-intelligence/CONTRACT.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.8
  - statement: "Issue #1321 requires this node to decide, not merely describe, whether a node's recorded revision may stay unchanged across an edit that touches other claims, and what an author must do when only some claims in a ledger are re-verified against a new HEAD."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1321 definition of done and task body"
  - statement: "AGENTS.md's 'Updating a node' section states, as of this node's recorded revision, that this exact question is unestablished, that its own four-branch text is a working practice rather than a corpus-wide rule, and that the section defers to this node once it lands."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
relationships:
  - type: references
    target: corpus-agents
---

# Standard: the recorded revision

What the commit citation that records a node's checked revision actually asserts,
whether it may stay put while a node is edited, and what an author owes the ledger
when only some of its claims are re-verified against a new `HEAD`.

This is a policy node. Look up the section you need.

| For | Read |
|---|---|
| Creating, updating and retiring a node; the six citation shapes and what the checker does with each | `launchpad/docs/corpus/AGENTS.md` |
| The front-matter contract -- there is no dedicated `revision` or `provenance` field | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose walkthrough of the front-matter fields | `launchpad/docs/corpus/schema/README.md` |
| What the checker actually enforces, including commit-citation handling | `launchpad/project-intelligence/corpus/validate.py` |
| The FACT/INFERENCE/TEAM_KNOWLEDGE contract this ledger reuses | `launchpad/project-intelligence/CONTRACT.md` |
| How to rank conflicting evidence, and the `confidence` field | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md`, `launchpad/docs/corpus/standards/confidence.md` |

Those files are authoritative. Where this document and any of them disagree, **they
win** -- this one has drifted and should be fixed.

## Scope and authority

**This standard governs** the evidence entry that records the repository revision a
corpus node was authored and checked against -- the entry every existing node writes
as `entry_class: FACT`, `statement: "This node was authored and checked against
repository revision <sha>"`, citing `commit <sha>`. It settles three things: what that
entry means, when it may be moved to a later revision, and what an author must do to
the rest of the ledger when only some of its claims are re-verified.

**Its authority is derived, not original**, in the same sense `confidence.md` states
for its own subject. The structural half is already law: `node.schema.json` defines
the `evidence` array as the node's only provenance mechanism, `validate.py` treats a
commit citation as a recognised-but-unverifiable shape, and neither can be relaxed by
this document. What this document adds is the half no schema can hold: what the
recorded-revision entry is *for*, when moving it is honest, and what a reviewer checks.
That half is enforced by review, not by `validate.py` -- see *What the checks
establish, and what they do not*.

**This document is what `AGENTS.md`'s "Updating a node" section currently defers to.**
As of the revision recorded above, that section states its own four-branch
revision-move text as a *working practice*, not a corpus-wide rule, and names this
node as the place the question is actually settled. This document settles it. It does
not itself edit `AGENTS.md` -- that file belongs to a different task -- and where the
rule stated here differs from `AGENTS.md`'s current text, `AGENTS.md` is the one that
has drifted.

## What the recorded revision means

**It is a whole-ledger claim, not a per-claim one.** The schema gives a node exactly
one place to record a checked revision: the `evidence` array, via a plain commit
citation. There is no field on an individual evidence entry that records the revision
*that entry* was checked against -- confirmed by reading every field
`node.schema.json`'s `evidenceEntry` defines. So when a node's recorded-revision entry
says "checked against revision `X`", the only claim the schema lets it make is about
the ledger as a whole: as of `X`, every claim in this node's evidence array held, as
stated.

**Nothing enforces that claim automatically, ever.** `validate.py` recognises the
shape `commit <sha>` and reports it `UNVERIFIED` -- printed, never fatal, and applied
identically to a node's recorded-revision entry and to any other commit-cited claim in
the same ledger. The checker does not know which entry is "the" recorded revision; it
only exists because every author, so far, has written it first and phrased it the same
way. Establishing that the cited revision even exists is a human running
`git cat-file -e <sha>`; establishing that the *claims* still hold at that revision is
never automated at all.

**One consequence follows directly, and it is the load-bearing point of this
document:** because the entry asserts something about the *whole* ledger, an edit that
re-verifies some claims and leaves others untouched cannot honestly move the entry
forward unless the untouched claims are *also* known to hold at the new revision.
"Known to hold" does not always mean "re-opened and re-read" -- see the next section
for the one narrower, checkable substitute this repository already uses.

## The rule

**MUST 1 -- The recorded-revision entry MUST move to the new `HEAD` only when every
claim in the ledger is known to hold there**, not only the claims an edit set out to
touch. This is the direct consequence of *What the recorded revision means* above:
the entry has no way to say "current for these claims, stale for those."

**MUST 2 -- A claim touched by an edit MUST be re-verified against current `HEAD` in
that same edit**, regardless of whether the recorded-revision entry moves. This is
unconditional and does not wait for MUST 1's broader bar: a claim whose source moved
is not still a `FACT` because it used to be, and leaving the recorded-revision entry in
place is never licence to leave a touched claim's citation stale.

**MUST 3 -- "Known to hold" for an *untouched* claim, for the purpose of MUST 1, is
established by exactly one of two routes, and no other:**

1. **Re-verification.** Open the claim's source at `HEAD` and confirm the statement
   still holds, the same act required for a touched claim under MUST 2.
2. **A clean, normalized `git diff`, and only when every citation on that claim is
   file-naming.** Run `git diff --name-only <recorded-sha> -- <path>` for each citation,
   with any `:line` or `:start-end` position stripped before the path is passed. Empty
   output for every citation on the claim establishes that its cited files did not
   change between the recorded revision and `HEAD` -- and, because the claim itself did
   not change either (it was not touched), checking it then would have been the
   identical act to checking it now, so nothing was skipped. **This route is closed to
   a claim carrying even one citation that is not a bare path, file line or file
   range.** A commit reference, a graph edge, a tool result, or either URL form
   `validate.py` recognises names nothing `git diff` can check, so a claim resting on
   any of those -- alone or alongside file citations -- falls back to route 1 or is left
   unmoved.

**MUST 4 -- If any claim in the ledger satisfies neither route, the recorded-revision
entry MUST NOT move.** It stays at its current value. This is always the safe default:
an unmoved entry never overclaims, it only under-claims currency the ledger may
actually have. Under-claiming costs a future author a repeat check; overclaiming costs
a reader a false `FACT`.

**MUST 5 -- The `id` is never touched by any of this.** Standard practice; restated
here only because moving a revision and renaming an id are unrelated operations that
should never be confused.

**SHOULD 1 -- Prefer re-verification over the diff route when the ledger is short.**
The diff route exists because a large ledger makes opening every source on every edit
expensive, not because it is preferable when it is not. `git diff --name-only` proves
files did not change; it does not prove nobody discovers, on the *next* read, that one
of those files always said something slightly different from what the claim quotes.

**SHOULD 2 -- Record which route MUST 3 used**, briefly, in the commit or PR
description of the edit that moves the revision. The ledger itself has no field for
this (front matter rejects any field the schema does not name), so the record lives
outside the node -- but a reviewer checking MUST 3 later has to reconstruct the same
work from nothing if it is not written down anywhere.

**SHOULD 3 -- Do not chase MUST 1 on an edit that only needs MUST 2.** A one-line fix
to a single claim does not obligate re-verifying an unrelated forty-entry ledger before
the fix can land. Leaving the recorded-revision entry in place (MUST 4) is a normal,
expected outcome of most edits, not a compromise -- see the worked example below,
which is exactly this case.

## Worked example

`AGENTS.md` itself is the nearest instance, and it predates this document: commit
`919886b4192df6251de50c547548ecae5d85afce`, on this same branch, fixed a defect in
that node's own citation-checking prose (a HIGH finding: an earlier version claimed a
clean diff established that "every claim still stood," without excluding the
unreachable citation shapes) and, in the same edit, rebased the file onto a new base
and added a ledger entry.

The recorded revision was **not** moved to the new `HEAD`. It was checked instead: the
commit's own message records running `git diff --name-only` for the ledger's nine
normalized file-naming citations against the recorded revision from the new base, with
the two non-file citations (a commit reference and a tool result) explicitly excluded
from that check rather than silently assumed clean. The diff came back empty for all
nine, so MUST 3's route 2 was satisfied for every claim the route could reach, and the
entry stayed at its original value. Nothing in that commit re-verified the two excluded
claims by opening their sources -- and nothing needed to, because MUST 1 only requires
that *the entry not move* when a claim cannot be shown to hold; it does not require
moving it, and does not require re-verifying a claim nobody's edit needed the entry to
cover.

This is MUST 3 route 2 and MUST 4, applied before this document existed to state them
as a rule. It is also the shape most edits should take, per SHOULD 3: touch what the
edit is actually about, narrow the rest with a diff where the citations allow it, and
leave the recorded revision exactly where an honest check leaves it.

## What the checks establish, and what they do not

**Enforced by nothing:** everything in *The rule* above. `validate.py` treats a
commit citation identically whether or not it is the ledger's recorded-revision entry,
never diffs anything itself, and never compares a node's evidence to git history. A
node that bumps its recorded revision without touching a single other claim validates
exactly as cleanly as one that followed every step of MUST 3. This is not a gap the
tooling is expected to close soon -- `AGENTS.md` makes the identical observation about
commit citations generally, and nothing in this document's own evidence found that
changed.

**What a passing `validate.py` run does establish, incidentally:** that the
recorded-revision entry is shaped like a commit citation at all (`commit
<7-to-40-hex-chars>`), and that it is reported as one `UNVERIFIED` notice among
however many the run prints. A run with zero `UNVERIFIED` notices is not possible for
any node carrying this entry, by construction -- do not read the count as a health
signal for this particular entry.

**Every MUST above is therefore a reviewer's responsibility.** Checking a node whose
diff shows the recorded-revision entry changed:

- confirms every claim in the ledger, not only the ones the diff touches, is covered by
  MUST 3 route 1 or route 2 (MUST 1);
- for any claim covered by route 2, re-runs the normalized `git diff` rather than
  trusting the PR description (SHOULD 2 exists to make this cheap, not to make it
  optional);
- confirms no claim covered by route 2 carries a non-file citation alongside its file
  citations (MUST 3's closing sentence) -- a mixed claim is not eligible, and the
  diff's emptiness on the file half says nothing about the other half;
- confirms every claim an edit actually touched was re-verified at `HEAD`, independent
  of whether the recorded revision moved (MUST 2).

A green `validate.py` run answers none of these, and does not claim to.

## Exceptions and escalation

**There is no exception to MUST 1 or MUST 4.** They follow directly from what the
schema makes the recorded-revision entry capable of asserting (see *What the recorded
revision means*), and no author can widen what a single ledger-wide citation says by
agreeing to widen it. Changing what the entry can express is a schema change, decided
under `launchpad/docs/corpus/schema/COMPATIBILITY.md`, not an exception to this
document.

**MUST 3's two routes are closed, not illustrative.** If neither re-verification nor a
clean, fully-file-naming diff is available for a claim, that claim blocks the entry
from moving (MUST 4) -- it does not fall back to a third, less rigorous check invented
for the occasion. If this repeatedly makes moving a large ledger's recorded revision
impractical, that is a signal about the ledger (candidate for splitting -- see "one
node is one independently maintainable idea" in `AGENTS.md`) or about the schema
(candidate for a per-claim revision field), not a reason to relax this document.
Either path is a proposal to whichever document owns it, not a unilateral exception
here.

**When a reviewer and an author disagree about whether MUST 3 was satisfied**, the
author re-runs the check named in MUST 3 and either produces its output or concedes
the entry does not move. There is nothing to negotiate: the diff either came back
empty for every reachable citation or it did not, and re-verification either happened
or it did not.

**A situation this document does not cover** is an open question for this repository's
usual route: a `type:adr` issue parented to the PRD that raised it, argued there, and
decided by a human. Do not resolve it in a node's body and do not widen this standard
by precedent.

## Scope and omissions

**This document covers** what the recorded-revision entry asserts, when it may move to
a later revision, what an author owes an untouched claim when only some claims in a
ledger are re-verified, and what `validate.py` does and does not establish about any of
it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The other evidence-entry fields, the six citation shapes generally, and how to choose `entry_class` | `launchpad/docs/corpus/AGENTS.md`; the general evidence standard, #1314 |
| The `confidence` field | `launchpad/docs/corpus/standards/confidence.md` |
| Citing a decision record | `launchpad/docs/corpus/standards/decision-references.md` |
| Whether a per-claim revision field should be added to the schema | Not raised as a task anywhere found; a reader who wants this should open one rather than infer support for it here |
| Verifying a citation's line number against the file it names | #1459 |
| Encoding any of this document's rule into `validate.py` itself | Not filed; this document intentionally states a review-enforced convention, the same posture `confidence.md` and `decision-references.md` take for their own review-only rules |

**Why `relationships` names only `corpus-agents`.** `corpus-agents` (`AGENTS.md`) is
the node whose own text explicitly defers to this one, is already merged on the branch
this node targets, and this document's *references* edge records that relationship
directly rather than leaving it implicit. `corpus-standard-confidence` and
`corpus-standard-decision-references` are also merged and on-subject-adjacent, but
neither their text nor this document's argument depends on the other, so an edge to
either would assert a connection this document does not actually use -- checked by
reading both rather than assumed absent. `ls launchpad/docs/corpus/standards/` is the
check for what else exists; run it before treating this list as exhaustive.

**Expected but not verified when this node was written**, per the rule in `AGENTS.md`'s
*Creating a node* step 3:

- **No node's recorded revision has yet been moved forward under this document's rule.**
  The one worked example above (`919886b4192df6251de50c547548ecae5d85afce`) is an
  instance of the entry staying *unmoved*, checked by the diff route. Whether MUST 3
  route 1 (full re-verification) reads as practical on a ledger this corpus's size,
  once a real edit needs it, is untested.
- **Whether a reviewer can actually reconstruct SHOULD 2's record from a typical PR
  description was not tested against a real PR** -- the worked example predates this
  document and was read from its commit message, not from a description written to
  satisfy SHOULD 2.
- **No generated view or tooling was found that reads the recorded-revision entry
  specifically** (as opposed to evidence entries generally), so whether anything
  downstream already assumes a stronger or weaker meaning than *What the recorded
  revision means* states is unknown.
