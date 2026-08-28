# Issue #1314 — task: document corpus standard for evidence

Stated size: no Size line  ->  cap: 5 steps
(Set by the batch brief rather than asked about: these are single documents written against
conventions #636 already settled, not the first node. Recorded here so the departure from
the skill's "ask before writing anything" rule is visible rather than silent.)

Target file: `launchpad/docs/corpus/standards/evidence.md`
Node id: `corpus-standard-evidence` (assigned in the task prompt; permanent)
Branch: `task/1314-corpus-standard-evidence`, based on `origin/task/636-corpus-agents-md`
(`ebe2daf72`) because `launchpad/docs/corpus/AGENTS.md` has not merged yet (PR #1462).

---

ALREADY TRUE  (verified against git and by running the tools, not against notes)
-------------------------------------------------------------------------------

- `git rev-parse HEAD` is `ebe2daf721c7d7a96fdd84eba0a0a5d37eefa109`. `git status --porcelain`
  was empty when the worktree was cut and now reports this plan file as untracked — that
  one line is the only working-tree change at the moment STEP 1 begins.
- `launchpad/docs/corpus/standards/evidence.md` does not exist on any branch:
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` lists only
  `schema/`, and this worktree adds only `AGENTS.md` on top of it.
- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 with exactly
  **1** `UNVERIFIED` notice (`corpus-agents` entry 1 — its provenance commit citation).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  runs 79 tests, OK.
- On `origin/launchpad` the corpus contains **no** node outside `schema/`, so no
  `relationships[].target` this node could declare would resolve there.
- The three entry classes and their field rules are already enforced twice, and were
  measured here: `node.schema.json` through `validate.py`, and `memory.py`'s
  `__post_init__`. Nine negative cases were run and all nine fail closed (FACT+confidence,
  FACT+provided_by, FACT with no evidence, INFERENCE without confidence, INFERENCE without
  evidence, INFERENCE+provided_by, TEAM_KNOWLEDGE+confidence, TEAM_KNOWLEDGE without
  provided_by, unknown class).
- Measured against `_classify_citation` at `ebe2daf72`: a `FACT` citing a real file that
  says nothing on the subject passes with no notice at all; `Justfile:999999` returns `ok`
  against a 1005-line file; a `blob/<40-hex>/does-not-exist.md` link returns `ok`;
  `commit deadbeef…` (a commit that does not exist) returns `unverified`, not `error`;
  three commit-only `FACT`s in one node exit 0 with three notices; a `TEAM_KNOWLEDGE` entry
  with no `evidence` array passes; free text matching no form is a hard `error`.
- `grep -c http launchpad/project-intelligence/CONTRACT.md` returns **0** — §3's six
  shapes contain no URL form, while `validate.py` implements two.
- Two sibling standards are open and unmerged and must not be duplicated:
  `origin/task/1308-corpus-standard-code-references` (`corpus-standard-code-references`)
  and `origin/task/1309-corpus-standard-confidence` (`corpus-standard-confidence`). Both
  recorded revision `60d4947b7`, which is **three commits behind** this branch's base
  (`git rev-list --count 60d4947b7..ebe2daf72` returns 3: `a1e8bbcd0`, `806af4e41`, `ebe2daf72`).
  That gap is load-bearing, not trivia — see the `confidence.md` row below.

Decisions taken before step 1 (each is a choice this plan makes, not a fact)

**`type: governance`.** The document sets rules for authors and reviewers about a
front-matter contract; it documents no architecture, capability, platform or interface.
Both sibling standards chose the same value, so choosing differently would fragment 45
documents for no gain.

**`audiences: agent, developer, reviewer`.** Agents and developers are the two authors
#605's outcome names; reviewers are named explicitly because the largest section of this
document is rules no check can hold. `developer` is the deliberately-unsettled question —
it is included, and the reason is recorded as `TEAM_KNOWLEDGE` attributed to #605's
outcome, exactly as `corpus-standard-code-references` did, rather than asserted as fact.

**`relationships`: none, and the reason is merge order.** `corpus-agents` is loadable from
this base, so an edge to it validates here and becomes a hard error the moment this node
reaches `launchpad` ahead of PR #1462. Verified above by listing the corpus on
`origin/launchpad`. Not "the corpus is empty" — that would be false.

**Deferred material: what this node accepts, and what it hands back.** This is the batch's
most-deferred-into node, so the boundary is decided here rather than left implicit.

| Deferred item | Decision |
|---|---|
| `AGENTS.md`'s citation-shape table, which says it "belongs in the evidence standard once that lands (#1314)" | **Accept half.** Take the rows that name **no openable file** — commit, graph edge, tool result, non-GitHub URL — and the ledger-level meaning of the whole table (what a verdict does and does not establish about an entry's class). **Hand back** the code-naming rows (bare path, `path:line`, GitHub `blob`/`raw`): `code-references.md` already treats them in more detail, measured, and a second copy here is the stale-duplicate failure the conventions forbid. `AGENTS.md`'s pointer is therefore now only half right, and this node may not edit `AGENTS.md` — so that becomes a filed finding, not a silent fix. |
| **#1476** — who owns the `FACT` and ledger-composition rules | **Accept.** This node owns class assignment and ledger composition, states that explicitly, and names `code-references`' MUST 9 and §6 classification guidance as provisional against it. The residual risk — two `active` governance nodes with no declared edge between them, because no edge can be declared yet — is recorded as an omission rather than papered over. |
| **#1478** — `CONTRACT.md` / `AGENTS.md` / `validate.py` disagree on the citation forms | **Accept the statement of it, not the fix.** State it accurately from measurement: §3 enumerates six shapes and contains no URL form (zero `http` hits), `validate.py` implements a URL branch anyway, `AGENTS.md` presents seven rows as six. Derive this node's list from `validate.py` and say why. Editing `CONTRACT.md` or `AGENTS.md` is out of scope. |
| **`confidence.md`'s `## Reasoning versus deciding` section** (#1309), which states the same distinction, the same adversarial test, and the same #636 worked example | **Accept ownership; do not re-tell the shared half.** Class assignment across all three classes is this node's (#1476 decides that in this node's favour), so the distinction is stated here as the owner. What this node must NOT do is restate `confidence.md`'s test verbatim: it links to that section for how to *rate* an INFERENCE once classified, and states only the part `confidence.md` does not have. **That part is a real delta, not a courtesy**: `confidence.md` records revision `60d4947b7` and presents the #636 incident as resolved by reclassification to TEAM_KNOWLEDGE, but `a1e8bbcd0` — three commits later, on this branch's base — refused the reclassification too, and the actual resolution was to withdraw the claim. This node states all three outcomes; `confidence.md` could not have, at the revision it recorded. The staleness in `confidence.md` is a finding to file, not something this node may edit. |
| **#1463** — a NaN `confidence` passes schema but `memory.py` rejects it | **Hand back to #1309.** `confidence` is that node's whole subject. Point at it; do not restate the gap. |
| **#1459** — `path:line` not bounds-checked | **Hand back to #1308.** Verified here as part of establishing what a citation proves, but the code-form rule is `code-references`'. |

**What this node does NOT restate**, because the validator never reads body prose and a
stale copy stays green forever: enum member lists, the schema's field-combination matrix
as a table, ADR-0029's precedence rule in full, and the `confidence` bounds.

---

STEP 1  Front matter, section skeleton, and the scope-and-authority section  [independent]  <- RUNS HERE
        Create `launchpad/docs/corpus/standards/evidence.md` with the complete
        `evidence` ledger (every claim the finished document will make, classified,
        with the one permitted commit-only FACT recording `ebe2daf72`), the section
        headings with no body prose yet, and the scope-and-authority section written.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 and
        prints exactly **2** `UNVERIFIED` notices — `corpus-agents` entry 1 and this node's
        own provenance entry; AND the body is present, not just the front matter, checked
        against the document itself because the validator never reads body prose
        (`_load_frontmatter` discards it): `grep -c '^## ' launchpad/docs/corpus/standards/evidence.md`
        returns at least 8, and
        `grep -c '^## Scope and authority$' launchpad/docs/corpus/standards/evidence.md`
        returns 1 with at least 15 non-blank lines beneath it before the next `## `.

STEP 2  The ledger, the three classes, and class-differentiated supersession  [needs 1]
        Write the sections covering what the ledger is, what each of the three classes is
        *for* (not the schema's matrix), and the one place class has a mechanical
        consequence beyond validation: `memory.py`'s `record_code_contradiction` supersedes
        a FACT or INFERENCE with a new FACT and refuses to supersede a TEAM_KNOWLEDGE at
        all, so only `record_team_statement` can retire one. State plainly that this is
        `memory.py`'s behaviour for its in-process store and that the corpus ledger has no
        supersession mechanism of its own.
        done when: validator still exits 0 with 2 notices; and
        `grep -nE '"?(architecture|layers|capabilities|platforms|implementation|interfaces-events|verification|operations|development|release|governance|agent|ingestion)"?,' launchpad/docs/corpus/standards/evidence.md`
        returns no line that is an enum-member list (checked by reading each hit), and
        `grep -c 'draft.*active.*deprecated.*retired.*flagged' launchpad/docs/corpus/standards/evidence.md`
        returns 0.

STEP 3  Reasoning from evidence versus dressing up a decision  [needs 2]
        The document's centrepiece. The distinction, the adversarial test, and the worked
        example from this repository's own record: on #636 an authored policy was
        classified INFERENCE citing a schema silent on the subject, then TEAM_KNOWLEDGE
        attributed to an issue's definition of done, and a cross-model reviewer refused
        both — the third fix was to stop making the claim. State the third outcome
        explicitly: when neither class is legal, the honest artefact is a named gap, not a
        relabelled claim. Then the precedence-and-conflict section, deferring to ADR-0029
        by link for the rule and stating only what this node adds.
        done when: validator exits 0 with 2 notices; AND, checked against the document
        rather than against git history,
        `grep -c 'withdraw' launchpad/docs/corpus/standards/evidence.md` returns at least 1,
        `grep -c 'a1e8bbcd0' launchpad/docs/corpus/standards/evidence.md` returns at least 1,
        and the section between `## Reasoning from evidence, and dressing up a decision` and
        the next `## ` contains all three of `INFERENCE`, `TEAM_KNOWLEDGE` and the withdraw
        outcome (one `awk` range extraction, then three greps over it, all three returning
        non-zero). Separately — and this verifies the *source*, not the step —
        `git log -1 --format=%B a1e8bbcd0846321c6f6684acfe551096da4d974a | grep -c 'the document stops making the claim'`
        returns 1; that command is already true today and gates nothing, so it is recorded
        as source verification rather than counted as a done-condition.

STEP 4  MUST / SHOULD, enforcement and where it stops, exceptions, and the boundaries  [needs 3]
        Separate MUST from SHOULD as the issue's done-criteria require. Write the
        enforcement section as measured verdicts, including what a green run does not
        establish. Write the exception and escalation process. Write the boundary
        declarations and the read-these-instead table: #1476 ownership taken, #1478 stated,
        #1463 and #1459 handed back, the `AGENTS.md` table taken by half.
        done when: validator exits 0 with 2 notices; the document contains a `## ` heading
        whose text contains `MUST` and one whose text contains `SHOULD`, each with at least
        one numbered item; and every `#`-issue reference in the file is one of
        1308, 1309, 1316, 1321, 1410, 1459, 1463, 1476, 1478, 605, 636, 639
        (checked with `grep -oE '#[0-9]+' … | sort -u`).

STEP 5  Audit the node against its own ledger, then re-check the base  [needs 4]
        Every substantive body claim has a ledger entry; every ledger entry has a home in
        the body; every FACT's cited source was opened and says so; exactly one commit-only
        FACT; no claim about `AGENTS.md` that `AGENTS.md` no longer supports (the #1472
        failure). Then re-fetch `origin/task/636-corpus-agents-md`; if it moved, merge it
        (never rebase), re-verify every claim about `AGENTS.md`, and re-run everything.
        done when: `git fetch origin task/636-corpus-agents-md && git rev-parse origin/task/636-corpus-agents-md`
        equals this branch's merge base with it; `python3 launchpad/project-intelligence/corpus/validate.py`
        exits 0; `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        reports 79 tests OK; and
        the count of commit-only `FACT` entries is exactly **1**, from this runnable command:
        `python3 -c "import yaml; d=yaml.safe_load(open('launchpad/docs/corpus/standards/evidence.md').read().split(chr(45)*3+chr(10),2)[1]); print(sum(1 for e in d['evidence'] if e['entry_class']=='FACT' and e.get('evidence') and all(str(c).startswith('commit ') for c in e['evidence'])))"`
        printing `1`.

---

PARALLEL  **Nothing here may run in parallel.** All five steps edit the same single
          file, `launchpad/docs/corpus/standards/evidence.md`. Two steps editing one file
          are sequential regardless of how unrelated the sections look, and the ledger
          written in STEP 1 is the contract STEPs 2-4 fill in — a fan-out would produce
          body prose with no matching entries, which is the exact defect STEP 5 exists to
          catch. Run them in order, in one session.

GATES     `review-plan` on this plan (not independent — same author, and it must be
          labelled as such). Then `review-code` after STEP 5 on the whole diff.
          `review-tests` does **not** apply: this branch adds no test and edits none —
          confirm with `git diff --stat` naming only the node and this plan before
          skipping it. `review-adjudicate` over every finding. Then the mandatory
          cross-model (Codex) final pass, which is expected to fail for lack of credits
          (#1467) — attempt it, record the failure verbatim, and use `review-final` only
          as an explicitly labelled same-vendor stand-in.
          **`qa` explore mode does not apply.** This change adds one Markdown document
          and one plan; there is no runtime interface, argument surface or UI to exercise.
          The only executable behaviour in scope is the validator, which is not modified
          and is exercised directly by every step's `done when`.

BUDGET    **STEP 3 is the step most likely to overrun.** It is the one section with no
          mechanical check behind it — the distinction between reasoning and deciding is
          precisely the thing no validator can see, so its quality is a judgement call
          that invites rewriting. STEP 1's ledger is the runner-up: writing every entry
          before any body prose exists means predicting the document's claims, and a
          missed claim costs a ledger edit in a later step.

OPEN      - **The issue asks for "typed relationships appropriate to the node" and the
            answer is none.** Merge order forbids any edge that would resolve on
            `launchpad`. This is a real, stated tension with the done-criteria, not a
            silent omission, and the plan records the reason rather than the rule.
          - **#1476 is a boundary question against an already-open PR.** This node
            declares ownership of the class and ledger-composition rules, but cannot edit
            `code-references.md` to add the provisional marker #1476 asks for. Whether the
            reconciliation lands as an edit to that PR or as a follow-up on this one is
            not this plan's to decide; it is reported.
          - **Whether `AGENTS.md`'s deferral pointer should be redirected.** Half the
            table moves here and half is already owned by #1308, so the pointer
            `AGENTS.md` carries is now wrong in one direction. This node may not edit
            `AGENTS.md`, so the fix is filed rather than made.
          - **Whether a commit message is a legitimate `provided_by` value.** `AGENTS.md`
            says the field names "who or what said it: a person, an issue, a decision
            record." A commit message is a record written by a person; this plan treats it
            as acceptable and says so, but no source settles it.

LEFT OUT  - **The code-naming citation forms.** Owned by `code-references` (#1308);
            duplicating them is the failure mode, not thoroughness.
          - **The `confidence` value's meaning, bands, and the NaN gap.** Owned by #1309
            and #1463.
          - **Any edit to `launchpad/docs/corpus/AGENTS.md`, `CONTRACT.md`,
            `node.schema.json`, `validate.py`, or any sibling's file.** Out of scope by the
            task prompt and by the issue's own out-of-scope list.
          - **Restating the field-combination matrix and the enums.** Linked instead; a
            copy the checker never reads stays green after going stale.
          - **Fixing #1459, #1463 or #1478.** All three are filed defects in files this
            node does not own. Named, not repaired.
