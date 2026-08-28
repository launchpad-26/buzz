Issue #608 — feature: canonical Buzz architecture corpus exists
Stated size: no `Size` line on the Feature issue itself, sized from its 47 pre-scoped child Tasks (#652-#698) the same way #606 was sized from its 8  ->  cap: 12 steps

(">1hr" tier. At 47 children, 1 step per child — what #606 did — blows the cap by
~4x, so this plan batches by the 5 natural document categories instead. See PARALLEL
and OPEN item 3 for why that's a right-sizing call, not a scope change.)

ALREADY TRUE  (verified against `origin/launchpad`, not the issue text)
  launchpad/docs/corpus/schema/node.schema.json and relationships.schema.json exist,
    merged (#622). `type` is a closed enum of 13 values; every node this plan produces
    uses `type: architecture` (PRD #602's own top-level taxonomy — no finer-grained
    container/context/deployment/flow/principle enum exists at the schema level).
    Required fields: id, type, status, origin, audiences, evidence. `relationships` is
    optional.
  launchpad/project-intelligence/corpus/validate.py exists, tested, wired to CI
    (#623). `just corpus-validate` runs it against `launchpad/docs/corpus` by default.
  launchpad/docs/corpus/AGENTS.md and README.md exist, merged (#636, #639). AGENTS.md
    states explicitly: "Until the standards land there is no per-type template to
    follow: write the node against node.schema.json and the rules above, and expect a
    later task to reshape it." This is the corpus's own governing instruction, not an
    inference — it is why this plan does not wait on #605/#606.
  launchpad/docs/corpus/templates/ does not exist — 0 of 26 templates are merged.
  launchpad/docs/corpus/standards/ has 2 of ~24 merged: confidence.md,
    decision-references.md. Both use a `corpus-standard-<slug>` id convention; README
    uses `corpus-readme`. No architecture-specific id convention exists yet — this
    plan proposes `architecture-<category>-<topic>` (e.g.
    `architecture-containers-agent-runtime`), matching the file path. Not dictated by
    any issue; flagged in OPEN.
  launchpad/docs/corpus/architecture/ does not exist — zero nodes authored under #608.
    None of its 47 child Task issues have any commit on `origin/launchpad`.
  All 47 children are `type:task` (repo convention: "Bounded work — one branch, one
    PR" per the label description) and are already fully DoD'd, individually — this
    plan does not re-derive their scope, only sequences dispatch.
  The 47 children fall into 5 disjoint categories by file path, confirmed via
    `trackedIssues`:
      containers   10   #652-#661   architecture/containers/*.md
      context       6   #662-#667   architecture/context/*.md
      deployment    7   #668-#674   architecture/deployment/*.md
      flows        14   #675-#688   architecture/flows/*.md
      principles   10   #689-#698   architecture/principles/*.md
  Each category shares one DoD tail beyond the common 7-bullet corpus checklist
    (verified against one representative issue per category: #652 containers, #663
    context, #668 deployment, #675 flows, #689 principles):
      containers   responsibility/technology/ownership boundary; inbound/outbound
                   interfaces; deployment/data/security links; implementation link.
      context      every directly relevant actor/system + relationship to Buzz;
                   diagram-as-code where it adds clarity; no container-level detail.
      deployment   environment/topology + execution nodes; container-to-node mapping;
                   network/persistence/trust boundaries without exposing secrets;
                   deployment automation as authority + failure/recovery behavior.
      flows        trigger/preconditions/termination; ordered interactions and
                   data/state movement; auth/trust-boundary crossings; failure/abort/
                   rollback behavior + representative verification link.
      principles   the invariant as one unambiguous property (MUST/MUST NOT only where
                   normative); scope; enforcement points + observable failure; at least
                   one verification/conformance link, or an explicit "missing" note.
  No `.claude/skills/corpus-*` exist yet (#628/629/630, part of #606, not merged) — the
    intended corpus-author/corpus-review workflow isn't available. Authors work
    directly against node.schema.json + AGENTS.md + validate.py, per AGENTS.md's own
    instruction above.

STEP 1  Author the 10 containers documents (#652-#661)          [independent]  ← RUNS HERE
        Each of the 10 pre-existing child issues is dispatched independently: one
        branch, one PR, per the repo's `type:task` convention. Each node uses
        `type: architecture`, an `architecture-containers-<topic>` id, and satisfies
        the containers DoD tail above. Evidence is gathered per-node from the
        container's actual source (Rust crate / desktop / mobile / relay code), not
        invented.
        done when: all 10 files exist at their issue-named paths under
        `launchpad/docs/corpus/architecture/containers/`, `just corpus-validate`
        passes with zero errors against the full corpus tree, and each file's DoD
        checklist (per its own issue) is satisfied.

STEP 2  Author the 6 context documents (#662-#667)               [independent]
        Same dispatch pattern as step 1, scoped to
        `architecture/context/*.md` and the context DoD tail.
        done when: all 6 files exist, `just corpus-validate` passes, each satisfies
        its issue's DoD checklist.

STEP 3  Author the 7 deployment documents (#668-#674)             [independent]
        Same dispatch pattern, scoped to `architecture/deployment/*.md` and the
        deployment DoD tail. Explicitly exclude secrets/live private infrastructure
        detail per PRD #602's own security-implications section.
        done when: all 7 files exist, `just corpus-validate` passes, each satisfies
        its issue's DoD checklist, and none names a live secret/credential/private
        host detail.

STEP 4  Author the 14 flows documents (#675-#688)                 [independent]
        Same dispatch pattern, scoped to `architecture/flows/*.md` and the flows DoD
        tail. Largest and most narratively demanding category — see BUDGET.
        done when: all 14 files exist, `just corpus-validate` passes, each satisfies
        its issue's DoD checklist.

STEP 5  Author the 10 principles documents (#689-#698)            [independent]
        Same dispatch pattern, scoped to `architecture/principles/*.md` and the
        principles DoD tail.
        done when: all 10 files exist, `just corpus-validate` passes, each satisfies
        its issue's DoD checklist.

STEP 6  Full-tree integration check                        [needs 1, 2, 3, 4, 5]
        Run `just corpus-validate` once against the complete merged
        `architecture/` tree (all 47 files present), not per-category. This is the
        only point where cross-category id collisions or dangling relationship
        targets between categories would surface — each step's own validate.py run
        only sees what had merged by that point.
        done when: `just corpus-validate` exits 0 against the full tree with all 47
        architecture documents present and zero UNVERIFIED-turned-error regressions.

PARALLEL  All 5 authoring steps are mutually independent — disjoint subdirectories,
          no shared file. Within each step, the individual child issues are also
          mutually independent (one file each) — up to all 47 could be dispatched as
          separate subagents/branches at once, capacity permitting; category grouping
          above is for this plan's readability, not an execution constraint. Step 6
          needs all five merged first, since it validates the combined tree.

GATES     `just corpus-validate` after every individual document (mechanical,
          structural gate only — schema, duplicate ids, citation resolution). No
          content-quality gate exists yet: the corpus-review skill (#630, part of
          #606) isn't merged, so there is no automated check for atomicity, evidence
          quality or source accuracy — human/reviewer read-through substitutes until
          #630 lands. `review-final` applies per-PR before merge, per repo convention.
          `qa` explore mode does not apply — this is a docs-only change with no
          runtime interface to exercise. `review-a11y` does not apply — no UI surface.

BUDGET    Step 4 (flows, 14 documents) is most likely to eat the budget: it's the
          largest category and its DoD tail is the most narratively demanding —
          ordered interactions, trust-boundary crossings, and failure/rollback
          behavior all need real evidence per flow, not templated prose.

OPEN      1. Confirmed with the user already: #608 is not blocked by #605/#606
             despite depending on their in-progress templates/standards/tooling.
             AGENTS.md instructs writing against node.schema.json now and expecting
             reshaping later — accepted, and any reshaping becomes its own issue.
          2. Standards gap: only confidence.md and decision-references.md are merged
             (2 of ~24). Diagram, naming, taxonomy and evidence-precedence standards
             relevant to some DoD tail bullets (e.g. containers' "diagram-as-code",
             flows' ordered-interaction notation) don't exist yet either. Same
             accepted gap as templates — not resolved here.
          3. Category-batch sizing (5 steps covering 47 issues) is this plan's
             right-sizing call, not the issue's own structure — each child issue
             still closes with its own branch/PR per repo convention. If a category
             batch (particularly flows, 14 issues) is too large a unit to dispatch or
             review together, splitting further is the reader's call, consistent with
             this skill's "flagged, not refused" rule for oversized work.
          4. Node `id` convention (`architecture-<category>-<topic>`) is this plan's
             proposal, following the `corpus-standard-<slug>` / `corpus-readme`
             precedent — not dictated by any issue or by AGENTS.md.
          5. `relationships` entries: the DoD checklist says "typed relationships
             appropriate to the node," but almost nothing else exists in the corpus
             yet outside the 2 standards + AGENTS.md/README, and AGENTS.md's own node
             carries none, explicitly noting "the first sibling node is the moment to
             revisit it." Treat relationships as added opportunistically as siblings
             land within and across categories (e.g. a flow referencing the
             containers it crosses), not as a hard per-node requirement from day one.

LEFT OUT  #605's and #606's own remaining child issues (templates, standards,
          corpus-* skills) — out of scope for #608, tracked separately. Any other
          corpus Feature (#605, #606, #607, and siblings under #602) — different
          Features. Regenerating corpus indexes or graph/completeness reports (#633-
          #635) — generated-output tooling, not this Feature's scope. Deciding
          unresolved ADR outcomes referenced by any individual node — stays explicit
          per each DoD's own "Out of scope" line.
