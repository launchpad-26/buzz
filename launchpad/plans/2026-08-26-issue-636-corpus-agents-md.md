Issue #636 — task: document AGENTS.md
Stated size: none given (no `Size` line/label) → asked Serina; she chose 30–60 minutes → cap: 8 steps

Revised 2026-08-26 after an independent cross-model review-plan pass (Codex, gpt-5.6-sol,
high effort) against the first draft. Eleven findings; all applied. That pass also refuted
one finding from the author's own self-review — see OPEN item 4 for what was withdrawn and
why, because the withdrawn reasoning is the kind that comes back.

ALREADY TRUE  (verified against git at 0052f5a7820ca4ca261efa233feb8bb53858ade6)
  #622 is merged: launchpad/docs/corpus/schema/node.schema.json is the frontmatter
    contract this document must describe rather than restate. Required fields are
    id, type, status, origin, audiences, evidence; relationships is optional; and
    `additionalProperties` is false, so the frontmatter has no field outside that set.
  The schema's own description of `evidence` calls it "The node's provenance ledger."
    There is no separate `provenance` property and adding one is a schema violation —
    verified: injecting `provenance:` yields "Additional properties are not allowed
    ('provenance' was unexpected)". The ledger IS the provenance mechanism.
  #623 is merged (PR #1422): launchpad/project-intelligence/corpus/validate.py exists
    and `just corpus-validate` runs it (Justfile:1004-1005). DEFAULT_ROOT is
    "launchpad/docs/corpus". `just corpus-validate` passes NO `--root`, so it always
    validates the real corpus and can never be pointed at a scratch tree.
  The scan excludes exactly one top-level directory by name, `schema/`. A new
    launchpad/docs/corpus/AGENTS.md WILL therefore be scanned and must carry
    schema-valid frontmatter. Not optional for this file.
  launchpad/docs/corpus/ today contains only `schema/` — ZERO real corpus content nodes.
    AGENTS.md is the first, so it can cite no sibling node as an example and can declare
    no `relationships` target: find_unresolved_relationship_targets rejects any target
    no loaded node's id matches, and today no such id exists.
  The validator does not read the Markdown body at all — `_, frontmatter, _body =
    text.split("---\n", 2)`. Every claim about body content, links, scope or one-concept
    discipline is enforced by a human or not at all.
  Citation checking is STRUCTURAL, not evidential. A bare path is checked to resolve to a
    real file inside the repo (is_file(), so a directory is rejected). A `path:line`
    citation is NOT checked against the file's length — `Justfile:999999` returns `ok`
    against a 1005-line file; filed as #1459, and this task avoids the positional forms
    because of it. A GitHub blob/raw URL must be pinned to a full 40-char SHA, but a
    pinned link to a real file proves only that the URL is well-formed. A non-GitHub URL
    and a `commit <sha>` reference both land on the non-fatal UNVERIFIED channel.
    Nothing the validator reports means a citation SUPPORTS the statement it sits under.
  find_ownership_violations fails closed on every non-.md file under the corpus root,
    including files under `generated/`, until #1316 defines the provenance contract. It
    says nothing about how MANY .md nodes exist — five valid nodes validate together —
    so the DoD's "exactly one hand-authored document" is not a property any tool checks.
  .github/workflows/launchpad-corpus-validate.yml triggers on `launchpad/docs/corpus/**`
    for pull_request and push-to-launchpad. This change is CI-gated with no workflow edit.
  This file will not only be a corpus node. `launchpad/scripts/preflight_core.py` sets
    `RULES_FILENAMES = ("AGENTS.md", "CLAUDE.md")` (line 164) and resolves the NEAREST one
    per changed path into `nearest_rules`, which is a FATAL_FIELD. Creating
    launchpad/docs/corpus/AGENTS.md therefore makes it the governing rules file surfaced
    for every future change under launchpad/docs/corpus/. That is what #605's acceptance
    criterion wants, but it means the document is read as instructions as well as
    validated as a node — so it must actually instruct, not merely describe.
  There is no mkdocs.yml anywhere in the repository — checked, so that despite
    launchpad/AGENTS.md §3 describing launchpad/docs/ as "MkDocs knowledge layer" there is
    no navigation to register and no docs build this file could break. The only workflows
    touching launchpad/docs/ are the two corpus ones above.
  `just` is NOT on PATH without `. ./bin/activate-hermit`, which must run in the SAME
    command as the recipe. Every done-when below therefore calls the interpreter directly.
  The 45 standards/template issues (#1307–#1351) are all OPEN, as are #639, #1316, #1410.
  Baseline before this plan existed: no branch, worktree, PR or plan for #636 or #639.
    That is a statement about the pre-plan baseline, not about the worktree now — this
    plan file is itself untracked in it.

STEP 1  Record the evidence base the issue demands before drafting.        [independent]
        The issue requires it BEFORE drafting: repository ref, inspected source paths and
        symbols, tests, specifications, migrations and configuration, relevant Git
        history/PRs/issues, and anything expected but NOT verified. Write it to the
        session scratchpad as a structured checklist with one section per required
        category — not a flat path list, which is satisfiable by writing nothing.
        Every category gets either at least one inspected item or an explicit
        "not verified, because …" line. Path candidates are checked with `test -f`, not
        `test -e`: the validator requires is_file(), so a directory passes a `-e` gate
        and fails two steps later as a citation error.
        done when: the note names commit 0052f5a7820ca4ca261efa233feb8bb53858ade6;
        every required category has an entry or an explicit not-verified reason; and
        every filesystem path it lists satisfies `test -f` from the worktree root.

STEP 2  Create AGENTS.md with schema-valid frontmatter and a skeleton.       [needs 1]
        id: `corpus-agents` — mirrors the file's own name so a reader maps node id to
        path without a lookup table. Chosen HERE rather than left to the builder because
        ids are never renamed: an id picked ad hoc mid-build is permanent. #1317 (the
        identifier standard) is still open, so there is no scheme to conform to yet; if
        it later prescribes a different one, that is a migration, not an edit.
        type: `agent` — decided by Serina 2026-08-26, and precedent for the remaining 45
        nodes. Reasoning: the enum's values are PRD #602's in-scope surfaces, this
        document's audience and subject are both agents, and it becomes the resolved
        AGENTS.md for the subtree (see ALREADY TRUE), which is an agent-facing surface
        in the most literal sense. `governance` was the rejected alternative — it would
        eventually absorb every process document and stop discriminating.
        status: active. origin: launchpad.
        audiences: [agent] at minimum. evidence: one entry per substantive claim. No
        `relationships` block — no other node exists to target, and inventing one is a
        hard validator error.
        The repository revision goes HERE, in the evidence ledger, because the ledger is
        the schema's provenance mechanism and no other schema-legal slot exists. It lands
        on the UNVERIFIED channel (a commit reference names no openable file), which is
        correct and non-fatal — but it means nothing enforces it, so STEP 8 checks it.
        done when: `python3` validates the file's frontmatter against
        launchpad/docs/corpus/schema/node.schema.json with zero errors — the schema
        itself, not a YAML parse, which would accept frontmatter with no `evidence` key
        at all; AND the ledger contains an entry recording
        0052f5a7820ca4ca261efa233feb8bb53858ade6.

STEP 3  Prove the validator actually scans the new node.       [needs 2]  ← RUNS HERE
        A pass that skipped the file looks identical to a pass that checked it — the
        failure this step rules out, and the class of defect (`schema/` exclusion,
        symlink escape) that cost #623 two review rounds.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0
        with the file present; AND after temporarily setting `type:` to a value outside
        the schema enum the same command exits non-zero AND its output names this node's
        id; AND the file is restored and the command exits 0 again. Asserting on the
        named id, not merely on a non-zero status: a non-zero status is produced by any
        failure, including the command not existing.

STEP 4  Write the node contract section — what a corpus node IS.             [needs 3]
        Where the file goes, the one-node-per-document rule, id stability, the closed
        enums, and the canonical-vs-generated boundary (non-.md files fail closed today;
        #1316 owns the contract that will change that). LINK to
        launchpad/docs/corpus/schema/README.md and node.schema.json rather than restating
        field lists — a second copy of an enum is a second thing to drift, and the
        validator never reads the body, so a stale copy stays green forever.
        done when: the section names the schema files by path, reproduces no enum member
        list and no field-combination matrix, and the validator still exits 0.

STEP 5  Write the evidence section — the ledger, and what validation proves.  [needs 4]
        NOT a restatement of the three classes and their field rules: those are canonical
        in node.schema.json and schema/README.md, and copying them here contradicts both
        STEP 4's anti-drift rule and the DoD's "without duplicating canonical content".
        Link them. What this section adds is the part living nowhere else: which citation
        forms the validator can check, that checking is STRUCTURAL only, that a `PASS`
        never means a citation supports its statement, that a GitHub file link needs a
        full 40-char SHA or CI fails, and that the positional `path:line` form does not
        verify the line exists (#1459) so a bare path is the safer citation today.
        done when: the section reproduces no field matrix or enum list; states the
        structural-vs-evidential distinction explicitly; states the full-SHA pin rule;
        and cites launchpad/project-intelligence/CONTRACT.md and validate.py by path.

STEP 6  Write the create / update / retire procedures.                       [needs 5]
        Three numbered procedures, each ending in the validator command. Retire is the
        one most likely to be got wrong: `status: retired`, id NEVER reused or renamed,
        inbound relationships from other nodes considered before retiring. #605's
        acceptance criterion for this file is exactly "create/update/retire one node
        without oral guidance" — this step is that criterion, and STEP 8's QA charter is
        what tests it.
        done when: all three procedures are present; each is a numbered sequence a reader
        could follow without asking a question; and each terminates in a command whose
        exit status decides success.

STEP 7  Write the scope-and-omissions section and the outbound links.        [needs 6]
        State what this document does NOT cover and who owns it: the 45 standards and
        templates (#1307–#1351), generated-content provenance (#1316), claim-type and
        flagged state (#1410), the human-facing entry point (#639). Link ADR-0028 and
        ADR-0029 by repo path. Say plainly that no sibling corpus node exists yet, so the
        frontmatter carries no `relationships` — an absence with a reason, not an
        oversight a reviewer has to guess at.
        done when: the section names each deferred area with its owning issue number, and
        every repo path it cites satisfies `test -f`. Body links are checked by hand
        here because the validator never reads the body.

STEP 8  Audit the ledger, the scope, and the changed-file set.                [needs 7]
        Four checks, none of which any tool performs:
        (a) Every substantive body claim maps to a ledger entry of the right class, and
            for each FACT the cited source is OPENED and read to confirm it actually
            supports the statement. A citation that only passes structurally, or that
            lands on the UNVERIFIED channel, does not support a FACT — either open the
            source and keep the class, or reclassify to INFERENCE with a confidence, or
            to TEAM_KNOWLEDGE with provided_by.
        (b) The revision recorded in STEP 2's ledger matches the revision actually
            inspected in STEP 1.
        (c) Scope: the document still represents ONE independently maintainable concept.
            Any second concept found while drafting is removed and filed as its own task,
            per the DoD — it is not folded in because it happened to be well-sourced.
        (d) Changed-file inventory against the merge base: `launchpad/docs/corpus/`
            contains exactly one added hand-authored .md file. Five valid nodes validate
            together, so "exactly one document" is a property only this check enforces.
        done when: all four pass; the validator exits 0; and the build report lists every
        UNVERIFIED notice with the classification decision taken for it, or states there
        were none.

PARALLEL  Nothing here may fan out. STEPs 2 and 4–8 all edit the single file
          launchpad/docs/corpus/AGENTS.md, which makes them strictly sequential
          regardless of how independent their subject matter looks. STEP 1 is the only
          step touching no repository file, and everything else needs its output.
          #639 (README.md) is genuinely independent and could run as a parallel worktree
          — but it is a different issue and a different PR, not a step of this plan.

GATES     review-plan: DONE — an independent Codex pass reviewed the first draft and its
          eleven findings are applied above. review-code after STEP 8: applies despite
          this being docs-only, because the frontmatter is machine-validated input to a
          checked-in validator, not prose. review-tests does NOT apply — no tests added,
          and #623's suite already covers the validator. review-a11y does NOT apply — no
          UI. review-adjudicate then review-final before merge, and review-final MUST be
          cross-model: three same-model passes on #120 missed what one Codex pass caught
          immediately, and this plan is a fresh data point for the same rule.
          qa explore mode APPLIES. Charter: in a scratch corpus root OUTSIDE the repo,
          follow STEP 6's procedures literally, as written, supplying nothing the document
          did not state. Exercise ALL THREE — create, update and retire — because #605's
          criterion names all three and a create-only charter cannot detect an update
          procedure that forgets provenance. Use at least two scratch nodes so retirement
          has an inbound relationship to handle. Validate with
          `python3 launchpad/project-intelligence/corpus/validate.py --root "$SCRATCH"`,
          never `just corpus-validate`, which takes no `--root` and would validate the
          real corpus while appearing to test the scratch one. Include a negative control:
          a deliberately invalid scratch node the run must reject, proving that root was
          the one scanned. Nothing from the scratch root is committed.

BUDGET    STEP 8(a). Opening every cited source and confirming it supports its statement
          is the only step whose cost scales with the ledger's length, and it is the one
          with no tool behind it — the validator reports structure and stops. It is also
          the step most likely to be quietly downgraded to "the validator passed", which
          is precisely the substitution it exists to prevent.

OPEN      1. RESOLVED 2026-08-26 by Serina: `type: agent`, and `id: corpus-agents`. Both
             are now stated in STEP 2 with their reasoning. They were listed here in an
             earlier revision, which was a defect: STEP 2 cannot write frontmatter without
             them, so a plan that both required them and forbade the builder deciding them
             blocked its own second step. An OPEN item that a step must consume is not an
             open question — it is a missing input.
          2. Forward references. The standards this document would defer to (#1307–#1351)
             do not exist. Naming them as "owned by #NNNN, not yet written" is honest but
             ages into a stale list; omitting them leaves a cold-start agent unable to
             tell a gap from an omission. STEP 7 assumes naming them is right.
          3. Whether YAML frontmatter at the top of a file that IS a rules document
             degrades it as instructions. No longer hypothetical: preflight_core.py will
             resolve this file as the nearest AGENTS.md for the subtree (see ALREADY
             TRUE), so it is handed to agents as governing rules, frontmatter first.
             Harmless to the validator and to preflight, which resolves the path without
             parsing content. Unverified against any agent harness actually reading it.
          4. WITHDRAWN, recorded because the reasoning will recur. The first draft claimed
             STEP 3's mutation clause could be satisfied by `just: command not found`
             (exit 127). The Codex pass refuted it: STEP 3's first and third clauses
             require exit 0, which 127 fails, so a missing `just` is fail-CLOSED. The
             underlying operational fact is real and kept — `just` needs Hermit activated
             in the same command — which is why every done-when now calls `python3`
             directly. The severity claim was wrong; the PATH observation was not.

LEFT OUT  launchpad/docs/corpus/README.md — that is #639, a separate PR; #636's own
          out-of-scope list forbids materially editing a second hand-authored node here.
          The generated-content provenance contract (#1316) — the validator deliberately
          refuses to guess at it and so does this document. ADR-0029's claim-type
          classification and flagged state (#1410) — that issue's work; `status: flagged`
          is simply not used. Fixing #1459 (positional citations not checked against file
          length) — a defect in merged code, filed separately; this task routes around it
          by preferring bare-path citations rather than changing the validator. Any change
          to the schema or the validator — both are merged and this task consumes them.

          AMENDED during build, 2026-08-26, authorised by Serina. ONE exception to the
          line above: `test_real_corpus_root_currently_has_no_content_outside_schema` in
          launchpad/project-intelligence/corpus/tests/test_validate.py asserted the corpus
          root is EMPTY. #636 authors the first node, so that test cannot survive this
          issue — it fails in CI via launchpad-corpus-validate.yml, not merely locally.
          It is replaced (not deleted) by an assertion of what its author's own comment
          says it was for: the root holds authored content AND none of it comes from
          schema/. Both halves are needed; the second alone is satisfied by an exclusion
          that rejects everything. Neither the review-plan self-pass nor the independent
          Codex pass caught this — the plan asserted "#623's suite already covers the
          validator" without running it against a corpus containing a node.
          CONSEQUENCE: the diff now touches tests, so review-tests JOINS the roster that
          the GATES line above says does not apply. Treat the GATES line as amended.
