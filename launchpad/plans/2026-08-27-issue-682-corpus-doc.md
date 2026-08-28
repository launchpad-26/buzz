Issue #682 — task: document architecture/flows/media-download.md
Stated size: no `Size` line  →  single hand-authored document, batch task under parent PRD #608.

ALREADY TRUE  (verified against git, not notes)
  On branch `task/682-corpus-doc`, based on `origin/launchpad` HEAD a44cf52fc740ebebbdd671427480d14f0bce0115,
    working tree clean. `node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are merged and authoritative.
    `launchpad/docs/corpus/architecture/flows/media-download.md` does not exist yet.

STEP 1  [independent]  Gather evidence for the media-download flow: read the Blossom GET/HEAD
        handlers in `crates/buzz-relay/src/api/media.rs` (`get_blob`, `head_blob`,
        `serve_blob_for_tenant`, `authenticate_media_read`, `bind_media_read_tenant`,
        `validate_media_path`, `resolve_s3_key`, `parse_byte_range`), the Blossom auth
        verification in `crates/buzz-media/src/auth.rs` (`verify_blossom_get_auth`,
        `verify_blossom_auth_event_for_verb`), the error-to-status mapping in
        `crates/buzz-media/src/error.rs`, the route wiring in `crates/buzz-relay/src/router.rs`,
        the relay-membership trust boundary in `crates/buzz-relay/src/api/mod.rs`
        (`enforce_relay_membership`), and the e2e coverage in
        `crates/buzz-test-client/tests/e2e_media.rs` and `e2e_media_video.rs`.
        done when: every claim planned for the body has a specific opened source (path +
        symbol) recorded.

STEP 2  [needs 1]  ← RUNS HERE  Write `launchpad/docs/corpus/architecture/flows/media-download.md`
        with schema-valid front matter (`id: architecture-flows-media-download`,
        `type: architecture` — the schema enum has no finer flow/container/deployment split,
        `status: draft`, `origin: launchpad`, `audiences: [agent, developer]`, an `evidence`
        ledger with a commit-provenance FACT plus one entry per substantive claim, no
        `relationships`) and a body covering: trigger/preconditions/termination per the
        category tail, the ordered request/response interactions and data movement (client
        constructs URL → Blossom auth header → relay tenant bind → auth verify → relay
        membership check → sidecar MIME/extension gate → S3 key resolution → range parsing →
        streamed or 206 response), the auth/trust-boundary crossings (Blossom NIP-24242
        signature+expiry, host-bound tenant, relay-membership gate, sidecar-authoritative
        content-type, CSP/nosniff/attachment-disposition), and failure/abort behavior (401
        auth failures collapsed to prevent oracle enumeration, 403 membership/forbidden,
        404 unknown blob/path, 416 unsatisfiable range, 500 storage/internal) with links to
        the representative e2e tests that verify each.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 and
        every issue-682 DoD bullet plus the four category-tail bullets is addressed by a
        distinct section.

STEP 3  [needs 2]  Self-verify the diff line-by-line against the issue's DoD checklist and
        the category tail; confirm every evidence entry supports its claim, no second
        canonical document was created, and validate.py still passes.
        done when: the audit is written and validate.py exits 0 on the current tree.

STEP 4  [needs 3]  Earn the verification stamp with the corpus unittest suite as the sole
        command in its own tool call, then commit the plan and the new document together.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        reports OK and `git commit -s` succeeds without `--no-verify`.

PARALLEL  None — single new file, steps are strictly sequential (evidence gathers before
          the body cites it; the body must exist before it can be audited).

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before
          commit. `review-adjudicate` and the cross-model pass are deferred to the batch
          owner's morning review — not run in this worktree.

BUDGET    STEP 2. The hard part is describing the auth/trust-boundary sequence accurately
          (tenant bind → Blossom signature/expiry/verb/server-tag check → relay-membership
          gate → sidecar-authoritative content-type) without collapsing steps that matter
          for a security-relevant flow document.

OPEN      The issue's own DoD does not say whether desktop/mobile client-side request
          construction (e.g. the Tauri media proxy in `desktop/src/shared/lib/mediaUrl.ts`)
          belongs inside this flow node or is a separate client-integration concern. This
          document treats the relay's Blossom GET/HEAD contract as the canonical flow (it
          is protocol-level and client-agnostic) and mentions the desktop proxy only as an
          example trigger, not as normative behavior of this node — left genuinely open
          rather than resolved silently.

LEFT OUT  Any `relationships` edge. The only nodes merged on `origin/launchpad` today are
          `corpus-agents`, `corpus-readme`, `corpus-standard-confidence` and
          `corpus-standard-decision-references` — all `type: governance` nodes documenting
          corpus authoring practice itself, not the media/architecture domain. No sibling
          architecture or flow node exists yet to point at with `depends-on`, `part-of`,
          `implements` or `references`. Declaring none is deliberate, not an oversight.
          Editing `launchpad/docs/corpus/AGENTS.md` or any other existing node.
          A second canonical document (e.g. a separate upload-flow node) — media upload is
          a distinct flow and, if it needs a node, is its own task.
