//! Provider-resolution and redaction-env tests for `agent_models_env`.
//!
//! Housed as a child of `agent_models_env` (not the shared `agent_models_tests`)
//! so these cases sit next to the code they exercise and reach its `pub(super)`
//! items directly via `use super::*` — and so the shared test file stays under
//! its size ratchet (see issue #1958).

use super::*;

#[test]
fn redaction_env_records_value_used_for_request() {
    let env = BTreeMap::from([("OPENAI_COMPAT_API_KEY".to_string(), "   ".to_string())]);

    let redaction_env =
        redaction_env_with_value(&env, "OPENAI_COMPAT_API_KEY", "inherited-process-key");

    assert_eq!(
        redaction_env
            .get("OPENAI_COMPAT_API_KEY")
            .map(String::as_str),
        Some("inherited-process-key")
    );
}

#[test]
fn effective_discovery_provider_prefers_the_explicit_provider() {
    let env = BTreeMap::from([(
        "BUZZ_AGENT_PROVIDER".to_string(),
        "databricks_v2".to_string(),
    )]);

    // A saved/selected provider is a deliberate choice and must win over the
    // build-provided default, so discovery matches what spawn will use.
    assert_eq!(
        effective_discovery_provider(Some("anthropic"), Some("BUZZ_AGENT_PROVIDER"), &env)
            .as_deref(),
        Some("anthropic")
    );
}

#[test]
fn effective_discovery_provider_recovers_baked_provider_when_record_has_none() {
    let env = BTreeMap::from([(
        "BUZZ_AGENT_PROVIDER".to_string(),
        "databricks_v2".to_string(),
    )]);

    // The regression this guards: records predating provider persistence carry
    // `provider: null`, so every discovery gate saw None and no live Databricks
    // catalog was ever fetched on builds that bake the provider in.
    for provider in [None, Some(""), Some("   ")] {
        assert_eq!(
            effective_discovery_provider(provider, Some("BUZZ_AGENT_PROVIDER"), &env).as_deref(),
            Some("databricks_v2"),
            "provider input {provider:?} must fall back to the env value"
        );
    }
}

#[test]
fn effective_discovery_provider_is_none_without_an_explicit_or_env_provider() {
    let env = BTreeMap::new();
    assert_eq!(
        effective_discovery_provider(None, Some(UNSET_PROVIDER_VAR), &env).as_deref(),
        None
    );
    // A runtime that takes no provider env var has nothing to recover from.
    assert_eq!(
        effective_discovery_provider(
            None,
            None,
            &BTreeMap::from([(UNSET_PROVIDER_VAR.to_string(), "databricks_v2".to_string())])
        )
        .as_deref(),
        None
    );
}

#[test]
fn env_derived_provider_falls_through_when_its_credential_is_missing() {
    let env = BTreeMap::from([("GOOSE_PROVIDER".to_string(), "anthropic".to_string())]);
    let inferred = effective_discovery_provider(None, Some("GOOSE_PROVIDER"), &env);
    assert_eq!(inferred.as_deref(), Some("anthropic"));

    // `export GOOSE_PROVIDER=anthropic` is goose's documented way to pick a
    // provider, and it keeps the API key in its own config/keyring rather than in
    // Buzz's env — so the provider is visible here and the credential is not.
    // Erroring would swap the working subprocess catalog for a hard
    // "config: ... required" on exactly the null-provider records this fallback
    // exists to serve; the gate has to decline instead.
    assert_eq!(inferred.required_env(&env, UNSET_CREDENTIAL), Ok(None));
}

/// A credential name no environment sets, so `required_env` is exercised without
/// depending on what the developer happens to have exported.
const UNSET_CREDENTIAL: &str = "BUZZ_TEST_UNSET_DISCOVERY_CREDENTIAL";

#[test]
fn explicit_provider_still_reports_a_missing_credential() {
    // An explicit provider is an assertion about this agent, so a missing
    // credential is a real misconfiguration and stays user-visible.
    let env = BTreeMap::new();
    let explicit = effective_discovery_provider(Some("anthropic"), Some("GOOSE_PROVIDER"), &env);
    assert_eq!(
        explicit.required_env(&env, UNSET_CREDENTIAL),
        Err(format!("config: {UNSET_CREDENTIAL} required"))
    );
}

#[test]
fn required_env_returns_a_configured_credential_however_the_provider_was_resolved() {
    let env = BTreeMap::from([
        ("GOOSE_PROVIDER".to_string(), "anthropic".to_string()),
        (
            UNSET_CREDENTIAL.to_string(),
            "  sk-configured  ".to_string(),
        ),
    ]);
    for provider in [Some("anthropic"), None] {
        let resolved = effective_discovery_provider(provider, Some("GOOSE_PROVIDER"), &env);
        assert_eq!(
            resolved.required_env(&env, UNSET_CREDENTIAL),
            Ok(Some("sk-configured".to_string())),
            "provider input {provider:?} must read the configured credential"
        );
    }
}

/// A provider env-var name no environment sets, so this test does not depend on
/// what the developer happens to have exported (e.g. `BUZZ_AGENT_PROVIDER`).
const UNSET_PROVIDER_VAR: &str = "BUZZ_TEST_UNSET_DISCOVERY_PROVIDER";

#[test]
fn effective_discovery_provider_reads_the_runtimes_own_env_var() {
    // goose keys its provider off GOOSE_PROVIDER, so a BUZZ_AGENT_PROVIDER in
    // the env must not be mistaken for this runtime's provider.
    let env = BTreeMap::from([
        ("GOOSE_PROVIDER".to_string(), "databricks".to_string()),
        (
            "BUZZ_AGENT_PROVIDER".to_string(),
            "databricks_v2".to_string(),
        ),
    ]);
    assert_eq!(
        effective_discovery_provider(None, Some("GOOSE_PROVIDER"), &env).as_deref(),
        Some("databricks")
    );
}

#[test]
fn merged_filter_value_overrides_inherited_process_value_even_when_blank() {
    let env = BTreeMap::from([("DATABRICKS_MODEL_FILTER".to_string(), "   ".to_string())]);
    assert_eq!(
        env_value_or_process_if_absent(&env, "DATABRICKS_MODEL_FILTER"),
        Some(String::new())
    );
}

#[test]
fn absent_filter_value_uses_process_value_when_available() {
    const TEST_FILTER_ENV: &str = "BUZZ_TEST_DATABRICKS_MODEL_FILTER";
    let original = std::env::var(TEST_FILTER_ENV).ok();
    std::env::set_var(TEST_FILTER_ENV, "process-*");
    let value = env_value_or_process_if_absent(&BTreeMap::new(), TEST_FILTER_ENV);
    match original {
        Some(value) => std::env::set_var(TEST_FILTER_ENV, value),
        None => std::env::remove_var(TEST_FILTER_ENV),
    }
    assert_eq!(value.as_deref(), Some("process-*"));
}

#[test]
fn openrouter_credential_redaction_env_records_key() {
    let env = BTreeMap::from([(
        "OPENROUTER_API_KEY".to_string(),
        "sk-or-v1-secret-key-12345".to_string(),
    )]);
    let redaction =
        redaction_env_with_value(&env, "OPENROUTER_API_KEY", "sk-or-v1-secret-key-12345");
    assert_eq!(
        redaction.get("OPENROUTER_API_KEY").map(String::as_str),
        Some("sk-or-v1-secret-key-12345"),
        "redaction env must record the API key for error body redaction"
    );
}
