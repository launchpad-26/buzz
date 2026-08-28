# Default model fallback policy

Checked 2026-08-27. The configuration uses a two-reviewer panel. Each lane is
ordered: the first available candidate that completes is the reviewer; later
entries are only failovers. This preserves the preferred native Claude + Codex
pair while keeping an independent, economical path available.

| Lane | Order | Provider family | Model | Why it is here |
|---|---:|---|---|---|
| Primary | 1 | Anthropic | Claude Sonnet (native CLI) | Preferred native reviewer. |
| Secondary | 1 | OpenAI | GPT-5.6 Sol (Codex CLI) | Preferred independent native reviewer. |
| Primary | 2 | Z.ai | GLM 5.3 Flash | Strong low-cost coding and long-context fallback: $0.15/M input and $0.50/M output (temporarily discounted at review time). |
| Secondary | 2 | DeepSeek | DeepSeek V4 Flash 0731 | Lowest-cost coding/reasoning fallback: $0.03/M input and $0.10/M output. |
| Primary | 3 | Qwen | Qwen3.8 Flash | Independent codebase-analysis fallback: $0.16/M input and $0.47/M output. |
| Secondary | 3 | Google | Gemini 3.7 Flash | Higher-cost, independent quality fallback for coding and multi-step reasoning: $0.375/M input and $1.875/M output. |

Use exact OpenRouter slugs rather than `latest` aliases so a fallback does not
silently change capability or pricing. Refresh the entries before changing the
policy with the OpenRouter Models API and each model's OpenRouter page:

- https://openrouter.ai/api/v1/models
- https://openrouter.ai/z-ai/glm-5.3-flash
- https://openrouter.ai/deepseek/deepseek-v4-flash-0731
- https://openrouter.ai/qwen/qwen3.8-flash
- https://openrouter.ai/google/gemini-3.7-flash
