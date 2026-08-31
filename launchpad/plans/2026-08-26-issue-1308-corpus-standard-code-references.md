Issue #1308 — task: document corpus standard for code references
Stated size: no Size line; cap set by the #605 batch brief  ->  cap: 5 steps

The issues in this batch carry no `Size` line. The dispatching brief settles it rather
than leaving it to be guessed: 5 steps. #636 was given 8 because it was the first node
and every convention was unsettled; these are single documents written against
conventions #636 already established, so the smaller cap is the right one.

Target file: `launchpad/docs/corpus/standards/code-references.md`
Node id: `corpus-standard-code-references` (assigned by dispatch; permanent)
Branch: `task/1308-corpus-standard-code-references`, based on `origin/task/636-corpus-agents-md`

---

ALREADY TRUE  (verified against git and the running validator, not against notes)

- `git rev-parse HEAD` -> `60d4947b7145a6ef25f185b9c25d43e43d99de3c`; `git status --short`
  is empty. The branch is `task/636-corpus-agents-md` plus nothing.
- `launchpad/docs/corpus/` contains exactly one authored node: `AGENTS.md`
  (`id: corpus-agents`). Everything else beneath it is `schema/`, which `validate.py`'s
  `EXCLUDED_TOP_LEVEL_DIRS` skips. There is no `standards/` directory yet, and no
  sibling node to point a relationship at.
- `node.schema.json` requires `id, type, status, origin, audiences, evidence`, permits
  `relationships`, and sets `additionalProperties: false` — there is no `provenance`
  field.
- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 today and prints
  `PASS  corpus validation found no errors; 1 item(s) reported unverified`. That one
  item is `corpus-agents`' commit citation.
- `launchpad/project-intelligence/CONTRACT.md` section 3 enumerates six citation
  shapes; `validate.py`'s `_classify_citation` is the only code that acts on them.
- CI runs the validator on `pull_request` and on pushes to `launchpad` for any change
  under `launchpad/docs/corpus/**`
  (`.github/workflows/launchpad-corpus-validate.yml`), so a local failure is a CI
  failure.
- The validator's behaviour has already been measured directly during planning, so
  STEP 1 is confirmation rather than discovery: `Justfile:999999` -> `ok` against a
  1005-line file (#1459); a GitHub `blob` link pinned to a full SHA naming a file that
  never existed -> `ok`; `blob/main` -> error; a bare directory -> error;
  `path:line:col` -> error; an uppercase 40-character SHA -> error.

---

FRONT-MATTER CHOICES  (decided here, not during drafting)

- `type: governance`. It is the only enum member that describes a policy node. This
  document rules on how other nodes cite code; it documents no architecture,
  capability, interface or platform. `agent` — #636's choice — would be wrong, because
  #636 *is* the file an agent harness resolves as instructions and this one is not.
- `audiences: [agent, developer, reviewer]`. `agent` and `reviewer` follow #636.
  `developer` is added because #605's Outcome line names a developer authoring a node
  ("A developer or agent can create one atomic corpus node..."), and this standard
  governs that act. That source is an issue, not a file, so the body claim resting on
  it is classified `TEAM_KNOWLEDGE` with `provided_by` naming #605 — not `INFERENCE`,
  which is the exact misclassification caught on #636. `operator` is excluded: nothing
  here is operational.
- `status: active`. `origin: launchpad`. Per the batch convention.
- No `relationships`. Every sibling standard is unmerged and `corpus-agents` is the
  only loaded node; a `relationships[].target` naming an id no node carries is a hard
  error in `find_unresolved_relationship_targets`. The absence and its reason are
  stated in the body, as #636 does.
- Provenance goes in the `evidence` ledger as `commit 60d4947b...`, the one permitted
  commit-only FACT. A second commit-only FACT would be a defect.

---

SCOPE BOUNDARY AGAINST #1314 (evidence) — the live tension

`AGENTS.md` states its citation-shape table "belongs in the evidence standard once that
lands (#1314)". #1308 is nevertheless the node for code references, and CONTRACT.md's
own §3 table marks three of its six shapes openable — file range, file line, bare path
— while a fourth, the commit form, pins a repository revision. Those four are the forms
that point at this repository's code; the remaining two, graph edge and tool result,
name tool output rather than code. The split adopted here, stated in the body rather
than resolved silently:

- This node owns how a corpus node points at code: which reference forms are permitted,
  what each one proves, pinning, positions, repo-relative resolution, and how a
  reference stays honest as code moves underneath it.
- #1314 owns the ledger itself — `FACT`/`INFERENCE`/`TEAM_KNOWLEDGE`, precedence, and
  the non-code evidence forms (tool results, graph edges, external URLs).
- The overlap is named in the body's scope section. The `AGENTS.md` forward-pointer
  that will need updating is reported as a finding, not fixed here: the brief forbids
  touching that file.

A second discrepancy, found while establishing the above and confirmed by counting both
tables: **a URL is not one of CONTRACT.md §3's six shapes.** CONTRACT.md §3's table
lists File range, File line, Bare path, Graph edge, Tool result and Commit — no URL row,
and the section contains no occurrence of "url", "http" or "github". `validate.py`
nevertheless implements a whole `_classify_url` branch that accepts a commit-pinned
GitHub `blob`/`raw` link as `ok` and reports every other URL `unverified`, and
`AGENTS.md` presents a **seven**-row table introduced by the sentence "CONTRACT.md §3
defines the six shapes", two of whose rows are URL forms CONTRACT.md does not contain.
This node therefore describes the forms `validate.py` actually accepts, names CONTRACT.md
§3 as the vocabulary for the six it does enumerate, and states plainly that the URL form
is validator behaviour not covered by that enumeration. The inconsistency itself is
filed as its own issue and named in the PR's Escalations; it is not fixed on this branch,
which may not touch `AGENTS.md` and does not own `CONTRACT.md`.

---

STEP 1  Confirm the validator's verdict for every shape the standard will rule on  [independent]
        Re-run the classification probe against `validate._classify_citation` at this
        HEAD and save the output, covering at minimum: bare file path, bare directory,
        non-existent path, `path:line`, `path:start-end`, out-of-range line, inverted
        range, line `0`, `path:line:col`, `path#fragment`, absolute path, path escaping
        the repository, path not relative to the repository root, markdown-wrapped
        path, GitHub `blob` at a full lowercase SHA, the same at an uppercase SHA, at a
        short SHA, at `main`, with no trailing path, the `tree`/`blame`/`commits`/`edit`
        verbs, `raw.githubusercontent`, the `http://` scheme, GitHub issue and PR URLs,
        `commit <sha>`, a graph edge, a tool result, an external URL, and free text.
        Every MUST and SHOULD the document later states must trace to a row in this
        output. No claim about validator behaviour enters the node from memory.
        done when: the probe has been run from the worktree and its stdout is saved to
        the scratchpad, and every citation form the document will name appears there
        with a recorded `ok` / `error` / `unverified` verdict.

STEP 2  Create the node with schema-valid front matter and its evidence ledger  [needs 1]  ← RUNS HERE
        Create `launchpad/docs/corpus/standards/code-references.md` with the front
        matter decided above and one `evidence` entry per claim the body will make,
        each classified against what STEP 1 measured and each citing a form STEP 1
        showed the validator accepts. The body may be a stub at this step.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` run from
        the worktree exits 0, names this node in no `FAIL` line, and reports exactly
        two `UNVERIFIED` items — `corpus-agents`' commit citation and this node's —
        proving the ledger rests on openable citations everywhere else.

STEP 3  Write the body  [needs 2]
        Sections in this order, each answering a definition-of-done clause:
        (1) Scope and authority — what this node governs, what it is not, that its
        authority is `node.schema.json` plus `validate.py` with CONTRACT.md section 3
        as the shape vocabulary, and the #1314 boundary above.
        (2) The reference forms and what each proves — the measured table from STEP 1;
        the verdict column is what the validator returns, the next column is what a
        passing verdict establishes, which for several forms is nothing.
        (3) MUST requirements, separated from SHOULD guidance, each traceable to a
        STEP 1 row.
        (4) Enforcement — the local command, the CI workflow, and plainly stated, the
        things a green run does not establish.
        (5) Exceptions and escalation — when a non-checkable form is legitimate, and
        what to do when a rule cannot be met.
        (6) Links, not copies — schema, ADRs, CONTRACT.md, `AGENTS.md`, #1459.
        (7) Scope and omissions — what is not covered, why no relationships, and what
        was expected but could not be verified.
        Enum member lists and the schema's field-combination matrix are linked, never
        restated: the validator never reads body prose, so a copy stays green while
        stale.
        done when: every one of the issue's eleven definition-of-done checkboxes maps
        to a named section or a front-matter field, written out clause by clause in the
        commit message body; and the forms table carries a row for each form STEP 1
        measured.

STEP 4  Verify  [needs 3]
        The negative control runs FIRST, so that every later command runs against the
        file as it will ship. Running the suites before a mutate-and-revert step, as an
        earlier draft of this plan did, means an imperfect revert — stray whitespace, an
        incompletely removed citation — satisfies the literal command sequence while
        shipping a node nothing re-checked. `review-plan` found that ordering defect in
        this plan; this is the corrected order.
        (a) Negative control: temporarily add to the node one citation the standard
        forbids — an unpinned `blob/main` link is the cheapest case — run
        `python3 launchpad/project-intelligence/corpus/validate.py`, observe it exit 1
        naming this node, then revert the edit and confirm with `git diff` that the file
        is byte-identical to its pre-control state. This shows the document's MUSTs are
        enforced rather than merely asserted.
        (b) Then, against that final file, run from the worktree, each as the last
        segment of its own command:
        `python3 launchpad/project-intelligence/corpus/validate.py` -> exit 0;
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        -> OK, which also lands the verify-gate stamp;
        `python3 -m unittest discover -s launchpad/docs/corpus/schema/tests -p "test_*.py"`
        -> OK.
        done when: the negative control was observed to exit 1 naming this node and the
        revert was confirmed byte-identical by `git diff`; all three commands in (b) then
        exit 0 against that reverted file; and `git status --short` shows only the
        intended two files: the node and this plan.

STEP 5  Commit  [needs 4]
        One commit for the node, signed off, message written to a file and applied with
        `git commit -s -F <file>` — never `-m`, because a backtick or a `$(...)` inside
        a double-quoted `-m` string is expanded by the shell and silently eats the
        message.
        done when: `git log --format='%s%n%b' -1` shows the clause-by-clause
        definition-of-done list and a `Signed-off-by:` trailer, and `git status --short`
        is empty.

---

PARALLEL  None. STEP 1 produces the evidence every later step consumes, and STEPs 2, 3
and 4 all touch the same single file, so they are sequential by the same-file rule
however separable they look. One agent executes this plan start to finish.

GATES  `review-plan` on this plan before STEP 1 — self-review, not independent, and the
report must say so. `review-code` after STEP 4. `review-tests` does not apply: the diff
adds one Markdown node plus this plan and touches no test file; if STEP 4's negative
control ever becomes a committed fixture that changes and `review-tests` applies.
`review-adjudicate` over every finding those reviewers report. Then a mandatory Codex
cross-model final pass, which must verify the document's claims by running the validator
rather than by reading prose, and must specifically hunt for holes opened by earlier
fixes. `qa` explore mode does not apply: the change adds no runtime interface, the only
executable surface is `validate.py` which this branch does not modify, and STEP 4's
negative control is the exercise of it.

BUDGET  STEP 3. Writing MUST/SHOULD rules that are each traceable to a measured verdict,
without restating the schema and without straying into #1314's territory, is where the
time goes. The second-largest risk is STEP 4's negative control, which needs a citation
forbidden by the standard yet still reachable by the validator — an unpinned
`blob/main` link is the cheapest such case.

OPEN  The issue did not decide these. They are named, not resolved.
1. Whether the citation-shape table belongs here or in #1314. `AGENTS.md` pre-assigned
   it to #1314 before #1308 existed as a drafted node. This plan puts the code-naming
   shapes here, leaves the ledger to #1314, states that split in the body, and reports
   the `AGENTS.md` pointer as a finding. If #1314 disagrees when it lands, one of the
   two nodes is edited then — a `supersedes`/`references` decision, not this issue's.
2. Whether `developer` belongs in `audiences`. #636 chose `agent, reviewer`, and the
   brief calls the question deliberately unsettled. This plan adds `developer` on
   #605's Outcome wording and says so; a later batch-wide decision may normalise it.
3. Whether ADR-0003's markdown-link wrapper is required on corpus citations.
   `_classify_url`'s docstring says the check is deliberately not enforced and that
   #605 owns the decision. This node describes the current state and does not decide it.

LEFT OUT  Deliberately excluded.
- Fixing #1459. It is a defect in already-merged code with its own issue. This node
  documents the behaviour that exists and prefers the form that is actually checked.
- Editing `launchpad/docs/corpus/AGENTS.md`. The brief forbids it; disagreements are
  reported instead.
- Declaring any relationship. Nothing resolvable exists to target.
- A second corpus node of any kind. The issue's out-of-scope list forbids it, and any
  second concept found while drafting is filed as its own issue.
- Any `generated/` artifact. `find_ownership_violations` fails closed on every non-`.md`
  file under the corpus root, including inside `generated/`, until #1316 defines the
  provenance contract.
