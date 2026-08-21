//! `buzz pack` subcommands — local persona pack operations.
//!
//! These commands operate on local pack directories. No relay connection needed.

use std::path::Path;

use crate::error::CliError;
use crate::PackInspectFormat;

/// Run `buzz pack validate <path>`.
///
/// Calls `validate_pack()` from the persona crate, prints diagnostics,
/// and exits with the appropriate code:
/// - 0: valid (may have warnings)
/// - 1: errors found
pub fn cmd_validate(path: &str) -> Result<(), CliError> {
    let pack_dir = Path::new(path);
    if !pack_dir.exists() {
        return Err(CliError::Usage(format!("path does not exist: {path}")));
    }
    if !pack_dir.is_dir() {
        return Err(CliError::Usage(format!("not a directory: {path}")));
    }

    let report = buzz_persona::validate::validate_pack(pack_dir);

    for diag in &report.diagnostics {
        match diag {
            buzz_persona::validate::ValidationDiagnostic::Error(msg) => {
                eprintln!("  ERROR: {msg}");
            }
            buzz_persona::validate::ValidationDiagnostic::Warning(msg) => {
                eprintln!("  WARN:  {msg}");
            }
        }
    }

    if report.has_errors() {
        return Err(CliError::Usage("Validation failed.".into()));
    } else if report.has_warnings() {
        println!("Valid (with warnings).");
    } else {
        println!("Valid.");
    }

    Ok(())
}

/// Mask MCP server env values and args before they reach `--format json`'s
/// stdout.
///
/// The human printer only ever prints an MCP server count, never `command`,
/// `args`, or `env` — so without this, JSON format would be the first thing
/// in the repo to print either literal env values or CLI arguments a pack
/// author wrote directly into `mcp_servers[]` (they're passed through
/// unresolved, not interpolated from real secrets, but a pack author can
/// write a real-looking value into either — a bare `env` map or an
/// `--api-key sk-...`-shaped arg are equally easy mistakes). Nothing in
/// buzz-acp or the #239 projector reads either field — buzz-acp's
/// `build_mcp_servers()` always spawns with an empty arg list regardless of
/// what a pack declares, and the projector script refuses to project a
/// persona whose MCP server has any args at all rather than silently
/// dropping them — so masking both costs nothing. `env` keeps its keys
/// (masks only the value half of each pair); `args` has no such non-secret
/// half, so every element is masked, with the array's length left intact so
/// a reader can still see how many there are.
fn redact_mcp_secrets(pack: &mut buzz_persona::resolve::ResolvedPack) {
    for persona in &mut pack.personas {
        for server in &mut persona.mcp_servers {
            for (_, value) in &mut server.env {
                *value = "***".to_string();
            }
            for arg in &mut server.args {
                *arg = "***".to_string();
            }
        }
    }
}

/// Run `buzz pack inspect <path>`.
///
/// Loads and resolves a pack. `format: Human` (default) pretty-prints a
/// summary of each persona's effective configuration, unchanged from before
/// this flag existed. `format: Json` emits the full `ResolvedPack` as JSON —
/// the shape a projector script (issue #239) consumes — with MCP server env
/// values and args redacted (see `redact_mcp_secrets`).
pub fn cmd_inspect(path: &str, format: &PackInspectFormat) -> Result<(), CliError> {
    let pack_dir = Path::new(path);
    if !pack_dir.exists() {
        return Err(CliError::Usage(format!("path does not exist: {path}")));
    }
    if !pack_dir.is_dir() {
        return Err(CliError::Usage(format!("not a directory: {path}")));
    }

    // Resolve the pack — shows fully effective config (post-merge, post-split).
    let pack = buzz_persona::resolve::resolve_pack(pack_dir)
        .map_err(|e| CliError::Other(format!("failed to resolve pack: {e}")))?;

    if matches!(format, PackInspectFormat::Json) {
        let mut pack = pack;
        redact_mcp_secrets(&mut pack);
        let json = serde_json::to_string_pretty(&pack)
            .map_err(|e| CliError::Other(format!("failed to serialize pack: {e}")))?;
        println!("{json}");
        return Ok(());
    }

    // Header
    println!("Pack: {} ({})", pack.name, pack.id);
    println!("Version: {}", pack.version);
    println!("Personas: {}", pack.personas.len());
    println!();

    // Per-persona summary (fully resolved effective config)
    for persona in &pack.personas {
        println!("  {}", persona.name);
        println!("    Display: {}", persona.display_name);
        println!("    Description: {}", persona.description);

        if let Some(ref llm_provider) = persona.llm_provider {
            if let Some(ref model) = persona.model {
                println!("    Model: {llm_provider}:{model}");
            } else {
                println!("    Provider: {llm_provider}");
            }
        } else if let Some(ref model) = persona.model {
            println!("    Model: {model}");
        }
        if let Some(temp) = persona.temperature {
            println!("    Temperature: {temp}");
        }
        if let Some(ctx) = persona.max_context_tokens {
            println!("    Max context tokens: {ctx}");
        }

        if !persona.subscribe.is_empty() {
            println!("    Subscribe: {}", persona.subscribe.join(", "));
        }

        let rt = &persona.triggers;
        let mut parts = Vec::new();
        if rt.mentions {
            parts.push("mentions".to_string());
        }
        if !rt.keywords.is_empty() {
            parts.push(format!("keywords {:?}", rt.keywords));
        }
        if rt.all_messages {
            parts.push("all_messages".to_string());
        }
        if !parts.is_empty() {
            println!("    Triggers: {}", parts.join(" + "));
        }

        println!("    Thread replies: {}", persona.thread_replies);
        println!("    Broadcast replies: {}", persona.broadcast_replies);

        if !persona.mcp_servers.is_empty() {
            println!("    MCP servers: {}", persona.mcp_servers.len());
        }

        if !persona.skills.is_empty() {
            println!("    Skills: {}", persona.skills.join(", "));
        }

        if let Some(ref avatar) = persona.avatar {
            println!("    Avatar: {avatar}");
        }

        let prompt_preview = if persona.system_prompt.chars().count() > 80 {
            let truncated: String = persona.system_prompt.chars().take(77).collect();
            format!("{truncated}...")
        } else {
            persona.system_prompt.clone()
        };
        println!(
            "    System prompt: {} chars ({})",
            persona.system_prompt.len(),
            prompt_preview.replace('\n', " ")
        );

        if !persona.runtime_env_vars.is_empty() {
            let env_str: Vec<String> = persona
                .runtime_env_vars
                .iter()
                .map(|(k, v)| format!("{k}={v}"))
                .collect();
            println!("    Env vars: {}", env_str.join(", "));
        }
        println!();
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn write_minimal_pack(dir: &std::path::Path) {
        std::fs::create_dir_all(dir.join(".plugin")).unwrap();
        std::fs::create_dir_all(dir.join("agents")).unwrap();
        std::fs::write(
            dir.join(".plugin/plugin.json"),
            r#"{
                "id": "com.test.cli",
                "name": "CLI Test Pack",
                "version": "0.1.0",
                "personas": ["agents/bot.persona.md"]
            }"#,
        )
        .unwrap();
        std::fs::write(
            dir.join("agents/bot.persona.md"),
            "---\nname: bot\ndisplay_name: Bot\ndescription: A test bot.\nmodel: anthropic:claude-sonnet-5\n---\nYou are Bot.\n",
        )
        .unwrap();
    }

    #[test]
    fn cmd_inspect_human_format_unchanged_default() {
        let tmp = tempfile::tempdir().unwrap();
        write_minimal_pack(tmp.path());
        // Default format (Human) must still succeed against a valid pack —
        // this is the pre-existing behavior every doc/example demonstrates.
        assert!(cmd_inspect(tmp.path().to_str().unwrap(), &PackInspectFormat::Human).is_ok());
    }

    #[test]
    fn cmd_inspect_json_format_succeeds() {
        let tmp = tempfile::tempdir().unwrap();
        write_minimal_pack(tmp.path());
        assert!(cmd_inspect(tmp.path().to_str().unwrap(), &PackInspectFormat::Json).is_ok());
    }

    #[test]
    fn cmd_inspect_missing_path_errors_for_both_formats() {
        let missing = "/nonexistent/pack/path/for/this/test";
        assert!(cmd_inspect(missing, &PackInspectFormat::Human).is_err());
        assert!(cmd_inspect(missing, &PackInspectFormat::Json).is_err());
    }

    #[test]
    fn redact_mcp_secrets_masks_env_values_and_args_keeps_env_keys() {
        let tmp = tempfile::tempdir().unwrap();
        std::fs::create_dir_all(tmp.path().join(".plugin")).unwrap();
        std::fs::create_dir_all(tmp.path().join("agents")).unwrap();
        std::fs::write(
            tmp.path().join(".plugin/plugin.json"),
            r#"{
                "id": "com.test.cli",
                "name": "CLI Test Pack",
                "version": "0.1.0",
                "personas": ["agents/bot.persona.md"]
            }"#,
        )
        .unwrap();
        std::fs::write(
            tmp.path().join("agents/bot.persona.md"),
            "---\nname: bot\ndisplay_name: Bot\ndescription: A test bot.\nmodel: anthropic:claude-sonnet-5\nmcp_servers:\n  - name: my-mcp\n    command: npx\n    args: ['--api-key', 'sk-abc123']\n    env:\n      TOKEN: abc123\n---\nYou are Bot.\n",
        )
        .unwrap();

        let mut pack = buzz_persona::resolve::resolve_pack(tmp.path()).unwrap();
        redact_mcp_secrets(&mut pack);

        let server = &pack.personas[0].mcp_servers[0];
        assert_eq!(server.env[0].0, "TOKEN");
        assert_eq!(server.env[0].1, "***");
        assert_eq!(server.args, vec!["***".to_string(), "***".to_string()]);
    }
}
