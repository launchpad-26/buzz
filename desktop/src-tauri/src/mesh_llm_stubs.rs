use tauri::State;

use crate::app_state::AppState;

type CmdResult<T> = Result<T, String>;

/// Stub counterpart of `commands::mesh_llm::mesh_llm_feature_enabled` — see
/// that function's doc comment for why this exists (#269).
#[tauri::command]
pub fn mesh_llm_feature_enabled() -> bool {
    false
}

#[tauri::command]
pub async fn mesh_start_node(
    _app: tauri::AppHandle,
    _state: State<'_, AppState>,
    _request: serde_json::Value,
) -> CmdResult<serde_json::Value> {
    Err("mesh-llm feature not enabled".to_string())
}

#[tauri::command]
pub async fn mesh_stop_node(
    _app: tauri::AppHandle,
    _state: State<'_, AppState>,
) -> CmdResult<serde_json::Value> {
    Err("mesh-llm feature not enabled".to_string())
}

#[tauri::command]
pub async fn mesh_node_status(_state: State<'_, AppState>) -> CmdResult<serde_json::Value> {
    Err("mesh-llm feature not enabled".to_string())
}

#[tauri::command]
pub async fn mesh_serving_usage(_state: State<'_, AppState>) -> CmdResult<serde_json::Value> {
    Err("mesh-llm feature not enabled".to_string())
}

#[tauri::command]
pub async fn mesh_installed_models(
    _state: State<'_, AppState>,
) -> CmdResult<Vec<serde_json::Value>> {
    Err("mesh-llm feature not enabled".to_string())
}

#[tauri::command]
pub async fn mesh_model_catalog() -> CmdResult<serde_json::Value> {
    Err("mesh-llm feature not enabled".to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn feature_enabled_reports_false_on_a_non_mesh_llm_build() {
        // The frontend uses this to hide "Buzz shared compute" from the
        // provider picker on a build that can't run it (#269) -- must report
        // false whenever this stub (not the real command) is what's compiled.
        assert!(!mesh_llm_feature_enabled());
    }
}
