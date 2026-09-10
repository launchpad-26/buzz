Issue #1209 — task: document operations/observability/alerts.md
Stated size: no `Size` line  →  single hand-authored document, batch task under parent Feature #618  ->  cap: 5 steps.

ALREADY TRUE  (verified against git, not notes)
  On branch `task/1209-observability-alerts`, based on `origin/launchpad` HEAD
  `473205a7457b208455f188847bfb27b01aa83cac`, working tree clean.
  `node.schema.json`, `relationships.schema.json` and `launchpad/docs/corpus/AGENTS.md`
  are merged and authoritative. `launchpad/docs/corpus/templates/reference.md` is merged
  (id `corpus-template-reference`) and is the assigned template.
  `launchpad/docs/corpus/operations/observability/alerts.md` does not exist yet
  (`launchpad/docs/corpus/operations/` does not exist at all yet).
  `layers-observability-prometheus`, `layers-observability-health-checks`,
  `layers-observability-metrics`, `layers-observability-liveness` and
  `layers-observability-readiness` are present in `<SCRATCH>/existing-node-ids.txt`
  (the authoritative `origin/launchpad` snapshot for this batch), so they are safe
  `relationships` targets. No `operations-*` id appears anywhere in that file.

STEP 1  [independent]  Gather evidence for what alerting actually exists in this
        repository. Confirm the repository ships exactly one `PrometheusRule`:
        `deploy/charts/buzz-push-gateway/templates/prometheusrule.yaml` (5 alerts:
        `PushGatewayConfigurationFault`, `PushGatewayAdmissionUnavailable`,
        `PushGatewayReadinessAuthorityFailing`, `PushGatewayReaperFailing`,
        `PushGatewayHighApnsRetryRate`), gated by `prometheusRule.enabled` (default
        `false` in `deploy/charts/buzz-push-gateway/values.yaml`, not overridden in
        `values-production.yaml`). Confirm the main relay chart
        (`deploy/charts/buzz`) has a `ServiceMonitor`
        (`templates/servicemonitor.yaml`, scraping only) but no `PrometheusRule`
        template at all. Read the matching prose table in
        `docs/push-gateway-deployment.md` and the chart's render-test assertions in
        `deploy/charts/buzz-push-gateway/tests/render.sh` (lines 67, 121, 137, 181-182).
        Read `crates/buzz-relay/src/router.rs` (`liveness_handler`, `readiness_handler`,
        401-449) and confirm the relay's readiness handler records no metric on
        failure (no `metrics::` call in that range), unlike
        `crates/buzz-push-gateway/src/metrics.rs`'s `record_readiness_failure`, which
        backs one of the five existing alerts directly. Check `launchpad/decisions/`
        for any accepted ADR governing alerting policy (none found by name) and read
        `launchpad/Research/324-alert-to-issue-prior-art.md` and
        `325-alert-duplicate-suppression.md` for the team's stated forward-looking
        intent (not yet implemented).
        done when: every claim planned for the body has a specific opened source
        (path, and path:line only where a range brackets a named alert/symbol)
        recorded.

STEP 2  [needs 1]  ← RUNS HERE  Write
        `launchpad/docs/corpus/operations/observability/alerts.md` against the
        `reference.md` template's required sections: a reference-description
        paragraph; a structured-entries table of the five push-gateway alerts
        (name, expression intent, `for`, severity, action) sourced from
        `prometheusrule.yaml` and cross-checked against
        `docs/push-gateway-deployment.md`'s table; a second table naming the
        signals that exist but have no alert rule (relay readiness/liveness
        endpoints, relay Prometheus metrics catalog, relay `ServiceMonitor`) with
        the central honest finding stated plainly: the relay itself ships zero
        alert definitions, only the push-gateway does, and even that one
        `PrometheusRule` is disabled by default and left disabled in the
        production values overlay; an optional Commands table (Helm
        `--set prometheusRule.enabled=true` / `--set podMonitor.enabled=true`,
        `kubectl get prometheusrule`); a Boundary section naming the three
        template exclusions plus the explicit sibling-node boundary (metrics
        #1212, logs #1211, traces #1213, dashboards #1210 are being written now
        and are named in prose only, no `relationships` edge, no linked path);
        `relationships: references` to `layers-observability-prometheus`,
        `layers-observability-health-checks` and `layers-observability-metrics`
        (all confirmed present in `<SCRATCH>/existing-node-ids.txt`); and a Scope
        and omissions section carrying both what the node does not cover (owner
        table) and what was expected but could not be verified (whether the one
        real alert set has ever actually fired, whether any Alertmanager/receiver
        beyond the chart's opt-in rule exists anywhere in this fork's operated
        environment).
        Front matter: `id: operations-observability-alerts`, `type: operations`,
        `status: draft`, `origin: launchpad`, `audiences: [operator, developer,
        reviewer]`.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py`
        exits 0 and every issue-1209 DoD bullet, including the four
        reference-specific tail bullets, is addressed by a distinct section.

STEP 3  [needs 2]  Self-verify the diff line-by-line against the issue's DoD
        checklist: confirm every evidence entry supports its claim (open each
        cited file again), confirm no second canonical document was created, and
        confirm the two absence-claims (relay ships no `PrometheusRule`; relay
        readiness records no failure metric) each rest on at least one openable
        citation rather than only a tool-result/negative claim, per the evidence
        standard's MUST 4/8.
        done when: the audit is written and `validate.py` exits 0 on the current
        tree.

STEP 4  [needs 3]  Earn the verification stamp with the corpus unittest suite as
        the sole command in its own tool call (no `| tail`, no chained `cd`),
        confirm `OK`, then in a separate tool call stage and commit the plan file
        and the new document together with `git commit -s`.
        done when: `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`
        and `git commit -s` succeeds without `--no-verify`.

PARALLEL  None — single new file, steps are strictly sequential (evidence gathers
          before the body cites it; the body must exist before it can be audited).

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
          before commit. `review-adjudicate` and the cross-model review pass are
          deferred to the batch owner's later review — not run in this worktree.

BUDGET    STEP 2. The hard part is stating the "no alerting exists at the relay
          layer, only a disabled-by-default one at the push-gateway layer" finding
          precisely enough to be useful to an operator, without either overstating
          it (the push-gateway rules do exist and are real, tested code) or
          softening it into vague reassurance.

OPEN      Whether any Alertmanager, Grafana alert routing, or PagerDuty/Slack
          receiver is actually configured in whatever cluster this fork's
          `buzz-relay`/`buzz-push-gateway` images are deployed to is not
          answerable from this repository — the repository only carries the
          opt-in chart template, not a receiver's live configuration. Named as a
          verify-and-could-not gap, not resolved here. Whether `#1212`'s
          eventual metrics node will list every relay series a future alert rule
          could threshold on is also left to that task.

LEFT OUT  Any `relationships` edge to a metrics/logs/traces/dashboards sibling
          node — none of `operations-observability-metrics`,
          `-logs`, `-traces`, `-dashboards` exist in
          `<SCRATCH>/existing-node-ids.txt`; naming them in prose only, per the
          brief. Writing or proposing a relay-level `PrometheusRule` — that is
          runtime/product work with its own separately-linked implementation
          issue, not a documentation task. Editing
          `docs/push-gateway-deployment.md`, `prometheusrule.yaml`, or any other
          existing file — this task is additive documentation only. A second
          canonical corpus document.
