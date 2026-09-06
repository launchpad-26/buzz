---
name: corpus-maintain
description: Given a commit range, PR, or change set, run impact and staleness tooling first, then update only the corpus nodes it names, preserving ids and applying the recorded-revision rule. Use when a repository change may have invalidated corpus nodes. Not for authoring a new node (corpus-author), reviewing a drafted node (corpus-review), or planning documents (corpus-plan).
allowed-tools:
  - Read
  - Bash
  - Edit
---

# corpus-maintain — update the nodes a change actually touched, provenance intact

Consumes four already-built, already-tested tools —
`launchpad/project-intelligence/corpus/impact.py` (issue #635),
`launchpad/project-intelligence/corpus/stale.py` (issue #556),
`launchpad/project-intelligence/corpus/regenerate.py` (issue #559), and
`launchpad/project-intelligence/corpus/validate.py` — and orchestrates them
into one procedure for keeping `launchpad/docs/corpus/` current after a real
change lands. This skill does not decide what the corpus needs to say next;
it decides which existing nodes a given change touches, whether their cited
sources actually moved, and what provenance rule applies to each. **It never
judges whether a node's claims are still true.** Only a human re-reading the
cited source does that — this skill narrows which nodes need that read, it
does not do the reading for you.

This is a maintenance skill, not an authoring one: it edits existing nodes
that `impact.py` names as impacted. It does not create new files. A changed
path that matches no citation at all is a coverage gap, reported as a
finding for a human to route to `corpus-author` under a new issue — see
Phase 2. `Write` is deliberately absent from `allowed-tools` above for this
reason: nothing this skill does legitimately requires creating a file, and
its absence is the mechanical backstop for the "never create a node for a
coverage gap" rule in Never below.

## Phase 1 — accept a change set, run the tooling first

Three inputs are accepted, and each reduces to exactly one `<base>` /
`<head>` pair before any tool runs:

1. **A commit range**, given directly as two revisions (`<rev1>..<rev2>` or
   two named refs). Use them verbatim as `--base <rev1> --head <rev2>` —
   the caller already named exact endpoints, so no further resolution
   happens.
2. **A PR**, given by number. Resolve with:
   ```
   gh pr view <n> --json baseRefOid,headRefOid
   ```
   then compute `git merge-base <baseRefOid> <headRefOid>` and use **that**
   merge-base commit as `--base`, with `headRefOid` as `--head`. Do not pass
   `baseRefOid` straight through. `impact.py`'s own diff is a deliberate,
   literal two-dot `git diff <base> <head>` (tree-to-tree) — its docstring
   states this explicitly and puts the choice of merge-base resolution on
   the caller. Reviewing a PR twice, once mid-review and once after
   unrelated commits land on its base branch, must report the same impacted
   set for the same head commit — not a growing one that includes base's
   unrelated churn. Computing the merge-base first gives that stability, and
   matches this repository's own diff convention elsewhere (`git diff
   origin/main...HEAD` in the pre-push lanes) rather than inventing a
   different one here. This settles the two-dot-versus-three-dot question
   this skill leaves no room to re-decide per run.
3. **A change set**, named any other way a human describes a body of work.
   It is only usable if it can be stated as exactly two revisions — the
   state before and the state after. **If it cannot be reduced to two
   revisions, refuse and say so.** Do not guess at endpoints from a
   description; a change set with no clear "before" is not this skill's
   job to infer.

With one `<base>`/`<head>` pair settled, run both tools **before opening any
node** — never hand-pick nodes from intuition:

```
python3 launchpad/project-intelligence/corpus/impact.py --base <base> --head <head>
python3 launchpad/project-intelligence/corpus/stale.py --head <head>
python3 launchpad/project-intelligence/corpus/regenerate.py --base <base> --head <head> --format text
```

`impact.py` answers "which nodes cite something this change touched, directly
or by a `depends-on`/`part-of`/`supersedes` relationship edge" (`references`
and `implements` do not propagate — a human decision, not this skill's own).
`stale.py` answers a different question — "for every node, independent of
this change, has anything it cites moved since the node's own recorded
revision" — and is run alongside `impact.py`, not instead of it: a node
`impact.py` did not name can still turn up `STALE` against its own recorded
revision, and a node `impact.py` did name is not automatically stale (its
citation could be unrelated to what actually changed in the cited file).
`regenerate.py` joins both of those (neither re-implemented) and adds the one
thing neither alone answers: for every node `impact.py` named, whether EVERY
claim in its full evidence ledger — not only the claims this change's diff
touched — is route-2 clean, producing a per-node `may-move` /
`must-not-move (MUST 4)` disposition plus, on `must-not-move`, the exact
blocking claim numbers. All three reports feed Phase 2's decision; none
replaces another.

**A large impacted set is a normal result to triage, never a signal the tool
misfired.** `crates/buzz-core/src/kind.rs` is cited by 62 of 205 nodes;
`crates/buzz-relay/src/router.rs` by 37 (#635's own measured figures). A
one-line change to a hot file can legitimately name 30% of the corpus as
impacted. Do not narrow that list by taste — triage every node it names.

### Worked example (run 2026-09-03, `feature/534-corpus-maintenance-updates` at `6f9f4cce39`)

```
python3 launchpad/project-intelligence/corpus/impact.py --base 067c085f37~1 --head 067c085f37
```
exits 0 and writes JSON with three top-level keys — `impacted_nodes`,
`coverage_gaps`, `unreadable_nodes` (not two; `unreadable_nodes` lists any
node `validate.load_nodes` could not schema-validate, empty in this run).
`impacted_nodes` is one flat list; a **direct** hit carries `changed_path`,
`evidence_entry_index` and `statement`, a **propagated** hit carries those
three as `null` with `reason` explaining the edge — there is no separate
`direct`/`propagated` split at the top level. Real rows from this run:

```json
{
  "changed_path": "crates/buzz-core/src/kind.rs",
  "evidence_entry_index": 11,
  "node_id": "architecture-containers-agent-runtime",
  "reason": "cites crates/buzz-core/src/kind.rs",
  "statement": "By default the harness subscribes to stream message kinds 9 (KIND_STREAM_MESSAGE), 46010 (KIND_WORKFLOW_APPROVAL_REQUESTED) and 40007 (KIND_STREAM_REMINDER); forum event kinds (45001-45003) require opting in with --kinds and disabling the mention filter."
}
```
```json
{
  "changed_path": null,
  "evidence_entry_index": null,
  "node_id": "layers-observability-audit-log",
  "reason": "propagated via 'depends-on' relationship with architecture-principles-community-is-security-boundary",
  "statement": null
}
```

This run named 68 unique impacted node ids (252 raw rows before de-dup) and
2 coverage-gap paths. `architecture-containers-agent-runtime` is a real node:
`git grep -l "architecture-containers-agent-runtime" launchpad/docs/corpus/`
resolves to its canonical file,
`launchpad/docs/corpus/architecture/containers/agent-runtime.md`, plus two
inbound citers.

`stale.py --head HEAD` against the same worktree exits 0 and prints one line
per `stale`/`unestablished` finding — a `fresh` verdict emits **no line of
its own**, only a count in the final summary — ending in exactly one summary
line:
```
STALE  architecture-containers-agent-runtime: crates/buzz-acp/src/config.rs -- file changed between the recorded revision and head (recorded a44cf52fc740ebebbdd671427480d14f0bce0115, current f177f4909d55ad48a36e86a682cd5be4f006f0fe)
...
SUMMARY  205 node(s): 195 stale, 6 fresh, 4 unestablished
```

Stop here. Do not edit a node yet — that is Phase 2 onward.

## Phase 2 — what may change, and what a coverage gap is

**Only nodes `impact.py` named change.** Nothing else. This includes
"mechanical generated views" per the issue's own wording — but **no such
views exist in this repository today**: `git ls-files launchpad/docs/corpus/
| grep "/generated/"` returns nothing, no `generated/` directory exists
anywhere under the corpus, and `validate.py` rejects a non-Markdown artefact
on sight even inside one, because no generator exists yet to prove it is
reproducible rather than hand-edited. That clause is inert for now — read it
as future scope, not a step this skill performs. Feature #621 ("corpus
indexes completeness and traceability are mechanically visible") owns that
surface when it lands.

**Stable node ids are preserved.** Not this skill's own rule —
`standards/provenance.md` MUST 5 ("The `id` is never touched by any of
this") and `AGENTS.md`'s "Updating a node" step 5 ("Leave the `id` alone.
Always.") already say it. The one exception is retirement or supersession,
and even then the file is never deleted: `AGENTS.md`'s "Retiring a node"
routes through a `status` change plus, where something replaces the node, a
`supersedes` edge from the replacement — never a deletion, because a
deleted node breaks every inbound `relationships[].target` that still names
its id.

**A coverage gap is reported, never filled.** `impact.py`'s `coverage_gaps`
channel (`{paths, redacted_count, by_area}`) lists every changed path that
matched no citation at all — #635's own plan measures this at roughly 90%
of a real range's changed paths, because most source files are not cited by
any node. Writing a new node for a gap is `corpus-author`'s job, under a new
issue. This skill's correct output for a gap is a named finding in the
review summary (Phase 4) — not a draft, not a stub, not a new file.

**A non-empty `unreadable_nodes` list is always its own finding, never
silently absorbed.** `impact.py` drops a schema-invalid node from
`valid_nodes` before building the citation index, so that node is excluded
from both direct matching and relationship propagation entirely — its
impact status is *unknowable*, not "not impacted," and any path it alone
used to cite will misleadingly surface as an ordinary coverage gap with
nothing pointing at the real cause. Treat `unreadable_nodes` the same way
as `coverage_gaps`: report each entry (its label/path plus the schema
error) as a named finding in Phase 4's review summary, distinct from
coverage gaps, every time the list is non-empty. Do not fix the node
yourself — that is a corpus-authoring edit, out of this skill's scope —
and do not let a broken node go unreported just because it produced no
coverage-gap or impacted-node row.

## Phase 3 — provenance, and the MUST 4 default

DoD bullet 4 says "Updated provenance records the source revision/evidence
that triggered the update." Read naively, that means bumping every touched
node's recorded-revision entry to the triggering commit. It does not.
`standards/provenance.md` states five MUSTs; this phase applies all five,
by number, to every node this skill edits:

- **MUST 1** — the recorded-revision entry moves to the new `HEAD` only when
  *every* claim in the ledger is known to hold there, not only the claims
  this edit touched.
- **MUST 2** — unconditional, independent of MUST 1: a claim this edit
  actually touches is re-verified against current `HEAD` in the same edit.
  A citation whose source moved is not still a `FACT` because it used to
  be, whether or not the recorded-revision entry moves.
- **MUST 3** — "known to hold" for an *untouched* claim is established by
  exactly one of two routes: **route 1**, re-verification (open the source
  at `HEAD`, confirm the statement still holds); or **route 2**, a clean,
  normalized `git diff --name-only <recorded-sha> -- <path>` for every
  citation on that claim, and *only* when every citation on that claim is
  file-naming. **Route 2 is closed to any claim carrying even one
  non-file citation** — a commit reference, a graph edge, a tool result, or
  either URL form `validate.py` recognises. A claim mixing a file citation
  with one of those falls back to route 1 or is left unmoved.
- **MUST 4 — the default outcome, not a compromise.** If any claim in the
  ledger satisfies neither route, the recorded-revision entry **MUST NOT
  move**. Staying put is the normal, expected result of most edits
  (`provenance.md` SHOULD 3: a one-line fix does not oblige re-verifying an
  unrelated forty-entry ledger before it can land). An unmoved entry only
  under-claims currency the ledger may actually have; a moved one that
  should not have moved overclaims a `FACT` a reader will trust.
- **MUST 5** — the `id` is never touched by any of this (already stated in
  Phase 2; restated here because moving a revision and renaming an id are
  unrelated operations that should never be confused).

**Do not hand-compute route 2 by running `git diff --name-only` per citation
yourself.** `regenerate.py` (Phase 1) already does exactly this — per
evidence-entry route-2 classification against the node's own recorded
revision, normalization trap included — and rolls every claim in a node's
full ledger up into the same `may-move` / `must-not-move (MUST 4)`
disposition MUST 1 and MUST 4 describe above, naming the blocking claim
numbers on `must-not-move`. Read its report for the node instead of
re-deriving MUST 3 route 2 claim-by-claim; only route 1 (opening the source
and re-reading it) is left for a human or agent under this skill to do by
hand.

**`stale.py`'s `unestablished` verdict means "route 2 could not run," never
"verified fresh."** Phase 1's worked example showed a summary dominated by
`unestablished` findings — under a shallow checkout (this repository's own
history is frequently shallow; CI checks out at depth 1) `stale.py` cannot
resolve a node's recorded revision or diff against it at all, and says so
via `unestablished` rather than guessing. Read an `unestablished` finding
the same way as MUST 3's "neither route available" case: it does not
satisfy route 2, so that claim falls back to route 1 (manual
re-verification) or is left unmoved under MUST 4. Never treat
`unestablished` as equivalent to `fresh` or as license to leave a node's
provenance untouched *because it checked out clean* — it did not check out
at all.

**The normalization trap.** `git diff --name-only <sha> -- <path>` for a
citation carrying a line or range suffix — `path/to/file.md:127` — matches
nothing and **exits 0 with empty output**, indistinguishable from a
genuinely unchanged file. Strip the `:line` or `:start-end` suffix before
the path reaches `git`, every time, or route 2 silently reports "unchanged"
for a citation it never actually checked.

**Where the triggering revision goes.** Front matter has no field for it —
`node.schema.json` "rejects any field the schema does not name," per
`provenance.md` SHOULD 2 — so it does not go in the node at all. It goes in
the commit or PR description of the edit that touches the node, alongside
which MUST 3 route was used for each claim that stayed unmoved. That
description is the only place a future reviewer can reconstruct the check
without redoing it.

## Phase 4 — the checks it runs, and the review summary

Run both, from the repository root, after every node edit:

```
python3 launchpad/project-intelligence/corpus/validate.py
python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"
```

(`just corpus-validate` is equivalent to the first command.)

**Read the final `PASS` line and the exit code — never the `UNVERIFIED`
count alone.** A healthy corpus prints hundreds of `UNVERIFIED` notices and
still exits 0: `PASS  corpus validation found no errors; 593 item(s)
reported unverified` is the current baseline (measured 2026-09-03 against
`origin/launchpad`). Compare the `UNVERIFIED` count before and after this
skill's edits — a stable or explicably-changed count is fine; a `FAIL` line
or a non-zero exit is not. Reporting any `UNVERIFIED` notice on its own as a
defect manufactures a corpus-wide emergency that is not happening.

**"Traceability checks" resolve to what `validate.py` already does.** No
distinct traceability tool exists anywhere in this repository (`git grep -rln
"traceab" -- launchpad/project-intelligence/ Justfile .github/` returns
nothing) and Feature #621, which would own one, is still open. `validate.py`
already resolves every `relationships[].target` to a real node id and every
file citation to a real path — that is the traceability check available
today. Name #621 if a caller wants more than this.

**The review summary** is one line per node this skill examined in the
impacted set — not only the ones it edited:

```
<node id>  <triggering path>  <evidence entry that cited it>  revision: moved to <sha> (MUST 3 route N) | unmoved (MUST 4)
```

plus a coverage-gap section grouped by `coverage_gaps.by_area`, and an
explicit list of any node the impacted set named that was examined and
correctly left unchanged. Listing those separately from nodes never opened
at all is the difference between "not affected" and "not looked at" — a
reviewer needs to tell them apart, and the impacted-set count alone does not.

**`regenerate.py --format text` already emits this format — run it, don't
hand-assemble it.** One line per triggering (node id, path, evidence entry)
ending `revision: unmoved (MUST 4) -- blocking claim(s): <n, n, …>` or,
once `--apply` has run, `moved to <sha>`, followed by a `COVERAGE GAPS
<n> path(s), <n> redacted` section grouped exactly the way
`coverage_gaps.by_area` groups it (one count line per area) and, when
non-empty, an `UNREADABLE NODES` section. It is not a line-for-line
identical rendering of the format above — it also names the blocking claim
numbers per node, which the format sketch omits — but it is the same
underlying data, already assembled, and satisfies this section's DoD without
hand-formatting `impact.py`'s and `stale.py`'s raw output yourself.

## Phase 5 — branch safety

**The measured truth: `launchpad` is this repository's default branch and
carries no protection.** Three endpoints agree — `gh api
repos/launchpad-26/buzz/rulesets` → `[]`, `gh api
repos/launchpad-26/buzz/rules/branches/launchpad` → `[]`, `gh api
repos/launchpad-26/buzz/branches/launchpad/protection` → `404`. Nothing on
GitHub will stop a push straight to `launchpad`. This skill does not tell its
reader the platform is a backstop, because it is not one — the refusal has
to be this skill's own.

**Before the first edit**, run:
```
git rev-parse --abbrev-ref HEAD
```
and refuse to proceed if the result is `launchpad`. Work happens on a branch
cut from `launchpad`; commits are `git commit -s` (DCO required); the result
reaches `launchpad` only through a PR opened with `--base launchpad`. For
Feature #534 work specifically, this skill's own output joins the
one-Feature-one-PR flow (ADR-0054) rather than opening its own PR.

## Never

- Never edit a node `impact.py` did not name.
- Never move a recorded-revision entry without MUST 3 satisfied, by name,
  for every claim in that node's ledger.
- Never change or invent a node `id`.
- Never create a node for a coverage gap — report it as a finding instead.
- Never delete a retired node's file.
- Never report a `validate.py` run's `UNVERIFIED` notices as failures.
- Never commit directly on `launchpad`.

## Where this came from

Written for issue #631, parent Feature #534, parent PRD #602. It depends on
two siblings already merged onto this branch — `stale.py` (#556) and
`impact.py` (#635) — and feeds one that comes after it: #559, which
demonstrates this whole flow on a real change and produces a reviewable
artefact. This skill's own worked example in Phase 1 is a rehearsal only —
it proves the commands written here are the commands that actually run; it
is not #559's deliverable, and it stops at the impacted-node list without
editing anything.
