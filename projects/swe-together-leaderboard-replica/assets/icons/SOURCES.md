# Chart brand icons

All files except `qwen.png` are copied byte-for-byte from the audited assets in [Scoheart/mux](https://github.com/Scoheart/mux) (`desktop/src/assets/agents|providers/`). Official sources are recorded in mux's `SOURCES.md`. Never recolor (no Simple Icons hex).

| File | Mux path | Official source (per mux) |
|------|----------|---------------------------|
| `openai.svg` | agents/openai.svg (`codex` → `openai`) | <https://openai.com/brand/> |
| `gemini.svg` | agents/gemini.svg | mux audited Gemini mark |
| `opencode.svg` | agents/opencode.svg | mux bundled OpenCode mark |
| `claude.svg` | agents/claude.svg | mux bundled Claude mark |
| `qwen-code.png` | agents/qwen-code.png (Qwen Code product) | <https://qwenlm.github.io/qwen-code-docs/favicon.png> |
| `qwen.png` | — (not in mux) | <https://github.com/QwenLM.png?size=200> — QwenLM official GitHub org avatar, same method as mux `alibaba.png`; retrieved 2026-10-10 |
| `anthropic.png` | providers/anthropic.png | <https://www.anthropic.com/favicon.ico> |
| `deepseek.png` | providers/deepseek.png | <https://www.deepseek.com/favicon.ico> |
| `moonshotai.png` | providers/moonshotai.png (alias `kimi`) | <https://platform.kimi.ai/favicon.ico?v=3> |
| `google.png` | providers/google.png | gstatic Google devrel touch icon |
| `alibaba.png` | providers/alibaba.png | <https://github.com/aliyun> org avatar |
| `xai.png` | providers/xai.png | <https://x.ai/favicon.ico> |

Usage: set `meta.harness_icon`, `meta.model_icon`, `meta.user_sim_icon` in `data.json` to a file stem (or alias above). Empty/missing → text only. A named icon that doesn't exist → render fails. No fallback to OpenAI.
