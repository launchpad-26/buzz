# P-10 Remediation — code-level contract

This is the implementation contract for one part of the design in
[`../architecture.md`](../architecture.md). An agent implementing P-10 builds exactly what is here;
an agent implementing a neighbour calls exactly what is here. Contract ids (`E-NN`) and record names
are those of [`../components.md`](../components.md) §6 and [`../container.md`](../container.md) §5.

**Responsibility, in one sentence.** Given an exact mechanical remedy, a pinned snapshot and a live
grant, validate the target, apply it to exact files in an isolated worktree, mechanically prove the
actual diff behavior-equivalent and in scope, and push one commit only to that PR head branch.

**Depends on.** ADR-G ([#2160](https://github.com/launchpad-26/buzz/issues/2160), assumed). P-10,
not P-02, enforces fork policy because E-10 receives the pinned snapshot.

## 1. Modules

```
rqa/remediation/
  __init__.py     re-exports: remediate and shared remediation outcomes, MECHANICAL_TOOL_SET,
                  ToolSpec, RemediationError
  tools.py        closed formatter registry, exact argv builder and behavior-equivalence oracles
  worktree.py     isolated exact-head checkout, target confinement and unconditional cleanup
  push.py         validated PR-head refspec builder (never force, never another ref)
  remediate.py    E-10 orchestration
```

P-10 imports cross-part values only from `rqa.contracts`, including `Snapshot`; it imports no path
matcher because remedies name exact files, not patterns. It never imports another part's
implementation or reads live configuration.

## 2. Types

All cross-part values are defined only in [`CONTRACTS.md`](CONTRACTS.md): `Job` in §1; `Finding` and
`Remedy` in §2; `Snapshot` in §3; `Facts` in §4; `RemediationRefusalReason`,
`RemediationPushed`, and `RemediationRefused` in §6; and `Grant`, `Activity`, `RecordWriter`,
`AppendFailed`, `ProcessRunner`, and `ProcessResult` in §§7–9. P-10 imports them unchanged.

```python
# tools.py — private registry metadata. A tool without a sound equivalence oracle is not registered.
@dataclass(frozen=True)
class ToolSpec:
    id: str
    fix_argv: tuple[str, ...]        # exact validated file paths appended
    check_id: str                    # must equal Remedy.check
    check_argv: tuple[str, ...]      # exact validated file paths appended
    extensions: frozenset[str]
    equivalence_id: str              # names one closed semantic_fingerprint implementation
    neutrality_contract: str

MECHANICAL_TOOL_SET: Mapping[str, ToolSpec]

def build_argv(*, prefix: tuple[str, ...], paths: tuple[str, ...]) -> tuple[str, ...]:
    """Append only paths already accepted by validate_remedy_paths."""

def validate_remedy_paths(*, remedy: Remedy, facts: Facts, finding: Finding) -> bool:
    """Exact, unique normalized changed files; known bytes; location included; tool/check/extensions match."""

def semantic_fingerprint(*, oracle: str, path: str, content: bytes) -> bytes | None:
    """Parser-derived behavior fingerprint; None on parse/unsupported/error."""

class RemediationError(Exception):
    """Programming error: E-10 received a wrong grant or internally inconsistent facts."""
```

`remediate()` uses the job's managed repo and immutable PR-head target, the exact remedy, the
captured facts, the pinned snapshot, and the grant. `remedy.paths` is both the complete tool argument
list and exact permitted diff set. `remedy.check` must equal the registry's `check_id`.

P-10 returns `FORK_NOT_ALLOWED` itself when `job.head_repo != job.repo` and
`snapshot.policy.remediation.allow_forks is False`; no caller-side inference substitutes for this
check.

## 3. Entry point — E-10

P-10 provides this signature verbatim from [`CONTRACTS.md`](CONTRACTS.md) §9:

```python
def remediate(*, job: Job, finding: Finding, grant: Grant, facts: Facts, snapshot: Snapshot,
              state_dir: Path, runner: ProcessRunner, record: RecordWriter) -> RemediationPushed | RemediationRefused: ...
```

Every value outcome records exactly one `action` entry. From worktree creation onward, clean-up is in
`finally`, so it precedes a propagating `AppendFailed`. Every decision branch below returns a value or
raises the named `RemediationError`; no branch falls through.

1. Before record/worktree action require `grant.activity is REMEDIATE`, `grant.repo == job.repo`,
   `grant.job_id == job.id`, `grant.snapshot_hash == snapshot.hash`, and
   `grant.categories == finding.categories`. Also require every Facts identity/ref/head field match
   `job`. Any mismatch raises `RemediationError`.
2. Missing remedy → `REMEDY_MISSING`; unknown tool → `TOOL_NOT_IN_SET`; mismatched
   `remedy.check` → `CHECK_NOT_IN_SET`.
3. A fork head with `snapshot.policy.remediation.allow_forks is False` → `FORK_NOT_ALLOWED`.
   Protected head → `HEAD_PROTECTED`. Each refuses before worktree creation.
4. Validate every remedy path before worktree creation: normalized exact repo-relative syntax, unique,
   no glob metacharacter, present in both `facts.changed_paths` and `facts.files`, suffix accepted by
   the selected tool, and including `finding.location.path`. Failure → `INVALID_PATH`.
5. Create fresh `state_dir/worktrees/<job.id>/`; remove but never reuse a crashed predecessor. Fetch
   only `job.head_sha` from `job.head_repo`, verify the resolved SHA, and check out detached. Failure
   → `NO_HEAD`.
6. Before any formatter invocation, resolve each checked-out target with `strict=True`; require a
   regular non-symlink file under the resolved worktree root. Capture its bytes and semantic
   fingerprint. Escape, symlink, missing file or unavailable fingerprint → `INVALID_PATH`.
7. Run the exact scoped fix argv. Missing binary → `TOOL_UNAVAILABLE`; non-zero → `TOOL_FAILED`.
8. Read `git diff --name-only -z`. Command failure, malformed output, or changed set not a subset of
   `set(remedy.paths)` → `SCOPE_EXCEEDED`. Exact set membership is used; no glob matcher exists here.
9. For every changed file, compute the registered semantic fingerprint after the fix and require
   byte equality with its captured pre-fix fingerprint. Any unavailable or different fingerprint →
   `BEHAVIOUR_CHANGED`.
10. Run the exact registered check argv. Non-zero → `CHECK_STILL_FAILING`.
11. Run the same fix argv again and require an empty diff against the post-step-9 tree; otherwise
    `NOT_FIXPOINT`. Re-run fingerprint/scope checks over any observed change before refusing.
12. Commit with fixed RQA identity and a message naming finding/tool. Commit failure →
    `COMMIT_FAILED`.
13. Validate `job.head_ref` with `git check-ref-format --branch`; reject empty, invalid or
    `rqa/`-prefixed values. Push only
    `HEAD:refs/heads/{job.head_ref}` to the HTTPS remote derived from `job.head_repo`. Never force or
    retry with force. Failure → `PUSH_REJECTED`.
14. Resolve new HEAD, clean unconditionally, append one pushed `action`, and return
    `RemediationPushed`. Every refusal also cleans, appends one named action and returns.

## 4. Dependencies consumed

**E-20 (git smart HTTP), owned by P-10.** `fetch_head()` builds a remote from `job.head_repo`, fetches
only `job.head_sha`, and never uses `job.head_ref` as a fetch fallback. `push_head()` is the only
function that builds `git push` argv:

```python
def push_head(*, runner: ProcessRunner, worktree: Path, head_repo: str, head_ref: str) -> ProcessResult: ...
```

It validates `head_ref` first, builds the HTTPS remote from `head_repo`, and constructs only
`HEAD:refs/heads/{head_ref}`. `--force` cannot be passed or constructed.

**E-26 (local processes), owned by P-10.** P-10 consumes the canonical `ProcessRunner.run` and
`ProcessResult` from [`CONTRACTS.md`](CONTRACTS.md) §8 unchanged; it declares no local substitute.

Formatter/check invocations contain exactly the prevalidated `remedy.paths`, never `.`. P-10 calls
no path matcher. `FileNotFoundError` maps to `TOOL_UNAVAILABLE`; E-13 appends the terminal action.

**Closed formatter registry.**

| id | extensions | fix/check | equivalence oracle |
|---|---|---|---|
| `ruff-format` | `.py`, `.pyi` | `ruff format` / `ruff format --check` | `python_ast_v1` |
| `prettier` | `.js`, `.jsx`, `.ts`, `.tsx` | `prettier --write` / `prettier --check` | `typescript_estree_v1` |
| `gofmt` | `.go` | `gofmt -w` / empty `gofmt -d` | `go_ast_v1` |
| `rustfmt` | `.rs` | `rustfmt` / `rustfmt --check` | `rust_syn_v1` |
| `dart-format` | `.dart` | `dart format` / `dart format --output=none --set-exit-if-changed` | `dart_analyzer_v1` |

Each oracle rejects parse errors and hashes a normalized compiler/parser AST with source positions
removed while retaining literal values, directives, ordered comments/doc attributes and macro token
trees. Any unsupported construct refuses remediation. Import sorting/fixing is absent. Policy can
remove registry entries but cannot add tools or weaken an oracle.

## 5. Store

P-10 owns no queryable store. Its only local state is `state/worktrees/<job.id>/`, created for a
single E-10 call and removed on every exit after step 5. The durable result is the `action` record
entry, not the worktree.

## 6. Record entries written

| kind | when | payload |
|---|---|---|
| `action` | every value outcome from E-10 | `finding_id`, `tool_id` (when a remedy exists), `decision: "pushed" \| "refused"`, `reason` (for refusal), `detail`, and `new_head_sha` (only for pushed) |

P-10 writes no `transition` and never changes job status.

## 7. What it does not do

- Does not decide candidate eligibility or mutation authority; P-07/P-08 do. It does independently
  enforce fork policy, protected-head facts, exact target paths and semantic equivalence.
- Does not push the base repository for a fork: fetch/push target `job.head_repo` and only its
  validated `job.head_ref`.
- Does not call a path matcher, modify the operator checkout, merge, force-push, read live policy,
  retain a worktree, or decide re-review.

## 8. Tests that prove it

Each is a unit test with fakes for `RecordWriter` and `ProcessRunner`; the runner records every
`(cwd, argv, timeout)` and can raise `FileNotFoundError`.

| # | Given | Then |
|---|---|---|
| T1 | grant differs on activity/repo/job/snapshot or complete finding-category set, or Facts differs from Job | `RemediationError`; no record/worktree |
| T2 | missing remedy, unknown tool, or mismatched check id | corresponding named refusal before worktree |
| T3 | fork disallowed by pinned snapshot | `FORK_NOT_ALLOWED`; no worktree/runner |
| T4 | protected fork or same-repo head | `HEAD_PROTECTED`; no worktree/runner |
| T5 | remedy path has traversal, absolute/glob/backslash syntax, duplicate, unknown/unchanged file, unsupported suffix, or omits finding location | `INVALID_PATH` before worktree |
| T6 | fetched SHA differs or checkout fails | `NO_HEAD`; target remote is `job.head_repo` |
| T7 | checked-out target is missing, symlink, non-file, escapes root, or cannot be fingerprinted | `INVALID_PATH` before formatter |
| T8 | missing formatter or failed fix | `TOOL_UNAVAILABLE` / `TOOL_FAILED`; clean; no push |
| T9 | NUL-delimited diff contains any file outside exact remedy set | `SCOPE_EXCEEDED`; no pattern matching |
| T10 | before/after semantic fingerprint differs or cannot be produced | `BEHAVIOUR_CHANGED`; no commit |
| T11 | check fails or second fix changes tree | `CHECK_STILL_FAILING` / `NOT_FIXPOINT` |
| T12 | fork allowed | remote is exact `job.head_repo`; sole refspec is PR `head_ref` |
| T13 | invalid or `rqa/` head ref | `PUSH_REJECTED` before push |
| T14 | success | pushed result; one action; worktree absent; argv contains exact files and no `.`/force |
| T15 | every registered tool over paired behavior-preserving formatting and adversarial semantic-change fixtures | oracle accepts only the former; registry contains no tool without a passing oracle |
| T16 | terminal append fails | exception propagates after cleanup |

## 9. Requirements this part answers for

Accountable: RQA-BR-006, RQA-FR-017, RQA-NFR-020, RQA-NFR-021. T9, T13, T14, and T16 prove the
scoped-remediation, PR-head-only, isolation, and no-force-push outcomes respectively. P-10 contributes
to RQA-FR-018 by rejecting an out-of-scope diff before it can invalidate unrelated evidence.
