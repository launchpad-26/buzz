//! Reads the committed, packaged documentation corpus and exposes it to
//! callers as typed nodes -- issue #552.
//!
//! Per `launchpad/crates/knowledge/AGENTS.md`'s "one rule", this crate never
//! re-derives the corpus: the JSON embedded below is produced out-of-band by
//! `launchpad/project-intelligence/corpus/package.py` and committed at
//! `generated/corpus.json`. This module only parses and serves it.

use std::sync::OnceLock;

/// The packaged corpus, embedded at compile time from the committed
/// artifact. Never read from disk at runtime -- this is what makes the crate
/// a pure reader rather than something that could invoke the Python
/// packaging pipeline.
const CORPUS_JSON: &str = include_str!("../generated/corpus.json");

/// One packaged corpus node -- the subset of `node.schema.json`'s
/// front-matter fields this crate's callers need, plus the Markdown body.
///
/// `evidence` and `relationships` are kept as raw JSON rather than typed
/// further: their own shape is governed by `node.schema.json`, not by this
/// crate, and callers that need to inspect them can deserialize `evidence`'s
/// well-known keys (`statement`, `entry_class`, `evidence`, `confidence`,
/// `provided_by`) themselves without this crate re-encoding that contract.
#[derive(Debug, Clone, serde::Deserialize)]
pub struct Node {
    pub id: String,
    #[serde(rename = "type")]
    pub node_type: String,
    pub status: String,
    pub origin: String,
    pub audiences: Vec<String>,
    #[serde(default)]
    pub relationships: serde_json::Value,
    pub evidence: serde_json::Value,
    /// The node's Markdown body -- everything after the closing `---` of its
    /// YAML frontmatter.
    pub body: String,
}

/// Failure to parse the committed `generated/corpus.json`. In practice this
/// can only happen if the artifact and this loader have drifted (e.g. a
/// packaging-script change that was not re-run), since the file is
/// committed, not user input.
#[derive(Debug, thiserror::Error)]
pub enum NodeLoadError {
    #[error("generated/corpus.json is not valid JSON: {0}")]
    Parse(#[from] serde_json::Error),
}

static NODES: OnceLock<Result<Vec<Node>, NodeLoadError>> = OnceLock::new();

/// Every node in the packaged corpus, parsed once and cached.
///
/// Returns `Result` rather than panicking on a parse failure -- this repo's
/// own rule against introducing `unwrap()`/`expect()` in production paths
/// applies here even though the input is a committed, not user-supplied,
/// file.
pub fn nodes() -> Result<&'static [Node], &'static NodeLoadError> {
    NODES
        .get_or_init(|| serde_json::from_str::<Vec<Node>>(CORPUS_JSON).map_err(NodeLoadError::from))
        .as_ref()
        .map(Vec::as_slice)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn loads_real_corpus_content_not_the_scaffold_placeholder() {
        let nodes = nodes().expect("committed generated/corpus.json must parse");

        // The scaffold placeholder this replaces was a single constant
        // string; real packaged content is dozens of nodes.
        assert!(
            nodes.len() > 1,
            "expected the real packaged corpus, not a single placeholder entry"
        );
    }

    #[test]
    fn known_real_ids_are_present_with_their_real_type_and_origin() {
        let nodes = nodes().expect("committed generated/corpus.json must parse");

        let readme = nodes
            .iter()
            .find(|node| node.id == "corpus-readme")
            .expect("corpus-readme must be present in the packaged corpus");
        assert_eq!(readme.node_type, "governance");
        assert_eq!(readme.origin, "launchpad");

        let taxonomy = nodes
            .iter()
            .find(|node| node.id == "corpus-standard-taxonomy")
            .expect("corpus-standard-taxonomy must be present in the packaged corpus");
        assert_eq!(taxonomy.node_type, "governance");
        assert_eq!(taxonomy.origin, "launchpad");
    }

    #[test]
    fn architecture_and_governance_types_are_both_represented() {
        let nodes = nodes().expect("committed generated/corpus.json must parse");

        assert!(
            nodes.iter().any(|node| node.node_type == "architecture"),
            "expected at least one architecture node"
        );
        assert!(
            nodes.iter().any(|node| node.node_type == "governance"),
            "expected at least one governance node"
        );
    }
}
