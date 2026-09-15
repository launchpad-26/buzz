---
name: "screen-sensitive"
description: "Screen drafted or rewritten documentation content for secrets, credentials, PII, and other sensitive material before it reaches disk — the unskippable gate every write goes through, never a judgement call. Use when draft-page or update-page has written a draft to a scratch file and is about to publish it — every Professor write, no exceptions, including a draft that is only prose. Not for screening files this pack did not draft, checking whether a claim's citation supports it (verify-claims), or contract compliance (the check-page subcommand of tools/professor.py, which draft-page and update-page run themselves)."
---

# Screening before any write

`draft-page` and `update-page` both call this as their last step before a write. It
is never optional and never skipped because a section "is just prose" — that
assumption is exactly how a secret ends up committed to a docs page, and per this
pack's own design principle (`the-professor-skill-suite-redesign.md` §2, carried from
the original design's §2): a fact that's silently wrong and mechanically checkable
belongs behind a tool the persona cannot decline to run, not behind judgement.

## 1. Run the screen

`<pack-root>` here means `$PROFESSOR_PACK_ROOT` (Open Questions item 6's decision).
**Confirm it is set before doing anything else in this skill. If it is unset, stop
immediately and fail loud with `PROFESSOR_PACK_ROOT is not set; see this pack's README
for how to configure it`** — the same message and the same rule `draft-page` §0 owns.

Do not assume a caller already checked it. This skill previously waived the check on the
premise that it "is never invoked standalone, only as `draft-page`/`update-page`'s last
step". That premise stopped being true when the seven skills were registered at the repo
root by symlink (#1397): any session can now load this skill directly, and its own
description — screening content for secrets before it reaches disk — invites exactly
that. Unset, `<pack-root>/tools/professor.py` expands to `/tools/professor.py`, which
does not exist, and that failure is indistinguishable from the subcommand not being
built. On a secrets gate, a run that reports clean without having screened anything is
the one outcome that must not be reachable.

Then run
`<pack-root>/tools/professor.py screen-content <scratch-file> --target
<target-root>` via Bash against the scratch file `draft-page`/`update-page` already
wrote (their own procedures cover why it's a scratch file, never the real target
path, at this point). Pass `--target` explicitly — the subcommand resolves the
ruleset itself, same two-step order as the contract (`.professor/sensitive-patterns.md`
in the target, else `tools/contract/sensitive-patterns.md` bundled in this pack), so
this skill does not separately read and interpret the ruleset text; that would be two
places doing the same resolution and risking disagreement between them.

This is local by construction — a screening gate has no cross-repo dimension, so
unlike the citation subcommands `draft-page`/`update-page` reach for, this one never
touches the network (`launchpad/Research/the-professor-skill-suite-redesign.md` §9 —
the subcommand's actual pattern-matching logic is deferred follow-up work; the
ruleset file scaffolded in this pack is the spec it implements).

**One category in the ruleset is not pattern-matched — added 2026-09-05, after a
review found this skill's own "mechanical for everything" framing wasn't quite
accurate, and its disposition wasn't defined precisely enough to actually run.**
`tools/contract/sensitive-patterns.md` marks every category **[pattern]** or
**[dispatch]**. `screen-content` (above) covers every **[pattern]** category
directly. The one **[dispatch]** category (member/roster names used as
access-control data, as opposed to attribution) needs recognizing what a name is
*being used for* in its sentence — not a shape `screen-content`'s pattern matching
can test.

**Which findings get dispatched.** `screen-content` marks every roster-names candidate
with an explicit requires-dispatch flag, and that flag — not the category name, not a
guess — is what this step acts on. Each such finding carries its `location` as a line
number **plus column offsets**: line-relative, measured in Unicode characters,
zero-based, end-exclusive. `match` stays `null`, as it does for every finding in this
gate; the offsets are coordinates, not content, which is exactly why they are safe to
carry when the matched text is not.

**Those offsets are the candidate's identity, and they travel with it.** Two names on
one line, or the same name twice in one sentence in different roles, produce findings
that are otherwise identical — so the offsets go into the dispatch input and the verdict
comes back against them. Without that, a verdict earned by a contributor's name can be
applied to an access-control entry sitting beside it, and the roster is silently
unprotected. That is the failure this whole mechanism exists to prevent, so it is not
optional bookkeeping.

**The protocol, run once per flagged candidate** (a plain name-shaped token — the pattern
side still does that detection; dispatch only decides *role*, it doesn't hunt for names
itself): run `$PROFESSOR_VERIFIER_CMD` as a subprocess, the same mechanism `verify-claims`
uses.

**Send the same four things `verify-claims` §2 requires**, for the same reason a real
dispatch proved on 2026-09-15: the task, the instruction to decide only from what it is
given, the response format and its three verdict literals, and the content itself — here,
the candidate's offsets, the name, and its containing sentence. A verifier sent only a
name and a sentence invents its own task and answers in a shape nothing can parse. As
there, prefer a verifier command without repository access; a verifier that can read the
target repo can substitute its own evidence for what it was shown.

**The response is matched whole, by `verify-claims` §2b's grammar**, with the verdict
literal below in place of that gate's three. Nothing is searched for inside a response.
It returns one of:

- **`ATTRIBUTION`** — the name is a citation's author or a provenance record's
  contributor. Not flagged at all; this is exactly the case
  `sensitive-patterns.md`'s own "why redact" column names as never sensitive. **This is
  the only verdict that removes protection, and only when the dispatch both completed
  and parsed cleanly for that exact candidate** — see the retention rule below.
- **`ROSTER_DATA`** — the name is being used as configuration/access-control data
  (an allowlist, a hardcoded reviewer list). **Disposition: `redact`** — matching
  `sensitive-patterns.md`'s own table (this category lives under "Redact," not
  "Block"). Corrected 2026-09-05: an earlier version of this text said "blocking,"
  contradicting the ruleset it's supposed to implement.
- **`AMBIGUOUS`** — the dispatch can't confidently tell. Treated as `ROSTER_DATA`
  (redact) — the same "when in doubt, the safer disposition" reasoning
  `sensitive-patterns.md`'s own block-vs-redact column already uses elsewhere on
  this list, applied to an uncertain verdict instead of an uncertain shape.

Still local (no GitHub API call), still unskippable, still folded into this
skill's own `pass`/`redact`/`block` outcome in step 2 below exactly like
`screen-content`'s findings — the dispatch mechanism, not the disposition or the
reporting shape, is what differs from the rest of this gate.

### The retention rule — stated as a default, not a list

**`screen-content` reports every roster-names candidate as `redact`, and that
disposition stands unless a dispatch takes it away.** Exactly one thing takes it away:
a dispatch that **completed and parsed cleanly** and returned `ATTRIBUTION` **for that
exact candidate**, identified by its offsets. Every other outcome — without exception,
including outcomes not imagined here — keeps the underlying `redact`, and keeps it
*inside* this skill's single outcome in step 2. Never reported separately, never set
aside as a special case, never dropped.

These are **instances** of that default, not its full extent:

- stdout that does not match the response grammar whole
- a parse failure of any kind, including an empty or truncated response
- a non-zero exit, whatever the stdout said
- a timeout, per `verify-claims` §2c's bound
- `ROSTER_DATA` or `AMBIGUOUS`, which are verdicts rather than failures but are not
  `ATTRIBUTION`
- a candidate that was never dispatched at all, for any reason

Writing this as a default rather than an enumeration is deliberate. **An enumeration is
a list of the failures someone thought of**, and the one nobody listed becomes the one
with no defined handling — which is how a finding ends up dropped. Stated this way, a new
failure mode is already covered the moment it exists.

**Why `redact` and not something weaker.** This is the same fail-closed correction §1a
below records for `target-ruleset-override`, and it is the resolution of issue #2110. An
earlier version of this skill returned `not-evaluated` for an undecided candidate — an
outcome step 2 defines no consumer action for, so a caller following this procedure
literally had nothing to do with it and could drop it silently, which is
indistinguishable from `pass` in effect. An undecided candidate therefore takes the
disposition the ruleset itself assigns an undecided one: `sensitive-patterns.md` lists
this category under Redact, and `AMBIGUOUS` above resolves to `redact` for exactly this
reason. **Over-redacting an attribution name is recoverable by a human reading the draft;
publishing an access-control roster is not.**

That floor also protects a consumer that never dispatches at all. Anything reading
`screen-content`'s JSON directly — CI, a script, the scheduled workflow — sees `redact`
and is safe without knowing this protocol exists.

**`screen-content` now exists** — Phase 1 shipped it (`tools/professor.py`, issue #2100,
PR #2106). There is therefore no manual-pass branch in this skill any more, and this
paragraph no longer describes an available option: a hand-read of
`tools/contract/sensitive-patterns.md` does **not** satisfy this gate. Running it by
hand instead of calling the real subcommand is exactly the "skipping the step because
the tooling is incomplete" failure mode this design exists to prevent, applied to
tooling that is no longer incomplete.

If the subcommand cannot be run — `$PROFESSOR_PACK_ROOT` unset (§1 fails loud on that),
the binary missing, or the call erroring — **stop and report the gate as unrunnable.
Never report `pass`.** An unrun gate and a passed gate are different outcomes, and only
one of them means the content was screened.

## 1a. A target-specific ruleset override this tool can't honour

**Added 2026-09-06, a fourth outcome alongside the three below** — `screen-content`
resolves the ruleset itself (step 1 above), in the same two-step order as the
contract: `.professor/sensitive-patterns.md` in the target, else the bundled
default. If a target-specific override exists, `screen-content` cannot actually
interpret its content — its pattern-matching categories are hardcoded Python, not
parsed from a markdown ruleset file at runtime. Rather than silently falling back
to screening against the bundled default as if nothing were overridden, it reports
an explicit `target-ruleset-override` finding with **disposition `block`**.

Treat this exactly like a `block` result in step 2 below: the write does not
proceed. This is deliberately fail-closed — an earlier version reported
`not_evaluated` here, an outcome this skill's procedure never defined a consumer
action for, and the nearest-sounding outcome by default reasoning was "pass", which
meant an overridden target's draft was effectively screened not at all. Resolve it
by removing the override, or by this tool gaining real support for custom rulesets
in a later phase — not by proceeding with the write anyway.

## 2. Act on the result

**One combined outcome, from both checks** — `screen-content`'s pattern findings and
step 1's roster-names candidates are merged into a single `pass`/`redact`/`block` result
for this skill, never reported or acted on separately; whichever category applies, apply
the discipline below. A candidate leaves step 1 in exactly one of two states: dropped,
because a clean dispatch returned `ATTRIBUTION` for it, or carrying `redact` — whether
that came from a `ROSTER_DATA`/`AMBIGUOUS` verdict or from the retention rule's default
after a failure. **Both states merge here; neither is reported on the side.** (A
target-ruleset-override result, step 1a above, is its own fourth outcome and is
always `block` — it does not merge with the pattern/dispatch findings the way
`redact` and `block` findings from those two checks do with each other.)

- **`pass`** — nothing flagged, by either check. The write proceeds unchanged.
- **`redact`** — one or more spans matched a category the ruleset marks as
  redact-not-block (e.g. an internal hostname that's useful context but shouldn't be
  published verbatim, or a name dispatch classified `ROSTER_DATA`/`AMBIGUOUS`).
  `screen-content` never hands back the flagged text itself — its `match` field is
  always `null`, for every disposition. Use each finding's `location` (which line, and
  for roster-names candidates the column offsets too — the only way to tell two
  candidates on one line apart) and `category` (which kind) to find the span in the
  draft file you already hold
  in your own context, and replace it there with `[REDACTED: <category>]`. Log the
  redaction — which category, which section, never the redacted value itself — so a
  reviewer can see what was removed without the removed content ever having been
  written anywhere, including a log.
- **`block`** — one or more spans matched a category the ruleset marks as
  block-not-redact (a live credential, a private key, anything where even a
  redaction-shaped placeholder in the page's history is a bad trade against just not
  writing the page yet). The write does not proceed. Report the finding — category
  and location, never the flagged content itself, same discipline as a redaction log
  — to whichever skill invoked you, in the same shape `check_page`'s `findings` list
  uses in the original design, so review has one consistent place to look regardless
  of which gate produced the finding.

**Never write a flagged span anywhere *else* while deciding what to do about it** —
not to a log, not into a tool call's arguments if that call's result might be cached
or logged upstream, and never into the real target path. This does not forbid the
scratch file the content already arrived in (step 1) — that file is the thing being
screened, its existence is how screening happens at all, and it gets discarded once
this gate runs regardless of outcome. What must never happen is a flagged span
surviving anywhere *beyond* that scratch file's lifetime: not copied into a log
entry, not left behind after a `block`, not quoted back in an error message.

## Summary checklist

- [ ] `$PROFESSOR_PACK_ROOT` confirmed set before anything else ran — failed loud with
      the specific message if not, never a generic error from a later step
- [ ] `screen-content` ran with `--target` set, against the scratch file — this skill
      did not separately read and interpret the ruleset itself
- [ ] If `screen-content` could not be run at all, the gate was reported **unrunnable**,
      never `pass` — an unrun gate and a passed gate are different outcomes
- [ ] Every category in the resolved ruleset was actually checked against the draft —
      not a subset "close enough" pass
- [ ] Every finding carrying the requires-dispatch flag was actually dispatched, one
      call per candidate, with its offsets in the input and the verdict returned
      against them — no candidate reached the outcome unresolved
- [ ] Protection was removed from a candidate **only** by a dispatch that completed and
      parsed cleanly and returned `ATTRIBUTION` for that exact candidate; every other
      outcome kept `redact` and stayed inside the combined result
- [ ] `redact` results replaced the exact flagged span, logged by category only, never
      by value
- [ ] `block` results stopped the write entirely and reported category + location only
- [ ] No flagged span was copied anywhere beyond the scratch file it arrived in — no
      log, no error message, no retry that reuses the same content unredacted
