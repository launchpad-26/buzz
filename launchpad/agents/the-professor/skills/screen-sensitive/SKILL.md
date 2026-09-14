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

**The protocol, run once per name `screen-content` flags as a candidate** (a plain
name-shaped token — the pattern side still does that detection; dispatch only
decides *role*, it doesn't hunt for names itself): run `$PROFESSOR_VERIFIER_CMD` as a
subprocess (same mechanism `verify-claims` uses, §6.7 — a fresh, isolated call),
fed only the name and its containing sentence, nothing else. It returns one of:

- **`ATTRIBUTION`** — the name is a citation's author or a provenance record's
  contributor. Not flagged at all; this is exactly the case
  `sensitive-patterns.md`'s own "why redact" column names as never sensitive.
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

**Interim behaviour until Phase 1b ships the dispatch — added 2026-09-09, issue
#2110.** The dispatch above does not exist yet. Until it does, `screen-content`
returns every roster-names candidate with disposition **`redact`** directly, and no
dispatch happens: treat those findings exactly like any other `redact` in step 2,
with no extra step and nothing to interpret.

This is deliberately the same fail-closed correction §1a below records for
`target-ruleset-override`. An earlier version returned `not-evaluated` here — an
outcome step 2 defines no consumer action for, so a caller following this procedure
literally had nothing to do with it and could drop it silently, which is
indistinguishable from `pass` in effect. An undecided candidate therefore takes the
disposition the ruleset itself assigns an undecided one: `sensitive-patterns.md`
lists this category under Redact, and the `AMBIGUOUS` verdict above already resolves
to `redact` for exactly this reason. Over-redacting an attribution name is
recoverable by a human reading the draft; publishing an access-control roster is not.

Once Phase 1b lands, `ATTRIBUTION` candidates stop being flagged at all and this
paragraph goes away — the interim rule is strictly more conservative than the
dispatch that replaces it, never less.

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
step 1's dispatch verdicts (`ROSTER_DATA`/`AMBIGUOUS`, both `redact`) are merged into
a single `pass`/`redact`/`block` result for this skill, never reported or acted on
separately; whichever category applies, apply the discipline below. (A
target-ruleset-override result, step 1a above, is its own fourth outcome and is
always `block` — it does not merge with the pattern/dispatch findings the way
`redact` and `block` findings from those two checks do with each other.)

- **`pass`** — nothing flagged, by either check. The write proceeds unchanged.
- **`redact`** — one or more spans matched a category the ruleset marks as
  redact-not-block (e.g. an internal hostname that's useful context but shouldn't be
  published verbatim, or a name dispatch classified `ROSTER_DATA`/`AMBIGUOUS`).
  `screen-content` never hands back the flagged text itself — its `match` field is
  always `null`, for every disposition. Use each finding's `location` (which line)
  and `category` (which kind) to find the span in the draft file you already hold
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
- [ ] `redact` results replaced the exact flagged span, logged by category only, never
      by value
- [ ] `block` results stopped the write entirely and reported category + location only
- [ ] No flagged span was copied anywhere beyond the scratch file it arrived in — no
      log, no error message, no retry that reuses the same content unredacted
