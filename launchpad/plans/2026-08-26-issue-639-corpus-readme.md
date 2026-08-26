Issue #639 — task: document README.md
Stated size: none given (no `Size` line/label) → cap: 5 steps, set by the shared task
brief for #605's document children. #636 was capped at 8 because it was the first node
and every convention was unsettled; those conventions are now settled, and this is one
document written against them.

ALREADY TRUE  (verified against git at 60d4947b7145a6ef25f185b9c25d43e43d99de3c)
  Base is origin/task/636-corpus-agents-md, NOT origin/launchpad. #636's AGENTS.md has
    not merged (PR #1462), and branching off launchpad would leave this task with no
    instruction node to follow and no worked example to match.
  launchpad/docs/corpus/ contains exactly TWO entries: AGENTS.md (the one authored node)
    and schema/ (the schema's own testing infrastructure, excluded from validation by
    EXCLUDED_TOP_LEVEL_DIRS = {"schema"} at validate.py:42). So the corpus has ONE
    authored node today. A README describing a populated corpus would be fiction.
  AGENTS.md's own "Scope and omissions" table already names "The human-facing entry
    point to the corpus" as owned by #639. This document fills a gap AGENTS.md declared,
    which is why it must not duplicate AGENTS.md — the two are a declared pair.
  launchpad/docs/corpus/schema/README.md:8-12 says the schema directory "is the
    reference point #636 and #639 ... will link to." Linking to it is asked for by name.
  #605's acceptance criteria assign the agent-facing create/update/retire instructions to
    launchpad/docs/corpus/AGENTS.md ("gives a cold-start agent enough instructions to
    create/update/retire one node without oral guidance"). That criterion is #636's, not
    this one's. #605's outcome line reads "A developer or agent can create one atomic
    corpus node" — the word `developer` appears in the parent feature's own outcome.
  node.schema.json requires id, type, status, origin, audiences, evidence; permits
    relationships; and sets additionalProperties: false, so there is no `provenance`
    field and the revision must be recorded as a commit citation inside the evidence
    ledger. The `type` enum has 13 members and contains no `reference`, `index` or
    `readme` value — the choice has to be made on the merits from what is there.
  The `audiences` enum is {agent, developer, operator, reviewer}. AGENTS.md carries
    agent + reviewer. Nothing in the corpus carries `developer` yet.
  A top-level README.md under the corpus root IS scanned: discover_markdown_files
    rglobs "*.md" and excludes only schema/. It must carry schema-valid front matter —
    the file cannot be a plain README.
  find_unresolved_relationship_targets rejects any relationships[].target matching no
    loaded node's id. AGENTS.md carries id `corpus-agents`, so `corpus-agents` WOULD
    resolve today — but it resolves only on this base branch, and every sibling standard
    (#1307–#1351) is unmerged. The shared brief settles this: declare NONE.
  Citation checking is structural only. A bare path must resolve to a real FILE inside
    the repo (is_file(), so a directory citation fails). `path:line` does not check the
    line against file length (#1459) — avoid the positional forms. A `commit <sha>`
    citation lands on the non-fatal UNVERIFIED channel, as do graph-edge and tool-result
    shapes. Nothing the validator reports means a citation SUPPORTS its statement.
  The validator never reads the Markdown body: `_, frontmatter, _body = text.split(...)`.
    Every claim about body content, links, scope or one-concept discipline is enforced by
    a human or not at all.
  `python3 launchpad/project-intelligence/corpus/validate.py` is the check; Justfile:1004-1005
    wraps it as `just corpus-validate` and passes no `--root`. `just` needs Hermit
    activated in the same command, so every done-when below calls the interpreter.
  .github/workflows/launchpad-corpus-validate.yml triggers on `launchpad/docs/corpus/**`
    for pull_request and push-to-launchpad, so this change is CI-gated with no workflow edit.
  There is no mkdocs.yml in the repository — no navigation to register this file in.
  Baseline: worktree __worktrees/task-639-corpus-readme and branch task/639-corpus-readme
    created off origin/task/636-corpus-agents-md; no PR, no plan, no README.md yet.

DECISIONS THIS PLAN MAKES  (both set precedent; both are called out in the PR body)
  `type: governance`. The enum offers no reference/index value. This node's subject is
    the corpus as a governed body of documentation — what it is, what contract it is
    held to, how that contract is checked. `agent` is AGENTS.md's on the merits (it
    instructs agents); `development` is the surface for developing Buzz, not for the
    documentation corpus's own rules; `ingestion` is about getting sources in.
    `governance` is the closest true fit for a node whose subject is the corpus's own
    rules and boundaries.
  `audiences: [developer, reviewer]` — and deliberately NOT `agent`. `audiences` names
    who the node is written FOR, not everyone who might read it. This README is the
    human-facing door, and its job for an agent is to hand it to AGENTS.md, which is the
    node authored for agents. Including `agent` here would make an audience-filtered
    projection return two nodes to a cold-start agent, one of which routes it to the
    other. `developer` is claimed because #605's own outcome line addresses a developer;
    `reviewer` because the README tells a corpus-PR reviewer what a passing validation
    run does and does not establish. This is the first `developer` in the corpus and the
    first deliberate audience EXCLUSION; #636 left the question open on purpose.

STEP 1  Create launchpad/docs/corpus/README.md with schema-valid front matter          [independent]
        (id: corpus-readme, type: governance, status: active, origin: launchpad,
        audiences: [developer, reviewer], evidence ledger opened with the provenance
        commit citation for 60d4947b7145a6ef25f185b9c25d43e43d99de3c) plus the body's
        opening: what the corpus is, and what is in it TODAY — one authored node
        (AGENTS.md) beside the excluded schema/ infrastructure, with the corpus being
        built out under #605 and its 47 child tasks.
        done when: all three commands below succeed, run from the worktree root —
          `git cat-file -e 60d4947b7145a6ef25f185b9c25d43e43d99de3c` exits 0
          `python3 launchpad/project-intelligence/corpus/validate.py` exits 0
          `python3 -c "import sys;sys.path.insert(0,'launchpad/project-intelligence/corpus');import validate as v;print(sorted(n.id for n in v.load_nodes(v.repo_root()/'launchpad/docs/corpus')))"`
            prints exactly ['corpus-agents', 'corpus-readme']

STEP 2  Add the routing section — the table that sends a reader to the authoritative   [needs 1]  ← RUNS HERE
        source for each need (AGENTS.md for creating/updating/retiring a node;
        schema/node.schema.json for the front-matter contract; schema/README.md for its
        prose; schema/relationships.schema.json for edges; schema/COMPATIBILITY.md for
        enum changes; ADR-0028 and ADR-0029 for the decisions; CONTRACT.md for citation
        forms; validate.py for what is enforced). Every destination is a link, never a
        restatement — AGENTS.md's create procedure is not summarised here.
        Each destination is written as a Markdown link whose LABEL is the backticked
        repo-relative path and whose TARGET is the corpus-relative path, so both halves
        are mechanically checkable:  [`launchpad/docs/corpus/schema/node.schema.json`](schema/node.schema.json)
        done when: validator exits 0, AND every backticked repo-relative path resolves
        from the repo root, AND every Markdown link target resolves from the corpus
        directory, AND both counts are at least 6 so the check cannot pass vacuously:
          `python3 -c "import re,pathlib,sys;p=pathlib.Path('launchpad/docs/corpus/README.md');b=re.sub(r'\`\`\`.*?\`\`\`','',p.read_text().split('---\n',2)[2],flags=re.S);t=[m for m in re.findall(r'\`([^\`]+)\`',b) if '/' in m and m.endswith(('.md','.json','.py','.yml','.txt'))];l=[x for x in re.findall(r'\]\(([^)\s]+)\)',b) if not x.startswith(('http://','https://','#'))];bad=[m for m in t if not pathlib.Path(m).is_file()]+[x for x in l if not (p.parent/x.split('#')[0]).is_file()];print('paths:',len(t),'links:',len(l),'BAD:',bad);sys.exit(0 if not bad and len(t)>=6 and len(l)>=6 else 1)"`
          exits 0 and prints `BAD: []`
        (Raised by review-plan, High: the first draft scanned backtick spans only, so a
        routing table written as plain Markdown links — which is what this step asks for —
        could carry a dead link and still report `BAD: []`. Proved with a fixture.)
        (Corrected again during the post-review fix pass: the gate scanned the body
        verbatim, so a fenced code block's ``` delimiters desynchronised inline-span
        pairing and the path count silently collapsed from 13 to 1 the moment a second
        code block was added. Fenced blocks are now stripped before scanning — commands
        belong in fences, citations belong in prose. This is the documented "a fix opens
        its neighbour" shape: the fix for the review-code High added the code block that
        broke this gate, and only the >=6 floor made the collapse visible instead of
        silent.)

STEP 3  Add the "how this corpus is checked" section: the one command, what exit 0 and  [needs 2]
        exit 1 mean, that `just corpus-validate` is the same command behind Hermit, that
        CI runs it on every change under launchpad/docs/corpus/, and that UNVERIFIED
        notices are printed and never fatal. What a passing run does NOT establish is
        stated in one line and LINKED to AGENTS.md's section on it, not re-explained.
        done when: validator exits 0, AND the command string in the README is byte-identical
        to the one the Justfile and the workflow run:
          `grep -Fl "python3 launchpad/project-intelligence/corpus/validate.py" Justfile .github/workflows/launchpad-corpus-validate.yml launchpad/docs/corpus/README.md`
          lists all three files

STEP 4  Add "Scope and omissions": what this node covers, what it deliberately does not  [needs 3]
        (the create/update/retire procedure — AGENTS.md; per-type standards and templates
        — #1307–#1351, none merged; generated-artifact provenance — #1316), why the front
        matter declares NO relationships, why `agent` is absent from `audiences`, and what
        was expected but could not be verified.
        done when: validator exits 0, AND the front matter provably carries no
        `relationships` key, AND the body carries all three of this step's own markers
        verbatim — a bare substring test for "relationships" would not do, because STEP 2
        already puts that word in the body:
          `python3 -c "import yaml,pathlib,sys;t=pathlib.Path('launchpad/docs/corpus/README.md').read_text();fm,b=t.split('---\n',2)[1:];d=yaml.safe_load(fm);m=['## Scope and omissions','This node declares no \`relationships\`','\`agent\` is deliberately absent'];miss=[x for x in m if x not in b];print('MISSING:',miss);sys.exit(0 if not miss and 'relationships' not in d else 1)"`
          exits 0 and prints `MISSING: []`
        (Raised by review-plan, High: the first draft's gate passed the moment STEP 2 linked
        `relationships.schema.json`, so STEP 4 could be skipped entirely and still report
        success. Proved with a fixture carrying STEP 2's output and none of STEP 4's.)

STEP 5  Audit the finished node against its own ledger: every evidence entry has a       [needs 4]
        corresponding body claim and every substantive body claim has an entry; every
        FACT's cited source was opened and says so; exactly ONE commit-only FACT (the
        provenance entry) exists, per the convention AGENTS.md records and no tool holds.
        done when: all four succeed —
          `python3 launchpad/project-intelligence/corpus/validate.py` exits 0
          `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` exits 0
          `python3 -m unittest discover -s launchpad/docs/corpus/schema/tests -p "test_*.py"` exits 0
          `python3 -c "import yaml,pathlib;d=yaml.safe_load(pathlib.Path('launchpad/docs/corpus/README.md').read_text().split('---\n',2)[1]);f=[e for e in d['evidence'] if e['entry_class']=='FACT'];assert all(e.get('evidence') for e in f),'a FACT carries no evidence';n=sum(1 for e in f if all(c.startswith('commit ') for c in e['evidence']));print(n);assert n==1"`
          prints 1
        (Raised by review-plan, Medium: STEP 5 was the only step whose gate did not re-run
        the validator, and `all()` over a missing `evidence` key returns True vacuously, so
        a schema-invalid FACT could be miscounted as the provenance entry and mask a real
        one. Both halves fixed — the validator runs, and a FACT with no evidence now asserts.)

PARALLEL  None. All five steps write the same single file, launchpad/docs/corpus/README.md,
          so they are strictly sequential regardless of how unrelated their subjects look.
          Fanning any of them out to a subagent would produce conflicting writes to one
          path. STEP 1 is `[independent]` only in the sense that nothing precedes it.

GATES     review-code after STEP 5 (the diff is one Markdown document plus this plan).
          review-tests does NOT apply — this branch touches no test file; the suites in
          STEP 5's done-when are existing suites run as evidence, not modified.
          review-adjudicate over every finding both reviewers raise.
          A cross-model Codex final pass is mandatory per the shared brief, after
          adjudication, with an explicit APPROVE / REQUEST_CHANGES verdict.
          `qa` explore mode does NOT apply: this change adds no runtime interface. The
          only executable surface touched is the existing validator, which is run as a
          check rather than changed.

BUDGET    STEP 1 is the step most likely to overrun. Not the front-matter mechanics —
          those are settled — but the evidence ledger. Every FACT has to rest on a source
          actually opened, and the honest classification of "the corpus contains exactly
          one authored node today" is the trap: it is an observation of the tree, and the
          openable citation for it (AGENTS.md) is a file that states it is the only node
          rather than a file that enumerates the tree. Getting that entry's wording and
          class right, without repeating #636's mistake of sourcing a policy choice to a
          file that does not discuss it, is where the time goes.

OPEN      Whether `governance` is the right `type` for an entry-point/index node, or
          whether the enum is missing a value for this shape entirely. The enum is closed
          and COMPATIBILITY.md governs additions; this plan does NOT open that process —
          it picks the closest true member and flags the tension here. If a later
          standard (#1307–#1351) introduces a reference/index taxonomy, this node's `type`
          is a candidate for revision. Its `id` is not: ids are permanent.
          Whether `audiences` should name everyone who might read a node or only those it
          is authored for. This plan takes the second reading and says so; #636 left it
          open. A reviewer who takes the first reading would add `agent` here.

LEFT OUT  Any `relationships` edge, including `references: corpus-agents` — which WOULD
          resolve on this base branch. Left out because every sibling standard is
          unmerged and the shared brief settles the corpus-wide convention as "declare
          none"; edges are added in one follow-up once the set has landed, so the whole
          corpus gains its graph in a single reviewable change rather than 46 partial ones.
          Any edit to launchpad/docs/corpus/AGENTS.md, even to fix something wrong in it.
          It is #636's file, unmerged, and a second author editing it would conflict; any
          defect found there is reported, not fixed.
          Registering this file in a docs navigation — there is no mkdocs.yml to register it in.
          Restating the schema's enum members, its field-combination matrix, or AGENTS.md's
          create procedure. The validator never reads body prose, so a second copy stays
          green forever after it goes stale.
          A second hand-authored corpus node of any kind — #639's own out-of-scope list.
