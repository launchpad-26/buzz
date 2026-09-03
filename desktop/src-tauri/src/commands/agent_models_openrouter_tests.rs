//! Filter and URL-derivation tests for `agent_models_openrouter`.
//!
//! Housed as a child of `agent_models_openrouter` (not the shared
//! `agent_models_tests`) so these cases sit next to the code they exercise and
//! reach its `pub(super)` items directly via `use super::*` — and so the
//! shared test file stays under its size ratchet (see issue #1958).

use super::*;

// ---------------------------------------------------------------------------
// OpenRouter provider
// ---------------------------------------------------------------------------

#[test]
fn is_openrouter_provider_matches() {
    assert!(is_openrouter_provider(Some("openrouter")));
    assert!(is_openrouter_provider(Some("  OpenRouter  ")));
    assert!(!is_openrouter_provider(Some("openai")));
    assert!(!is_openrouter_provider(Some("anthropic")));
    assert!(!is_openrouter_provider(None));
}

#[test]
fn openrouter_models_url_uses_default_base_url() {
    assert_eq!(
        openrouter_models_url(&BTreeMap::new()),
        "https://openrouter.ai/api/v1/models"
    );
}

#[test]
fn openrouter_models_url_respects_custom_base_url() {
    let env = BTreeMap::from([(
        "OPENROUTER_BASE_URL".to_string(),
        "https://eu.openrouter.ai/api/v1".to_string(),
    )]);
    assert_eq!(
        openrouter_models_url(&env),
        "https://eu.openrouter.ai/api/v1/models"
    );
}

#[test]
fn openrouter_models_url_strips_trailing_slash() {
    let env = BTreeMap::from([(
        "OPENROUTER_BASE_URL".to_string(),
        "https://proxy.example.com/api/v1/".to_string(),
    )]);
    assert_eq!(
        openrouter_models_url(&env),
        "https://proxy.example.com/api/v1/models"
    );
}

#[test]
fn openrouter_filter_keeps_tools_capable_models() {
    let response = OpenRouterModelListResponse {
        data: vec![
            OpenRouterModelListItem {
                id: "anthropic/claude-opus-4-7".to_string(),
                supported_parameters: vec!["tools".to_string(), "reasoning".to_string()],
            },
            OpenRouterModelListItem {
                id: "openai/gpt-5.5-pro".to_string(),
                supported_parameters: vec!["tools".to_string()],
            },
            OpenRouterModelListItem {
                id: "meta-llama/llama-no-tools".to_string(),
                supported_parameters: vec!["temperature".to_string()],
            },
        ],
    };
    let result = filter_openrouter_models(response, None).unwrap().unwrap();
    let ids: Vec<_> = result.models.iter().map(|m| m.id.as_str()).collect();
    assert_eq!(ids, vec!["anthropic/claude-opus-4-7", "openai/gpt-5.5-pro"]);
}

#[test]
fn openrouter_filter_excludes_absent_supported_parameters() {
    let response: OpenRouterModelListResponse =
        serde_json::from_str(r#"{"data": [{"id": "model-no-params"}]}"#).unwrap();
    assert!(
        response.data[0].supported_parameters.is_empty(),
        "absent supported_parameters must default to empty vec"
    );
    let result = filter_openrouter_models(response, None);
    assert!(
        result.is_err(),
        "models with no supported_parameters must be excluded"
    );
    assert!(
        result.unwrap_err().contains("no tools-capable models"),
        "error must indicate no tools-capable models"
    );
}

#[test]
fn openrouter_filter_excludes_empty_supported_parameters() {
    let response = OpenRouterModelListResponse {
        data: vec![OpenRouterModelListItem {
            id: "model-empty-params".to_string(),
            supported_parameters: Vec::new(),
        }],
    };
    let result = filter_openrouter_models(response, None);
    assert!(result.is_err());
    assert!(result.unwrap_err().contains("no tools-capable models"));
}

#[test]
fn openrouter_filter_empty_result_returns_error() {
    let response = OpenRouterModelListResponse { data: Vec::new() };
    let result = filter_openrouter_models(response, None);
    assert!(result.is_err());
    assert!(result.unwrap_err().contains("no tools-capable models"));
}

#[test]
fn openrouter_filter_preserves_selected_model() {
    let response = OpenRouterModelListResponse {
        data: vec![OpenRouterModelListItem {
            id: "openai/gpt-5.5-pro".to_string(),
            supported_parameters: vec!["tools".to_string()],
        }],
    };
    let result = filter_openrouter_models(response, Some("openai/gpt-5.5-pro".to_string()))
        .unwrap()
        .unwrap();
    assert_eq!(result.selected_model.as_deref(), Some("openai/gpt-5.5-pro"));
}
