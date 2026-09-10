---
id: governance-ownership
type: governance
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "launchpad/AGENTS.md section 3 opens with the ownership rule in two sentences -- 'Everything cohort-specific lives under `launchpad/`. Upstream owns everything else.' -- and separately states in bold 'Never move or rename upstream files', giving as its reason that upstream is approximately 3,800 files merged from regularly and a rename turns every future merge into manual work."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "launchpad/AGENTS.md section 3 lists seven deliberate exceptions to that rule, introduced as 'all accepted knowingly', then closes the list with 'The list itself is closed; any further exception needs its own ADR.'"
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "launchpad/AGENTS.md section 1 states 'We operate Buzz. We do not develop Buzz.', describes the root CLAUDE.md and AGENTS.md as upstream's contributor guide whose guidance for deployment, docs and cohort process work 'is wrong, not merely irrelevant', and states that section supersedes it for anything under launchpad/, .github/workflows/launchpad-*, and all cohort process work."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "launchpad/AGENTS.md section 3 requires that new workflows go in .github/workflows/ because GitHub requires it, and must be named launchpad-*.yml so they never collide with upstream's."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "At the recorded revision, 10 of the 30 files in .github/workflows/ carry the launchpad- prefix: launchpad-adr-check.yml, launchpad-agents-tests.yml, launchpad-corpus-schema-tests.yml, launchpad-corpus-validate.yml, launchpad-issue-check.yml, launchpad-pr-check.yml, launchpad-review-agent-controls.yml, launchpad-review-agent-publish.yml, launchpad-rqa-tests.yml and launchpad-security-audit.yml."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='.github/workflows/') -> 30 entries, 10 matching 'launchpad-', at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
      - ".github/workflows/launchpad-adr-check.yml"
  - statement: "ADR-0005 is status Accepted, sanctions exactly five upstream files to carry Launchpad values (deploy/compose/compose.yml, .github/workflows/docker.yml, deploy/compose/.env.example, Dockerfile, deploy/compose/README.md), states that the record itself is the source of truth for that list rather than the checker holding its own copy, and names launchpad/scripts/adr_boundary_check.py and the launchpad-adr-check.yml workflow as its enforcement with #153 as the task to make it required."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0005-launchpad-deployment-boundary.md"
  - statement: "ADR-0017 is status Accepted and scopes its exception to exactly bin/lefthook and bin/.lefthook-*.pkg, describing it in its own Consequences as 'a standing divergence, not a temporary one' that will conflict on every future merge from block/buzz touching those files."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0017-lefthook-pin-upstream-boundary-exception.md"
  - statement: "ADR-0043 is status Accepted, chose 'a fork-owned file that overrides, wraps, or delegates to upstream's -- never a copy', states explicitly that it 'governs the form a divergence takes, not whether one is permitted' and that section 3's exception list stays closed and this record does not add to it, and records that the divergence ledger where an in-place edit's justification is meant to live does not exist on launchpad yet, so 'this rule cannot be complied with as written' in the interim."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0043-prefer-fork-owned-overrides.md"
  - statement: "ADR-0045 is status Accepted, places cohort Rust crates under launchpad/crates/ as members of the upstream root Cargo workspace, and corrects an earlier draft of itself by stating that two upstream files diverge and not one -- the root Cargo.toml members list and Cargo.lock -- naming Cargo.lock as 'the real cost of this option rather than the members line'."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0045-cohort-crates-in-launchpad-workspace.md"
  - statement: "At the recorded revision the root Cargo.toml members list carries exactly one launchpad entry, 'launchpad/crates/knowledge', and launchpad/crates/ contains exactly one crate directory, knowledge."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/crates/') -> launchpad/crates/knowledge, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "ADR-0046 is status Proposed, not Accepted; its own Decision section opens 'Not yet settled by a human.' and states that the record becomes Accepted only when a human states the outcome in #1415, and it further states that the root .mcp.json file 'does not exist yet' and that the record decides only that adding one is permitted."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0046-root-mcp-registration-exception.md"
  - statement: "At the recorded revision there is no .mcp.json at the repository root, which is consistent with ADR-0046's own statement about itself."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='.mcp.json') -> no entry, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
      - "launchpad/decisions/ADR-0046-root-mcp-registration-exception.md"
  - statement: "ADR-0051 is status Accepted, scopes its registration seam to the single upstream file desktop/src/features/settings/ui/SettingsPanels.tsx, states that 'the cohort's own section descriptors and components live under `launchpad/`', and records in its own Consequences that 'launchpad/scripts/adr_boundary_check.py cannot see this divergence' because that checker validates only ADR-0005's deployment-file list, so 'nothing mechanically detects the seam being widened past what this record grants'."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0051-cohort-settings-registration-seam.md"
  - statement: "ADR-0053 is status Accepted and is the record section 3 names as amending ADR-0051 so that the seam owns sidebar nav-group membership as well as section registration."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0053-settings-seam-owns-nav-groups.md"
      - "launchpad/AGENTS.md"
  - statement: "At the recorded revision desktop/src/launchpad/ exists and holds two cohort-authored files -- settings/registry.ts and settings/knowledge/KnowledgeSettingsPanel.tsx -- inside upstream's desktop source tree rather than under the repository-root launchpad/ directory."
    entry_class: FACT
    evidence:
      - "desktop/src/launchpad/settings/registry.ts"
      - "desktop/src/launchpad/settings/knowledge/KnowledgeSettingsPanel.tsx"
  - statement: "SettingsPanels.tsx imports the cohort registry as '@/launchpad/settings/registry', and desktop/tsconfig.json maps the path alias '@/*' to './src/*' while desktop/vite.config.ts resolves alias '@' to '/src', so that specifier resolves to desktop/src/launchpad/settings/registry.ts and not to the repository-root launchpad/ directory."
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/ui/SettingsPanels.tsx"
      - "desktop/tsconfig.json"
      - "desktop/vite.config.ts"
  - statement: "Searching launchpad/*.md and launchpad/decisions/*.md for the string 'desktop/src/launchpad' at the recorded revision returns zero matches, so no section 3 exception bullet and no accepted decision record names that location."
    entry_class: FACT
    evidence:
      - "grep_recursive(pattern='desktop/src/launchpad', paths='launchpad/*.md launchpad/decisions/*.md') -> no matches, exit status 1, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
      - "launchpad/AGENTS.md"
  - statement: "Section 3's directory map lists 10 entries under launchpad/ while git reports 21 at the recorded revision: 9 appear in both, upstream-intel/ appears in the map and not in the tree, and 12 appear in the tree and not in the map -- six directories (Research, crates, plans, project-intelligence, review-agent, scripts) and six top-level Markdown files (ARCHITECTURE.md, ENVIRONMENTS.md, README.md, REQUIREMENTS.md, SECURITY-POSTURE.md, VISION.md)."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/') -> 21 entries; set difference against the 10 entries in section 3's code block, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "launchpad/scripts/adr_boundary_check.py checks two things and only two: that ADR-0005's table, ADR-0005's own prose count and launchpad/AGENTS.md section 3 name the same files, and that each sanctioned file no longer carries the upstream value it was sanctioned to replace; it locates the section 3 entry by the marker string 'Deployment image provenance' rather than scanning the whole document."
    entry_class: FACT
    evidence:
      - "launchpad/scripts/adr_boundary_check.py"
  - statement: ".github/workflows/launchpad-adr-check.yml runs adr_boundary_check.py on every pull request with no path filter, deliberately, and fails closed when the checker or either document is missing from the commit under check."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-adr-check.yml"
  - statement: "launchpad/AGENTS.md section 6 records that branch protection on launchpad was measured on 2026-08-28 with required_status_checks empty, so the checks visible on a pull request are informational and marking them required waits on #153 and #146."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "launchpad/scripts/security_audit_classifier.py answers ownership from upstream tree membership rather than from a path prefix: classify() returns 'inherited' when a path is present in block/buzz's default-branch tree and 'fork-added' when it is absent, and divergence() returns one of fork-added, inherited-modified, inherited-identical or indeterminate, with only inherited-identical licensing a caller to treat a file as none of the cohort's business."
    entry_class: FACT
    evidence:
      - "launchpad/scripts/security_audit_classifier.py"
  - statement: "launchpad/scripts/security_audit_classifier.py returns 'indeterminate' for every path when upstream is unreachable, and its module docstring gives the asymmetry as the reason: calling an inherited file fork-added makes the audit permanently red over files nobody here wrote, and calling a fork-added file inherited makes the audit blind to exactly the files it exists to watch."
    entry_class: FACT
    evidence:
      - "launchpad/scripts/security_audit_classifier.py"
  - statement: "corpus-standard-naming's MUST 3 requires a document's id to be formed by stripping .md, lowercasing the stem, prefixing with 'corpus-', and inserting the containing subdirectory's singular form, which would give this node the id corpus-governance-ownership rather than governance-ownership."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/naming.md"
  - statement: "corpus-standard-normative-language's MUST 1 requires a statement intended to bind an author or reviewer of this repository's corpus or decision documents to use MUST, MUST NOT, SHOULD, SHOULD NOT or MAY in full capitals, and its MUST 4 requires MUST-class and SHOULD-class statements to be separated so a reader can tell which class a statement belongs to without reading every sentence."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/normative-language.md"
  - statement: "corpus-standard-linking's MUST 5 states that restating another source's enumerated or precisely-bounded rule set in place of linking to it is a defect rather than a convenience, whether or not the restatement is currently accurate."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/linking.md"
  - statement: "Issue #2037 records that desktop/src/launchpad/ is cohort code in upstream's tree appearing in no section 3 exception."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#2037"
  - statement: "Issue #2033 records that launchpad/AGENTS.md documents launchpad/upstream-intel/, which does not exist."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#2033"
  - statement: "Issue #2029 records that the corpus id convention settled on <directory>-<stem> without a corpus- prefix, against corpus-standard-naming's MUST 3, and that 179 of 229 merged content nodes omit the prefix."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#2029"
  - statement: "Issue #914's Definition of Done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and an exception/escalation process, and link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#914 definition of done"
  - statement: "Issues #913 (governance/maintainers.md) and #907 (governance/codeowners.md) are open, unmerged sibling tasks under the same parent feature, so neither is a valid relationship target and neither's subject is absorbed here."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#913 and launchpad-26/buzz#907"
  - statement: "This repository now carries two independent encodings of the same ownership question -- section 3's path-prefix rule, which says where cohort files belong, and security_audit_classifier.py's provenance rule, which says who wrote a file -- and they answer different questions, so a file can be correctly classified fork-added by the script while sitting in a location section 3 does not permit."
    entry_class: INFERENCE
    evidence:
      - "launchpad/AGENTS.md"
      - "launchpad/scripts/security_audit_classifier.py"
      - "desktop/src/launchpad/settings/registry.ts"
    confidence: 0.85
  - statement: "Nothing mechanical enforces section 3's location rule at the recorded revision: adr_boundary_check.py validates only ADR-0005's five-file list, ADR-0051 records in its own text that the same checker cannot see the Settings seam, and no other script under launchpad/scripts/ reads section 3's directory map or its exception bullets."
    entry_class: INFERENCE
    evidence:
      - "launchpad/scripts/adr_boundary_check.py"
      - "launchpad/decisions/ADR-0051-cohort-settings-registration-seam.md"
      - "launchpad/AGENTS.md"
    confidence: 0.8
relationships:
  - type: depends-on
    target: corpus-agents
  - type: implements
    target: corpus-template-policy
  - type: references
    target: corpus-standard-decision-references
---

# Policy: the upstream/fork ownership boundary

Which files in this repository the launchpad-26 cohort owns, which belong to
`block/buzz`, and what a contributor MUST do when a change would cross that line. This
node states requirements on **where cohort work goes and what form a permitted
divergence takes**; it does not restate the exception list, which has exactly one home.

**Read this before touching any file outside `launchpad/`.**

## Scope and authority

**This node governs** the ownership boundary between this fork and its upstream: the
default rule that cohort work lives under `launchpad/`, the discipline that governs a
permitted divergence from that default, and what a contributor or reviewer MUST verify
before treating a file outside `launchpad/` as theirs to edit.

**Its authority is derived, not original.** Every requirement below restates an
obligation already imposed by `launchpad/AGENTS.md` §3 or by an accepted decision
record, expressed here in RFC 2119 keywords so it can be cited in a review. This node
creates no new obligation, grants no exception, and cannot widen or narrow the list §3
holds.

**Where this node and `launchpad/AGENTS.md` disagree, `launchpad/AGENTS.md` wins** —
it names itself the normative spec for how work is filed, reviewed and merged in this
fork, and this node has drifted and should be fixed. Where `launchpad/AGENTS.md` and an
accepted ADR disagree, the ADR is the record and §3 is the summary: §3's own convention
is that an amending ADR is applied to §3 in the same pull request, so a disagreement
between them is a defect in one of the two rather than a precedence question. Where §3
and the **repository tree** disagree, **the tree is the fact and the disagreement is a
finding** — two such findings are recorded under *Where the boundary has drifted from
the tree* below, and neither is resolved here.

| For | Read |
|---|---|
| The boundary rule and its complete exception list | `launchpad/AGENTS.md` §3 |
| Why this fork operates rather than develops Buzz | `launchpad/AGENTS.md` §1 |
| The deployment-provenance exception and its five files | `launchpad/decisions/ADR-0005-launchpad-deployment-boundary.md` |
| The Hermit lefthook pin exception | `launchpad/decisions/ADR-0017-lefthook-pin-upstream-boundary-exception.md` |
| Override versus in-place edit, once a divergence is permitted | `launchpad/decisions/ADR-0043-prefer-fork-owned-overrides.md` |
| Cohort Rust crates in the root workspace | `launchpad/decisions/ADR-0045-cohort-crates-in-launchpad-workspace.md` |
| Root MCP registration (**`Proposed`, not accepted**) | `launchpad/decisions/ADR-0046-root-mcp-registration-exception.md` |
| The Desktop Settings registration seam | `launchpad/decisions/ADR-0051-cohort-settings-registration-seam.md`, as amended by `launchpad/decisions/ADR-0053-settings-seam-owns-nav-groups.md` |
| What is mechanically checked | `launchpad/scripts/adr_boundary_check.py`, `.github/workflows/launchpad-adr-check.yml` |
| How ownership is computed from upstream provenance | `launchpad/scripts/security_audit_classifier.py` |
| How to cite a decision record from a corpus node | `launchpad/docs/corpus/standards/decision-references.md` |

## Why the boundary exists

`launchpad/AGENTS.md` §1 states the premise in five words: *"We operate Buzz. We do not
develop Buzz."* The fork's typical change is Ansible, CI/CD, docs and relay config; the
upstream's is Rust crates, desktop React and mobile Flutter. That is not a preference
about taste — it is what makes the fork maintainable.

§3 gives the mechanical reason for the strictest part of the rule, the prohibition on
moving or renaming an upstream file: upstream is roughly 3,800 files, the fork merges
from it regularly, and *"a rename turns every future merge into manual work."* Every
requirement below is downstream of that one sentence. The cost of a boundary violation
is not paid at the moment of the edit; it is paid on every subsequent merge, by whoever
is holding the conflict.

**Two different questions are being answered, and conflating them is the common
mistake.** "Who wrote this file" is a provenance question, answered by whether the path
exists in `block/buzz`'s tree. "Where does this file belong" is a location question,
answered by §3. `launchpad/scripts/security_audit_classifier.py` implements the first
and knows nothing about the second: its `classify()` returns `inherited` for a path
present upstream and `fork-added` for one absent, and its `divergence()` refines that
into `fork-added`, `inherited-modified`, `inherited-identical` or `indeterminate`, with
only `inherited-identical` licensing a caller to treat a file as none of the cohort's
business. A cohort-authored file placed inside an upstream directory is correctly
`fork-added` to that script **and** a §3 location violation. The script is not wrong;
it is answering the other question.

## MUST

These bind every contributor and every agent working in this repository. Identifiers
`O1`–`O9` are this node's own and are stable once published.

| # | Requirement |
|---|---|
| **O1** | Cohort-specific work MUST be created under `launchpad/`. Upstream owns every other path in the repository. This is §3's opening rule, restated in citable form; §3 is where it lives. |
| **O2** | An upstream file MUST NOT be moved or renamed. There is no exception to this and none may be granted by a pull request — §3 states it in bold and gives the merge cost as the reason. |
| **O3** | A contributor MUST NOT edit a file outside `launchpad/` unless that file is named by a §3 exception bullet. The list is closed; §3 states that *"any further exception needs its own ADR."* |
| **O4** | A proposed new exception MUST be raised as an ADR issue and settled by a human before the edit lands. `launchpad/AGENTS.md` §5 rule 1 reserves an ADR outcome for a human, and §4 requires the decision to be written to `launchpad/decisions/ADR-XXXX-slug.md` in the pull request that closes its issue. An agent MUST NOT decide a boundary exception on its own judgement. |
| **O5** | This node, and any other document summarizing the boundary, MUST NOT restate §3's exception list. `corpus-standard-linking` MUST 5 makes an enumerated rule set restated in place of a link a defect regardless of current accuracy, and `ADR-0005` independently records that a further copy of its file list *"would be the very defect being checked for."* Link; do not copy. |
| **O6** | Where a divergence is permitted, a fork-owned file that overrides, wraps or delegates to upstream's MUST be preferred to an in-place edit, and a **copy** of an upstream file MUST NOT be created. `ADR-0043` states the override/copy distinction explicitly and prohibits copies. |
| **O7** | Where no override mechanism exists and an in-place edit is therefore taken, the reason MUST be recorded. `ADR-0043` names the divergence ledger as that reason's durable home, and states plainly that the ledger does not exist on `launchpad` yet — so until it does, the reason goes in the pull-request body and the row is owed. See *Exceptions and escalation*. |
| **O8** | A new GitHub Actions workflow added by this cohort MUST be named `launchpad-*.yml`. §3 requires it so cohort workflows never collide with upstream's; `.github/workflows/` is the only permitted location because GitHub requires it. |
| **O9** | A claim that a specific file is cohort-owned or upstream-owned MUST be checked against the tree before it is relied on, not restated from §3's directory map. That map is out of date at the recorded revision — see *Where the boundary has drifted from the tree*. |

## SHOULD

| # | Guidance |
|---|---|
| **G1** | Before proposing a new exception, a contributor SHOULD check whether an existing seam already covers the case. `ADR-0051` exists precisely so that a second, third or tenth cohort Settings panel costs zero further upstream edits; reaching for a new ADR when a granted seam already applies spends a human decision for nothing. |
| **G2** | A boundary question SHOULD be resolved by opening the ADR, not by reading §3's summary bullet. Two claims in §3's own bullets did not survive being checked against their records at the recorded revision — see *Where the boundary has drifted from the tree*. §3 is an index; the ADR is the record. |
| **G3** | An exception's cost SHOULD be stated in the ADR that grants it, in terms of the future merges it will conflict on. `ADR-0017` and `ADR-0045` both do this, and `ADR-0045` corrects its own earlier draft to name `Cargo.lock` rather than the `members` line as the real cost. An exception whose cost is unstated cannot be weighed against the next one. |
| **G4** | A cohort file placed near upstream code for a technical reason SHOULD be named in the ADR that permits it, by full repository path. The `desktop/src/launchpad/` case in *Where the boundary has drifted from the tree* is what happens when it is not: the location is invisible to every search a reviewer would run. |

## Enforcement

**One narrow slice of the boundary is mechanically checked. The rest is review.**

`launchpad/scripts/adr_boundary_check.py` checks exactly two things, and both are
scoped to `ADR-0005`: that the ADR's table, the ADR's own prose count and §3 name the
same five files; and that each of those files no longer carries the upstream value it
was sanctioned to replace. It locates the §3 entry by the marker string
`"Deployment image provenance"` rather than searching the whole document — its own
comments record that a plain whole-document substring search was a real defect it was
written to fix. `.github/workflows/launchpad-adr-check.yml` runs it on every pull
request with no path filter, deliberately, and fails closed if the checker or either
document is missing from the commit under check.

**What that check does not establish**, stated because a green run is easy to
over-read:

| Not established | Consequence |
|---|---|
| That any exception other than `ADR-0005`'s is honoured | `ADR-0051` records this about itself: the checker *"cannot see this divergence"*, so *"nothing mechanically detects the seam being widened past what this record grants"* |
| That cohort-authored files are under `launchpad/` | Nothing reads §3's directory map or its location rule; the `desktop/src/launchpad/` case below is invisible to every check in the repository |
| That §3's directory map matches the tree | Twelve tree entries are absent from the map and one map entry is absent from the tree, and the run is green |
| That a new workflow is named `launchpad-*.yml` | O8 is held by review alone |
| That an in-place edit carries a recorded reason | `ADR-0043`'s ledger does not exist yet, so there is nothing to check against |
| That the check is required to pass before merge | §6 records `required_status_checks` as **empty** as of 2026-08-28; the checks visible on a pull request are informational, and making them required waits on #153 and #146 |

**Review is the enforcement mechanism for everything above.** That is by design for the
same reason `ADR-0005` gives when it distinguishes a deterministic check from a model
verdict — *"Scripts gate. Model output annotates."* — but it means the boundary's
location rule currently rests entirely on a reviewer noticing.

## Where the boundary has drifted from the tree

Two divergences between §3 and the repository were measured at the recorded revision,
not inferred. Both are filed; neither is fixed here. They are recorded because O9 exists
because of them.

### Cohort code inside upstream's desktop tree

`desktop/src/launchpad/` exists and holds two cohort-authored files:
`settings/registry.ts` and `settings/knowledge/KnowledgeSettingsPanel.tsx`. That path is
inside upstream's desktop source tree, not under the repository-root `launchpad/`
directory.

`ADR-0051`, which grants the Settings seam, scopes it to the single upstream file
`desktop/src/features/settings/ui/SettingsPanels.tsx` and states that *"the cohort's
own section descriptors and components live under `launchpad/`."* At the recorded
revision they do not. `SettingsPanels.tsx` imports the registry as
`@/launchpad/settings/registry`; `desktop/tsconfig.json` maps `@/*` to `./src/*` and
`desktop/vite.config.ts` resolves `@` to `/src`, so that specifier resolves to
`desktop/src/launchpad/settings/registry.ts`. The alias is what makes the location easy
to miss: the import **reads** as though it points at the repository-root `launchpad/`
directory, and it does not.

Searching `launchpad/*.md` and `launchpad/decisions/*.md` for the string
`desktop/src/launchpad` returns **zero matches**. No §3 exception bullet and no accepted
decision record names that location. Filed as
[#2037](https://github.com/launchpad-26/buzz/issues/2037).

Note what this does *and does not* mean. The files are correctly `fork-added` to
`security_audit_classifier.py` — they are absent from upstream's tree, so the cohort
plainly wrote them. What is unresolved is the location rule, which no script reads.

### §3's directory map does not match `launchpad/`

§3's code block lists ten entries under `launchpad/`. `git ls-tree` reports twenty-one
at the recorded revision. Nine appear in both.

- **One map entry has no tree entry:** `upstream-intel/`. Filed as
  [#2033](https://github.com/launchpad-26/buzz/issues/2033).
- **Twelve tree entries have no map entry:** six directories — `Research/`, `crates/`,
  `plans/`, `project-intelligence/`, `review-agent/`, `scripts/` — and six top-level
  Markdown files — `ARCHITECTURE.md`, `ENVIRONMENTS.md`, `README.md`, `REQUIREMENTS.md`,
  `SECURITY-POSTURE.md`, `VISION.md`.

`launchpad/crates/` is the sharp one: §3's **own exception list** grants it by name via
`ADR-0045`, while §3's directory map three paragraphs earlier omits it. The two halves
of one section disagree about the same directory. `launchpad/scripts/` is the second:
it holds `adr_boundary_check.py`, the script that enforces the boundary the map is
describing.

The map is illustrative, not normative — nothing reads it — but O9 exists because a
reader cannot tell that from looking at it, and an omitted directory reads as an
unsanctioned one.

### A third observation, not filed

`ADR-0046` is `status: Proposed`, not `Accepted`. Its own Decision section opens *"Not
yet settled by a human."* and states that the record becomes `Accepted` only when a
human states the outcome in #1415. §3 introduces its seven bullets as *"The deliberate
exceptions, all accepted knowingly"* — a description that does not hold for the root
MCP registration bullet at the recorded revision. Consistent with the ADR's own account
of itself, no `.mcp.json` exists at the repository root, so the unaccepted exception is
also unused. This is recorded as measured, not filed as a defect: whether §3's
introductory phrasing should be narrowed, or the record accepted, is a human's call and
not this node's.

## Exceptions and escalation

**There is no exemption from O2.** Moving or renaming an upstream file is prohibited
outright. No ADR at the recorded revision grants one, and §3 states the rule without a
carve-out.

**Every other departure runs through an ADR, and only a human closes it.** The path is
§3's and `launchpad/AGENTS.md` §4's, not this node's invention: file an ADR issue
(`type:adr`, plus `needs-decision`, which §5's *Filing an issue* records the CLI does
not apply automatically);
a human decides; the accepted record is written to `launchpad/decisions/` in the pull
request that closes the issue; §3's list is amended in that same pull request so the two
documents do not disagree. `ADR-0046` and `ADR-0051` both document following exactly
this sequence, and `ADR-0045` records what happens when it is short-circuited — an
earlier automated pass left #1409's chosen option blank and the outcome *"decided
automatically"* and *"not personally selected"*, and the record stayed `Proposed` until
a named human picked.

**An agent MUST NOT decide a boundary exception.** `launchpad/AGENTS.md` §5 rule 1
withholds it; the delegated-authority conditions in that section may let an agent
*record* a human's ruling, and never let it supply one. That is `launchpad/AGENTS.md`'s
rule and its full conditions live there — this node does not restate them, per O5.

**A permitted divergence still owes a form decision.** Once an exception exists, `ADR-0043`
decides *how*: override, not in-place edit; never a copy. Where no override mechanism
exists, the in-place edit is allowed **with its reason recorded**. `ADR-0043` states
that the ledger meant to hold that reason does not exist yet and that, in consequence,
*"this rule cannot be complied with as written"* — so the interim practice it names is
the pull-request body alone, with a ledger row owed once `ADR-0047` lands. Do not read
the missing ledger as permission to skip the reason.

**A boundary question raised in review is not settled in review.** `ADR-0005`'s
deployment-provenance exception is explicitly marked settled in §3 — *"do not raise it
as a §3 violation in review"* — and adding a sixth file to it is a change to that
record, not a call to make in a pull request. The same shape applies to every other
granted exception: a reviewer may find that a change exceeds what an ADR grants, and the
remedy is a new ADR issue, not a negotiated widening in a thread.

**A case none of this covers is escalated, not invented.** File it against the parent
feature (#619) or as a standalone ADR issue describing the boundary question that could
not be answered. Do not resolve it locally: a boundary each contributor quietly
reinterprets has stopped being one, and no check in this repository will notice.

## Scope and omissions

**This node covers** the upstream/fork ownership boundary as it stands at the recorded
revision: the default location rule, the prohibition on moving or renaming upstream
files, the closed-list discipline for exceptions and how a new one is raised, the
override-first rule governing a permitted divergence's form, what is mechanically
checked and what is not, and two measured divergences between §3 and the tree.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The exception list itself — which files are sanctioned, and their contents | `launchpad/AGENTS.md` §3 and the ADR behind each bullet. Restating it here would violate O5 |
| Who reviews and approves a change, and with what authority | `launchpad/AGENTS.md` §5 and `ADR-0052`; and `governance/maintainers.md` |
| Which reviewers GitHub requests automatically for a path | `governance/codeowners.md`. No `CODEOWNERS` claim is made here |
| The divergence ledger's contract and format | `ADR-0047` (#294), open at the recorded revision |
| Making the boundary check a required status check | #153, with #146 |
| A mechanical check for the location rule, or for exceptions other than `ADR-0005`'s | Unowned at the recorded revision. `ADR-0051` names #1499 as carrying the wider gap |
| How to cite a decision record from a corpus node | `corpus-standard-decision-references` |
| Whether §3's directory map should be normative or is illustrative | Unsettled. #2033 asks only that it match the tree |

**This node's `id`.** It is `governance-ownership`, following the `<directory>-<stem>`
convention that the merged corpus overwhelmingly uses. `corpus-standard-naming` MUST 3
as written would require `corpus-governance-ownership`. That conflict is not this node's
to settle and is tracked at
[#2029](https://github.com/launchpad-26/buzz/issues/2029); the tension is recorded here
rather than resolved silently in either direction.

**Relationships.** Three are declared, each resolving against `origin/launchpad` at the
recorded revision rather than against this worktree:

- `depends-on: corpus-agents` — this node's authority over its own construction (its
  evidence classes, its provenance ledger, its citation discipline) is `corpus-agents`',
  not its own.
- `implements: corpus-template-policy` — this node is a concrete instance of that
  template's policy shape, which is the direction `relationships.schema.json`'s own
  worked example describes for `implements`.
- `references: corpus-standard-decision-references` — this node cites seven decision
  records, and that standard governs how a corpus node does so.

No edge declared to `governance-maintainers` or `governance-codeowners`: at the
recorded revision neither existed, and a `relationships[].target` naming an id no
loaded node carries is a hard validation error. Both have since landed in this same
integration. Wiring them in now, under the pressure of a pre-merge fix pass, risks the
same kind of error this fix pass exists to catch; adding them belongs to a dedicated
pass across the whole `development`/`governance`/`releases` shelf once all 37 nodes are
stable.

**Expected but not verified when this node was written:**

- **No upstream fetch was performed.** Every claim about what is cohort-owned rests on
  §3, on the ADRs, and on this repository's tree. `security_audit_classifier.py` is
  described from its source; it was **not run**, so no path in this document has been
  classified `fork-added` or `inherited` by the script itself. The `desktop/src/launchpad/`
  claim rests on the files' absence from any §3 exception, not on an upstream tree
  comparison.
- **`adr_boundary_check.py` was not executed.** Its behaviour is read from its source
  and its docstring. Whether it currently exits 0 against this revision is unverified.
- **No CI run has exercised this node.** All validator evidence is local to this
  worktree.
- **The five files `ADR-0005` sanctions were not opened.** The ADR's table and §3's
  bullet were read and agree; whether each file actually carries its Launchpad value
  today is what `adr_boundary_check.py` exists to assert, and that assertion was not run.
- **`ADR-0051`'s *Related* section describes `ADR-0043` as `status: Proposed`.** At the
  recorded revision `ADR-0043` is `Accepted` — the commit accepting it is in this
  branch's history. That cross-reference is stale rather than wrong-at-writing, and no
  attempt was made here to establish whether any conclusion in `ADR-0051` depends on it.
- **Whether §3's directory map is intended as normative** was not established. It is
  treated as illustrative above because nothing reads it, which is an argument from
  absence of enforcement, not from a stated intent.
