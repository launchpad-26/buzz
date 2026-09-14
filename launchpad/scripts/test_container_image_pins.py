#!/usr/bin/env python3
"""Assert every MinIO image in this repo is pullable by CI, and pinned.

WHY THIS EXISTS. On 2026-09-14 every CI lane that runs `docker compose up`
started failing:

    minio Error pull access denied for minio/minio, repository does not exist
    or may require 'docker login'

MinIO had removed `minio/minio` and `minio/mc` from Docker Hub. Both names now
return `{"message":"object not found"}` from the Hub API. Upstream `block/buzz`
had already moved to quay.io and pinned by digest; this fork had not, so it
inherited a break that upstream no longer had.

Two properties would each have caught it earlier, and this file asserts both:

  1. REGISTRY. A MinIO image must not be requested from Docker Hub, because
     that is where the images stopped existing.
  2. DIGEST PIN. `:latest` cannot fail loudly. It resolves differently on
     different days and silently stops resolving at all; the root compose files
     used it, which is why nothing warned before CI did.

WHY THE NETWORK CHECK IS OPT-IN. The static assertions above are deterministic
and are the ones that would have prevented this. Reachability depends on a
third party being up, so a default-on network probe would make this suite fail
for reasons that are not the repository's fault -- a test that fails for
reasons unrelated to the change is a test people learn to ignore. Run the probe
deliberately:

    CHECK_REGISTRY=1 python3 launchpad/scripts/test_container_image_pins.py

That probe is what verified the fix: an anonymous manifest request (exactly
what a CI runner does, with no `docker login`) returned HTTP 200 from quay.io
for both images with digests matching the pins, while the same request to
Docker Hub returned 401.

Run:  python3 launchpad/scripts/test_container_image_pins.py
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import urllib.request

# Files that name a container image CI or a deployment will actually pull.
# Add to this list rather than assuming a new compose file is covered.
FILES = (
    "docker-compose.yml",
    "docker-compose.harness.yml",
    "deploy/compose/compose.yml",
    "deploy/charts/buzz/values.yaml",
)

IMAGE_RE = re.compile(r"^\s*(?:image|mcImage):\s*(\S+)\s*$", re.M)

# Only MinIO is asserted here. Scope is deliberate: this file records a specific
# outage with specific evidence, and a blanket "everything must be digest
# pinned" rule is a policy change for an ADR, not a check to smuggle in with a
# bug fix. Widen it when the cohort decides to.
MINIO_RE = re.compile(r"(^|/)minio/(minio|mc)\b")

failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{' — ' + detail if detail else ''}")
    if not ok:
        failures.append(name)


def repo_root() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def minio_images() -> list[tuple[str, str]]:
    """(file, image-reference) for every MinIO image named in FILES."""
    found = []
    for rel in FILES:
        path = os.path.join(repo_root(), rel)
        if not os.path.exists(path):
            failures.append(f"{rel} is missing")
            print(f"  FAIL  {rel} is missing — FILES is out of date")
            continue
        text = open(path, encoding="utf-8").read()
        for ref in IMAGE_RE.findall(text):
            if MINIO_RE.search(ref):
                found.append((rel, ref))
    return found


def probe(ref: str) -> tuple[int, str]:
    """Anonymous manifest request — what a CI runner does with no docker login."""
    name, _, rest = ref.partition(":")
    tag = rest.split("@")[0]
    host, _, repo = name.partition("/")
    req = urllib.request.Request(
        f"https://{host}/v2/{repo}/manifests/{tag}",
        headers={
            "Accept": ", ".join([
                "application/vnd.docker.distribution.manifest.v2+json",
                "application/vnd.docker.distribution.manifest.list.v2+json",
                "application/vnd.oci.image.index.v1+json",
            ])
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.headers.get("Docker-Content-Digest", "")
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        return 0, f"{type(exc).__name__}: {exc}"


def main() -> int:
    print("Container image pins\n")
    images = minio_images()
    check("MinIO images found in the tracked compose/chart files",
          bool(images), f"{len(images)} reference(s)")
    if not images:
        print("\nFAILED — no MinIO image found. Either FILES is stale or the")
        print("images moved; both need a human, so this is a failure not a pass.")
        return 1

    for rel, ref in images:
        short = ref.split("@")[0]
        check(f"not Docker Hub — {rel}",
              not ref.startswith("minio/"),
              f"{short} (Docker Hub no longer serves minio/*)")
        check(f"digest pinned — {rel}",
              "@sha256:" in ref,
              short if "@sha256:" in ref else f"{short} has no @sha256: pin")

    if os.environ.get("CHECK_REGISTRY"):
        print("\nRegistry reachability (anonymous, as a CI runner would)")
        for rel, ref in images:
            want = ref.partition("@")[2]
            status, got = probe(ref)
            check(f"anonymously pullable — {ref.split('@')[0]}",
                  status == 200, f"HTTP {status}" if status else got)
            if status == 200 and want:
                check(f"digest matches the pin — {rel}", got == want,
                      f"pinned {want[:19]}…, registry {got[:19]}…")
    else:
        print("\n  (registry reachability skipped — set CHECK_REGISTRY=1 to probe)")

    print()
    if failures:
        print(f"FAILED — {len(failures)} check(s) did not pass:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
