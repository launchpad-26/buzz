# Issue #965 — ingestion/provenance-records.md

ALREADY TRUE: `launchpad/docs/corpus/standards/provenance.md` is merged on `origin/launchpad`
and governs a different subject — the corpus's own internal "checked against repository
revision X" recorded-revision ledger entry every node carries. It says nothing about
external cryptographic or platform attestation of an artifact's own origin.
`launchpad/docs/corpus/architecture/flows/git-push.md` is also merged and explicitly names
NIP-GS commit/tag signing (`git-sign-nostr`) as "orthogonal ... this flow neither requires
nor inspects" — confirming no merged node currently documents it. Real, citable external
provenance mechanisms exist in this repository: NIP-GS (`crates/git-sign-nostr/`,
`docs/nips/NIP-GS.md`) signs git commits/tags with Nostr secp256k1 keys, verified via
`git verify-commit`/`git verify-tag`; `.github/workflows/docker.yml` and
`.github/workflows/sprig-image.yml` run `actions/attest-build-provenance` (Sigstore-signed
in-toto attestations), verifiable with `gh attestation verify`, plus a narrower custom
"deployment eligibility" predicate attestation (`actions/attest`) binding a release image to
its qualifying CI run and source SHA. `launchpad/docs/corpus/ingestion/provenance-records.md`
does not exist yet. This confirms reading (b) from the task brief, not (a): genuinely new
ground, not a duplicate of `standards/provenance.md`.

STEP 1  Gather evidence: read `crates/git-sign-nostr/README.md` and `docs/nips/NIP-GS.md` in
full (signature format, verification procedure, and the explicit "Identity Binding" security
consideration: a verified signature proves key custody only, never a person's identity or
repo authorization). Read `.github/workflows/docker.yml` (build-provenance + deployment-
eligibility attestation steps and their `gh attestation verify` commands) and
`.github/workflows/sprig-image.yml` (same pattern for the sprig image). Re-confirm via
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` that no merged node
already covers either mechanism, and read `standards/code-references.md` and
`CONTRACT.md`'s six citation shapes so the new node cites correctly rather than inventing a
seventh shape. ← RUNS HERE (done; see this task's own investigation)

STEP 2  [needs 1] Write front matter (schema-valid: id `ingestion-provenance-records`, type
`ingestion`, status `draft`, origin `launchpad`, audiences `[agent, reviewer]`, relationships
`depends-on: corpus-agents`, `references: corpus-standard-provenance` and
`references: architecture-flows-git-push` — both merged, both real boundary-setting
pointers, neither a currency dependency) and the body using `templates/policy.md`'s six
required sections in order (DoD tail is policy-shaped: MUST/SHOULD/enforcement/exceptions).
Content: MUST/SHOULD rules for how an authoring/ingesting agent treats a NIP-GS-signed git
object or a Sigstore/GitHub build-provenance (or deployment-eligibility) attestation as
evidence for a corpus claim — requiring the actual verification command and its real output
as the citation (not the workflow file alone, which only proves the step exists), forbidding
conflation of "signature/attestation verifies" with "signer's identity" or "deployment
approval," and an Enforcement section stating plainly that `validate.py` treats these
citations identically to any other commit/tool-result/bare-path shape and never runs
verification itself.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and
re-run until exit 0.

STEP 4  [needs 3] Run the corpus unittest suite as the sole prior command to earn the
verification stamp, then commit the plan + document in a separate call. Per this task's own
instructions, stop after commit — no push, no PR.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`review-adjudicate` and the cross-model final review pass are deferred to the batch owner's
morning review — not run here; an independent `review-code` pass runs instead, per this
task's own step 7.

BUDGET: small — one document, no code changes; evidence gathering scoped to two NIP/README
files, two workflow YAML files, and the merged corpus nodes already read.

OPEN: Neither the NIP-GS verification (`git verify-commit`) nor a live
`gh attestation verify` run was actually executed in this task — no signed commit or
published container digest was available to check against. The document must therefore cite
the NIP's own documented test-vector status output and the workflow's own documented verify
commands as FACTs about what the mechanism *specifies* and *runs in CI*, and must not
overclaim that this task itself executed and confirmed a live verification.

LEFT OUT: No relationship to any sibling `ingestion/*.md` task (none merged, all authored in
parallel per this batch's own worktree isolation). No attempt to reconcile or edit
`standards/provenance.md` or `architecture/flows/git-push.md` — both stay as they are; this
node only cites and distinguishes itself from them. No coverage of NIP-46 remote signing,
key revocation, or the `buzz-relay` server-side git-object-signing verification path (none
exists — NIP-GS is explicitly client/local-only, uninvolving relays, per its own Non-Goals).
