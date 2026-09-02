# Incident Postmortem

## Incident Metadata

| Field | Value |
|---|---|
| **Incident Number** | _Unique identifier for tracking and reference_ |
| **Date** | _Date and time of incident discovery_ |
| **Severity** | _SEV-1 / SEV-2 / SEV-3 based on impact_ |
| **Duration** | _Time from detection to recovery_ |

## Time Metrics

| Metric | Value |
|---|---|
| **TTD (Time To Detect)** | _Minutes from start to discovery_ |
| **TTM (Time To Mitigate)** | _Minutes from detection to service recovery_ |
| **TTR (Time To Resolve)** | _Minutes from start to root cause fix deployed_ |

## Incident Leads and Roles

| Role | Owner | Contact |
|---|---|---|
| **Incident Commander** | _Name and team_ | _Email or Slack handle_ |
| **Subject Matter Expert** | _Name and team for affected layer_ | _Email or Slack handle_ |
| **Communications Lead** | _Name responsible for customer updates_ | _Email or Slack handle_ |

## Executive Summary

_One or two sentences capturing what failed, the observed impact, and the immediate workaround or fix applied._

## Impact Assessment

### End-User Impact
_Describe what customers saw: unavailable feature, degraded performance, errors. Include affected user count or percentage if known._

### Infrastructure Impact
_Describe degraded or failed services, systems, or dependencies. Resource exhaustion, cascading failures, or secondary effects._

### Productivity Impact
_If applicable: loss of internal tooling, deployment blockers, or team coordination disruption._

## Timeline

| Time | Event | Details |
|---|---|---|
| _HH:MM_ | _Event type (alert, page, deploy, workaround applied, service restored)_ | _What happened and who was involved_ |
| _HH:MM_ | _Next event_ | _Additional context_ |

## Trigger

_Describe the initial event that started the incident. Distinguish between the trigger (the event that happened) and the root cause (why it created an outage). Example: "A deployment of service X at 14:22 UTC" is trigger; "the deployment introduced a memory leak" is root cause._

## Detection and Response

_Describe how the incident was detected, who was alerted, and what investigations or mitigations were attempted before resolution._

## Process Breakdown

_Describe failures in process, procedure, tooling or detection systems that allowed the trigger to cause an outage. Example: "Code review did not catch the memory leak because reviewers cannot see heap usage patterns in diffs."_

## Hypotheses Considered and Ruled Out

_Describe each hypothesis tested during investigation, whether it was supported, refuted, or untested, and the specific evidence that decided its status. This is the evidence chain._

| Hypothesis | Verdict | Evidence |
|---|---|---|
| _Concise statement of a suspected cause_ | Supported / Refuted / Untested | _Specific logs, metrics, traces, or tests that proved or disproved it_ |
| _Next hypothesis_ | Supported / Refuted / Untested | _The evidence that decided it_ |

## What Caused the Incident?

_Statement of root cause. This is the failure mode that, if corrected, would prevent recurrence. This is a strict failure of a control or design, not an external event; distinguish it clearly from Trigger above._

## Resolution

_Describe the fix or workaround applied to restore service. Include deployment time, blast radius, validation steps, and whether it is temporary or permanent._

## Open Questions

_Outstanding questions that remain after the investigation, not yet answered by evidence._

| Question | Owner | Status |
|---|---|---|
| _Question raised during the incident or postmortem_ | _Name responsible for follow-up_ | Open / In Progress / Closed |

## Action Items

_Tasks to prevent recurrence or improve response. Include type (process, tooling, design), owner, priority, related bug tracker issue, and due date._

| Action | Type | Owner | Priority | Bug # | Due Date |
|---|---|---|---|---|---|
| _Specific action item_ | Process / Tooling / Design | _Name_ | High / Medium / Low | _Ticket or issue #_ | _Target date_ |

## Appendix: Investigation Details

_Any additional technical details, code snippets, configuration changes, or detailed logs that support the analysis above but were too large for the main sections._
