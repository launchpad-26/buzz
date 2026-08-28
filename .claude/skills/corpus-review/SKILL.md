---
name: corpus-review
description: Review one drafted corpus node before it merges — structural validation, evidence honesty, duplication/atomicity, and public-boundary safety, each reported separately. Use after corpus-author drafts a node. Not for authoring content and not for reviewing a whole branch or PR body.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# corpus-review — one node, four separate questions

Reviews exactly one drafted corpus node — the output of `corpus-author`
(issue #629) — before it merges. Four questions, kept structurally separate
because they fail in different ways and a reader needs to know which one
broke: **is it structurally valid, is its evidence honest, does it duplicate
or fragment another node, and is it safe for a public repository.** Read
`launchpad/docs/corpus/AGENTS.md` before your first use — this skill checks
compliance with it, it does not restate it.

## Run the deterministic validator first

```bash
python3 launchpad/project-intelligence/corpus/validate.py
```

**This is not one of your four findings categories — it is the gate in
front of them.** A non-zero exit is a hard Blocker, full stop, regardless of
how good the prose reads: the node is not schema-valid, or a citation form
is unrecognised, or a relationship target doesn't resolve, or something else
`validate.py` checks structurally. Report its exact output. Everything below
is **advisory** — your judgment, for a human to weigh — precisely because it
is NOT what `validate.py` checks. Do not blur the two: a Blocker you found
by reading is a recommendation; a Blocker `validate.py` found is a fact.

## The four reports

Keep these visibly separate in your output — a reader scanning for "is the
schema OK" should not have to parse prose to find out whether that question
is even a Blocker.

### 1. Structural validation

`validate.py`'s own result, quoted, not paraphrased. If it passed cleanly,
say so in one line — a passing check is not a finding, and inventing
severity for good news is exactly what `review-final`'s own convention
warns against.

### 2. Factual and evidence findings

For **every** `evidence` entry in the node's front matter:

- **Open the cited source yourself.** Do not accept the author's `FACT`
  label on their word — `AGENTS.md` is explicit that a citation resolving
  structurally (which `validate.py` already checked) does not mean it
  supports the claim; only a human who opened it establishes that, and here
  you are that human, a second time.
- **Check the class against what `evidence.py` would say.** If the entry's
  only real backing is discussion (an issue comment, a PR review, a PR
  comment — the same three classes `evidence.py` marks
  `fact_eligible=False`) but the node calls it `FACT`, that is a finding,
  not a nitpick — it is exactly the failure issue #629's corpus-author skill
  exists to prevent, and your job here is to catch it if that prevention
  failed.
- **`INFERENCE` needs to actually be reasoning, not a fact dressed up with a
  `confidence` number.** Read whether the stated confidence is earned by
  the cited evidence or just asserted.
- **`TEAM_KNOWLEDGE` needs a real `provided_by`**, not the author's own
  judgment relabelled to dodge having to justify it as `INFERENCE`.
- **Missing or unverifiable evidence is a finding, never a silent pass.**
  A citation you cannot open (broken path, ambiguous target, an
  `UNVERIFIED`-only chain per `AGENTS.md`'s "three things a passing run
  does not mean") does not default to OK because `validate.py` didn't
  reject it structurally — `validate.py` checks the citation *resolves*,
  never that it *supports the claim*. That gap is yours to check, every
  time, not just when something looks suspicious.
- **Check claims against current source, not just against the citation's
  existence.** Where the node cites a test or spec as evidence, open that
  test/spec and confirm it still says what the node claims — a citation
  that resolved when written can have drifted since. Prefer a
  representative sample of the node's substantive claims over skimming all
  of them equally; spend real time on the ones the node leans on most.

### 3. Duplication and atomicity findings

- **Atomicity**: does this node describe exactly one independently
  maintainable idea, per `AGENTS.md`'s "one node is one independently
  maintainable idea"? A node that is really two contracts stitched together
  is a finding here, with a recommendation to split — not something to wave
  through because both halves are individually well-cited.
- **Duplication across neighbors**: search the corpus
  (`launchpad/docs/corpus/**/*.md`) for the same canonical claim restated in
  a different node. When you find one, **route it to one owner** — recommend
  which node should carry the claim and which should link to it instead of
  restating it (a `references` relationship, per `AGENTS.md`'s "link, don't
  restate" discipline that #1308's own node was found violating in an
  earlier batch). Name both nodes; a duplication finding with only one
  citation is not yet a duplication finding.

### 4. Security and public-boundary findings

This corpus is public and may ship in desktop builds (PRD #602's own
security implications). Check the node for:

- Private-source content, secrets, or internal-only decisions synthesized
  into public prose.
- A citation naming a credential-shaped path — the same short, exact list
  `validate.py`/`evidence.py` already use (`.env`, `.env.local`,
  `id_rsa*`/`id_ed25519*`, `*.pem`/`*.key`), never a broad substring guess
  like `*auth*` or `*secret*` that would false-positive on a real crate name
  like `buzz-auth`.
- Provenance that would let source-controlled prose forge a `FACT`/
  `INFERENCE`/`TEAM_KNOWLEDGE` label the evidence doesn't actually support —
  i.e., an unusually convenient-looking citation worth a second look, not
  just a first one.

## Output is advisory unless the validator says otherwise

State this explicitly in your report: findings 2-4 are your judgment, for a
human to weigh, not a verdict. Only `validate.py`'s own exit code is a hard
contract failure. Do not phrase an advisory finding as if it blocks the
merge on its own authority — say what you found and why it matters, and let
the human decide, same discipline `review-final` holds for its own findings.

## Final checklist — replay this, don't just read it

An independent reviewer should be able to run this list against the same
node and reach the same four reports:

- [ ] Ran `validate.py`, quoted its exact exit status and output
- [ ] Opened every cited source in the `evidence` array, not just the ones
      that looked doubtful
- [ ] Checked every `FACT`/`INFERENCE`/`TEAM_KNOWLEDGE` label against what
      its citations actually are, using `evidence.py`'s class list as the
      standard for which classes can never be `FACT`
- [ ] Searched the corpus for neighboring nodes making the same claim
- [ ] Checked the node describes one idea, not two
- [ ] Checked for credential-shaped citations and private-source content
- [ ] Stated plainly which findings are advisory (all of 2-4) versus which
      are hard (only `validate.py`'s own result)

## Never

- Never let a structurally-passing `validate.py` run stand in for having
  checked evidence honesty — they check different things.
- Never accept a `FACT` label without opening its citation yourself.
- Never report a duplication finding with only one node named.
- Never treat an advisory finding as if it blocks the merge on its own.
- Never use a broad substring credential check — exact names only, per
  `validate.py`'s own documented reasoning for why.

## Where this came from

Written for issue #630, as the counterpart to `corpus-author` (#629):
`corpus-author` gathers evidence and drafts under real constraints;
`corpus-review` is the second, independent check that those constraints
were actually honored, structured the same way `review-final` separates
"what the ledger proves" from "what only cross-cutting reading can catch."
