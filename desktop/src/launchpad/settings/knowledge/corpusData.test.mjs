/**
 * Data-integrity test for the desktop-side packaged corpus copy -- issue
 * #552 step 7.
 *
 * Unlike corpusNodes.test.mjs (pure logic over synthetic fixtures), this
 * file imports the REAL generated/corpus.json this panel actually ships,
 * the same way corpus/tests/test_package.py's DriftGuardTest and
 * knowledge/src/lib.rs's own tests read the real committed artifact rather
 * than a fixture -- there is no substitute for checking the thing that
 * actually ships. It closes the loop on the DoD's "provenance/origin
 * metadata survive the packaging boundary" bullet end-to-end: `origin` and
 * `evidence` must still be present and unmodified from the source node once
 * the data has crossed into the frontend, not just inside the Rust crate
 * (lib.rs's own known_real_ids_are_present_with_their_real_type_and_origin
 * test covers that half).
 */

import assert from "node:assert/strict";
import { describe, it } from "node:test";

import corpusJson from "./generated/corpus.json" with { type: "json" };

describe("the desktop copy of generated/corpus.json", () => {
  it("is non-trivially populated, not the empty scaffold", () => {
    assert.ok(Array.isArray(corpusJson));
    assert.ok(corpusJson.length > 1);
  });

  it("carries corpus-readme's real origin and evidence, unmodified", () => {
    const node = corpusJson.find((n) => n.id === "corpus-readme");
    assert.ok(node, "corpus-readme must be present in the packaged corpus");
    assert.equal(node.type, "governance");
    assert.equal(node.origin, "launchpad");
    assert.ok(Array.isArray(node.evidence));
    assert.ok(node.evidence.length > 0, "evidence must not be stripped");
    for (const entry of node.evidence) {
      assert.ok(
        typeof entry.statement === "string" && entry.statement.length > 0,
      );
      assert.ok(
        ["FACT", "INFERENCE", "TEAM_KNOWLEDGE"].includes(entry.entry_class),
      );
    }
  });

  it("carries architecture-containers-postgres's real origin and evidence, unmodified", () => {
    const node = corpusJson.find(
      (n) => n.id === "architecture-containers-postgres",
    );
    assert.ok(node, "architecture-containers-postgres must be present");
    assert.equal(node.type, "architecture");
    assert.equal(node.origin, "launchpad");
    assert.ok(node.evidence.length > 0, "evidence must not be stripped");
  });

  it("every node carries a non-empty origin and evidence array", () => {
    // Broader than the two known-id checks above: confirms the packaging
    // boundary preserves provenance for the whole artifact, not just the
    // two ids this test happens to name.
    for (const node of corpusJson) {
      assert.ok(
        typeof node.origin === "string" && node.origin.length > 0,
        `${node.id}: origin must be a non-empty string`,
      );
      assert.ok(
        Array.isArray(node.evidence) && node.evidence.length > 0,
        `${node.id}: evidence must be a non-empty array`,
      );
    }
  });
});
