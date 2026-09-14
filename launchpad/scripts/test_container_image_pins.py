#!/usr/bin/env python3
"""Assert every MinIO image this repo pulls comes from a registry CI can reach.

WHY THIS EXISTS. On 2026-09-14 every CI lane running `docker compose up` began
failing with `pull access denied for minio/minio`. MinIO had removed
`minio/minio` and `minio/mc` from Docker Hub — the Hub API returns
`{"message":"object not found"}` for both. Upstream `block/buzz` had already
moved to quay.io and pinned by digest; this fork had not.

WHAT THIS CAN AND CANNOT DO — stated because the first draft overclaimed, and a
cross-model review said so.

It CAN reject a configuration that points at Docker Hub, or that names an image
without a digest. Those are the two properties this fork's configuration was
missing.

It CANNOT prevent this outage class. A vendor deleting a repository is not
something a static check prevents; digest pinning stops tag *content* drifting
under you, it does not keep a registry serving the image. Nor is `:latest`
"silent" at pull time — a failed pull is loud. What `:latest` hides is the
*risk*, before anyone pulls: nothing in the file to review, no pinned identity
to compare, no way to tell a working config from a doomed one by reading it.
That is what this restores, and it is a smaller claim than "cannot happen
again".

THE FIRST DRAFT WAS ALSO WEAKER THAN ITS OWN ASSERTION NAMES, in three ways a
reviewer demonstrated rather than argued:

  * It matched images with a line regex over YAML. `image: "minio/minio:latest"`
    — same value, quoted — was not detected at all, because the quote broke the
    pattern's anchor. Inline comments, renamed keys, flow mappings and anchors
    slipped past too. It parses the YAML now.
  * "not Docker Hub" tested `not ref.startswith("minio/")`, so the explicit form
    `docker.io/minio/minio:latest` PASSED while being exactly what was broken.
    Registries are normalised before comparison now.
  * "digest pinned" tested `"@sha256:" in ref`, so `@sha256:garbage` PASSED. A
    full 64-hex digest is required now.

And it was named `test_*.py` while defining no discoverable test, so
`unittest discover` collected nothing and no workflow invoked it: the check
existed and never ran. It is a TestCase now.

Run either way:
    python3 -m unittest discover -s launchpad/scripts -p 'test_container_*.py'
    python3 launchpad/scripts/test_container_image_pins.py     # readable report

Registry reachability is opt-in, because it depends on a third party being up,
and a suite that fails for reasons unrelated to the change is one people learn
to ignore:
    CHECK_REGISTRY=1 python3 launchpad/scripts/test_container_image_pins.py
"""

from __future__ import annotations

import glob
import os
import re
import subprocess
import sys
import unittest
import urllib.request

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install pyyaml")

# Globs for files that can define an image a runner or deployment will pull.
# DISCOVERED, not hardcoded: the first draft named four paths, so a fifth
# compose file introducing a Docker Hub image would have passed silently.
PATTERNS = (
    "docker-compose*.yml", "docker-compose*.yaml",
    "deploy/**/*.yml", "deploy/**/*.yaml",
)

# Hosts that ARE Docker Hub, however spelled. A reference with no host is also
# Docker Hub — the implicit form that broke.
DOCKER_HUB = {"docker.io", "index.docker.io", "registry-1.docker.io"}

MINIO_REPO_RE = re.compile(r"(?:^|/)minio/(?:minio|mc)$")
DIGEST_RE = re.compile(r"@sha256:[0-9a-f]{64}$")
# DISCOVERY ONLY — deliberately permissive about the digest.
#
# This pattern previously required `@sha256:[0-9a-fA-F]+`, which made
# `quay.io/minio/minio:latest@sha256:garbage` fail to match at all. The
# reference became INVISIBLE rather than failing: discovery was doing double
# duty as validation, so a malformed digest skipped the very assertion meant to
# catch it. Found by mutation, after a review had already caught the same
# shape of defect twice in this file.
#
# Discovery must therefore be looser than every assertion it feeds. Anything
# shaped like an image reference is collected here; whether its digest is
# well-formed is `test_every_image_is_digest_pinned`'s job to decide, loudly.
IMAGE_SHAPE_RE = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._/-]*(?::[\w.-]+)?(?:@[^\s]+)?$"
)
# Fallback for files a YAML parser cannot read — see minio_references().
TEXT_IMAGE_RE = re.compile(
    r"""(?:image|mcImage)\s*:\s*(["']?[A-Za-z0-9][A-Za-z0-9._/:@-]*["']?)""",
    re.I,
)


def repo_root() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def split_ref(ref: str) -> tuple[str, str]:
    """(registry, repository). A reference with no host component is Docker Hub."""
    name = ref.split("@")[0]
    head, sep, tail = name.partition("/")
    if sep and ("." in head or ":" in head or head == "localhost"):
        registry, remainder = head, tail
    else:
        registry, remainder = "docker.io", name
    # Strip a tag from the final path segment only, so a port or a dotted path
    # component is not mistaken for one.
    last = remainder.rsplit("/", 1)[-1]
    if ":" in last:
        remainder = remainder[: len(remainder) - len(last)] + last.rsplit(":", 1)[0]
    return registry, remainder


def walk_strings(node):
    """Every string anywhere in a parsed YAML document."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from walk_strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk_strings(v)


def minio_references() -> list[tuple[str, str]]:
    """(relative path, image reference) for every MinIO image in tracked YAML."""
    root = repo_root()
    found: list[tuple[str, str]] = []
    for pattern in PATTERNS:
        for path in glob.glob(os.path.join(root, pattern), recursive=True):
            rel = os.path.relpath(path, root)
            text = open(path, encoding="utf-8", errors="replace").read()
            try:
                with open(path, encoding="utf-8") as fh:
                    docs = list(yaml.safe_load_all(fh))
            except Exception:  # noqa: BLE001
                # HELM TEMPLATES ARE NOT YAML, and that is not an error.
                # `deploy/charts/**/templates/*.yaml` carry Go template actions
                # (`{{ .Values… }}`), so a YAML parser raises on every one.
                #
                # The first version of this branch treated a parse failure as a
                # finding, which produced 48 failures against files that are
                # correct. Skipping them silently would be the opposite mistake:
                # a template CAN hardcode an image.
                #
                # So parsing degrades to a textual scan for exactly the thing
                # this check is about. Weaker, and applied only where the
                # stronger method cannot run — never as a way to skip a file.
                for m in TEXT_IMAGE_RE.finditer(text):
                    ref = m.group(1).strip("'\"")
                    if MINIO_REPO_RE.search(split_ref(ref)[1]):
                        found.append((rel, ref))
                continue
            for doc in docs:
                for s in walk_strings(doc):
                    s = s.strip()
                    if not IMAGE_SHAPE_RE.match(s):
                        continue
                    if MINIO_REPO_RE.search(split_ref(s)[1]):
                        found.append((rel, s))
    return sorted(set(found))


class MinioImagePins(unittest.TestCase):
    """The two properties this fork's configuration was missing."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.refs = minio_references()

    def test_minio_images_are_found(self) -> None:
        """No references means discovery broke, not that the repo is clean."""
        self.assertTrue(
            self.refs,
            "found no MinIO image in any compose or chart file. Either the "
            "discovery globs are stale or the images moved; both need a human, "
            "so this fails rather than passing silently.",
        )

    def test_no_image_comes_from_docker_hub(self) -> None:
        for rel, ref in self.refs:
            with self.subTest(file=rel, image=ref):
                registry = split_ref(ref)[0]
                self.assertNotIn(
                    registry, DOCKER_HUB,
                    f"{rel}: {ref} resolves to {registry}. Docker Hub no longer "
                    "serves minio/*; use quay.io.",
                )

    def test_every_image_is_digest_pinned(self) -> None:
        for rel, ref in self.refs:
            with self.subTest(file=rel, image=ref):
                self.assertRegex(
                    ref, DIGEST_RE,
                    f"{rel}: {ref} lacks a full @sha256:<64 hex> digest.",
                )


def probe(ref: str) -> tuple[int, str]:
    """Anonymous manifest request — what a runner does with no `docker login`."""
    registry, repo = split_ref(ref)
    last = ref.split("@")[0].rsplit("/", 1)[-1]
    tag = last.rsplit(":", 1)[-1] if ":" in last else "latest"
    req = urllib.request.Request(
        f"https://{registry}/v2/{repo}/manifests/{tag}",
        headers={"Accept": ", ".join([
            "application/vnd.docker.distribution.manifest.v2+json",
            "application/vnd.docker.distribution.manifest.list.v2+json",
            "application/vnd.oci.image.index.v1+json",
        ])},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.headers.get("Docker-Content-Digest", "")
    except Exception as exc:  # noqa: BLE001 — reported, never swallowed
        return 0, f"{type(exc).__name__}: {exc}"


def report() -> int:
    """Human-readable run. Same assertions, plus the opt-in registry probe."""
    refs = minio_references()
    print("Container image pins\n")
    print(f"  {len(refs)} MinIO reference(s) discovered\n")
    for rel, ref in refs:
        registry = split_ref(ref)[0]
        hub = registry in DOCKER_HUB
        pinned = bool(DIGEST_RE.search(ref))
        print(f"  {'FAIL' if hub else 'PASS'}  registry {registry:<10}  {rel}")
        print(f"  {'PASS' if pinned else 'FAIL'}  digest pinned         {ref.split('@')[0]}")

    if os.environ.get("CHECK_REGISTRY"):
        print("\nRegistry reachability (anonymous, as a CI runner would)")
        for _rel, ref in refs:
            want = ref.partition("@")[2]
            status, got = probe(ref)
            ok = status == 200 and (not want or got == want)
            suffix = ""
            if want and status == 200:
                suffix = f", digest {'matches' if got == want else 'MISMATCH'}"
            print(f"  {'PASS' if ok else 'FAIL'}  {ref.split('@')[0]} — "
                  f"HTTP {status or got}{suffix}")
    else:
        print("\n  (registry reachability skipped — set CHECK_REGISTRY=1 to probe)")

    with open(os.devnull, "w") as devnull:
        result = unittest.TextTestRunner(verbosity=0, stream=devnull).run(
            unittest.TestLoader().loadTestsFromTestCase(MinioImagePins)
        )
    print()
    if result.wasSuccessful():
        print("All checks passed.")
        return 0
    print(f"FAILED — {len(result.failures) + len(result.errors)} check(s) did not pass.")
    for case, trace in result.failures + result.errors:
        print(f"  - {case}")
        print(f"    {trace.strip().splitlines()[-1]}")
    return 1


if __name__ == "__main__":
    raise SystemExit(report())
