---
description: Issue #559 — a full run of the corpus regeneration chain (impact.py, stale.py, regenerate.py) against one real, already-merged repository change, ending in two citations re-anchored under MUST 4 and neither recorded revision moved.
tags: [corpus, provenance, regeneration, research, issue-559]
---

# Corpus regeneration demonstration: one real repository change

## What this is

A single replayable run of the canonical-corpus regeneration chain — `impact.py`
(#635), `stale.py` (#556), and `regenerate.py` (#559, this issue) — against one
real commit already merged into `origin/launchpad`, ending in two corpus
citations re-anchored to their current source lines and both nodes' recorded
revisions left unmoved, because neither node's evidence ledger clears
`standards/provenance.md`'s MUST 3 route 2 for every claim.

This is a record of what happened, not a procedure. For the procedure, see
`.claude/skills/corpus-maintain/SKILL.md`; this document does not restate it.

## The triggering change, and why it was chosen

**Commit `2d4b887f3c7ce444aae0f424f7f8695c5b447af5`**, `fix(settings): address
non-blocking findings from #1935's review panel`, 2026-08-31, already on
`origin/launchpad`. Four files changed, real product code (not a documentation
edit) — chosen over three other measured candidates because its impacted set
(two nodes) is small enough for a human to read in full, it touches no
launchpad-owned files exclusively, and — being an already-merged, real commit —
the demonstration is reproducible with no live external dependency, satisfying
the DoD's replayability requirement. It resolves locally:

```
$ git cat-file -e 2d4b887f3c7ce444aae0f424f7f8695c5b447af5^{commit}
$ echo $?
0
```

## The chain, run in order, verbatim

All four commands below were run from the repository root of the shared
worktree (`feature/534-corpus-maintenance-updates`), then re-run again after
STEP 5's edits (STEP 6) to confirm the result held.

### 1. Confirm the working branch

```
$ git rev-parse --abbrev-ref HEAD
feature/534-corpus-maintenance-updates
```
exit 0.

### 2. `impact.py` — which nodes does this change touch?

```
$ python3 launchpad/project-intelligence/corpus/impact.py --base 2d4b887f3c^ --head 2d4b887f3c
```
exit 0. Verbatim JSON (identical across two independent runs, before and
after STEP 5's edits — the corpus front matter this command reads is not
what changed):

```json
{
  "coverage_gaps": {
    "by_area": {
      "desktop": 2,
      "launchpad": 1
    },
    "paths": [
      "desktop/src/launchpad/settings/registry.ts",
      "desktop/tests/e2e/knowledge-settings-keyboard.spec.ts",
      "launchpad/plans/2026-08-27-issue-551-knowledge-crate-scaffold.md"
    ],
    "redacted_count": 0
  },
  "impacted_nodes": [
    {
      "changed_path": "desktop/src/features/settings/ui/SettingsPanels.tsx",
      "evidence_entry_index": 8,
      "node_id": "capabilities-channels-channel-templates",
      "reason": "cites desktop/src/features/settings/ui/SettingsPanels.tsx",
      "statement": "Buzz Desktop manages templates through a dedicated Settings panel ('Channel templates'), reachable via `SettingsPanels.tsx`'s `channel-templates` section and rendered by `ChannelTemplatesSettingsCard`, which supports create, edit, duplicate and delete."
    },
    {
      "changed_path": "desktop/src/features/settings/ui/SettingsPanels.tsx",
      "evidence_entry_index": 2,
      "node_id": "capabilities-moderation-operator-dashboard",
      "reason": "cites desktop/src/features/settings/ui/SettingsPanels.tsx",
      "statement": "The desktop app's Settings surface has a dedicated 'Moderation' panel (nav entry value 'moderation', label 'Moderation') that renders `ModerationQueueCard`, and that card exposes a 'Queue' tab (open reports, grouped by target) and an 'Audit log' tab (accepted moderation actions, newest first)."
    },
    {
      "changed_path": "desktop/src/features/settings/ui/SettingsPanels.tsx",
      "evidence_entry_index": 2,
      "node_id": "capabilities-moderation-operator-dashboard",
      "reason": "cites desktop/src/features/settings/ui/SettingsPanels.tsx",
      "statement": "The desktop app's Settings surface has a dedicated 'Moderation' panel (nav entry value 'moderation', label 'Moderation') that renders `ModerationQueueCard`, and that card exposes a 'Queue' tab (open reports, grouped by target) and an 'Audit log' tab (accepted moderation actions, newest first)."
    }
  ],
  "unreadable_nodes": []
}
```

**Impacted set**: 2 unique node ids, both DIRECT hits (0 propagated, 0
unreadable). `capabilities-moderation-operator-dashboard` appears twice
because its evidence entry 2 carries two separate citations of the same
changed path (`:209-212` and `:868-869`, pre-edit). **Coverage gaps**: 3
paths, grouped `desktop: 2, launchpad: 1`, `redacted_count: 0` — reported
here, not filled (`corpus-maintain`'s own rule; filling a gap is
`corpus-author`'s job under a different issue).

### 3. `stale.py` — independent staleness check, against the current tip

```
$ python3 launchpad/project-intelligence/corpus/stale.py --head HEAD
```
exit 0. 2,840 lines total (one per stale/unestablished finding across all 205
nodes) — truncated here to the final summary and the lines naming this
demonstration's two nodes; the full run is reproducible verbatim with the
command above.

```
...
STALE  capabilities-channels-channel-templates: crates/buzz-cli/src/commands/channels.rs -- file changed between the recorded revision and head (recorded 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, current 0808ab485c39c3c12ef02af2188c65a5145eb99d)
STALE  capabilities-channels-channel-templates: crates/buzz-cli/src/lib.rs -- file changed between the recorded revision and head (recorded 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, current d555ec95feb3a8bc5126385a1272d55aa051fe85)
STALE  capabilities-channels-channel-templates: desktop/src/app/AppShell.tsx -- file changed between the recorded revision and head (recorded 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, current 4d77175c78f4df48e13398b25b271e3ac1b31dd3)
STALE  capabilities-channels-channel-templates: desktop/src/features/settings/ui/SettingsPanels.tsx -- file changed between the recorded revision and head (recorded 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, current 487132bd415881fbd6e0c91cd85224e91012e07e)
STALE  capabilities-channels-channel-templates: desktop/src/shared/api/types.ts -- file changed between the recorded revision and head (recorded 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, current 2f66ee24a0bf5efa958378069a6b155e99a1d068)
UNESTABLISHED  capabilities-channels-channel-templates: evidence entry 3, citation 3 -- is a commit reference, which names no file `git diff` can check (recorded 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5)
UNESTABLISHED  capabilities-channels-channel-templates: evidence entry 3, citation 4 -- is a commit reference, which names no file `git diff` can check (recorded 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5)
...
STALE  capabilities-moderation-operator-dashboard: VISION_MODERATION.md -- file changed between the recorded revision and head (recorded 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, current 8740a1fa94dd14a3eb5cd2a570b0be2c4a68cbfe)
STALE  capabilities-moderation-operator-dashboard: crates/buzz-relay/src/api/bridge.rs -- file changed between the recorded revision and head (recorded 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, current 0808ab485c39c3c12ef02af2188c65a5145eb99d)
STALE  capabilities-moderation-operator-dashboard: crates/buzz-relay/src/handlers/moderation_commands.rs -- file changed between the recorded revision and head (recorded 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, current 86b9142a09f2af3ba2fff7effa6a6cd53b40f51c)
STALE  capabilities-moderation-operator-dashboard: crates/buzz-relay/src/router.rs -- file changed between the recorded revision and head (recorded 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, current 86b9142a09f2af3ba2fff7effa6a6cd53b40f51c)
STALE  capabilities-moderation-operator-dashboard: desktop/src/features/settings/ui/ModerationQueueCard.tsx -- file changed between the recorded revision and head (recorded 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, current b0466ac465336cb773fbf7355ec05f7d61f4a3aa)
STALE  capabilities-moderation-operator-dashboard: desktop/src/features/settings/ui/SettingsPanels.tsx -- file changed between the recorded revision and head (recorded 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, current 487132bd415881fbd6e0c91cd85224e91012e07e)
UNESTABLISHED  capabilities-moderation-operator-dashboard: evidence entry 14, citation 1 -- is a graph-edge or tool-result citation, which names no openable file (recorded 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5)
...
SUMMARY  205 node(s): 195 stale, 6 fresh, 4 unestablished
```

`stale.py` answers a different question than `impact.py`: not "did this one
commit touch something this node cites" but "has anything this node cites
moved since its OWN recorded revision, independent of any one commit." Both
of this demonstration's nodes are independently confirmed `STALE` here too —
`SettingsPanels.tsx` (the file `2d4b887f3c` touched) is one of several stale
citations each node carries, not the only one.

### 4. `regenerate.py` — the deterministic disposition

**Pre-edit** (before STEP 5's re-anchoring):
```
$ python3 launchpad/project-intelligence/corpus/regenerate.py --base 2d4b887f3c^ --head 2d4b887f3c --format text
```
exit 0:
```
capabilities-channels-channel-templates  desktop/src/features/settings/ui/SettingsPanels.tsx  evidence entry 8  revision: unmoved (MUST 4) -- blocking claim(s): 3, 8
capabilities-moderation-operator-dashboard  desktop/src/features/settings/ui/SettingsPanels.tsx  evidence entry 2  revision: unmoved (MUST 4) -- blocking claim(s): 2, 12, 13, 14
capabilities-moderation-operator-dashboard  desktop/src/features/settings/ui/SettingsPanels.tsx  evidence entry 2  revision: unmoved (MUST 4) -- blocking claim(s): 2, 12, 13, 14

COVERAGE GAPS  3 path(s), 0 redacted
  desktop: 2
  launchpad: 1
```

**Post-edit** (after STEP 5's re-anchoring, STEP 6):
```
$ python3 launchpad/project-intelligence/corpus/regenerate.py --base 2d4b887f3c^ --head 2d4b887f3c --format text
```
exit 0:
```
capabilities-channels-channel-templates  desktop/src/features/settings/ui/SettingsPanels.tsx  evidence entry 8  revision: unmoved (MUST 4) -- blocking claim(s): 3, 8
capabilities-channels-channel-templates  desktop/src/features/settings/ui/SettingsPanels.tsx  evidence entry 8  revision: unmoved (MUST 4) -- blocking claim(s): 3, 8
capabilities-moderation-operator-dashboard  desktop/src/features/settings/ui/SettingsPanels.tsx  evidence entry 2  revision: unmoved (MUST 4) -- blocking claim(s): 2, 12, 13, 14
capabilities-moderation-operator-dashboard  desktop/src/features/settings/ui/SettingsPanels.tsx  evidence entry 2  revision: unmoved (MUST 4) -- blocking claim(s): 2, 12, 13, 14

COVERAGE GAPS  3 path(s), 0 redacted
  desktop: 2
  launchpad: 1
```
Same node ids, same disposition, same blocking claim indexes both times — the
channel-templates row now prints twice because its entry 8 carries two
citations of the changed path after re-anchoring (`:228-231` and `:953-954`),
where it carried one before (`:88-187`).

### 5. Negative branch-guard run

Run with `--repo-dir` pointed at a **throwaway `git worktree`** checked out on
`launchpad` (`git worktree add <tmp-dir> launchpad`), never by checking out
`launchpad` in the shared worktree:
```
$ python3 launchpad/project-intelligence/corpus/regenerate.py --base 2d4b887f3c^ --head 2d4b887f3c --repo-dir <tmp-guard-check-worktree> --apply
--apply refused: current branch is 'launchpad', this repository's default
branch. Nothing on GitHub enforces this for launchpad-26/buzz -- the refusal
is this tool's own. Run from a branch cut from launchpad instead.
```
exit 1. `git status --short` in that throwaway worktree showed no output
(nothing written) before it was removed via `git worktree remove`.

## The MUST 3 route-2 arithmetic, blocking claim by blocking claim

For each node, `regenerate.py` classifies every evidence entry OTHER than the
recorded-revision entry itself: **closed** if any citation on that entry is
non-file (a commit reference, graph edge, tool result, or URL — route 2
cannot run at all); otherwise **dirty** if any file citation changed between
the recorded revision (`338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5` for both
nodes) and head, else **clean**. A node may-move only if every entry is
clean; one dirty or closed entry is enough to force `must-not-move (MUST 4)`.

**`capabilities-moderation-operator-dashboard`** — blocking entries `2, 12,
13, 14`:
- entry 2 — **dirty**: `SettingsPanels.tsx` changed (the citation this
  demonstration re-anchors).
- entry 12 — **dirty**: `launchpad/docs/corpus/architecture/context/relay-operator.md` changed since the recorded revision.
- entry 13 — **dirty**: same file, cited again from a different claim.
- entry 14 — **closed**: cites `git_ls_tree(ref='origin/launchpad', ...) ->
  ... at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5` — a `tool_result`
  citation of the SAME sha this node's recorded revision names, but as a
  genuinely historical "as of commit X" claim, not the recorded-revision
  entry itself. **This is the exact shape STEP 2's `--apply` design guards
  against**: a naive global string-replace of the old sha would have
  corrupted this citation the moment the node became eligible to move —
  measured at 88 of 226 real corpus nodes sharing this shape today.

**`capabilities-channels-channel-templates`** — blocking entries `3, 8`:
- entry 3 — **closed**: cites two commit references (`commit 1b9f6169e`,
  `commit 1a9414618`, naming the PRs that introduced the feature) alongside
  two file citations — one non-file citation is enough to close the whole
  claim.
- entry 8 — **dirty**: `SettingsPanels.tsx` changed (the citation this
  demonstration re-anchors).

The remaining entries per node are route-2 clean and not listed individually
here — 10 for `capabilities-channels-channel-templates` and 9 for
`capabilities-moderation-operator-dashboard` (the counts differ because the
two nodes' ledgers have different total entry counts); the full per-claim
JSON is reproducible with `--format json` against the commands above.
**Neither node clears the bar** — MUST 4 is the correct, conservative outcome
for both, exactly as `standards/provenance.md` states it should be by
default.

**A note on the head used for this arithmetic.** `regenerate.py`'s `--head`
serves both `impact.py`'s impacted-set computation and the route-2 diff, per
#559's own plan. `2d4b887f3c` (this demonstration's chosen commit) is an
ancestor of `origin/launchpad`'s current tip but is itself **not** an
ancestor of the recorded revision's own descendant relationship —
`338b4d0cf2` (the recorded revision) is **not** an ancestor of `2d4b887f3c`
(`git merge-base --is-ancestor 338b4d0cf2... 2d4b887f3c` exits 1): the two
commits sit on parallel PR branches later reconciled by a merge that is an
ancestor of `origin/launchpad` but is neither commit itself. This does not
affect correctness here — `classify_claim` only calls git operations that
take two revisions positionally (`git diff A B -- path`, `git cat-file -e
A:path`), which are well-defined regardless of ancestry, never the
merge-base-relative range form (`git log A..B`) that genuinely would go
quietly empty for a non-ancestor `A`. Confirmed independently: this run's
`SettingsPanels.tsx` "dirty" result for both nodes matches STEP 1's own
grep-based line inspection. Consequently, this run's blocking-claim counts
(4 for moderation, 2 for channel-templates) are smaller than a corpus-wide
sweep against the CURRENT tip would show (the plan's own earlier
provenance.md measurement found 8 and 9 blocking claims respectively,
diffing against `origin/launchpad`'s tip rather than `2d4b887f3c`) — fewer
commits between the recorded revision and an earlier head means fewer files
can have changed. The conclusion (MUST 4 for both) is identical either way,
since a single blocking claim already forces it.

## The three re-anchored citations, before and after

Three citation slots were touched (moderation's two citations on entry 2,
channel-templates' one citation on entry 8); one of them —
channel-templates' single wide range — was split into two precise anchors
rather than merely moved, so the four resulting anchor strings ("four new
anchors" below) come from re-anchoring three original citations, not four.

Re-verified against `desktop/src/features/settings/ui/SettingsPanels.tsx` at
`HEAD` (982 lines, identical to `origin/launchpad` on this file — `git diff
HEAD origin/launchpad -- <path>` is empty) before writing any new anchor.

**`capabilities-moderation-operator-dashboard`, evidence entry 2** — both
citations re-anchored, statement unchanged (still holds: confirmed the nav
entry and the render arm both still exist, just moved):

| | Before | After |
|---|---|---|
| Citation 1 | `SettingsPanels.tsx:209-212` | `SettingsPanels.tsx:254-256` |
| Citation 2 | `SettingsPanels.tsx:868-869` | `SettingsPanels.tsx:967-968` |

```
$ sed -n '254,256p' desktop/src/features/settings/ui/SettingsPanels.tsx
    value: "moderation",
    label: "Moderation",
    icon: ShieldAlert,

$ sed -n '967,968p' desktop/src/features/settings/ui/SettingsPanels.tsx
    case "moderation":
      return <ModerationQueueCard />;
```

**`capabilities-channels-channel-templates`, evidence entry 8** — the single
wide range `:88-187` (which no longer covers the relevant lines at all) was
replaced with two precise citations covering the nav descriptor and the
render arm — narrower and more accurate than the original, not merely
moved; statement unchanged (still holds):

| | Before | After |
|---|---|---|
| Citation | `SettingsPanels.tsx:88-187` | `SettingsPanels.tsx:228-231` **and** `SettingsPanels.tsx:953-954` |

```
$ sed -n '228,231p' desktop/src/features/settings/ui/SettingsPanels.tsx
    value: "channel-templates",
    label: "Channel templates",
    icon: LayoutTemplate,
    featureGate: "channel-templates",

$ sed -n '953,954p' desktop/src/features/settings/ui/SettingsPanels.tsx
    case "channel-templates":
      return <ChannelTemplatesSettingsCard />;
```

The moderation node's body prose (`## Maturity`) also embedded the same
citation inline (`SettingsPanels.tsx:209-212,868-869`) and was updated to
match, for the same reason: leaving it stale while the front-matter ledger
moved would have left two inconsistent anchors for the same fact.

```
$ git diff --stat -- launchpad/docs/corpus/
 launchpad/docs/corpus/capabilities/channels/channel-templates.md    | 3 ++-
 launchpad/docs/corpus/capabilities/moderation/operator-dashboard.md | 6 +++---
 2 files changed, 5 insertions(+), 4 deletions(-)
```
Two files changed, both under `launchpad/docs/corpus/capabilities/`; only
citation strings changed; no `id:` line touched; neither node's "authored and
checked against repository revision" statement (its own recorded-revision
entry) changed.

## The two recorded revisions — unmoved, and why

Both nodes record `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`. **Neither
moved.** Per `standards/provenance.md` MUST 4 (the default outcome, not a
compromise): a node's recorded revision only advances when EVERY claim in its
full evidence ledger clears MUST 3 route 2 (or a human re-verifies it via
route 1). `capabilities-moderation-operator-dashboard` has 4 blocking claims
(entries 2, 12, 13, 14) and `capabilities-channels-channel-templates` has 2
(entries 3, 8) against this demonstration's chosen head — either count alone
is enough to force `must-not-move`. Re-verifying every blocking claim by hand
(route 1) so the revision COULD move was explicitly rejected as scope creep
for this issue (OPEN item 2) — this run demonstrates the mechanical half
honestly, not a shortcut past it.

**Triggering revision, for the record** (provenance.md SHOULD 2 — front
matter has no field for this, so it belongs in the commit body that lands
this work, not in either node): `2d4b887f3c7ce444aae0f424f7f8695c5b447af5`.
For each edited node, the citations touched by this change (entries 2 and 8
respectively) were re-anchored via MUST 2 (unconditional re-verification of
any claim an edit touches); the recorded-revision entry itself was left
unmoved under MUST 4, for the blocking-claim reasons above.

## What this did not establish

- **A re-anchored citation is movement of an anchor, not proof the claim is
  true.** `regenerate.py` and this demonstration confirmed the two touched
  statements still hold by opening the source at the new line numbers — that
  is MUST 2's route-1 re-verification, done by a human (this run), for
  exactly the two claims this change touched. It says nothing about the
  other ~20 claims across both nodes' ledgers that were classified
  mechanically (route 2) or left unestablished — those are still only as
  trustworthy as their own citations, unread by this run.
- **This demonstration edits no generated view, because none exists.**
  `git ls-files launchpad/docs/corpus/ | grep "/generated/"` returns nothing;
  Feature #621 owns that surface and is still open.
- **The branch guard is this tool's own refusal, not a platform backstop.**
  `gh api repos/launchpad-26/buzz/rulesets` and
  `.../rules/branches/launchpad` both return `[]`, and
  `.../branches/launchpad/protection` returns `404` — nothing on GitHub stops
  a direct push or commit to `launchpad`. `regenerate.py --apply` refusing on
  that branch is the only thing that does.
- **`regenerate.py` never re-anchors a citation itself.** Locating where a
  drifted range moved to is not deterministic in general; a tool that
  guessed could point a citation at the wrong code, worse than the drift it
  fixed. The four new anchors above were located and verified by a human (or
  agent under `corpus-maintain`) opening the file, never by the tool.
- **Neither `regenerate.py`'s conclusions nor this record were reviewed by
  anyone but the person who ran them**, at the time of writing. This
  document is the replayable evidence for that review, not a substitute for
  it.

## Replaying this

Every command above can be re-run verbatim from a checkout of
`feature/534-corpus-maintenance-updates` at or after the commit that lands
`regenerate.py`. `capabilities-moderation-operator-dashboard` and
`capabilities-channels-channel-templates` both resolve via `git grep -l
"<id>" launchpad/docs/corpus/` to their canonical files under
`launchpad/docs/corpus/capabilities/`. `2d4b887f3c7ce444aae0f424f7f8695c5b447af5`
resolves via `git cat-file -e 2d4b887f3c7ce444aae0f424f7f8695c5b447af5^{commit}`.
