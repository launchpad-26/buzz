# ADR-F — Provenance integrity mechanism for the review record

**Status:** decided 2026-09-11 — recommendation (b) accepted; recorded as [ADR-0063](../../../../decisions/ADR-0063-rqa-record-provenance-integrity.md), which closes [issue #2159](https://github.com/launchpad-26/buzz/issues/2159). This draft is retained as the architecture's rationale, not as an open question.
**Parent:** [#2006](https://github.com/launchpad-26/buzz/issues/2006) · **Raised by:** #2071 architecture · **Decomposition-blocking:** **not blocking**
**Parts affected:** P-12 · **Requirements:** RQA-NFR-028, RQA-NFR-022, RQA-NFR-032

## Question

RQA-NFR-028 requires that an unauthorised creation or alteration of any provenance element is detected
and never accepted as authoritative; Security bullet 4 scopes this to tamper-evidence *within the
operator's trust boundary* and explicitly does not defend against a compromised operator machine. The
record is a SQLite table on the operator's disk. What mechanism makes it tamper-evident?

## Why the architecture cannot settle it alone

The choice sets a security posture and, for two of the options, a key-custody obligation on the
operator — decisions the specification (Non-goal 4) leaves to design but which carry operational and
security consequences the maintainer owns.

## Options

| | option | detects | consequence |
|---|---|---|---|
| (a) | Plain hash chain: each entry hashes its predecessor. | Accidental corruption, reordering, and edits by anyone who does not recompute the chain. **Not** tail truncation: `verify` walks the rows present and returns `ok=True` on a complete walk (`P-12-record.md` §3.2), so a deleted tail leaves a clean-verifying prefix; (b) inherits the same blind spot. | No key. An actor with write access to the file who also recomputes the chain is not detected. |
| (b) | Hash chain **plus** an HMAC over the chain head with a key held outside the state directory (OS keychain), verified by `explain`. | Everything (a) detects, plus recomputation by an actor with file access but not keychain access. | One key the operator must keep; loss of the key makes old records unverifiable (still readable). |
| (c) | Signed entries with a per-installation asymmetric key. | As (b), plus third-party verifiability. | Key custody as (b); more machinery for a property no requirement asks for (nothing outside the operator machine verifies). |

## Recommendation — (b)

It is the smallest mechanism that meets RQA-NFR-028's "detected and refused" for the threat the
specification names — an actor on the operator's machine lacking the operator's authority — and no
more. (a) detects most of the named threat — any alteration by an actor who does not also recompute the chain — and (b) adds only the recompute case for an actor with file access but no keychain access, at the cost of one operator-held key; since RQA itself must read that key on every append, any process running as the operator can read it too, so the margin over (a) is real but thin. (c) buys a property nothing requires. The maintainer should weigh (a) against (b) knowing that margin is the whole difference. The key is the operator's and
never RQA's to write into the record. Legacy `ledger_entries` rows are carried as an unattested segment
below the first chained entry (Non-goal 8).

## Why not blocking

E-13's contract (`append` → `Entry(seq, hash)` or `AppendFailed`) and P-12's ownership of
`record_entries` are the same under all three options; only P-12's internals differ.
