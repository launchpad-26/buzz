/**
 * Pure helpers over the packaged corpus JSON (#552) -- no React, no Tauri,
 * no network. Extracted for deterministic unit-testing, matching this
 * directory's existing *Logic.ts convention (see
 * desktop/src/features/settings/ui/harnessGalleryLogic.ts).
 *
 * The corpus artifact itself is produced out-of-band by
 * launchpad/project-intelligence/corpus/package.py and committed at
 * ./generated/corpus.json -- this module only reads it, per
 * launchpad/crates/knowledge/AGENTS.md's "one rule".
 */

/** One evidence entry, per node.schema.json's evidenceEntry $def. */
export type CorpusEvidenceEntry = {
  statement: string;
  entry_class: "FACT" | "INFERENCE" | "TEAM_KNOWLEDGE";
  evidence?: string[];
  confidence?: number;
  provided_by?: string;
};

/** One typed edge to another corpus node, per node.schema.json's relationship $def. */
export type CorpusRelationship = {
  type: string;
  target: string;
};

/** One packaged corpus node -- the shape package.py writes to corpus.json. */
export type CorpusNode = {
  id: string;
  type: string;
  status: string;
  origin: string;
  audiences: string[];
  relationships: CorpusRelationship[];
  evidence: CorpusEvidenceEntry[];
  body: string;
};

/** One rendered group: a corpus `type` value and its chosen representative node. */
export type CorpusTypeGroup = {
  type: string;
  representative: CorpusNode;
};

/**
 * Groups nodes by their `type` field and picks one representative per group,
 * generically over whatever `type` values are actually present in the data
 * -- never a hardcoded list, so a future `capabilities`/`operations` node
 * renders the moment it is authored and repackaged (#552's DoD).
 *
 * Groups are returned sorted by `type` name for a stable render order.
 */
export function groupNodesByType(
  nodes: readonly CorpusNode[],
): CorpusTypeGroup[] {
  const byType = new Map<string, CorpusNode[]>();
  for (const node of nodes) {
    const bucket = byType.get(node.type);
    if (bucket) {
      bucket.push(node);
    } else {
      byType.set(node.type, [node]);
    }
  }

  return [...byType.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([type, groupNodes]) => ({
      type,
      representative: selectRepresentativeNode(groupNodes),
    }));
}

/**
 * Deterministically picks one node from a non-empty group: the lowest `id`.
 * Sorts independently of package.py's own id-sort rather than trusting the
 * artifact's ordering, so this helper's result doesn't silently depend on an
 * upstream invariant it doesn't own.
 */
export function selectRepresentativeNode(
  nodes: readonly CorpusNode[],
): CorpusNode {
  if (nodes.length === 0) {
    throw new Error("selectRepresentativeNode: nodes must be non-empty");
  }
  return [...nodes].sort((a, b) => a.id.localeCompare(b.id))[0];
}

/**
 * The node's display title: its Markdown body's first `# ` heading line,
 * with the marker stripped -- or its `id` if the body has no such heading.
 */
export function deriveTitle(node: Pick<CorpusNode, "id" | "body">): string {
  const headingLine = node.body
    .split("\n")
    .find((line) => line.startsWith("# "));
  return headingLine ? headingLine.slice(2).trim() : node.id;
}

/** Default excerpt length for {@link deriveExcerpt}. */
export const EXCERPT_MAX_CHARS = 600;

/**
 * A bounded preview of the node's body, for compact Settings rendering.
 *
 * Real corpus node bodies run to hundreds of source lines (e.g. the
 * corpus's own AGENTS.md is 500+), which as wrapped `whitespace-pre-wrap`
 * text would push a single representative node past ten thousand rendered
 * pixels -- an unreadable wall of raw markdown syntax in a Settings panel,
 * not a help surface. This truncates to `maxChars`, dropping the leading
 * `# ` heading line (already shown via {@link deriveTitle}) and cutting at
 * the nearest word boundary with a trailing ellipsis when truncated.
 *
 * Display-only: the full `body` stays on the `CorpusNode` this reads from
 * and is never discarded from the underlying corpus data.
 */
export function deriveExcerpt(
  body: string,
  maxChars: number = EXCERPT_MAX_CHARS,
): string {
  const withoutHeading = body.replace(/^#\s.*\n+/, "");
  const trimmed = withoutHeading.trim();
  if (trimmed.length <= maxChars) {
    return trimmed;
  }
  const truncated = trimmed.slice(0, maxChars);
  const lastSpace = truncated.lastIndexOf(" ");
  const boundary = lastSpace > 0 ? truncated.slice(0, lastSpace) : truncated;
  return `${boundary}…`;
}
