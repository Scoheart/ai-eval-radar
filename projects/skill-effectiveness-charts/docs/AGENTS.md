# AGENTS.md — Skill Effectiveness Charts

给任意 agent / 协作者的操作手册。目标：打开仓库 **30 秒** 知道怎么跑、改什么、不能碰什么。

## 一分钟心智模型

```
唯一输入:  data.json
唯一入口:  python3 render_html.py [--lang en|zh | --both-langs] [--task T01]
产物:      平均表 / 单任务 / 矩阵 HTML + docs/metrics 公式卡
```

Harness / Model 写死为 **Codex CLI · GPT-6 Luna**；变量只有 **Skill**。数据是示意数据，水印原文：

`Illustrative Data — Not Actual Benchmark Results`

## 硬验收清单（必须全部满足）

1. **唯一入口**：`python3 render_html.py --both-langs`（单任务再加 `--task Txx`）。不要另写第二套出图脚本。
2. **改数只动 `data.json`**。不要手改生成出来的 HTML 数字。
3. **Pass@1 = 0 / 50 / 100**（k=2 时每个任务的均值）；**禁止**把「至少一个 replicate 通过」叫做 Pass@1。
4. **SSR ≥ pass²**；列名照论文 Table 2：`pass@1 ↑`、`SSR ↑`、`pass² ↑`、`Mean judge ↑`、`U-Corr ↓`、`Tok./task`、`Min./task`。
5. **禁止**推送 `PLACEHOLDER`、`__LOAD_FROM_FILE__`、bootstrap/stitcher 壳、`.part*` / `.b64` 分片。大文件用 **一次完整写入** 或本机 `git push`。
6. **产物清单**（4 类，无后缀 HTML = 英文别名不算新类）：
   - 平均表 `skill_leaderboard.{en,zh}.html`
   - 单任务 `skill_task_Txx.{en,zh}.html`
   - 矩阵 `skill_task_matrix.{en,zh}.html`
   - 公式卡 `docs/metrics/metrics_{en,zh}.html`
7. 改 `data.json` 或 `render_html.py` 后本地必须跑通对账（脚本内 `verify_reconcile`）；CI `Expand sources` 应变绿。
8. **先读再改**：指标公式以论文与 `docs/metrics/` 为准；bootstrap CI 是附加列，勿写成论文原指标。

## 该改谁

| 你想… | 改这里 | 不要改 |
|--------|--------|--------|
| 换演示数字 / 任务 / skill 结果 | `data.json` | 生成 HTML |
| 改表头文案、中英 chrome | `i18n_packs.py` | 指标英文名 |
| 改颜色、卡片、表格 CSS | `chart_styles.py` | — |
| 改指标定义 / 对账 / 布局结构 | `render_html.py`（需有明确需求） | 分片重写该文件 |
| 改公式说明卡 | `docs/metrics/metrics_*.html` | 与论文不一致的符号 |

## 常用命令

```bash
python3 render_html.py --both-langs
python3 render_html.py --task T01 --both-langs
python3 render_html.py --lang zh
python3 -m http.server   # 预览根目录 HTML
cd docs/metrics && ./export_png.sh both   # 公式卡 PNG（可选，不入库）
```

## 推送规则（血泪）

- `render_html.py` ≈ 31KB：必须推送**完整正文**。工具参数里没带正文 → 仓库里会出现占位符 → CI 秒红。
- 不要发明「先推壳再拼 part」流程。
- 群聊无法完成 `gh` 设备码登录；需要 CLI 登录时在 **1:1** 做。
- PNG/SVG 被 `.gitignore` 忽略；截图只本地出，需要给人看就贴图，不要强行 commit 二进制图（除非用户明确要求改 ignore）。

## 对账与口径（摘要）

- `τ = 0.85`；judge 先 `round(j, 2)` 再判通过。
- `pass_at_1` / `pass_squared` 必须与 `task_outcomes` + `task_runs` 一致；`task_runs[i][r]` 必须等于该 replicate 的 `judge_passes`。
- U-Corr = `corrections + 0.2 * nudges`（由脚本算，不手填汇总）。
- 排序：baseline 置顶，其余按 Mean judge 降序。
- 中英：只翻译 UI chrome；**指标名、Skill 名、任务描述不翻译**。

## 做完自检（贴给评测前）

- [ ] `python3 render_html.py --both-langs` 退出码 0
- [ ] 平均表 Pass@1 与 `data.json` 一致（当前 demo：47.5 / 66.25 / 57.5 / 52.5）
- [ ] 无 `PLACEHOLDER` / `.part*` 残留
- [ ] 未改需求时不动 `render_html.py` 指标逻辑
