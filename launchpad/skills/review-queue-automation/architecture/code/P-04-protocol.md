# P-04 Protocol — code-level contract

This is the implementation contract for one part of the design in
[`../architecture.md`](../architecture.md). An agent implementing P-04 builds exactly what is here;
an agent implementing a neighbour calls exactly what is here. Anything not stated is the implementer's
choice, provided the stated shape, behaviour and tests hold. Contract ids (`E-NN`) and record names
are those of [`../components.md`](../components.md) §6 and [`../container.md`](../container.md) §5.

**Responsibility, in one sentence.** Be the one published definition of what a review is — its
obligations, its finding categories, its seven evidence states, and its wire format — and answer,
for one `verdict.json` at a time, *does this conform, and is it internally coherent?*

**Depends on.** No ADR. None of ADR-D/E/F/G bind this part's behaviour: D is P-02's verdict-authority
branch, E is P-08's credential, F is P-12's record integrity, G is P-10's remediation-form question.
Issue [#2064](https://github.com/launchpad-26/buzz/issues/2064) is where the published artefact
(schema plus prose) is filed as a repo-wide policy/contract document — RQA-FR-001's ADR field, not a
decomposition-blocking ADR.

## 1. Modules

```
rqa/protocol/
  __init__.py         re-exports: validate, Valid, Invalid, ProtocolError,
                       Location, Category, MECHANICAL_GROUP, SUBSTANTIVE_GROUP, EvidenceState,
                       Obligation, Remedy, Finding, InjectionAttempt, HarnessIdentity, Verdict,
                       PROTOCOL_VERSION, protocol_hash, PROBE_MARKER, envelope, extract
  types.py            implements the P-04-owned shared types exactly as CONTRACTS.md §2 defines them
  paths.py            matches(): the sole PathGlob matcher in RQA
  fence.py            strip_fence(): markdown-fence normalisation (U-VERDICT-01, kept)
  schema.py           structural validation against schema/verdict-<version>.json
  contradictions.py   the semantic-coherence predicate list (U-VERDICT-02, reworked)
  validate.py         validate(): the one entry point (E-08)
  version.py          PROTOCOL_VERSION, schema_path(), protocol_hash()
  envelope.py         the nonce-envelope grammar: envelope(), extract()
  interaction.py      PROBE_MARKER and the probe-invocation contract note (E-19/E-24)
  schema/
    verdict-1.json    the published JSON Schema — §2 reproduces it verbatim
  PROTOCOL.md          the published prose companion: review scope, the two category
                       groups, the seven evidence states and what each means, blocking-
                       condition semantics, review-completion and final-disposition
                       semantics, and the interaction contract (E-19/E-24). Filed under
                       #2064 alongside the schema; not reproduced here because it is prose,
                       not code — this file fixes only what it must say, in §7 and §9.
```

Other parts import protocol types only through `rqa.protocol.__init__`, except for the deliberately
qualified `rqa.protocol.paths.matches` import mandated in §2. No module in `rqa.protocol` imports
from another RQA part. P-06 alone calls `validate()` through E-08; every part that needs `Location`,
`Category`, `EvidenceState`, `Obligation`, `Finding`, `HarnessIdentity`, `Verdict`,
`PROTOCOL_VERSION`, `PROBE_MARKER`, `envelope`, or `extract` imports the shared type or pure function
directly. `protocol_hash()` is likewise a read of a packaged static artefact, not an E-NN call.

## 2. Shared protocol types, wire schema, and paths

`EvidenceState`, `Category`, both category groups, `Location`, `Remedy`, `Finding`,
`InjectionAttempt`, `HarnessIdentity`, `Verdict`, `Obligation`, `Valid` and `Invalid` are the
P-04-owned shared types defined only in [`CONTRACTS.md`](CONTRACTS.md) §2. `types.py` implements
those exact frozen types; this contract does not redefine them. `Finding.categories` is non-empty,
`extra_tags` is the separate open vocabulary, `remedy` is exact or absent, and
`behaviour_changing` is only the reviewer's nullable assertion.

**PathGlob and the sole matcher.** `Obligation.paths` contains `PathGlob` patterns, and a file is in
scope when `rqa.protocol.paths.matches(path, pattern)` returns `True` for at least one pattern. An
empty `Obligation.paths` remains in scope for every file; callers must implement that policy outside
the matcher. `matches` has the shared signature from `CONTRACTS.md` §2:

```python
def matches(path: str, pattern: str) -> bool: ...
```

```python
class PathGlobError(Exception):
    """A path or pattern is outside the normalized PathGlob grammar."""
```

It is the **only** path matcher in RQA. P-03, P-06, P-10, and P-13 import and call
`rqa.protocol.paths.matches`; they MUST NOT use `fnmatch`, `PurePath.match`, a regex matcher, or
their own glob implementation.

`paths.py` validates both inputs as normalized repository-relative paths before matching. A path or
pattern that is empty, absolute, begins `./`, contains `\`, an empty segment, `.` or `..`, or has
`**` other than as a complete segment raises `PathGlobError`; no invalid-input branch returns a
plausible Boolean. For valid input, split on `/` and match segments recursively: ordinary segments
support `*` for any run of non-`/` characters and `?` for exactly one non-`/` character; a `**`
segment matches zero or more complete segments. Matching is anchored at the repository root,
case-sensitive, and treats a leading `.` as an ordinary character. These are the grammar and
semantics in `CONTRACTS.md` §2, not gitignore semantics.

| Vector | `path` | `pattern` | Result |
|---|---|---|---|
| root | `README.md` | `README.md` | `True` |
| nested | `src/a/main.py` | `src/*/main.py` | `True` |
| `*` does not cross a separator | `src/a/main.py` | `src/*.py` | `False` |
| zero-segment `**` | `src/main.py` | `src/**/main.py` | `True` |
| nested `**` | `src/a/b/main.py` | `src/**/main.py` | `True` |
| dotfile | `.github/workflows/ci.yml` | `.github/**/*.yml` | `True` |
| question mark | `src/a.py` | `src/?.py` | `True` |
| question mark does not cross a separator | `src/a/b.py` | `src/?.py` | `False` |
| separator and case | `src/main.py` | `SRC/main.py` | `False` |
| invalid pattern | `src/main.py` | `/src/**/*.py` | raises `PathGlobError` |

**Wire schema (`schema/verdict-1.json`).** What `validate()` (§3) checks a payload against,
reproduced verbatim; it is the published artefact filed under #2064 alongside `PROTOCOL.md`.


```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://launchpad-26.example/rqa/protocol/schema/verdict-1.json",
  "type": "object",
  "additionalProperties": false,
  "required": ["protocol_version", "identity", "obligations", "findings",
               "injection_attempts"],
  "properties": {
    "protocol_version": { "type": "string", "minLength": 1 },
    "identity": {
      "type": "object",
      "additionalProperties": false,
      "required": ["harness", "model", "provider"],
      "properties": {
        "harness":  { "type": "string", "minLength": 1 },
        "model":    { "type": "string", "minLength": 1 },
        "provider": { "type": "string", "minLength": 1 }
      }
    },
    "obligations": {
      "type": "object",
      "minProperties": 1,
      "additionalProperties": {
        "type": "object",
        "additionalProperties": false,
        "required": ["state"],
        "properties": {
          "state": {
            "enum": ["verified", "not_verified", "unavailable", "contradictory",
                     "failed", "incomplete", "unknown"]
          },
          "findings": {
            "type": "array",
            "items": { "type": "string", "minLength": 1 }
          }
        }
      }
    },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "categories", "extra_tags", "location", "evidence", "severity",
                     "remedy", "behaviour_changing", "source_attempt"],
        "properties": {
          "id": { "type": "string", "minLength": 1 },
          "categories": {
            "type": "array",
            "minItems": 1,
            "uniqueItems": true,
            "items": {
              "enum": ["mechanical", "procedural", "creation_time",
                       "correctness", "security", "architectural", "evidence"]
            }
          },
          "extra_tags": {
            "type": "array",
            "uniqueItems": true,
            "items": { "type": "string" }
          },
          "location": {
            "type": "object",
            "additionalProperties": false,
            "required": ["path"],
            "properties": {
              "path": { "type": "string", "minLength": 1 },
              "line": { "type": ["integer", "null"], "minimum": 1 }
            }
          },
          "evidence": { "type": "string" },
          "severity": { "type": "string", "minLength": 1 },
          "remedy": {
            "type": ["object", "null"],
            "additionalProperties": false,
            "required": ["tool", "paths", "check"],
            "properties": {
              "tool": { "type": "string", "minLength": 1 },
              "paths": {
                "type": "array",
                "minItems": 1,
                "uniqueItems": true,
                "items": { "type": "string", "minLength": 1 }
              },
              "check": { "type": "string", "minLength": 1 }
            }
          },
          "behaviour_changing": { "type": ["boolean", "null"] },
          "source_attempt": { "type": "string" }
        }
      }
    },
    "injection_attempts": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["field", "span_hash", "reason"],
        "properties": {
          "field": { "type": "string", "minLength": 1 },
          "span_hash": { "type": "string", "pattern": "^[0-9a-f]{64}$" },
          "reason": { "type": "string", "minLength": 1 }
        }
      }
    }
  }
}
```

`source_attempt` is overwritten with the caller's `attempt_id`; the harness cannot know P-06's
identifier. Every object level uses `additionalProperties: false`. `injection_attempts` is
mandatory even when empty; each span is a lowercase SHA-256 hash, never untrusted text.

`obligations[*].findings` is a citation list — the ids of findings that are evidence for or against
that obligation, present only to let `validate()` detect the contradiction "obligation X is marked
`verified` but a finding cites it" (§3, §8). It is never carried into `Verdict.obligations`, which per
the shared contract is `Mapping[str, EvidenceState]` and nothing more; the citation is discarded once
validation completes.

## 3. Entry point — E-08

```python
def validate(*, path: Path, attempt_id: str) -> Valid | Invalid: ...
```

```python
class ProtocolError(Exception):
    """Programming error: blank attempt_id. Malformed verdicts return shared Invalid."""
```

`Valid` and `Invalid` are the shared types in `CONTRACTS.md` §2; P-04 does not create a second
definition.

**Behaviour, in order.** Steps 4–9 read the file's fence-normalised text; each collects every issue
of its kind rather than stopping at the first, so `Invalid.reasons` is the complete list a caller (or
a person debugging a harness) needs in one round trip. Every branch below returns `Valid` or
`Invalid`, or raises `ProtocolError`.

1. `attempt_id` is `""` or not a `str` → raise `ProtocolError`. This is P-06 calling the contract
   wrongly, not a property of the verdict.
2. `path` cannot be opened and read as UTF-8 (missing, a directory, permission error, any `OSError`,
   or invalid UTF-8) → `Invalid(("unreadable",))`. This is how a harness that exited 0 but wrote
   nothing, or wrote binary garbage, is rejected (flow step 7a).
3. The text, stripped of surrounding whitespace, is `""` → `Invalid(("empty_payload",))`.
4. Fence-normalise (`fence.strip_fence`, U-VERDICT-01, kept unchanged): if the *entire* stripped text
   is one markdown fence — an opening ```` ``` ```` (with an optional language tag) immediately
   followed by a newline, content, a newline, and a closing ```` ``` ```` with nothing else before or
   after — the fence markers are removed and the inner content (itself stripped) is used from here on.
   Anything else (prose around a fence, two fences, an unclosed fence) is left exactly as it was: it
   is never partially repaired, so it falls through to a decode failure at step 5, and no signal or
   field is ever read out of surrounding prose.
5. Parse the fence-normalised text as strict JSON (`json.loads`) → a `json.JSONDecodeError` →
   `Invalid(("malformed_json: " + the decoder's own message,))`.
6. The parsed value is not a JSON object (a list, a string, a number, `null`, `true`/`false`) →
   `Invalid(("not_an_object",))`.
7. Structural validation against `schema/verdict-<PROTOCOL_VERSION>.json` (`schema.py`): every
   `required` key is present at every level; every value's JSON type matches its `type`; every enum
   value is one of the schema's own list; `additionalProperties: false` is enforced at the document,
   `identity`, per-obligation, finding, `location`, and non-null `remedy` levels; and each nested
   shape is honoured. Any violation → one reason string per violation (for example `"missing required
   field: identity"`, `"findings[2]: unexpected property 'notes'"`, or
   `"findings[2].categories: must contain at least one item"`) →
   `Invalid(tuple(sorted(reasons)))`. This is where the closed category set, open tags, nullable
   remedy/assertion, seven evidence states, mandatory injection-attempt array and exact object shapes
   are enforced.
8. `data["protocol_version"] != PROTOCOL_VERSION` → `Invalid(("protocol_version_mismatch: got "
   + repr(data["protocol_version"]) + ", expected " + repr(PROTOCOL_VERSION),))`. Kept separate from
   step 7's type check because a harness targeting a retired or future protocol version is a distinct,
   nameable failure, not merely "the wrong type of string".
9. Contradiction detection (`contradictions.py`; U-VERDICT-02 reworked from the six `_CONTRADICTIONS`
   predicates onto the shared shape — the *pattern* of a list of independent predicates, every hit
   collected, is what is kept). Every predicate below that fires contributes one reason string; any
   hit → `Invalid(tuple(sorted(reasons)))`:
   - two or more findings share one `id` → `"duplicate_finding_id: <id>"`.
   - a finding's `evidence`, stripped, is `""` → `"empty_evidence: <finding id>"`. JSON Schema's
     `minLength` was deliberately left off `evidence` (§2) so a whitespace-only string, which passes
     `minLength: 1`, is still caught here.
   - an obligation's `state` is `"verified"` while its `findings` citation list is non-empty →
     `"obligation_verified_but_cited: <obligation id>"`.
   - an obligation cites a finding `id` that does not appear in the top-level `findings` array →
     `"unknown_finding_reference: <obligation id> -> <finding id>"`.
   - A non-null remedy path that is not a unique normalized exact repository-relative path, or that
     contains `*`, `?`, `[`, `]`, an absolute/empty/`.`/`..` segment or backslash →
     `"invalid_remedy_path: <finding id> -> <path>"`. Remedy paths are never PathGlob patterns.
   - An injection field is not `body`, `comment:<nonempty-id>`, or `diff:<normalized-exact-path>`,
     or its reason is blank after stripping → a corresponding `invalid_injection_attempt` reason.
   - A substantive-category finding with a non-null `remedy` remains `Valid`; P-07 rejects it as
     mechanical. P-04 does not classify findings.
10. Every check passed → construct and return `Valid(Verdict(...))`:
    - `obligations = {oid: EvidenceState(obj["state"]) for oid, obj in data["obligations"].items()}`
      (the citation lists are read in step 9 and discarded here).
    - `findings = tuple(Finding(id=f["id"],
      categories=frozenset(Category(category) for category in f["categories"]),
      extra_tags=frozenset(f["extra_tags"]),
      location=Location(f["location"]["path"], f["location"].get("line")), evidence=f["evidence"],
      severity=f["severity"],
      remedy=None if f["remedy"] is None else Remedy(tool=f["remedy"]["tool"],
      paths=tuple(f["remedy"]["paths"]), check=f["remedy"]["check"]),
      behaviour_changing=f["behaviour_changing"], source_attempt=attempt_id)
      for f in data["findings"])`.
    - `injection_attempts = tuple(InjectionAttempt(**item) for item in
      data["injection_attempts"])`.
    - `identity = HarnessIdentity(**data["identity"])`; `protocol_version` is copied exactly.

**Guarantees the caller may rely on.**
- Deterministic: the same bytes at `path` with the same `attempt_id` always produce the same `Valid`
  or `Invalid`.
- Never partially validates: `Invalid.reasons` is always the complete set found at whichever step
  first produced any (steps 7, 8 and 9 each collect fully before returning; a step 7 violation is
  never reported alongside a step 9 one, since step 9 never runs on structurally invalid data).
- Reads only the one file named by `path` and its own packaged schema; never the network, the
  environment, another job's files, or GitHub.
- Trusts nothing in `Verdict.identity`: it is passed through unchanged as the harness's self-reported
  account, for P-06 to attest against separately (E-19); `validate()` never uses it to decide
  `Valid`/`Invalid`.

## 4. Dependencies consumed

None. Per components.md §6, P-04 "Consumes: -": it calls no other part's entry point. `validate()`
takes every input as an argument (`path`, `attempt_id`) and reads only its own packaged schema file;
it never asks P-03 for a snapshot, never asks P-09 for anything, and never appends to the record
through P-12 (§6).

## 5. Store

None. No SQLite table (container.md §5 does not list one for P-04) and no file under the operator's
state directory. The published artefact — `schema/verdict-1.json` and `PROTOCOL.md` — is packaged
with the RQA source tree under version control, not written or read from `state/`; it changes only
when a maintainer publishes a new protocol version (a new `schema/verdict-<n>.json`, a bumped
`PROTOCOL_VERSION`, and updated prose), never at runtime. What ties one job to the version in force is
`Snapshot.protocol_hash` (P-03's field, computed by calling `version.protocol_hash()` against this
packaged file — §1) and `Verdict.protocol_version` (read back from the harness's own claim, checked
in §3 step 8).

## 6. Record entries written

None. Per components.md's E-13 row, "every part except P-04" appends to the record — P-04 is the one
named exception. The protocol's identity in a job's history is carried by other parts' entries: P-03
writes `protocol_hash` into `snapshots`, and P-06 writes `protocol_version` into the `attestation` it
records for each attempt (container.md §5). P-04 itself writes nothing, ever.

## 7. What P-04 does not do

- Does not decide a specific job's blocking outcome, corroboration, or disposition. It defines the
  evidence-state vocabulary, category shape, and structural/coherence rules a verdict must satisfy;
  P-07 applies them to one job's evidence (RQA-BR-004, contributed to by P-04, accountable to P-07).
  The published `PROTOCOL.md` cites `CheckConclusion`, `FAILING`, `UNSETTLED`, and `PASSING` from
  P-09's shared vocabulary (`CONTRACTS.md` §4) for check attribution and corroboration: `FAILING =
  {failure, timed_out, action_required}`, `UNSETTLED = {pending}`, and `PASSING` is the rest.
  Pending never corroborates, blocks, or is inherited; an obligation it bears on is `incomplete`.
- Does not compute obligation invalidation from a diff. It owns and implements `matches()` (§2);
  P-13 supplies the diff traversal and calls that matcher for every candidate path.
- Does not invoke a harness, build a bundle, or read PR facts, a diff, files or checks — P-06's job
  (E-07, E-19). It only validates the one file `path` names, after P-06 has already written it.
- Does not read `.rqa/config.json`, a snapshot, or any repository policy (§4).
- Does not write to the record or own a table (§5, §6).
- Does not retry an attempt or classify a failure into `TRANSIENT` / `PROVIDER_TERMINAL` /
  `CANDIDATE_TERMINAL` — P-06 does that, using `Invalid` as one of its inputs (flow step 7a: an
  `Invalid` verdict makes P-06 classify the attempt `CANDIDATE_TERMINAL`).
- Does not trust `HarnessIdentity`: it is recorded as self-reported and untrusted (§3); RQA's own
  account of what ran is P-06's attestation, a different fact.
- Does not enforce nonce-envelope use at runtime, and never touches PR content. `envelope()`/`extract()`
  (module `envelope.py`) are stateless string functions defining the grammar (U-RESILIENCE-15's
  envelope format); applying them to every PR-derived byte in the bundle is P-06's mechanism, under
  RQA-NFR-015, not something P-04 calls or checks.
- Does not support more than one protocol version being in force for a running sweep: `validate()`
  checks the payload against exactly `PROTOCOL_VERSION`, the version this build packages; there is no
  migration, negotiation, or multi-version dispatch. Publishing a new version is a new release, not a
  runtime choice.
- Has no successor to the binned author-triage schema. `schemas/author-triage.json` (U-VERDICT-03)
  is not carried forward: nothing in the frozen specification names an author-triage lane, and P-04
  defines exactly one verdict shape, for the one review protocol RQA-FR-001 requires. A future
  author-triage feature would need its own requirement and its own protocol artefact; none exists
  today.

## 8. Tests that prove it

Each is a unit test against a `verdict.json` fixture written to a temp path; no fakes are needed since
`validate()` takes no collaborator arguments.

| # | Given | Then |
|---|---|---|
| T1 | `attempt_id=""` | `ProtocolError` |
| T2 | `path` does not exist | `Invalid(("unreadable",))` |
| T3 | file content is `"   \n"` | `Invalid(("empty_payload",))` |
| T4 | a fully valid payload wrapped in a single ```` ```json ... ``` ```` fence | fence stripped; `Valid` |
| T5 | a valid payload with one sentence of prose before the fence | `Invalid`, reason names malformed/not-an-object — never repaired |
| T6 | a valid payload wrapped in two consecutive fences | `Invalid` — the anchored match fails, fence untouched, JSON decode fails |
| T7 | an unclosed fence | `Invalid(("malformed_json: ...",))` |
| T8 | `"not json{"` | `Invalid(("malformed_json: ...",))` |
| T9 | a JSON array instead of an object | `Invalid(("not_an_object",))` |
| T10 | payload missing top-level `identity` | `Invalid` names `"missing required field: identity"` |
| T11 | a finding object missing `categories` | `Invalid` names the missing `categories` field |
| T12 | a finding object carrying an extra key `"notes"` | `Invalid` names the unexpected property — proves finding `additionalProperties: false` |
| T13 | an obligation `state` is `"maybe"` | `Invalid` names the value as outside the seven evidence states |
| T14 | seven otherwise-identical payloads, one per `EvidenceState` value | all seven are `Valid` |
| T15 | `protocol_version: "999"` on an otherwise valid payload | `Invalid(("protocol_version_mismatch: ...",))` |
| T16 | a verified obligation cites existing finding `f1` | `Invalid(("obligation_verified_but_cited: <id>",))` |
| T17 | a finding has whitespace-only `evidence` | `Invalid(("empty_evidence: <id>",))` |
| T18 | two findings share `id: "f1"` | `Invalid(("duplicate_finding_id: f1",))` |
| T19 | an obligation cites missing finding `"ghost"` | `Invalid(("unknown_finding_reference: <id> -> ghost",))` |
| T20 | a finding has categories from both groups, tags, exact remedy, and `behaviour_changing: false` | `Valid`; exact frozen fields preserved; source attempt overwritten |
| T21 | empty or unknown category | `Invalid` |
| T22 | remedy path is absolute, contains traversal/backslash/glob syntax, duplicates another path, or is empty | `Invalid(("invalid_remedy_path: ...", ...))` |
| T23 | substantive-only finding has a syntactically exact remedy | `Valid`; classification remains P-07's responsibility |
| T24 | mandatory `injection_attempts: []` | `Valid`; omission is structurally invalid |
| T25 | injection item has malformed field, non-SHA-256 hash, blank reason, or extra key | `Invalid` |
| T26 | every valid row in §2's path conformance table | `matches` returns the stated Boolean |
| T27 | each invalid PathGlob input | `PathGlobError`, never Boolean |
| T28 | nonce envelope round trip and wrong nonce | exact bytes recover only with correct nonce |
| T29 | protocol hash before/after one schema-byte change | stable, then changed |
| T30 | `set(Category)` | exact disjoint union of the two named groups |

## 9. Requirements this part answers for

Accountable: RQA-BR-002, RQA-BR-005, RQA-FR-001, RQA-FR-002, RQA-FR-008, RQA-FR-033.

- **RQA-BR-002** (a review has one consistent definition, independent of reviewer). Fit criterion:
  two reviewers independently describe the same review scope, required evidence, findings taxonomy,
  blocking conditions, review-completion condition and final-disposition semantics — all six AC01
  concepts. Met by: `PROTOCOL.md` plus `schema/verdict-1.json` being the one place any of the six is
  defined (§1, §2); §3's `validate()` is the single gate every verdict passes through regardless of
  which harness produced it, so no reviewer can privately redefine any of the six. T4–T24.
- **RQA-BR-005** (mechanical/procedural/creation-time findings must stay distinguishable from
  substantive ones in the record even when both block). Fit criterion: a reader can tell the two kinds
  of finding apart from its closed, non-empty `categories`, even when it also carries open
  `extra_tags`. Met by: the required `categories` collection and preserved `extra_tags` (§2, §3
  step 7), never merged or dropped by validation. T20–T24, T29.
- **RQA-FR-001** (every managed review's verdict validates against one published protocol
  definition). Fit criterion: a verdict can be checked against a single published definition and
  either validates or fails; exactly one such definition is in force. Met by: `schema/verdict-1.json`
  plus `PROTOCOL.md`, versioned as one pair (§1, §5); `validate()` is that check (§3); ADR reference
  #2064 is where the pair is filed. T2–T24.
- **RQA-FR-002** (two reviews of the same PR by different harnesses/models/providers carry the same
  concept semantics). Fit criterion: each of AC01's six concepts means the same thing across both
  records. Met by: the `CONTRACTS.md` §2 types being the one shape every harness's output is coerced
  into or rejected from (§2, §3 step 10); a harness cannot smuggle a private field past
  `additionalProperties: false`. T12, T20–T24.
- **RQA-FR-008** (every finding carries categories distinguishing the two named groups, and no finding
  is uncategorised). Fit criterion: every finding carries at least one closed category from one of the
  two named groups while retaining arbitrary open tags separately. Met by: required `categories` with
  its closed enum and `minItems: 1` (§2), enforced at §3 step 7. T11, T20–T22.
- **RQA-FR-033** (removing the external provider from configuration leaves the protocol and its
  semantics unchanged). Fit criterion: with the external provider removed, the same published
  definition still validates reviews and the same concept semantics still hold. Met by: `validate()`
  and the schema taking no provider, route or external-send input at all (§3, §4) — nothing about the
  protocol's shape or meaning depends on which route produced the verdict being validated.
