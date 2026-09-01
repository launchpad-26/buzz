---
name: cloud
summary: Provider and account-side faults in cloud platform infrastructure — service health, IAM, quotas, autoscaling, and managed services
layer: Cloud Platform
---

# Cloud Platform

## First five checks

1. **Check the provider's public status page and personal health dashboard for the affected region.** A provider-side incident explains fleet-wide symptoms in minutes and rules out everything else on this list — check it first so you don't spend an hour debugging your own account for a fault that isn't yours.
2. **Check for a recent deploy, IaC apply, or config change to the affected account or resource in the last change window.** Most cloud-layer incidents are self-inflicted: a role policy edit, a security group change, a Terraform apply, or a manual console change immediately preceding onset.
3. **Check IAM: has a role, policy, or trust relationship changed, and can the calling identity still assume the role it needs?** Auth failures that look like an application outage are frequently a revoked permission, an expired credential, or a changed trust policy on an assumed role.
4. **Check service quotas and rate limits against current usage for the affected service.** Autoscaling that silently hits an account limit, or an API that starts throttling, produces symptoms indistinguishable from a capacity problem until the quota is checked directly.
5. **Check whether autoscaling is responding to the load it sees, and whether a managed service is at its own configured limit (e.g. connection pool, concurrency cap, table/partition throughput).** This is the highest-yield check for that specific symptom shape — "it worked yesterday but load didn't change" — where the managed service's own ceiling, not the workload, is often the fault.

## Evidence sources

- Provider status page and personal/account health dashboard (per-region, not global)
- Provider audit/activity log (who changed what, when, from where — the API-call-level record)
- IAM policy and role-assumption history
- Service quota and rate-limit dashboards for the affected service
- Autoscaling group / managed compute scaling activity history
- Managed service metrics (connection counts, throttled-request counts, provisioned vs consumed throughput)
- Cost and billing anomaly alerts (a cost-control action can be the trigger, not just a symptom)
- CDN/edge and load balancer health-check and target-group status
- Cross-region replication and DNS failover status

## Common root causes in this layer

- A provider region or availability zone outage or degradation
- An IAM policy, role trust relationship, or credential expiring or being revoked
- A service quota or API rate limit hit, causing silent throttling or request rejection
- Autoscaling misconfiguration — wrong metric, cooldown too long, max capacity set too low
- A managed service hitting its own internal limit (connection pool exhaustion, provisioned throughput cap, concurrency limit)
- An automated cost-control or budget-alert action that throttled or shut down a resource
- DNS or load balancer misconfiguration following a failover or region shift
- A change (IaC apply, console edit, policy update) applied without a corresponding review or rollback plan
- Cross-AZ or cross-region network partition affecting only a subset of traffic

## Diagnostic commands and queries

Every command below is read-only. Where a provider CLI has a same-named mutating counterpart or a
dangerous flag, it is called out explicitly — do not run anything but the listed read verb during
an incident.

- Query the provider status API or health dashboard for the affected region/service (read-only by nature; no provider exposes a mutating status endpoint).
- List/describe IAM roles, policies, and trust relationships for the affected identity (e.g. `aws iam get-role`, `aws iam simulate-principal-policy`, `gcloud iam roles describe`, `az role assignment list`). These are read-only `get`/`list`/`describe`/`simulate` verbs — do not run the corresponding `put`/`attach`/`delete` verbs, which mutate policy.
- Query current quota and usage against limits (e.g. `aws service-quotas get-service-quota`, `gcloud compute project-info describe`, `az vm list-usage`). Read-only; the mutating sibling is a quota *increase request*, which is a change action, not a diagnostic.
- Describe autoscaling group activity history and current desired/min/max capacity (e.g. `aws autoscaling describe-scaling-activities`, `gcloud compute instance-groups managed describe`). Read-only — do not call the corresponding `set-desired-capacity`/`update-instance-group` mutating commands mid-diagnosis.
- Query the provider audit/activity log for the affected resource in the incident window (e.g. `aws cloudtrail lookup-events`, `gcloud logging read`, `az monitor activity-log list`). Read-only.
- Describe load balancer target group / backend health (e.g. `aws elbv2 describe-target-health`, `gcloud compute backend-services get-health`). Read-only — do not run the corresponding `register-targets`/`deregister-targets` calls.
- Get current metrics for the managed service in question — connection count, throttled-request count, consumed vs provisioned throughput (e.g. `aws cloudwatch get-metric-data`, `gcloud monitoring time-series list`). Read-only.
- Check DNS resolution and health-check status for the affected endpoint (e.g. `dig`, `nslookup`, `aws route53 get-health-check-status`). Read-only.

## Escalation signals

- Provider status page confirms an active incident in the affected region or service — stop
  investigating account configuration and hand off to tracking the provider's own incident, since no
  account-side fix resolves a provider-side outage.
- IAM, quotas, autoscaling, and managed service limits all check out clean, and traffic reaching the
  affected resource is confirmed healthy at the load balancer or edge — the fault is upstream or
  downstream of this layer (application logic, database, or client-side), not in the cloud platform
  itself.
- The audit log shows no change to any resource, policy, or configuration in or before the incident
  window, and no scaling or quota event correlates with onset — a genuinely un-triggered cloud-layer
  fault is rare enough that this pattern usually means the true cause sits in application code, a
  database, or a dependency the cloud platform merely hosts.
- Symptoms are isolated to a single host or process rather than a scope the cloud platform controls
  (a region, an AZ, an account-wide quota, an IAM identity) — single-instance symptoms with normal
  fleet-wide health point to the endpoint or application layer, not the platform.
- Network connectivity is confirmed intact between all cloud-side components (VPC routing, security
  groups, peering, DNS all resolve and pass health checks) but the failure persists — the fault has
  moved past the network/cloud boundary into the application or database layer.
