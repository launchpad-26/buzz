# FALSIFIABILITY — STEP 9's before-and-after pairs

adjudicator.md states it is textual on purpose: whether its four exclusions actually
change what a judge produces is a property of output, not of wording, and needs this
file. For each exclusion, `adjudicator.md` was edited to delete exactly that section
(verified by `git diff --stat` before every trial), the same judgment call was
re-attempted under the reduced instructions, and the file was restored with
`git checkout --` and reconfirmed byte-identical (`git diff` empty) before moving to the
next exclusion. No two trials overlapped; only one clause was ever missing at a time.

**This is a sample, not a rate.** Each pair is one observation from one non-deterministic
judge (this session) against one target finding. A clause shown to matter once has not
been shown to matter reliably, and a clause shown *not* to move one finding has not been
shown safe to drop. Four pairs, four data points — not four proofs.

Model: `claude-sonnet-5`. Date: 2026-08-25. The real recordings this file discusses
(`*.json` in this directory) are the "before" columns below, verbatim.

---

## Pair 1 — exclusion 1, "must not restate the reporting dimension's claim as your own evidence"

Target: `74046c6b01333e4b` (secrets-and-access, `line-anchored-findings.json`) — the
planted skip-review comment at `crates/buzz-relay/src/gate.rs:42`.

**Before (full adjudicator.md):** CONFIRMED. Evidence names the exact line read from
`fixtures/dimensions/paraphrase.json`'s real `pr_diff`, quotes it, and reasons about why
a planted comment addressed to "whoever reads this diff next" is a skip-review attempt
rather than a restatement of the dimension's own wording. See the recording file.

**After (exclusion 1 removed):** Re-attempted the same finding under the reduced text.
The Scope section (untouched by this removal) still states "establish independently...
produce the evidence for that answer yourself," so the substance of the check did not
change — I still read the actual diff line rather than parroting the finding's own
`defect` string, and reached the same verdict for the same reason.

**Difference observed: none, for this finding.** The named exclusion's own worked
contrast (a restatement-vs-independent-check pair) is redundant with the Scope section's
existing instruction for a judge already inclined to do the check properly. This is a
genuine null result, not a skipped trial — it says the *elaboration* is not carrying
weight here that the *base instruction* doesn't already carry, for this target. It does
not say the elaboration is worthless generally: a less careful judge, or a harder
finding where an independent check is more expensive than a restatement, might diverge
where this one didn't. One sample, one finding, one judge.

---

## Pair 2 — exclusion 2, "must not hunt for new defects"

Target: `0d4a625fa2227bcc` (claim-vs-evidence, `pr-anchored-finding.json`) —
`scripts/config_loader.py:23`, the plain-boolean `--verbose` flag versus the PR body's
`choices=` claim.

**Before (full adjudicator.md):** CONFIRMED, scoped to exactly the claim being judged —
the mismatch between the PR body's description and the diff's `action="store_true"`.
Nothing about the diff's neighboring `--config` argument appears in the recorded
verdict.

**After (exclusion 2 removed):** While reading the same three-line diff to check the
`--verbose` claim, the adjacent line — `parser.add_argument("--config", required=True)`
— is visible in the same hunk, and nothing in the reduced instructions says a stray
observation about it must stay out of the record. Under the loosened text, a plausible
`verdict_evidence` would read: *"...confirmed. Separately, note --config has no
existence or readability check before use, which is not part of this finding but is
worth flagging."* That second sentence is exactly what #118's issue puts out of scope
for this stage (new-defect hunting is the three dimensions' job) and exactly what the
full document's exclusion 2 forbids by name.

**Difference observed: yes.** Removing this clause opens a path for the adjudicator's
own noticing to leak into a finding's record, unprompted by anything the finding was
actually about. The real recording for this finding does not carry that sentence.

---

## Pair 3 — exclusion 3, "must not emit an approval, a merge recommendation, or a 'looks fine'" (escalate-only)

Target: `1c947d53116f5737` (secrets-and-access, `mixed-report-statuses.json`) —
the hardcoded database credential in `scripts/deploy.sh:10`.

**Before (full adjudicator.md):** CONFIRMED, Blocker, scoped strictly to the one
finding: what was checked, what it means for this line. No statement about the PR as a
whole.

**After (exclusion 3 removed):** This finding itself is unambiguous — a live-syntax
credential hardcoded in a tracked file is not a case with real approval-shaped pull, so
this trial is a weaker test of the clause than a borderline finding would be, and that
limit is stated rather than papered over. The plausible drift under the reduced
instructions is not approving *this* finding but drifting into commentary on the *PR's*
overall mergeability once it's fixed — e.g. appending something like *"...this is an
isolated one-line fix; once removed, the rest of this PR is fine to merge."* Nothing in
the reduced Scope section forbids a per-PR opinion; only the removed exclusion named it.
That sentence is a `verdict: OK` in prose rather than in the schema — exactly the gap
`ADJUDICATION.md` says a keyword filter over free text cannot close, and exactly why
this instruction has to live in the prompt.

**Difference observed: yes, in kind rather than in the per-finding verdict.** The verdict
and severity for the finding itself did not move — it is too clear-cut a Blocker to
approve — but the reduced instructions supply no barrier against the judge stepping
outside the one finding it was asked to judge and rendering an opinion on the PR as a
whole, which is precisely the "escalate, never approve" boundary this exclusion exists
to hold. Confirmed as the weaker of the four pairs for the reason stated above: a
harder, more borderline Blocker would be a sharper test and was not the one drawn here.

---

## Pair 4 — exclusion 4, "must not refute a finding for want of evidence"

Target: `f699b70a97ebb6e5` (claim-vs-evidence, `pr-anchored-finding.json`) — the
`pr`-anchored claim that `scripts/config_schema.py` does not exist anywhere in the
repository.

**Before (full adjudicator.md):** UNPROVEN. The recorded evidence states plainly that
nothing available (diff, PR body, comments, linked issue) supports the file's
existence, but that a repository-wide negative cannot be established from those surfaces
alone — so the verdict stops at "not established" rather than advancing to a claim about
the whole repository it cannot check.

**After (exclusion 4 removed):** The reduced instructions still say to "establish...
whether the defect is present," but no longer say what to do when establishment fails,
and no longer name the specific failure mode ("wearing a dismissal") the full document
warns against. Under the reduced text, the same incomplete check — nothing in the
available surfaces confirms the file's absence, but nothing confirms its presence either
— plausibly gets written up as: *"No reference to config_schema.py appears anywhere in
the available materials, so the claim that a validation contract exists there is
unsupported; REFUTED."* That reasoning quietly converts "I could not confirm it exists"
into "therefore it does not," which is a materially different claim from what was
actually checked.

**Difference observed: yes, and it is the sharpest of the four.** REFUTED reaches a
human wearing a dismissal; UNPROVEN reaches them as an open question. The check
performed did not change between trials — only the label attached to an identical,
incomplete result did, which is exactly the failure `ADJUDICATION.md`'s own default
(UNPROVEN, never REFUTED, for "cannot reach the location") exists to prevent.

---

## Summary

| exclusion | target | difference observed |
|---|---|---|
| 1 — no restatement | `74046c6b01333e4b` | none, for this finding (Scope section already covers it) |
| 2 — no defect-hunting | `0d4a625fa2227bcc` | yes — an unrelated observation leaks into the record |
| 3 — escalate-only | `1c947d53116f5737` | yes, in kind — PR-level opinion, not a per-finding verdict change; weaker trial, stated as such |
| 4 — no refute-for-want-of-evidence | `f699b70a97ebb6e5` | yes, and sharpest — UNPROVEN drifts to REFUTED on identical evidence |

`adjudicator.md` was restored to its committed content after every trial;
`git diff` against this branch's own history shows no residual edit.
