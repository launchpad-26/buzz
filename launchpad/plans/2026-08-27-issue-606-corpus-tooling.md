Issue #606 — feature: agents can plan author review and maintain the corpus with deterministic tooling
Stated size: no `Size` line on the Feature issue itself — sized from its 8 child Tasks → cap: 12 steps

ALREADY TRUE  (verified against `origin/launchpad`, not the issue text)
  launchpad/docs/corpus/AGENTS.md and README.md exist and are merged (#636, #639).
  launchpad/docs/corpus/schema/ exists: node.schema.json, relationships.schema.json,
    valid/invalid fixtures, tests/test_schema.py (#622).
  launchpad/project-intelligence/corpus/validate.py exists with tests/fixtures — the
    deterministic validator + CI entry point (#623). `just corpus-validate` wraps it.
  launchpad/docs/corpus/standards/ has 2 of ~24 planned standards merged: confidence.md,
    decision-references.md. The rest are open PRs or undispatched (see OPEN).
  launchpad/docs/corpus/templates/ does not exist — 0 of 26 template docs are merged.
    ~20 have open PRs pending review/merge, 6 remain undispatched.
  .claude/skills/<name>/SKILL.md convention already exists (agentic-debugging,
    desktop-screenshot, review-final, sprout-cli) — a real pattern for #628/629/630 to follow.
  GitHub Project "Buzz delivery" (#20) already has Priority, Size, Estimate, Start date,
    Target date and Effort fields — #627 has real fields to write to.
  None of #606's own 8 child tasks have any code on `origin/launchpad`:
    launchpad/project-intelligence/corpus/{inventory,evidence,manifest,issue_plan,scaffold}.py
    and .claude/skills/{corpus-plan,corpus-author,corpus-review}/ are all absent.

STEP 1  #624 — implement deterministic Buzz source inventory        [independent]
        launchpad/project-intelligence/corpus/inventory.py discovers Rust workspace
        members, relay APIs, desktop/mobile/web features, event kinds/NIPs, migrations,
        config, test suites and existing docs, each with a stable source key and
        concrete path/symbol location. No dependency on the corpus contract — pure
        Buzz-source and repo scanning.
        done when: running inventory.py twice against the same revision produces
        byte-identical output, and `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` passes covering
        representative Rust, client, migration and event-kind discovery (full DoD: #624).

STEP 2  #625 — Git and GitHub evidence bundle collection             [independent]
        launchpad/project-intelligence/corpus/evidence.py builds reproducible bundles
        of code/test/spec plus commits, blame, PRs, reviews and issues for one planned
        node, keeping FACT/historical-discussion/ADR evidence classes distinguishable
        and excluding secret/private-source content. No dependency on #624's output or
        on the corpus contract's content — scans Git/GitHub directly.
        done when: one fixture demonstrates a bundle containing code + tests + commit +
        PR + issue evidence with stable identifiers/URLs, and its test asserts historical
        discussion is never auto-promoted to FACT (full DoD: #625).

STEP 3  #626 — generate the one-document one-task corpus manifest    [needs 1]
        launchpad/project-intelligence/corpus/manifest.py emits one row per planned
        canonical/generated document: path, filename, issue title, parent feature,
        priority, dates, effort, blockers, template, purpose, audiences and concrete
        source start points. "Source start points" are pulled from inventory.py's
        output, hence the dependency on step 1. The "template" field can name a
        template by its planned filename even where the template body isn't merged yet
        (see OPEN) — this plan does not resolve whether to block on template content.
        done when: re-running manifest.py against the same plan/revision produces no
        diff, no document is assigned to two tasks, and no Feature exceeds 100
        document-task children (full DoD: #626).

STEP 4  #632 — one-node corpus scaffold helper                       [needs 3]
        launchpad/project-intelligence/corpus/scaffold.py creates exactly one canonical
        file from a manifest row + assigned template, populating front matter from
        manifest/schema values only, refusing to overwrite existing files, and failing
        closed on an unknown manifest row or template.
        done when: tests cover create, existing-file-refusal and invalid-template cases,
        and a scaffolded file's front matter validates against node.schema.json via
        validate.py (full DoD: #632).

STEP 5  #627 — idempotent GitHub issue-plan helper                   [needs 3]
        launchpad/project-intelligence/corpus/issue_plan.py creates PRD/feature/document
        tasks from the manifest, dry-run first, with exact-title/alias duplicate guards,
        real sub-issue linking, and project-field writes to the fields confirmed to
        exist on Project #20 (Priority/Start date/Target date/Effort) — falling back to
        an explicit manual-action list where a field can't be written automatically.
        Independent of step 4 — both consume the manifest but touch different files.
        done when: `--dry-run` emits proposed issues/metadata/relationships with zero
        GitHub mutation; a second `--apply` run against the same manifest creates no
        duplicate document tasks; tests run against fixtures/mocked GitHub responses and
        cover interrupted/resumed execution (full DoD: #627).

STEP 6  #628 — create the corpus-plan agent skill                    [needs 3, 5]
        .claude/skills/corpus-plan/SKILL.md wraps manifest.py + issue_plan.py: requires
        dry-run/duplicate checks before issue creation, explains one-document=one-task
        and blocker rules, and tells the agent how to resolve aliases to live issue
        numbers.
        done when: the skill follows the existing `.claude/skills/<name>/SKILL.md`
        convention, and every helper script it invokes has its own passing test suite
        (full DoD: #628).

STEP 7  #629 — create the corpus-author agent skill                  [needs 2, 4]
        .claude/skills/corpus-author/SKILL.md wraps evidence.py + scaffold.py: starts
        from task metadata, refuses a second canonical document per task, gathers
        evidence before drafting, applies the assigned template's acceptance profile,
        keeps FACT/INFERENCE/TEAM_KNOWLEDGE distinguishable, and runs validate.py before
        proposing completion. This is the step most exposed to the templates gap — see
        BUDGET and OPEN.
        done when: the skill refuses to author a second document in the same task
        (tested against a fixture task), and a drafted node passes validate.py locally
        before the skill reports done (full DoD: #629).

STEP 8  #630 — create the corpus-review agent skill      [needs 7]  ← RUNS HERE
        .claude/skills/corpus-review/SKILL.md checks atomicity, evidence quality,
        source accuracy, graph links and public-boundary safety, separately reporting
        structural/factual/duplication/security findings, with missing evidence never
        becoming PASS, and output advisory unless validate.py finds a hard contract
        failure.
        done when: the skill's final checklist, run against one real corpus-author
        output from step 7, produces a real advisory review an independent reviewer can
        replay — this is the first point in the plan where the full plan-author-review
        loop is demonstrable end to end, even though earlier steps are individually
        testable (full DoD: #630).

PARALLEL  Steps 1 and 2 have no shared files and no dependency on each other or on the
          corpus contract's content — dispatch as independent subagents first. Steps 4
          and 5 both depend only on step 3's manifest schema and touch different files
          (scaffold.py vs issue_plan.py) — safe to dispatch together once step 3 lands.
          Steps 6, 7 and 8 are sequential in practice even though 6 and 7 don't share a
          file, because 7 and 8 both need real scaffold/manifest output to test against
          rather than fixtures alone.

GATES     review-code and review-tests apply after every step (each DoD requires its own
          passing tests, and steps 3-8 are new Python + Markdown). qa explore mode applies
          from step 5 onward: #627 has a real `--dry-run`/`--apply` CLI surface, and steps
          6-8 are agent skills meant to be run, not just read — exercise them against a
          fixture manifest row, not only unit-tested. review-a11y does not apply — no UI
          surface anywhere in this Feature.

BUDGET    Step 7 (#629, corpus-author skill) is most likely to eat the budget — it's the
          step most exposed to the templates gap (see OPEN) and carries the most
          judgment-heavy DoD (FACT/INFERENCE/TEAM_KNOWLEDGE discipline, refusing to
          invent missing project decisions).

OPEN      1. #606's issue body never states the templates dependency. Only 0 of 26
             templates are merged onto `origin/launchpad` (~20 have open PRs, 6 are
             undispatched). Steps 3, 7 and 8 can be built now against template *names*
             from the manifest, but #629's "applies the assigned template" and #630's
             "template-specific acceptance criteria" DoD items can't be fully exercised
             until more templates merge. This plan does not decide whether to build
             those steps against stubs now and re-test as templates land, or wait.
             Surfacing it, not resolving it.
          2. Standards docs are similarly incomplete (2 of ~24 merged) — validate.py and
             the review skill (step 8) may need to enforce standards that don't exist yet.
          3. No `Size` line exists on #606 itself; this plan sized off its 8 pre-scoped
             child Tasks and treated the Feature as the >1hr / 12-step tier. If #606
             should instead be split into two PRs (contract-dependent vs.
             contract-independent tooling), that's a call for whoever reads this plan,
             not one this skill makes.

LEFT OUT  #631 (corpus-maintain skill) is a child of #534, not #606 — confirmed via its
          issue body's Parent PRD field. #633/#634/#635/#552/#556/#559/#553 (graph/index
          generation, completeness accounting, change-mapping, knowledge-crate packaging)
          belong to #621/#534/#532 — different Features, out of scope here. Actually
          running this tooling against the full ~2000-document corpus is execution, not
          construction, and isn't part of this plan.
