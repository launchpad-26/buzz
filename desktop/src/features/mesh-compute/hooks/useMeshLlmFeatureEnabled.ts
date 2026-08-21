import * as React from "react";

import { meshLlmFeatureEnabled } from "@/shared/api/tauriMesh";

/**
 * Whether this build was compiled with the `mesh-llm` feature. Defaults to
 * `false` (fail closed) until the first successful check resolves, and stays
 * `false` if the check itself errors — the option this gates ("Buzz shared
 * compute" in the persona/agent provider picker) should never be offered on
 * an uncertain answer, only on a confirmed `true` (#269).
 */
export function useMeshLlmFeatureEnabled(): boolean {
  const [enabled, setEnabled] = React.useState(false);

  React.useEffect(() => {
    let cancelled = false;
    meshLlmFeatureEnabled()
      .then((value) => {
        if (!cancelled) setEnabled(value);
      })
      .catch(() => {
        // Stays false — see doc comment above.
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return enabled;
}
