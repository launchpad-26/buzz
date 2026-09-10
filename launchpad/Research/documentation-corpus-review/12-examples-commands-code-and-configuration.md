---
description: Research into reviewing examples, commands, code samples, configuration fragments, and expected output in the Buzz documentation corpus.
tags: [documentation, corpus, examples, commands, code, configuration, testing, safety, reproducibility, research]
---

# Examples, commands, code, and configuration

Researched 2026-09-08. This is research, not an adopted corpus standard.

## Research question

How should Buzz determine whether examples, commands, code samples, configuration
fragments, and expected outputs are correct, safe, reproducible, usable, and
maintainable in the environments for which they claim to work?

The investigation considered twelve subquestions:

1. Which kinds of executable or execution-adjacent content need to be distinguished?
2. What does “correct” mean for an illustrative fragment, a runnable example, a shell
   command, a configuration setting, and an output transcript?
3. Which context must be stated for a reader to reproduce an example?
4. What levels of checking exist between visual inspection and a realistic workflow?
5. When should documentation examples be compiled, executed, or tested as part of the
   product?
6. How should expected results, errors, variable output, and omissions be represented?
7. What makes a command safe to copy, adapt, and run?
8. Which facts must a configuration reference establish beyond a variable name and
   example value?
9. How should documentation balance concise teaching examples against secure,
   production-worthy practice?
10. How can executable content remain synchronized with the implementation without
    making the documentation unreadable?
11. Which checks can be automated, and which require technical and editorial judgment?
12. What does the current Buzz corpus make easy or difficult to establish?

## Bottom line

Executable content makes stronger claims than ordinary illustrative prose. A command
invites action; a code sample implies that some program can accept it; a configuration
row implies that a real component reads the named setting with the described semantics;
and an output block implies a relationship between an input and an observable result.
Review must identify the exact claim before deciding what evidence is sufficient.

The strongest practical model is:

> **Purpose and scenario → artifact class → environment and starting state → literal
> input and substitutions → declared validation level → expected observable result →
> side effects and recovery → authoritative source and change trigger.**

Five conclusions should govern the later checklist:

1. **Classify before testing.** An illustrative fragment, complete runnable example,
   command invocation, output transcript, and configuration reference row have different
   contracts. A fragment can be intentionally incomplete; an advertised quickstart
   cannot. The distinction must be visible to the reader rather than inferred from the
   fence language.
2. **State the assurance level honestly.** Syntax highlighting, parsing, linting,
   compiling, executing, asserting output, exercising an integration, and completing a
   reader task are progressively different observations. Success at one level does not
   prove the next. In particular, “compiled” is not “works,” and “ran without error” is
   not “produced the correct behavior.”
3. **Treat context as part of the example.** Version, platform, shell, working directory,
   dependencies, permissions, target environment, starting data or service state, and
   placeholder meanings can change the result. Hidden context makes a technically
   accurate snippet non-reproducible.
4. **Make safety and outcome observable.** A reader needs to distinguish input from
   output, know what will change, recognize success and failure, avoid pasting literal
   placeholders or secrets, and have cleanup or recovery where side effects matter.
5. **Connect examples to their source of truth.** Executable checks reduce syntax and
   drift defects, but they do not decide whether a scenario is relevant, the sample is
   pedagogically honest, the command is safe, or the documented configuration semantics
   match reader needs. Generation from canonical source, docs-as-tests, and human review
   solve different parts of the maintenance problem.

Buzz already has strong local guidance for procedures, configuration tables, evidence,
code references, and test references. It lacks one shared executable-content contract
and does not validate body content. Its validator can establish that a cited repository
path exists, but it does not parse, compile, execute, or compare fenced examples; inspect
commands for dangerous behavior; validate configuration rows against loaders; or verify
output transcripts. All eight observed configuration-template implementations are also
still `draft`. The foundations are therefore useful, but the current corpus cannot infer
sample correctness from a green corpus-validation run.

## Scope and method

This report covers code and pseudocode examples, command-line invocations, scripts and
fragments, configuration tables and sample configuration, expected output and error
transcripts, and placeholders embedded in those artifacts. It considers content inside
procedures, tutorials, reference pages, runbooks, and other document forms.

It does not:

- test every current Buzz command or sample;
- establish one mandatory execution level for every artifact;
- prescribe a particular snippet-testing framework or configuration schema;
- redesign the corpus templates, front matter, or validation pipeline;
- approve current configuration defaults or production deployment choices;
- treat all fenced blocks as executable; or
- introduce LLM-specific generation controls, which remain set aside for this research
  sequence.

Local inspection covered the procedure, reference, configuration, runbook, and
implementation-reference templates; the code-reference and test-reference standards;
the current configuration-template implementations; representative development
instructions; and the corpus validator's body-processing boundary. Fence and lexical
counts are discovery observations, not semantic classifications. Markdown can contain
nested fences, templates can demonstrate fence syntax, inline commands are not fenced,
and language labels do not establish intent.

External sources were selected in this order:

1. current Google and Microsoft developer-documentation guidance for code, commands,
   placeholders, output, security, and testing;
2. Rust's official executable-documentation mechanism as a concrete docs-as-tests model;
3. JSON Schema's official explanation of `default` and `examples` annotations;
4. OWASP guidance for secure defaults and secret handling;
5. IETF reserved namespaces for safe documentary examples; and
6. peer-reviewed research on executable examples and API-learning obstacles.

Vendor style guides are practice guidance, not neutral standards. Rustdoc is a
language-specific mechanism, not a universal implementation. JSON Schema describes its
own vocabulary and does not govern Buzz's Rust configuration loader. The empirical
studies concern API documentation, mostly in older programming contexts, so they support
the importance and limits of examples rather than a measured effect for the whole Buzz
corpus.

## Classify the artifact and its promise

A fence is presentation syntax, not a quality category. Review should first determine
what the content promises.

| Artifact class | Reader-facing promise | Minimum evidence shape | Typical hidden failure |
|---|---|---|---|
| Illustrative pseudocode | Explains an idea or control flow; is not accepted literally by a named tool | Conceptual review and an unmistakable non-runnable label | Reader mistakes it for supported syntax |
| Code fragment | Shows a valid portion of a larger program with declared omissions | Parse/type evidence where feasible, plus explicit setup and omissions | Omitted imports, state, or error handling make adaptation fail |
| Complete runnable example | Can be copied or assembled and run in the stated environment | Build and execution evidence with an asserted result | It compiles but demonstrates the wrong behavior |
| Command invocation | Can be issued in the stated shell and starting state | Safe execution at the declared scope, expected result, and side-effect review | Wrong directory, target, account, quoting, or platform |
| Command synopsis | Describes command grammar rather than a literal invocation | Agreement with the actual parser/help or canonical specification | Optional-argument notation is pasted as literal input |
| Configuration example | Demonstrates a coherent deploy or task scenario | Schema/parser/loader validation plus scenario review | Example value is mistaken for the runtime default or safe production value |
| Configuration reference entry | States the accepted name, type, default, semantics, and constraints | Direct inspection or generated facts from the canonical loader/schema | A committed template or stale sample is treated as authority |
| Expected output or error | Shows what an input should observably produce | Assertion against stable features of stdout, stderr, exit state, file/state change, or UI | Nondeterministic data is presented as exact, or output is confused with input |
| Transcript | Shows an interaction over time | Clear input/output roles and representative execution evidence | Prompts, commands, and responses cannot be distinguished or safely copied |

The same content can occupy more than one class. A tutorial may contain a complete
example and then excerpt one fragment for explanation. A command reference may show a
formal synopsis followed by a literal invocation. The review requirement is not one
label per fence; it is that the reader can tell which parts are runnable and what claim
each part makes.

Google's [command-line syntax guidance](https://developers.google.com/style/code-syntax)
draws this distinction directly: reference syntax can use conventional notation for
optional and mutually exclusive arguments, while procedural commands intended for copy
and paste should use literal values or clearly explained placeholders. Brackets, braces,
vertical bars, and ellipses that express grammar can become invalid or dangerous when a
reader mistakes them for input.

## An assurance ladder

“Tested example” is too vague to be a useful review verdict. The observation should name
the highest level actually established.

| Level | What the check can establish | What it does not establish |
|---|---|---|
| 0. Render and classify | The block displays correctly and the reader can identify code, input, output, and placeholders | The content is accepted by any tool |
| 1. Parse or lint | The artifact is syntactically acceptable to a named parser, shell linter, formatter, or schema | Dependencies exist, it executes, or semantics are correct |
| 2. Build or type-check | The sample compiles or type-checks in a declared build context | It runs, reaches the intended branch, or produces the claimed result |
| 3. Execute | The command or example completes under one declared invocation and environment | The behavior or output is correct, repeatable, safe elsewhere, or complete |
| 4. Assert behavior | Stable outputs, errors, exit status, or resulting state match explicit expectations | External integrations and reader adaptation work |
| 5. Exercise integration | The artifact works with representative real dependencies and configuration | Every supported environment, failure path, or production condition works |
| 6. Exercise the reader task | An intended reader can select, adapt, run, interpret, and recover using the documentation | Future versions remain correct |

This is a ladder of evidence, not a maturity score. Some artifacts do not need the top
level. Pseudocode might stop at conceptual review; a destructive production command may
be inappropriate to run automatically at all and instead need a sandboxed equivalent,
expert inspection, approval, and periodic controlled exercise. The defensible rule is to
test at the highest safe and proportionate level, record the level, and avoid wording
that implies more.

Rustdoc demonstrates both the strength and the boundary of executable documentation.
Its [documentation tests](https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html)
extract code examples, compile them, and normally execute them. Hidden setup lines can
keep the displayed example focused while preserving runnable completeness. Assertions
are still needed to prove a result rather than mere absence of panic, and annotations
such as `no_run`, `compile_fail`, and `ignore` deliberately create different assurance
levels. Rustdoc also warns that filesystem behavior depends on the execution working
directory. The transferable lesson is not “make every Markdown fence a doctest”; it is
that tooling, context, and declared exceptions must preserve the exact claim being made.

Hoffman and Strooper's
[executable-example model](https://doi.org/10.1016/S0164-1212(02)00055-9)
treats an example with inputs and expected outputs as a test-like, partial formal
specification. Executing it can demonstrate consistency between documentation and
implementation for those covered inputs. It cannot establish that the API is completely
specified or correct outside them. This is the right epistemic boundary for corpus
review: an executable example is stronger evidence than an unrun snippet, but it remains
a sampled claim.

## A common contract for executable content

Every material artifact should make the following information available either beside
the artifact or through an unambiguous enclosing document contract.

### Purpose and selection

- What reader goal, question, or scenario does this artifact serve?
- Is it illustrative, directly runnable, a formal synopsis, or observed output?
- Is it the smallest example that teaches the task without hiding a required condition?
- Does it use the product's supported and idiomatic path rather than merely a path that
  happened to work?

The field study by Robillard and DeLine,
[“A Field Study of API Learning Obstacles”](https://doi.org/10.1007/s10664-010-9150-8),
identified intent, code examples, scenario matching, penetrability, and format and
presentation as recurring factors in API learning among more than 440 professional
developers. It does not prove a checklist for Buzz, but it supports reviewing whether an
example matches the reader's scenario rather than scoring example quantity.

### Environment and starting state

As applicable, state:

- product, API, dependency, and format versions;
- operating system, architecture, runtime, and shell;
- working directory and repository state;
- required packages, imports, services, files, data, ports, and network access;
- identity, permissions, role, and target environment;
- preceding steps or state that the artifact depends on; and
- whether the context is disposable development, CI, staging, or production.

Context can be factored into a nearby prerequisite section when all following examples
share it. It should not be duplicated around every fence. The test is whether a reader
can determine the applicable context at the point of action without reconstructing it
from unrelated pages.

### Literal input, variables, and omissions

The reader must be able to distinguish:

- characters to enter exactly;
- placeholders to replace;
- shell prompts that should not be copied;
- generated or expected output;
- comments and explanatory annotations; and
- code deliberately omitted from a fragment.

Google's [placeholder guidance](https://developers.google.com/style/placeholders)
recommends descriptive placeholder names and an explicit explanation of what substitutes
for each. Its [code-sample guidance](https://developers.google.com/style/code-samples)
advises using the language's comment syntax to mark omitted code rather than ambiguous
ellipsis characters, especially where copy behavior matters. A placeholder that looks
like a plausible hostname, secret, path, or identifier is a correctness and safety
hazard because readers may run it unchanged.

### Observable result

State what success means at the level the example claims:

- exit status, stable stdout, or stable stderr;
- returned value or raised error;
- file, database, network, or service state change;
- UI state or visible response;
- invariant established after the action; or
- the next safe state in a larger procedure.

Expected output should say whether it is exact or illustrative. Variable timestamps,
IDs, hashes, paths, ordering, durations, and hostnames should use explained placeholders
or an explicit omission convention. If output is shortened, the reader should know what
was removed and whether ordering or adjacency still matters. Secrets and personal or
production data do not belong in transcripts.

### Side effects, failure, and recovery

For commands and executable examples, review:

- resources read, created, mutated, replaced, or deleted;
- network destinations and billable or production effects;
- privileges and credentials used;
- idempotence and behavior after partial completion;
- common failure signals and where to diagnose them;
- cleanup, rollback, roll-forward, or restoration; and
- the point beyond which an action is irreversible.

This overlaps the earlier report on
[procedural and operational documentation](08-reviewing-procedural-and-operational-documentation.md).
The executable-content review should inspect the individual artifact; the procedure
review should inspect the full sequence, branches, coordination, and recovery system.

### Provenance and maintenance

Record or make traceable:

- the implementation, parser, schema, CLI help, test, or specification that authorizes
  the artifact;
- the revision or version against which it was checked;
- the check or execution method and its actual scope;
- ownership where the sample crosses component boundaries; and
- the changes that should trigger revalidation.

This is not a demand for verbose metadata beside every one-line command. A test harness
or generated include can centralize it. The review requirement is traceability: a future
maintainer should be able to learn why the sample is believed and what change can make it
false.

## Code and pseudocode

### Correctness includes selection and pedagogy

Microsoft's [code-example guidance](https://learn.microsoft.com/en-us/style-guide/developer-content/code-examples)
says examples should solve meaningful audience tasks, remain concise and scannable,
identify dependencies and prerequisites, be easy to copy and run, show expected output,
use secure practices, and be compiled and tested. These criteria reveal why syntactic
validity is necessary but insufficient. A sample can compile while using a deprecated
API, bypassing the intended abstraction, hiding a required check, or teaching an unsafe
default.

Review should ask whether the example:

- exercises the behavior named by the surrounding prose;
- uses the supported public interface and project idioms;
- contains enough setup to reproduce the result;
- identifies exactly what has been omitted;
- includes imports, dependency declarations, and versions when they are not otherwise
  fixed;
- handles errors and untrusted input to the level appropriate for the scenario;
- avoids hard-coded secrets, live identifiers, and unnecessary privileges;
- produces the expected result through an assertion or other observable oracle; and
- remains readable after any generated or hidden scaffolding is accounted for.

Pseudocode must be labeled as such and should not borrow a real language fence if doing
so implies literal validity. Conversely, incomplete real code should not be relabeled
“pseudocode” merely to avoid maintaining it. Its purpose determines the appropriate
class.

### Minimal versus production-worthy examples

There is a genuine tension. Complete production code can bury the teaching point in
logging, retries, dependency injection, error taxonomy, resource cleanup, and policy.
Minimal code can normalize insecure or brittle practice. A useful reconciliation is:

1. retain everything required to avoid a materially false mental model or unsafe copied
   behavior;
2. omit incidental infrastructure when it does not change the lesson;
3. identify the omission at the location where a reader could otherwise infer
   completeness; and
4. link to a complete, tested example when the fragment is not a safe starting point for
   adaptation.

The label “simplified” does not excuse undisclosed security or correctness gaps. Review
must judge the likely reuse path: a conceptual algorithm and an authentication snippet
carry different copy risk.

## Commands and transcripts

A command is an intervention in a system, not decorative syntax. Review it against the
actual parser and a controlled environment, then against the surrounding task.

### Copy-safe command presentation

For literal invocations:

- name the shell and platform when syntax varies;
- state the working directory or use a stable, explicit path;
- put commands and output in separate blocks or mark their roles unmistakably;
- omit the prompt from copyable text unless the interface separates it;
- use descriptive placeholders and explain their allowed shape;
- quote placeholders and paths correctly for the target shell;
- show continuation characters only for that shell and avoid hidden trailing spaces;
- avoid formal synopsis notation in a click-to-copy block;
- name environment variables without exposing live values; and
- prefer a dry run, plan, list, or read-only inspection before a consequential action
  when the tool supports one.

Static checking must know the intended language. ShellCheck's
[SC2148 guidance](https://www.shellcheck.net/wiki/SC2148) explains that results depend on
the selected shell and recommends a shebang, a shell directive, or an explicit shell
selection. Running a shell linter without declaring whether a fragment targets POSIX
`sh`, Bash, or another shell can create misleading passes and failures.

For examples that require domains or IP addresses, use resources reserved for
documentation rather than plausible live targets. [RFC 2606](https://www.rfc-editor.org/rfc/rfc2606)
reserves `.example` and `example.com`, `example.net`, and `example.org` for examples;
[RFC 5737](https://www.rfc-editor.org/rfc/rfc5737) reserves three IPv4 TEST-NET blocks
for documentation. The RFCs exist partly because example values escape into real use.
They do not make a command safe by themselves: the action, credentials, and surrounding
target still need review.

### Expected output and errors

Output is most useful when it helps the reader verify a transition, understand the data
shape, or select the next branch. Decorative transcripts create maintenance cost without
an oracle.

A transcript should make clear:

- which lines are user input, stdout, stderr, prompts, or commentary;
- whether whitespace and order are significant;
- the expected exit status;
- which values vary and the rule they satisfy;
- whether the output is complete, abridged, or illustrative;
- what a normal warning looks like; and
- which difference means stop, diagnose, recover, or escalate.

Tests should assert stable semantics instead of snapshotting incidental timestamps,
temporary paths, nondeterministic order, terminal color, or dependency noise. When exact
text is itself an interface, such as a documented machine-readable format, exact output
can be appropriate and should be versioned accordingly.

## Configuration documentation

Configuration combines reference facts with scenario-specific advice. Review must keep
three values distinct:

1. **actual default:** the value or behavior used by the implementation when the setting
   is absent;
2. **example value:** a safe, syntactically valid value chosen to demonstrate a scenario;
3. **recommended value:** a contextual operational judgment for a named environment or
   workload.

They are not interchangeable. JSON Schema's official
[annotation guidance](https://json-schema.org/understanding-json-schema/reference/annotations)
is a useful warning: `default` is an annotation and does not automatically fill a missing
instance during validation; `examples` is also annotation-oriented. A schema can document
or validate aspects of a value without proving that the running application applies the
same default. For Buzz, the configuration loader remains authoritative unless the
application deliberately generates or consumes a stronger shared specification.

### Facts each setting may need

Depending on the setting, review for:

- exact key, CLI flag, field, or file location;
- owning component and environment scope;
- type, syntax, units, ranges, enumerated values, and normalization;
- whether it is required and under what condition;
- actual absent-value behavior and source of that fact;
- secret or sensitive-data classification, without ever recording the value;
- precedence among flags, environment variables, files, remote configuration, and
  built-ins;
- interactions, mutual exclusions, and dependencies on other settings;
- validation timing and the exact failure or fallback behavior;
- whether change is dynamic, reloadable, restart-bound, or migration-bound;
- development example, production implications, and secure posture;
- deprecation, replacement, removal version, and whether the setting is currently inert;
  and
- an authoritative source and freshness trigger.

OWASP's [secure-by-default guidance](https://devguide.owasp.org/en/04-design/02-web-app-checklist/01-secure-by-default/)
supports least privilege, secure defaults, and keeping clear-text passwords, secrets,
connection strings, and key material out of source and build artifacts. That is a
security baseline, not a claim that every current Buzz development default must be
production-hardened. Documentation should identify when a convenient development value
is intentionally unsuitable for production.

The [Twelve-Factor Config principle](https://www.12factor.net/config) remains useful for
distinguishing deploy-varying configuration and for its open-source credential litmus
test. It is dated guidance and does not specify a documentation schema, precedence model,
secret manager, reload behavior, or modern deployment control. Buzz's existing
configuration template sensibly combines its boundary with a structured reference
shape; this report does not treat Twelve-Factor as a complete configuration standard.

### Validate configurations as coherent scenarios

Validating individual values is weaker than validating the example as a whole. A sample
file or environment block should be checked for:

- parseability and schema or loader acceptance;
- mutual compatibility among the chosen values;
- presence of prerequisites and referenced files or services;
- absence of secrets and live infrastructure identifiers;
- applicability to the labeled environment;
- expected startup, reload, or validation behavior; and
- the user-visible task or operational outcome the configuration is intended to enable.

A syntactically valid configuration can still be internally contradictory, insecure,
ignored due to precedence, or attached to the wrong component.

## Source synchronization and maintenance

Three maintenance patterns are available, and none should be treated as universally
best.

| Pattern | Strength | Main risk |
|---|---|---|
| Hand-authored and separately tested | Editorial freedom and task-focused explanation | Sample and test can drift independently |
| Extracted or included from tested source | One canonical executable body | Production scaffolding can make the document noisy; context around the excerpt can still drift |
| Generated from schema, CLI help, or source metadata | High consistency for structured facts | Generator output can be unreadable, omit operational judgment, or faithfully reproduce a wrong source |

Choose at the unit of truth. Exact flag names, accepted values, and defaults are strong
candidates for generation when one machine-readable authority exists. Scenario choice,
warnings, why a value matters, and production tradeoffs need authored explanation. Code
that must compile can live in a testable example file and be included or checked against
the document. A one-line illustrative fragment may cost less to review manually than to
build into a fragile extraction system.

Changes that should trigger focused revalidation include:

- public API, type, function, or error changes;
- CLI parser, help, exit-code, shell, or platform changes;
- configuration loader, schema, default, precedence, validation, reload, or deprecation
  changes;
- dependency and toolchain version changes;
- security policy, permissions, network target, or secret-handling changes;
- output format and nondeterministic-field changes;
- renamed files, packages, services, paths, or environment variables; and
- product workflow changes that invalidate the example's scenario.

This connects directly to the report on
[freshness, staleness, and change impact](07-freshness-staleness-and-change-impact.md).
Age alone is not the signal; dependency change and failed re-execution are.

## Automation and human judgment

### Strong candidates for deterministic checks

Tools can usefully:

- find and classify fenced blocks, while allowing explicit exceptions;
- require or infer a declared language where a parser depends on it;
- detect malformed fences, tabs, prompts, and input/output ambiguity under decided
  formatting rules;
- lint shell and programming-language syntax in a declared environment;
- compile and type-check complete examples;
- execute safe examples in disposable environments;
- assert stable output, error, exit-status, and state-change expectations;
- validate sample configuration with the actual parser, schema, or loader;
- compare documented keys, defaults, enums, deprecations, and help text with canonical
  structured sources;
- scan examples for secret patterns, live hostnames, prohibited privileges, and known
  dangerous command forms;
- detect unexpanded placeholders and undocumented environment assumptions encoded in a
  harness; and
- map product changes to the samples and configuration facts they can invalidate.

The output must name what actually ran and what it proves. A lint pass should not be
reported as execution, and a test skipped because its environment was unavailable should
not be reported as a tested example.

### Human review remains necessary for

- deciding the artifact's real class and reader promise;
- selecting scenarios that represent audience goals;
- judging whether omissions create a false or unsafe mental model;
- evaluating copy risk, privilege, blast radius, and recovery;
- deciding whether an example is idiomatic and supportable rather than merely accepted;
- determining whether variable output is represented honestly;
- reconciling code truth with product intent and operational policy;
- deciding whether the chosen validation level is proportionate;
- testing whether an intended reader can adapt the artifact; and
- reviewing generated output for explanation, navigation, and usefulness.

A secret scanner cannot prove that a placeholder will not be replaced unsafely. A
sandbox pass cannot prove that a production command has the correct target. A compiler
cannot decide that the sample teaches the intended abstraction. Automation should produce
specific observations and review candidates, not an undifferentiated “examples pass.”

## Findings in the current Buzz corpus

### Existing strengths

The corpus already has complementary controls:

- The [procedure template](../../docs/corpus/templates/procedure.md) expects a real
  end-to-end workflow test for a how-to, not merely a source citation.
- The [reference template](../../docs/corpus/templates/reference.md) treats command rows
  and other entries as facts that should cite code, schema, or specification.
- The [configuration template](../../docs/corpus/templates/configuration.md) requires
  variable, type or format, default, required status, secret status, and effect, and
  explicitly says loader code rather than `.env.example` establishes a default.
- The [runbook template](../../docs/corpus/templates/runbook.md) situates commands within
  trigger, diagnosis, mitigation, resolution, and escalation rather than treating them as
  context-free scripts.
- The [code-reference standard](../../docs/corpus/standards/code-references.md) defines
  accepted citation shapes and openly states that path validation does not prove a cited
  line or supporting claim.
- The [test-reference standard](../../docs/corpus/standards/test-references.md)
  distinguishes a test's existence, an observed test run, and a system-behavior claim.

Together these support a future contract. They are distributed by document genre and
evidence type, so a reviewer currently has to compose them.

### No shared code-example form or body-level validation

The template directory has no dedicated `code-example.md` template. This is not
necessarily a missing document type: examples usually belong inside another genre. It
does mean there is no one local place that states the common contract for runnable versus
illustrative code, commands, configuration fragments, placeholders, and expected output.

The corpus validator checks front matter, relationship structure, citation shapes, and
local path existence. It does not inspect the semantic content of document bodies. A
green validation run therefore does not establish that a fenced sample parses, a command
exists, an output matches, a placeholder is safe, or a configuration row agrees with
runtime behavior.

The local code-reference standard makes the evidence boundary explicit: a bare path can
be resolved, while a line number is not checked against the file and the validator does
not decide whether the cited content supports the statement. The test-reference standard
likewise records tool-result citations as unverified by the validator. A future example
check must report its own execution evidence rather than inheriting credibility from
these citation checks.

### Executable-looking content is broader than fenced shell code

A fence-aware lexical scan of the 205 current Markdown nodes outside `schema/` found 53
nodes containing 69 fenced blocks. The parser classified 14 as `bash`, 3 as Rust, 1 as
Python, 1 as text, 7 as unlabeled, and the remainder primarily as Mermaid or Markdown
template material. One apparent language label came from prose demonstrating nested fence
syntax, so these figures are discovery counts, not a semantic inventory.

An exact line scan found 13 literal ```` ```bash ```` opening lines, which differs from the
fence parser because templates and nested fences complicate Markdown interpretation.
Inline commands and configuration table values are more numerous and are not represented
by either count. The practical finding is that a fence scan can route candidate content
to checkers, but it cannot define the review population or determine which blocks promise
execution.

### Configuration guidance is detailed but not yet an executable source of truth

Eight nodes declare that they implement the configuration template: agent, desktop,
environment, feature flags, mobile, relay, secrets, and validation configuration. All
eight currently have `status: draft`. The relay configuration node is notably detailed:
it distinguishes the `Config::from_env()` surface, types and defaults, required and secret
status, effects, restart behavior, validation failures, insecure development defaults,
and deprecated or inert values. It also records environment variables outside that
specific loader as a boundary.

Those are strong review dimensions. The tables remain hand-authored Markdown facts; the
corpus validator does not compare them with the Rust loader. Their detail should not be
mistaken for mechanical synchronization, and their draft status should not be mistaken
for an adopted, reviewed configuration reference set.

### The principal local gap

Buzz can currently answer pieces of the question:

- a procedure says the whole workflow should be exercised;
- a configuration row should cite its loader;
- a test reference can report a run;
- a code citation can point to source; and
- the evidence model can qualify a claim.

It cannot yet answer, uniformly and mechanically or editorially, **what this particular
artifact claims, which environment and assurance level were checked, which result is the
oracle, whether copying is safe, and which implementation change should invalidate it**.
That common record is the main contribution this topic should make to the later
synthesis.

## Candidate checklist criteria

These are research outputs for later synthesis, not approved requirements.

For each material example, command, code sample, configuration fragment, or output block,
a reviewer could ask:

- [ ] Is its class explicit: pseudocode, fragment, runnable example, command synopsis,
      literal invocation, configuration example, reference fact, expected output, or
      transcript?
- [ ] Does it serve a named reader goal or scenario rather than existing as decorative
      illustration?
- [ ] Is the claimed environment clear enough: version, platform, shell, working
      directory, dependencies, services, permissions, target, and starting state as
      applicable?
- [ ] Can the reader distinguish literal input, prompts, placeholders, omitted code,
      commentary, stdout, and stderr?
- [ ] Are placeholders descriptive, explained, syntactically safe, and visibly not real
      secrets, hosts, IDs, or paths?
- [ ] Are omissions marked with the target language's comment syntax, and do they avoid
      concealing required correctness or security work?
- [ ] Is the highest completed validation level named accurately: rendered, parsed or
      linted, built, executed, behavior-asserted, integration-exercised, or reader-tested?
- [ ] Was the artifact checked in an environment representative of the one claimed, or
      is the difference explicit?
- [ ] Does an observable oracle establish the promised outcome rather than only absence
      of an error?
- [ ] Are expected output, exit state, errors, and variable fields labeled exact or
      illustrative and represented without sensitive data?
- [ ] Does the command identify its target, privilege, side effects, idempotence,
      irreversible point, and cleanup or recovery in proportion to risk?
- [ ] Does a code sample use supported, idiomatic, secure interfaces and identify
      dependencies, imports, and versions that are not otherwise fixed?
- [ ] Does a configuration fact distinguish actual default, example value, and contextual
      recommendation?
- [ ] Does each material configuration setting document its type or syntax, units and
      constraints, required and secret status, precedence, validation and failure
      behavior, reload or restart semantics, interactions, deprecation, and environment
      scope where applicable?
- [ ] Has a sample configuration been validated as a coherent whole, not just as
      individually plausible values?
- [ ] Is the artifact traceable to its authoritative code, parser, schema, CLI help,
      test, or specification and the revision checked?
- [ ] Is there a defined change trigger or dependency path that causes revalidation?
- [ ] If generated or extracted, has a human reviewed scenario selection, explanation,
      safety, and readability?
- [ ] Does the wording avoid claiming a stronger assurance level than the recorded
      evidence establishes?
- [ ] For high-value or high-risk tasks, has an intended reader successfully selected,
      adapted, executed, interpreted, and recovered using the content?

## Measures that could support later review

No single count measures example quality. Useful evidence could include:

- artifacts inventoried by class, risk, owner, and claimed environment;
- percentage of runnable artifacts with an automated build or execution check;
- percentage with a behavioral oracle rather than only successful exit;
- configuration keys and defaults matched to the canonical loader or schema;
- unclassified fences and command-shaped inline content awaiting review;
- stale or failing examples after API, CLI, configuration, or dependency changes;
- examples skipped, ignored, or validated below their declared level;
- unsafe-command and possible-secret findings resolved by risk;
- time from implementation change to affected-sample revalidation;
- copy, execution, adaptation, and interpretation failures in representative reader
  tasks; and
- incident, support, and onboarding defects caused by incorrect examples or configuration.

Denominators must be explicit. “Ninety percent tested” is meaningless unless “tested”
names an assurance level and the population states whether it includes pseudocode,
commands, tables, and inline examples.

## Common failure modes

- **Fence equivalence:** treating every fenced block as runnable, or every unfenced
  command as non-executable.
- **Syntax-as-correctness:** reporting a parse, lint, or compile pass as proof of the
  claimed behavior.
- **No-oracle execution:** running a sample without asserting its result.
- **Hidden context:** omitting shell, directory, version, credentials, target, or starting
  state that determines behavior.
- **Synopsis copy trap:** placing optional-argument grammar in a block presented for
  literal copying.
- **Prompt/output ambiguity:** making it unclear which lines the reader should enter.
- **Plausible placeholder:** using a value that appears real and may be run unchanged.
- **Ellipsis damage:** using `...` where it is unclear whether code, output, list items,
  or literal syntax were removed.
- **Happy-path sample:** omitting errors, cleanup, rollback, or partial completion where
  the risk requires them.
- **Minimality as excuse:** hiding security, resource management, or correctness
  obligations behind an unlabeled simplified example.
- **Production theatre:** drowning a teaching point in framework scaffolding and calling
  the result more realistic.
- **Example/default collapse:** documenting the value in `.env.example` as the actual
  loader default.
- **Schema-default assumption:** assuming a documented schema `default` is applied at
  runtime.
- **Row-wise configuration validation:** checking each value's syntax while ignoring an
  incoherent or unsafe combination.
- **Secure-looking sample:** avoiding a literal secret while still teaching excessive
  privilege, an insecure endpoint, or unsafe storage.
- **Golden-output brittleness:** asserting timestamps, ordering, paths, colors, or other
  incidental output and creating noisy failures.
- **Generated-truth fallacy:** assuming source-generated reference text is useful,
  complete, and aligned with product intent because it cannot drift lexically.
- **Duplicate-source drift:** maintaining independent documentation, test, and sample
  bodies with no comparison or common change trigger.
- **Validation laundering:** treating a green corpus-structure check or existing test file
  as evidence that a sample was executed.

## Competing positions and reconciliations

### “Every example must execute” versus “some examples are explanatory”

Execution catches real defects and makes drift visible. Pseudocode, partial patterns,
failure illustrations, and consequential operational commands may not be safely or
meaningfully executable. Classify the artifact, test to the highest safe proportionate
level, and make non-executable status explicit. Do not leave runnable appearance with an
illustrative contract.

### “Keep examples minimal” versus “show production-quality code”

Minimal examples help readers isolate a concept; complete examples prevent unsafe or
misleading reuse. Preserve the correctness and security boundary, mark omissions at the
point of inference, and link a complete tested form when the fragment is not itself a
safe adaptation base.

### “Generate docs from source” versus “write for the reader”

Generation is strong for exact enumerable facts with one canonical representation.
Reader goals, scenario selection, warnings, rationale, and configuration tradeoffs do not
fall out of a parser. Generate or include the facts most vulnerable to mechanical drift;
author and review the task model around them.

### “Pin every version” versus “keep examples durable”

Pinning creates reproducibility but can teach obsolete versions and increase maintenance.
Unbounded “latest” can make the same instructions produce different results. Pin when
behavior, supply chain, output, or compatibility depends on it; otherwise declare a
supported range or test against the project's canonical lockfile and state that contract.

### “Snapshot exact output” versus “show representative output”

Exact assertions detect interface changes but become brittle around incidental data.
Representative output is durable but can hide breaking changes. Assert the stable
semantic interface exactly and mark variable or omitted fields explicitly. If exact text
is a public interface, version and test it as such.

### “Static safety rules can block dangerous commands” versus “context determines risk”

Patterns can find obvious secrets, recursive deletion, privilege escalation, or live
targets. The same command can be safe in a disposable directory and catastrophic at a
broader unresolved target. Static checks should block decided invariants and route the
rest to contextual review; they cannot replace target resolution and execution judgment.

## Claim ledger

| Claim | Support | Counterevidence or boundary | Confidence |
|---|---|---|---|
| Executable content needs an explicit class before evidence can be judged. | Google command-syntax distinction; Rustdoc modes; local genre-specific rules | Some one-line examples are unambiguous from their enclosing context | High |
| Parse, compile, execute, and behavior assertion are distinct assurance levels. | Rustdoc behavior and annotations; executable-example research; local test-reference distinctions | Particular tools may combine several levels in one invocation | High |
| Examples need declared environmental and starting-state context. | Google command guidance; Rustdoc working-directory caveat; Microsoft prerequisites guidance | Context may be inherited once from a clear document-level contract | High |
| Expected output or another observable oracle is needed to establish claimed behavior. | Microsoft code-example guidance; Rustdoc assertion guidance; executable-example research | Some examples exist only to demonstrate syntax or shape and should claim no behavior | High |
| Scenario match and intent are part of example usefulness. | Robillard and DeLine field study; Microsoft task-selection guidance | The empirical study concerns API learning, not every Buzz document genre | Medium-high |
| Configuration defaults must be verified against runtime authority, not inferred from an example or schema annotation. | JSON Schema annotation semantics; local configuration template and loader boundary | A project can deliberately generate and consume one schema as runtime authority | High |
| Safety includes defaults, secrets, privilege, targets, side effects, and recovery. | OWASP secure-by-default guidance; Google copy guidance; RFC example namespaces; local procedure research | Exact controls must remain proportional to the command and environment | High |
| Generated or extracted examples reduce some drift but do not guarantee usefulness or semantic completeness. | Limits of executable examples; distinction between source facts and reader scenarios | In narrow reference surfaces, generation may cover nearly the entire need | High |
| Buzz's corpus validator does not establish body-example correctness. | Local validator and code/test-reference standards | Separate repository CI may happen to exercise some examples without the corpus validator knowing | High |
| Buzz has no single shared executable-content contract. | Local template and standard inspection | Relevant rules already exist in several genre-specific documents and can be composed manually | Medium-high |
| The current configuration corpus is detailed but not mechanically synchronized or adopted as final. | Eight draft template implementations; local validator boundary; relay configuration inspection | Individual authors may have manually verified every row; this research did not retest them | High |

## Implications for the later corpus checklist

This topic should contribute six separable concerns:

1. **Artifact contract:** what the example is and what it promises.
2. **Reproducibility:** environment, state, dependencies, substitutions, and target.
3. **Assurance:** the exact level of parsing, building, execution, behavioral assertion,
   integration, or reader testing completed.
4. **Safety:** privilege, secrets, side effects, blast radius, failure, and recovery.
5. **Configuration truth:** runtime defaults, precedence, constraints, lifecycle, and
   secure environmental guidance.
6. **Maintenance:** canonical source, ownership, affected-by relationships, and
   revalidation triggers.

These concerns should not become a demand for identical metadata on every inline token.
The later synthesis should define risk tiers and allow document-level context where it is
unambiguous. The common review chain can remain stable while the required depth varies.

The topic connects to [truth and evidence](03-truth-and-evidence-in-living-technical-documentation.md),
[freshness and change impact](07-freshness-staleness-and-change-impact.md),
[procedures and operational documentation](08-reviewing-procedural-and-operational-documentation.md),
and [normative versus descriptive writing](09-normative-versus-descriptive-technical-writing.md).
A sample's test result is evidence, its dependency mapping governs freshness, its
placement in a workflow governs task success, and words such as “must,” “default,” and
“supported” determine the strength of its promise.

## Limitations and open questions

- No current Buzz sample or command was executed as part of this topic.
- Fence counts are lexical observations affected by nested Markdown and cannot classify
  intent or enumerate inline commands and configuration facts.
- The research did not inspect all eight configuration nodes row by row or compare them
  programmatically with every loader path.
- The empirical evidence is concentrated on API documentation and does not quantify the
  value of these controls for Buzz's operational or architectural material.
- Vendor style guides reflect their publishers' authoring environments and are not a
  universal standard.
- No reader study tested whether Buzz contributors can copy, adapt, or diagnose using the
  current examples.
- The right balance among embedded snippets, included files, generated reference, and
  hand-authored material remains a design decision.
- A safe automated environment for integration examples and consequential commands has
  not been designed.
- Risk tiers, required assurance levels, exception handling, ownership, and revalidation
  cadence remain unresolved.
- It is not yet known whether executable-content metadata belongs in prose, a sidecar,
  test manifests, front matter, or generated reports.

Questions for synthesis:

1. Which artifact classes and risk tiers should the corpus formally recognize?
2. What minimum assurance level applies to tutorials, procedures, runbooks, reference
   entries, and illustrative explanation?
3. How should an author declare a non-runnable fragment or a deliberately skipped
   execution check?
4. Which existing examples can be extracted into tests or generated from canonical
   sources without reducing readability?
5. What is the authoritative source for each configuration surface, and can it emit a
   machine-readable inventory?
6. How will execution evidence record version, environment, skipped checks, expected
   output, and revision without overwhelming readers?
7. Which command-safety findings are deterministic enough to block, and which require a
   reviewer?
8. Which product changes should automatically identify affected examples and
   configuration rows?
9. What representative reader tasks will validate copy, adaptation, interpretation, and
   recovery?

## Sources

Primary and authoritative guidance:

- [Google developer documentation style guide: Code samples](https://developers.google.com/style/code-samples)
- [Google developer documentation style guide: Command-line syntax](https://developers.google.com/style/code-syntax)
- [Google developer documentation style guide: Placeholders](https://developers.google.com/style/placeholders)
- [Microsoft Writing Style Guide: Code examples](https://learn.microsoft.com/en-us/style-guide/developer-content/code-examples)
- [The rustdoc book: Documentation tests](https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html)
- [JSON Schema: Annotations including `default` and `examples`](https://json-schema.org/understanding-json-schema/reference/annotations)
- [OWASP Developer Guide: Secure by Default](https://devguide.owasp.org/en/04-design/02-web-app-checklist/01-secure-by-default/)
- [The Twelve-Factor App: Config](https://www.12factor.net/config)
- [ShellCheck SC2148: Tips depend on target shell](https://www.shellcheck.net/wiki/SC2148)
- [RFC 2606: Reserved Top Level DNS Names](https://www.rfc-editor.org/rfc/rfc2606)
- [RFC 5737: IPv4 Address Blocks Reserved for Documentation](https://www.rfc-editor.org/rfc/rfc5737)

Research:

- Hoffman and Strooper,
  [“API documentation with executable examples”](https://doi.org/10.1016/S0164-1212(02)00055-9),
  *Journal of Systems and Software* 66(2), 2003.
- Robillard and DeLine,
  [“A Field Study of API Learning Obstacles”](https://doi.org/10.1007/s10664-010-9150-8),
  *Empirical Software Engineering* 16, 2011.

Local evidence:

- [Corpus procedure template](../../docs/corpus/templates/procedure.md)
- [Corpus reference template](../../docs/corpus/templates/reference.md)
- [Corpus configuration template](../../docs/corpus/templates/configuration.md)
- [Corpus runbook template](../../docs/corpus/templates/runbook.md)
- [Corpus implementation-reference template](../../docs/corpus/templates/implementation-reference.md)
- [Corpus code-reference standard](../../docs/corpus/standards/code-references.md)
- [Corpus test-reference standard](../../docs/corpus/standards/test-references.md)
- [Relay configuration node](../../docs/corpus/layers/configuration/relay-configuration.md)
- [Development prerequisites](../../docs/corpus/development/prerequisites.md)
- [Corpus validator](../../project-intelligence/corpus/validate.py)
