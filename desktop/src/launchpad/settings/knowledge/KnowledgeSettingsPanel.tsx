import { BookOpen } from "lucide-react";
import { useEffect, useState } from "react";
import type { CohortSettingsSectionDescriptor } from "../registry";
import {
  SettingsOptionGroup,
  SettingsOptionGroupList,
  SettingsOptionRow,
} from "@/features/settings/ui/SettingsOptionGroup";
import { SettingsSectionHeader } from "@/features/settings/ui/SettingsSectionHeader";
import {
  deriveExcerpt,
  deriveTitle,
  groupNodesByType,
  humanizeCorpusType,
  type CorpusNode,
  type CorpusTypeGroup,
} from "./corpusNodes";

/**
 * Renders one representative node per corpus `type` present in the packaged
 * data (#552). Groups over whatever `type` values actually appear, not a
 * hardcoded list, so a future `capabilities`/`operations` node renders the
 * moment it is authored and repackaged.
 *
 * A static, non-interactive list -- the same
 * SettingsOptionGroupList/SettingsOptionGroup/SettingsOptionRow structure
 * KeyboardShortcutsCard.tsx already uses for read-only Settings content, so
 * no new ARIA role or custom widget is introduced.
 *
 * Body text is a bounded excerpt (see deriveExcerpt), not the full raw
 * Markdown body: real corpus nodes run to hundreds of source lines, and
 * dumping one whole body as wrapped plain text would push a single
 * representative past ten thousand rendered pixels -- an unreadable wall of
 * markdown syntax rather than a help surface. The full body stays on the
 * underlying `CorpusNode`; only this display is truncated.
 *
 * The committed, packaged corpus (#552) -- produced out-of-band by
 * launchpad/project-intelligence/corpus/package.py, never re-derived here.
 * See launchpad/crates/knowledge/AGENTS.md's "one rule". Loaded via a
 * dynamic `import()` on mount, not a top-level static import: the artefact
 * is multiple megabytes (204 nodes as of this writing, and growing with the
 * corpus), and a static import inlines it into whatever chunk eagerly loads
 * this module -- shipped to every user on cold start whether or not they
 * ever open Settings. A dynamic import puts it in its own chunk, fetched
 * only when this panel actually mounts (review-final finding on #552).
 *
 * A rejected chunk load (real after a desktop update replaces the on-disk
 * chunk files a still-open window has already resolved import specifiers
 * against) surfaces as an explicit error message rather than an unhandled
 * rejection plus a permanently empty panel with no explanation.
 */
function KnowledgeSettingsPanel() {
  const [corpusTypeGroups, setCorpusTypeGroups] = useState<
    CorpusTypeGroup[] | null
  >(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    import("./generated/corpus.json")
      .then((module) => {
        if (cancelled) {
          return;
        }
        const nodes = module.default as CorpusNode[];
        setCorpusTypeGroups(groupNodesByType(nodes));
      })
      .catch(() => {
        if (cancelled) {
          return;
        }
        setLoadError(
          "Couldn't load Help content. Try restarting Buzz, or check for an update.",
        );
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section data-testid="settings-knowledge">
      <SettingsSectionHeader
        title="Help"
        description="Buzz's built-in documentation, packaged from the canonical corpus."
      />
      {loadError ? (
        <p
          className="text-sm text-muted-foreground"
          data-testid="settings-knowledge-error"
          role="status"
        >
          {loadError}
        </p>
      ) : corpusTypeGroups === null ? (
        <p
          className="text-sm text-muted-foreground"
          data-testid="settings-knowledge-loading"
          role="status"
        >
          Loading Help content…
        </p>
      ) : (
        <SettingsOptionGroupList>
          {corpusTypeGroups.map(({ type, representative }) => (
            <SettingsOptionGroup key={type} title={humanizeCorpusType(type)}>
              <SettingsOptionRow
                className="flex-col items-start gap-2 py-4"
                data-testid={`settings-knowledge-node-${representative.id}`}
              >
                <h3 className="text-sm font-medium text-foreground">
                  {deriveTitle(representative)}
                </h3>
                <p
                  className="text-2xs text-muted-foreground"
                  data-settings-subcopy
                  data-testid={`settings-knowledge-node-${representative.id}-provenance`}
                >
                  id: {representative.id} · origin: {representative.origin}
                </p>
                <p className="whitespace-pre-wrap text-sm text-muted-foreground">
                  {deriveExcerpt(representative.body)}
                </p>
              </SettingsOptionRow>
            </SettingsOptionGroup>
          ))}
        </SettingsOptionGroupList>
      )}
    </section>
  );
}

export const knowledgeSettingsSection: CohortSettingsSectionDescriptor = {
  value: "knowledge",
  label: "Help",
  icon: BookOpen,
  render: () => <KnowledgeSettingsPanel />,
  navGroup: "Help",
};
