---
status: Accepted
date: 2026-09-11
issue: launchpad-26/buzz#2159
decided_in: agent session — no addressable comment exists; see Provenance
supersedes: none
---

# ADR-0063 — The review record is a hash chain plus an operator-held HMAC

## Decision

Review-queue-automation (RQA) makes its review record tamper-evident with a **hash chain over every
entry, plus an HMAC keyed by a secret the operator holds outside the state directory (the OS
keychain), verified by `explain`**. This is option **(b)** of
[`ADR-F`](../skills/review-queue-automation/architecture/adr-drafts/ADR-F.md), the architecture's
recommendation.

Specifics that are part of the decision:

- **The key is the operator's and never RQA's to write into the record.** RQA reads it (E-25); it
  never creates, rotates or logs it.
- **A missing key degrades, it never blocks.** An append with no key available succeeds and records
  itself as explicitly unkeyed; `verify` and `explain` then report that span as
  `unverifiable: no key` — never as a hash or HMAC break, and never as a stopped review.
- **Legacy `ledger_entries` rows are carried as an unattested segment** below the first chained
  entry, and are never presented as chained provenance (Non-goal 8).
- **Only P-12 writes the record.** A harness's self-reported identity is untrusted input that P-06
  attests into a sidecar and P-12 records; it is never an authoritative write of its own.

## Context

RQA-NFR-028 requires that an unauthorised creation or alteration of any provenance element is
detected and never accepted as authoritative. Security bullet 4 of #2006 scopes that to
tamper-evidence *within the operator's trust boundary* and explicitly does not defend against a
compromised operator machine. The record is a SQLite table on the operator's disk, so the question was
which mechanism makes it tamper-evident. Non-goal 4 leaves the mechanism to design, but two of the
three options place a **key-custody obligation on the operator**, which is an operational and security
consequence the maintainer owns.

The margin this decision buys over the cheaper option is narrow, and the draft says so: a plain hash
chain (a) already detects accidental corruption, truncation, reordering, and any edit by an actor who
does not recompute the chain. (b) adds only the recompute case — an actor with file access but not
keychain access. Because RQA itself must read the key on every append, **any process running as the
operator can read it too**, so the margin is real but thin. Option (c), signed entries with an
asymmetric key, buys third-party verifiability that no requirement asks for.

Affected part: **P-12** (record). Requirements: RQA-NFR-028, RQA-NFR-022, RQA-NFR-032.

## Consequences

- **Good.** It is the smallest mechanism meeting RQA-NFR-028's "detected and refused" for the threat
  the specification actually names — an actor on the operator's machine lacking the operator's
  authority — and no more.
- **Bad, stated plainly.** The operator now has **one key to keep**. Losing it makes old records
  *unverifiable* (they remain readable), and the protection it adds over a plain hash chain is thin
  for the reason above: a process running as the operator can read the key. Anyone relying on this
  for defence against a compromised operator machine is relying on something it explicitly does not
  provide.
- **Decomposition.** This ADR was **not** decomposition-blocking: E-13's contract (`append` →
  `Entry(seq, hash)` or `AppendFailed`) and P-12's ownership of `record_entries` are identical under
  all three options; only P-12's internals differ. #2072 could always cut the P-12 lane, and this
  ruling settles its internals.

## Provenance

**This outcome was written by an AI agent exercising `launchpad/AGENTS.md` §5 delegated authority on
behalf of @tucktuck101**, who ruled on all four RQA architecture ADRs (#2157, #2158, #2159, #2160) in
one instruction, verbatim:

> urgh just go with the recomendations, record the adr files we need and submit a pr for them as a batch.

**Deviation from `launchpad/decisions/README.md`, recorded here rather than below the conclusion it
qualifies:** that README requires the deciding human's instruction to be quoted verbatim *and the
comment where they said it to be linked*. **No such comment exists.** The instruction was given only
in an agent session, which §5 rule 2 states is not a record — "not addressable, not durable, and not
readable by whoever audits this later". Offered the choice between posting the instruction as a
comment first and proceeding without one, @tucktuck101 selected "I proceed now, quoting this session
verbatim", with the deviation disclosed in every record and in the pull request. An auditor therefore
cannot reach the original instruction; this quotation is its only surviving form.

**A second caveat belongs here, at the decision, not below it:** the draft explicitly asked the
maintainer to weigh (a) against (b) *knowing the margin between them is thin*, and the ruling was a
blanket "go with the recommendations" across four ADRs rather than a response to that specific
trade-off. The recommendation is followed as instructed; whether the operator wants the key-custody
obligation for that margin is a question this record answers by default rather than by deliberation,
and it is cheap to revisit — only P-12's internals change.

The argument is on [#2159](https://github.com/launchpad-26/buzz/issues/2159) and in
[`ADR-F`](../skills/review-queue-automation/architecture/adr-drafts/ADR-F.md).
