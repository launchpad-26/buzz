Issue #1178 — task: document layers/security/ssrf-protection.md

ALREADY TRUE  node.schema.json and launchpad/docs/corpus/AGENTS.md are merged on
  origin/launchpad (checked out at 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5); no
  layers/-typed node exists anywhere in the corpus yet (0 files under
  launchpad/docs/corpus/layers/); the invariant template
  (launchpad/docs/corpus/templates/invariant.md) matches this issue's DoD shape
  (invariant statement / scope / enforcement / consequence / verification) even
  though no per-`layers`-type template is assigned; and
  launchpad/docs/corpus/layers/security/ssrf-protection.md does not exist in this
  worktree. A sibling flow node, architecture-flows-workflow-execution.md, already
  cites the same SSRF guard as supporting evidence for a different claim (SEC-006
  authority gating) — it does not claim to be the canonical SSRF node, so this task
  does not duplicate it, and this task's node may `references` it as a merged,
  topically adjacent target.

STEP 1  Gather evidence for the invariant: read crates/buzz-workflow/src/executor.rs
        (ActionDef::CallWebhook's dispatch arm, `check_ssrf`, `call_webhook_impl`,
        `WEBHOOK_MAX_RESPONSE_BYTES`), crates/buzz-core/src/network.rs
        (`is_private_ip` and its exhaustive range table/tests), crates/buzz-workflow/
        Cargo.toml + crates/buzz-relay/Cargo.toml (confirms the relay build enables
        the `reqwest` feature, so the guard is live in production, not a stub),
        crates/buzz-workflow/src/schema.rs (`ActionDef::CallWebhook`'s doc comment,
        `requires_elevated_authority`), crates/buzz-relay/src/handlers/
        command_executor.rs (the SEC-006 owner/admin gate at workflow-save time —
        an authorization control, not itself an SSRF guard, so it belongs in scope
        as context and boundary, not as an enforcement point), and confirm via grep
        that buzz-media has no fetch-by-URL path and buzz-push-gateway's outbound
        calls target operator-configured APNs/FCM endpoints, not per-request
        user-controlled URLs — so `call_webhook` is the only outbound-request
        surface driven by user input.
        done when: every claim in the finished document has a citation to a file
        actually opened above.

STEP 2  Run `cargo test -p buzz-core --lib network::` (hermit-activated) and record
        the pass count as the FACT backing `is_private_ip`'s classification
        correctness; confirm no unit or integration test exists for `check_ssrf` or
        `call_webhook_impl` themselves (grep confirms this), so the document must
        state that gap honestly rather than imply end-to-end coverage.
        done when: the test command's actual output is captured for citation.

STEP 3  Write the front matter (id: layers-security-ssrf-protection, type: layers,
        status: draft, origin: launchpad, audiences: [agent, developer, operator,
        reviewer], one `references` relationship to architecture-flows-workflow-
        execution — merged and topically adjacent) and the body: one unambiguous
        MUST/MUST NOT statement of the invariant, scope (which action and which
        surface this governs, and what it explicitly does not — media, push
        delivery, the SEC-006 authority gate), enforcement points (DNS-resolve-then-
        reject-private, DNS-pinned per-call client, proxy disabled, redirects
        disabled, capped incremental body read) each cited to the exact function,
        consequence of violation (SSRF-driven internal network/metadata-service
        access via an operator-supplied webhook URL), and a scope-and-omissions
        section naming the unit-tested `is_private_ip` classifier as the verified
        mechanism while recording plainly that `check_ssrf`/`call_webhook_impl`
        themselves have no automated test exercising the end-to-end guard.
        done when: the file exists and is schema-shaped.                [RUNS HERE]

STEP 4  Validate: `python3 launchpad/project-intelligence/corpus/validate.py` must
        exit 0 against the full corpus tree including the new file.
        done when: exit 0.

STEP 5  Earn the commit-verification stamp with
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        (run alone, in its own tool call), then commit the plan and the document
        together and open a draft PR against launchpad.
        done when: unittest reports OK, commit succeeds, PR is opened as draft.

PARALLEL  None — one document, one plan file, strictly sequential.

GATES     python3 launchpad/project-intelligence/corpus/validate.py (must exit 0).
          review-adjudicate and the cross-model final pass are explicitly deferred to
          the batch owner's review — not run here (self-review only).

BUDGET    STEP 1 is the step most likely to take the most time: distinguishing the
          one real outbound-request-on-user-input surface (`call_webhook`) from
          adjacent but out-of-scope outbound paths (media, push delivery) requires
          reading enough of each to rule it out, not just grepping for `reqwest`.

OPEN      No automated test exercises `check_ssrf`/`call_webhook_impl` end to end
          (DNS resolution, pinning, redirect/proxy denial, body cap) against a real
          or mocked private-IP target — only the pure `is_private_ip` classifier is
          unit-tested. The document records this as an explicit verification gap
          rather than rounding the classifier's own test coverage up to cover the
          integration it feeds.

LEFT OUT  Standing up a live target host to exercise `call_webhook_impl` end to end.
          Any second hand-authored corpus document, including edits to
          architecture-flows-workflow-execution.md. Editing AGENTS.md or the schema.
          Documenting the SEC-006 authority gate itself (owned by the
          architecture-flows-workflow-execution node already merged).
