---
id: ingestion-provenance-records
type: ingestion
status: draft
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "NIP-GS defines a signature format and verification protocol for signing git commits and tags with Nostr secp256k1 keys (BIP-340 Schnorr), using git's pluggable `gpg.x509.program` signing-program interface; the companion `git-sign-nostr` binary implements it, configured via `git config gpg.format x509` / `gpg.x509.program` / `user.signingkey`, and verified with the ordinary `git verify-commit` / `git verify-tag` commands."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-GS.md"
      - "crates/git-sign-nostr/README.md"
  - statement: "NIP-GS's own Identity Binding section states directly that a verified nostr commit signature proves only 'this secp256k1 key signed this git object,' and does NOT prove the signer is a specific person, that the signer is authorized to commit to the repository, or that the commit content is trustworthy -- each requiring separate, out-of-band verification the signature itself does not supply."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-GS.md:817-829"
  - statement: "NIP-GS's verification procedure determines a `TRUST_FULLY` vs `TRUST_UNDEFINED` trust level purely by comparing the signature's embedded public key against the locally configured `user.signingkey` git config value, and the spec states explicitly that `TRUST_FULLY` means only 'this is the locally configured signing key' -- not a global trust assertion -- recommending an allowed-signers mechanism (out of the NIP's own scope) for verifying other people's commits."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-GS.md:261-273"
  - statement: "When a NIP-GS envelope carries an optional NIP-OA owner-attestation (`oa` field) and verifies successfully, the spec's Trust Display section states a verifier MUST display 'signed by the agent key' and 'authorized by the owner key' as two distinct facts. Separately, its Verification section states that if the owner-attestation signature fails, the outer commit signature (`sig`) may still be valid, and verifiers SHOULD (not MUST) report the commit as signed but the owner authorization as failed/unverified, rather than collapsing the two into one pass/fail result."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-GS.md:420-426"
      - "docs/nips/NIP-GS.md:446-453"
  - statement: "`.github/workflows/docker.yml` grants `id-token: write` and `attestations: write` to its image-publishing jobs and runs `actions/attest-build-provenance@0f67c3f4856b2e3261c31976d6725780e5e4c373` against the merged manifest digest of every built variant (both the main image and the public push-gateway image), producing a Sigstore-signed in-toto attestation the job's own summary step documents as verifiable with `gh attestation verify oci://<image>@<digest> --owner <org>`."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml:176-177"
      - ".github/workflows/docker.yml:504-507"
      - ".github/workflows/docker.yml:571-573"
      - ".github/workflows/docker.yml:713-714"
      - ".github/workflows/docker.yml:737"
  - statement: "`.github/workflows/sprig-image.yml` runs the identical `actions/attest-build-provenance` step against the merged `buzz-sprig` image manifest digest, with the same job-level `id-token`/`attestations` write permissions and the same `gh attestation verify oci://ghcr.io/block/buzz-sprig:<tag> --owner block` verification command documented in its own comment."
    entry_class: FACT
    evidence:
      - ".github/workflows/sprig-image.yml:61-62"
      - ".github/workflows/sprig-image.yml:215-217"
  - statement: "For the release variant only (`matrix.variant == 'release'`), `docker.yml` additionally builds and attests a second, narrower predicate -- `https://buzz.block.xyz/attestations/deployment-eligibility/v1`, via `actions/attest@1e69f48acb82d1966a394da916b4c1698aa569d6` -- whose JSON payload binds the image digest to a specific qualifying CI run id/attempt and source SHA, and which the job's own summary step documents as checked with a distinct, more specific command: `gh attestation verify oci://<image>@<digest> --repo block/buzz --signer-workflow block/buzz/.github/workflows/docker.yml --predicate-type https://buzz.block.xyz/attestations/deployment-eligibility/v1 --source-digest <source_sha>`."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml:513-544"
      - ".github/workflows/docker.yml:579"
  - statement: "validate.py's `_classify_citation` routes a `commit <sha>`-shaped citation and a `symbol(args) -> result`-shaped tool-result citation through the identical outcome: both are recognised, neither is opened, and both resolve to `CitationVerdict(\"unverified\", ...)` -- printed as a non-fatal UNVERIFIED notice and never distinguished from each other or from any other citation of either shape."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py:701-743"
  - statement: "`standards/provenance.md`, an active, merged corpus standard, governs a distinct subject: the one evidence entry every corpus node carries recording the repository revision it was checked against ('This node was authored and checked against repository revision <sha>'). Its own Scope and authority section states its governance is limited to that recorded-revision entry; it does not mention git commit/tag signing, Sigstore, build attestations, or any external cryptographic or platform-issued attestation of an artifact's own origin anywhere in its text."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/provenance.md:105-129"
  - statement: "`architecture/flows/git-push.md`, a merged corpus node (status `draft`) documenting the git-push HTTP transport, explicitly excludes NIP-GS from its own scope: its evidence ledger states that signing git objects with a Nostr key 'is a related but independent concern from the push-transport authentication this node documents,' and its Scope and omissions table names 'NIP-GS commit/tag object signing (`git-sign-nostr`)' as 'orthogonal to transport auth' and owned elsewhere -- confirming no merged corpus node covers NIP-GS signing or build-provenance attestation as of this node's authoring revision."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/git-push.md:331-348"
  - statement: "CONTRACT.md's six recognised citation shapes are file range, file line, bare path, graph edge, tool result, and commit reference; a tool result is illustrated as `find_references('x', crate='buzz-core') -> no callers in this crate` -- a function-call notation naming the command and summarizing its real output -- and is explicitly one of the three shapes CONTRACT.md itself marks 'not openable,' the same non-fatal treatment `validate.py` gives a commit reference."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/CONTRACT.md"
  - statement: "Parent Feature #620 lists this task among 32 child document tasks under an `agents/` and `ingestion/` path family with the stated outcome 'Agents can deterministically navigate, evidence, draft, validate and maintain corpus nodes using documented procedures,' and its sibling ingestion tasks (#953-#972, this node's own family) name other specific evidence-source and process types -- commits, git history, issues, pull requests, evidence ranking, evidence conflicts -- none of which, on inspection of their own issue titles, name external cryptographic or platform attestation as their subject, distinguishing this node's subject from every sibling's."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body and launchpad-26/buzz#953-#972 issue titles"
  - statement: "Issue #965's own Definition of Done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and an exception/escalation process, and link decisions or higher-order policy instead of duplicating them -- the same policy-shaped boilerplate carried by every task in this batch, per `templates/policy.md`'s own documented observation that the boilerplate is shared across the corpus-plan tool's tasks generally, not evidence on its own that any particular task's real subject is policy-shaped."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#965 definition of done"
  - statement: "This node's subject -- how an authoring/ingesting agent must treat an externally cryptographically-or-platform-attested provenance record as evidence -- is genuinely policy-shaped (MUST/SHOULD rules governing a citation and evidence-class practice) rather than a duplicate of `standards/provenance.md`'s narrower, already-settled subject (the corpus's own internal recorded-revision bookkeeping entry), because the two govern disjoint evidence: one is about citing the corpus's own checked-revision claim, the other is about citing an external artifact's cryptographic or platform-issued attestation of its own origin."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/standards/provenance.md"
      - "docs/nips/NIP-GS.md"
      - ".github/workflows/docker.yml"
    confidence: 0.8
relationships:
  - type: depends-on
    target: corpus-agents
  - type: references
    target: corpus-standard-provenance
  - type: references
    target: architecture-flows-git-push
---

# Policy: treating externally-attested provenance records as evidence

How an authoring or ingesting agent treats an externally cryptographically-or-platform-
attested provenance record -- a git commit or tag signed under NIP-GS, or a container
image carrying a Sigstore/GitHub build-provenance or deployment-eligibility attestation
-- as evidence for a corpus claim: what evidence class such a claim may honestly carry,
what citation shape it must use, and which conflations it must not make.

## Scope and authority

**This node governs** a corpus claim that cites, as its evidence, an artifact's own
cryptographic or platform-issued attestation of its origin -- specifically the two such
mechanisms that exist in this repository today: NIP-GS git-object signing
(`crates/git-sign-nostr/`, `docs/nips/NIP-GS.md`) and GitHub Actions build-provenance /
deployment-eligibility attestation (`.github/workflows/docker.yml`,
`.github/workflows/sprig-image.yml`, via `actions/attest-build-provenance` and
`actions/attest`). It does not govern the corpus's own internal recorded-revision
citation -- a different subject entirely, owned by `standards/provenance.md` (see
*Boundary* below) -- nor the mechanisms themselves, which are specified in full by the
NIP and the workflow files this node cites and does not restate.

**Its authority is derived, not original.** The structural half is already law:
`node.schema.json` defines the `evidence` array as the only place a claim's citation
lives, and `validate.py`'s `_classify_citation` already recognises the shapes this
node's claims must use (see *Enforcement*). NIP-GS and the two attestation workflows are
themselves authoritative over what each mechanism actually establishes; this node adds
only the half no schema or spec states -- how an agent citing one of them honestly,
without overclaiming what was checked.

**Where this document and `node.schema.json`, `validate.py`, `docs/nips/NIP-GS.md`, or
the cited workflow files disagree, they win** -- this document has drifted and should be
fixed.

| For | Read |
|---|---|
| The corpus's own internal recorded-revision citation convention (a different subject) | `launchpad/docs/corpus/standards/provenance.md` |
| The NIP-GS signature format, signing/verification procedure, and security considerations | `docs/nips/NIP-GS.md` |
| The `git-sign-nostr` program's configuration and usage | `crates/git-sign-nostr/README.md` |
| The six citation shapes generally and how a claim is classified | `launchpad/project-intelligence/CONTRACT.md`, `launchpad/docs/corpus/standards/code-references.md` |
| How conflicting evidence is ranked and escalated | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |
| The `confidence` field on an INFERENCE | `launchpad/docs/corpus/standards/confidence.md` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| The git-push HTTP transport this node's subject is orthogonal to | `launchpad/docs/corpus/architecture/flows/git-push.md` |

### Boundary: this node versus `standards/provenance.md`

**Read this before citing either document.** Both names could plausibly mean
"provenance," and only one of them governs the recorded-revision entry every corpus node
already carries. `standards/provenance.md`'s own Scope and authority section states its
governance is limited to "the evidence entry that records the repository revision a
corpus node was authored and checked against" -- a bookkeeping claim about *this corpus's
own* evidence ledger, never about an external artifact. Its entire text, read in full
while authoring this node, contains no mention of git signing, Sigstore, build
attestations, or any cryptographic or platform-issued attestation of an artifact's own
origin. This node's subject -- what an authoring agent may honestly claim about a
signed commit or an attested container image -- is disjoint from that: the two nodes
govern different citations that happen to share the English word "provenance." Neither
restates the other; each links to the other via the *references* relationship declared
in front matter, per P9's link-not-duplicate rule.

## MUST

| # | Requirement |
|---|---|
| **N1** | A claim citing NIP-GS signing or a Sigstore/GitHub build-provenance or deployment-eligibility attestation as its evidence MUST cite the actual verification act and its real observed output (a tool-result-shaped citation naming the command run and what it printed), not merely the workflow file, README, or spec that defines the mechanism. A citation of the defining file alone establishes only that the mechanism exists and runs in CI for every artifact of that kind -- it establishes nothing about whether any specific commit, tag, or image was actually checked and found valid. Enforced by review only; nothing mechanical can tell the two apart (see *Enforcement*). |
| **N2** | A `FACT`-class entry asserting "this commit/tag/image is signature- or attestation-verified" MUST NOT be written unless the author actually ran `git verify-commit` / `git verify-tag` or `gh attestation verify` and observed its output. Describing what the command would probably show, without running it, MUST be written as `INFERENCE` (with `confidence`) or left unestablished -- never as `FACT`. Enforced by review only. |
| **N3** | A claim MUST NOT conflate "a NIP-GS signature verifies" with "the signer is a specific, real-world identity" or "the signer was authorized to make this change." Per NIP-GS's own Identity Binding section, a verified signature establishes only that one secp256k1 key signed the object -- nothing about the person behind the key (absent independent identity verification, e.g. NIP-05) or repository authorization (a separate access-control concern documented in `architecture/flows/git-push.md`). |
| **N4** | Where a NIP-GS envelope carries an `oa` (NIP-OA owner-attestation) field, an owner-authorization claim MUST cite that the `oa` verification specifically succeeded. A valid outer signature (`sig`) with a failed or absent `oa` check is signed but not owner-authorized; NIP-GS's Trust Display section requires these be shown as distinct facts when `oa` succeeds, and separately recommends (SHOULD) the same distinction on failure -- either way, a corpus claim MUST NOT collapse them into one pass/fail result. This node holds authors to that distinction as a MUST regardless of which NIP-GS sub-case applies, since a corpus claim conflating them is dishonest evidence either way. |
| **N5** | A claim MUST NOT conflate the generic build-provenance attestation (`actions/attest-build-provenance`, run for every built variant of every image) with the narrower deployment-eligibility attestation (`actions/attest`, predicate `https://buzz.block.xyz/attestations/deployment-eligibility/v1`, run only for `matrix.variant == 'release'`). The first establishes only which repository and workflow produced the image; the second additionally binds it to a specific qualifying CI run and source SHA. A claim about deployment approval or eligibility MUST cite the deployment-eligibility attestation and its `--predicate-type`/`--source-digest`-scoped verify command, not the generic one. |
| **N6** | A citation under this node's subject MUST use one of CONTRACT.md's six recognised shapes -- ordinarily a tool-result citation for a run verification command, or a bare/positioned path citation for the defining workflow or spec file -- never an invented seventh shape. `node.schema.json`'s `evidence` field accepts any non-empty string, but `validate.py`'s `_classify_citation` recognises only six forms; an unrecognised shape is a hard error, not a softer unverified one. |
| **N7** | Every `entry_class` rule in `node.schema.json` (`FACT` requires `evidence` and forbids `confidence`/`provided_by`; `INFERENCE` requires `evidence` and `confidence`; `TEAM_KNOWLEDGE` requires `provided_by` and forbids `confidence`) applies to a provenance-attestation claim exactly as to any other evidence entry. This node adds no new field, class, or exemption for these two evidence types. |

## SHOULD

| # | Guidance |
|---|---|
| **N8** | Prefer citing a signature- or attestation-verified artifact over a plain `commit <sha>` reference when both are available for the same claim. The former is independently re-checkable by any reader running the same command; the latter is, per `standards/provenance.md` and `validate.py`, `UNVERIFIED`-shaped and never automatically re-checked by anyone. |
| **N9** | When citing `git verify-commit` / `git verify-tag` output, quote the actual `GOODSIG`/`VALIDSIG`/`TRUST_*` status lines observed. When illustrating the mechanism rather than reporting a live check, say so explicitly and cite NIP-GS's own documented test-vector status output (`docs/nips/NIP-GS.md`'s Test Vectors section) rather than inventing an example that looks like a real run. |
| **N10** | An author who cannot run the required verification (no signed commit available to test against, no network access to the OCI registry, no `gh` auth configured) SHOULD say so plainly in the node's *Scope and omissions*, rather than silently omitting the claim or writing a downgraded confidence without explanation -- the same disclosure `AGENTS.md` already asks for any expected-but-unverified claim. |

## Enforcement

**Nothing here is checked mechanically.** `validate.py`'s `_classify_citation`
(`launchpad/project-intelligence/corpus/validate.py:701-743`) routes a `commit
<sha>`-shaped citation and a `symbol(args) -> result`-shaped tool-result citation to the
identical outcome: both are recognised by shape, neither is opened, and both resolve to
`CitationVerdict("unverified", ...)` -- printed as a non-fatal notice and never fatal to
the run. This means a `FACT` entry backed by a tool-result citation that genuinely
reports `git verify-commit`'s real output validates exactly the same as one backed by a
plausible-looking tool-result string nobody ran. **A green `validate.py` run establishes
only that the citation is shaped like one of the six recognised forms -- never that the
verification behind it was actually performed, and never that N1-N5 above were honored.**

**The workflows themselves genuinely run the attestation steps** (`docker.yml`,
`sprig-image.yml`): `actions/attest-build-provenance` and `actions/attest` really do
produce Sigstore-signed in-toto attestations, pushed to the registry alongside each
image, for every CI run that reaches those steps. That is real and independently
verifiable by anyone with `gh` and network access. **It is orthogonal to whether a
corpus node's citation of the resulting artifact is honest** -- CI having produced a
real attestation says nothing about whether a later corpus claim describing it was ever
actually checked by the person who wrote the claim.

**Enforced by review only:** N1-N5 (whether the cited verification was actually run,
whether identity/authorization/deployment-eligibility claims stay properly separated).
**Enforced mechanically:** N6 (citation shape) and N7 (entry-class field rules), by the
same schema and validator every other corpus claim goes through.

## Exceptions and escalation

**There is no exemption from N1-N5.** They follow directly from what NIP-GS's own spec
and the workflows' own attestation steps actually establish -- not from a norm this
document invented. When a required verification genuinely cannot be run (see N10), the
claim stays unestablished or is written as `INFERENCE`/`TEAM_KNOWLEDGE` rather than met
by a fabricated `FACT`.

**A disputed application is a reviewer's judgment, not an exception.** Whether a given
claim needed the deployment-eligibility attestation specifically (N5) versus the generic
build-provenance one, or whether a stated verification output looks genuinely run versus
merely plausible (N1/N2), is recorded in the pull request and decided by the reviewer.
A repeated disagreement is filed as an issue against this node, because a rule two
people read differently is a defect in the rule.

**A provenance mechanism this node does not cover** -- NIP-46 remote signing, a future
SBOM format, a different platform's attestation scheme -- is escalated as a new task
against parent Feature #620, describing the mechanism and why N1-N7 as written do not
reach it. Do not widen this node's scope locally to fit; a policy an author quietly
reinterprets per-case has stopped being one.

## Scope and omissions

**This node covers** how an authoring/ingesting agent treats an externally attested
provenance record -- a NIP-GS-signed git commit/tag, or a Sigstore/GitHub build-
provenance or deployment-eligibility attestation on a container image -- as evidence for
a corpus claim: what class such a claim may honestly carry, what citation shape it must
use, and the conflations (identity, owner-authorization, deployment-eligibility) it must
not make.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The corpus's own internal recorded-revision ledger citation ("checked against repository revision X") | `launchpad/docs/corpus/standards/provenance.md` |
| The git-push HTTP transport authentication (NIP-98) that authenticates the *pusher*, as distinct from NIP-GS which authenticates the *committer* | `launchpad/docs/corpus/architecture/flows/git-push.md` |
| The NIP-GS signature format, signing/verification procedure, and security considerations themselves | `docs/nips/NIP-GS.md` |
| The citation-shape rules generally, for all six forms and not only these two | `launchpad/docs/corpus/standards/code-references.md`, `launchpad/project-intelligence/CONTRACT.md` |
| Which claim types are ranked over which when authoritative sources conflict | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md`, `launchpad/docs/corpus/standards/confidence.md` |
| Ingesting plain, unattested commit and git-history evidence | `ingestion/commits.md`, `ingestion/git-history.md` (sibling tasks, unmerged at this node's authoring time) |
| NIP-46 remote signing, key revocation/rotation, and any future SBOM or additional attestation predicate type | Not raised as a task anywhere found; escalate per *Exceptions and escalation* above |

**This node's own relationships.** Declared: `depends-on: corpus-agents` -- real and
resolvable on `origin/launchpad`, and a genuine dependency: this node's evidence and
citation-shape rules are derived from `AGENTS.md`, not original. Declared:
`references: corpus-standard-provenance` and `references: architecture-flows-git-push`
-- both real, resolvable, merged nodes this document explicitly distinguishes itself
from in *Boundary* and the omissions table above, cited as supporting context rather
than a currency dependency, per `relationships.schema.json`'s own directionality for
`references`. No edge to any sibling `ingestion/*.md` task: none of #953-#972 are merged
at this node's authoring time, and a `relationships[].target` naming an id no loaded
node carries is a hard validation error.

**Expected but not verified when this node was written:**

- **Neither `git verify-commit` against a real NIP-GS-signed commit nor a live `gh
  attestation verify` against a published image digest was actually executed while
  authoring this node.** Every claim above about verification output is sourced from
  NIP-GS's own documented test vectors and the workflow files' own echoed commands, not
  from a run this task performed. Whether the real CLI output matches these documented
  shapes exactly, on a live `git`/`gh` install, is untested here.
- **Whether any container image currently published under `ghcr.io/launchpad-26/buzz`,
  `ghcr.io/block/buzz-sprig`, or `ghcr.io/block/buzz-push-gateway` actually carries a
  verifiable attestation right now** was not checked against the live registry -- only
  that the workflow steps that would produce one are present in the workflow files at
  this revision.
- **Whether any commit in this repository's history is actually NIP-GS-signed today**
  was not checked; this task did not search commit history for `gpgsig` headers in the
  NIP-GS armor form (`-----BEGIN SIGNED MESSAGE-----`).
- **No CI run has exercised this node.** All validator evidence above is local to this
  worktree.
