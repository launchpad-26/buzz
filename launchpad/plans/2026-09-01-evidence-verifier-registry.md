# Evidence Verifier Registry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the validator’s undifferentiated citation handling with typed evidence parsing and verifier-owned proof results, while keeping unverifiable evidence blocking by default.

**Architecture:** `evidence.py` owns citation parsing into typed evidence objects and verifier dispatch. Each verifier returns a structured result with status and safe detail. `validate.py` remains responsible for corpus traversal, entry-level policy, aggregation, and CLI exit status. CI keeps separate structural and live-link responsibilities; arbitrary shell prose is never executed.

**Tech Stack:** Python 3.12/3.11, `dataclasses`, `urllib.request`, Git subprocesses, `unittest`, existing YAML/JSON Schema dependencies.

## Global Constraints

- No citation value or secret-shaped content may be echoed in diagnostics.
- `PASS` requires proof; recognised-but-unverified evidence remains blocking.
- URL checks are opt-in via `--check-links`; offline mode remains deterministic.
- Only allowlisted structured verifiers may execute; arbitrary `shell(...)`, `curl(...)`, or free-form command prose remains unsupported.
- Existing public validator CLI and corpus formats remain backward compatible during this slice.

---

### Task 1: Define typed evidence and verifier result contracts

**Files:**
- Modify: `launchpad/project-intelligence/corpus/evidence.py`
- Test: `launchpad/project-intelligence/corpus/tests/test_evidence.py`

**Interfaces:**
- Produce `EvidenceKind` values for local path, local position, commit, GitHub URL, external URL, graph edge, tool result, and unknown.
- Produce immutable parsed evidence values containing only normalized safe fields.
- Produce `VerificationResult(status, detail)` where status is `ok`, `error`, or `unverified`.

- [ ] Write tests for parsing one representative citation of every supported kind and preserving no raw diagnostic value.
- [ ] Run `python3 -m unittest launchpad/project-intelligence/corpus/tests/test_evidence.py -v`; confirm new tests fail because the contracts do not exist.
- [ ] Implement the enum/dataclasses and parser only; do not execute commands or network requests yet.
- [ ] Run the evidence tests and confirm they pass.
- [ ] Commit: `refactor: type corpus evidence citations`

### Task 2: Move local and commit proof into typed verifiers

**Files:**
- Modify: `launchpad/project-intelligence/corpus/evidence.py`
- Modify: `launchpad/project-intelligence/corpus/validate.py`
- Test: `launchpad/project-intelligence/corpus/tests/test_validate.py`

**Interfaces:**
- `verify_evidence(parsed, repo_root, check_links=False) -> VerificationResult`.
- Local path/line/range verification checks containment, file existence, and line bounds.
- Commit verification uses `git cat-file -e <sha>^{commit}` with suppressed output.

- [ ] Write failing tests for existing/missing commits and valid/out-of-range local positions through the public citation path.
- [ ] Run the targeted tests and confirm expected failures.
- [ ] Implement the verifier dispatch and route existing validation through it.
- [ ] Run the targeted tests and confirm they pass.
- [ ] Commit: `refactor: verify local corpus evidence by kind`

### Task 3: Add safe URL verifier dispatch

**Files:**
- Modify: `launchpad/project-intelligence/corpus/evidence.py`
- Modify: `launchpad/project-intelligence/corpus/validate.py`
- Test: `launchpad/project-intelligence/corpus/tests/test_validate.py`

**Interfaces:**
- Offline URL result: `unverified` with detail requiring `--check-links`.
- Link-check URL result: `ok` only for reachable `2xx/3xx`; HTTP errors, timeouts, malformed targets, and transport errors are `error`.
- GitHub file URL additionally requires full SHA, file verb, non-empty path, and reachable target in link-check mode.

- [ ] Write failing tests with the existing local HTTP fixture for reachable, missing, and metadata-suffixed URLs.
- [ ] Run targeted tests and confirm failures.
- [ ] Implement URL verifier dispatch with bounded HEAD/GET requests and no response-body logging.
- [ ] Run targeted tests and confirm they pass.
- [ ] Commit: `feat: verify corpus URLs in link-check mode`

### Task 4: Add narrow structured tool-result and graph verifier hooks

**Files:**
- Modify: `launchpad/project-intelligence/corpus/evidence.py`
- Modify: `launchpad/project-intelligence/corpus/validate.py`
- Test: `launchpad/project-intelligence/corpus/tests/test_validate.py`

**Interfaces:**
- Existing prose tool-result/graph citations remain `unverified` and blocking.
- Add structured verifier hooks only for explicitly supported future forms; unsupported command prose must return `unverified`, never execute.
- No `shell`, `curl`, or arbitrary subprocess execution from citation text.

- [ ] Write tests proving unsupported tool-result and graph citations are classified as blocking unverified with actionable verifier-kind detail.
- [ ] Run tests and confirm failures.
- [ ] Implement the allowlist boundary without adding replay behavior yet.
- [ ] Run tests and confirm they pass.
- [ ] Commit: `refactor: isolate unsupported evidence verifiers`

### Task 5: Integrate CI job boundaries and full verification

**Files:**
- Modify: `.github/workflows/launchpad-corpus-validate.yml`
- Modify: `launchpad/project-intelligence/corpus/validate.py`
- Test: `launchpad/project-intelligence/corpus/tests/`

- [ ] Add a structural validation step using offline mode.
- [ ] Keep a separate `--check-links` step for live URL verification.
- [ ] Run the full corpus test suite.
- [ ] Run offline validation and record blocking unsupported evidence.
- [ ] Run link-check validation and record remaining blocking unsupported evidence/dead links.
- [ ] Commit: `ci: separate corpus structure and link validation`
