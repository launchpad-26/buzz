# Prior art for an alert-opens-an-issue pipeline

**Title:** How "an alert fires and an issue is opened with the telemetry attached" is normally built
**Summary:** A solved problem with maintained off-the-shelf receivers — the cohort should adopt, not build. The pipeline is always webhook → receiver → issue, and the telemetry is attached as links and evaluated values rather than embedded data. The decisive variable is the credential: a `repo`-scoped PAT grants full write over repository code, a GitHub App or a workflow `GITHUB_TOKEN` can be narrowed to issues. A third approach — webhook into a GitHub Actions workflow — is the only one that also serves criterion 4, because the workflow can run the investigating agent.
**Tags:** `observability` `alerting` `github` `automation` `prior-art` `credentials`
**Reviewed:** 2026-08-22 · **Answers:** [#324](https://github.com/launchpad-26/buzz/issues/324)

---

## Finding

**At least two off-the-shelf receivers exist; only one is maintained.** The pipeline is always three parts: the monitoring system fires a **webhook**, a **receiver** turns the payload into an issue, and the **telemetry is attached as links plus evaluated values rather than embedded data**.

The one genuinely important variable is the **credential**. A `repo`-scoped personal access token grants full read/write over the repository's code; a GitHub App installation or a workflow's `GITHUB_TOKEN` can be narrowed to issues on one repository. On a public repository holding the cohort's own work, that is the security decision in this question.

A third approach fits #289 better than either tool: **the webhook triggers a GitHub Actions workflow**, which creates the issue *and can run the investigating agent* — criterion 4, not just criterion 5.

---
## The three implementations

### 1. `pfnet-research/alertmanager-to-github` — the strongest of the two dedicated receivers

| Aspect | What it does |
|---|---|
| **Carrier** | Alertmanager (or any Alertmanager-compatible) webhook |
| **Creator** | Standalone Go service |
| **Auth** | **PAT** (`ATG_GITHUB_TOKEN`) **or GitHub App** (`ATG_GITHUB_APP_ID`, `ATG_GITHUB_APP_INSTALLATION_ID`, `ATG_GITHUB_APP_PRIVATE_KEY`) |
| **Alert → issue mapping** | A configurable alert identifier, `"{{.Payload.GroupKey}}"` by default, overridable with `--alert-id-template`. Issues are tracked by that key to decide create-vs-update |
| **On resolve** | `--auto-close-resolved-issues`, **enabled by default**; individual alerts opt out with an `atg_skip_auto_close: true` annotation |
| **Templating** | Go templates for title, body **and labels**, with `.Payload`, `.PreviousIssue` (used with `--reopen-window`), and helpers `urlQueryEscape`, `json`, `timeNow` |
| **Maintenance** | 69 stars, 9 forks; releases automated via tagpr. No last-release date visible |

The `.PreviousIssue` variable plus `--reopen-window` is the detail that matters: it is a designed answer to "this fired again shortly after we closed it", which is exactly the flapping problem [#325](https://github.com/launchpad-26/buzz/issues/325) asks about.

### 2. `m-lab/alertmanager-github-receiver` — same category, simpler, weaker

| Aspect | What it does |
|---|---|
| **Auth** | **PAT with `repo` scope only** — no GitHub App option |
| **Alert → issue mapping** | Title generated from alert labels, default `{{ .Data.GroupLabels.alertname }}` |
| **On resolve** | `-enable-auto-close`; finds the issue by filtering open issues on `-alertlabel` and **matching titles** |
| **Extras** | Optional per-alert repository routing via a `repo` label |
| **Maintenance** | 116 commits on main, 50 stars, 23 forks. No explicit maintenance statement |

Two honest weaknesses. **Matching by title is fragile** — retitle an issue and auto-close loses it. And **the documentation does not state whether it reuses an existing issue for a repeating alert**; I could not establish the dedup behaviour from the docs, which is itself a finding rather than an omission on my part.

### 3. Webhook → GitHub Actions → issue (no bespoke service)

The alert's webhook triggers a workflow (via `repository_dispatch` or `workflow_dispatch`), and the workflow creates the issue.

| Aspect | What it does |
|---|---|
| **Carrier** | Grafana's own webhook contact point |
| **Creator** | A `launchpad-*.yml` workflow, using `GITHUB_TOKEN` |
| **Auth** | The workflow's built-in `GITHUB_TOKEN`, scopable per-workflow with `permissions: issues: write` — **no long-lived credential stored anywhere** |
| **Dedup / close** | Whatever the workflow implements — nothing free |
| **Distinctive** | The workflow can run the investigating agent, not just file a ticket |

This is the one that fits #289 rather than merely satisfying it. Criterion 5 says the recipient is the pipeline; criterion 4 wants an agent to do the diagnosis and produce the bug report. A dedicated receiver files a ticket and stops. A workflow can file the ticket *and* start the investigation in the same trigger.

It also fits this fork's conventions exactly: `launchpad/AGENTS.md` §3 reserves the `launchpad-*.yml` namespace, so it adds **no upstream divergence**, and the cohort already has precedent for machine-authored issues in `.github/workflows/launchpad-security-audit.yml` and `launchpad/review-agent/`.

---

## What carries the telemetry, in all three cases

Grafana's webhook contact point payload is the source, and it answers the PRD's "with the telemetry attached" concretely — **as links and evaluated values, not embedded data**:

| Field | What it gives the issue |
|---|---|
| `values` | *"Values that triggered the current status"* — the actual numbers |
| `generatorURL` | Direct link to the alert rule in Grafana |
| `dashboardURL`, `panelURL` | The dashboard and panel, when the UID/Panel ID annotations are set |
| `imageURL` | A **screenshot** of the triggering panel |
| `silenceURL` | One-click silence |
| `labels`, `annotations` | The alert's dimensions and text |
| `fingerprint` | *"Unique identifier for alerts with identical labels"* — the natural dedup key |
| `status`, `startsAt`, `endsAt` | Firing/resolved and the window |

Grafana also supports **custom payload templates**, so the JSON posted to the receiver can be shaped freely, and the webhook itself supports **basic auth or a bearer token** (one at a time).

Note what is *not* in the list: the underlying data. An issue gets a link to the query and the values that tripped the threshold — not the logs or spans themselves. If #289 wants the telemetry *in* the issue rather than linked from it, something has to run a query and paste the result, which is approach 3 or an agent, not a receiver.

---

## Known failure modes, from the sources

1. **The PAT scope is the blast radius.** `m-lab`'s receiver needs a token with `repo` scope — full read **and write** to repository content, not just issues. A GitHub App installation, which `alertmanager-to-github` supports, can be narrowed to issues on one repository. On a public repo where the cohort's actual work lives, that difference is the security decision in this question.
2. **Title-matching for auto-close is brittle** (`m-lab`). Any retitle breaks the link between alert and issue.
3. **Unspecified dedup is a real risk, not a documentation gap.** `m-lab`'s docs do not say what happens when the same alert fires repeatedly. Deploying it without establishing that empirically is how a tracker fills up.
4. **`imageURL` renders a panel screenshot** — convenient, and worth noticing on a public repository: a screenshot of a dashboard can contain more than the alert, including labels and hostnames the filtering policy would otherwise have excluded.

---

## What this means for #289

1. **Criterion 5 needs no bespoke software.** Two maintained receivers exist. The build-versus-adopt question is answered: adopt.
2. **Approach 3 is the one that serves criteria 4 and 5 together**, costs no upstream divergence, and stores no long-lived credential. It is worth considering ahead of the dedicated receivers even though they are more mature.
3. **Prefer GitHub App or `GITHUB_TOKEN` over a PAT.** This is the single most consequential choice in the pipeline and it is easy to get wrong by reaching for the simplest tool.
4. **"With the telemetry attached" should be specified before it is built.** The prior art attaches *links and values*. If the PRD means the log lines and spans themselves — which criterion 4's "supporting telemetry" implies — that is an agent querying the backend, not a webhook receiver.
5. **The `fingerprint` field is the dedup primitive** and is available for free. That is [#325](https://github.com/launchpad-26/buzz/issues/325)'s question and this is the input to it.

---

## Confidence and what is still unknown

**High confidence** on the Grafana webhook payload fields and its auth options, quoted from the current documentation, and on `alertmanager-to-github`'s configuration surface, read from its own README.

**Maintenance status was initially unestablished and has since been measured** — see the section above. That check changed the recommendation from "compare them" to "one is three years stale".

**Not verified:** neither tool was deployed or run. No webhook was fired, no issue was created, and the Grafana payload was read from documentation rather than captured from a live alert. Approach 3 is assembled from parts I know exist rather than from a worked example — **I did not find a published implementation of "Grafana alert → GitHub Actions → agent investigation"**, so it is a design sketch with cited components, not prior art.

**Not researched:** whether Grafana's bundled Alertmanager is fully compatible with receivers written for Prometheus Alertmanager's webhook schema, which both tools assume — that compatibility is the load-bearing assumption for approaches 1 and 2 and I did not confirm it; GitLab or Jira equivalents; and whether GitHub rate-limits issue creation in a way that matters during an alert storm.

## Maintenance status, checked

Stars are not a maintenance signal, so this was measured:

```
=== pfnet-research/alertmanager-to-github ===
pushed_at: 2026-08-17T08:03:52Z  archived: false  open_issues: 0  stars: 69
last commit: 2026-08-17T08:03:37Z
latest release: v0.3.1 @ 2026-08-17T08:03:52Z

=== m-lab/alertmanager-github-receiver ===
pushed_at: 2026-04-07T13:26:42Z  archived: false  open_issues: 8  stars: 50
last commit: 2023-08-25T12:56:43Z
latest release: v0.11 @ 2023-01-04T15:19:05Z
```

`alertmanager-to-github` is actively maintained — a commit and a release on 2026-08-17, zero open issues. `m-lab/alertmanager-github-receiver` has had no default-branch commit since **August 2023** and no release since **January 2023**, with 8 open issues.

The two are therefore not comparable options. Combined with GitHub App auth versus a `repo`-scoped PAT, and `GroupKey` identity versus title matching, **approach 1 wins on every axis examined**; approach 2 is worth keeping in the record only as evidence the pattern has been built more than once.

**One trap worth recording.** `m-lab`'s `pushed_at` is **2026-04-07**, which looks current; its last default-branch commit is **2023-08-25**. `pushed_at` moves for a push to *any* branch or tag, so it is not a liveness signal — the default branch's last commit date is. Assessing a dependency by eyeballing "last pushed" gets this wrong.

---

## Sources

- [pfnet-research/alertmanager-to-github](https://github.com/pfnet-research/alertmanager-to-github) — GroupKey alert id, GitHub App auth, auto-close default, `.PreviousIssue` and `--reopen-window`
- [m-lab/alertmanager-github-receiver](https://github.com/m-lab/alertmanager-github-receiver) — PAT with `repo` scope, `-enable-auto-close`, title matching
- [Configure webhook notifications — Grafana Alerting](https://grafana.com/docs/grafana/latest/alerting/configure-notifications/manage-contact-points/integrations/webhook-notifier/) — payload fields, `fingerprint`, `values`, the URLs, auth options, custom payload templates
- [prometheus/alertmanager](https://github.com/prometheus/alertmanager) — the webhook contract both receivers implement
