# RQA gap analysis — dispositions: `verdict` cluster

A recommended disposition — `keep`, `salvage`, `rework` or `bin` — for each of
the 21 disposition units of [`../evidence/verdict.md`](../evidence/verdict.md),
in that file's order, per [`../methodology.md`](../methodology.md) §7. Revision
`9267b6308714454a3b987622d90cda03a8972827`. All paths are relative to
`launchpad/skills/review-queue-automation/`.

This document recommends what should happen to what exists. It designs no
replacement: naming a constraint the rebuilt behaviour must hold is a
disposition, naming the component that would hold it is architecture work, which
issue #2070 places out of scope. It changes no gap degree and no root cause; the
`Root cause:` line of each unit quotes the register as it stands.

## Searches reproduced for this document

Every negative asserted below is one of these four searches, or a `path:line`
into the named artefact whose structure is the claim. Each command is run from
`launchpad/skills/review-queue-automation/`; the output is its literal stdout.
The scopes are not interchangeable and are named where each search is used:
**S-B is `scripts/**/*.py` only** and establishes nothing about `tests/`,
`schemas/` or the operator-facing documents, and **S-D** is the tree-wide form
for the claims that need one.

**S-A — which register rows cite each `verdict` unit.** Grounds every
`Root cause:` line, and the "no register row depends on this unit" claims in
U-VERDICT-03, U-VERDICT-19, U-VERDICT-20 and U-VERDICT-21.

```
python3 -c 'import re,pathlib;t="".join(p.read_text() for p in sorted(pathlib.Path("gap/register").glob("*.md")));rows=[l for l in t.splitlines() if l.startswith("| RQA-")];[print(f"U-VERDICT-{n:02d}: "+(", ".join(l.split("|")[1].strip()+" ("+l.split("|")[2].strip()+")" for l in rows if f"U-VERDICT-{n:02d}" in l) or "(no register row cites this unit)")) for n in range(1,22)]'

U-VERDICT-01: RQA-FR-001 (partial gap)
U-VERDICT-02: RQA-BR-002 (partial gap), RQA-BR-004 (partial gap), RQA-FR-001 (partial gap), RQA-FR-008 (full gap), RQA-FR-033 (fit), RQA-FR-034 (full gap), RQA-NFR-003 (partial gap)
U-VERDICT-03: (no register row cites this unit)
U-VERDICT-04: RQA-BR-005 (full gap), RQA-BR-008 (partial gap), RQA-FR-002 (fit), RQA-FR-008 (full gap), RQA-NFR-031 (full gap), RQA-NFR-033 (full gap), RQA-NFR-016 (full gap)
U-VERDICT-05: RQA-BR-004 (partial gap), RQA-BR-005 (full gap), RQA-BR-003 (partial gap), RQA-BR-008 (partial gap)
U-VERDICT-06: RQA-BR-009 (partial gap), RQA-FR-014 (conflicting), RQA-FR-036 (conflicting)
U-VERDICT-07: RQA-BR-014 (partial gap), RQA-FR-002 (fit), RQA-NFR-012 (partial gap), RQA-NFR-015 (partial gap)
U-VERDICT-08: RQA-NFR-007 (partial gap)
U-VERDICT-09: RQA-FR-023 (fit), RQA-FR-024 (fit)
U-VERDICT-10: RQA-FR-023 (fit), RQA-FR-024 (fit)
U-VERDICT-11: RQA-BR-003 (partial gap), RQA-FR-002 (fit), RQA-NFR-022 (fit), RQA-NFR-032 (fit)
U-VERDICT-12: RQA-BR-002 (partial gap), RQA-FR-002 (fit), RQA-FR-037 (conflicting)
U-VERDICT-13: RQA-BR-004 (partial gap)
U-VERDICT-14: RQA-BR-004 (partial gap), RQA-FR-034 (full gap)
U-VERDICT-15: RQA-FR-034 (full gap)
U-VERDICT-16: RQA-BR-001 (partial gap), RQA-FR-036 (conflicting), RQA-FR-010 (full gap), RQA-FR-011 (conflicting)
U-VERDICT-17: RQA-FR-034 (full gap)
U-VERDICT-18: RQA-BR-008 (partial gap), RQA-BR-014 (partial gap), RQA-FR-034 (full gap)
U-VERDICT-19: (no register row cites this unit)
U-VERDICT-20: (no register row cites this unit)
U-VERDICT-21: (no register row cites this unit)
```

**S-B — every occurrence under `scripts/` of the symbols this document calls
unreached.** Each hit is a definition, a same-module local in `risk.py`'s own
`compute_assurance`, a dataclass field, that field's own serialisation, or a
string in `worktree.py`. No hit is a call site in another module.

```
python3 -c 'import re,pathlib;pat=re.compile(r"read_verdict|validate_structure|BoundedChange|write_assessment|read_assessment|DEFAULT_PROTECTED|ProtectedTriggerError|can_approve|can_request_changes|can_comment|action_recommended|action_attempted|action_confirmed|author-triage");print("\n".join(f"{p}:{i}:{l.rstrip()}" for p in sorted(pathlib.Path("scripts").rglob("*.py")) for i,l in enumerate(p.read_text().splitlines(),1) if pat.search(l)))'

scripts/risk.py:134:class ProtectedTriggerError(Exception):
scripts/risk.py:155:DEFAULT_PROTECTED = (
scripts/risk.py:169:class BoundedChange:
scripts/risk.py:288:def write_assessment(path: str | pathlib.Path, data: dict[str, Any]) -> pathlib.Path:
scripts/risk.py:301:def read_assessment(path: str | pathlib.Path) -> tuple[int, dict[str, Any]]:
scripts/risk.py:341:    can_approve: bool = False
scripts/risk.py:342:    can_request_changes: bool = False
scripts/risk.py:343:    can_comment: bool = True
scripts/risk.py:345:    action_recommended: str = "none"
scripts/risk.py:346:    action_attempted: str = "none"
scripts/risk.py:347:    action_confirmed: str = "none"
scripts/risk.py:365:            "can_approve": self.can_approve,
scripts/risk.py:366:            "can_request_changes": self.can_request_changes,
scripts/risk.py:367:            "can_comment": self.can_comment,
scripts/risk.py:368:            "action_recommended": self.action_recommended,
scripts/risk.py:369:            "action_attempted": self.action_attempted,
scripts/risk.py:370:            "action_confirmed": self.action_confirmed,
scripts/risk.py:415:    can_approve = met and completeness >= 0.8 and uncertainty <= 0.2 and not blockers_list
scripts/risk.py:416:    can_request_changes = bool(any("blocker" in b for b in blockers_list))
scripts/risk.py:417:    can_comment = True
scripts/risk.py:424:        can_approve=can_approve,
scripts/risk.py:425:        can_request_changes=can_request_changes,
scripts/risk.py:426:        can_comment=can_comment,
scripts/verdict.py:107:def validate_structure(text: str) -> tuple[bool, list[str]]:
scripts/verdict.py:200:def read_verdict(path: pathlib.Path) -> dict[str, Any] | None:
scripts/worktree.py:2:"""Isolated author-triage worktree operations: create, commit, push, clean.
scripts/worktree.py:288:        result = commit(config, args.repo, args.job, args.message or f"author-triage {args.job}", args.signoff, args.provenance, args.number)
```

**S-C — shadow mode, backtesting, calibration and triage in the frozen
specification.**

```
python3 -c 'import re,pathlib;pat=re.compile(r"shadow|backtest|calibrat|triage",re.I);print("\n".join(f"{p}:{i}:{l.rstrip()}" for p in sorted(pathlib.Path("requirements").rglob("*.md")) for i,l in enumerate(p.read_text().splitlines(),1) if pat.search(l)))'
```

The command matches no line anywhere under `requirements/`. Its entire stdout is
the single empty line that printing an empty join emits, which is why the block
above shows the command and nothing after it: there is no output to quote and
none has been elided.

**S-D — the same symbols across the whole assessed estate, not only
`scripts/`.** This is the tree-wide form S-B is not: it walks every file under
the skill directory and excludes only `gap/`, this analysis's own documents,
which postdate `9267b6308` and are not among the files
[`../manifest.md`](../manifest.md) pins. It carries the claims about `tests/`
scope in U-VERDICT-15, U-VERDICT-17 and U-VERDICT-18, and it adds
`risk-assessment` to the pattern so the artefact name is searched as well as its
writer. The count line is the command's own first line of output.

```
python3 -c 'import re,pathlib;pat=re.compile(r"read_verdict|validate_structure|BoundedChange|write_assessment|read_assessment|DEFAULT_PROTECTED|ProtectedTriggerError|can_approve|can_request_changes|can_comment|action_recommended|action_attempted|action_confirmed|author-triage|risk-assessment");hits=[f"{p}:{i}:{l.rstrip()}" for p in sorted(pathlib.Path(".").rglob("*")) if p.is_file() and not str(p).startswith("gap/") for i,l in enumerate(p.read_text(errors="replace").splitlines(),1) if pat.search(l)];print(f"{len(hits)} hits");print("\n".join(hits))'

58 hits
OPERATORS.md:280:| author-triage canary | The author-triage lane. | The `canaries` table row for `author_triage`, if present; otherwise `dispatch.author_canary_approved`. |
SKILL.md:3:description: Automate PR review and author-triage across launchpad-26/buzz and
SKILL.md:295:requested-changes-fixed, author-triage, human-decision, closed, merged, plus the
references/contracts.md:128:2. One author-triage job runs end to end. Continuous author dispatch remains disabled until human inspection.
scripts/risk.py:15:`validate_bands`, and a versioned `risk-assessment.json` writer/reader keeps the
scripts/risk.py:33:#: Version of the serialized `risk-assessment.json` shape. Bumped on schema change;
scripts/risk.py:134:class ProtectedTriggerError(Exception):
scripts/risk.py:155:DEFAULT_PROTECTED = (
scripts/risk.py:169:class BoundedChange:
scripts/risk.py:279:# ---- versioned risk-assessment.json -----------------------------------------
scripts/risk.py:288:def write_assessment(path: str | pathlib.Path, data: dict[str, Any]) -> pathlib.Path:
scripts/risk.py:289:    """Persist a versioned `risk-assessment.json` atomically. The envelope is
scripts/risk.py:301:def read_assessment(path: str | pathlib.Path) -> tuple[int, dict[str, Any]]:
scripts/risk.py:302:    """Read a versioned `risk-assessment.json`, returning (version, data).
scripts/risk.py:311:            f"risk-assessment.json version {version} unsupported (expected {RISK_ASSESSMENT_VERSION})"
scripts/risk.py:315:        raise ValueError("risk-assessment.json is missing a risk_assessment object")
scripts/risk.py:341:    can_approve: bool = False
scripts/risk.py:342:    can_request_changes: bool = False
scripts/risk.py:343:    can_comment: bool = True
scripts/risk.py:345:    action_recommended: str = "none"
scripts/risk.py:346:    action_attempted: str = "none"
scripts/risk.py:347:    action_confirmed: str = "none"
scripts/risk.py:365:            "can_approve": self.can_approve,
scripts/risk.py:366:            "can_request_changes": self.can_request_changes,
scripts/risk.py:367:            "can_comment": self.can_comment,
scripts/risk.py:368:            "action_recommended": self.action_recommended,
scripts/risk.py:369:            "action_attempted": self.action_attempted,
scripts/risk.py:370:            "action_confirmed": self.action_confirmed,
scripts/risk.py:415:    can_approve = met and completeness >= 0.8 and uncertainty <= 0.2 and not blockers_list
scripts/risk.py:416:    can_request_changes = bool(any("blocker" in b for b in blockers_list))
scripts/risk.py:417:    can_comment = True
scripts/risk.py:424:        can_approve=can_approve,
scripts/risk.py:425:        can_request_changes=can_request_changes,
scripts/risk.py:426:        can_comment=can_comment,
scripts/verdict.py:107:def validate_structure(text: str) -> tuple[bool, list[str]]:
scripts/verdict.py:200:def read_verdict(path: pathlib.Path) -> dict[str, Any] | None:
scripts/worktree.py:2:"""Isolated author-triage worktree operations: create, commit, push, clean.
scripts/worktree.py:288:        result = commit(config, args.repo, args.job, args.message or f"author-triage {args.job}", args.signoff, args.provenance, args.number)
tests/test_phase1.py:150:    assert full.can_approve and not partial.can_approve
tests/test_phase1.py:190:    assert not ev.can_approve
tests/test_phase1.py:191:    assert ev.can_request_changes is True or ev.blockers
tests/test_repairs.py:20:# `RequestQueueError`, `enqueue`, `policy_hash_of` and `ProtectedTriggerError`
tests/test_repairs.py:346:    from verdict import signal_from_verdict, validate_structure
tests/test_repairs.py:354:    ok, _ = validate_structure('{"signal":"SUPPORTED","summary":"s","findings":[],"good":[]}')
tests/test_risk.py:6:protected triggers, and versioned risk-assessment.json writing.
tests/test_risk.py:20:    BoundedChange,
tests/test_risk.py:23:    ProtectedTriggerError,
tests/test_risk.py:27:    read_assessment,
tests/test_risk.py:30:    write_assessment,
tests/test_risk.py:116:    ok = BoundedChange(one_clear_purpose=True, bounded_blast_radius=True,
tests/test_risk.py:119:    bad = BoundedChange(one_clear_purpose=True, bounded_blast_radius=False)
tests/test_risk.py:125:    target = pathlib.Path(tempfile.mkdtemp()) / "risk-assessment.json"
tests/test_risk.py:127:    write_assessment(target, payload)
tests/test_risk.py:131:    version, data = read_assessment(target)
tests/test_risk.py:137:    target = pathlib.Path(tempfile.mkdtemp()) / "risk-assessment.json"
tests/test_risk.py:140:        read_assessment(target)
tests/test_verdict_schema.py:23:    validate_structure,
tests/test_verdict_schema.py:42:    ok2, _ = validate_structure(json.dumps(_full()))
```

---

### U-VERDICT-01 — Reviewer-verdict text parsing and markdown-fence normalisation

Disposition: keep
Requirements: RQA-FR-001
Root cause: `not built` (RQA-FR-001) — that row's unmet obligations are the
validator's incomplete enforcement and the absent review-scope definition,
neither of which is this unit's responsibility.

RQA-FR-001 requires every managed review to produce a verdict that validates
against one published definition. Validation presupposes an unambiguous payload
boundary: something has to decide which bytes are the verdict before anything
can check them. The two decisions here are the narrowest form of that. The fence
match is anchored at both ends (scripts/verdict.py:57-63), so prose around a
fence, two fences, or an unclosed fence is never repaired into JSON — each falls
through to a decode failure and an empty signal. And a signal is read only from
a parsed JSON string field whose value is one of the six enumerated tokens
(scripts/verdict.py:91-104), never from a token in surrounding text.

A materially simpler extractor — take the first `{`…`}`, or scan the output for
one of the six signal words — accepts payloads the published definition never
validated, and lets text that arrived from the pull request through the evidence
envelope decide a review's signal, which is the behaviour RQA-NFR-015's fit
criterion tests for. Dropping fence handling entirely is simpler still, but it
does not remove the problem: it either pushes the same normalisation into every
caller of the parser, or makes the protocol depend on a model never wrapping its
output. Neither is less trust, only a less visible place to put it.

What is kept is the rule, not its location: the same anchored-boundary and
signal-from-a-real-field rules are what the rebuilt validator (U-VERDICT-02)
must sit on top of.

---

### U-VERDICT-02 — Reviewer-verdict schema-driven validation and contradiction detection

Disposition: rework
Requirements: RQA-FR-001, RQA-FR-002, RQA-FR-033, RQA-FR-034, RQA-FR-008, RQA-BR-002, RQA-BR-004, RQA-NFR-003
Root cause: `not built` (RQA-FR-001, RQA-FR-034, RQA-FR-008, RQA-BR-002,
RQA-BR-004, RQA-NFR-003); `-` (RQA-FR-002, RQA-FR-033, both `fit`).

The responsibility is required and is not in question: one gate that decides
whether a returned payload is a verdict, applied wherever a reviewer slot is
filled. RQA-FR-033 is `fit` because that gate is the same whatever the
configured pools contain, and RQA-FR-002's `fit` rests in part on there being
one findings shape for every harness.

The shape is wrong. `validate_verdict` reads the published schema's `required`
list at runtime (scripts/verdict.py:165-169) and then re-states a subset of the
rest in Python — the `signal` and `recommendation` enums, the presence of five
finding keys — while the schema's finding-level `severity` enum, its `location`
pattern, its `minLength` constraints and its `additionalProperties: false` are
enforced nowhere (schemas/reviewer-verdict.json:4-5,16-21). A validator that
transcribes its schema is not a simpler approach that happens to be incomplete;
it is a second definition of the protocol, and having exactly one is the whole
of RQA-FR-001's obligation. The register records the cost twice: FR-001 is
`partial gap` because a verdict the published definition rejects still fills a
slot, and RQA-BR-004 is `partial gap` because two reviewers writing `blocker`
and `critical` for one defect never corroborate — U-VERDICT-04's fingerprint
keys on severity — so the blocking threshold remains each reviewer's own word.

Retained in intent: validation at the moment a slot would be filled rather than
afterwards, and the six `_CONTRADICTIONS` predicates (scripts/verdict.py:34-45),
which reject internally incoherent verdicts — a `SUPPORTED` signal carrying
findings, a `DEFECTS_FOUND` signal carrying none. That class of defect is not
expressible as a structural schema constraint, and it is the part of this unit
worth carrying verbatim.

Changes: the enforced constraint set is derived from the published definition
instead of copied from it, so divergence is not possible; and the two functions
no product path reaches do not survive — `validate_structure`
(scripts/verdict.py:107), a second and weaker structural check, and
`read_verdict` (scripts/verdict.py:200), which has no caller at all under
`scripts/` (search S-B). RQA-FR-034 admits a retained component only on a
specific, checkable justification, and a duplicate validator that nothing calls
has none.

---

### U-VERDICT-03 — Author-triage verdict schema

Disposition: bin
Requirements: RQA-FR-034
Root cause: `not built` (RQA-FR-034).

`schemas/author-triage.json` declares a per-review-comment triage output shape,
and no code reaches it. `panel.py`'s `VERDICT_SCHEMA` names `reviewer-verdict`
alone and raises `JobBlockingError` for any strategy declaring another
(scripts/panel.py:84-86,566-574), every strategy in `strategies.py` declares
that one, and search S-B shows the only occurrences of "author-triage" under
`scripts/` are two strings inside `worktree.py`.

What is lost: the only written contract for author-triage output in the tree,
including its four-value per-finding classification
(`VALID`/`VALID_BUT_DIFFERENT_FIX`/`INVALID`/`OUT_OF_SCOPE`) scoped per comment
rather than per verdict.

Nothing in the frozen specification depends on it. Search S-A shows no register
row cites this unit at all, and search S-C shows the specification does not use
the word "triage" anywhere. The rows that do carry the author-triage lane —
RQA-FR-017 and RQA-BR-006, both `full gap` / `built then orphaned` — are
evidenced against `scripts/worktree.py`, not against this file, so binning it
takes no evidence from them. RQA-FR-008, the row that does require a finding
vocabulary, is a `full gap` stated against `schemas/reviewer-verdict.json`'s
five fixed finding keys; it is not closed by retaining an unreferenced second
schema whose enum was written for a different question.

---

### U-VERDICT-04 — Finding extraction with an evidence-completeness filter

Disposition: keep
Requirements: RQA-FR-002, RQA-BR-008, RQA-BR-014, RQA-BR-005, RQA-FR-008, RQA-NFR-016, RQA-NFR-031, RQA-NFR-033
Root cause: `-` (RQA-FR-002, `fit`); `not built` (RQA-BR-008, RQA-BR-014,
RQA-BR-005, RQA-FR-008, RQA-NFR-016, RQA-NFR-031, RQA-NFR-033).

Two mechanisms, one responsibility, and one of them carries a `fit` row.
RQA-FR-002 requires a finding to mean the same thing in two reviews by different
models or providers; the fingerprint that delivers it is severity plus a
whitespace- and case-normalised location and deliberately nothing else
(scripts/findings.py:53-61). That coarseness is the mechanism: two models
describing one defect in different prose are recognised as one defect. A simpler
or stricter match — on title, or on the finding object as a whole — corroborates
only reviewers who happen to write alike, which would make U-VERDICT-05's
two-family rule unreachable in practice and leave RQA-BR-008's verified /
unverified split with nothing on the verified side.

The completeness filter is the other half: a finding with no severity, location,
evidence or primary source is dropped before corroboration
(scripts/findings.py:110-111). Passing everything through and weighing it later
is the approach RQA-BR-008 rules out — its criterion is that a reader can say
which claims and cited evidence were verified, as distinct from cosmetic
observations, and an assertion with no location and no cited source cannot be
placed on either side of that line.

Two bounded claims. First, the drop is silent: nothing records that a malformed
finding was discarded. The register attributes RQA-BR-014's unmet obligation to
the absent per-obligation evidence state (a contract dependency on RQA-FR-010),
not to this unit, so that is not the ground of this disposition — but a later
wave should not assume the record shows what was discarded. Second, the
`full gap` rows citing this unit (RQA-NFR-016, RQA-NFR-031, RQA-NFR-033,
RQA-BR-005) cite it as the nearest thing that does *not* carry a remedy class, a
finding category or an induced-clean determination; keeping the extractor is not
a claim that it does any of those.

---

### U-VERDICT-05 — Finding corroboration: two-family or check-backed blocking rule

Disposition: keep
Requirements: RQA-BR-008, RQA-BR-014, RQA-BR-004, RQA-BR-003, RQA-BR-005, RQA-FR-012
Root cause: `not built` (RQA-BR-008, RQA-BR-014, RQA-BR-004, RQA-BR-005,
RQA-FR-012); `built against superseded intent` (RQA-BR-003) — in that row the
superseded behaviour is the unpinned policy identity in
`config.py`/`dispatcher.py`, and this unit is named among the parts that hold.

RQA-BR-008 requires review output to establish which higher-value claims and
cited evidence were verified. The register records the verified/unverified split
with its per-finding basis as this row's one complete, reachable and published
obligation, and this unit is that split. Neither of its two narrowings can be
loosened without giving the requirement away. Independent agreement means two
*distinct provider families* reporting the same fingerprint
(scripts/findings.py:168-177) — counting two models from one vendor as
independent would make agreement a property of the provider rather than of the
evidence. The single-family alternative requires the finding to cite, in its own
evidence or primary source, a check whose conclusion is in the deliberately
narrow `FAILING` set (scripts/findings.py:133-143, scripts/checks.py:51) —
accepting "not passing" instead would let a pending or unrecognised check
corroborate a defect, which is a corroboration by absence of information.

The default is what makes it load-bearing: an uncorroborated blocking finding is
returned `verified=False` with basis `single_family_uncorroborated` and
escalates rather than acting (scripts/findings.py:193-196), so a lone model
assertion cannot become an authoritative CHANGES_REQUESTED. `blocking_summary`
is the same decision made legible to RQA-FR-012's reconstruction and to the
published bodies (scripts/findings.py:212-221).

Recorded, not resolved: branch (b) selects on a substring of model-authored text
(`_cited_failing_check`, scripts/findings.py:139-142). A failure cannot be
invented — the named check must genuinely be in `FAILING` — but which finding
gets corroborated is decided by text the model wrote. No register row attributes
this to RQA-NFR-015, whose criterion concerns pull-request content followed as
an instruction, so it is not the ground of this disposition; it is flagged so a
later wave does not inherit branch (b) as a trust boundary someone has checked.

---

### U-VERDICT-06 — Canonical check-conclusion vocabulary

Disposition: rework
Requirements: RQA-BR-009, RQA-FR-014, RQA-FR-036, RQA-NFR-010
Root cause: `built contrary` (RQA-FR-014, RQA-FR-036); `not built`
(RQA-BR-009); `built contrary` (RQA-NFR-010) — that row's contrary execution is
`_ledger_record`'s swallowed write in `dispatcher.py` (U-DISPATCH-20), not this
unit, whose cited behaviour is on the compatible side.

The responsibility survives: one canonicalisation and one conclusion vocabulary
that every consumer imports rather than re-declares. RQA-BR-009 cannot be served
without it — an attribution has to be attached to a single, agreed answer to
"did this check fail" — and the register records that this module replaced four
independently drifted literal sets. Its fail-closed defaults are right too: an
empty check list and a single pending check are both not-green
(scripts/checks.py:115-123), and an unrecognised status passes through un-mapped
so `is_failing` treats it as standing in the way (scripts/checks.py:77-85).

The shape is nonetheless wrong for the requirements that turn on it. A
conclusion in this vocabulary says what a check reported and has nowhere to say
whose failure it is. RQA-FR-014 and RQA-FR-036 are both `conflicting` /
`built contrary`, and both cite scripts/checks.py:115-123 alongside
scripts/dispatcher.py:296-297: `all_passing` over a head's checks feeds the
`checks_complete_ok` approval gate, so a failure that also fails on the merge
base contributes to a blocking disposition — which RQA-FR-036 forbids in terms.
The register states the fix is subtractive: it "requires changing that
evaluation, not adding a mechanism". A vocabulary that cannot express the
distinction therefore cannot remain the whole input to a blocking gate.
RQA-BR-009's six-value attribution is the same hole from the other side.

Retained in intent: one canonicalisation, one `PASSING` set, one `FAILING` set,
imported by every consumer, with both fail-closed defaults above and the
narrower `FAILING` set that U-VERDICT-05's corroboration depends on. Changes: a
bare conclusion stops being sufficient input to a blocking decision — what the
gate consumes has to carry the PR-versus-base attribution RQA-FR-014,
RQA-FR-036 and RQA-BR-009 name. Which component derives that attribution is a
design question this analysis does not answer.

---

### U-VERDICT-07 — Evidence bundle collection for one PR

Disposition: keep
Requirements: RQA-FR-002, RQA-BR-014, RQA-FR-012, RQA-NFR-015, RQA-NFR-010, RQA-NFR-012
Root cause: `-` (RQA-FR-002, `fit`); `not built` (RQA-BR-014, RQA-FR-012,
RQA-NFR-015, RQA-NFR-012); `built contrary` (RQA-NFR-010) — that row's contrary
execution is the swallowed ledger write in `dispatcher.py`, and this unit's
fail-closed collection is named among the compatible behaviour.

Three mechanisms, each answering a different requirement.

`collect` raises `EvidenceIncompleteError` when the fetched metadata is empty,
the head SHA is missing, or the check-runs read returns `None`, before anything
is written (scripts/evidence.py:37-50). The simpler alternative — write what was
fetched and let the reviewer notice — produces exactly the partial evidence
RQA-NFR-010 forbids and RQA-BR-014 cannot demonstrate from, and it fails
invisibly: a model handed a short bundle reviews it rather than refusing it, so
the shortfall surfaces as a confident verdict rather than an error.

The artefact set is fixed to three names declared in one place and read back by
that contract (scripts/evidence.py:21-23, scripts/panel.py:537-540). RQA-FR-002
is `fit` partly on that fixity: "required evidence" means the same thing in two
reviews because there is one declaration of what a bundle is, not one per
reader.

The nonce-keyed envelope around every GitHub-sourced field
(scripts/evidence.py:93-124) is the mechanism RQA-NFR-015's met part rests on.
There is no simpler delimiter: a fixed marker is one a pull-request author can
write into the diff themselves, and a per-job nonce is the smallest thing that
content cannot forge.

Not claimed: keeping this closes neither RQA-NFR-015 — the prompt names the
envelope path but nothing decides what an embedded instruction means — nor
RQA-NFR-012, which stays a `partial gap` for a reason that is settled rather
than open. Under the maintainer's 2026-09-08 ruling on NFR012-RUNNER-SEND the
requirement permits code, diffs, metadata and evidence to be sent rather than
obliging RQA to send them, so what leaves that row short is `--no-tools`
disabling the runner's own file access, not anything this bundle does or fails
to do.

---

### U-VERDICT-08 — Assurance escalation ladder (capability / effort / independence)

Disposition: keep
Requirements: RQA-NFR-007, RQA-FR-023, RQA-FR-024
Root cause: `built then orphaned` (RQA-NFR-007) — the orphaned mechanisms in
that row are `scripts/worktree.py` and the degrade ladder, and the register
names this ladder among the parts that run; `-` (RQA-FR-023, RQA-FR-024, both
`fit`).

This is the reachable side of RQA-NFR-007, not one of its orphans:
`dispatcher.py` imports `drive` (scripts/dispatcher.py:33) and runs the loop
(scripts/dispatcher.py:1367), and `panel.py` imports and calls `minimum_profile`
(scripts/panel.py:48,157).

RQA-NFR-007 requires every managed PR to be carried to an authoritative
APPROVED or CHANGES_REQUESTED outcome whenever progression remains possible.
That obliges two things: a rule that decides from the signals in hand whether
progression is still possible or a human is required, and a bound guaranteeing
the attempt terminates. `classify` is the first — `HUMAN_RESERVED` routes to a
human whatever else is present, `DEFECTS_FOUND` with `SUPPORTED` and
`MATERIAL_DISAGREEMENT` convene a panel from lower independence and escalate
once already at panel, and `INSUFFICIENT_CAPABILITY` raises effort before
capability (scripts/assurance.py:94-134). `raised` is the second: it moves one
step on one named axis and returns `None` at that axis's cap
(scripts/assurance.py:69-86), so `drive` cannot escalate past
`frontier`/`xhigh`/`panel` and always terminates at `SUCCESS`,
`REQUEST_CHANGES` or `HUMAN`.

A materially simpler rule fails the requirement in one direction or the other.
Escalating to a human on the first disagreement abandons progression the
requirement says to carry, turning a panel-resolvable disagreement into an
interrupt. Retrying the same profile makes no progress and has no termination
argument at all. Separating the three axes is what makes "one step up" a defined
move rather than a judgement call, which is also why RQA-FR-023's fallback and
RQA-FR-024's no-invention hold at each rung.

---

### U-VERDICT-09 — Panel candidate-pool selection, capability/effort qualification and cooldown tracking

Disposition: keep
Requirements: RQA-FR-023, RQA-FR-024, RQA-FR-038
Root cause: `-` (RQA-FR-023, RQA-FR-024, both `fit`); `not built`
(RQA-FR-038) — that row's unmet obligation is credential-scope observability
(U-AUTHORITY-02), not this unit.

RQA-FR-024 forbids substituting an unconfigured alternative when a configured
reviewer, model or provider becomes unavailable; RQA-FR-023 requires the review
to continue through a configured fallback. Both are `fit` and both cite this
unit. The mechanism that earns them is the qualification filter and, more
precisely, what it does when the filter empties a lane: `_qualifying` excludes
any entry whose declared capability rank is below the profile's or whose
declared efforts exclude the requested effort, and a lane with no qualifying
entry is dropped rather than refilled unfiltered
(scripts/panel.py:549-557,576-582). The simpler behaviour — take whatever
remains available — is not a smaller mechanism, it is the substitution
RQA-FR-024 prohibits.

Cooldown keyed by `runner:selector`, with every model of a provider family
retired for the run after a provider-scoped failure
(scripts/panel.py:274-284,718-722), is the narrowest form that still holds under
RQA-FR-023: keying on the model alone would retry a sibling behind the same
outage and spend the ladder's remaining rungs on one correlated failure, leaving
the review with no configured route left rather than a working fallback.

On the invariant the evidence records as unnamed by any requirement — a slot can
never be filled twice by one selector or one provider family
(scripts/panel.py:657-664,708-710) — it is retained here for a derived reason
and not on its own account: it is what makes a filled slot count as an
independent participant in the completeness predicate (U-VERDICT-12) and in the
mode aggregation that reads the trusted sidecar (U-VERDICT-11). If a later
design does not count independence per slot, that invariant is the part of this
unit with nothing behind it.

---

### U-VERDICT-10 — Candidate attempt execution, error-class taxonomy and the slot-fill validation gate

Disposition: keep
Requirements: RQA-FR-023, RQA-FR-024, RQA-NFR-009, RQA-FR-038, RQA-FR-001, RQA-FR-037
Root cause: `-` (RQA-FR-023, RQA-FR-024, RQA-NFR-009, all `fit`); `not built`
(RQA-FR-001, RQA-FR-038); `built contrary` (RQA-FR-037) — that row's contrary
execution is the human-authorization bypass in `human_cli.py`, not this unit.

The error taxonomy is the substance. Only a genuine subprocess timeout is
retried, once, on the same candidate; a non-zero exit, an `OSError` and a
returned-but-invalid verdict are terminal for that candidate and fall through to
the next entry in the ordered lane (scripts/panel.py:301-332,358-424). That
distinction is what makes RQA-FR-023's "continue through the fallback" mean
something precise: a blanket transient/permanent split either re-invokes a model
that just returned unparseable output — spending budget on a deterministic
failure — or abandons a configured lane on a network blip, which is the halt
RQA-FR-023 forbids.

The slot-fill gate is the second mechanism: a slot is filled only when raw
stdout passes validation, and otherwise the partial output file is deleted and
the candidate is cooled down as `candidate_terminal`
(scripts/panel.py:344-356,406-424). Placing the gate at slot-fill, rather than
after aggregation, is what stops an unvalidated response ever being counted as a
participant — RQA-FR-037's floor applied at the first point a success signal
could be manufactured. And an unknown runner adapter or an unenforceable effort
raises `JobBlockingError` instead of being demoted to one candidate's bad luck
(scripts/panel.py:301-314), so a misconfiguration stops the job rather than
walking silently down the ladder, which is what RQA-FR-038's clear, safe,
recoverable stop asks for.

Bounded claim: the gate is exactly as strong as the validator it calls, and that
validator is a `rework` (U-VERDICT-02). Keeping this unit is a judgement about
where validation happens, not about what it currently enforces.

---

### U-VERDICT-11 — Trust boundary between machinery-attested identity and model-controlled verdict content

Disposition: keep
Requirements: RQA-NFR-022, RQA-NFR-032, RQA-FR-002, RQA-BR-003
Root cause: `-` (RQA-NFR-022, RQA-NFR-032, RQA-FR-002, all `fit`);
`built against superseded intent` (RQA-BR-003) — that row's superseded
behaviour is the unpinned protocol/policy identity elsewhere, and this sidecar
is named among the parts that establish performer and judgement basis.

RQA-NFR-022 forbids any element of the provenance record to be writable by
model output; RQA-NFR-032 requires the record to be written by the system
itself. Both are `fit` and both rest on this unit. The mechanism is a placement
decision, not a file: runner, model, `provider_family`, capability and effort
are written by the harness into a `.meta.json` sidecar immediately after a slot
is filled (scripts/panel.py:249-263,711-715), and `_mode_participants` reads
`provider_family` for independence aggregation from that sidecar rather than
from the verdict (scripts/panel.py:215-246).

The materially simpler approach is the one the requirement names as the failure:
reading the family from the JSON the model produced lets a model assert an
independence it does not have, and independence is precisely what the mode
aggregation counts. Validating a model's self-reported family against a list is
not materially simpler either — it leaves model output as the source of a
provenance element, and RQA-NFR-032 is about who writes the record, not about
whether the value looks plausible.

The fail-closed detail belongs to the same mechanism and should not be separated
from it: a slot with no verdict file on disk contributes an explicitly invalid
participant instead of being omitted, so a missing file cannot quietly shrink
the denominator the completeness predicate divides by.

---

### U-VERDICT-12 — Panel run orchestration and completeness predicate

Disposition: keep
Requirements: RQA-FR-037, RQA-FR-011, RQA-FR-002, RQA-FR-001, RQA-BR-002
Root cause: `built contrary` (RQA-FR-037, RQA-FR-011) — in both rows the
contrary execution is the human authorization in
`human_cli.py`/`approval_evaluate.py` that converts a gate-failed job into
`completed_auto_approved`, and both rows name this predicate among the parts
that never manufacture success; `-` (RQA-FR-002, `fit`); `not built`
(RQA-FR-001, RQA-BR-002).

RQA-FR-037 forbids the review from manufacturing a successful outcome when its
obligations are unsatisfied. This predicate is the mechanism that refuses:
`complete` requires the count of parsed signals, the count of filled slots and
the count of mode-counted participants each to reach the profile's required
number, and anything less is `degraded` or `retryable` and is never upgraded
(scripts/panel.py:726-751).

Three counts rather than one is the point, and each simpler version fails a
specific way. Counting verdict files on disk accepts a file written under a
weaker prior profile. Counting parsed signals alone accepts a participant the
mode aggregation rejected as invalid — the count that reflects the trusted
sidecar, not the model's own output. Counting filled slots alone accepts a slot
whose verdict yielded no signal. The complement is the clearing step: every
pre-existing slot file is deleted before an attempt runs
(scripts/panel.py:626-631), without which an escalated re-run could be satisfied
by the very output that caused the escalation. The strategy fence — a declared
`output_schema` other than `reviewer-verdict` raises before any candidate is
invoked (scripts/panel.py:566-574) — is the same posture applied to
configuration rather than to model output.

The `conflicting` degrees on RQA-FR-011 and RQA-FR-037 are not findings against
this unit; both rows locate the contradiction in the authority cluster's human
bypass. Keeping this predicate does not close them, and neither does binning it.

---

### U-VERDICT-13 — FMEA-C risk scoring and band classification

Disposition: keep
Requirements: RQA-BR-004, RQA-NFR-018
Root cause: `not built` (RQA-BR-004) — that row's unmet obligation is the
severity vocabulary, which the register places on the validation path
(U-VERDICT-02), not here; `built contrary` (RQA-NFR-018) — that row's two
contrary executions are in `resolve_snapshot` (scripts/dispatcher.py:1584-1600)
and its evidence does not cite this unit.

RQA-BR-004 requires the threshold at which a finding blocks a PR to be
consistent rather than left to each reviewer's judgement — two reviewers
applying the same policy to equivalent findings must reach the same decision.
Three decisions here deliver that, and each has a simpler alternative that gives
it away.

`effective_risk` takes the **maximum** RPN over failure modes, never the mean
(scripts/risk.py:110-112): an averaging aggregate is simpler and makes the
blocking decision depend on how many mild modes a reviewer bothered to
enumerate, which is reviewer judgement re-entering by the back door.
`combined_risk` returns the maximum of the deterministic floor and the
model-observed score (scripts/risk.py:115-122), so a model observation can only
raise risk; taking the model's number directly is simpler and restores exactly
the per-reviewer variation the requirement excludes. `validate_bands` raises
`ConfigBandError` on a band set that is not strictly increasing and continuous
(scripts/risk.py:42-56), so a malformed policy fails closed instead of
classifying risk into a lower band than intended.

Bounded claim: keeping this unit does not close RQA-BR-004. That row's unmet
obligation is that `blocker` and `critical` are not one vocabulary, and the
register places the fix on the reachable validation path as an additive change.

---

### U-VERDICT-14 — Protected-path trigger detection

Disposition: rework
Requirements: RQA-BR-004, RQA-FR-034
Root cause: `not built` (RQA-BR-004, RQA-FR-034).

The responsibility is required. RQA-BR-004 needs the protected-path decision to
be a deterministic match of repository policy against changed paths, decided
before any model sees the change, and `protected_triggered` is that
(scripts/risk.py:138-152), reachable, fed from validated policy config
(scripts/config.py:275-293), and returning both the matched path and the pattern
that matched so the decision basis is legible. What makes this a rework rather
than a keep is a failure mode inside the same function, plus two components with
nothing behind them.

The function silently skips any pattern that fails to compile
(`except re.error: continue`, scripts/risk.py:150-151) while its own docstring
one line above states "Fail-closed: unknown/matching surface is protected"
(scripts/risk.py:140). The behaviour is the inverse of the claim: a malformed
pattern removes a path from the protected set, `no_protected_trigger` — the one
gate of `ApprovalState` that defaults `True` (scripts/risk.py:219) — stays
satisfied, and the change proceeds with authority the policy author meant to
withhold. Read against RQA-NFR-018's text ("a malformed or unreadable policy
shall never widen authority beyond what was already granted"), that is the shape
the requirement forbids. I am not changing that row: its `conflicting` degree
rests on `resolve_snapshot` and its evidence does not cite this line. It is
recorded here as the reason the mechanism must be rebuilt rather than retained.

Retained in intent: a deterministic, policy-driven path match whose result names
the path and the pattern. Changes: an uncompilable or unreadable pattern must
not narrow the protected set; and `DEFAULT_PROTECTED` and `ProtectedTriggerError`
(scripts/risk.py:134-136,155-165) do not survive — search S-B shows both occur
only at their own definitions, the live protected set comes from repository
policy, and RQA-FR-034 admits a retained component only on a specific,
checkable justification that neither has.

---

### U-VERDICT-15 — Bounded-change assessment: seven named gates aggregated into one bounded verdict

Disposition: bin
Requirements: RQA-FR-034
Root cause: `not built` (RQA-FR-034).

`BoundedChange` occurs under `scripts/` only at its own definition (search S-B:
scripts/risk.py:169), and across the whole assessed estate its only other
appearances are three lines of one test module (search S-D:
tests/test_risk.py:20,116,119). Methodology §2.3 settles what that means — a
behaviour whose only caller is a test is not implemented. The `bounded_change`
boolean the approval path actually consumes is computed from an addition-count
threshold elsewhere (scripts/shadow.py:259 and the dispatcher's evidence
assembly), never from this class.

What is lost: the seven-way articulation of what "bounded" means — one clear
purpose, bounded blast radius, no protected trigger, straightforward rollback,
adequate tests, no unexplained dependencies, no unresolved ambiguity — together
with a `failed()` list naming which of those a change missed. That is a
substantially richer statement than a line-count threshold, and the loss is
real.

No requirement depends on it. Search S-A shows RQA-FR-034 is the only register
row citing this unit, and this component sits on that row's failing side: FR-034
requires a retained component to carry a specific, checkable justification, and
an aggregator no product path reaches has none. The nearest requirement in the
specification, RQA-NFR-019, bounds *remediation authority* to the finding
categories policy names as mechanical — a different obligation, resting on
RQA-FR-008's absent category vocabulary rather than on this class. Nothing in
the frozen specification requires the approval predicate's `bounded_change`
input to be seven-valued rather than one boolean, so binning this takes no row's
evidence with it.

`VERDICT-ORPHANED` was settled by the maintainer on 2026-09-08: `(orphaned)`
comes out of both unit names, and the reachability fact stays, stated in each
unit's own evidence as a fact with its citation and its quoted negative search.
His reasoning, as he gave it:

> `built then orphaned` is a §6 root-cause term, and root cause is a register
> judgement made per requirement row. A wave-1 unit name carrying `(orphaned)`
> imports that judgement into the evidence layer, where it pre-empts the
> register row that is supposed to reach it, and it does so for a whole unit
> when root cause is per requirement — a unit serving several requirements could
> have different root causes across them. The layers must stay separate:
> evidence establishes what the code does and whether it is reached; the
> register decides degree and root cause from that. So name each unit for the
> behavioural responsibility it is, and let its evidence say — with the
> `path:line` and the negative search quoted per the standing rule — that
> nothing under `scripts/` reaches it. Nothing is lost: the same fact still
> reaches the register, and both of these units' registers already carry
> `built then orphaned` where it belongs.

One correction to that last clause, recorded rather than smoothed over: the only
register row citing either unit is `RQA-FR-034` (search S-A), and that row reads
`full gap` / `not built`, not `built then orphaned` — correctly, because its
obligation is the missing justification record for a retained component, which
no code anywhere provides. The `built then orphaned` vocabulary is carried by
the remediation-family rows (`RQA-BR-006`, `RQA-FR-017`, `RQA-FR-018`,
`RQA-NFR-007`, `RQA-NFR-020`, `RQA-NFR-021`), where a mechanism's own
unreachedness is what the degree turns on. The ruling's operative point is
unaffected: the layers stay separate, the fact reaches the register from the
evidence, and no unit name carries a root cause. This disposition is unchanged —
it rested on the reachability fact before the ruling and rests on it now.

---

### U-VERDICT-16 — `ApprovalState`: the canonical fail-closed 22-gate auto-approval predicate

Disposition: rework
Requirements: RQA-FR-011, RQA-FR-037, RQA-NFR-018, RQA-FR-010, RQA-FR-036, RQA-BR-001
Root cause: `built contrary` (RQA-FR-011, RQA-FR-037, RQA-FR-036,
RQA-NFR-018); `not built` (RQA-FR-010); `built against superseded intent`
(RQA-BR-001).

The responsibility survives and must: one canonical, enumerable gate set with a
single all-must-hold predicate and no second path to a true result. RQA-FR-037
and RQA-FR-011 are unmeetable without it — if each caller assembled its own
conditions there would be no single place where "every obligation satisfied" is
decided — and `all_gates()`/`failed()` are what let a refusal name the specific
gates that failed in a human request. The shape is wrong in three ways, each one
recorded in the register rather than asserted here.

(i) The predicate is not fail-closed throughout. Twenty-one gates default
`False`; `no_protected_trigger` defaults `True` (scripts/risk.py:219). A gate
whose default reads "satisfied", inside a predicate whose entire purpose is that
nothing is satisfied until evidenced, is the wrong default — and U-VERDICT-14
shows a live route to it, where a policy pattern that fails to compile leaves
the gate at that default.

(ii) The gates are booleans. RQA-FR-010 is a `full gap` precisely because no
obligation carries a state from the specification's evidence-state vocabulary;
the register's words are "approval gates are booleans". RQA-FR-011's own fit
criterion is written in that vocabulary — an obligation "neither in the
'verified' evidence state nor demonstrably satisfied through a recorded, named
human approval" — so a conjunction of bare booleans cannot express the
distinction the requirement's own test turns on.

(iii) RQA-FR-036 is `conflicting` and cites scripts/risk.py:223-250:
`checks_complete_ok` is one of the 22, so a check that also fails on the merge
base makes approval unreachable, which that requirement forbids. Closing it is
subtractive.

Retained in intent: one predicate, explicitly enumerated gates, refusal by
default, and a named failure list a human packet can carry. Changes: every gate
defaults closed without exception; the gate vocabulary carries RQA-FR-010's
evidence states rather than a bare boolean; and the checks input is constrained
by the attribution RQA-FR-014 and RQA-FR-036 require (U-VERDICT-06). The bypass
that makes RQA-FR-011 and RQA-FR-037 `conflicting` is `persist_human_approval`
in the authority cluster, not this unit — but for those rows to close, the
rebuilt predicate has to be the only path to a successful disposition, which is
a constraint on that boundary, not a design for it.

---

### U-VERDICT-17 — Versioned `risk-assessment.json` persistence: write, read and version-mismatch refusal

Disposition: bin
Requirements: RQA-FR-034
Root cause: `not built` (RQA-FR-034).

`write_assessment` and `read_assessment` occur under `scripts/` only at their
own definitions (search S-B: scripts/risk.py:288,301), and across the whole
assessed estate their only callers are in one test module (search S-D:
tests/test_risk.py:27,30,127,131,140). The artefact name is searched too: the
string `risk-assessment.json` appears only in `scripts/risk.py`'s own
definitions and docstrings and in that same test module, which writes it into a
temporary directory (search S-D: tests/test_risk.py:125,137). No reachable
dispatch path produces or consumes the artefact.

What is lost: a versioned envelope whose reader raises rather than reinterpreting
a payload written under a different `RISK_ASSESSMENT_VERSION`
(scripts/risk.py:309-312). Nothing about that is worth carrying as a named
mechanism, which is why this is `bin` and not `salvage`: it serves no frozen
requirement, no artefact is written in the envelope, so no reader is at risk of
misparsing one, and how a replacement versions an artefact it decides to persist
is a decision that design takes on its own terms rather than one this estate
established.

No requirement depends on it. Search S-A shows RQA-FR-034 is the only register
row citing this unit — the row a retained component with no specific
justification fails. RQA-FR-012's reconstruction obligation is met from the
ledger (U-RESILIENCE-06, U-RESILIENCE-07), not from this file, so removing it
takes no evidence from that row either.

`VERDICT-ORPHANED` was settled by the maintainer on 2026-09-08, and this unit's
name loses `(orphaned)` for the reason given under U-VERDICT-15: root cause is a
per-row register judgement, not a property of a unit name, and the reachability
fact reaches the register perfectly well from this unit's own evidence, where it
is now quoted with the searches that establish it. The disposition does not turn
on the ruling and does not move.

---

### U-VERDICT-18 — Deterministic assurance evaluation (evidence completeness, residual uncertainty, assurance-met floor)

Disposition: rework
Requirements: RQA-BR-014, RQA-BR-008, RQA-FR-037, RQA-FR-034
Root cause: `not built` (RQA-BR-014, RQA-BR-008, RQA-FR-034); `built contrary`
(RQA-FR-037) — that row's contrary execution is the human bypass, not this
computation.

The core is required and reachable. `compute_assurance` derives a required
assurance from the FMEA risk band, computes achieved assurance as evidence
completeness times a reviewer-completion ratio (halving both when evidence is
not fresh), adds residual uncertainty for incompleteness, disagreement and
unknown outcomes, and sets `assurance_met` against a fixed floor per band
(scripts/risk.py:391-412); `action_gate.request_changes_gate` reads that
property as one of its six deny conditions (scripts/action_gate.py:76-77).
RQA-BR-014 requires a reader to confirm from the record that the important
risks and evidence were examined rather than trusting the volume of activity,
and a deterministic number tied to evidence completeness is how that is stated
without appealing to volume.

The shape is wrong in one respect, and it damages the same requirement. The same
evaluation computes `can_approve`, `can_request_changes` and `can_comment`, and
declares `action_recommended`, `action_attempted` and `action_confirmed`. Search
S-B shows that under `scripts/` all six occur only inside `scripts/risk.py`: the
booleans are computed at :415-417, passed to the constructor at :424-426 and
serialised at :365-367; the three markers are declared at :345-347 and
serialised at :368-370, and nothing under `scripts/` sets them away from
`"none"`. Search S-D widens the scope and finds nothing that changes the
reading: the three markers appear nowhere in the assessed estate outside
`scripts/risk.py`, and the three booleans appear outside it only as three
assertions in `tests/test_phase1.py:150,190,191`, which methodology §2.3 says
confer no reachability. They are not merely unused —
`as_dict()` is written into the ledger (scripts/dispatcher.py:962), so the
provenance record carries three action-eligibility verdicts that drive no branch
and three tracking markers that read `"none"` whatever the run actually did. A
record stating `action_recommended: "none"` for a run that requested changes is
worse than one that stays silent, and RQA-BR-014's obligation is exactly that a
reader can rely on the record.

Retained in intent: the deterministic derivation of achieved against required
assurance from evidence completeness and reviewer completion, and its
consumption as a gate rather than as a report. Changes: the evaluation records
only what it decides and only what something consumes; fields nothing sets are
removed rather than serialised, since RQA-FR-034 admits no justification for
them.

---

### U-VERDICT-19 — Shadow-mode historical evidence reconstruction (fail-closed, pre-cutoff only)

Disposition: salvage
Requirements: RQA-FR-011
Root cause: `built contrary` (RQA-FR-011) — that row's contrary execution is
`persist_human_approval`; search S-A shows no register row cites this unit.

The code does not survive on its own account. No requirement in the frozen
specification names shadow mode, backtesting or calibration (search S-C), and no
register row rests on this unit (search S-A), so a behaviour no frozen
requirement obliges cannot be retained on the strength of the analysis's own
record. One design decision inside it should be carried, and it is not the
reconstruction plumbing.

The mechanism to lift: **a gate reads true only from evidence the record
positively supports, and only when that evidence is timestamped at or before the
decision's own cutoff.** `before_merge_facts` sets `checks_ok`,
`adjudication_complete` and `evidence_fresh` true only when the corresponding
timestamp exists and is at or before the sample's cutoff
(scripts/shadow.py:125-150), and `historical_evidence` proves `bounded_change`
from a recorded addition count and `audit_writable` from a real write probe
instead of assuming either (scripts/shadow.py:214-281). That rule is embodied by
`scripts/shadow.py` itself and would survive a from-scratch rewrite of it.

Why nothing simpler serves RQA-FR-011, which forbids a successful disposition
while any required obligation is unsatisfied: the alternative to positive,
cutoff-bounded proof is a gate that reads true because nothing contradicted it,
and what that costs is measurable in this same tree.
`approval_evaluate.evaluate` called with no evidence object defaults all five of
these gate names to `True` (scripts/approval_evaluate.py:175-180) — an argument
that is merely omitted satisfies five obligations. This unit applies the
opposite discipline to every gate it reconstructs, which is what makes the rule
worth carrying rather than re-deriving.

Scope of the salvage, stated so it is not read wider than the unit: the
interface constraint that an evaluator should be uncallable without an explicit
evidence object is a property of `scripts/approval_evaluate.py`, which
[`../clusters.md`](../clusters.md) places in the **authority** cluster. It is
not part of this salvage, and this lane dispositions nothing in that cluster;
scripts/approval_evaluate.py:175-180 is cited above as evidence of what a
defaulting gate costs and for nothing else. Nothing of the `HistoricalSample`
model, the merge-time reconstruction or the mapping of gates onto historical
fields is carried either.

---

### U-VERDICT-20 — Shadow backtest calibration: time-ordered train/calibrate split, fitted threshold, absence-of-evidence warnings

Disposition: salvage
Requirements: RQA-BR-014
Root cause: `not built` (RQA-BR-014) — that row's unmet obligation is the
per-obligation evidence state; search S-A shows no register row cites this unit.

Same standing as U-VERDICT-19: search S-C finds no requirement naming
calibration or backtesting, and search S-A finds no register row resting on this
unit, so the code is not retained. Two of its mechanisms are explicitly not
carried either. The time-ordered train/calibrate split is an artefact of
backtesting, which nothing requires; and `learn_threshold` proposes a policy
value fitted to history — it places a ceiling just below the lowest risk score
among adverse or contested train samples that cleared every non-risk gate, and
only ever lowers the configured ceiling (scripts/shadow.py:395-437) — where
RQA-BR-004 requires the blocking threshold to be a repository policy rule. The
module's own docstring records that the learned value is advisory and that
nothing applies it (scripts/shadow.py:411-412), so it is a proposal with no
requirement behind it and no consumer, and it should not be inherited.

The mechanism to lift: **an empty or unmatched input set is reported as an
absence of evidence, distinguished by its cause, never as a result.** The report
separates three conditions — no verdicts supplied, verdicts supplied but none
matched a sample, and a gate failed for every evaluated sample — rather than
presenting the identical 0% would-approve rate all three produce
(scripts/shadow.py:512-547).

Why nothing simpler serves RQA-BR-014: that row requires a reader to confirm
from the record that the important risks and evidence were actually examined,
not to infer it from the volume of activity. A report that emits only a rate is
the artefact that defeats exactly that check — a 0% figure computed from zero
inputs is indistinguishable on its face from a 0% figure computed from a hundred
rejections, and the reader who most needs the difference is the one deciding
whether to grant an authority. Emitting the cause alongside the number is the
whole mechanism, it costs one branch, and it transfers to any summarising
artefact the replacement produces, not only to a backtest.

---

### U-VERDICT-21 — Shadow CLI entrypoints (backtest and current-shadow)

Disposition: bin
Requirements: RQA-NFR-010
Root cause: `built contrary` (RQA-NFR-010) — that row's contrary execution is
`_ledger_record`'s swallowed write on the authoritative-action paths in
`dispatcher.py`; search S-A shows no register row cites this unit.

These are the operator surface over the calibration machinery that U-VERDICT-19
and U-VERDICT-20 do not carry forward. With that machinery not retained, the two
modes have nothing to drive, and they do not earn retention independently:
search S-C shows no requirement in the specification names shadow mode, and
search S-A shows no register row cites this unit — including RQA-NFR-010, whose
`conflicting` degree and every one of its citations concern the live dispatch
and ledger paths.

What is lost, and it is real: two commands an operator is instructed to run
(`OPERATORS.md` §8.2) — a historical backtest, and `--mode current`, which
evaluates one live PR head with no mutation and no decision persistence
(scripts/shadow.py:591-609) and prints `WOULD_AUTO_APPROVE` or
`FAILED_GATES [...]` with an explicit note that it performs no mutation
(scripts/shadow.py:753-767).
Being able to ask "what would the gates decide about this PR" without touching
it is worth something to whoever turns live approval on for a repository, and
binning this removes that.

No requirement depends on it. RQA-NFR-010's obligation is that a failure during
a review leaves no ambiguous, corrupted or partially authoritative outcome; a
command that produces no outcome at all cannot discharge that obligation, and
its removal cannot breach it. If the replacement wants a preview command, it is
a preview of the rebuilt approval predicate (U-VERDICT-16), not of this one.
