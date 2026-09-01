import assert from "node:assert/strict";
import { describe, it } from "node:test";

import {
  deriveExcerpt,
  deriveTitle,
  groupNodesByType,
  selectRepresentativeNode,
} from "./corpusNodes.ts";

function node(overrides = {}) {
  return {
    id: overrides.id ?? "test-node",
    type: overrides.type ?? "governance",
    status: overrides.status ?? "active",
    origin: overrides.origin ?? "launchpad",
    audiences: overrides.audiences ?? ["developer"],
    relationships: overrides.relationships ?? [],
    evidence: overrides.evidence ?? [
      { statement: "test", entry_class: "FACT", evidence: ["Justfile"] },
    ],
    body: overrides.body ?? "# Test node\n\nBody text.",
  };
}

// ── deriveTitle ──────────────────────────────────────────────────────────────

describe("deriveTitle", () => {
  it("strips the leading '# ' marker from the first heading line", () => {
    assert.equal(
      deriveTitle(node({ body: "# Container: Postgres\n\nMore text." })),
      "Container: Postgres",
    );
  });

  it("falls back to the node id when the body has no '# ' heading", () => {
    assert.equal(
      deriveTitle(node({ id: "no-heading-node", body: "No heading here." })),
      "no-heading-node",
    );
  });

  it("ignores a '## ' subheading and finds the first true '# ' heading", () => {
    assert.equal(
      deriveTitle(
        node({ body: "## Not this one\n# Container: Postgres\nMore." }),
      ),
      "Container: Postgres",
    );
  });
});

// ── deriveExcerpt ────────────────────────────────────────────────────────────

describe("deriveExcerpt", () => {
  it("returns a short body unchanged, with the heading line dropped", () => {
    assert.equal(
      deriveExcerpt("# Container: Postgres\n\nShort body text."),
      "Short body text.",
    );
  });

  it("truncates a long body at a word boundary with a trailing ellipsis", () => {
    const longBody = "word ".repeat(200).trim();
    const excerpt = deriveExcerpt(longBody, 50);
    assert.ok(
      excerpt.length <= 51,
      `expected <= 51 chars, got ${excerpt.length}`,
    );
    assert.ok(excerpt.endsWith("…"));
    assert.ok(!excerpt.slice(0, -1).endsWith(" "), "must not cut mid-word");
    // Content fidelity, not just shape: the visible text (minus the
    // trailing ellipsis) must actually be a prefix of the source body, so a
    // slice-from-the-wrong-end (or otherwise-wrong-offset) regression can't
    // pass by coincidentally matching length/ellipsis/no-mid-word-cut alone.
    assert.ok(
      longBody.startsWith(excerpt.slice(0, -1)),
      "truncated text must be a genuine prefix of the source body",
    );
  });

  it("does not truncate a body exactly at the character limit", () => {
    const exact = "a".repeat(50);
    assert.equal(deriveExcerpt(exact, 50), exact);
  });

  it("finds the heading line wherever deriveTitle finds it, not only at position 0", () => {
    // deriveTitle searches the whole body for the first '# ' line; the
    // excerpt must drop that same line, not just whatever sits at offset 0,
    // or the heading renders twice (once as the <h3> title, once inside the
    // excerpt body).
    const body = "## Not this one\n# Real Heading\nBody text after.";
    assert.equal(deriveTitle({ id: "x", body }), "Real Heading");
    assert.equal(deriveExcerpt(body), "## Not this one\n\nBody text after.");
  });

  it("converts a Markdown table to readable prose instead of literal pipes", () => {
    const body = [
      "# Table node",
      "",
      "| For | Read |",
      "|---|---|",
      "| Config | `settings.json` |",
    ].join("\n");
    const excerpt = deriveExcerpt(body);
    assert.ok(!excerpt.includes("|"), "no literal pipe characters remain");
    assert.ok(excerpt.includes("For · Read"));
    assert.ok(excerpt.includes("Config · settings.json"));
  });

  it("strips inline emphasis, code spans, and link syntax to plain text", () => {
    const body =
      "# Node\n\nSee **bold**, *italic*, `code`, and [a link](https://example.com).";
    assert.equal(deriveExcerpt(body), "See bold, italic, code, and a link.");
  });
});

// ── selectRepresentativeNode ─────────────────────────────────────────────────

describe("selectRepresentativeNode", () => {
  it("picks the lowest id, independent of input order", () => {
    const a = node({ id: "architecture-zeta" });
    const b = node({ id: "architecture-alpha" });
    assert.equal(selectRepresentativeNode([a, b]).id, "architecture-alpha");
    assert.equal(selectRepresentativeNode([b, a]).id, "architecture-alpha");
  });

  it("throws on an empty group rather than returning undefined", () => {
    assert.throws(() => selectRepresentativeNode([]));
  });
});

// ── groupNodesByType ──────────────────────────────────────────────────────────

describe("groupNodesByType", () => {
  it("groups generically over whatever type values are present, not a hardcoded list", () => {
    const nodes = [
      node({ id: "architecture-b", type: "architecture" }),
      node({ id: "architecture-a", type: "architecture" }),
      node({ id: "governance-a", type: "governance" }),
      node({ id: "capabilities-a", type: "capabilities" }),
    ];
    const groups = groupNodesByType(nodes);
    assert.deepEqual(
      groups.map((g) => g.type),
      ["architecture", "capabilities", "governance"],
    );
  });

  it("picks the lowest-id representative within each group", () => {
    const nodes = [
      node({ id: "architecture-b", type: "architecture" }),
      node({ id: "architecture-a", type: "architecture" }),
    ];
    const [group] = groupNodesByType(nodes);
    assert.equal(group.representative.id, "architecture-a");
  });

  it("a future type present in the data renders without any code change here", () => {
    // Regression guard for the DoD's "a future capabilities/operations node
    // renders the moment it is authored and repackaged" -- no hardcoded
    // 4-category list to update.
    const nodes = [node({ id: "brand-new-type-node", type: "operations" })];
    const groups = groupNodesByType(nodes);
    assert.deepEqual(
      groups.map((g) => g.type),
      ["operations"],
    );
  });

  it("returns no groups for an empty node list", () => {
    assert.deepEqual(groupNodesByType([]), []);
  });
});
