# Publishing — one review, kept current

Implements [#119](https://github.com/launchpad-26/buzz/issues/119), under PRD
[#109](https://github.com/launchpad-26/buzz/issues/109).

A pull request gets exactly one review comment from this agent. Pushing a new commit
updates that same review object rather than adding another — GitHub offers no way to
remove a submitted COMMENT review, so accumulation is permanent the moment it happens.
This document is the normative contract for how that one review is identified, when it
is judged incomplete rather than clean, and what runs it under which credential.

**#117's contract is SETTLED** as of the plan at
`launchpad/plans/2026-08-12-issue-117-review-dimensions.md` (feat-review-agent-dimensions
worktree), reviewed three times and still uncommitted — a settled decision, not a settled
ref. **#118 is MERGED** to `launchpad` at `b904a5a` (PR #1406), closing
[#118](https://github.com/launchpad-26/buzz/issues/118). The one thing this stage cannot
verify from either: the completion-marker nonce authenticates a marker echoed out of
author text, never the document itself — a compromised runner emits a self-consistent
document with its own nonce, and nothing here can tell. See § The credential and its
controls, and never describe a published review as unforgeable.

---

## Identity — marker AND author, never marker alone

Every body this agent posts starts with a hidden marker,
`<!-- launchpad-review-agent:v1 -->`. The marker says "this is our kind of review"; the
author login says "this one is ours" — and neither alone is sufficient.

**The marker is attacker-writable.** This fork is public: any GitHub user with read
access can submit a COMMENT review on a pull request and write its body, marker
included. Matching on the marker alone lets an outside party choose which review object
`find_existing` resolves to. If that review is not one this token owns, the PUT is
refused and — under the hard-fail rule below — nothing is posted at all. Marker-only
matching turns that into a denial of publication an outsider can trigger deliberately,
on any pull request they choose, at any time.

**The author login is SUPPLIED, never discovered.** It arrives via `--as`
(default `github-actions[bot]`) and is compared against each review's `user.login`.
Not `GET /user`: that endpoint's own documentation lists OAuth-app and personal-access
tokens as what it supports, and an installation access token is not among them — a
runtime call to resolve identity is a needless failure mode for a value known before
the run starts, on every pull request, the day it fails. Not a login frozen into the
source either: [#110](https://github.com/launchpad-26/buzz/issues/110) commits to
revisiting the credential, and a hardcoded comparison breaks at exactly the moment it
moves. The configured value is verified against the live identity by
`check_publish_scope.py`'s IDENTITY control (§ The credential and its controls), which
is the only place that comparison can be checked at all.

**An unresolved identity aborts.** `find_existing` raises on an empty or missing login
rather than degrading to matching on the marker alone. A loud failure to publish is
strictly better than a quiet invitation: one is visible in a job log, the other is
available to anyone who can open a pull request.

**A marked review under any other login is foreign, and is never a PUT target.** The
listing already carries what the filter needs — `find_existing` compares each marked
review's `user.login` against the configured login BEFORE ranking by recency, not
after. Newest-wins ignoring authorship is the one combination worse than either concern
alone: it removes even the timing requirement an attacker would otherwise need, so a
review planted at any moment wins every run thereafter.

**A NONZERO foreign count also refuses a fresh POST.** If `find_existing`'s first
element is `None` and the foreign count is nonzero, `post_or_update` raises rather than
creating a new review. That count cannot be told apart, from the data alone, between a
planted decoy and this agent's own review orphaned by a changed `--as` value — both
read identically once the configured login no longer matches whoever it posted as. A
human looks at the pull request's existing reviews before this proceeds, rather than
the tool guessing which case it is. The refusal is checked a second time immediately
before the POST, since two pushes seconds apart produce two workflow runs and a check
made at the start of a run is stale by the time it posts.

**A clean listing — zero foreign count, not merely "no match" — still posts.** These
two rules are paired on purpose: both a foreign-only listing and an empty listing
return `None` as `find_existing`'s first element, and only one of them may post. The
refusal keys on the foreign count, never on the first element being `None` alone.

---

## Exactly one review object, updated in place

`find_existing` paginates the full listing (`gh api ... --paginate`) and resolves to
the NEWEST review under the configured login that carries the marker — never the
oldest. A submitted COMMENT review cannot be deleted, so once two of the agent's own
markers exist on one pull request, neither can be retired; the one a human reaches at
the bottom of the timeline must be the current one, and that is always the newest.

A failed PUT — any non-2xx status — raises. It never falls back to POST. A fallback
would create the second review this entire contract exists to prevent, on exactly the
run where something is already wrong.

The event posted is the literal `"COMMENT"`, hardcoded at the one call site.
`post_or_update` takes no event parameter. `APPROVE` and `REQUEST_CHANGES` do not
appear anywhere in `publish.py` — a parameter that could hold `"APPROVE"` is a
parameter that one day will.

**The head SHA lives in the rendered body, not in GitHub's own metadata**, because
`commit_id` is frozen at submission: an updated review keeps its original
`submitted_at` and `commit_id`, so the PR timeline shows the review at the time of the
first push with a body describing the latest commit. The body names the SHA — and the
merge base alongside it, see below — so nothing is ambiguous to a reader who reads it.

---

## The incomplete case — ten conditions, and the default is incomplete

A review is INCOMPLETE, and renders a banner naming every offending stage, dimension
or entry point at the TOP of the body — above every finding — when any of:

1. a stage in the manifest has status other than `"complete"`
2. a report has `status: failed`
3. a report's `completion_marker` is absent, or is not the last key
4. a report's marker names a dimension other than that report's own `dimension` field
5. a report's marker nonce differs from the merged document's `nonce`, or two reports'
   markers disagree with each other
6. `findings_count` does not equal `len(findings)`
7. a dimension named by the manifest produced no report at all
8. a report has `status: complete` and no `outcome`
9. the `containment` block is absent or unparseable
10. `set(containment.states)` does not EQUAL `set(contain.ENTRY_POINTS)` — a set
    comparison, never a count. Six real keys plus one typo also counts to seven.

Two more conditions apply, inherited from the renderer itself rather than from any
upstream stage: a finding whose `severity` is outside `review.SEVERITY_ORDER` triggers
the banner (and renders under "malformed finding" — see below), and a `containment`
argument of `None` triggers it too.

**The banner is at the top because a reader who stops after the first finding must
still have seen it.** A partial review that reads as a complete one is exactly what
this stage exists to prevent. **The default is incomplete**: an input this stage
cannot classify — an unparseable report, a manifest entry with no status — renders the
banner rather than being silently treated as fine. Absence of a failure signal is not
evidence of success.

On condition 5 and what the nonce does and does not prove: #117's marker is
`BUZZ-DIMENSION-COMPLETE:{dimension}:{nonce}`, and the merged document carries that
same run's `nonce` as a top-level key — ONE nonce per run, so no marker can
legitimately carry a different dimension's. The primary check is each report's marker
against the document's own value; agreement between sibling reports is a secondary
check, because a run whose reports disagree with each other is broken whatever the
document says. **What the key does not do**, in #117's own words: it is "not an
authentication token for the document, only for a marker echoed out of author text." A
pull-request author can type a fixed marker string into their own diff; they cannot
know the run nonce, so a forged marker fails against the document. A compromised
runner emits a self-consistent document with its own nonce, and this stage cannot tell.
That residual is real, it is bounded, and no prose here or anywhere else may describe
the published review as unforgeable.

**`adjudication.total_refutation` needs no dedicated trigger of its own.** #118's
`stages` entry for `adjudication` is `"complete"` only when every finding received a
verdict, the nonce was established, AND the run was not a total refutation — so a
totally-refuted run's `adjudication` stage entry is never `"complete"`, and condition
(1) already bannerises it. This is #118's own stated design (`ADJUDICATION.md`),
"that existing machinery is what STEP 6's total-refutation flag uses, rather than
inventing a second signal #119 would have to learn" — not an inference made here.

---

## The clean case still posts

Every stage complete and every report `outcome: clean` renders an explicit body: the
head SHA (in the header line every body carries), the name of every dimension the
manifest ran, and a sentence stating no confirmed findings were produced. Silence is
indistinguishable from a crashed agent, so this path posts on exactly the same code
path as the findings path. There is no early return in `main` that skips publication
for an empty result — that omission would go silent on precisely the pull requests
where the agent found nothing, which is this contract's own criterion stated in
reverse.

`outcome: clean` and an empty `findings` array are not the same input as `status:
complete` with no `outcome` at all — the second is condition (8) above, and renders
the incomplete banner, never the clean sentence.

---

## Both SHAs, and why the pair

The rendered body's header names the head SHA the review read AND the merge base it
was diffed against. Findings are anchored to new-side line numbers in the merge-base
diff, so a reader given only the head SHA cannot reconstruct which diff a `path:line`
refers to — a force-push that rewrites the base makes the same head SHA mean a
different diff, and the merge base is what distinguishes them. "A review is valid only
for the commit it read" means the commit PAIR, not the head alone.

---

## Rendering untrusted text — two different rules for two different kinds

**Evidence** — pull-request-authored text quoted verbatim, on every containment
finding and on any dimension finding carrying an `entry_point` — is rendered through
`contain.escape` and inside a fence sized by `review.fence_for`, both imported and
never reimplemented. No fence in this renderer is ever a fixed three backticks:
attacker text containing a long backtick run would close a fixed fence early and spill
the remainder of the review out of its code block, in the one place a human is reading.
Escaping means a published excerpt shows a doubled tilde where the author wrote one —
`contain.escape` doubles every literal `~` as well as neutralising the envelope token —
so a reader must not mistake the renderer's own escape for the author's original text.

**`defect` and `failure`** — model-authored prose describing a finding, not
author-supplied text — are NOT passed through `contain.escape`. Only the envelope
token (`contain.TOKEN` → `contain.ESC_TOKEN`) is neutralised in them. Measured, not
assumed: `contain.ESC` is a single tilde, and `~~text~~` is strikethrough in
GitHub-flavoured markdown. This fork's own subject matter is dotfile paths
(`~/.claude/...`), so escaping ordinary prose the same way evidence is escaped
would visibly corrupt the most likely findings in the one surface a human reads —
a single mention publishes a visible doubled tilde, and two home-relative paths in
one line publish with the passage between them struck through. What is worth
neutralising in model-authored prose is the envelope token re-entering the document,
not a character the model had every reason to type honestly.

A finding whose anchor and fields disagree, or whose `severity` is outside the ladder,
renders under an explicit "malformed finding" heading with its raw record — serialised,
then given the SAME escape-and-fence treatment as evidence, because it is the path a
record takes precisely because its fields did not match the contract, so it is the
last place to assume anything is well-formed. A finding is never silently dropped for
being malformed: a finding discarded by the publisher is a finding the reviewer
believes it reported.

---

## Duplicates collapse to their survivor

A finding named as a `duplicates` entry in any `adjudication.duplicate_groups` group is
removed from the rendered list; the group's `survivor` finding gains one line naming
how many dimensions independently reported it. Nothing in `reports[].findings` is ever
removed by adjudication itself — `duplicate_of` and `duplicate_groups` mark a
duplicate, they do not delete one — so this is a rendering choice, not a data change. A
group naming a `survivor` finding_id absent from the current render pass renders its
real duplicate under "malformed finding" rather than dropping it from the count or the
output silently.

`adjudication` is an EIGHTH, OPTIONAL key on the merged document, exactly as
`containment` was before #117 settled it: a caller with no adjudication stage omits the
key, and `duplicate_groups` defaults to empty rather than the key being required.

---

## The verdict word, never the reasoning

A finding carrying a `verdict` (`CONFIRMED` | `REFUTED` | `UNPROVEN`) renders that word
beside it — not optional, per `ADJUDICATION.md`'s own words: "a REFUTED finding is
still published, with its verdict beside it." `verdict_evidence` — the adjudicator's
free-text reasoning — is never rendered anywhere. It carries no structural guard
against approval-shaped content: #118's own `FALSIFIABILITY.md` (Pair 3) recorded a
live instance of a judge producing exactly that ("the rest of the diff is fine to merge
once that's done") once its escalate-only clause was removed, and rendering that text
would publish it. A finding with no `verdict` key at all — a document that never
reached adjudication — renders with none of the three words adjacent to it: absence of
the key is not the same fact as a verdict of "unproven," and must not be dressed as
one.

`severity` is #118's re-rated value (same field name #117 used); `reported_severity`
— the dimension's original rating, preserved verbatim — is not currently rendered
anywhere. Nothing in this issue's own done-criteria asks for it.

---

## The `containment` block this stage consumes

A top-level sibling of `reports`, present on every run per #117's settled contract —
"never a missing key." Two keys, unrenamed from `contain.Finding`:

- `findings` — `[{severity, kind, entry_point, evidence}]`
- `states` — a map of all SEVEN entry points (`pr_title`, `pr_body`, `pr_diff`,
  `pr_issue_comments`, `pr_review_comments`, `pr_review_bodies`, `linked_issue`) to
  `fetch.Surface` state

There is no `unreadable` key. An earlier draft of this renderer accepted one; it was
removed once `states` alone was shown to carry the same fact, and passing it now raises
`TypeError`. `states` is what the incomplete banner's condition (10) actually reads —
`review.render_review` derives its own "Incomplete" line from the same map, so a
`containment` block that is present but names a thin `states` map (six real keys, one
typo) is the dangerous shape a bare presence check would let through.

A MISSING `containment` block is INCOMPLETE — never rendered as "no containment
findings," which is a positive claim this stage cannot make about a stage that never
ran.

---

## The credential and its controls

Publishing runs under `pull_request_target`, not `pull_request`, because this job
holds `pull-requests: write`. Under plain `pull_request`, a same-repository pull
request — no fork required — gets that same write-capable token while its own diff can
modify `publish.py` or `check_publish_scope.py`, the exact code the job then executes:
a pull request could rewrite either to submit an `APPROVE` under the bot's identity, a
hard violation of `launchpad/AGENTS.md` rule 1, "Draft everything. Approve nothing."
`pull_request_target` closes this the standard way: it grants the base repository's
token to every pull request, fork or not, but the checkout step MUST NEVER set `ref:`
toward the pull request's head — doing so recreates the exact vulnerability the
trigger change exists to close, now with a base-repository token instead of a fork's.
The only untrusted content this job ever reads is the seven-or-eight-key document
piped into `publish.py` on stdin — DATA, fetched over the API, never code checked out
and executed.

The fork skip is a JOB-LEVEL `if:` on a separate `guard` job's output, never a step
that exits 0. A step exiting 0 marks only that step successful; every later step in the
same job still runs regardless, so the publisher and the scope control would execute
under a fork PR's token anyway. `needs: guard` plus `if: needs.guard.outputs.is-fork
!= 'true'` skips the whole job at once, visibly, in the job list.

Two controls prove this contract rather than merely stating it: `check_publish_scope.py`
(the live credential, below) and `check_publish_single.py` (ten offline behavioural
assertions over recorded fixtures — the single-review invariant, pagination, severity
ordering, the incomplete banner, fencing, the hard-fail-no-fallback PUT, the clean path
actually posting, and the foreign-marker refusal keying on count rather than on a `None`
first element — each with a mutation proof that it can fail). Both are registered in
`run_controls.py`.

**`check_publish_scope.py`** is three assertions:

- **STATIC** parses the workflow YAML: permissions equal exactly `{contents: read,
  pull-requests: write}`, the trigger is `pull_request_target`, and no checkout step
  overrides `ref:` toward the pull request's head. Runs anywhere, needs no token.
- **LIVE** attempts one contents write (create a ref, named from `GITHUB_RUN_ID`) under
  the workflow's own token and asserts HTTP 403. Any other outcome — including an
  unexpected success, which also deletes the ref it made — is FAIL.
- **IDENTITY** compares the login `--as` was configured with against
  `post_or_update`'s own `author_login` (`user.login` off the live POST/PUT response) —
  the only place the live identity exists. Crosses the step boundary via
  `$GITHUB_OUTPUT`: `publish.py` writes `author_login` there, and the workflow passes
  `steps.publish.outputs.author_login` into the scope-check step's environment.

**Both LIVE and IDENTITY PASS only from the publish workflow, and SKIP everywhere
else** — checked against `GITHUB_WORKFLOW`, never against "a token exists." #120's
read-only containment-controls workflow also carries a real token, with `contents:
read`; a ref-create under THAT token 403s too, so a guard keyed only on token presence
would report PASS having measured the wrong credential entirely. A control that passes
under the wrong token is not a weak control; it is a false one. Registering this
control in `run_controls.py` (invoked by both workflows) does not make that runner its
home — a PASS from the read-only runner is not evidence about the publish token.

`publish.py` OWNS the marker constant; `publish_render.py` RECEIVES it as an argument
and imports nothing from `publish.py` — the reverse import would form a cycle the
moment `publish.py` gained a `main`.

---

## Cross-references

- [CONTAINMENT.md](CONTAINMENT.md) § Contract for later stages names this stage's row:
  `review.render_review(findings, states)`, with `states` taken from `render()`'s own
  return, never re-derived; never publish evidence in raw form.
- [FINDINGS.md](FINDINGS.md) is #117's settled contract for the finding record, the
  report envelope, and the merged document this stage's `reports` and `containment`
  arguments are read from verbatim.
- [ADJUDICATION.md](ADJUDICATION.md) is #118's settled contract for the six added
  finding fields, the nine-key `adjudication` block, and the `stages` manifest entry
  this stage's incomplete condition (1) already covers without a dedicated
  total-refutation trigger.
