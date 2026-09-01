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
 * A presentable label for a corpus `type` value, for the group heading's
 * accessible name -- e.g. `architecture` -> `Architecture`. Deliberately a
 * generic transform (capitalize the raw value) rather than a lookup table
 * naming today's known types, so a future `capabilities`/`operations` type
 * still gets a real label the moment it's authored, matching this module's
 * "no hardcoded type list" rule (see {@link groupNodesByType}).
 */
export function humanizeCorpusType(type: string): string {
  if (type.length === 0) {
    return type;
  }
  return type.charAt(0).toUpperCase() + type.slice(1);
}

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
 * Finds the body's first `# ` (level-1) heading line, if any. Shared by
 * {@link deriveTitle} and {@link deriveExcerpt} so both agree on which line
 * is "the heading" -- they used to disagree (title searched the whole body,
 * the excerpt only stripped position 0), which could duplicate a heading
 * found deeper in the body under the rendered `<h3>` title.
 */
function findHeadingLine(body: string): string | undefined {
  return body.split("\n").find((line) => line.startsWith("# "));
}

/**
 * The node's display title: its Markdown body's first `# ` heading line,
 * with the marker stripped -- or its `id` if the body has no such heading.
 */
export function deriveTitle(node: Pick<CorpusNode, "id" | "body">): string {
  const headingLine = findHeadingLine(node.body);
  return headingLine ? headingLine.slice(2).trim() : node.id;
}

/** Default excerpt length for {@link deriveExcerpt}. */
export const EXCERPT_MAX_CHARS = 600;

/**
 * Strips the handful of Markdown constructs a corpus body realistically
 * contains, so a plain-text excerpt doesn't read as a wall of syntax to a
 * screen reader -- most concretely, a Markdown table rendered as literal
 * `|` characters carries no row/column relationship for assistive tech
 * (WCAG SC 1.3.1). Not a Markdown renderer: this converts to plain,
 * readable prose rather than real semantic HTML, which is the smaller fix
 * for a short Settings preview whose full body already renders properly
 * through the app's normal Markdown pipeline elsewhere.
 */
function stripBasicMarkdown(text: string): string {
  return text
    .split("\n")
    .filter((line) => !/^[\s|:-]+$/.test(line) || !line.includes("|"))
    .map((line) =>
      line.includes("|")
        ? line
            .trim()
            .replace(/^\|/, "")
            .replace(/\|$/, "")
            .split("|")
            .map((cell) => cell.trim())
            .join(" · ")
        : line,
    )
    .join("\n")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/\*([^*]+)\*/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1");
}

/**
 * A bounded preview of the node's body, for compact Settings rendering.
 *
 * Real corpus node bodies run to hundreds of source lines (e.g. the
 * corpus's own AGENTS.md is 500+), which as wrapped `whitespace-pre-wrap`
 * text would push a single representative node past ten thousand rendered
 * pixels -- an unreadable wall of raw markdown syntax in a Settings panel,
 * not a help surface. This truncates to `maxChars`, dropping the leading
 * `# ` heading line (already shown via {@link deriveTitle}), stripping the
 * Markdown constructs {@link stripBasicMarkdown} handles, and cutting at
 * the nearest word boundary with a trailing ellipsis when truncated.
 *
 * Display-only: the full `body` stays on the `CorpusNode` this reads from
 * and is never discarded from the underlying corpus data.
 */
export function deriveExcerpt(
  body: string,
  maxChars: number = EXCERPT_MAX_CHARS,
): string {
  const headingLine = findHeadingLine(body);
  const withoutHeading = headingLine
    ? body.replace(headingLine, "").replace(/^\n+/, "")
    : body;
  const trimmed = stripBasicMarkdown(withoutHeading).trim();
  if (trimmed.length <= maxChars) {
    return trimmed;
  }
  const truncated = trimmed.slice(0, maxChars);
  const lastSpace = truncated.lastIndexOf(" ");
  const boundary = lastSpace > 0 ? truncated.slice(0, lastSpace) : truncated;
  return `${boundary}…`;
}
