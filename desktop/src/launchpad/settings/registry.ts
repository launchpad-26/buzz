import type { LucideIcon } from "lucide-react";
import { knowledgeSettingsSection } from "./knowledge/KnowledgeSettingsPanel";

/**
 * The registration seam ADR-0051 grants: a cohort Settings section is added
 * here, under `launchpad/`-owned code, never by editing
 * `SettingsPanels.tsx`'s four upstream registration sites directly.
 *
 * Adding a new cohort section: widen this union, add its descriptor's import
 * and array entry below. Both edits stay in this file.
 */
export type CohortSettingsSectionId = "knowledge";

export type CohortSettingsSectionDescriptor = {
  value: CohortSettingsSectionId;
  label: string;
  icon: LucideIcon;
  render: () => React.ReactNode;
};

export const cohortSettingsSections: CohortSettingsSectionDescriptor[] = [
  knowledgeSettingsSection,
];
