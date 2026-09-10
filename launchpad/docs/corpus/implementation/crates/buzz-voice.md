---
id: implementation-crates-buzz-voice
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "buzz-voice's Cargo.toml describes it as \"Reusable local voice primitives for Buzz\" and its dependency list (ort, ort-sys pinned to =2.0.0-rc.12, sherpa-onnx, symphonia with format-decoder features, tokenizers, sentencepiece-model, sha2, hex, atomic-write-file, rand) is entirely ONNX-runtime inference, audio decode/resample, and local-file-storage tooling -- no HTTP client, no Nostr/relay dependency, no network dependency of any kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-voice/Cargo.toml"
  - statement: "buzz-voice is a workspace member declared at crates/buzz-voice in the root Cargo.toml."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
  - statement: "buzz-voice's public surface (lib.rs) is exactly two modules -- pub mod imported and pub mod pocket -- re-exporting april_model_info, load_text_to_speech, load_voice_style, PocketTts, VoiceStyle, DEFAULT_VOICE, SAMPLE_RATE, VOICE_FILE_EXT from pocket, plus the PocketModelArtifact type alias and the APRIL_BUNDLE_ID/APRIL_MODEL_ID/APRIL_MODEL_REVISION constants."
    entry_class: FACT
    evidence:
      - "crates/buzz-voice/src/lib.rs"
  - statement: "pocket.rs's module doc states the crate implements Kyutai's Pocket TTS (english_2026-04 bundle) via an ONNX export from KevinAHM/pocket-tts-onnx, using SentencePiece tokenization, a learned voice BOS embedding, recurrent FlowLM state, and stateful Mimi audio decoding; Buzz selects the upstream three-graph INT8-quantized variant while keeping the Mimi encoder and text conditioner full precision. Attribution: Pocket TTS/Mimi (Kyutai, CC-BY-4.0), the ONNX export (KevinAHM/pocket-tts-onnx, CC-BY-4.0), and the reference voice (Kyutai's Mary preset / VCTK p333, CC-BY-4.0)."
    entry_class: FACT
    evidence:
      - "crates/buzz-voice/src/pocket.rs"
  - statement: "pocket_models.rs pins APRIL_MODEL_ID = \"KevinAHM/pocket-tts-onnx\", APRIL_MODEL_REVISION = \"58a6d00cf13d239b6748cb0769f35c580a8f606c\", APRIL_BUNDLE_ID = \"english_2026-04\", and APRIL_MAX_TOKEN_PER_CHUNK = 50; april_model_info() returns a const PocketModelInfo naming exactly eight required artifact files (bundle.json, bos_before_voice.npy, tokenizer.model, flow_lm_main_int8.onnx, flow_lm_flow_int8.onnx, mimi_decoder_int8.onnx, mimi_encoder.onnx, text_conditioner.onnx), each with a pinned sha256 and size_bytes, and three components (flow_lm_main, flow_lm_flow, mimi_decoder) marked quantized -- mimi_encoder and text_conditioner stay full precision."
    entry_class: FACT
    evidence:
      - "crates/buzz-voice/src/pocket_models.rs"
  - statement: "load_text_to_speech(model_dir) checks that every artifact named by april_model_info() exists as a file under model_dir before constructing a PocketTts, and returns an error naming the first missing file rather than partially loading; PocketTts wraps a Mutex<AprilPocketTts> so it can be shared across threads with interior locking."
    entry_class: FACT
    evidence:
      - "crates/buzz-voice/src/pocket.rs"
  - statement: "PocketTts exposes four public synthesis-adjacent methods: split_text_into_chunks (packs sentences into the bundle's 50-token limit, used to size units for the model), split_text_for_playback (isolates the first sentence so it reaches synthesis before the remainder is packed, for faster time-to-first-audio), synth_chunk (splits then synthesizes each packed unit and concatenates PCM), and synth_chunk_streaming (same splitting, but invokes an on_audio callback with PCM deltas roughly every emit_frames of decoded audio and can be cancelled by the callback returning false)."
    entry_class: FACT
    evidence:
      - "crates/buzz-voice/src/pocket.rs"
  - statement: "A unit test (every_production_splitter_delegation_is_declared in pocket.rs) parses pocket.rs's own source at compile-checked runtime and asserts exactly which splitter (split_prompt vs split_playback_prompt) each of the four public methods calls, guarding against silently reinstating either of two previously shipped defects: losing first-sentence isolation in playback, or re-isolating an already-packed synthesis unit."
    entry_class: FACT
    evidence:
      - "crates/buzz-voice/src/pocket.rs"
  - statement: "load_voice_style(path) reads a reference-voice WAV via sherpa_onnx::Wave::read, rejects an empty sample buffer, and returns a VoiceStyle carrying the raw samples and the WAV's own sample rate -- it performs no resampling or validation beyond emptiness; VoiceStyle's Debug/Clone derive and its two private fields (samples, sample_rate) are the crate's only public voice-conditioning input type."
    entry_class: FACT
    evidence:
      - "crates/buzz-voice/src/pocket.rs"
  - statement: "AprilPocketTts::load (pocket_april.rs) validates the loaded bundle.json against the exact expected shape for the english_2026-04 model before constructing any ONNX session: schema_version must equal 2, language must equal \"english_2026-04\", sample_rate/frame_rate/samples_per_frame/latent_dim/conditioning_dim must equal 24000/12.5/1920/32/1024 exactly, insert_bos_before_voice must be true, and pad_with_spaces_for_short_inputs/remove_semicolons/model_recommended_frames_after_eos/max_token_per_chunk must all match the one supported policy (false/false/None/50) -- any mismatch is a load-time error naming the field, not a silent fallback."
    entry_class: FACT
    evidence:
      - "crates/buzz-voice/src/pocket_april.rs"
  - statement: "AprilPocketTts holds five loaded ONNX Sessions (mimi_encoder, text_conditioner, flow_main, flow, mimi_decoder), the parsed Bundle manifest, a SentencePiece-derived Tokenizer, the BOS embedding vector, and two content-keyed caches (cached_voice for Mimi-encoder voice embeddings, cached_conditioning for post-condition_voice Flow LM recurrent state) -- both caches are explicitly keyed by a content hash of the voice sample buffer plus its length and rate (voice_key), documented in-source as deliberately NOT keyed by buffer address, because voice switching can hand a new voice's samples the same address a previous voice's buffer held."
    entry_class: FACT
    evidence:
      - "crates/buzz-voice/src/pocket_april.rs"
  - statement: "load_session (pocket_april.rs) builds each ONNX Runtime session with with_intra_threads(num_threads) and with_inter_threads(1); tts_num_threads() (pocket.rs) reads BUZZ_TTS_THREADS to override the production default of 1 intra-op thread, documented in-source as EXPERIMENTAL for latency tuning."
    entry_class: FACT
    evidence:
      - "crates/buzz-voice/src/pocket_april.rs"
      - "crates/buzz-voice/src/pocket.rs"
  - statement: "imported.rs's PocketVoiceLibrary manages a device-local registry (registry.json, versioned, schema version 1) of user-imported reference voices under a caller-supplied root directory; import_path() rejects sources over 25 MB (MAX_SOURCE_BYTES), decodes WAV natively (decode_wav, a hand-rolled RIFF/WAVE parser) or via symphonia for m4a/mp3/flac/ogg/oga/aif/aiff, resamples to a fixed CANONICAL_SAMPLE_RATE of 32,000 Hz (resample_linear, simple linear interpolation), re-encodes as 16-bit PCM WAV, content-hashes the canonical bytes with SHA-256, and uses that hash as both the registry key (\"pocket:imported:<hash>\") and the stored file name -- so identical audio content always imports idempotently to the same entry regardless of source file name or format."
    entry_class: FACT
    evidence:
      - "crates/buzz-voice/src/imported.rs"
  - statement: "decode_wav and decode_media both reject audio shorter than 2.0 s or longer than 30.0 s (MIN/MAX_DURATION_SECONDS), reject a sample rate outside 8,000-96,000 Hz, reject more than 8 channels, downmix to mono by averaging channels, and reject the result if PcmStats::analyze reports it as silent (peak < 0.001, RMS < 0.0001, or zero non-silent samples) -- these checks run before any content reaches the registry or disk, and a rejected import leaves the registry file untouched."
    entry_class: FACT
    evidence:
      - "crates/buzz-voice/src/imported.rs"
  - statement: "PocketVoiceLibrary's on-disk writes are hardened: ensure_storage_dir sets the storage directory to mode 0o700 and atomic_write_restricted (registry.json and imported audio) sets file mode 0o600 and writes via atomic-write-file's AtomicWriteFile, both gated #[cfg(unix)]; resolve_file and the import path's re-verification of an already-existing file both call is_regular_file_without_symlink (via fs::symlink_metadata) before reading, refusing a symlinked entry outright; a failed registry save after writing new audio bytes triggers cleanup of the just-written file (import_path), and a failed audio-file deletion after removing a registry entry restores the previous in-memory registry to disk (delete) rather than leaving the two inconsistent."
    entry_class: FACT
    evidence:
      - "crates/buzz-voice/src/imported.rs"
  - statement: "buzz-voice ships two test files: pocket.rs and pocket_models.rs and imported.rs each carry #[cfg(test)] unit tests exercising bundle metadata invariants, splitter delegation, WAV encode/decode round-trips, symlink/registry edge cases, and PCM silence analysis; crates/buzz-voice/tests/pocket_import_audio.rs is a single integration test (#[ignore = \"requires BUZZ_POCKET_MODEL_DIR and runs the installed Pocket ONNX model\"]) that imports a checked-in voice fixture (desktop/src-tauri/resources/pocket-voices/eve.wav), synthesizes preview audio with both the imported voice and the built-in Mary fallback, asserts the output is non-silent and long enough, writes WAV evidence files, and asserts the Mary fallback path resolves to reference_sample.wav -- this test is not run by default because it requires a real downloaded model directory."
    entry_class: FACT
    evidence:
      - "crates/buzz-voice/src/pocket.rs"
      - "crates/buzz-voice/src/pocket_models.rs"
      - "crates/buzz-voice/tests/pocket_import_audio.rs"
  - statement: "Also #[ignore]-gated: pocket.rs's production_api_emits_non_silent_april_int8_pcm (requires BUZZ_POCKET_TEST_MODEL_DIR) and imported.rs's imports_common_audio_format_fixtures (requires BUZZ_VOICE_IMPORT_TEST_DIR) -- both need externally supplied model or fixture directories not present in CI by default, so buzz-voice's default `cargo test` run exercises unit-level logic (splitting, bundle validation, WAV codec, registry persistence) but not an actual ONNX inference pass."
    entry_class: FACT
    evidence:
      - "crates/buzz-voice/src/pocket.rs"
      - "crates/buzz-voice/src/imported.rs"
  - statement: "desktop/src-tauri/Cargo.toml declares buzz_voice_pkg as package \"buzz-voice\" at path ../../crates/buzz-voice -- the only crate in the workspace that depends on buzz-voice, confirmed by grep across every crates/*/Cargo.toml finding no other dependent."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml"
      - "grep(pattern='buzz-voice', path='crates/*/Cargo.toml') -> only crates/buzz-voice/Cargo.toml itself (its own package name/description), no other crate depends on it"
  - statement: "desktop/src-tauri/src/huddle/pocket.rs re-exports buzz_voice_pkg::pocket::* (pub use) plus april_model_info/PocketModelArtifact/APRIL_BUNDLE_ID/APRIL_MODEL_ID/APRIL_MODEL_REVISION as pub(crate); desktop/src-tauri/src/huddle/tts_voice_import.rs imports buzz_voice_pkg::imported::{ImportedVoice, PocketVoiceLibrary} directly and wraps them with Tauri AppHandle-scoped path resolution (voices_dir, load_registry, resolve_file, delete) -- these two files are the crate's only consumers."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/huddle/pocket.rs"
      - "desktop/src-tauri/src/huddle/tts_voice_import.rs"
  - statement: "desktop/src-tauri/src/huddle/models.rs (module doc: \"Model download manager for STT (Parakeet TDT-CTC 110M) and TTS (Pocket TTS) models\") owns fetching april_model_info()'s named artifacts over HTTP, verifying their pinned sha256 hashes, caching them under ~/.buzz/models/, writing a version manifest to force re-download on upgrade, and writing CC-BY-4.0 attribution sidecars beside the cached bytes -- buzz-voice itself performs no network I/O and no download; it only supplies the static artifact list (filenames, hashes, sizes) that models.rs downloads against and load_text_to_speech's own existence check that the named files are present before constructing a session."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/huddle/models.rs"
      - "crates/buzz-voice/src/pocket.rs"
      - "crates/buzz-voice/src/pocket_models.rs"
  - statement: "The desktop huddle module (desktop/src-tauri/src/huddle/) contains over 25 files with tts_*.rs and stt.rs/transcription.rs/agent_tts_*.rs prefixes covering STT/TTS pipeline orchestration, playback, streaming, activity/barge-in detection, voice-turn routing, and jitter/reconnect handling -- none of these import buzz_voice_pkg (only pocket.rs and tts_voice_import.rs do, per the grep above), so this orchestration logic is desktop-owned, not part of buzz-voice's own responsibility."
    entry_class: FACT
    evidence:
      - "grep(pattern='buzz_voice_pkg', path='desktop/src-tauri/src/**/*.rs') -> matches only desktop/src-tauri/src/huddle/pocket.rs and desktop/src-tauri/src/huddle/tts_voice_import.rs"
  - statement: "The corpus node architecture-context-external-services (merged on origin/launchpad) already states, in its own Scope and omissions section, that buzz-voice was checked and deliberately excluded from that node's external-system inventory because its PocketTts primitives load a bundled, on-device model rather than calling a network service."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/context/external-services.md"
  - statement: "The corpus node architecture-flows-huddle-audio (merged on origin/launchpad) documents crates/buzz-relay/src/audio/'s real-time WebSocket Opus relay for huddle voice channels -- a distinct system from buzz-voice: huddle-audio's own Scope and omissions table lists \"Agent-side STT/TTS integration for huddle participation\" as not yet a corpus node, confirming that huddle-audio does not already cover buzz-voice's subject matter and that the two crates (buzz-relay's audio module and buzz-voice) are unrelated code paths despite both concerning voice."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/huddle-audio.md"
  - statement: "No ADR under launchpad/decisions/, no NIP under docs/nips/, and no existing corpus node names a \"Pocket TTS\" or \"buzz-voice\" contract/specification for this crate to realize -- checked by grep across launchpad/decisions/ and docs/nips/ for \"pocket\"/\"tts\"/\"voice\"/\"buzz-voice\" (case-insensitive) and by the git ls-tree of launchpad/docs/corpus at the recorded revision, which lists no implementation/ subtree prior to this node."
    entry_class: FACT
    evidence:
      - "grep(pattern='(?i)pocket|buzz-voice|text-to-speech', path='launchpad/decisions/**') -> no matches"
      - "git_ls_tree(ref='HEAD', path='launchpad/docs/corpus') -> no implementation/ subtree present before this node"
  - statement: "Issue #940's Definition of Done requires this node to state implementation responsibility and what it deliberately does not own, name public interfaces/entry points and important dependencies, and link owned source paths and representative tests -- this is the acceptance bar this node is built against."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#940 definition of done"
---

# buzz-voice: implementation reference

`crates/buzz-voice` is a local, on-device text-to-speech engine for Buzz Desktop's
huddle voice pipeline: it loads Kyutai's Pocket TTS model (`english_2026-04` bundle,
INT8-quantized, exported to ONNX) via `sherpa-onnx`/`ort`, synthesizes PCM audio from
text conditioned on a reference voice sample, and separately manages a local library
of user-imported reference voices. It has no wire-level protocol, ADR, or NIP that it
realizes -- its only "target" is its own crate contract, consumed by exactly one
caller (`desktop/src-tauri`). It is unrelated to `buzz-relay`'s real-time huddle audio
*relay* (`crates/buzz-relay/src/audio/`, documented at `architecture-flows-huddle-audio`)
despite both concerning voice: that crate moves live Opus frames between WebSocket
peers over the network; this crate runs offline model inference on one machine.

## Target

There is no external spec, ADR, or NIP this crate implements -- checked directly
against `launchpad/decisions/`, `docs/nips/`, and the corpus tree at the recorded
revision, none of which name a Pocket TTS or `buzz-voice` contract. The crate's
"target" is its own public Rust API (`crates/buzz-voice/src/lib.rs`) and the
`english_2026-04` bundle's own `bundle.json` manifest contract, which
`AprilPocketTts::load` (`crates/buzz-voice/src/pocket_april.rs`) validates field-by-field
at load time. No `implements` relationship is declared in this node's front matter for
that reason -- see *Relationships* below.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `crates/buzz-voice/src/lib.rs` | Crate's public API surface | Re-exports `pocket` and `imported` modules; no logic of its own |
| `crates/buzz-voice/src/pocket.rs` — `PocketTts`, `load_text_to_speech`, `load_voice_style` | The crate's synthesis entry points | `split_text_into_chunks`/`split_text_for_playback`/`synth_chunk`/`synth_chunk_streaming` |
| `crates/buzz-voice/src/pocket_models.rs` — `april_model_info`, `PocketModelInfo`, `PocketModelArtifact` | Immutable bundle metadata: pinned model id/revision, 8 required artifact files with sha256 + size, which components are INT8-quantized | Data only, no I/O |
| `crates/buzz-voice/src/pocket_april.rs` — `AprilPocketTts` (crate-private) | The ONNX inference engine: bundle validation, tokenization, voice conditioning, Flow LM generation loop, Mimi decode, text-splitting-at-natural-boundaries | Not part of the public API; reached only through `PocketTts` |
| `crates/buzz-voice/src/imported.rs` — `PocketVoiceLibrary`, `PcmStats`, `write_pcm16_wav` | Device-local imported-voice registry: validate, canonicalize (resample to 32 kHz mono PCM16), content-hash, persist, delete | Independent of the TTS engine; only shares `VoiceStyle`'s data shape by convention |
| `desktop/src-tauri/src/huddle/pocket.rs` | Consumer: re-exports `buzz_voice_pkg::pocket::*` into the desktop crate | Outside this crate; cited for the boundary, not as buzz-voice's own surface |
| `desktop/src-tauri/src/huddle/tts_voice_import.rs` | Consumer: wraps `PocketVoiceLibrary`/`ImportedVoice` with Tauri `AppHandle`-scoped paths | Outside this crate; cited for the boundary |
| `desktop/src-tauri/src/huddle/models.rs` | Consumer: downloads/verifies/caches the artifacts `april_model_info()` names, writes CC-BY-4.0 attribution sidecars | Outside this crate; buzz-voice performs no network I/O itself |

## Divergences

None found, checked against: the crate's own `bundle.json` validation logic in
`AprilPocketTts::load` (which fails closed on any mismatch against the
`english_2026-04` bundle's expected shape, rather than silently tolerating drift),
the module doc's stated attribution/licensing claims (Kyutai, KevinAHM's ONNX export,
both CC-BY-4.0 — matched against the pinned `APRIL_MODEL_ID`/`APRIL_MODEL_REVISION`
constants), and the crate's own test suite (`every_production_splitter_delegation_is_declared`
and `engine_splitters_keep_opposite_isolation_polarity`, both of which parse the crate's
own source at test time specifically to catch a production function's behavior
drifting from its documented contract). Because there is no external spec this crate
implements (see *Target*), "divergence" here means only internal
contract-vs-implementation consistency, not conformance to an outside specification —
that is a narrower question than a typical `implements`-typed node answers, and is
named as such rather than left implicit.

## Verification

- **Unit tests**, run by default (`cargo test -p buzz-voice`): bundle-metadata
  invariants (`pocket_models.rs::tests::metadata_matches_pinned_int8_layout`),
  splitter delegation and its opposite-polarity check (`pocket.rs::tests`,
  `pocket_april.rs::tests`), WAV encode/decode round-trips, symlink/registry edge
  cases, and PCM silence analysis (`imported.rs::tests`, including
  `imports_persists_reloads_and_deletes_canonical_voice`,
  `common_stereo_audio_is_downmixed_to_canonical_mono`,
  `invalid_unsupported_and_silent_files_do_not_mutate_registry`,
  `pcm_analysis_distinguishes_signal_from_silence`).
- **Ignored integration tests**, not run by default: `pocket.rs`'s
  `production_api_emits_non_silent_april_int8_pcm` (needs `BUZZ_POCKET_TEST_MODEL_DIR`),
  `imported.rs`'s `imports_common_audio_format_fixtures` (needs
  `BUZZ_VOICE_IMPORT_TEST_DIR`), and
  `crates/buzz-voice/tests/pocket_import_audio.rs`'s
  `objective_import_synthesis_delete_and_mary_fallback` (needs `BUZZ_POCKET_MODEL_DIR`;
  imports a checked-in fixture voice, synthesizes with it and with the Mary fallback,
  and asserts non-silent, sufficiently long output plus WAV evidence written to disk).
  All three require an externally supplied model or fixture directory not present in
  CI by default, so **no automated run in this repository currently exercises a real
  ONNX inference pass through this crate** — coverage of the actual synthesis output
  (versus the surrounding validation/splitting/registry logic, which unit tests do
  cover) depends on a developer or CI job supplying those environment variables.
- **No CI job configuration was inspected** to confirm whether any pipeline sets these
  variables; this is named as unverified below rather than assumed either way.

## Relationships

**Declared: none.** Checked against `git ls-tree -r --name-only HEAD -- launchpad/docs/corpus`
at the recorded revision:

- **No `implements` edge.** No ADR, NIP, or existing corpus node describes a
  Pocket-TTS/`buzz-voice` contract this crate would realize (see *Target*). Per the
  template's own rule, an edge to a nonexistent target is a hard validation error, not
  a soft placeholder, so none is declared.
- **No `part-of` edge.** No broader implementation-reference node for
  `desktop/src-tauri` or the huddle module exists yet on `origin/launchpad` for this
  to sit under.
- **No `references` edge**, despite two merged nodes discussing this crate in prose
  (`architecture-context-external-services`, which excludes it from that node's
  external-system inventory, and `architecture-flows-huddle-audio`, which documents
  the unrelated real-time relay crate) — neither is a verification/test-strategy node,
  which is what `references` is for per the template. Both are cited directly in this
  node's evidence ledger and prose instead, which states the connection honestly
  without stretching a relationship type past its intended use.
- **The first future edge worth adding**, once such a node exists, is a `part-of`
  toward a `desktop`/huddle-module implementation-reference node — this crate's own
  entry points (`pocket.rs`, `tts_voice_import.rs` on the desktop side) would then sit
  under it as one sub-component among the huddle module's several.

## Scope and omissions

**This node covers** what `crates/buzz-voice` is responsible for (local Pocket TTS
synthesis and local imported-voice-registry management), its public entry points and
important dependencies, its owned source paths and representative tests, and its one
real consumer (`desktop/src-tauri`), including the explicit boundary between what this
crate owns (inference, validation, registry persistence) and what the desktop huddle
module owns instead (model download/caching/attribution, playback, streaming
orchestration, activity/barge-in detection).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `desktop/src-tauri/src/huddle/tts_*.rs`'s own TTS pipeline orchestration, playback, streaming, and activity/barge-in logic | Not yet a corpus node; desktop-app implementation surface, out of scope for this crate-level reference |
| Model download, caching, version-manifest, and attribution-sidecar logic | `desktop/src-tauri/src/huddle/models.rs`; not yet a corpus node |
| `crates/buzz-relay/src/audio/`'s real-time WebSocket huddle audio relay | `architecture-flows-huddle-audio` — a distinct system, unrelated to this crate despite the shared "voice" domain word |
| STT (speech-to-text, e.g. `desktop/src-tauri/src/huddle/stt.rs`, Parakeet TDT-CTC) | Not covered by this crate at all; `buzz-voice` is TTS- and imported-voice-registry-only |
| ONNX Runtime's / `sherpa-onnx`'s / `ort`'s own internals | Third-party dependencies; used, not implemented, by this crate |

**Expected but not verified when this node was written:**

- **No CI job configuration was inspected** to determine whether `BUZZ_POCKET_MODEL_DIR`,
  `BUZZ_POCKET_TEST_MODEL_DIR`, or `BUZZ_VOICE_IMPORT_TEST_DIR` are ever set in an
  automated pipeline; the honest current claim is that the crate's default test run
  exercises no real ONNX inference, not that no such run ever happens anywhere.
- **The desktop huddle module's `tts_*.rs` files were surveyed by directory listing
  and by confirming which files import `buzz_voice_pkg` (only two do), not read
  file-by-file.** Their own responsibilities are named only insofar as needed to state
  the boundary; a future desktop/huddle-module implementation-reference node is where
  their internals belong.
- **`sherpa-onnx`'s `Wave`/`LinearResampler` types and `ort`'s `Session`/`Tensor` API
  were read only as far as `buzz-voice`'s own call sites required**, not inspected as
  independent library internals.
