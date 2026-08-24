# Whether key-backup material could leave a client through a span or log

**Title:** The desktop egress guard's coverage of telemetry as an egress boundary
**Summary:** The guard's inventory-completeness test scans for the literal string `/events`, so an OTLP exporter — which constructs no such URL — would pass it silently; files absent from the inventory are *expected* to have zero sites. No leak exists today: no print site interpolates key material, and the `nostr` key and NIP-49 error `Display` impls do not echo their input. Two structural points matter more: the inventory can already express a no-URL boundary, and the guard matches `ncryptsec` only, so a raw `nsec` on a telemetry path would be caught by nothing.
**Tags:** `observability` `security` `desktop` `egress` `nip-49` `exfiltration`
**Reviewed:** 2026-08-22 · **Source:** `launchpad-26/buzz` at `678008ea4` · **Answers:** [#317](https://github.com/launchpad-26/buzz/issues/317)

---

## Finding

**No — the completeness test does not cover a telemetry exporter.** It matches on the literal string `/events`. An OTLP exporter constructs no such URL, and the scan's stated default is that a file absent from the inventory table should have zero `/events` sites and zero guard calls. An exporter is precisely that file: it would be added, ship, and the test would stay green.

That is not a flaw in the test. It is a narrowly-scoped control doing exactly what it says. Telemetry is a boundary that did not exist when the inventory was written.

**No leak exists today**, and that was checked rather than assumed. But three things follow that matter more than the reassurance:

1. The inventory **can already express** a boundary with no URL — `native_websocket.rs` is `(0, 2)`. Extending the guard needs no new machinery, only the knowledge that it applies.
2. The guard matches `ncryptsec` **only**. A raw `nsec` reaching telemetry would be caught by nothing, by design.
3. There is currently **no destination** for a desktop leak to reach. #289 creates one.

---

## Part 1 — What the completeness test asserts

`desktop/src-tauri/src/egress_guard_tests.rs:263-282`:

```rust
const EVENTS_INVENTORY: &[(&str, usize, usize)] = &[
    // Production egress boundaries (see egress_guard.rs table):
    ("src/relay.rs", 2, 2),                             // boundaries 2, 4
    ("src/relay/submit.rs", 1, 1),                      // boundaries 1 + 3 (shared funnel)
    ("src/huddle/pipeline.rs", 1, 1),                   // boundary 5
    ("src/commands/team_snapshot.rs", 1, 1),            // boundary 6
    ("src/commands/personas/snapshot/import.rs", 2, 1), // boundary 7 + its in-file injection-test fixture URL
    ("src/native_websocket.rs", 0, 2),                  // boundary 8 (WS frames; no events URL)
    ...
];
```

What it matches on (`:283-288`):

```rust
fn events_needle() -> String {
    ["/ev", "ents"].concat()
}
fn guard_needle() -> String {
    ["egress_guard::", "assert_no_key_backup"].concat()
}
```

And the default for anything not in the table, from the scan's own doc comment (`:290-293`):

> *"empty means every file matches its inventory row exactly (files absent from the table are expected to have zero `/events` sites and zero guard calls)"*

A file with no `/events` occurrence and no guard call is compliant. That is an OTLP exporter.

## Part 2 — The mechanism can already express this

The `native_websocket.rs` row is `(0, 2)`: zero `/events` sites, two guard calls. Boundary 8 in `egress_guard.rs`'s own module table is annotated "WS frames; no events URL". So a URL-less boundary is already representable — extending the guard to a telemetry exporter is one inventory row plus two guard calls.

**What it needs is for somebody to know to do it.** The scan detects drift against a declared inventory; it cannot detect the arrival of an undeclared *kind* of egress.

## Part 3 — No leak today, on the paths checked

Every print site whose text names key material:

```
$ grep -rn "eprintln!\|println!" desktop/src-tauri/src --include='*.rs' | grep -iE "nsec|ncryptsec|secret|privkey|private_key|seckey|passphrase|password|token"
desktop/src-tauri/src/migration.rs:779:        eprintln!("buzz-desktop: shared-agent-sync: BUZZ_PRIVATE_KEY missing or invalid, skipping");
desktop/src-tauri/src/app_state.rs:147:                eprintln!("buzz-desktop: invalid BUZZ_PRIVATE_KEY: {error}");
desktop/src-tauri/src/app_state.rs:152:            eprintln!("buzz-desktop: BUZZ_PRIVATE_KEY contains invalid UTF-8");
desktop/src-tauri/src/app_state.rs:675:    eprintln!("buzz-desktop: corrupt nsec in keyring ({error}), clearing and recovering from file");
```

Three carry no interpolation of a value. Two interpolate `{error}` from parsing a private key — the shape that leaks if the error echoes its input. It does not. `nostr 0.44.7` (the version pinned in `Cargo.lock`), `src/key/mod.rs:34-57`:

```rust
pub enum Error {
    Secp256k1(secp256k1::Error),
    Hex(hex::FromHexError),
    InvalidSecretKey,
    InvalidPublicKey,
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Secp256k1(e) => e.fmt(f),
            Self::Hex(e) => e.fmt(f),
            Self::InvalidSecretKey => f.write_str("Invalid secret key"),
            Self::InvalidPublicKey => f.write_str("Invalid public key"),
        }
    }
}
```

The other candidate is `key_backup.rs:97`, where a NIP-49 decode error is interpolated into `"invalid ncryptsec: {e}"`. Also safe — `src/nips/nip49.rs:80-100`, every arm writes a fixed string, a length pair or a version byte, or delegates to `key::Error`:

```rust
            Self::TryFromSlice => f.write_str("From slice error"),
            Self::InvalidLength { expected, found } => {
                write!(f, "Invalid bytes len: expected={expected}, found={found}")
            }
            Self::UnknownVersion(v) => write!(f, "unknown version: {v}"),
```

Two facts from the sibling questions compound this for *today*: the desktop installs no `tracing` subscriber, and a packaged build's stdout is `/dev/null` ([#315](https://github.com/launchpad-26/buzz/issues/315)). There is no destination for a leak to reach.

## Part 4 — The `nsec` gap is deliberate, and telemetry widens it

`desktop/src-tauri/src/egress_guard.rs`, module documentation:

> *"Scope: `ncryptsec1` only. The raw `nsec` intentionally transits the NIP-44-encrypted pairing session (NIP-AB payload_type "nsec"); guarding it here would break pairing. Raw-key DLP is separate policy work."*

The guard matches two prefixes and nothing else:

```rust
const NCRYPTSEC_PREFIX: &str = "ncryptsec1";
const NCRYPTSEC_PREFIX_UPPER: &str = "NCRYPTSEC1";
```

A raw `nsec` on a telemetry path is caught by nothing — not by the guard as written, and not by the guard merely extended to telemetry. That scope is correct for relay egress, where pairing must keep working. It is not obviously correct for an exporter, where there is no pairing flow to break.

---

## What this means for #289

1. **A telemetry exporter is a new egress boundary that inherits no protection.** Whatever the PRD adds on the desktop should carry a guard call and an inventory row in the same change. The mechanism exists; only the knowledge that it applies was missing.
2. **The `ncryptsec`-only scope needs reconsidering for telemetry specifically.** Extending the guard while keeping that match produces a control that looks complete and misses raw keys. Whether telemetry egress should match a wider set than relay egress belongs to criterion 6's filtering policy, not to whoever writes the exporter.
3. **The window is now.** There is no destination for a desktop leak today. The first change that adds a subscriber, a log file or an exporter creates one — and #315 argues that is the cheapest first step for criterion 2. The guard question and the "just add a log file" step therefore land in the same change whether or not anyone plans it.
4. **This is a pattern, not one file.** The inventory-completeness test is a good control *because* it is narrow. Any new egress kind — exporter, log shipper, crash uploader — is invisible to it until declared.

---

## Confidence, and what was not checked

**High confidence** on the test's scope: the inventory, the needles and the absent-file default are quoted from source, and the conclusion follows from the code.

**Moderate confidence** on "no leak today" — it is a bounded search, not a proof. Checked: the print/log sites whose text names key material, `nostr::key::Error`'s `Display`, and `nip49::Error`'s `Display`.

**Not checked:** whether any of the other ~398 print sites interpolates a variable that transitively holds key material under a name the grep did not match; `egress_guard_tests.rs`'s tests other than the inventory scan; the relay side, where a client-published `ncryptsec` could appear in a relay log and no equivalent guard exists at all; the frontend, which has no guard concept; whether any Tauri command returns key material in an error string that reaches a toast; mobile, out of scope.

**Nothing here is a vulnerability report**, because nothing found is one — both interpolation sites are safe on the pinned versions. Had they not been, this would have gone to a private advisory per `launchpad/AGENTS.md` §8 rather than into a tracked document in a public repository.
