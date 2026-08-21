# Preventing duplicate issues when an alert condition flaps

**Title:** Duplicate suppression for alert-driven issue creation
**Summary:** Nothing at the issue-creation step stops a flapping alert — suppression happens in three layers upstream, and only the third decides "same issue or new issue". Alertmanager's default `repeat_interval` is 4h, so one stuck condition re-notifies six times a day forever. The specific anti-flap control is Grafana's "Keep firing for", which holds an alert in a Recovering state so a re-trigger does not become a new alert. Both available dedup identities derive from the alert's label set, which makes `group_by` the real dedup configuration.
**Tags:** `observability` `alerting` `deduplication` `flapping` `alertmanager` `grafana`
**Reviewed:** 2026-08-22 · **Answers:** [#325](https://github.com/launchpad-26/buzz/issues/325)

---

## Finding

**Nothing at the issue-creation step stops a flapping alert.** Suppression happens in three layers upstream of it, and only the third decides whether a repeat becomes a new issue. Teams get this wrong by reaching for the third layer alone.

The sharpest number: **Alertmanager's default `repeat_interval` is `4h`** — one unresolved condition re-notifies **six times a day**, indefinitely. Whether that becomes six issues a day or one depends entirely on whether the receiver keys on a stable identity, and one of the two receivers surveyed in [#324](https://github.com/launchpad-26/buzz/issues/324) does not document that it does.

The specific anti-flap control is **"Keep firing for"**, which holds an alert in a *Recovering* state after its condition clears so a re-trigger inside that window does not become a new alert — stopping the cycle at source rather than cleaning up after it.

---
## The three layers

### Layer 1 — the rule: stop it firing at all

| Control | What it does |
|---|---|
| **Pending period** (`for`) | *"When the alert condition is met, the alert instance enters the Pending state. It remains in this state until the condition has been continuously true for the entire Pending period."* Kills transient blips before they are alerts. |
| **Keep firing for** (`keep_firing_for`) | *"defines how long the alert continues to fire after the condition is no longer met"* — the alert enters a **Recovering** state, and *"a re-triggered threshold incurred during this period won't trigger a new alert."* |

Keep-firing-for is the direct answer to this question. Grafana documents its purpose in exactly these terms: *"You can set a Keep firing for period to avoid repeated firing-resolving-firing notifications caused by flapping conditions."*

The two compose: pending period filters noise on the way **in**, keep-firing-for filters it on the way **out**.

### Layer 2 — the notifier: fewer notifications per firing

Alertmanager route defaults, which are what you get if nobody sets them:

| Setting | Default | What it controls |
|---|---|---|
| `group_by` | *(no default)* | **The identity.** Which labels batch alerts into one group |
| `group_wait` | `30s` | Initial delay before the first notification, so related alerts arrive together |
| `group_interval` | `5m` | Re-notify **only if** alerts were added or resolved since last time |
| `repeat_interval` | **`4h`** | Re-notify an **unchanged** group at most this often |

This layer reduces *notifications*, not *issues*. It is why the arithmetic above matters: `repeat_interval: 4h` is a floor of six webhook deliveries per day for one stuck condition.

### Layer 3 — the receiver: same issue, or a new one?

This is the only layer that decides duplication, and it is the one the tools differ on.

| Mechanism | Identity it uses |
|---|---|
| Grafana `fingerprint` (in the webhook payload) | *"Unique identifier for alerts with identical labels"* — a hash of the label set |
| `alertmanager-to-github`'s `--alert-id-template` | `"{{.Payload.GroupKey}}"` by default; *"The system tracks issues by this key to determine whether to create new issues or update existing ones"* |
| `m-lab/alertmanager-github-receiver` | Title matching on `{{ .Data.GroupLabels.alertname }}` plus an `-alertlabel` filter. **Reuse behaviour is not documented** |

So both available identities are **derived from the alert's label set** — `fingerprint` hashes it, `GroupKey` is the `group_by` grouping of it. Which means **`group_by` is the real dedup configuration**, two layers away from the receiver. Group too coarsely and unrelated faults land in one issue; too finely and every dimension gets its own.

---

## What happens on the second firing, and on resolve

**Second firing of the same condition, per tool:**

- `alertmanager-to-github`: tracked by alert id → updates the existing issue. With `--reopen-window` and the `.PreviousIssue` template variable, a recently-closed issue is **reopened** rather than duplicated. This is a designed answer to flapping.
- `m-lab`: undocumented. Not "does nothing" — *unknown*, which is worse for planning.

**On resolve:**

- `alertmanager-to-github`: `--auto-close-resolved-issues` is **enabled by default**; individual alerts opt out with an `atg_skip_auto_close: true` annotation.
- `m-lab`: `-enable-auto-close` closes by filtering open issues on `-alertlabel` and **matching titles** — brittle, since any retitle breaks the link.
- Grafana itself sends a `status: "resolved"` payload with `endsAt` set, so the receiver has what it needs either way.

**The flap cycle without layer 1** is therefore: fire → issue opened → resolve → issue auto-closed → fire → issue reopened (or a new one). Every cycle is at least two tracker events. `keep_firing_for` collapses the whole cycle into one firing.

---

## What this means for #289

1. **Duplicate suppression is not part of the alert-to-issue tool, and should not be scoped as if it were.** It is `for`, `keep_firing_for`, `group_by` and `repeat_interval` — three of the four set on the alert rule or the route, before any issue exists.
2. **The default `repeat_interval` of 4h must be set deliberately.** On this fork the tracker *is* the planning board, so an unattended stuck condition producing six deliveries a day is a board problem, not a notification problem.
3. **`group_by` is the dedup decision in disguise** and deserves to be written down per alert rather than defaulted.
4. **Reinforces [#324](https://github.com/launchpad-26/buzz/issues/324)'s recommendation.** `alertmanager-to-github` has explicit, documented answers to reuse, reopen and close; the alternative has none, and it is also three years stale. For this question the gap is not close.
5. **Criterion 5 needs a stated resolve-side policy.** Auto-close is on by default in the recommended tool. An issue that closes itself when the alert clears is reasonable for a flapping metric and wrong for a fault someone is meant to investigate — #289 says an alert *starts an investigation*, and an investigation that gets auto-closed under the investigator is a real failure mode. The `atg_skip_auto_close` annotation exists precisely for that and should be used deliberately.

---

## Confidence and what is still unknown

**High confidence** on the Alertmanager route defaults (`30s`, `5m`, `4h`) and on the two receivers' documented behaviour — quoted from the projects' own documentation.

**Moderate confidence on "Keep firing for" availability.** I read Grafana's own description of the feature and the Recovering state, but I sourced it partly from a *What's New* post dated 2025-05-05, and **I did not confirm which Grafana version introduced it or that it is present in the OSS release the cohort would self-host.** That is the one thing to check before relying on it, and it is the load-bearing control in this answer.

**Not verified:** nothing was run. No alert was made to flap, no webhook fired, no issue created, reopened or auto-closed. Every claim about second-firing behaviour is from documentation.

**Not researched:** Alertmanager **silences** and **inhibition rules**, which are the other two standard suppression mechanisms and which I did not cover — inhibition in particular (suppressing a dependent alert when its cause is already firing) is relevant to a small stack where one root fault trips several rules; whether GitHub rate-limits or abuse-detects rapid issue creation and reopening; and whether Grafana's bundled Alertmanager exposes the same route settings as upstream Prometheus Alertmanager, which is the same open compatibility question flagged in #324.

## Sources

- [Alertmanager configuration — Prometheus](https://prometheus.io/docs/alerting/latest/configuration/) — `group_by`, `group_wait` `30s`, `group_interval` `5m`, `repeat_interval` `4h`
- [Alert rule evaluation — Grafana](https://grafana.com/docs/grafana/latest/alerting/fundamentals/alert-rule-evaluation/) — pending period, keep firing for, state transitions
- [Grafana-managed alert rule "Recovering" state — Grafana Labs](https://grafana.com/whats-new/2025-05-05-grafana-managed-alert-rule--recovering--state/) — the Recovering state and its anti-flapping purpose
- [Configure webhook notifications — Grafana Alerting](https://grafana.com/docs/grafana/latest/alerting/configure-notifications/manage-contact-points/integrations/webhook-notifier/) — `fingerprint`, `status`, `endsAt`
- [pfnet-research/alertmanager-to-github](https://github.com/pfnet-research/alertmanager-to-github) — `--alert-id-template`, `--reopen-window`, `.PreviousIssue`, `--auto-close-resolved-issues`, `atg_skip_auto_close`
- [m-lab/alertmanager-github-receiver](https://github.com/m-lab/alertmanager-github-receiver) — `-enable-auto-close`, title matching
