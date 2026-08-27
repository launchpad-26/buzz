import { BookOpen } from "lucide-react";
import type { CohortSettingsSectionDescriptor } from "../registry";
import { SettingsOptionGroup } from "@/features/settings/ui/SettingsOptionGroup";
import { SettingsSectionHeader } from "@/features/settings/ui/SettingsSectionHeader";

/**
 * Scaffold only (#551). No corpus content and no `knowledge.*` query
 * interface yet — see `launchpad/crates/knowledge/AGENTS.md`.
 */
function KnowledgeSettingsPanel() {
  return (
    <section aria-labelledby="knowledge-settings-heading">
      <SettingsSectionHeader
        title={<span id="knowledge-settings-heading">Help</span>}
        description="Buzz's built-in help is coming soon."
      />
      <SettingsOptionGroup title="Coming soon">
        <p className="px-4 py-3 text-sm text-muted-foreground/70">
          This panel will surface Buzz's documentation once it is seeded.
        </p>
      </SettingsOptionGroup>
    </section>
  );
}

export const knowledgeSettingsSection: CohortSettingsSectionDescriptor = {
  value: "knowledge",
  label: "Help",
  icon: BookOpen,
  render: () => <KnowledgeSettingsPanel />,
};
