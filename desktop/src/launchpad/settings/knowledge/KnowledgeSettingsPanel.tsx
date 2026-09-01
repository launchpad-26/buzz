import { BookOpen } from "lucide-react";
import type { CohortSettingsSectionDescriptor } from "../registry";
import {
  SettingsOptionGroup,
  SettingsOptionGroupList,
  SettingsOptionRow,
} from "@/features/settings/ui/SettingsOptionGroup";
import { SettingsSectionHeader } from "@/features/settings/ui/SettingsSectionHeader";
import corpusJson from "./generated/corpus.json";
import {
  deriveExcerpt,
  deriveTitle,
  groupNodesByType,
  humanizeCorpusType,
  type CorpusNode,
} from "./corpusNodes";

// The committed, packaged corpus (#552) -- produced out-of-band by
// launchpad/project-intelligence/corpus/package.py, never re-derived here.
// See launchpad/crates/knowledge/AGENTS.md's "one rule".
const corpusNodes = corpusJson as CorpusNode[];
const corpusTypeGroups = groupNodesByType(corpusNodes);

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
 */
function KnowledgeSettingsPanel() {
  return (
    <section data-testid="settings-knowledge">
      <SettingsSectionHeader
        title="Help"
        description="Buzz's built-in documentation, packaged from the canonical corpus."
      />
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
