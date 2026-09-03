//! Discovery-config resolution tests for `agent_models_discovery_config`.
//!
//! Housed as a child of `agent_models_discovery_config` (not the shared
//! `agent_models_tests`) so these cases sit next to the code they exercise and
//! reach its `pub(super)` items directly via `use super::*` — and so the
//! shared test file stays under its size ratchet (see issue #1958).

use super::*;

#[test]
fn saved_agent_model_discovery_uses_record_snapshot_for_definition_less_agent() {
    let record: crate::managed_agents::ManagedAgentRecord = serde_json::from_str(
        r#"{
            "pubkey": "abcd1234",
            "name": "test-agent",
            "private_key_nsec": "nsec1fake",
            "relay_url": "wss://localhost:3000",
            "acp_command": "buzz-acp",
            "agent_command": "goose",
            "agent_command_override": "goose",
            "agent_args": [],
            "mcp_command": "",
            "turn_timeout_seconds": 320,
            "system_prompt": null,
            "model": "record-model",
            "provider": "databricks",
            "env_vars": {
                "OPENAI_API_KEY": "record-key",
                "BUZZ_PRIVATE_KEY": "must-not-leak"
            },
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "last_started_at": null,
            "last_stopped_at": null,
            "last_exit_code": null,
            "last_error": null
        }"#,
    )
    .expect("sample managed agent record");

    // agent_model_discovery_config is the single helper get_agent_models
    // consumes — verify it layers env correctly, strips reserved keys, and
    // keeps the record's own model/provider for a definition-less instance
    // (matching spawn's `resolve_definition_less` arm).
    let discovery = agent_model_discovery_config(&record, &[], &Default::default())
        .expect("discovery config should resolve for a valid record");

    assert_eq!(discovery.command.as_str(), "goose");
    assert_eq!(discovery.model.as_deref(), Some("record-model"));
    assert_eq!(discovery.provider.as_deref(), Some("databricks"));
    assert_eq!(
        discovery.env.get("GOOSE_MODEL").map(String::as_str),
        Some("record-model")
    );
    assert_eq!(
        discovery.env.get("GOOSE_PROVIDER").map(String::as_str),
        Some("databricks")
    );
    assert_eq!(
        discovery.env.get("OPENAI_API_KEY").map(String::as_str),
        Some("record-key")
    );
    // Reserved keys are stripped from the descriptor env.
    assert!(!discovery.env.contains_key("BUZZ_PRIVATE_KEY"));
    // The provider env var is recovered from the runtime metadata for the
    // effective command (the old SavedAgentModelDiscoveryConfig.provider_env_var).
    assert_eq!(discovery.provider_env_var, Some("GOOSE_PROVIDER"));
}

/// Definition-authoritative: a linked agent's stale materialized
/// `record.model`/`record.provider` must never drive model discovery — the
/// linked definition's current model/provider wins, mirroring spawn's
/// `resolve_effective_model_provider`.
#[test]
fn model_discovery_ignores_stale_record_for_linked_agent() {
    let record: crate::managed_agents::ManagedAgentRecord = serde_json::from_str(
        r#"{
            "pubkey": "abcd1234",
            "name": "test-agent",
            "persona_id": "persona-1",
            "private_key_nsec": "nsec1fake",
            "relay_url": "wss://localhost:3000",
            "acp_command": "buzz-acp",
            "agent_command": "goose",
            "agent_args": [],
            "mcp_command": "",
            "turn_timeout_seconds": 320,
            "system_prompt": null,
            "model": "stale-record-model",
            "provider": "stale-record-provider",
            "env_vars": {},
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "last_started_at": null,
            "last_stopped_at": null,
            "last_exit_code": null,
            "last_error": null
        }"#,
    )
    .expect("sample managed agent record");

    let persona = crate::managed_agents::AgentDefinition {
        id: "persona-1".to_string(),
        display_name: "Persona".to_string(),
        avatar_url: None,
        system_prompt: "You are a persona.".to_string(),
        runtime: Some("goose".to_string()),
        model: Some("persona-model".to_string()),
        provider: Some("anthropic".to_string()),
        name_pool: Vec::new(),
        is_builtin: false,
        is_active: true,
        shared: false,
        source_team: None,
        source_team_persona_slug: None,
        catalog_source: None,
        team_catalog_source: None,
        env_vars: BTreeMap::new(),
        respond_to: None,
        respond_to_allowlist: Vec::new(),
        parallelism: None,
        created_at: "".to_string(),
        updated_at: "".to_string(),
    };

    // agent_model_discovery_config is the single helper get_agent_models
    // consumes — the stale record bytes must lose to the persona's current
    // model/provider (the same authoritative resolver spawn uses).
    let personas = [persona];
    let global = crate::managed_agents::GlobalAgentConfig::default();
    let discovery = agent_model_discovery_config(&record, &personas, &global)
        .expect("discovery config should resolve for a linked record");
    assert_eq!(discovery.model.as_deref(), Some("persona-model"));
    assert_eq!(discovery.provider.as_deref(), Some("anthropic"));

    // And the discovery env comes from the descriptor, whose layering also
    // resolves through the definition — the derived model env var must carry
    // the persona's model, not the stale record snapshot.
    assert_eq!(
        discovery.env.get("GOOSE_MODEL").map(String::as_str),
        Some("persona-model")
    );
    assert_eq!(
        discovery.env.get("GOOSE_PROVIDER").map(String::as_str),
        Some("anthropic")
    );
}

#[test]
fn openrouter_saved_agent_model_discovery_resolves_provider() {
    let record: crate::managed_agents::ManagedAgentRecord = serde_json::from_str(
        r#"{
            "pubkey": "abcd1234",
            "name": "test-agent",
            "private_key_nsec": "nsec1fake",
            "relay_url": "wss://localhost:3000",
            "acp_command": "buzz-acp",
            "agent_command": "buzz-agent",
            "agent_command_override": "buzz-agent",
            "agent_args": [],
            "mcp_command": "",
            "turn_timeout_seconds": 320,
            "system_prompt": null,
            "model": "anthropic/claude-sonnet-4",
            "provider": "openrouter",
            "env_vars": {
                "OPENROUTER_API_KEY": "sk-or-test-key",
                "BUZZ_PRIVATE_KEY": "must-not-leak"
            },
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "last_started_at": null,
            "last_stopped_at": null,
            "last_exit_code": null,
            "last_error": null
        }"#,
    )
    .expect("sample openrouter managed agent record");

    let discovery = agent_model_discovery_config(
        &record,
        &[],
        &crate::managed_agents::GlobalAgentConfig::default(),
    )
    .expect("discovery config should resolve for an openrouter record");
    assert_eq!(discovery.provider.as_deref(), Some("openrouter"));
    assert_eq!(
        discovery.model.as_deref(),
        Some("anthropic/claude-sonnet-4")
    );
    assert_eq!(
        discovery.env.get("OPENROUTER_API_KEY").map(String::as_str),
        Some("sk-or-test-key")
    );
    assert!(!discovery.env.contains_key("BUZZ_PRIVATE_KEY"));
}

/// B5/T4: unsaved-agent ("draft") discovery mirrors the saved-agent path —
/// `draft_agent_model_discovery_env` must derive the provider env var from
/// form input the same way `agent_model_discovery_config` derives it from a
/// persisted record's harness descriptor, and preserve caller-supplied env
/// (including the OpenRouter API key) unmodified.
#[test]
fn openrouter_draft_agent_model_discovery_derives_provider_env() {
    let env_vars = BTreeMap::from([(
        "OPENROUTER_API_KEY".to_string(),
        "sk-or-draft-key".to_string(),
    )]);

    let merged = draft_agent_model_discovery_env(
        "buzz-agent",
        Some("openrouter"),
        &BTreeMap::new(),
        &env_vars,
    );

    assert_eq!(
        merged.get("BUZZ_AGENT_PROVIDER").map(String::as_str),
        Some("openrouter"),
        "provider env var must be derived from form input for a known ACP runtime"
    );
    assert_eq!(
        merged.get("OPENROUTER_API_KEY").map(String::as_str),
        Some("sk-or-draft-key"),
        "caller-supplied env vars must survive the merge"
    );
}

#[test]
fn draft_agent_model_discovery_env_omits_provider_when_absent() {
    let merged =
        draft_agent_model_discovery_env("buzz-agent", None, &BTreeMap::new(), &BTreeMap::new());
    assert!(
        !merged.contains_key("BUZZ_AGENT_PROVIDER"),
        "no provider must be derived when the caller supplies none"
    );
}

/// The three-tier precedence this merge exists to preserve: main's inline
/// `derived → definition_env → env_vars` layering was folded into
/// `draft_agent_model_discovery_env`, so pin the order at every collision
/// boundary rather than trusting the two single-tier tests above.
///
/// `SHARED` collides across all three tiers, so the user value proves the
/// full chain; the pairwise keys prove each adjacent boundary independently
/// (a merge that dropped only the middle tier would still satisfy `SHARED`).
/// `BUZZ_PRIVATE_KEY` proves a reserved key cannot ride in on a harness
/// definition, which is the tier a user never types.
#[test]
fn draft_agent_model_discovery_env_layers_all_three_tiers_in_order() {
    // Tier 2 (middle): harness definition env — overlays the runtime-derived
    // floor, loses to user env.
    let definition_env = BTreeMap::from([
        ("SHARED".to_string(), "from-definition".to_string()),
        // Collides with tier 1: `buzz-agent`'s own provider env var, which the
        // `provider` argument derives below.
        ("BUZZ_AGENT_PROVIDER".to_string(), "openai".to_string()),
        ("USER_OVER_DEF".to_string(), "from-definition".to_string()),
        ("DEFINITION_ONLY".to_string(), "from-definition".to_string()),
        // Reserved: must never reach the child, even from a definition.
        ("BUZZ_PRIVATE_KEY".to_string(), "must-not-leak".to_string()),
    ]);
    // Tier 3 (top): user-entered env — wins over everything.
    let env_vars = BTreeMap::from([
        ("SHARED".to_string(), "from-user".to_string()),
        ("USER_OVER_DEF".to_string(), "from-user".to_string()),
        ("USER_ONLY".to_string(), "from-user".to_string()),
    ]);

    // Tier 1 (floor): `Some("openrouter")` derives BUZZ_AGENT_PROVIDER.
    let merged = draft_agent_model_discovery_env(
        "buzz-agent",
        Some("openrouter"),
        &definition_env,
        &env_vars,
    );

    let expected: &[(&str, Option<&str>)] = &[
        // Collides in all three tiers — the top tier wins.
        ("SHARED", Some("from-user")),
        // Tier 2 over tier 1: the definition's value survives, proving the
        // derived provider is the floor and not layered on top.
        ("BUZZ_AGENT_PROVIDER", Some("openai")),
        // Tier 3 over tier 2.
        ("USER_OVER_DEF", Some("from-user")),
        // Single-tier keys pass through untouched.
        ("DEFINITION_ONLY", Some("from-definition")),
        ("USER_ONLY", Some("from-user")),
        // Reserved keys never survive the definition tier. Doubly enforced —
        // the explicit `is_reserved_env_key` filter here and `merged_user_env`'s
        // own `retain` — so this pins the contract, not either mechanism.
        ("BUZZ_PRIVATE_KEY", None),
    ];
    for (key, want) in expected {
        assert_eq!(
            merged.get(*key).map(String::as_str),
            *want,
            "env key `{key}` must resolve to {want:?} after three-tier layering"
        );
    }
}
