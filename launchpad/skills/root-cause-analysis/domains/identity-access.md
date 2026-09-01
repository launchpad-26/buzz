---
name: identity-access
summary: Who can get in — authentication, authorization, and the trust plumbing between them
layer: Identity and Access
---

# Identity and Access

## First five checks

1. **Check certificate and secret expiry on every trust relationship in the path** — signing certs, client secrets, and token-signing keys on identity providers, service principals, and SAML/OIDC trust configs. Expiry is silent until the exact second it isn't, it fails every user or service behind that trust at once, and it is the single most common cause of a sudden, total identity outage.
2. **Check directory synchronisation status and lag** — is the sync agent running, and how far behind is it? A stalled or backlogged sync means changes made in the source directory (password resets, group membership, account enablement/disablement) never reach the systems doing the authenticating, producing a fault that looks intermittent or user-specific but is actually a stale replica.
3. **Check recent conditional access / access policy changes** — list policy changes in the incident window. A tightened or misconfigured conditional access rule (device compliance, location, risk score) is one of the highest-yield "started suddenly, nothing changed" explanations, because the change is invisible to the user who suddenly can't sign in.
4. **Check MFA and identity provider service health** — is the MFA provider, the IdP itself, or its regional endpoint degraded? This distinguishes a scoped account problem from a provider-wide outage that no amount of per-user troubleshooting will fix.
5. **Check token and session lifetime versus the failure pattern** — do failures cluster at a fixed interval after login (matching an access or refresh token lifetime), or correlate with a session revocation event? This catches faults that present as "worked for a while, then broke" rather than "never worked."

## Evidence sources

Identity provider sign-in and audit logs (success/failure, reason codes), directory synchronisation logs and connector health dashboards, conditional access / policy evaluation logs, MFA provider status page and challenge logs, SAML/OIDC trust and federation metadata, certificate and secret expiry dashboards, group membership change history, session and token issuance logs, privileged access / just-in-time elevation logs.

## Common root causes in this layer

Expired signing certificate or client secret on an IdP, service principal, or federation trust. Directory synchronisation stalled or badly lagged. A conditional access or access policy change that unintentionally tightened scope. MFA provider outage or misconfigured MFA method. SAML/OIDC trust metadata mismatch after a provider-side rotation. Group membership change that hasn't propagated to a downstream system yet. Token or session lifetime misconfiguration causing premature expiry. Clock skew between an identity provider and a relying party breaking token validation. Account lockout from a leaked-credential or risk-based policy triggering on legitimate traffic.

## Diagnostic commands and queries

- Query identity provider sign-in logs filtered to the affected time window and error/reason code (e.g. Entra ID sign-in logs, Okta System Log, AWS CloudTrail `ConsoleLogin` events) — read-only log query.
- Check certificate and secret expiry dates on federation trusts, service principals, and app registrations via the provider's admin API or CLI `list`/`describe`/`show` commands — read-only; avoid any `rotate`, `renew`, or `reset` subcommand, which mutates the credential.
- Check directory sync connector health and last successful sync timestamp (e.g. Azure AD Connect health, sync agent status endpoint) — read-only status query.
- List recent conditional access / access policy changes via the provider's audit log or policy version history — read-only; do not use the corresponding "revert" or "restore" action while investigating.
- Check MFA provider status via its public status page or health API — read-only.
- Query SAML/OIDC federation metadata for trust configuration (issuer, certificate thumbprint, endpoints) via a `metadata`/`describe` read endpoint — read-only; do not re-import or overwrite metadata.
- List recent group membership changes via directory audit logs (`get`/`list` membership-change events) — read-only.
- Decode and inspect a sample token's claims (issuer, audience, expiry) using a local decoder — read-only; never use an endpoint that mints or refreshes a token as a diagnostic step.

## Escalation signals

- Sign-in and audit logs for this identity/directory layer show no failures, expiries, or relevant changes in the incident window, and the failure reproduces only when reaching a specific downstream application or API — the fault is likely in that application's authorization logic, not in identity and access.
- The identity provider, directory sync, and MFA provider all report healthy status, trust certificates are valid, and no conditional access policy changed, yet users report being unable to reach a service — check network path and DNS to the identity provider and the application before continuing to investigate this layer.
- Authentication succeeds (valid token issued, session established) but the failure occurs after that point, e.g. in application-level permission checks, feature flags, or data access — hand off to the application or database layer, since identity and access ends at successful authentication and coarse-grained authorization.
- The pattern affects only one endpoint's compute, storage, or network path (e.g. a single VM or region) rather than a class of user, group, or trust relationship — this points to an infrastructure fault rather than identity and access, which is defined by who can authenticate and what they're authorized to reach.
