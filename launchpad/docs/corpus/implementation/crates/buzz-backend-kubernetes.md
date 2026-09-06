---
id: implementation-crates-buzz-backend-kubernetes
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
relationships:
  - type: references
    target: architecture-deployment-kubernetes
  - type: references
    target: architecture-containers-agent-runtime
evidence:
  - statement: "This node was authored and checked against repository revision 1ed55e980b0043f92d9c652e6a39a8e49345389c on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 1ed55e980b0043f92d9c652e6a39a8e49345389c"
  - statement: "buzz-backend-kubernetes is a Rust binary crate at crates/buzz-backend-kubernetes, described in its own manifest as 'Kubernetes backend provider for Buzz remote agents (docs/remote-agents.md)'. Its source tree is 14 modules under src/ (classify, client, cluster, config, env, gc, image, intent, main, naming, observe, pod, reconcile, wire) totalling roughly 6,400 lines, plus one integration-test file (tests/wire_fixtures.rs) and a golden-fixture directory (tests/fixtures/provider-wire/)."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/Cargo.toml"
      - "crates/buzz-backend-kubernetes/src/main.rs"
  - statement: "main.rs's own module-level doc comment states the process contract: one process per operation, read exactly one JSON request from stdin, write exactly one JSON response to stdout, exit 0 for a response that was produced and 1 only for a failure to read a request at all -- outcomes are carried in the response's own `ok` field, never in the exit code, so there is exactly one error channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/main.rs:1-58"
  - statement: "wire.rs defines the stdin/stdout JSON protocol at PROTOCOL_VERSION 1: a tagged `Request` enum (`Info`, `Deploy`), an `AgentPayload` struct that types only the fields this binding actually consumes (deliberately omitting `name`, `model`, `provider`, `turn_timeout_seconds`), a `LaunchBlock` carrying the desktop-resolved three-tier launch data, and an untagged, flat-serializing `Response` enum (`Info`/`Deploy`/`Error`) because the desktop reads `ok`, `error`, and `agent_id` off the top level rather than through a variant tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/wire.rs:1-148"
  - statement: "main.rs's `refuse_relay_mesh` reads the raw, untyped wire JSON (not the parsed `AgentPayload`, which deliberately carries no `provider` field) and refuses a deploy whose trimmed `agent.provider` equals `relay-mesh` before any typed parsing, cluster contact, or Secret creation occurs; its own doc comment names this the spec's backstop, since the desktop already refuses the same case first (`agents_deploy.rs:116`) and this is the layer that owes the obligation independently."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/main.rs:28-32"
      - "crates/buzz-backend-kubernetes/src/main.rs:97-113"
  - statement: "One successful deploy call runs, in order: config::parse (provider_config -> ProviderConfig), naming::AgentIdentity::from_nsec (pubkey derived from the payload's private_key_nsec before any cluster read or mutation), env::build_env (three-tier environment resolution), client::connect (kubeconfig-based cluster client), cluster::Cluster::new, and reconcile::deploy (the state-machine loop) -- exactly the order deploy_agent in main.rs codes."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/main.rs:116-135"
  - statement: "config.rs parses exactly nine provider_config v1 fields (context, namespace, image, cpu_request, memory_request, cpu_limit, memory_limit, inactivity_seconds, service_account), pinned by its own test asserting the schema declares exactly those nine keys; there is no credential field in either the parsed struct or the schema, and a dedicated test asserts a caller-supplied token/client_key has no effect on the parsed ProviderConfig's Debug output."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/config.rs:64-176"
      - "crates/buzz-backend-kubernetes/src/config.rs:362-470"
  - statement: "Resource defaults are 1 CPU / 2Gi request scaling to 2 CPU / 4Gi limit, all four independently configurable; the default inactivity budget is 7200 seconds; and `inactivity_seconds: 0` (the spec's blessed indefinite-lifetime opt-in) is explicitly refused in this version with an error naming the reason -- it would require restartPolicy OnFailure, which config.rs's own comment and the RESTART_POLICY constant's doc comment both state is double-gated on a harness exit-code contract and a crash-loop classification row that do not yet exist, so silently downgrading to Never (which would kill an indefinite agent on its first crash) is refused rather than attempted."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/config.rs:11-63"
      - "crates/buzz-backend-kubernetes/src/config.rs:148-166"
  - statement: "image.rs requires every provider_config.image value to be digest-pinned (name@sha256:<64 lowercase hex>); a tag-only reference (including a traceable sha-<gitsha> tag) is rejected with an error naming the field, and a tag-plus-digest reference normalizes by dropping the tag so two spellings of identical bytes produce one canonical ImageRef and one create-intent fingerprint. A registry port (host:5000/name) is correctly distinguished from a tag by only treating a final colon segment as a tag when it contains no '/'."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/image.rs:1-93"
  - statement: "naming.rs derives an AgentIdentity exclusively from the payload's private_key_nsec via nostr::SecretKey::from_bech32 -- there is no code path that accepts a caller-supplied pubkey to reach a selector. The pod name is deterministic (buzz-agent-<first 12 hex chars>), the label-selector pubkey is truncated to the first 32 of 64 hex characters (Kubernetes label values cap at 63), and every object this provider creates carries three labels: the truncated pubkey, app.kubernetes.io/managed-by=buzz-backend-kubernetes, and a binding-version label -- collectively the 'management marker' the rest of the crate treats as the fence between provider-owned objects and everything else in a shared namespace."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/naming.rs:1-123"
  - statement: "Because a 32-hex label is collision-resistant but not collision-free, every read path re-checks a second, full 64-hex pubkey carried as an annotation (buzz.block.xyz/agent-pubkey-full) rather than trusting the label alone; observe.rs's `verify` function is the single gate through which a pod or Secret must pass this full-annotation-plus-marker check before classify.rs, gc.rs, or the returned agent_id can act on it at all -- an object that merely matches the label selector but fails this check is never deleted, never GC'd, and never adopted."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/observe.rs:38-67"
      - "crates/buzz-backend-kubernetes/src/observe.rs:248-260"
      - "crates/buzz-backend-kubernetes/src/naming.rs:22-35"
  - statement: "intent.rs computes a create-intent Fingerprint as a hex SHA-256 digest over a canonical serde_json serialization of IntentTemplate, a type constructed so it structurally cannot hold Secret data or the per-attempt generation token: env values are excluded (only sorted env *keys* are hashed), and the per-attempt Secret name in the envFrom position is replaced by a fixed SECRET_PLACEHOLDER constant, so two attempts of identical configuration always fingerprint identically regardless of which generation created them. A dedicated test enumerates every scheduling-relevant field and asserts each one changes the digest, and another asserts the serialized bytes contain no nsec/URL/generation-shaped string."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/intent.rs:1-135"
      - "crates/buzz-backend-kubernetes/src/intent.rs:275-300"
  - statement: "classify.rs is a pure function (no I/O) mapping an Option<VerifiedPod> plus a desired Fingerprint to one of six Actions (Create, Delete, AwaitDisappearance, NoOp, Observe, Report). Its own module doc states two invariants enforced structurally rather than by convention: every Action::Delete carries the Fence (UID + resourceVersion) from the exact observation that authorized it, so there is no code path that re-reads and substitutes a fresher fence; and the PullFailure reason type is absent from Action::Delete's own definition, so a pull-failure reason string can never become deletion authority, which the compiler enforces rather than a runtime check."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/classify.rs:1-101"
  - statement: "classify() checks a pod's deletion-marked flag before its startup state, with a comment explaining why the ordering is load-bearing: Kubernetes has no distinct 'Terminating' phase, so a pod undergoing graceful deletion reports phase Running for the whole of its grace period, and checking startup first would misclassify a dying pod as the live no-op row and hand back a pod name that evaporates."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/classify.rs:108-123"
  - statement: "For a never-started-but-recoverable pod, classify() only ever replaces it when the recorded create-intent annotation diverges from the freshly computed fingerprint; identical intent always yields Action::Observe regardless of how long the pod has been pending, with a test (repeated_identical_starts_never_delete) exercising the same identical-intent classification 100 times and asserting none of them is a Delete. Pod age is not an input to classify() at all -- the module's own comment states any finite age threshold would collide with Cluster Autoscaler's own pod-age delays, and a delete-recreate cycle resets exactly the age signal it would key on."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/classify.rs:155-172"
      - "crates/buzz-backend-kubernetes/src/classify.rs:280-305"
  - statement: "cluster.rs is the real Substrate implementation over kube-rs, and its own module doc names three normative mappings: a 409 response is discriminated on the apiserver's Status.reason string, never on the HTTP code alone -- a create 409 with reason AlreadyExists (a lost create race) and a delete 409 with reason Conflict (a failed compare-and-delete precondition) are structurally different outcomes that the code keeps apart by a dedicated const-based reason_is() check, with a test named the_two_409s_are_never_conflated asserting the discrimination directly; reads that must be most-recent (list_pods, secret_exists, get_pod) leave resourceVersion unset for a quorum read rather than passing \"0\" (a possibly-stale cache read); and delete_pod never sets grace_period_seconds, so the pod's own declared 60-second termination grace period applies rather than a force-kill."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/cluster.rs:1-38"
      - "crates/buzz-backend-kubernetes/src/cluster.rs:200-232"
      - "crates/buzz-backend-kubernetes/src/cluster.rs:358-427"
  - statement: "cluster.rs's list_with_date function deliberately bypasses kube-rs's typed Api::list (which returns only the decoded body) and instead builds the raw request and calls Client::send directly, so the apiserver's own HTTP Date response header is reachable; this is the only clock the orphan-Secret age gate in gc.rs is permitted to use, because a desktop-local clock running fast would deterministically compute every in-flight Secret as expired on every pass."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/cluster.rs:79-133"
  - statement: "gc.rs's plan() function is pure (identity, observed pods/secrets, a terminated predicate, and an optional apiserver clock in; a GcPlan of pod/secret names out) and runs as a preflight pass on every deploy. Terminated, verified, marker-bearing pods are collected together with their referenced Secret. An unreferenced Secret is only orphan-collected once it is older than ORPHAN_SECRET_MIN_AGE_SECS, defined as exactly twice the 600-second operation deadline (1200s); the module doc explains this age bound exists because Secret-create and pod-create are not atomic against an independent concurrent GC pass, so any attempt that could still reference an unreferenced Secret has, past that bound, necessarily exceeded its own operation deadline."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/gc.rs:1-115"
  - statement: "The orphan-Secret sweep in gc.rs's plan() is skipped in its entirety whenever the passed-in apiserver clock is None (header absent or unparseable) -- terminated-pod GC, which does not consult the clock, still runs. A dedicated test (without_a_server_clock_the_orphan_sweep_is_skipped) constructs a Secret with a 10,000,000-second recorded age and asserts it is not collected when no clock is supplied, with a comment stating a fast local clock would otherwise delete every in-flight Secret on every pass."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/gc.rs:41-56"
      - "crates/buzz-backend-kubernetes/src/gc.rs:307-320"
  - statement: "reconcile.rs's deploy() function drives classify::classify() in a loop against a Substrate trait (implemented by the real Cluster in production and by an in-process Fake driving the same shipped deploy() in tests) until the harness container reports state.running or a 600-second operation deadline elapses; its own module doc states success has exactly one meaning -- the harness container started -- with no 'deployed but not confirmed' outcome, and the wire protocol has no third response form to carry one."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/reconcile.rs:1-19"
      - "crates/buzz-backend-kubernetes/src/reconcile.rs:351-488"
  - statement: "reconcile.rs's deploy() tracks a created_this_call boolean that is set only once this specific call's own Create action lands, and a subsequent Delete classification is treated differently depending on it: before this call has created anything, a Delete is executed normally (fenced delete, await disappearance, re-enter); once this call has already created its own attempt, the same Delete classification is instead reported in-band as a startup failure and NOT retried within the call, with a comment stating the unbounded retry was measured live producing 107 immutable Secrets in a single 600-second call, all younger than the orphan sweep's 1200-second age gate, before this bound was added."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/reconcile.rs:363-373"
      - "crates/buzz-backend-kubernetes/src/reconcile.rs:406-428"
  - statement: "adopt_winner() in reconcile.rs is the code path taken when this call's own pod create returns CreateOutcome::AlreadyExists (a lost create race): it verifies the winning pod is actually managed by this provider for this identity (erroring out, not repairing, if not), drops its own now-superfluous Secret once nothing references it, and then only ever *observes* the winner until it starts or reports its terminal condition -- the function has no delete edge for the winning pod at all, matching the module doc's statement that a create-conflict loser never repairs the pod it lost to; that is left to a subsequent deploy call's own normal classification."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/reconcile.rs:278-349"
  - statement: "env.rs resolves the pod's environment in three explicit, ordered tiers before serialization -- tier 1 policy_env (overridable behavior defaults), tier 2 the desktop-merged user/launch env (agent.env_vars is read only as a fallback when agent.launch is absent, and is deliberately NOT re-merged on top of launch.env when launch is present, since the descriptor already merged global<persona<agent), and tier 3 an authoritative set of Buzz-identity/harness-control keys that is cleared key-by-key before being conditionally rewritten, so an authoritative key with no value for a given deploy is removed rather than left holding a lower tier's value."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/env.rs:1-42"
      - "crates/buzz-backend-kubernetes/src/env.rs:161-230"
  - statement: "env.rs validates every lower-tier env key as a POSIX shell identifier ([A-Za-z_][A-Za-z0-9_]*) and refuses the deploy outright if any key fails, with a comment citing that Kubernetes' own kubelet behavior for a non-POSIX Secret key (which Kubernetes itself validates more loosely, as IsConfigMapKey) changed between versions -- filtered with a warning event through v1.29, injected verbatim from v1.30 per KEP-4369 -- so the identical manifest would behave differently across clusters, and this provider fails closed on its own side rather than depend on the target cluster's kubelet version."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/env.rs:55-73"
      - "crates/buzz-backend-kubernetes/src/env.rs:195-209"
  - statement: "env.rs refuses to set BUZZ_ACP_NO_PRESENCE (a forbidden key, not merely an authoritative one), with the comment stating relay presence is the only remote liveness signal and there is no authoritative value to overwrite a suppression with, unlike a same-named collision on any other reserved key, which is silently overwritten by the authoritative tier rather than refused."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/env.rs:44-47"
      - "crates/buzz-backend-kubernetes/src/env.rs:203-209"
  - statement: "env.rs enforces Kubernetes' own Secret data size cap (1 MiB, MAX_SECRET_BYTES = 1024*1024) by summing resolved env value lengths and returning a named provider error before the Secret is built, rather than letting an oversized Secret fail at the apiserver partway through a deploy."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/env.rs:49-53"
      - "crates/buzz-backend-kubernetes/src/env.rs:288-294"
  - statement: "env.rs's respond_to gate validation (validate_respond_to_gate) checks against exactly the four modes buzz-acp's own CLI parser accepts (owner-only, allowlist, anyone, nobody) rather than the desktop's narrower three-mode UI surface, with a comment stating the desktop deliberately rejects 'nobody' in its own UI but the harness itself accepts it, so inheriting the desktop's narrowing here would refuse a launch that would otherwise work for a non-desktop caller; validation of the allowlist itself (64-hex entries) fires only in allowlist mode, mirroring buzz-acp's own asymmetric rule rather than validating it unconditionally."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/env.rs:85-149"
  - statement: "pod.rs's build_pod hardens every created pod identically: automount_service_account_token is false (the agent runs prompted, untrusted-code-adjacent work while holding an nsec, so an ambient ServiceAccount token is a credential it never needs), the container runs as a fixed non-root UID/GID (10001/10001) with all Linux capabilities dropped and allowPrivilegeEscalation false, seccompProfile is RuntimeDefault, and the container spec sets no command/args override, so the image's own entrypoint execs the harness as PID 1 and receives termination signals directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/pod.rs:1-183"
      - "crates/buzz-backend-kubernetes/src/pod.rs:232-250"
  - statement: "pod.rs's build_secret marks the per-attempt Secret immutable: true, written once per generation and never updated; its own doc comment states this is what lets the pod's envFrom reference be treated as an atomic binding to that exact payload, and the Secret's name (identity.secret_name(generation)) changes on every create attempt so no two attempts ever share or overwrite one Secret."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/pod.rs:29-59"
  - statement: "client.rs resolves the apiserver client from standard kubeconfig resolution (KUBECONFIG then ~/.kube/config) and carries no credential field of its own in provider_config -- its module doc names this I2 ('no config path for cluster credentials exists'). It also prepends two fixed plugin directories (/opt/homebrew/bin, /usr/local/bin) plus ~/.local/bin to the process PATH before building the client, with a comment explaining Block's kubeconfigs near-universally authenticate through exec credential plugins (aws eks get-token, gke-gcloud-auth-plugin) resolved via PATH, and this provider inherits a Finder-launched desktop's minimal PATH, which contains none of the directories those plugins install to."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/client.rs:1-123"
  - statement: "The tests/fixtures/provider-wire/ directory's own README states its fixtures are 'recorded, not invented' -- executed and transcribed from the desktop's real build_launch_block -> deploy_payload_json code path -- and recounts that an earlier, derived (not recorded) version of one fixture silently carried four impossible values at once (a respond_to shaped as a raw pubkey instead of the desktop's kebab-case enum, allowlist/owner values failing the desktop's own 64-hex validation, an invented env-var name where the real emitter uses a different one, and a launch.env key from no real resolution layer), which is why the file states the desktop's own whole-object equality test is what actually polices fixture correctness, not this provider, which is deliberately indifferent to several of those same fields (respond_to, allowlist, policy_env are typed as opaque strings/maps)."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/tests/fixtures/provider-wire/README.md"
  - statement: "tests/wire_fixtures.rs drives the actually-built binary (env!(\"CARGO_BIN_EXE_buzz-backend-kubernetes\")) over a real OS pipe with KUBECONFIG pointed at a nonexistent path (so any fixture that accidentally reaches a real cluster fails loudly rather than depending on the developer's ambient kubeconfig), and asserts response fixtures byte-for-byte after key-sorted re-serialization, a full desktop-shaped payload is accepted up to the point of a named connection failure, and a nine-case respond_to acceptance matrix distinguishes 'refused before reaching the cluster' from 'reached the cluster' by inspecting the returned error string for the word 'kubeconfig'."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/tests/wire_fixtures.rs:1-222"
  - statement: "Counting `#[test]` occurrences directly in each of the 14 src/*.rs files plus tests/wire_fixtures.rs yields 155 unit/property tests across the library modules (classify 12, client 4, cluster 4, config 14, env 27, gc 11, image 8, intent 7, main 5, naming 7, observe 12, pod 13, reconcile 24, wire 7) plus 4 integration tests in wire_fixtures.rs, for 159 automated tests total in this crate at the recorded revision."
    entry_class: FACT
    evidence:
      - "grep(pattern='#\\[test\\]', path='crates/buzz-backend-kubernetes/src/*.rs;crates/buzz-backend-kubernetes/tests/wire_fixtures.rs') -> per-file counts summing to 159, at commit 1ed55e980b0043f92d9c652e6a39a8e49345389c"
  - statement: "Justfile's ci unit-test recipe enumerates `cargo nextest run -p buzz-backend-kubernetes` explicitly, with a comment stating the crate's decision layers (state machine, GC planner, env precedence, naming, wire) are pure functions with a fake substrate and therefore belong in the unit job, and that this line exists because nothing in CI runs `cargo test --workspace` -- workspace membership alone buys clippy/check, not a single executed test."
    entry_class: FACT
    evidence:
      - "Justfile:348-352"
  - statement: "docs/remote-agents.md is a ~1,780-line, section-numbered formal specification ('Remote Agents and Their Management: A Formal Specification'), with a dedicated top-level section '## The Kubernetes Binding (buzz-backend-kubernetes)' (lines 991-1410) covering cluster auth, namespace, image, entrypoint/launch ABI, pod shape, Secrets, and garbage collection, plus a '[L3] Kubernetes binding conformance -- this binding' subsection (line 1493) mapping each L2 protocol-conformance item onto this crate's own mechanisms by name (full-pubkey annotation, state.running, resourceVersion-unset reads, UID+resourceVersion delete preconditions, Status.reason as the 409 discriminator, and the managed-by/binding-version labels)."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1"
      - "docs/remote-agents.md:991-1410"
      - "docs/remote-agents.md:1493-1515"
  - statement: "docs/remote-agents.md's 'Implementation Correspondence' table (lines 1687-1708) still lists the row 'Kubernetes binding | *to be added*: crates/buzz-backend-kubernetes' and the row 'Sprig image | *to be added*: Dockerfile.sprig + workflow' as not-yet-built, even though at the recorded revision crates/buzz-backend-kubernetes exists as a 14-module, ~6,400-line crate, Dockerfile.sprig exists as a 44-line multi-stage image build, and .github/workflows/sprig.yml and .github/workflows/sprig-image.yml both exist as dedicated release workflows -- confirmed by direct file checks (`test -f Dockerfile.sprig`, `.github/workflows/sprig-image.yml`, `.github/workflows/sprig.yml`, all present) rather than assumed from the crate's own existence alone."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md:1706-1707"
      - "Dockerfile.sprig"
      - ".github/workflows/sprig-image.yml"
      - ".github/workflows/sprig.yml"
  - statement: "This staleness is explained by git history, not merely by content comparison: docs/remote-agents.md was authored in PR #3748 (commit 28ae6cd21, the commit the spec's own 'Known Defects' section is explicitly pinned against), and crates/buzz-backend-kubernetes plus the desktop deploy path were added afterward in PR #4289 (commit 6530b58a6, 'feat(k8s): Kubernetes backend plugin + desktop deploy path') -- the spec predates the crate it is now stale about by one full feature PR, and nothing in the intervening history (checked via `git log --oneline -- crates/buzz-backend-kubernetes docs/remote-agents.md`) updated the correspondence table's two rows to reflect that."
    entry_class: FACT
    evidence:
      - "git_log_oneline(paths='crates/buzz-backend-kubernetes;docs/remote-agents.md') -> 6 commits from 28ae6cd21 (spec merge) through 50a71137e (HEAD-of-history at this revision), with 6530b58a6 ('feat(k8s): Kubernetes backend plugin + desktop deploy path') adding the crate; none of the later commits touch the correspondence table's two stale rows"
  - statement: "Dockerfile.sprig's builder stage compiles only the `sprig` binary (`cargo build --locked --profile sprig -p sprig`), and its runtime stage symlinks that one binary under the names buzz-acp, buzz-agent, buzz-dev-mcp, rg, tree, buzz, git-credential-nostr, and git-sign-nostr -- buzz-backend-kubernetes is not among them, confirming architecture-containers-agent-runtime.md's own account that sprig's only crate dependencies are buzz-acp/buzz-agent/buzz-dev-mcp: this provider crate runs desktop-side to deploy pods running that image, and is never itself packaged into the image it deploys."
    entry_class: FACT
    evidence:
      - "Dockerfile.sprig:19"
      - "Dockerfile.sprig:34-38"
  - statement: "architecture-deployment-kubernetes.md (a merged corpus node documenting the relay's own Helm chart) states explicitly, in its own evidence ledger and Scope and omissions table, that buzz-backend-kubernetes is 'a separate crate ... a distinct compute-provisioning concern from the relay's own deployment topology' and 'belongs in its own node' -- naming this crate as deliberately out of that node's scope rather than silently omitting it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/kubernetes.md"
  - statement: "architecture-containers-agent-runtime.md (a merged corpus node) independently names buzz-backend-kubernetes as 'a backend provider ... which the Desktop hands the agent's private key to and which realizes the container as a bare Kubernetes Pod running the sprig image,' and cites docs/remote-agents.md as the formal specification governing remote deployment -- corroborating, from the agent-runtime side, this node's own reading of the crate's role."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "No envtest/kind (real-apiserver) conformance test suite for this crate was found in the repository: a grep for 'envtest' and 'kind suite' across crates/buzz-backend-kubernetes/ matches only prose (the fixtures README and two src-file doc comments describing such a suite as feasible future work), and no CI workflow or Justfile recipe references envtest or a kind cluster for this crate -- so the L3 conformance case families docs/remote-agents.md describes as testable via 'an envtest/kind suite' are, at the recorded revision, exercised only by this crate's own fake-Substrate unit tests over the shipped reconcile::deploy function, not against a real Kubernetes apiserver."
    entry_class: FACT
    evidence:
      - "grep(pattern='envtest|kind suite', path='crates/buzz-backend-kubernetes/**') -> 3 matches, all prose in doc comments/README, no test harness"
      - "docs/remote-agents.md:1516-1527"
  - statement: "Because the private squareup/block-coder-tf-stacks and sprout-backend-blox repositories are not present in this checkout, it is a reasonable but unverified inference that this crate is the compute provider Block's own internal deployment actually wires up for Kubernetes-hosted remote agents, rather than one of possibly several alternative provider binaries -- the repository's own AGENTS.md documents sprout-backend-blox as 'Desktop backend provider script connecting Blox workstation agents to the relay,' a name suggesting a second, non-Kubernetes provider exists for Block's own Blox compute, but that script's actual protocol conformance was not inspected here."
    entry_class: INFERENCE
    evidence:
      - "AGENTS.md"
      - "crates/buzz-backend-kubernetes/Cargo.toml"
    confidence: 0.5
---

# `buzz-backend-kubernetes`: implementation reference

`crates/buzz-backend-kubernetes` (binary `buzz-backend-kubernetes`) is a Kubernetes
compute-provider plugin for Buzz's remote-agent system. It runs desktop-side, invoked
as a short-lived subprocess per operation, and realizes `docs/remote-agents.md`'s
formal specification for the `deploy` operation of a remote-agent provider: given an
agent's Nostr identity and relay connection details, it deploys that agent as a
Kubernetes Pod running the published `sprig` agent-runtime image, converging
idempotently to exactly one live instance per agent identity per namespace.

## Target

There is no separate corpus node yet for the specification this crate realizes, so no
`implements` edge is declared here — inventing one to a nonexistent id is a hard
validation error, and `architecture-deployment-kubernetes.md`/`architecture-containers-agent-runtime.md`
already set the precedent of naming a target in prose and omitting the edge until the
target itself has a corpus id.

The target, concretely, is `docs/remote-agents.md` — a ~1,780-line, section-numbered
formal specification titled "Remote Agents and Their Management." Two of its sections
name this crate directly:

- **"The Kubernetes Binding (`buzz-backend-kubernetes`)"** (`docs/remote-agents.md:991-1410`)
  — cluster auth, namespace handling, image requirements, the pod's entrypoint/launch
  ABI, pod shape/hardening, Secrets handling, and garbage collection.
- **"[L3] Kubernetes binding conformance — this binding"** (`docs/remote-agents.md:1493-1580`)
  — maps the protocol-level (`L2`) conformance items onto this crate's own concrete
  mechanisms, and enumerates the specific failure-mode test families a conformance
  suite for this binding is expected to cover.

The rest of the specification (the shared `Provider Protocol`, `Deploy State Machine`,
`Auto-Stop`, and `[L1]`/`[L2]` conformance sections) governs any remote-agent provider,
not only this one; this crate's own `wire.rs`, `classify.rs`, and `reconcile.rs` realize
those shared sections as well as the Kubernetes-specific ones, and this node treats the
whole document as the target rather than only its Kubernetes-titled subsections.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `src/main.rs` (`main`, `respond`, `deploy_agent`, `refuse_relay_mesh`) | §Provider Protocol's process contract (one JSON request in, one JSON response out, exit 0/1) and the relay-mesh deployability refusal | The relay-mesh check reads the raw wire value, not the typed `AgentPayload`, which carries no `provider` field by design |
| `src/wire.rs` (`Request`, `AgentPayload`, `LaunchBlock`, `Response`) | §Provider Protocol's `info`/`deploy` wire schema, `PROTOCOL_VERSION = 1` | Only fields this binding consumes are typed; unconsumed desktop fields (`model`, `provider`, `system_prompt`, …) are accepted and ignored, not rejected |
| `src/config.rs` (`parse`, `config_schema`, `Resources`) | §`provider_config` v1 fields (9 fields), §Image's schema-prefill contract | `inactivity_seconds: 0` is refused pending the harness exit-code contract (see *Divergences* — no divergence found, this is spec-compliant gating) |
| `src/image.rs` (`parse`, `ImageRef`) | §Image's digest-pinning requirement | Normalizes `name:tag@sha256:…` to tagless canonical form so fingerprinting is stable across equivalent spellings |
| `src/naming.rs` (`AgentIdentity`, labels/selector/annotation constants) | §Pod shape's object-naming and management-marker contract | Pubkey derived only from `private_key_nsec`; 32-hex label + 64-hex annotation double-check for collision resistance |
| `src/intent.rs` (`IntentTemplate`, `Fingerprint`) | §Deploy State Machine's create-intent fingerprint | Structurally excludes Secret values and the per-attempt generation from the hashed bytes |
| `src/classify.rs` (`classify`, `Action`, `Startup`) | §Deploy State Machine's ordered classification table | Pure function; `PullFailure` is compiler-excluded from `Action::Delete`'s own type |
| `src/observe.rs` (`decode_startup`, `verify`, `condition`, `pull_failure_message`) | §Deploy State Machine step 1 (verified observation) and the redaction rule for reported conditions | `verify` is the one gate through which an object must pass before classification, deletion, or GC can touch it |
| `src/cluster.rs` (`Cluster`, the `Substrate` impl) | §Cluster auth's I/O layer; the 409-discrimination, quorum-read, and grace-period normative mappings §K8s GC and §Deploy State Machine both depend on | Bypasses `Api::list` for `list_pods`/`list_secrets` specifically to read the apiserver's own `Date` header |
| `src/gc.rs` (`plan`, `GcPlan`) | §K8s GC's preflight garbage-collection contract | Orphan-Secret sweep is age-gated at 2× the 600s deadline and skipped entirely without a trustworthy apiserver clock |
| `src/reconcile.rs` (`deploy`, `Substrate` trait, `adopt_winner`, `await_disappearance`) | §Deploy State Machine's full state-machine loop, the 600s operation deadline | `created_this_call` bounds the delete/recreate cycle to one residue-producing attempt per call (measured live at 107 Secrets/600s before this bound existed) |
| `src/env.rs` (`build_env`, `AUTHORITATIVE_KEYS`, `validate_respond_to_gate`) | §Launch data's three-tier env precedence, the reserved-key rule, the harness's respond-to acceptance surface | Authoritative tier clears its owned keys before conditionally rewriting them, so absence-means-absence propagates from the local-spawn path |
| `src/pod.rs` (`build_pod`, `build_secret`, `intent_template`) | §Pod shape's hardening defaults, §K8s Secrets' immutable-per-attempt Secret contract | No `command`/`args` override — the image's own entrypoint execs the harness as PID 1 |
| `src/client.rs` (`connect`, `prepend_plugin_path`, `explain`) | §Cluster auth's ambient-kubeconfig-only contract (I2) | PATH-prepends credential-plugin directories to work around a Finder-launched desktop's minimal inherited PATH |
| `tests/fixtures/provider-wire/*` + `tests/wire_fixtures.rs` | §Provider Protocol's wire contract, shared with the desktop's own request-construction code | Fixtures are recorded from the desktop's real code path, not derived by reading it — the fixtures README documents a past failure of the derived approach |

## Divergences

- **`docs/remote-agents.md`'s own "Implementation Correspondence" table is stale about
  this crate's existence.** Two of its rows — "Kubernetes binding" and "Sprig image" —
  still read `*to be added*: crates/buzz-backend-kubernetes` and `*to be added*:
  Dockerfile.sprig + workflow` respectively, even though at the recorded revision both
  artifacts exist substantially: this crate is a 14-module, ~6,400-line binary crate
  with 159 automated tests, `Dockerfile.sprig` is a 44-line multi-stage image build, and
  both `.github/workflows/sprig.yml` and `.github/workflows/sprig-image.yml` exist as
  dedicated release workflows. Checked directly against git history: the spec merged in
  PR #3748 (commit `28ae6cd21`, the commit its own "Known Defects" section is pinned
  against); this crate and the desktop deploy path were added afterward in PR #4289
  (commit `6530b58a6`); no later commit updated the two stale correspondence rows. This
  is drift in the specification document, not in the crate — the crate's own behavior
  was checked directly against the spec's normative prose (§Pod shape, §K8s Secrets,
  §K8s GC, §Deploy State Machine, [L3]) throughout this node's *Implementation surface*
  table above, and no divergence between the crate's code and that normative prose was
  found. Fixing the spec document's table is out of this node's own scope (issue #921
  excludes changing runtime product behavior or a separately-owned document without a
  linked implementation issue); it is named here as the honest reading of a check this
  node ran, not left silent.
- **`RESTART_POLICY = "Never"` and the `inactivity_seconds: 0` refusal are compliant
  with, not divergent from, [L3] item 2** — checked directly: the spec states the
  indefinite-lifetime opt-in (`inactivity_seconds: 0` → `restartPolicy: OnFailure`)
  applies "only after both prerequisites land — the pinned exit-code contract … *and*
  the crash-loop classification row," and `config.rs`'s own refusal message names
  exactly that gate. This is recorded explicitly (per this template's evidence
  expectations, an empty divergence claim needs the same evidentiary weight as a found
  one) rather than left as silence that could be misread as "not checked."
- **No divergence found in the [L3] mechanism mapping.** Checked directly, mechanism by
  mechanism, against `docs/remote-agents.md:1497-1515`: full-pubkey annotation identity
  evidence (`observe.rs`'s `verify`), `state.running` as "started" (`observe.rs`'s
  `decode_startup`), `resourceVersion`-unset quorum reads (`cluster.rs`'s
  `list_with_date`/`get_pod`/`secret_exists`), UID+`resourceVersion` delete
  preconditions (`cluster.rs`'s `delete_pod` via `classify::Fence`), `Status.reason` as
  the 409 discriminator (`cluster.rs`'s `reason_is`), and the
  `app.kubernetes.io/managed-by` + binding-version labels as the management marker
  (`naming.rs`) — every one of these is present in the code exactly as the spec
  describes it, each backed by its own unit test named for the property it pins (for
  example `the_two_409s_are_never_conflated`, `deletion_mark_beats_every_startup_state`,
  `every_delete_carries_the_authorizing_fence`).

## Verification

- **155 unit/property tests** across the 14 `src/*.rs` files, counted directly by
  grepping `#[test]` occurrences per file (classify 12, client 4, cluster 4, config 14,
  env 27, gc 11, image 8, intent 7, main 5, naming 7, observe 12, pod 13, reconcile 24,
  wire 7). The pure decision layers (`classify`, `gc::plan`, `intent`, `image`,
  `naming`, `env`, `wire`) are tested with no I/O at all; `reconcile.rs`'s own 24 tests
  drive the *shipped* `deploy()` function against an in-process `Fake` implementing the
  `Substrate` trait, with a scripted fake clock and pod-map mutations, rather than a
  reimplemented test-only reconciler — the same seam `cluster.rs` fills in production.
  `cluster.rs`'s own 4 tests exercise the real kube-rs request-building/response-parsing
  path through a `tower::service_fn` fake HTTP service, including the specific mutation
  (`reason == …` → `code == 409`) the module's own doc comment names as the trap the
  specification warns about.
- **4 integration tests** in `tests/wire_fixtures.rs`, run against the actually-built
  `buzz-backend-kubernetes` binary over a real OS pipe (not an in-process function
  call), with `KUBECONFIG` pointed at a nonexistent path so a fixture that accidentally
  reaches a live cluster fails loudly rather than depending on the developer's ambient
  environment. Golden request/response fixtures under `tests/fixtures/provider-wire/`
  are recorded from the desktop's real request-construction code path, not
  hand-derived — the fixtures' own README documents a specific past failure (four
  simultaneously-impossible values) that resulted from deriving rather than recording
  a fixture.
- **CI wiring**: `Justfile`'s unit-test recipe enumerates `cargo nextest run -p
  buzz-backend-kubernetes` explicitly, with a comment stating this is necessary because
  no CI step runs `cargo test --workspace` — workspace membership alone buys
  clippy/check, not execution of a single test.
- **No envtest/kind (real-apiserver) conformance suite exists in this repository** for
  this crate, despite `docs/remote-agents.md`'s own [L3] section describing one as
  feasible and enumerating the specific failure-mode families it should cover
  (startup-state discrimination under slow/unschedulable scheduling, the GC/attempt
  interleaving race, the divergence-discriminator and 409-split cases). Checked
  directly: no CI workflow or `Justfile` recipe references `envtest` or a `kind`
  cluster for this crate, and the only in-repository mentions of either term are prose
  in doc comments and the fixtures README describing such a suite as future work. The
  159 automated tests above are static/fake-substrate; none of them exercise a real
  Kubernetes apiserver.
- **No live cluster was exercised while authoring this node.** This is a static-source
  reading of the crate's own code, tests, and the specification it targets.

## Relationships

- references: architecture-deployment-kubernetes
- references: architecture-containers-agent-runtime

Both targets are merged on `origin/launchpad` at the recorded revision and already
discuss this crate from their own side: `architecture-deployment-kubernetes.md`
explicitly names `buzz-backend-kubernetes` as a distinct compute-provisioning concern
outside its own scope, stating it "belongs in its own node" (which this node now is);
`architecture-containers-agent-runtime.md` independently names this crate as the
backend provider the Desktop hands the agent's private key to, realizing the
agent-runtime container as a bare Kubernetes Pod. Both citations support the
`references` directionality `relationships.schema.json` defines ("cites target as
supporting context, no ownership or currency dependency implied") rather than
`part-of` — this crate is a standalone binary and workspace member, not a constituent
source file of either node's own subject. No `implements` edge is declared (see
*Target*, above). No `part-of` edge is declared: this crate is not a sub-component of
the Kubernetes deployment topology `architecture-deployment-kubernetes.md` documents
(that node itself draws this same boundary) nor of the agent-runtime container itself
(it deploys pods running that container's image; it does not run inside one).

## Scope and omissions

**This node covers** `buzz-backend-kubernetes`'s implementation responsibility and
boundary as a Kubernetes remote-agent provider plugin; its wire protocol, deploy state
machine, garbage collection, identity/naming, environment-resolution, and pod-hardening
mechanisms; its owned source paths and representative/counted automated tests; where it
plugs into CI (`Justfile`) and the desktop's binary sidecar bundling
(`.github/workflows/ci.yml`, `release.yml`, the `*-canary.yml` workflows); and the
divergence found between the specification document's own correspondence table and
current code.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `buzz-acp`/`buzz-agent`/`buzz-dev-mcp`/`sprig` agent-runtime container this crate deploys pods *of* (the image contents, the harness's own lifecycle/shutdown behavior, the `sprig` multicall dispatch) | `architecture-containers-agent-runtime.md` |
| The relay's own Kubernetes deployment topology (the Helm chart at `deploy/charts/buzz/`) — a separate compute-provisioning concern this crate is not part of | `architecture-deployment-kubernetes.md` |
| The desktop-side half of the remote-agent protocol: discovery, invocation, redaction, the launch resolver, and the eight "Known Defects" `docs/remote-agents.md` names as desktop- or harness-code prerequisites (`backend.rs`, `agents_deploy.rs`, `readiness.rs`, `crates/buzz-acp`) | `docs/remote-agents.md`'s own "Known Defects" and "Implementation Correspondence" sections; no desktop-side corpus node exists yet for this surface |
| `docs/remote-agents.md` becoming a corpus node in its own right (a prerequisite for a future `implements` edge from this node) | Unresolved; not filed as its own task by this node — an author hitting this gap should check for an existing issue before filing a new one, per `AGENTS.md`'s own guidance |
| `Dockerfile.sprig`'s own content and the `sprig-image.yml`/`sprig.yml` release workflows in depth | Named here as evidence for the *Divergences* section only; not documented as their own node |
| Whether Block's private `squareup/block-coder-tf-stacks` or `sprout-backend-blox` repositories actually invoke this binary in production, or use a different provider | Outside this repository's visible source; recorded as an `INFERENCE` (confidence 0.5) rather than a `FACT`, the same boundary `architecture-deployment-kubernetes.md` already draws for the private staging-cluster pipeline |

**Expected but not verified when this node was written:**

- **No live cluster, envtest, or kind suite was run.** Every claim above about the
  crate's behavior is a static reading of its source and its 159 automated tests
  (themselves fake-substrate or built-binary-over-a-broken-kubeconfig), not observed
  runtime behavior against a real Kubernetes apiserver.
- **Whether the eight "Known Defects" `docs/remote-agents.md` names (desktop- and
  harness-code prerequisites, e.g. the deploy payload bypassing the launch resolver,
  the missing I5 inactivity-reaper timer, the unpinned clean-exit contract) remain
  unresolved at the recorded revision was not independently re-verified against current
  desktop/`buzz-acp` code** — this node's own scope is the Kubernetes-provider crate,
  and several of this crate's own doc comments (in `wire.rs`, `env.rs`) reference those
  defects by number as the reason a given field is optional or handled a particular
  way, which is evidence the crate's authors tracked them, not evidence of their
  current resolution status.
- **Whether the nine-field `provider_config` schema, the pod hardening defaults, or the
  600-second operation deadline have been tuned against real-world cluster behavior**
  (autoscaler cold-start latency, actual image pull times) was not checked; the
  specification's own "Open Decisions" section (`docs/remote-agents.md:1745-1754`)
  names the deadline's exact value as an open UX question, not a settled one.
