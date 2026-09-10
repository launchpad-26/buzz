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
 * The packaged corpus, served as a static asset from `desktop/public/` rather
 * than imported from under `desktop/src/`. That placement is load-bearing, not
 * incidental (#2172): the artefact is generated documentation describing this
 * whole repository, so it contains literal instances of strings the
 * repository's own scanners search for -- including two corpus nodes that
 * document `ci.yml`'s `dead-token-guard` and quote its pattern verbatim. Under
 * `desktop/src/` that guard read the corpus as client source and failed, and
 * so would any future scanner over that tree. `desktop/public/` sits outside
 * every path those guards scan, and Vite copies it to the bundle root
 * unchanged. Do not move this back under `desktop/src/`.
 */
const CORPUS_ASSET_URL = "/knowledge-corpus.json";

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
 * See launchpad/crates/knowledge/AGENTS.md's "one rule". Fetched from
 * CORPUS_ASSET_URL on mount, not imported: the artefact is multiple megabytes
 * (719 nodes as of this writing, and growing with the corpus), and any import
 * -- static or dynamic -- makes it a bundled chunk. As a static asset it is
 * never parsed, never chunked, and never shipped to a user who does not open
 * this panel. That preserves the cold-start property the original dynamic
 * import was chosen for (review-final finding on #552) while also keeping the
 * file out of desktop/src/, which is what #2172 required.
 *
 * A failed fetch -- a missing or unreadable asset after a desktop update
 * replaces bundle files a still-open window is resolving against -- surfaces
 * as an explicit error message rather than an unhandled rejection plus a
 * permanently empty panel with no explanation. A non-2xx response is thrown
 * explicitly, because fetch() resolves rather than rejects on 404 and would
 * otherwise reach .json() and fail with a parse error naming the wrong
 * cause.
 */
function KnowledgeSettingsPanel() {
  const [corpusTypeGroups, setCorpusTypeGroups] = useState<
    CorpusTypeGroup[] | null
  >(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch(CORPUS_ASSET_URL)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`corpus asset responded ${response.status}`);
        }
        return response.json();
      })
      .then((nodes: CorpusNode[]) => {
        if (cancelled) {
          return;
        }
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
