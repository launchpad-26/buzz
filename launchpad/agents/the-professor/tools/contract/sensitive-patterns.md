# The Professor's default sensitive-data ruleset

Used by `screen-sensitive` when a target repo doesn't define its own at
`.professor/sensitive-patterns.md`. Each category names what it matches, why it's in
this list, and its disposition — **redact** (replace the span, keep the page) or
**block** (refuse the write entirely). See `screen-sensitive/SKILL.md` for how a
result in either disposition gets handled, and
`launchpad/Research/the-professor-skill-suite-redesign.md` §9 for the status of the
script that will eventually apply this mechanically (not yet built — screened by hand
against this list until then, per that skill's own instruction, not skipped).

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
| API keys / access tokens | Provider-recognizable prefixes (e.g. `sk-`, `AKIA`, `ghp_`, `xox[bp]-`) or a high-entropy opaque string adjacent to words like `key`/`token`/`secret` | A redaction placeholder in the page's git history still proves *something* lived there and roughly where — not worth it when the real value could instead just not be drafted yet |
| Private keys / certificates | `-----BEGIN ... PRIVATE KEY-----` or equivalent PEM/OpenSSH markers | Same reasoning, more severe — a private key fragment is never safe to leave any trace of |
| Passwords / connection strings with embedded credentials | `://user:password@host`, or a literal assigned to a variable named like `password`/`passwd` | The credential is live data, not descriptive text about a system |
| Live webhook/callback URLs with embedded tokens | A URL whose query string or path segment is itself an auth token | Same class as an API key, just URL-shaped |

## Redact (span replaced with `[REDACTED: <category>]`, page still ships)

| Category | Shape | Why redact, not block |
|---|---|---|
| Email addresses | Standard email shape, outside of a `git blame`-style attribution context the contract's own provenance already covers | Useful to know a section references *a* contact; the specific address is the sensitive part, not the fact of a reference existing |
| Internal hostnames / private IP ranges | `*.internal`, `10.x.x.x`/`172.16-31.x.x`/`192.168.x.x`, or a project's own known-internal domain suffix | Context ("this calls an internal service") is worth keeping; the literal address is what shouldn't leave the private network's own boundary |
| Member/roster names in a non-attribution context | A personal name appearing as configuration data (an allowlist, a hardcoded reviewer list) rather than as a citation's author or a provenance record's contributor | The mere presence of a name isn't sensitive — `provenance-log`'s own `updated_by` field is exactly that, deliberately not screened. What's flagged is a name used *as data* (who's allowed to do X), which is roster disclosure, not attribution |
| Physical addresses | Standard street-address shape | Same reasoning as email — the surrounding sentence's claim usually survives redaction intact |

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
