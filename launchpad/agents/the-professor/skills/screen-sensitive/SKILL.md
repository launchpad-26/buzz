---
name: "screen-sensitive"
description: "Screen drafted or rewritten documentation content for secrets, credentials, PII, and other sensitive material before it reaches disk — the unskippable gate every write goes through, never a judgement call."
---

# Screening before any write

`draft-page` and `update-page` both call this as their last step before a write. It
is never optional and never skipped because a section "is just prose" — that
assumption is exactly how a secret ends up committed to a docs page, and per this
pack's own design principle (`the-professor-skill-suite-redesign.md` §2, carried from
the original design's §2): a fact that's silently wrong and mechanically checkable
belongs behind a tool the persona cannot decline to run, not behind judgement.

## 1. Run the screen

`<pack-root>` here means `$PROFESSOR_PACK_ROOT` (Open Questions item 6's decision,
`draft-page` §0 has the fail-loud requirement) — already confirmed set by whichever
skill called this one, since this skill is never invoked standalone, only as
`draft-page`/`update-page`'s last step. Run
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
accurate.** `tools/contract/sensitive-patterns.md` marks every category **[pattern]**
or **[dispatch]**. `screen-content` (above) covers every **[pattern]** category
directly. The one **[dispatch]** category (member/roster names used as
access-control data, as opposed to attribution) needs recognizing what a name is
*being used for* in its sentence — not a shape `screen-content`'s pattern matching
can test — so it is checked the same way `verify-claims` checks a claim: a fresh,
isolated, mandatory dispatch to `$PROFESSOR_VERIFIER_CMD` (§3/§6.7), run as an
additional step alongside `screen-content`, not folded into it. Still local (no
GitHub API call), still unskippable, still blocking on a finding — the dispatch
mechanism, not the severity, is what differs from the rest of this gate.

**Until that subcommand exists, this whole skill is a Phase 1 dependency, not a
standing design choice.** A manual pass — reading `tools/contract/sensitive-patterns.md`
(or the target's override, same resolution order) and checking the scratch file's
content against every category it lists by hand — is what happens *before* Phase 1
(§9) ships `screen-content`, so that a real dry run (Phase 2) isn't blocked on the
subcommand existing first. It is advisory, not the mechanical, undecideable-by-the-
persona gate this skill's whole premise requires (§2's own test: "is being wrong
silent and mechanically checkable" only holds once a script, not a model's own
judgement, is doing the checking). **Do not treat a manual pass as satisfying this
gate once `screen-content` exists** — from that point on, running it by hand instead
of calling the real subcommand is exactly the "skipping the step because the tooling
is incomplete" failure mode this design exists to prevent, applied to tooling that
isn't incomplete anymore.

## 2. Act on the result

- **`pass`** — nothing flagged. The write proceeds unchanged.
- **`redact`** — one or more spans matched a category the ruleset marks as
  redact-not-block (e.g. an internal hostname that's useful context but shouldn't be
  published verbatim). Replace each flagged span with `[REDACTED: <category>]`, and
  log the redaction — which category, which section, never the redacted value itself
  — so a reviewer can see what was removed without the removed content ever having
  been written anywhere, including a log.
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

- [ ] `screen-content` ran with `--target` set, against the scratch file — this skill
      did not separately read and interpret the ruleset itself
- [ ] Every category in the resolved ruleset was actually checked against the draft —
      not a subset "close enough" pass
- [ ] `redact` results replaced the exact flagged span, logged by category only, never
      by value
- [ ] `block` results stopped the write entirely and reported category + location only
- [ ] No flagged span was copied anywhere beyond the scratch file it arrived in — no
      log, no error message, no retry that reuses the same content unredacted
