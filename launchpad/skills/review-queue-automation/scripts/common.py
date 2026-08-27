#!/usr/bin/env python3
"""Shared configuration, SQLite state, REST client, and filesystem helpers."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import pathlib
import sqlite3
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

try:
    from errors import JobBlockingError
except ImportError:
    class JobBlockingError(Exception):
        pass

try:
    from errors import StatePersistenceError
except ImportError:
    class StatePersistenceError(Exception):
        pass

SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = pathlib.Path("~/.config/review-queue-automation/config.json").expanduser()


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def expand_path(value: str) -> pathlib.Path:
    return pathlib.Path(os.path.expandvars(os.path.expanduser(value))).resolve()


def load_config(path: str | None = None) -> tuple[dict[str, Any], pathlib.Path]:
    """Load the authoritative config. Accepts BOTH the repo-local shape
    (repository + logging + approval...) and the legacy shape (repos + github),
    normalizing to a single unified form so every entry point consumes one config.

    Returns (normalized_config, config_path).
    """
    config_path = expand_path(path or os.environ.get("REVIEW_QUEUE_CONFIG", str(DEFAULT_CONFIG)))
    if not config_path.is_file():
        raise SystemExit(f"Error: configuration not found: {config_path}")
    with config_path.open(encoding="utf-8") as handle:
        config = json.load(handle)
    return normalize_config(config), config_path


def normalize_config(config: dict[str, Any]) -> dict[str, Any]:
    """Normalize a repo-local or legacy config into the unified runtime shape.

    The unified shape ALWAYS carries a `repos` dict so that downstream consumers
    (evidence, panel, lease) can do `config["repos"].get(repo, {})` without a
    legacy KeyError when the repo-local shape (or an onboarding-generated config
    whose slug is not yet filled) is normalized:

    - If `repository` is present (repo-local shape), synthesize `repos[slug]`
      carrying path/base/preflight/dco from the `repository` block.
    - If `github` is absent, default it (read-only transport settings).

    Validation is intentionally NOT done here; callers validate with
    `config.validate_config` / `load_repo_config` first, so existing config
    validation is never weakened by normalization.
    """
    cfg = dict(config)
    repo_cfg = cfg.get("repository") or {}
    repos = dict(cfg.get("repos") or {})
    slug = repo_cfg.get("slug") or ""
    root = repo_cfg.get("root") or ""
    if slug and root:
        repos.setdefault(
            slug,
            {
                "path": root,
                "base": repo_cfg.get("base", "launchpad"),
                "preflight": repo_cfg.get("preflight", ""),
                "dco": repo_cfg.get("dco", True),
            },
        )
    cfg["repos"] = repos
    cfg.setdefault("state_dir", "~/.config/review-queue-automation")
    cfg.setdefault("github", {"api_version": "2022-11-28", "timeout_seconds": 30, "read_only": True})
    return cfg


def github_token() -> str:
    for name in ("GITHUB_TOKEN", "GH_TOKEN"):
        value = os.environ.get(name, "").strip()
        if value:
            return value
    try:
        result = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, check=True, timeout=10
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise SystemExit("Error: GITHUB_TOKEN/GH_TOKEN is unset and `gh auth token` failed") from exc
    token = result.stdout.strip()
    if not token:
        raise SystemExit("Error: GitHub authentication returned an empty token")
    return token


class State:
    """SQLite-backed durable state: etag/link cache, PR meta, jobs, leases,
    providers, mutations, approval decisions, human requests, canaries."""

    def __init__(self, config: dict[str, Any]):
        self.root = expand_path(config["state_dir"])
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "jobs").mkdir(exist_ok=True)
        self.db_path = self.root / "state.sqlite3"
        try:
            self.db = sqlite3.connect(self.db_path, timeout=30)
            self.db.row_factory = sqlite3.Row
            self.db.execute("PRAGMA journal_mode=WAL")
            self.db.execute("PRAGMA foreign_keys=ON")
            self._migrate()
        except (sqlite3.Error, OSError) as exc:
            raise StatePersistenceError(
                f"SQLite state persistence did not open cleanly at {self.db_path}: {exc}"
            ) from exc

    def execute(self, sql: str, params: tuple = ()) -> Any:
        """Run a SQL statement through the typed persistence path.

        SQLite failures become StatePersistenceError instead of a raw
        sqlite3.Error so callers can dispose of them deterministically.
        """
        try:
            return self.db.execute(sql, params)
        except sqlite3.Error as exc:
            raise StatePersistenceError(f"state persistence failed on state.sqlite3: {exc}") from exc

    def _commit(self) -> None:
        try:
            self.db.commit()
        except sqlite3.Error as exc:
            raise StatePersistenceError(f"state persistence commit failed on state.sqlite3: {exc}") from exc

    def _migrate(self) -> None:
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS etags (
              url TEXT PRIMARY KEY,
              etag TEXT NOT NULL,
              body TEXT NOT NULL,
              link TEXT,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS api_calls (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              called_at TEXT NOT NULL,
              transport TEXT NOT NULL,
              operation TEXT NOT NULL,
              status INTEGER NOT NULL,
              cost INTEGER,
              remaining INTEGER,
              reset_at TEXT
            );
            CREATE TABLE IF NOT EXISTS prs (
              repo TEXT NOT NULL,
              number INTEGER NOT NULL,
              head_sha TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              payload TEXT NOT NULL,
              open INTEGER NOT NULL DEFAULT 1,
              last_seen TEXT NOT NULL,
              PRIMARY KEY (repo, number)
            );
            CREATE TABLE IF NOT EXISTS jobs (
              id TEXT PRIMARY KEY,
              repo TEXT NOT NULL,
              number INTEGER NOT NULL,
              head_sha TEXT NOT NULL,
              lane TEXT NOT NULL,
              status TEXT NOT NULL,
              reason TEXT,
              assurance TEXT,
              artifact_dir TEXT NOT NULL,
              retries INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              UNIQUE (repo, number, head_sha, lane)
            );
            CREATE TABLE IF NOT EXISTS leases (
              repo TEXT NOT NULL,
              number INTEGER NOT NULL,
              job_id TEXT NOT NULL,
              claimed_at TEXT NOT NULL,
              PRIMARY KEY (repo, number),
              FOREIGN KEY (job_id) REFERENCES jobs(id)
            );
            CREATE TABLE IF NOT EXISTS providers (
              key TEXT PRIMARY KEY,
              unavailable_until TEXT,
              last_error TEXT,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS mutations (
              client_mutation_id TEXT PRIMARY KEY,
              operation TEXT NOT NULL,
              status TEXT NOT NULL,
              response TEXT,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS approval_decisions (
              id TEXT PRIMARY KEY,
              job_id TEXT,
              repo TEXT NOT NULL,
              number INTEGER NOT NULL,
              head_sha TEXT NOT NULL,
              policy_hash TEXT NOT NULL,
              status TEXT NOT NULL,
              mode TEXT NOT NULL,
              risk_score INTEGER NOT NULL,
              created_at TEXT NOT NULL,
              expires_at TEXT,
              UNIQUE (repo, number, head_sha, policy_hash)
            );
            CREATE TABLE IF NOT EXISTS human_requests (
              request_id TEXT PRIMARY KEY,
              repo TEXT NOT NULL,
              number INTEGER NOT NULL,
              head_sha TEXT NOT NULL,
              policy_hash TEXT NOT NULL,
              job_id TEXT,
              state TEXT NOT NULL,
              created_at TEXT NOT NULL,
              expires_at TEXT,
              summary TEXT,
              assurance TEXT,
              reviewers TEXT,
              risk_score REAL,
              risk_band TEXT,
              protected TEXT,
              failed_gates TEXT,
              ci TEXT,
              findings TEXT,
              recommendation TEXT,
              rationale TEXT,
              action TEXT,
              decision TEXT,
              decision_actor TEXT,
              decided_at TEXT,
              UNIQUE (repo, number, head_sha, policy_hash, job_id)
            );
            CREATE TABLE IF NOT EXISTS canaries (
              lane TEXT PRIMARY KEY,
              status TEXT NOT NULL,
              job_id TEXT,
              updated_at TEXT NOT NULL
            );
            """
        )
        self._commit()

    def close(self) -> None:
        self.db.close()

    def job_dir(self, job_id: str) -> pathlib.Path:
        path = self.root / "jobs" / job_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def current_status(self, job_id: str) -> str | None:
        row = self.execute("SELECT status FROM jobs WHERE id=?", (job_id,)).fetchone()
        return row["status"] if row else None

    def transition(
        self,
        job_id: str,
        target: str,
        *,
        reason: str | None = None,
        logger=None,
        phase: str = "state",
    ) -> tuple[str | None, str]:
        """Validate and apply a job state transition.

        A job that does not exist is refused before any write or success event.
        An illegal move leaves state unchanged, writes an error event (when a
        logger is present), and raises JobBlockingError.
        """
        prior = self.current_status(job_id)
        if prior is None:
            raise JobBlockingError(
                f"state transition on nonexistent job {job_id} rejected before any write"
            )
        from states import assert_transition

        try:
            assert_transition(prior, target)
        except Exception as exc:
            if logger is not None:
                logger.error(
                    body=f"illegal state transition: {prior} -> {target}",
                    phase=phase,
                    outcome="transition_rejected",
                    attributes={"job.prior_status": prior, "job.status": target, "review.outcome": "transition_rejected"},
                )
            self._commit()
            raise
        self.execute(
            "UPDATE jobs SET status=?, reason=?, updated_at=? WHERE id=?",
            (target, reason, utcnow(), job_id),
        )
        self._commit()
        if logger is not None:
            logger.transition(prior, target, phase=phase, reason=reason)
        return prior, target

    def record_api_call(self, transport: str, operation: str, status: int, headers: Any) -> None:
        def integer(name: str) -> int | None:
            raw = headers.get(name)
            return int(raw) if raw and str(raw).isdigit() else None

        reset = headers.get("x-ratelimit-reset")
        reset_at = None
        if reset and str(reset).isdigit():
            reset_at = dt.datetime.fromtimestamp(int(reset), dt.timezone.utc).isoformat().replace("+00:00", "Z")
        self.execute(
            "INSERT INTO api_calls(called_at,transport,operation,status,cost,remaining,reset_at) VALUES(?,?,?,?,?,?,?)",
            (utcnow(), transport, operation, status, integer("x-ratelimit-used"), integer("x-ratelimit-remaining"), reset_at),
        )
        self._commit()


def atomic_write(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def job_id(repo: str, number: int, head_sha: str, lane: str) -> str:
    digest = hashlib.sha256(f"{repo}#{number}:{head_sha}:{lane}".encode()).hexdigest()[:16]
    return f"{repo.replace('/', '-')}-{number}-{lane}-{digest}"


def mutation_id(job: str, operation: str, discriminator: str = "") -> str:
    digest = hashlib.sha256(f"{job}:{operation}:{discriminator}".encode()).hexdigest()[:24]
    return f"rqa-{digest}"


def repo_parts(repo: str) -> tuple[str, str]:
    pieces = repo.split("/", 1)
    if len(pieces) != 2 or not all(pieces):
        raise ValueError(f"invalid repository: {repo}")
    return pieces[0], pieces[1]


class GithubRest:
    """The sole GitHub read transport: authenticated REST GET with ETag caching."""

    def __init__(self, config: dict[str, Any], state: State):
        self.config = config
        self.state = state
        self.token = github_token()
        self.timeout = int(config["github"].get("timeout_seconds", 30))
        self.api_version = config["github"].get("api_version", "2022-11-28")

    def _request(self, url: str, operation: str, etag: str | None) -> tuple[int, Any, str | None, Any]:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": self.api_version,
            "User-Agent": "review-queue-automation",
        }
        if etag:
            headers["If-None-Match"] = etag
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
                status = response.status
                response_headers = response.headers
        except urllib.error.HTTPError as exc:
            status = exc.code
            response_headers = exc.headers
            if status == 304:
                self.state.record_api_call("rest", operation, status, response_headers)
                return status, None, etag, response_headers
            detail = exc.read().decode("utf-8", errors="replace")
            self.state.record_api_call("rest", operation, status, response_headers)
            raise RuntimeError(f"GitHub REST {operation} failed ({status}): {detail}") from exc
        self.state.record_api_call("rest", operation, status, response_headers)
        return status, json.loads(body) if body else None, response_headers.get("ETag"), response_headers

    def get(self, path: str, operation: str, params: dict[str, Any] | None = None, paginate: bool = False) -> Any:
        if not path.startswith("/"):
            raise ValueError("REST paths must begin with /")
        query = urllib.parse.urlencode(params or {}, doseq=True)
        url = f"https://api.github.com{path}" + (f"?{query}" if query else "")
        items: list[Any] = []
        while url:
            cached = self.state.execute("SELECT etag,body FROM etags WHERE url=?", (url,)).fetchone()
            etag = cached["etag"] if cached else None
            status, payload, new_etag, headers = self._request(url, operation, etag)
            if status == 304:
                if not cached:
                    raise RuntimeError(f"GitHub returned 304 without cached body for {url}")
                payload = json.loads(cached["body"])
            elif new_etag:
                link = headers.get("Link", "")
                self.state.execute(
                    "INSERT INTO etags(url,etag,body,link,updated_at) VALUES(?,?,?,?,?) "
                    "ON CONFLICT(url) DO UPDATE SET etag=excluded.etag,body=excluded.body,link=excluded.link,updated_at=excluded.updated_at",
                    (url, new_etag, json.dumps(payload), link, utcnow()),
                )
                self.state._commit()
            if not paginate:
                return payload
            if not isinstance(payload, list):
                raise RuntimeError(f"paginated REST operation {operation} returned a non-list")
            items.extend(payload)
            # Link header is stored with the cached body, not just on the in-flight
            # response: a 304 reuses the ORIGINAL Link so later pages are not lost.
            link = headers.get("Link", "")
            if status == 304:
                # Re-read the pagination link from the cached response if present.
                cached_row = self.state.execute(
                    "SELECT body, link FROM etags WHERE url=?", (url,)
                ).fetchone()
                link = (cached_row["link"] or "") if cached_row else ""
            next_url = None
            for entry in link.split(","):
                if 'rel="next"' in entry:
                    next_url = entry[entry.find("<") + 1 : entry.find(">")]
                    break
            url = next_url
        return items


def nonce_envelope(label: str, value: Any, nonce: str) -> str:
    serialized = value if isinstance(value, str) else json.dumps(value, indent=2, sort_keys=True)
    return f"<<<{label}:{nonce}>>>\n{serialized}\n<<<END:{label}:{nonce}>>>"
