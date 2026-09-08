# The Professor's default sensitive-data ruleset

Used by `screen-sensitive` when a target repo doesn't define its own at
`.professor/sensitive-patterns.md`. Each category names what it matches, why it's in
this list, and its disposition — **redact** (replace the span, keep the page) or
**block** (refuse the write entirely). See `screen-sensitive/SKILL.md` for how a
result in either disposition gets handled, and
`launchpad/Research/the-professor-skill-suite-redesign.md` §9 for the status of the
script that applies this mechanically. **That script now exists for every
[pattern] category below:** `tools/professor.py screen-content` implements them
directly, no model call involved. The one **[dispatch]** category (member/roster
names) still isn't pattern-matched — see `screen-sensitive/SKILL.md` for how that
one is handled instead. This file remains the spec `screen-content` implements for
every [pattern] category, not a placeholder screened by hand while the script
doesn't exist yet.

**Two dispositions of a different kind, added 2026-09-05 after a review found every
category below being described as equally "mechanical" wasn't accurate.** Every
category is marked **[pattern]** or **[dispatch]**:

- **[pattern]** categories are genuinely regex/entropy/structure checks — a fixed
  prefix, a PEM marker, a URL shape, a Shannon-entropy threshold next to a suspicious
  word, an IP range. `tools/professor.py screen-content` implements these directly, no
  model call involved, exactly as `screen-sensitive/SKILL.md` describes.
- **[dispatch]** categories require recognizing what a name or value is *being used
  for* in its sentence — not a shape a regex can test. These are checked the same way
  `verify-claims` checks a claim: a fresh, isolated, mandatory model dispatch (reusing
  `$PROFESSOR_VERIFIER_CMD`, §3/§6.7 — no separate mechanism invented for this), never
  a plain-text pattern match pretending to be one. Still unskippable — **disposition
  is `redact`, not block, matching the roster-names row's own table entry below**
  (corrected 2026-09-05, this line previously said "blocking" and contradicted the
  table it's introducing) — the dispatch, not the mechanism or the disposition, is
  what differs from the rest of this list.

This list's shape deliberately mirrors `the-professor-design.md`'s own "What stays out" table
(under "How the next agent gets built") — *"Secrets, tokens, credentials, private
host paths and member rosters"* — because the reasoning is the same reasoning, one
level down: **git history outlives every later edit, and a repository outlives its
current visibility.** A committed secret is disclosed to everyone who ever gets
access, and no deletion undoes that. That's true of a target repo's docs library
exactly as it's true of this pack itself.

## Block (write refused, no redaction shipped)

| Category | Shape | Why block, not redact |
|---|---|---|
| **[pattern]** API keys / access tokens | Provider-recognizable prefixes (e.g. `sk-`, `AKIA`, `ghp_`, `xox[bp]-`) or a high-entropy opaque string adjacent to words like `key`/`token`/`secret` | A redaction placeholder in the page's git history still proves *something* lived there and roughly where — not worth it when the real value could instead just not be drafted yet |
| **[pattern]** Private keys / certificates | `-----BEGIN ... PRIVATE KEY-----` or equivalent PEM/OpenSSH markers | Same reasoning, more severe — a private key fragment is never safe to leave any trace of |
| **[pattern]** Passwords / connection strings with embedded credentials | `://user:password@host`, or a literal assigned to a variable named like `password`/`passwd` | The credential is live data, not descriptive text about a system |
| **[pattern]** Live webhook/callback URLs with embedded tokens | A URL whose query string or path segment is itself an auth token | Same class as an API key, just URL-shaped |

## Redact (span replaced with `[REDACTED: <category>]`, page still ships)

| Category | Shape | Why redact, not block |
|---|---|---|
| **[pattern]** Email addresses | Standard email shape, outside a structurally-identifiable attribution context (a citation's `author` frontmatter field, or inside a `professor:section` provenance comment) — a structural check, not a semantic one: is this email inside one of those specific fields, yes or no | Useful to know a section references *a* contact; the specific address is the sensitive part, not the fact of a reference existing |
| **[pattern]** Internal hostnames / private IP ranges | `*.internal`, `10.x.x.x`/`172.16-31.x.x`/`192.168.x.x`, or a project's own known-internal domain suffix **— that suffix is target-specific and not knowable by this bundled default; a target with one configures it in its own `.professor/sensitive-patterns.md` override (§3), not by this list guessing it** | Context ("this calls an internal service") is worth keeping; the literal address is what shouldn't leave the private network's own boundary |
| **[dispatch]** Member/roster names in a non-attribution context | A personal name appearing as configuration data (an allowlist, a hardcoded reviewer list) rather than as a citation's author or a provenance record's contributor — **recognizing "used as access-control data" vs. "merely mentioned" is a semantic judgment about the name's role in its sentence, not a shape**, which is why this is the one category dispatched rather than pattern-matched | The mere presence of a name isn't sensitive — `provenance-log`'s own `updated_by` field is exactly that, deliberately not screened. What's flagged is a name used *as data* (who's allowed to do X), which is roster disclosure, not attribution |
| **[pattern]** Physical addresses | Standard street-address shape (number + street name + suffix, or a recognizable multi-line mailing-address block) | Same reasoning as email — the surrounding sentence's claim usually survives redaction intact |

## What this list deliberately excludes

- **Public API documentation values** — a documented public endpoint, a public
  package name, a public repo URL. This ruleset screens for what shouldn't be
  disclosed, not for everything that looks credential-shaped; a false-positive rate
  high enough to redact ordinary public identifiers would train reviewers to ignore
  the gate's output, which defeats it.
- **Test/example credentials clearly marked as such** (a `.env.example` value, a
  README's `sk-test-...` placeholder) — left to the eventual script's own
  false-positive tuning (§9), not decided here; noted so whoever builds that script
  doesn't have to rediscover this trade-off from scratch.
