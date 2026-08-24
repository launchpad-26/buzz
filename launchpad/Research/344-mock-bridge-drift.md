---
description: Whether the desktop E2E mock bridge has drifted from the real Tauri command surface — five handlers are dead, while one backend-less handler is exercised by a registered spec. Nothing detects the mismatch.
tags: [testing, desktop, tauri, e2e, mock, drift, research, issue-344]
---

# Has the desktop E2E mock bridge drifted from the real Tauri command surface?

All source references below are pinned to `5d76799d6e44f2f76aa7bd78c5343d339af98f63`.

## Finding

**Yes: five handlers appear dead, and one backend-less handler is actively exercised by a spec.**

The failure mode #344 was written to look for — a mock reporting green for behaviour the
application no longer has — **is present in one direction**. The registered
`identity-lost.spec.ts` invokes `complete_identity_recovery_pairing`, for which the mock has a
handler and the Rust backend has none. In the opposite direction, an unknown backend command raises
rather than returning a plausible default, so missing mock coverage fails loudly.

What *is* true is that **nothing detects drift**. Six handlers for commands that exist nowhere in
the repository accumulated without any check noticing, and the same silence would cover a more
dangerous divergence.

## The two sets

**Real:** 322 `#[tauri::command]` attributes exist under `desktop/src-tauri/src/`. 312 distinct
commands are registered in the main handler at
[`lib.rs:604`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/desktop/src-tauri/src/lib.rs#L604); a second, smaller handler exists at
[`native_websocket.rs:325`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/desktop/src-tauri/src/native_websocket.rs#L325).

**Mocked:** 259 commands are handled by
[`e2eBridge.ts`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/desktop/src/testing/e2eBridge.ts), counted from its
`case "…"` labels. `e2eBridgeCustomHarnesses.ts` contributes zero such labels. `e2eBridge.ts` is
13,450 lines.

## Direction 1 — mock handles, backend does not: 9

```
clear_e2e_opened_external_urls
complete_identity_recovery_pairing
export_team_to_json
get_e2e_opened_external_urls
get_global_agent_config_set_call_count
install_team_from_directory
parse_team_file
pick_team_directory
sync_team_directory
```

**Three are deliberate test-only helpers**, not drift: `clear_e2e_opened_external_urls`,
`get_e2e_opened_external_urls` and `get_global_agent_config_set_call_count` exist so a spec can
inspect what the harness recorded. They have no backend counterpart by design.

**All six lack Rust implementations, but only five appear dead.**
`complete_identity_recovery_pairing`, `export_team_to_json`, `install_team_from_directory`,
`parse_team_file`, `pick_team_directory` and `sync_team_directory` are defined nowhere in the
Rust backend:

```
complete_identity_recovery_pairing: defined_in_rust=0  in_lib.rs=0
export_team_to_json:               defined_in_rust=0  in_lib.rs=0
install_team_from_directory:       defined_in_rust=0  in_lib.rs=0
parse_team_file:                   defined_in_rust=0  in_lib.rs=0
pick_team_directory:               defined_in_rust=0  in_lib.rs=0
sync_team_directory:               defined_in_rust=0  in_lib.rs=0
```

Five have no caller found outside the mock. The original research checked one name and incorrectly
generalised its result to all six:

```
$ grep -rln "pick_team_directory" desktop/
desktop/src/testing/e2eBridge.ts
```

`complete_identity_recovery_pairing` is different: `desktop/tests/e2e/identity-lost.spec.ts`
invokes it, and that spec is registered by `desktop/playwright.config.ts`. A green mock-driven UI
transition therefore exercises behaviour with no backend implementation. The other five are
residue based on the per-name search; deleting the sixth would break a registered test.

## Direction 2 — backend has, mock does not: 62

62 registered commands have no mock handler, including `add_relay_member`,
`change_channel_member_role`, `decrypt_observer_event`, `download_voice_models` and
`discover_git_bash_prerequisite`.

This is the direction that would matter, and it is defused by the fallback at
[`e2eBridge.ts:13423-13424`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/desktop/src/testing/e2eBridge.ts#L13423-L13424):

```typescript
      default:
        throw new Error(`Unsupported mocked Tauri command: ${command}`);
```

An unmocked command produces an exception, not a default value. A spec that reaches one fails, and
fails with the command name in the message. **Missing coverage in the mock cannot manifest as a
false pass** — it manifests as a broken test, which is the correct direction to fail in.

## Would anything catch future drift?

No check compares the two sets. Searching the repository finds no script, test or workflow that
reads both the `generate_handler!` registration and the mock's `case` labels. The evidence is
negative — I did not find one — rather than a demonstration that none can exist.

The 62-command gap is also expected rather than a defect: the mock is deliberately partial, covering
what the 146 specs exercise. Whether that partiality is written down anywhere I did not establish.

## Recommendations

**Opinion, mine (Claude Opus 5, drafting for @tucktuck101). Not established by any source above.**

1. **I would not treat this as a bug to fix, and I would not add mocks for the 62.** The throwing
   fallback already makes the gap safe, and mocking commands no spec exercises would add
   maintenance surface for no assurance.
2. **I would delete only the five handlers with no caller**, as tidying rather than as a correctness
   fix. `complete_identity_recovery_pairing` needs separate product/test adjudication because a
   registered spec depends on it.
3. **A name-level drift check looks cheap and worth having** — compare the `generate_handler!`
   list against the mock's `case` labels and report handlers with no backend counterpart. It would
   have caught these six backend mismatches. I would scope it to that direction only, since the other direction is
   already enforced at runtime by the throw.
4. **The more valuable check is the one I did not perform** — see below. If I were prioritising, I
   would put return-shape fidelity above name-level drift, because that is where a false green
   could actually come from.

None of these is a decision I am entitled to take.

## Confidence and what was not checked

**High confidence:** the two command sets and their difference (extracted mechanically from the
pinned source), that all six are absent from the Rust backend, that five lack callers while
`complete_identity_recovery_pairing` is invoked by a registered spec, and the throwing fallback.

**Not checked, and the first item is the important one:**

- **Return-shape fidelity was not examined at all.** This is a **name-level** comparison. A mocked
  command whose name matches but whose return value has drifted from the real signature would pass
  every check in this document and *could* produce a false green. That is the dangerous version of
  the question #344 asks, it applies to all ~250 commands the mock does handle, and it is
  unmeasured. Establishing it means comparing each handler's returned shape against its Rust
  function's return type — a much larger piece of work than this was.
- **The second handler at `native_websocket.rs:325` was not expanded.** Its commands are not in the
  312 counted from `lib.rs`, so a few of the "unmocked" 62 may be registered there instead, and the
  real total is above 312.
- **Whether the mock's partiality is documented** anywhere was not established.
- **The count of 259 mock handlers comes from `case "…"` labels.** If the bridge dispatches some
  commands another way — a lookup table, a prefix match — those would not be counted, and the mock
  may handle more than 259.
- **No specs were run.** #322 established this host cannot resolve pnpm, so the 146 Playwright specs
  were not executed as part of this work.
