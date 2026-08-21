# What a drop-and-redact policy can and cannot express

**Title:** Expressiveness of the collection tooling's filtering and redaction controls
**Summary:** A true allowlist exists — the redaction processor's `allowed_keys` deletes every attribute not explicitly listed, so the policy fails closed. What it cannot express is free text: the processor works on attributes only and does not sanitise an unstructured log body, which is exactly the shape of #279's raw-stderr incident. Logs and metrics support is Alpha; only traces are Beta. Redaction can run in Alloy on the member's machine or centrally, and those are materially different promises to make to a member.
**Tags:** `observability` `redaction` `filtering-policy` `opentelemetry` `security` `criterion-6`
**Reviewed:** 2026-08-22 · **Answers:** [#335](https://github.com/launchpad-26/buzz/issues/335)

---

## Finding

**Yes — a true allowlist exists, and it is the strongest thing in this document.** `allowed_keys` *"deletes span attributes that don't match a list of allowed span attributes"*. You declare what you keep; everything else is dropped. That is the inversion the question asked about, and it is available out of the box.

**What it cannot express is the case this repository has already been bitten by: free text.** The processor operates on **attributes only**. A secret inside a log *message* — exactly [#279](https://github.com/launchpad-26/buzz/issues/279)'s raw-stderr shape — is invisible to it.

**Two things to check before relying on it:** logs and metrics support is **Alpha**, only traces are Beta; and redaction can run on the member's machine or centrally, which is a policy decision rather than a config one.

---
## What it can express

### The allowlist — `allowed_keys`

> *"The redaction processor deletes span attributes that don't match a list of allowed span attributes."*

<sub>Wording note per [#420](https://github.com/launchpad-26/buzz/issues/420). The quoted line above and the `blocked_values` line below say **"span attributes"**; the current upstream README words the same behaviour uniformly as **"span, log, and metric datapoint attributes"**. The substance is unaffected — the processor covers all three signals, as the stability table below states — but a reader diffing this note against upstream could briefly wonder whether behaviour changed. It did not; this quote was captured from secondary documentation using the older phrasing.</sub>

> *"The `allowed_keys` approach is powerful because it is a whitelist. Instead of trying to think of every sensitive key that might appear, you define only the keys you want to keep. Everything else gets dropped."*

This matters more than any other single fact here. A denylist fails silently the first time somebody adds an attribute nobody anticipated — which is how telemetry leaks. An allowlist fails *closed*: a new field is dropped until someone deliberately adds it. For a PRD whose criterion 6 requires knowing what is **not** collected, an allowlist makes the policy and the enforcement the same document.

### Value matching, and its precedence rules

| Setting | What it does |
|---|---|
| `allowed_keys` | Keys to keep. Everything else is deleted |
| `blocked_values` | *"a list of regular expressions for blocking values of allowed span attributes"* — matches are **masked**, not dropped |
| `allowed_values` | Takes precedence over `blocked_values` — *"allows operators to explicitly whitelist known-safe values while still blocking broader patterns"* |
| `ignored_keys` | *"Any keys in this list are allowed so they don't need to be in both lists"* |

**Order matters and is documented:** *"Span attributes that aren't on the allowed list are removed before any value checks are done."* So the allowlist is the primary control and regex masking is a second pass over what survived.

The worked example from the documentation is a good model for the cohort: if `notes` is allowed, the attribute is kept — but a credit-card-shaped value inside it is masked by `blocked_values`. Keep the field, redact the payload.

### It covers all three signals

Traces, metrics **and** logs — so one policy expression can govern the whole pipeline rather than needing a different mechanism per signal.

---

## What it cannot express

### 1. Free text — the important gap

The processor works on **attributes only**. It does not sanitise unstructured log body or span content.

There is one partial exception: *"For log records whose body is a map, the processor additionally appends audit attributes into the body map itself."* So a **structured** body gets some treatment; a plain string body gets none.

**Why this is the gap that matters here.** #279 exists because raw subprocess stderr reached a public field — a secret in free text, not in a structured key. [#314](https://github.com/launchpad-26/buzz/issues/314) found the relay's join path emits messages like `audio auth failed: {e}`, where `{e}` is an interpolated error string. If a secret ever lands in one of those, `allowed_keys` will not see it, because the message is the body, not an attribute.

**The escape hatch is a different processor.** The `transform` processor's OTTL statements can rewrite body text (pattern replacement over `body`). That is the tool for free text, and it is a denylist by nature — regexes for things you thought of. So the strong guarantee applies to attributes and the weak one applies to messages, which is exactly the wrong way round for a codebase whose known incident was in a message.

### 2. Stability is not uniform

- **Traces: Beta**
- **Metrics: Alpha**
- **Logs: Alpha**

Criterion 2 — the error a human saw — is a **logs** problem, and logs are the least mature path for this processor. Worth knowing before the filtering policy is written as though all three are equivalent.

### 3. A conditional worth reading twice

*"Database sanitization for spans and metric attributes only runs when the telemetry includes a `db.system.name` or `db.system` attribute."* A control that only engages when a particular attribute is present is a control that silently does nothing when it is absent.

### 4. Numeric values

There is an open upstream issue on numeric attribute values not being redacted (`opentelemetry-collector-contrib#36684`). I did not read it in full and cannot say whether it is current, but a value-masking control that treats strings and numbers differently is worth checking against before relying on it for anything numeric.

---

## Where in the path it can run

Both, and the choice is a policy decision:

- **On the member's machine.** Alloy exposes the collector's processors as `otelcol.processor.*` components, so redaction can run in the agent — data is filtered **before it leaves the member's laptop**.
- **At the central collector.** Simpler to change and audit in one place; the unfiltered data has already crossed the network and arrived.

For [#326](https://github.com/launchpad-26/buzz/issues/326)'s consent question these are very different promises. "We drop it before it leaves your machine" is a materially stronger statement to a member than "we drop it when it arrives at ours", and only the first is true if redaction runs centrally.

---

## What this means for #289


> **Recommendations, not findings.** Everything in this section is my assessment as the author, not behaviour established by the evidence above. Per [ADR-0003]'s claim rule: a claim about how the system *behaves* carries a source reference; a claim about what the cohort *should do* is opinion, attributed. Nothing is both — so nothing below is cited as though it were established.
1. **Criterion 6's policy can be written as an allowlist and enforced as one.** That is a much better position than the PRD assumes, and it should be written that way — a list of permitted attribute keys — rather than as prose about what is excluded.
2. **The known-bad case is the weakly-covered one.** Attributes get the strong guarantee; message bodies get regexes. Given #279, the policy should say explicitly what happens to interpolated error strings, and probably that they are not exported at all rather than exported-and-scrubbed.
3. **Run redaction in Alloy, on the member's machine**, unless there is a reason not to. It is the same processor either way and it makes a stronger, truer promise.
4. **Check the Alpha status for logs** before the policy depends on it.
5. **This pairs with [#311](https://github.com/launchpad-26/buzz/issues/311).** The allowlist is only as good as the field inventory it is written from; #311 produces that inventory and is unanswered.

---

## Confidence and what is still unknown

**High confidence** on the processor's semantics, ordering, signal coverage and stability levels — all from the component's own README and documentation.

**Not verified: nothing was run.** No processor was configured, no attribute redacted, no regex tested. Everything here is documentation, and the ordering guarantee in particular is the kind of thing worth confirming with a five-minute test before a policy leans on it.

**Also not researched:** the `transform`/OTTL processor's actual capability over body text, which I have named as the escape hatch without establishing what it can and cannot match — **that is the largest remaining gap**, because it is the mechanism that would have to cover the #279 case; the `filter` processor, which drops whole spans or records rather than attributes and is a different and possibly better tool for "do not collect this at all"; issue #36684's current status; whether Alloy's `otelcol.processor.redaction` is at feature parity with the upstream contrib processor, which I assumed rather than checked; and the performance cost of regex value-matching at volume.

## Sources

- [Redaction Processor README — opentelemetry-collector-contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/processor/redactionprocessor/README.md) — signals, attributes-only scope, map-body exception, stability levels, the `db.system` conditional
- [redactionprocessor (v0.154.0) — opentelemetry-collector-contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/v0.154.0/processor/redactionprocessor) — configuration surface
- [Mastering the OpenTelemetry Redaction Processor — Dash0](https://www.dash0.com/guides/opentelemetry-redaction-processor) — the allowlist framing, `allowed_values` precedence, processing order
- [Redaction processor — Splunk Docs](https://help.splunk.com/en/splunk-observability-cloud/manage-data/splunk-distribution-of-the-opentelemetry-collector/get-started-with-the-splunk-distribution-of-the-opentelemetry-collector/collector-components/processors/redaction-processor) — `ignored_keys`, the allowed-then-blocked worked example
- [No Redaction of Numeric Attribute Values · Issue #36684](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/36684) — surfaced, not read in full
