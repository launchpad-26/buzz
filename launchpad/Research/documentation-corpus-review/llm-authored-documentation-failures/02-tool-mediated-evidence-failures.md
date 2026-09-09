# Tool-mediated evidence failures

| Metadata | Value |
|---|---|
| Topic number | 02 |
| Exact research question | How do search failures, truncated output, inaccessible files, ignored command errors, unsuitable tools, and lost execution context affect the accuracy of agent-authored documentation? |
| Primary model | Codex |
| Research date | 2026-09-08 |
| Scope | Agent-authored technical documentation grounded in repositories, command output, tests, configuration, schemas, and web or document retrieval. Local observations refer to the `launchpad-26/buzz` worktree at revision `4bac39fe512c9b289992951de1222abd61d5790c`. External evidence spans official tool specifications and primary studies published from 2021 through April 2026. “Accuracy” means correspondence between a document's factual or procedural claims and the intended repository revision and execution environment. |
| Evidence limitations | No located controlled study isolates all six named tool failures in an end-to-end documentation-authoring task. The causal chain is therefore supported by direct tool semantics and local observations, then triangulated with retrieval, long-context, and software-agent studies. Confidence is high about what the tools expose or omit, but moderate about the size and frequency of the resulting documentation errors. This limitation qualifies the executive answer and each cross-domain inference below. |

## Executive answer

**Bottom line — moderate confidence:** the six failures damage documentation accuracy by corrupting the evidence channel before prose is written. They produce three recurring epistemic errors:

1. **false absence** — an agent treats “my search did not return it” or “I could not open it” as “it does not exist”;
2. **false completeness** — an agent treats a clipped, filtered, or top-ranked observation as the whole relevant artifact; and
3. **false success or false attribution** — an agent treats a command's apparent success, or output from the wrong directory, branch, build, service, credentials, or time, as evidence about the intended system.

Those errors can become incorrect defaults, missing prerequisites, wrong command sequences, fictional architecture, omitted failure cases, and claims validated against the wrong target. The risk is not limited to hallucinating new facts: a sentence may accurately summarize the bytes the agent saw while still being inaccurate about the repository because the observation was incomplete or came from the wrong state.

Primary research supports the mechanisms, although mostly outside documentation authoring. Retrieval-augmented models often fail to recognize unanswerable or contradictory retrieved sets and then hallucinate; retrieval approaches also vary substantially by domain ([Park and Lee 2024](https://aclanthology.org/2024.tacl-1.91/); [Thakur et al. 2021](https://arxiv.org/abs/2104.08663)). Long-context experiments show that providing more evidence does not ensure that a model will use it, especially when relevant material is buried in the middle ([Liu et al. 2024](https://aclanthology.org/2024.tacl-1.9/)). Stateful tool benchmarks and software-agent experiments show that tool schema, feedback, state dependencies, and interface design materially affect task success ([Lu et al. 2025](https://aclanthology.org/2025.findings-naacl.65/); [Yang et al. 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html)). I infer that documentation grounded through the same observation-and-action loop inherits these failure channels.

The counterevidence matters. Browsing with citations can improve factual accuracy, and SWE-agent's intentionally bounded, stateful interface outperformed a plain shell. Some models in the long-context study retrieved middle-position key-value evidence perfectly. Deliberately suppressing verbose results can also prevent context flooding. Therefore the supported conclusion is **not** that tool use or truncation inherently reduces accuracy. Accuracy falls when loss, error, scope, or state is silent or mistaken for evidence; explicit limits, recoverable navigation, state capture, and independent postcondition checks can make tools accuracy-improving rather than accuracy-eroding ([Nakano et al. 2021](https://cdn.openai.com/WebGPT.pdf); [Yang et al. 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/5a7c947568c1b1328ccc5230172e1e7c-Paper-Conference.pdf)).

## Question, scope, and method

### Subquestions

- What distinct observation failures arise from search, output limits, access controls, command-status handling, tool choice, and execution-state loss?
- Through what mechanisms do those failures turn into inaccurate factual and procedural documentation?
- Which failures are detectable from a trace, and which require an independent repository or runtime observation?
- Which mitigations are supported, what trade-offs do they introduce, and what do they still fail to prove?
- Under which conditions do tools, filtering, and context reduction improve rather than degrade accuracy?

### Exclusions

- Deliberate source poisoning and prompt injection, except where imperfect retrieval research supplies a boundary case; those belong primarily to topic 17.
- General model hallucination without a tool-mediated cause; that belongs primarily to topic 4.
- Staleness across releases or revisions except where the immediate cause is lost execution context; broader revision coherence belongs to topic 3.
- Security and disclosure consequences of access controls, and program-wide policy synthesis.
- Quantifying prevalence in production documentation corpora; the located evidence does not support such an estimate.

### Evidence and source plan

The investigation used four evidence layers. First, it inspected the assigned repository instructions and tracked implementation at the recorded revision. Second, it checked official semantics for `ripgrep`, Git sparse checkouts and worktrees, POSIX/Bash status propagation, `curl`, and Playwright. Third, it used peer-reviewed primary studies of retrieval, long-context use, tool-state handling, and agent-computer interfaces. Fourth, it examined a recent repository-documentation evaluation preprint, explicitly treating its results as preliminary.

A working claim ledger tracked support, contrary evidence, context, confidence, and gaps. Consequential claims were triangulated where practical; specifications were treated as definitive only for their own tool's semantics. Counter-searches targeted successful tool use, benefits of selective context, models robust to position, and limits of automated validation. Source saturation was reached when additional searches repeated the same mechanisms—retrieval recall, observation loss, state dependence, and misleading success—without adding a new in-scope failure class. No claim is made that the search exhausted unpublished or proprietary evidence.

### Claim/evidence summary

| Claim | Best support | Counterevidence or boundary | Confidence and remaining gap |
|---|---|---|---|
| Failed or filtered retrieval can turn an answerable repository question into an apparently unanswerable one, and models do not reliably abstain. | Official search semantics plus experiments with unanswerable and contradictory retrieved sets ([ripgrep guide](https://github.com/BurntSushi/ripgrep/blob/14.1.1/GUIDE.md#automatic-filtering); [Park and Lee 2024](https://aclanthology.org/2024.tacl-1.91/)). | Browsing and retrieval improve factuality when relevant, reliable evidence is found ([Nakano et al. 2021](https://cdn.openai.com/WebGPT.pdf)). | High for the retrieval mechanism; moderate for documentation impact because no documentation study injected the failure. |
| Showing more raw output is not a monotonic accuracy improvement. | Position-sensitive long-context performance and context saturation; SWE-agent's context-flooding analysis ([Liu et al. 2024](https://aclanthology.org/2024.tacl-1.9/); [Yang et al. 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/5a7c947568c1b1328ccc5230172e1e7c-Paper-Conference.pdf)). | Some evaluated models were nearly perfect on synthetic key-value retrieval; bounded output can improve navigation. | Moderate; results vary by model, task, ordering, and interface. |
| Tool interface and state representation can change agent outcomes without changing model weights. | SWE-agent's interface ablations and ToolSandbox's state-dependency/tool-schema results ([Yang et al. 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html); [Lu et al. 2025](https://aclanthology.org/2025.findings-naacl.65/)). | Results are from coding and simulated mobile tasks, not documentation. Stronger models were not uniformly better on state-dependency tasks. | High within those benchmarks; moderate when transferred to documentation authoring. |
| Exit status alone does not prove the intended evidence-producing postcondition. | POSIX pipeline rules, `curl`'s HTTP status behavior, and Buzz's `pgschema` boundary ([POSIX.1-2024](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html#tag_19_09_02); [curl FAQ](https://curl.se/docs/faq.html#curl_does_not_return_error_for_HTTP_non_200_responses); [Buzz guidance](../../../../AGENTS.md#common-gotchas)). | Exit zero can be sufficient when the command's success contract exactly matches the asserted postcondition. | High for command semantics; the author must still define the intended postcondition. |
| Surface-quality review cannot establish repository-level documentation accuracy. | A 2026 preprint reports a case where an LLM judge gave perfect scores to both generic and repository-aware documentation while functional QA distinguished them ([Wang et al. 2026](https://arxiv.org/abs/2604.06793v1)). | One case and one new benchmark do not establish general evaluator failure; the paper is a preprint. | Low-to-moderate; useful as a warning, not a settled effect size. |

## Failure taxonomy

| Failure class | Description | Evidence and boundary conditions |
|---|---|---|
| Search failure | The query, index, traversal scope, ranking cutoff, ignore rules, regex, case handling, or vocabulary fails to return relevant evidence. The document then overrepresents easy-to-find names and may convert zero hits into an absence claim. | `ripgrep` recursively searches the current directory, respects ignore files, and skips hidden files, binary files, and symlinks by default; all are reasonable defaults, but they bound a negative result ([official guide, v14.1.1](https://github.com/BurntSushi/ripgrep/blob/14.1.1/GUIDE.md#automatic-filtering)). BEIR found large cross-domain differences among lexical, sparse, dense, and reranking systems; in-domain performance did not predict zero-shot generalization ([Thakur et al. 2021](https://arxiv.org/abs/2104.08663)). A zero-result search is evidence only about the declared query, corpus, filters, revision, and tool semantics—not proof that the concept is absent. |
| Truncated output | The tool or interface drops a tail, middle, old observation, result set, or oversized response. Explicit truncation can invite a follow-up; silent truncation can look complete. Either can omit the one constraint, error, or counterexample needed to qualify a claim. | SWE-agent caps search results and file windows but exposes totals, omitted-line counts, navigation, and instructions to refine overbroad searches; it also collapses old observations to control stale and duplicate context ([Yang et al. 2024, pp. 2–3 and 42](https://proceedings.neurips.cc/paper_files/paper/2024/file/5a7c947568c1b1328ccc5230172e1e7c-Paper-Conference.pdf)). This is counterevidence to a blanket anti-truncation rule: bounded views can help if loss is visible and recoverable. Completeness of transport still does not prove that the model used every visible item; long-context utilization is position-sensitive ([Liu et al. 2024](https://aclanthology.org/2024.tacl-1.9/)). |
| Inaccessible file or source | Evidence exists but cannot be read because it is outside the checkout, denied by permissions, not fetched, behind authentication, unavailable on the network, or encoded in a format the selected reader cannot parse. If access failure is flattened to “not found,” the document may assert nonexistence or substitute a plausible guess. | POSIX distinguishes permission denial (`EACCES`) from a missing path (`ENOENT`), so those states must not be collapsed ([POSIX `open()`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html)). Git sparse checkout intentionally leaves tracked files out of the working tree ([Git documentation](https://git-scm.com/docs/sparse-checkout#_purpose_of_sparse_checkouts)). Access through one identity, mirror, or extractor proves only that surface was readable, not that every relevant source was. |
| Ignored or misread command error | A non-zero exit, stderr, timeout, partial result, HTTP error, failing pipeline component, or domain-specific warning is discarded or interpreted as success. Conversely, a non-zero informational status such as “differences found” may be misclassified as an execution failure. | Without `pipefail`, POSIX derives a pipeline's status from its rightmost command; Bash also has documented `errexit` exceptions ([POSIX.1-2024](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html#tag_19_09_02); [GNU Bash manual](https://www.gnu.org/software/bash/manual/bash.html#Pipelines)). By default, `curl` can successfully transfer an HTTP 404 or 401 response and return success unless the caller requests HTTP-failure semantics ([curl FAQ](https://curl.se/docs/faq.html#curl_does_not_return_error_for_HTTP_non_200_responses)). Exit zero proves only the command's defined success condition, not the author's intended claim. |
| Unsuitable tool | The tool's abstraction does not match the evidence question: line-oriented text search is used for semantic control flow, a schema diff for seed data, a mock for production behavior, a screenshot for hidden state, or a generic shell where structured feedback is needed. The output can be technically correct yet non-probative. | SWE-agent's custom interface improved resolution by 10.7 percentage points over its shell-only baseline on a 300-task SWE-bench Lite ablation, and the authors identify context flooding, inconsistent search output, and weak edit feedback as shell-interface problems ([Yang et al. 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/5a7c947568c1b1328ccc5230172e1e7c-Paper-Conference.pdf)). ToolSandbox found performance sensitivity to distracting tools and scrambled names, descriptions, or argument types ([Lu et al. 2025](https://aclanthology.org/2025.findings-naacl.65/)). Neither result says one interface is universally best; fitness depends on the claim and environment. |
| Lost execution context | The observation loses its binding to working directory, worktree, branch/commit, dirty state, environment variables, credentials, tool version, configuration, build mode, running process, subscription, or time. Evidence from a different state is then attributed to the intended state. | Git worktrees share repository data but have per-worktree `HEAD` and index state ([Git worktree documentation](https://git-scm.com/docs/git-worktree#_description)). ToolSandbox shows that state dependencies and insufficient-information cases remain challenging and that models may forget unresolved state and repeat errors ([Lu et al. 2025](https://aclanthology.org/2025.findings-naacl.65/)). Recording a commit alone is insufficient for runtime claims; recording runtime state alone is insufficient for source-revision claims. |

## Causes and mechanisms

### The evidence funnel

**Sourced fact:** retrieval is not a neutral window onto a corpus. `ripgrep` applies traversal filters by default, and BEIR's 17 zero-shot datasets show that retriever performance depends on task and domain. Park and Lee's controlled RALM experiments further show that models often fail to identify an unanswerable or contradictory retrieved set, leading to hallucinated answers ([ripgrep guide](https://github.com/BurntSushi/ripgrep/blob/14.1.1/GUIDE.md#automatic-filtering); [Thakur et al. 2021](https://arxiv.org/abs/2104.08663); [Park and Lee 2024](https://aclanthology.org/2024.tacl-1.91/)).

**Interpretation:** documentation generation is an evidence funnel:

`source state → accessible corpus → search result → visible tool output → retained model context → claim → validation`

Every arrow can remove information or change its meaning. Later fluent synthesis cannot recover facts that never entered the accessible corpus, and it cannot reliably tell whether no evidence was returned because the fact is absent, the query missed it, the path was excluded, or the tool failed. The characteristic error is therefore an **open-world observation presented as a closed-world conclusion**.

### Selection and observation failures compound

Search and access failures decide *which* evidence is available; truncation decides *which part* is visible. These failures are not additive only. For example, a broad search may return many generated or test fixtures first, a result limit may hide the production implementation, and a model may then summarize the fixtures accurately but document the production path incorrectly. Approximate semantic retrieval can bridge vocabulary gaps, while exact lexical search is stronger for identifiers; BEIR shows that neither family dominates every domain and that reranking trades higher average zero-shot performance for computational cost ([Thakur et al. 2021](https://arxiv.org/abs/2104.08663)).

Longer output is an incomplete remedy. Liu et al. varied only the position of relevant evidence and observed large performance changes; on their multi-document QA task, relevant evidence in the middle could yield worse performance than a closed-book baseline for GPT-3.5-Turbo. Yet Claude-1.3 variants were nearly perfect on the study's synthetic key-value task, and encoder-decoder models were more position-robust within training lengths ([Liu et al. 2024](https://aclanthology.org/2024.tacl-1.9/)). Thus the defensible claim is model- and task-conditional: output must be both available and usable, and “fits in the context window” is not a completeness guarantee.

### Status is part of the evidence

Commands communicate through more than stdout. Exit status, stderr, timeout, signal, response metadata, and post-execution state determine what the bytes mean. POSIX and Bash make pipeline and `errexit` behavior conditional, while `curl` explicitly treats a completed HTTP transfer separately from whether the server returned a 4xx/5xx application status. Dropping these channels can transform “query rejected,” “permission denied,” or “left command failed” into an empty or apparently successful observation.

**Interpretation:** an agent that quotes stdout without status provenance may produce locally faithful but semantically inverted documentation. A 403 body can be documented as an API response example when it actually shows missing authentication; an empty grep result can support “no configuration exists” when the directory was unreadable; a downstream formatter's zero exit can mask an upstream producer's failure. Conversely, treating every non-zero status as fatal can discard valid negative-test evidence. Correct handling requires the command-specific contract, not a universal “zero good, non-zero bad” heuristic.

### State loss changes the referent of a true statement

ToolSandbox formalizes an execution context that holds world-state snapshots and message history, and evaluates intermediate milestones rather than only a final response. Its state-dependency tasks remained difficult even for strong proprietary models; larger models sometimes did worse because they issued dependent tool calls in parallel, and models sometimes forgot unresolved issues and repeated errors ([Lu et al. 2025](https://aclanthology.org/2025.findings-naacl.65/)). SWE-agent likewise injects state such as the current working directory into observations and reports that stale or recent-but-wrong file views can cause edits against erroneous content ([Yang et al. 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/5a7c947568c1b1328ccc5230172e1e7c-Paper-Conference.pdf)).

**Interpretation:** in documentation, lost context commonly changes the subject without changing the sentence. “The test passes,” “the endpoint returns 200,” or “the file is absent” may each be true in one worktree, environment, role, or build and false in the one the document names. Because the prose remains plausible, wrong-state evidence can survive review more easily than a visible command failure.

### Concrete Buzz repository and tool failure modes

The following are bounded observations, not claims that these failures occurred in existing published Buzz documentation:

| Failure mode observed or documented at revision `4bac39f` | Documentation error it could induce | Validation boundary |
|---|---|---|
| This research worktree is sparse. `git sparse-checkout list` returned four included paths, `./bin/activate-hermit` was absent from the filesystem, and `git cat-file -e HEAD:bin/activate-hermit` succeeded. | A filesystem-only inventory could say the tracked activation script or whole source areas do not exist. | `git ls-tree -r --name-only HEAD` or revision-addressed `git show` can establish tracked-tree presence; neither proves the file is runnable in the sparse worktree. Git documents that sparse-checkout files remain tracked while absent from the working tree ([Git sparse-checkout](https://git-scm.com/docs/sparse-checkout#_purpose_of_sparse_checkouts)). |
| An initial combined read of the governing files produced an explicit tool warning: “truncated output” after 10,419 original tokens. The files were then re-read separately before research continued. | If the marker were missed, later sections of the research contract or template could be treated as if read and complied with. | An explicit marker establishes that loss occurred, not which unseen requirement matters. Separate bounded reads with known end lines established transport in this run; they do not prove perfect model recall. |
| Buzz's Playwright configuration reuses an existing local server outside CI, and repository guidance warns that it can serve a previous build. The mock bridge is compiled only for dev or E2E mode ([Playwright config](../../../../desktop/playwright.config.ts#L200-L204); [desktop bootstrap](../../../../desktop/src/main.tsx#L111-L132); [repository runbook](../../../../AGENTS.md#writing-e2e-screenshot-specs)). | A failure caused by a plain build may be documented as a product connection bug; a pass against a stale server may be documented as evidence for code that was never exercised. | Playwright's documented `reuseExistingServer` contract proves reuse behavior, not freshness ([Playwright](https://playwright.dev/docs/test-webserver)). Validate process ownership/build identity and exercise the intended build mode; a passing UI assertion alone does not identify the artifact served. |
| The runbook says live mock messages are silently dropped before subscription, and identical unscoped screenshots can capture the same pixels for supposedly distinct states ([repository runbook](../../../../AGENTS.md#writing-e2e-screenshot-specs)). | An empty screenshot can be described as “no unread indicator,” or duplicate images can be presented as evidence of different states. | Wait for the subscription and assert seeded state before capture; hash distinctness detects byte-identical shots but does not prove that different images depict the intended states. |
| Root `cargo test` excludes the desktop crate, while `pgschema apply` omits seed DML and some storage parameters ([repository gotchas](../../../../AGENTS.md#common-gotchas)). | A green partial test may become “all desktop tests pass”; a successful schema apply may become “the live database matches `schema.sql`.” | Invoke the explicitly scoped desktop test. For schema state, use the repository's reconciliation plus live catalog/data assertions. A source-string comparison proves neither database convergence nor runtime behavior. |

These examples show why a command or screenshot must be evaluated against the claim it is meant to support. “The tool ran” and “the evidence-producing postcondition holds” are different propositions.

## Detection and validation

### Preserve an evidence envelope

A material observation should remain bound to an evidence envelope: repository and revision, worktree and current directory, dirty state, sparse-checkout or submodule state, command and arguments, relevant non-secret environment/configuration, tool version, start time, exit status, stderr, timeout, and whether output was filtered, paginated, summarized, or truncated. For live systems, add target identity, authentication role, request identifiers, and response status.

This envelope detects mismatches and makes replay possible. It **cannot** establish that the selected source was authoritative, that the command's semantics matched the question, or that the agent interpreted the visible bytes correctly.

### Test retrieval coverage separately from claim support

Candidate detection methods include:

- enumerate the intended tracked tree or document corpus independently of the text-search tool;
- inspect ignore, hidden-file, binary, symlink, type, path, branch, and index settings;
- repeat consequential negative searches with exact identifiers, synonyms, filename search, and a structurally aware or semantic method where appropriate;
- seed known sentinel evidence to measure whether the search path can retrieve it; and
- record total-result counts and ranking/cutoff information.

These checks can reveal a broken retrieval route. They **cannot** prove full recall over unknown relevant evidence: passing a sentinel tests the sentinel's path, and multiple searches may share the same incomplete corpus or index. BEIR's domain-dependent results are a reason to measure retrieval on representative repository questions instead of assuming benchmark or in-domain performance transfers ([Thakur et al. 2021](https://arxiv.org/abs/2104.08663)).

### Fail visibly on observation loss

Output interfaces should return an explicit completeness state such as `complete`, `truncated`, `timed_out`, or `unavailable`, together with totals or continuation cursors where the tool can know them. On truncation, the agent can narrow the query, page through results, request line-addressed windows, or save and inspect a content-addressed artifact. SWE-agent provides a useful bounded pattern: at most 50 search results and 100 file lines, but with omitted counts, path and line state, navigation, and a request to refine overly broad queries ([Yang et al. 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/5a7c947568c1b1328ccc5230172e1e7c-Paper-Conference.pdf)).

Reading all pages or matching a checksum can establish that the retrieved artifact was transferred intact. It **cannot** establish that the artifact itself was complete, current, or correctly parsed, nor that the model attended to every part. Claim-level evidence extraction—recording the exact supporting span or machine observation—is still needed.

### Interpret command status by contract and verify effects

For shell pipelines, `pipefail` exposes a failing component that would otherwise be masked, but Bash documents contexts in which `errexit` does not exit; strict mode is therefore a guard, not a proof ([GNU Bash manual](https://www.gnu.org/software/bash/manual/bash.html#The-Set-Builtin)). HTTP clients should surface response status and use failure flags when the intended postcondition requires a successful application response. Stderr should not be discarded before classification, and timeouts or killed processes should be recorded separately from valid empty results.

After status checks, validate the postcondition through a different observation: query the live catalog after schema application, inspect the generated artifact after a build, confirm the expected test set was collected, or read back the API resource after a write. This detects “command succeeded by its own definition but did not establish my claim.” It **cannot** eliminate shared-mode errors when the command and validator consult the same stale cache, mock, credentials, or wrong target.

### Reassert state at boundaries

Capture state before each consequential read and after any operation that can change it. Useful boundaries include a new tool session, shell, worktree, branch switch, dependency installation, build, service restart, authentication change, or resumed task. Prefer revision-addressed reads and absolute or tool-provided working directories over a remembered `cd`. Git's per-worktree `HEAD` and index are a concrete reason not to infer revision from a sibling worktree ([Git worktree documentation](https://git-scm.com/docs/git-worktree#_refs)).

A state capsule can prove what was recorded at capture time. It **cannot** prove that a background service did not change afterward or that unrecorded environment variables were irrelevant. For mutable runtime evidence, freshness and identity checks must be adjacent to the observation.

### Validate the document against repository tasks

Claim-to-source review can catch unsupported statements, but fluent prose and internally valid citations can still describe the wrong scope. A complementary approach asks whether the document supports repository-grounded tasks such as detecting a feature, locating its implementation, reconstructing required steps, or executing an example. The April 2026 SWD-Bench preprint reports one case in which an LLM judge assigned perfect surface scores to both generic and repository-aware documentation, while repository-level completion questions distinguished them ([Wang et al. 2026](https://arxiv.org/abs/2604.06793v1)).

This is promising counterevidence to relying only on prose review, but the boundary is strict: SWD-Bench is a new preprint, functional QA is not equivalent to every documentation use case, and successful downstream task execution may exploit source code or model prior knowledge rather than the document. Evaluation should isolate what evidence the reader receives and include negative and failure-path questions.

## Mitigations

These are evidence-derived candidates, not adopted project policy.

1. **Represent uncertainty as a state, not a disclaimer.** If a file is inaccessible, a search is incomplete, or a command's status is ambiguous, classify the affected claim as unverified and keep that qualifier beside the claim. This prevents “not observed” from silently becoming “does not exist.” The trade-off is more abstention and follow-up work.

2. **Use layered retrieval matched to the claim.** Combine tracked-tree enumeration with lexical identifier search, structural navigation, and semantic search when the question crosses naming conventions. Inspect production code, tests, configuration, schemas, and generated artifacts separately. Cross-method agreement raises confidence only when methods do not share the same excluded corpus. Layering increases cost and can add distractors; reranking itself has computational trade-offs ([Thakur et al. 2021](https://arxiv.org/abs/2104.08663)).

3. **Design bounded but recoverable observations.** Prefer line-addressed windows, result totals, explicit omission markers, stable cursors, and query-refinement feedback over either silent clipping or unbounded dumps. Collapse stale output only after retaining an addressable trace or summary of what was removed. SWE-agent's results show that interface design can materially improve agent performance, but its exact limits are not validated defaults for documentation work ([Yang et al. 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html)).

4. **Make errors typed and actionable.** Preserve exit status and stderr; distinguish no matches, access denied, timeout, parse failure, HTTP rejection, partial success, and valid negative result. Return current state and legal recovery actions where possible. ToolSandbox's informative exceptions and state-dependent tasks support exposing the dependency rather than asking the model to guess it ([Lu et al. 2025](https://aclanthology.org/2025.findings-naacl.65/)). Detailed errors may expose sensitive paths or data, so reports should retain diagnostic class and provenance without publishing secrets.

5. **Bind every material claim to a state capsule.** Record revision, worktree, path, dirty state, tool version, build identity, runtime target, and timestamp. Re-capture after state transitions and before drafting conclusions. This adds trace volume; summaries should remain linked to raw observations so context reduction is reversible.

6. **Validate postconditions independently.** Do not let process completion stand in for database convergence, test collection, artifact freshness, message delivery, or API acceptance. Choose a validator that observes the intended effect and, for high-consequence claims, a second method with a different failure mode. Independence is imperfect: two tools can share a cache, mock, parser, or source.

7. **Test the evidence pipeline with controlled failures.** Include a hidden or ignored sentinel, an inaccessible file, a relevant match beyond the output limit, a failing left-hand pipeline command, a successful HTTP transfer with a 404, a wrong worktree, and a stale server. The purpose is to verify that each becomes an explicit non-success state rather than plausible prose. Passing injected cases demonstrates handling of those cases, not coverage of all real failures.

8. **Keep citations close to claims and replay a sample.** Citations make fact-checking more tractable, as WebGPT's design demonstrates, but WebGPT also reports failures from unreliable sources ([Nakano et al. 2021](https://cdn.openai.com/WebGPT.pdf)). Reviewers should replay consequential observations from the recorded state and check whether the cited span entails the wording. Citation presence alone is not evidence quality.

## Limits and open questions

- **Directness:** retrieval QA, software repair, and simulated mobile tool use are analogous to repository-grounded documentation, not identical. They establish plausible mechanisms and intervention effects, not a documentation-specific error rate.
- **Model and harness drift:** the strongest controlled studies evaluated model and interface generations from 2021–2025. Liu et al. already found material differences among architectures and models; ToolSandbox found larger models were not uniformly better on state-dependency tasks. Results should not be projected as fixed properties of “LLMs.”
- **No prevalence estimate:** local runbooks enumerate known pitfalls but do not show how often agents caused documentation defects through them. This report does not infer prevalence from the number of warnings.
- **Counterevidence:** tools can improve factuality and task success, explicit context reduction can remove stale or distracting observations, and some models use long contexts robustly on some tasks. These findings reject both “more raw evidence is always better” and “tool mediation is inherently unreliable.”
- **Detection regress:** a validator is another tool with scope, access, status, and state. Independent modes and deliberate fault injection reduce correlated failure; they do not produce absolute assurance.
- **Invisible truncation:** explicit omission markers are detectable. If an API, UI, parser, or intermediary silently drops content and exposes no total or checksum, downstream inspection may be unable to distinguish a complete artifact from a prefix without an independent source.
- **Access and confidentiality:** broader access can reduce evidence gaps but is not automatically desirable. Least-privilege constraints may intentionally leave evidence unavailable. The accurate response is bounded uncertainty or human escalation, not permission expansion or fabricated completeness.
- **Open empirical question:** how much do each of the six failures change factual accuracy, procedural executability, and omission rates when modern documentation agents work on version-pinned repositories? A controlled benchmark would need injected tool faults, complete execution traces, claim-level ground truth, multiple documentation genres, current models, and blinded human or functional evaluation.

## Practical review checks

- Candidate check: for every negative claim (“none,” “not supported,” “no file”), record the searched corpus, revision, path, filters, query variants, and access failures; reject the claim if the observation was truncated or the corpus was not enumerated.
- Candidate check: require every tool observation used as evidence to declare `complete`, `truncated`, `timed_out`, `unavailable`, or `partial`, with a continuation path for non-complete states.
- Candidate check: preserve command, working directory, revision, relevant configuration, tool version, exit status, stderr, and output-limit metadata for each consequential claim.
- Candidate check: inspect pipeline component statuses and HTTP application status; do not accept a final zero status without the command-specific success contract.
- Candidate check: pair each “command passed” claim with a postcondition assertion and state what the assertion cannot prove.
- Candidate check: before using filesystem search as a repository inventory, inspect sparse-checkout, submodules, generated/ignored files, hidden paths, binary formats, symlinks, and permissions.
- Candidate check: choose validation tools by claim type—syntax/parser for structure, live query for state, integration test for behavior, screenshot for appearance—and prohibit a validator from claiming beyond its observable surface.
- Candidate check: after a new session or state transition, re-capture repository/worktree/branch, dirty state, current directory, build artifact, runtime target, credentials role, and time.
- Candidate check: inject at least one known retrieval sentinel, one deliberate command failure, one beyond-limit result, and one wrong-state target into the evidence pipeline; verify that none becomes an unqualified documentation claim.
- Candidate check: replay a risk-ranked sample of claims from their recorded evidence envelopes and include failure paths, prerequisites, defaults, and negative behavior—not only happy-path statements.
- Candidate check: treat citation presence, green CI, complete byte transfer, and polished prose as separate signals; none alone establishes repository-level documentation accuracy.

## References

- [SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html) — Yang et al., NeurIPS 2024; interface ablations, bounded search/file views, explicit feedback, context management, and shell-only comparison.
- [Lost in the Middle: How Language Models Use Long Contexts](https://aclanthology.org/2024.tacl-1.9/) — Liu et al., *Transactions of the Association for Computational Linguistics*, 2024; controlled context-position and retrieval-utilization evidence, including model-dependent counterexamples.
- [Toward Robust RALMs: Revealing the Impact of Imperfect Retrieval on Retrieval-Augmented Language Models](https://aclanthology.org/2024.tacl-1.91/) — Park and Lee, *TACL* 12, 2024; behavior under unanswerable, conflicting, and adversarial retrieved document sets.
- [BEIR: A Heterogenous Benchmark for Zero-shot Evaluation of Information Retrieval Models](https://arxiv.org/abs/2104.08663) — Thakur et al., NeurIPS Datasets and Benchmarks 2021; domain/task variation and efficiency trade-offs across retrieval architectures.
- [ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities](https://aclanthology.org/2025.findings-naacl.65/) — Lu et al., Findings of NAACL 2025; state dependencies, insufficient information, informative execution errors, tool-description perturbations, and evaluation limitations.
- [WebGPT: Browser-assisted question-answering with human feedback](https://cdn.openai.com/WebGPT.pdf) — Nakano et al., OpenAI, 2021; counterevidence that browser tools and citations can improve factuality, with source-reliability and out-of-distribution limits.
- [Evaluating Repository-level Software Documentation via Question Answering and Feature-Driven Development](https://arxiv.org/abs/2604.06793v1) — Wang et al., arXiv preprint v1, 2026-04-08; preliminary repository-level documentation evaluation and a boundary of surface LLM judging.
- [ripgrep User Guide: Automatic filtering](https://github.com/BurntSushi/ripgrep/blob/14.1.1/GUIDE.md#automatic-filtering) — BurntSushi/ripgrep, release 14.1.1; default ignore, hidden, binary, and symlink traversal semantics.
- [Git sparse-checkout documentation](https://git-scm.com/docs/sparse-checkout#_purpose_of_sparse_checkouts) — Git project documentation, accessed 2026-09-08; tracked files omitted from a sparse working tree and command-behavior boundaries.
- [Git worktree documentation](https://git-scm.com/docs/git-worktree#_refs) — Git project documentation, accessed 2026-09-08; shared repository data and per-worktree `HEAD`, index, and pseudo-ref state.
- [POSIX.1-2024 Shell Command Language: Pipelines](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html#tag_19_09_02) — The Open Group Base Specifications Issue 8, 2024; pipeline exit-status derivation and `pipefail` semantics.
- [POSIX.1-2024 `open()`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html) — The Open Group Base Specifications Issue 8, 2024; distinct success, missing-path, and permission-denied states.
- [GNU Bash Reference Manual](https://www.gnu.org/software/bash/manual/bash.html#The-Set-Builtin) — GNU Project, accessed 2026-09-08; `pipefail`, `errexit`, and their exceptions.
- [curl FAQ: HTTP non-200 responses](https://curl.se/docs/faq.html#curl_does_not_return_error_for_HTTP_non_200_responses) — curl project, accessed 2026-09-08; distinction between successful transfer and HTTP application failure.
- [Playwright web server documentation](https://playwright.dev/docs/test-webserver) — Microsoft Playwright, accessed 2026-09-08; `reuseExistingServer` and server-readiness semantics.
- [Buzz contributor guidance: E2E screenshot specifications](../../../../AGENTS.md#writing-e2e-screenshot-specs) — `launchpad-26/buzz`, revision `4bac39fe512c9b289992951de1222abd61d5790c`; build-mode, stale-server, subscription, animation, and screenshot-evidence boundaries.
- [Buzz contributor guidance: common gotchas](../../../../AGENTS.md#common-gotchas) — `launchpad-26/buzz`, revision `4bac39fe512c9b289992951de1222abd61d5790c`; worktree shell context, test-scope, and `pgschema` validation boundaries.
