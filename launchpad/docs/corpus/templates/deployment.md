---
id: corpus-template-deployment
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "A node's front matter is validated against node.schema.json, whose type enum is architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion, and contains no template or policy value."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Every other corpus meta-document at the recorded revision — AGENTS.md excepted, which is type: agent — uses type: governance: README.md, standards/confidence.md and standards/decision-references.md all do."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "schema/README.md and schema/COMPATIBILITY.md were both read in full while choosing this node's type, and neither names a template-specific or policy-specific value beyond what node.schema.json's own field table already states."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/README.md"
      - "launchpad/docs/corpus/schema/COMPATIBILITY.md"
  - statement: "This node is a meta-document about how to author a corpus node, not itself a deployment topology, so governance is chosen by the same reasoning corpus-readme and the sibling architecture-container template (issue #1327) already recorded for their own type choices, rather than as an independent precedent this node invents."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/README.md"
    confidence: 0.6
  - statement: "A corpus node instance actually written from this template — a real deployment-view document about a real system's environments — most plausibly takes type: architecture rather than type: operations or type: platforms: arc42 groups its Deployment View (§7) as one of the same twelve sections as Context & Scope (§3) and Building Block View (§5) inside one architecture-documentation template, and the C4 model groups its Deployment diagram among the same diagram set (core plus supplementary) that the Container and Context diagrams belong to. type: platforms was considered and set aside because this repository's own platform-shaped subject matter is client platforms (desktop/web/mobile), not infrastructure. type: operations was considered and set aside on the strength of a sibling precedent: issue #1347's runbook template independently concluded a real operational-practice document takes type: operations, which is a different kind of subject (what to do when something breaks) than a structural view (where things run)."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "https://arc42.org/overview"
      - "https://c4model.com/"
    confidence: 0.6
  - statement: "Issue #1347's corpus-template-runbook pull request (#1527) states that a real instance of the runbook template should use type: operations, calling that value \"the natural fit for an operational document\" — establishing operations as the surface this template's own real-instance candidates (architecture, platforms) are being distinguished against, not merely asserted against nothing."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1527 (open PR, corpus-template-runbook), read directly via gh pr view"
  - statement: "Relationships must resolve against the corpus tree on the branch being merged into, and at the recorded revision origin/launchpad's launchpad/docs/corpus tree carries exactly four validated content nodes: AGENTS.md (corpus-agents), README.md (corpus-readme), standards/confidence.md (corpus-standard-confidence) and standards/decision-references.md (corpus-standard-decision-references); schema/ is present but excluded from validation."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> AGENTS.md, README.md, standards/confidence.md, standards/decision-references.md; schema/ present but excluded from validation"
  - statement: "None of the four existing content nodes has deployment, infrastructure, environments, arc42 or C4 as its subject, so no relationships.target among them would be a substantive edge rather than a citation duplicate of what this node's evidence ledger already cites directly."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
    confidence: 0.8
  - statement: "arc42's overview page states section 7, Deployment View, as \"Hardware, infrastructure and deployment\"; it states section 3, Context & Scope, as \"External systems and interfaces\", and section 5, Building Block View, as \"Structure of source code, modularization, hierarchically refined\" — three separate, non-overlapping sections of the same twelve-section template."
    entry_class: FACT
    evidence:
      - "https://arc42.org/overview"
  - statement: "arc42's section-7 documentation states the deployment view covers two things: \"the technical infrastructure used to execute your system, with infrastructure elements like geographical locations, environments, computers, processors, channels and net topologies\", and \"the mapping of (software) building blocks to that infrastructure elements\"; its stated motivation is that \"software does not run without hardware\" and that infrastructure \"can and will influence your system and/or some cross-cutting concepts\"."
    entry_class: FACT
    evidence:
      - "https://docs.arc42.org/section-7/"
  - statement: "arc42's section-7 documentation defines two levels: Infrastructure Level 1, covering distribution across locations/environments/computers, the justification for that structure, and the mapping of software artifacts to infrastructure elements; and Infrastructure Level 2, which gives \"the internal structure of (some) infrastructure elements from infrastructure level 1\" for deeper examination of selected components. It recommends UML deployment diagrams, or \"any kind that is able to show nodes and channels of the infrastructure\"."
    entry_class: FACT
    evidence:
      - "https://docs.arc42.org/section-7/"
  - statement: "The C4 model's own front page groups System Context, Container, Component and Code as \"a set of hierarchical diagrams\", and names System Landscape, Dynamic and Deployment as \"an additional set of supporting diagrams\" — a stated distinction between the two groups, not a claim this node infers."
    entry_class: FACT
    evidence:
      - "https://c4model.com/"
  - statement: "The C4 Deployment diagram page states a deployment diagram \"allow[s] you to illustrate how instances of software systems and/or containers in the static model are deployed on to the infrastructure within a given deployment environment\" (naming production, staging and development as example environments), using deployment nodes (physical, virtualized, containerized or execution-environment infrastructure, which can be nested) and infrastructure nodes (for example DNS services, load balancers and firewalls), for an audience of \"technical people inside and outside of the software development team; including software architects, developers, infrastructure architects, and operations/support staff\"."
    entry_class: FACT
    evidence:
      - "https://c4model.com/diagrams/deployment"
  - statement: "The C4 model's container-abstraction page states that a single logical container may be deployed with a different physical topology in different environments and gives a worked example: \"At development time I might have three web applications running on a single Apache Tomcat server, while each web application may be deployed onto a dedicated Apache Tomcat server in a live environment. In this situation, each web application is a 'C4 container', with the deployment being a separate concern.\""
    entry_class: FACT
    evidence:
      - "https://c4model.com/abstractions/container"
  - statement: "Issue #1327's architecture-container template pull request (#1529, open and unmerged at the recorded revision) describes a container as \"the deployable, runnable units that make it up, the technology choice for each, and how they communicate,\" and states, in its Escalations section quoting the C4 primary source, that the Container diagram \"says very little about deployment aspects... because it will likely vary across different environments\" and that a Deployment diagram is a distinct diagram type, concluding \"the boundary is not ambiguous at the primary-source level.\" The more elaborate framing this node uses elsewhere — deployment as \"the physical/environment mapping\" — is this node's own synthesis of that same C4 primary source (cited directly, as FACT, above), not a verbatim statement #1529 itself makes; #1529's own wording is the terser sentence quoted here."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1529 (open PR, corpus-template-architecture-container), read directly via gh pr view and gh pr diff"
  - statement: "The research note at launchpad/Research/project-documentation-templates.md, on unmerged PR #1466, lists arc42's twelve sections including \"7. Deployment View\", and states the C4 model's diagrams are \"diagrams, not prose\" that \"slots into arc42 §3/§5/§7 rather than competing with it\" — naming §7 as one of the sections C4's diagrams (including its Deployment diagram) slot into, though the note does not itself elaborate on the Deployment diagram or the container/deployment boundary anywhere in its text."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1466 (unmerged research note)"
  - statement: "docker-compose.yml at the repository root defines postgres, redis, adminer, keycloak, minio, minio-init and prometheus services on a single bridge network (buzz-net), each labeled com.buzz.env: \"dev\", and defines no relay or buzz-relay service of its own."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "CLAUDE.md's Getting Started section instructs `just relay` to \"start relay at ws://localhost:3000\" as a separate step from `just setup`, consistent with the relay running as a locally built process against docker-compose's containerized Postgres and Redis rather than as a fourth container inside docker-compose.yml itself."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "The repository's root Dockerfile builds the buzz-relay binary and the buzz-web static bundle into a debian-slim runtime image, published as ghcr.io/launchpad-26/buzz per its own header comment and per .github/workflows/docker.yml, whose `on:` block triggers the workflow on push to the launchpad branch, on relay-v[0-9]* tags, on pull requests touching a defined set of paths (Dockerfile, crates/**, web/**, and related build inputs — build-only, no push), and on manual workflow_dispatch for a relay-tag rescue republish."
    entry_class: FACT
    evidence:
      - "Dockerfile"
      - ".github/workflows/docker.yml"
  - statement: "deploy/charts/buzz/README.md documents two operating profiles for the buzz Helm chart selected by values: a default \"Production\" profile (external managed Postgres/Redis/S3, `secrets.existingSecret`, no chart-side secret autogeneration, HA-capable with `replicaCount >= 2`) and an opt-in \"Quickstart\" profile for evaluation (in-cluster Postgres + Redis + MinIO subcharts/Deployments, chart-autogenerated secrets, single replica)."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "deploy/charts/buzz/values.yaml's default image.repository is ghcr.io/block/buzz (the upstream chart's own default), which is a different GHCR namespace than this fork's own docker.yml workflow, which publishes to ghcr.io/launchpad-26/buzz — a real, checked discrepancy between the chart's shipped default and this fork's own built image, not resolved by this node."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
      - "Dockerfile"
      - ".github/workflows/docker.yml"
  - statement: "deploy/charts/buzz/README.md states production deploys are designed for ArgoCD and Flux GitOps, pointing to deploy/charts/buzz/examples/argocd-app.yaml and deploy/charts/buzz/examples/flux-helmrelease.yaml as the canonical configurations, and states that production deploys MUST use `secrets.existingSecret` because Helm's `lookup` function (needed for chart-side secret autogeneration) returns empty when ArgoCD or Flux render the chart with `helm template`."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
      - "deploy/charts/buzz/examples/argocd-app.yaml"
      - "deploy/charts/buzz/examples/flux-helmrelease.yaml"
  - statement: "deploy/charts/buzz/templates/deployment.yaml renders a Kubernetes Deployment with a RollingUpdate strategy of maxSurge: 1 and maxUnavailable: 0, and its replica count is taken from .Values.replicaCount unless .Values.autoscaling.enabled is set, in which case the field is omitted so a HorizontalPodAutoscaler controls it instead."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/deployment.yaml"
  - statement: "A second, separately versioned chart, deploy/charts/buzz-push-gateway, exists alongside deploy/charts/buzz, with its own Chart.yaml, its own values-production.yaml carrying deliberately empty required fields (image.tag, image.digest, appAttestAppId) that a production renderer must inject, and its own PodDisruptionBudget, NetworkPolicy, PrometheusRule and migration Job templates — a second deployable unit with a deployment topology of its own, distinct from the buzz chart's."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz-push-gateway/Chart.yaml"
      - "deploy/charts/buzz-push-gateway/values-production.yaml"
      - "deploy/charts/buzz-push-gateway/templates/pdb.yaml"
      - "deploy/charts/buzz-push-gateway/templates/networkpolicy.yaml"
      - "deploy/charts/buzz-push-gateway/templates/prometheusrule.yaml"
      - "deploy/charts/buzz-push-gateway/templates/migration-job.yaml"
  - statement: "crates/buzz-relay/Cargo.toml declares a [[bin]] target (name = \"buzz-relay\", path = \"src/main.rs\"), and crates/buzz-relay/src/main.rs exists at that path — an independently runnable binary by the same test (a [[bin]] target plus its entry point) issue #1327's architecture-container template applies to identify a container."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml"
      - "crates/buzz-relay/src/main.rs"
  - statement: "Issue #1327's architecture-container template (PR #1529) independently established buzz-relay as a C4 container using exactly this bin-target-plus-entry-point test, and cites CLAUDE.md's own crate map describing it as the relay server's \"main entry point\"; this node reuses that established container identity for its worked deployment illustration rather than re-arguing it."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1529 (open PR, corpus-template-architecture-container), read directly via gh pr view and gh pr diff"
  - statement: "Every non-.md file under the corpus root is rejected by validate.py today, including one placed under a generated/ directory, because no generator exists yet to reproduce it from canonical Markdown, so a corpus change may add Markdown only until issue #1316 lands."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Because the corpus accepts Markdown only, a deployment diagram authored into a corpus node under this template must be expressed as text inside the Markdown body — for example a Mermaid fenced code block — rather than as a separate diagram asset, until issue #1316's generated-artifact mechanism exists."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.8
  - statement: "Issue #605 (parent PRD) states the real acceptance criterion for every template task in this batch as: every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts — distinct from the byte-identical MUST/SHOULD/enforcement/policy checklist copied into this node's own issue #1336 from the standards-track issues."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 (parent PRD), opened directly via gh issue view"
  - statement: "Issue #1336's definition of done otherwise requires one hand-authored canonical document, schema-valid front matter, one independently maintainable idea, traceable FACT/INFERENCE/TEAM_KNOWLEDGE claims, links instead of duplicated content, a check against the recorded provenance revision, and a clean validator run."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1336 definition of done, opened directly via gh issue view"
  - statement: "Issue #1467 records that the cross-model (Codex) review provider is currently unavailable — the Codex workspace is out of credits, confirmed twice including with a trivial read-only prompt, and no other external-model CLI (gemini, agy, pi, llm, ollama, cursor-agent, opencode) is installed — so a same-model adversarial self-review is the substitute this node's own review pass used."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1467, opened directly via gh issue view"
---

# Template: deployment

How to write a corpus node whose subject is a system's **deployment view** — where
its already-inventoried containers actually run: the infrastructure, the named
environments (development, staging, production, or whatever a system calls its
own), and how the mapping of containers onto infrastructure changes from one
environment to the next. This node is the template itself, not an instance of one:
it states what a deployment node must contain, not a deployment diagram for any
real system.

## Scope and authority

**This node covers** the purpose of a deployment document, the sections it must
contain, what evidence each section needs, and the industry model it adapts (arc42
section 7, read together with the C4 model's Deployment diagram). It does not
itself document any real system's deployment topology, beyond one illustrative,
scoped worked example.

**A note on this issue's own definition of done.** Issue #1336's checklist carries
a MUST/SHOULD/enforcement/exception block copied verbatim from the standards-track
issues that produced `standards/confidence.md` and `standards/decision-references.md`
— documents whose subject is a normative policy. This node's subject is a
template, and the parent PRD (#605) states the acceptance bar that actually
applies to a template task: *every template states its purpose, required
sections, evidence expectations and the industry model/standard it adapts.* This
document is built against that sentence. The rest of #1336's checklist — one
hand-authored document, schema-valid front matter, one independently maintainable
idea, traceable claims, links instead of duplication, a check against the
recorded revision, a clean validator run — is generic to any corpus node and is
honoured below regardless. This is the same note the sibling architecture-container
template (#1327, PR #1529) records for the identical stale-checklist problem.

**Its authority is derived, not original.** `node.schema.json` is the front-matter
law; `AGENTS.md` is the create/update/retire procedure; `standards/confidence.md`
and `standards/decision-references.md` are the two evidence-mechanics standards
merged so far. This document adds nothing to any of those. What it adds is the
part none of them can: what a *deployment-scoped* node must say, and where that
shape comes from.

**A note on this template's own `type`, versus a real instance's.** This document
is `type: governance` because it is a meta-document about how to author a node,
not a deployment topology itself — the same reasoning `corpus-readme` and the
sibling architecture-container template (#1327) already apply to themselves. A
real instance written *from* this template — an actual system's deployment
view — most plausibly takes `type: architecture` instead, reasoned through in
this node's own evidence ledger against `type: operations` (the value the
sibling runbook template, #1347, independently claimed for itself) and
`type: platforms` (this repository's own sense of "platforms" is client
platforms — desktop/web/mobile — not infrastructure). That reasoning lives in
the ledger rather than being re-argued here in prose a second time.

| For | Read |
|---|---|
| The front-matter contract | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| Evidence classes and citation shapes | `launchpad/docs/corpus/AGENTS.md`, `launchpad/project-intelligence/CONTRACT.md` §3 |
| Relationship types and directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| The boundary this node draws against, primary source | `launchpad-26/buzz#1529` (architecture-container template) |
| arc42, primary source | `https://arc42.org/overview`, `https://docs.arc42.org/section-7/` |
| C4 model, primary source | `https://c4model.com/`, `https://c4model.com/diagrams/deployment`, `https://c4model.com/abstractions/container` |

If this file and any of those disagree, **they win** — this one has drifted and
should be fixed.

## Purpose

A deployment node exists to answer one question for a reader who already knows a
system's containers (its architecture-container document, if one exists): ***where
does each of these actually run, in which environment, and what changes between
environments?*** It is not a second inventory of the containers themselves — it
takes that inventory as given and adds the axis container documents deliberately
omit: physical or virtual infrastructure, named environments, and the mapping
between the two. A reader should come away able to name, for each environment the
system operates in, which infrastructure each container instance runs on, what
fronts it (load balancer, ingress, DNS), and what is materially different about
that environment compared to its neighbours — without being told anything new
about what a container *is* or what is inside one.

**The failure this template exists to prevent.** Left unscoped, a deployment
document drifts in one of two directions: back into container territory (re-describing
what each container is and what technology it uses — the architecture-container
document's job, not this one's), or forward into operational-practice territory
(runbooks, on-call escalation, incident response — issue #1347's territory).
Both drifts produce a document that is not wrong so much as mis-shelved: a reader
looking for "what runs where" has to wade through "what this container is built
in" or "what to do when it pages someone" to find it. The sections below exist to
keep those two concerns out.

## The industry model this adapts

**arc42, section 7 (Deployment View)** (`https://arc42.org/overview`,
`https://docs.arc42.org/section-7/`, CC BY-SA 4.0, no version number published).
The primary source states this section covers "the technical infrastructure used
to execute your system, with infrastructure elements like geographical locations,
environments, computers, processors, channels and net topologies" together with
"the mapping of (software) building blocks to that infrastructure elements." Its
stated motivation is blunt: "software does not run without hardware," and that
underlying infrastructure "can and will influence your system and/or some
cross-cutting concepts." The source defines two levels — **Infrastructure Level
1** (distribution across locations/environments/computers, the justification for
that structure, and the mapping of software artifacts onto it) and
**Infrastructure Level 2** (the internal structure of one selected Level-1
element, for a deeper zoom where warranted) — and recommends UML deployment
diagrams or "any kind that is able to show nodes and channels of the
infrastructure."

**C4 model, Deployment diagram** (Simon Brown, `https://c4model.com/`, undated —
no version number published). The primary source groups System Context,
Container, Component and Code as "a set of hierarchical diagrams," and names
System Landscape, Dynamic and **Deployment** as "an additional set of supporting
diagrams" — a diagram type outside that zoom hierarchy entirely, not a further
level inside it. The Deployment diagram page states it "allow[s] you to
illustrate how instances of software systems and/or containers in the static
model are deployed on to the infrastructure within a given deployment
environment" (naming production, staging and development as example
environments), using two kinds of node: **deployment nodes** (physical,
virtualized, containerized, or execution-environment infrastructure, which can be
nested) and **infrastructure nodes** (supporting elements such as DNS services,
load balancers and firewalls). Its stated audience is "technical people inside
and outside of the software development team; including software architects,
developers, infrastructure architects, and operations/support staff" — a
superset of the Container diagram's audience, with infrastructure architects and
operations/support staff added.

**Both sources agree the same logical unit can be deployed differently in
different places, and that this is a distinct concern from what the unit is.**
C4's own container-abstraction page makes this explicit with a worked example: "At
development time I might have three web applications running on a single Apache
Tomcat server, while each web application may be deployed onto a dedicated Apache
Tomcat server in a live environment. In this situation, each web application is a
'C4 container', with the deployment being a separate concern." That sentence is
this template's whole reason to exist as a document distinct from the
architecture-container template.

**Both sources agree C4 is diagrams, not prose** — same observation the sibling
architecture-container template (#1327) made about the Container diagram, and it
holds identically here. This template is the surrounding write-up: it tells an
author what prose has to accompany a deployment diagram so a reader can trust it,
because a corpus node cannot be an image with no traceable claims under it.

## The boundary against architecture-container (#1327)

Issue #1327's already-open architecture-container template (PR #1529) states the
boundary this node inherits rather than re-derives: **container** is the
deployable/runnable units and their technology choice, a logical view, independent
of how many instances of it exist or where they run; **deployment** (this node) is
the physical/environment mapping — which container instances run on which
infrastructure, in which environment, and how that changes across environments.
The C4 primary source above (the Apache Tomcat example) independently confirms
this split at the source level rather than merely inheriting #1529's framing of
it: a container's identity does not change when its deployment topology does.

**The practical test a deployment document should apply:** if a fact would still
be true regardless of which environment is being described (what a container is
built in, what protocol it speaks to its neighbour), it belongs in the
architecture-container document, not here. If a fact is true in one environment
and false in another (how many replicas, whether a dependency is external or
in-cluster, which load balancer fronts it), it belongs here.

## Required sections

A deployment node MUST contain the following, in this order. ("MUST" here is this
template's own requirement for the shape of an instance node, not a restatement of
any MUST/SHOULD normative-policy framework — this document is a template, not a
standard, per the *Scope and authority* note above.)

1. **Purpose & scope statement.** One paragraph naming the system this document
   covers, stating explicitly that this is a deployment view — a physical and
   environment mapping of containers already inventoried elsewhere — and naming
   the sibling architecture-container node (if one exists) whose inventory this
   document maps. List the named environments this document covers (for example
   dev, staging, production, or a system's own names for them) up front, so a
   reader knows the document's scope before reading a single diagram.

2. **Notation legend.** What a deployment node, an infrastructure node, and a
   container-instance box mean in the diagram that follows, and how per-environment
   grouping is shown (separate diagrams per environment, or one diagram with
   per-environment subgraphs — state which this document chose and why). A reader
   who has never seen a C4 deployment diagram before should not have to already
   know the convention.

3. **The deployment diagram(s) themselves**, authored as text inside the Markdown
   body — a Mermaid fenced code block is the recommended form. **This is not
   optional and it is not an external image file.** `AGENTS.md` states that every
   non-Markdown file under the corpus root is rejected today, including one
   placed under `generated/`, because no generator exists yet to reproduce it
   from canonical Markdown (issue #1316). A deployment node with a linked PNG and
   no inline diagram does not validate today and would not survive review even if
   it did.

4. **Secrets and sensitive values.** A node built from this template **must
   never record a live secret, key, token, credential, or private
   hostname/endpoint value** — not even as a "just this once" example — per the
   repository's root `AGENTS.md` §8: "Never add a secret, key, token, or private
   hostname to a tracked file." A corpus node is a tracked file like any other;
   nothing about being a deployment document exempts it, and nothing
   automatically catches a violation (`launchpad/SECURITY-POSTURE.md`) — this
   template states the rule because compliance otherwise rests entirely on
   whoever is writing. The rule binds every table in this document and every
   citation in *Evidence expectations* below, including one that states what
   another repository's own documentation says: `launchpad/ENVIRONMENTS.md`
   applies the identical "no hostnames" rule to naming this repository's own
   environments, and the same reasoning extends to any deployment or
   infrastructure node named here. Point the reader at the *role* and the
   *reference*, never the *value* — name the managed service or node and the
   configuration key, Secret name, or Terraform/Pulumi resource that addresses
   it (for example, "the managed Postgres addressed by
   `externalPostgresql.url`", "the cluster Secret named by
   `secrets.existingSecret`", "the load balancer, its DNS name held in
   Terraform state this repository does not check in") — never the literal
   hostname, connection string, IP address, or credential itself. Where an
   example is genuinely needed, use an obviously fake placeholder and say so.

5. **Environment inventory.** One row per named environment: its name, its
   purpose (development, evaluation, staging, production, or whatever the system
   calls it), and what is materially different about it from its neighbours —
   replica counts, whether dependencies are external/managed or bundled/in-cluster,
   how secrets are provisioned (a mechanism — Kubernetes Secret, Terraform-managed,
   chart `lookup`-generated — never the secret value itself, per item 4 above),
   whether it is GitOps-managed. This is the table that keeps "which environment"
   answerable without re-reading every diagram.

6. **Deployment and infrastructure node inventory.** One row per deployment node
   (a host, VM, Kubernetes cluster or namespace, PaaS instance) and per
   infrastructure node (load balancer, ingress, DNS, firewall) shown in the
   diagram(s): its name (a logical or role name — "production ingress", not a
   literal hostname or IP address; see item 4), its kind, and a one-line
   statement of what runs on it or what it fronts.

7. **Container-to-infrastructure mapping.** For each container (named per the
   architecture-container document, if one exists) in each environment: which
   deployment node it runs on, how many instances, and what is different about
   that mapping from the same container's mapping in another environment. This is
   the table that turns "instances of containers are deployed onto
   infrastructure," which the C4 source names as the diagram's job, into prose a
   reader can verify against real deployment configuration rather than trusting
   the arrows alone.

8. **Scope and omissions**, per `AGENTS.md`'s own required shape for this
   section: what this document does not cover and who owns it (the containers'
   own identity and technology → the architecture-container template, #1327;
   what operators do when a deployment misbehaves → the runbook template, #1347;
   internal component structure of any one container → the architecture-component
   template, #1326), and — separately — anything expected to verify while
   drafting this node and unable to.

## What counts as a deployment node, an infrastructure node, and a container instance

**The container/deployment test, from the primary source:** would this fact still
be true if the system were deployed somewhere else, or with a different replica
count? If yes, it is a container-level fact and does not belong in this document.
If no — it is true in this environment specifically — it belongs here. C4's own
Apache Tomcat example is the primary-source illustration: three web applications
sharing one server in development, each on its own dedicated server in
production, are the *same three C4 containers* in both cases. What differs is
answered entirely by a deployment document, not a container one.

**Deployment node versus infrastructure node**, per the C4 Deployment diagram
source: a deployment node is *where a container instance runs* (a host, a VM, a
pod, a serverless execution environment); an infrastructure node is something
that supports the deployment without itself running application code (a load
balancer, a DNS service, a firewall). Both may be nested — the C4 source allows a
deployment node to contain other deployment nodes (for example, a Kubernetes node
containing pods).

**A worked, evidence-checked illustration from this repository** (illustrative
only — not a claim that this is Buzz's authoritative or complete deployment
topology, which is future work for whoever writes that instance node, not this
template). The container used below (`buzz-relay`) is the same container issue
#1327's template established by the same test it uses (a `[[bin]]` target and
`src/main.rs`); this node reuses that identity rather than re-arguing it, and
maps how its deployment topology genuinely differs across three environments this
repository actually defines:

| Environment | Source | How `buzz-relay` is deployed |
|---|---|---|
| **Local development** | `docker-compose.yml` | `buzz-relay` itself is **not** a service in this file — it runs as a locally built process (`just relay`, per `CLAUDE.md`) against containerized `postgres`, `redis`, `keycloak`, `minio` and `prometheus`, all on one Docker bridge network (`buzz-net`), one instance each, no load balancer, each labeled `com.buzz.env: "dev"`. |
| **Quickstart / eval** | `deploy/charts/buzz`, `quickstart=true` | `buzz-relay` runs as a Kubernetes `Deployment` (from `templates/deployment.yaml`) alongside **bundled, in-cluster** Postgres, Redis and MinIO subcharts; the chart autogenerates relay and service secrets via Helm's `lookup` function; single replica; installed directly with `helm install`, not GitOps. |
| **Production** | `deploy/charts/buzz`, default profile | The same `Deployment` template, but pointed at **external, managed** Postgres/Redis/S3 (`externalPostgresql.url`, `externalRedis.url`, `s3.endpoint`) with `secrets.existingSecret` required rather than chart-generated (chart-side secret generation is unsafe once ArgoCD/Flux render the chart with `helm template`, per the chart's own README); `replicaCount >= 2` for HA; a `RollingUpdate` strategy with `maxUnavailable: 0`; deployed via ArgoCD or Flux GitOps (`examples/argocd-app.yaml`, `examples/flux-helmrelease.yaml`). |

**One real discrepancy surfaced and deliberately left unresolved.** The `buzz`
chart's own default `image.repository` is `ghcr.io/block/buzz` — the upstream
project's own image — while this fork's `Dockerfile` and `.github/workflows/docker.yml`
build and publish a separate image to `ghcr.io/launchpad-26/buzz`. Both are real,
checkable facts; which registry actually serves which of the three environments
above was not established while drafting this node, and a real instance document
should settle it rather than assume either answer. Naming this rather than
silently picking one is exactly the kind of gap `AGENTS.md`'s step 3 asks an
author to record.

**A second deployable unit exists with its own topology.**
`deploy/charts/buzz-push-gateway` is a separate, separately versioned chart with
its own production values, `PodDisruptionBudget`, `NetworkPolicy`,
`PrometheusRule` and migration `Job` — evidence that this repository's real
deployment picture has more than one container to map, which a real instance
document (not this template) would need to inventory alongside `buzz-relay`.

## Evidence expectations

Every row in the environment inventory, the deployment/infrastructure node
inventory, and the container-to-infrastructure mapping is a claim, and needs the
same evidence-ledger treatment `AGENTS.md` requires of any corpus node —
classified honestly, not defaulted to `FACT`:

- **A deployment node's existence and what runs on it** is a `FACT` when it cites
  actual deployment configuration: a Helm chart's `templates/`, a Kubernetes
  manifest, a Terraform/Pulumi resource, a `docker-compose.yml` service, a CI/CD
  pipeline step that provisions it. Do not cite a README's prose description
  alone — configuration is what actually runs; prose drifts from it. Citing that
  configuration means naming the file, resource, or pipeline step — never
  quoting a secret, hostname, or credential value the configuration happens to
  contain; see *Secrets and sensitive values* above.
- **A difference between two environments** (replica count, external versus
  bundled dependencies, secret provisioning) is a `FACT` when it cites the
  values or manifests that actually differ between them — for example two
  values files, or one values file's conditionally rendered blocks — not a
  verbal description of the difference.
- **Infrastructure this repository does not itself define** — a managed cloud
  service, a cluster or Terraform stack that lives in a different repository —
  cannot be a `FACT` cited to a file this repository's checker can open. State
  what the *other* repository or its own documentation says as `TEAM_KNOWLEDGE`,
  attributed to that source, and say plainly that the underlying infrastructure
  itself was not independently opened. This repository's own `CLAUDE.md`
  Ecosystem table is exactly this case for Buzz: it names `squareup/block-coder-tf-stacks`
  as the repository whose Terraform and ArgoCD deploy the relay to a staging
  Kubernetes cluster, but that is a `FACT` about what `CLAUDE.md` states, not a
  `FACT` about the Terraform itself — the Terraform was not opened while writing
  this template, and a real instance document should open it before promoting
  the claim. Stating what the other repository or its own documentation says is
  itself bound by *Secrets and sensitive values* above: name that repository,
  the resource type, and the mechanism (a Terraform resource, a Helm value) —
  never a hostname, endpoint, or credential value that other documentation
  might contain, even when quoting it accurately.
- **A planned or intended deployment topology** — something a diagram shows
  because it is planned, not because it is live — is `TEAM_KNOWLEDGE` attributed
  to the issue, PR, or decision that intends it, never `FACT`.
- **Whether two running things belong to the same environment, or are genuinely
  separate environments**, is sometimes a judgement call (a preview/ephemeral
  environment that shares production infrastructure but not production data, for
  instance). Where it is a judgement call, it is an `INFERENCE` with
  `confidence`, and the reasoning must be visible per `standards/confidence.md`'s
  Requirement 4 — not asserted as settled fact.

**This template does not restate the FACT/INFERENCE/TEAM_KNOWLEDGE contract
itself, `confidence`'s meaning, or the citation shapes.** `AGENTS.md` and
`standards/confidence.md` own those, and a second copy here would be exactly the
drift-prone duplication `AGENTS.md` warns against.

**None of the citation forms above license recording a secret, key, token, or
private hostname/endpoint value.** *Secrets and sensitive values* (required
section 4) binds every citation in this document, including one made solely to
satisfy an evidence requirement — a `FACT` citation to real configuration, or a
`TEAM_KNOWLEDGE` citation to another repository's documentation, is still
naming the reference, never quoting the value.

## Relationships an instance node should consider

This template's own front matter declares none (see *Scope and omissions*
below), but an instance node written from this template usually has real edges
to declare once its siblings exist:

- **`depends-on`**, authored by the deployment document, targeting the
  architecture-container node whose containers it maps. This is the correct
  direction and the correct type: the deployment document's own claims (which
  container instances run where) stop holding the moment the container
  inventory changes — a container renamed, added, or removed — which is exactly
  `depends-on`'s stated directionality ("source requires target to be true/current
  for source's own claims to hold"). The container document does not declare the
  reverse edge; `depended-on-by` is `depends-on`'s generated inverse, produced by
  tooling, not hand-authored.
- **`implements`**, targeting a future per-type diagram standard (#1312) once it
  merges, the same candidate edge the architecture-container template names for
  itself — `relationships.schema.json` describes exactly this directionality
  ("source is the concrete realization of target, e.g. a template instance of a
  standard") for a template pointing at its governing standard. #1312 is unmerged
  today and this relationship would not resolve in CI.

**Whether a deployment document should also declare `part-of` targeting an
architecture-context node was considered and deliberately left open.** The
architecture-container template declares `part-of` targeting context, because a
container view is a zoomed-in constituent part of the same system the context
node describes. A deployment view is not a further zoom in that same hierarchy —
the C4 source places Deployment outside the hierarchical (context → container →
component → code) diagram set entirely, as a supporting diagram — so whether
`part-of`'s "constituent section/child of" directionality is the right
description for a deployment view's relationship to a context view, versus no
relationship at all, is a genuine open question this node does not resolve. A
future author with a real instance of both documents in hand is better placed to
answer it than this template is in the abstract.

None of these can be declared by *this* template document itself — a template is
not an instance of the system it describes, and declaring `depends-on` or
`implements` here would target a node that does not exist for a system that is
never named.

## Boundary against sibling templates

| This template (deployment) | Its neighbors |
|---|---|
| **Logical/technology view it maps:** architecture-container (#1327) | Names what each container is and what technology it uses. This template does not repeat that — it names the container document and adds only where each container instance runs, in which environment. |
| **What happens when it breaks:** runbook (#1347) | Operational response to an incident or alert. This template stops at "what runs where" — it does not describe on-call procedure, alert thresholds, or debugging steps. |
| **One container's internals:** architecture-component (#1326) | Internal module/class structure of a single container. Out of scope here regardless of environment. |

## Scope and omissions

**This node covers** the purpose of a deployment document, its required
sections, its evidence expectations, and the industry model (arc42 section 7,
the C4 Deployment diagram) it adapts.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| A container's identity and technology choice | #1327 (architecture-container template) |
| One container's internal building blocks | #1326 (architecture-component template) |
| Operational response once something is deployed — on-call, alerts, incident procedure | #1347 (runbook template) |
| The evidence-class contract itself (FACT/INFERENCE/TEAM_KNOWLEDGE, citation shapes) | `launchpad/docs/corpus/AGENTS.md` |
| The `confidence` field's meaning and requirements | `launchpad/docs/corpus/standards/confidence.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |
| A per-type diagram standard (notation conventions across all corpus diagrams, not just this one) | #1312, `task/1312-corpus-standard-diagrams`, unmerged at the recorded revision |

**No `relationships` in this node's front matter.** At the recorded revision,
`origin/launchpad`'s corpus tree carries four validated content nodes —
`corpus-agents`, `corpus-readme`, `corpus-standard-confidence`,
`corpus-standard-decision-references` — and none of the four has deployment,
infrastructure, environments, arc42 or C4 as its subject. An edge to any of them
would be a citation duplicate of what this node's evidence ledger already cites
directly by path, not a substantive typed relationship. This was checked against
the actual tree (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`),
not assumed from "the corpus is new." The most likely first genuine edges for
this node are `depends-on` targeting a merged architecture-container instance and
`implements` targeting a future per-type diagram standard (#1312), both named
above and neither available today.

**No edge to the sibling batch-2 templates (#1331, #1340, #1346, #1351) or to
the sibling architecture templates authored in the same corpus-templates effort
(#1326, #1328, #1347).** All are being authored in parallel by independent
agents, and none is guaranteed merged when review starts on the others —
declaring an edge to any of them today would validate inside this node's own
worktree but be a hard error against `origin/launchpad`.

**Expected but not verified when this node was written:**

- **No instance of this template has been written yet.** Whether the seven
  required sections above are sufficient, or whether a real system's deployment
  topology surfaces a concern this template does not anticipate (multi-region
  deployment, canary/blue-green rollout, a deployment node this template's
  two-kind vocabulary does not cleanly describe), is untested. The first real
  deployment node is the test.
- **Whether the `ghcr.io/block/buzz` versus `ghcr.io/launchpad-26/buzz` registry
  discrepancy noted above reflects an intentional fork decision or untouched
  upstream chart defaults was not established.** It is named as a real gap, not
  resolved.
- **`squareup/block-coder-tf-stacks`'s actual Terraform and ArgoCD configuration
  was not opened.** Only `CLAUDE.md`'s own description of that repository's role
  was read; the repository itself is not imported here, and this node's ledger
  is explicit that this is a `FACT` about `CLAUDE.md`'s prose, not about the
  Terraform.
- **Whether Mermaid is the only workable in-Markdown diagram notation for a
  deployment view, specifically for nested deployment nodes, was not surveyed.**
  It is recommended above for the same reasons the architecture-container
  template gives (renders on GitHub without a generator, is plain text a diff
  can show meaningfully); no alternative was evaluated against those two
  properties for this document's specific nesting needs.
- **The worked `buzz-relay` illustration was checked only for the three
  environments named above**, using only the files cited, and is explicitly not
  offered as Buzz's own complete or authoritative deployment topology.
- **Cross-model review was not run.** Issue #1467 records that the cross-model
  review provider (Codex) is currently unavailable; a same-model final pass was
  substituted, per the corpus-templates batch dispatch brief.
