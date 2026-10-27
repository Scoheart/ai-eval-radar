# Skill Effectiveness Charts（HTML）

固定 **Harness = Codex CLI**、**Model = GPT-6 Luna**，只对比不同 **Skill**（No Skill / Workbench / Superpowers / Custom）。一份 `data.json` → `render_html.py` → HTML 出图。

**Demo data only — Illustrative Data — Not Actual Benchmark Results.**

## 30 秒跑通

```bash
# 无需 venv，仅标准库
python3 render_html.py --both-langs
python3 render_html.py --task T01 --both-langs

python3 -m http.server
# 打开 skill_leaderboard.en.html / skill_task_T01.en.html
```

改数字 → 只动 `data.json`，再跑上面两条。改样式/逻辑 → 见 `AGENTS.md`。**新 agent 先读 [`AGENTS.md`](AGENTS.md)。**

## 管道（一眼）

```
data.json  ──►  render_html.py  ──►  三类 Skill HTML（en/zh）
                                    └─ docs/metrics/ 公式卡（独立）
```

| 产物 | 文件 | 怎么出 |
|------|------|--------|
| ① 平均表 | `skill_leaderboard.{en,zh}.html` | `python3 render_html.py --both-langs` |
| ② 单任务 | `skill_task_T01.{en,zh}.html` | `--task T01 --both-langs`（任意 task id） |
| ③ 矩阵 | `skill_task_matrix.{en,zh}.html` | 与 ① 同命令一并生成 |
| ④ 公式卡 | `docs/metrics/metrics_{en,zh}.html` | 已有静态页；PNG 用 `docs/metrics/export_png.sh` |

无后缀的 `.html` = 英文别名，不算新图。PNG/SVG 由 `.gitignore` 忽略，不进仓库。

## 目录

| 路径 | 角色 |
|------|------|
| `data.json` | **唯一输入数据** |
| `render_html.py` | **唯一出图入口**（含对账、指标、bootstrap CI） |
| `chart_styles.py` / `i18n_packs.py` | CSS / UI 文案（指标名保持英文） |
| `docs/metrics/` | 论文指标公式卡 |
| `AGENTS.md` | 给 agent 的用法与硬规则 |
| `.github/workflows/` | CI：跑 `render_html.py --both-langs` |

## 指标（与论文 Table 2 一致）

术语与 [SWE-Together](https://arxiv.org/html/2606.29957) §2.3 / Table 2 逐字一致：`pass@1 ↑`、`SSR ↑`、`pass² ↑`、`Mean judge ↑`、`U-Corr ↓`、`Tok./task`、`Min./task`；`k = 2`；`round(j, 2) ≥ τ = 0.85` 为通过。

- **pass@1**：单 replicate 通过率在 k 次间平均，再跨任务平均 → 单任务 **0 / 50 / 100**（「至少一个过」是 pass@2，不是 pass@1）
- **pass²**：两次都过的任务比例
- **SSR**：任务内 k 次 judge 均值 ≥ 0.85 的任务比例（应 ≥ pass²）
- **U-Corr**：`N_correction + 0.2 × N_nudge`
- **vs Baseline**：相对 No Skill 的 pass@1 百分点差；平均表下灰色 **95% CI** 为配对 bootstrap（B=10000，seed=20261010）——**论文外附加，图上已标注**

排序：非 baseline 按 **Mean judge** 降序（跟论文 Table 2，不是网站的 pass@1 序）。中英 UI 只翻译 chrome；**指标名始终英文**。

`task_run_metrics` 紧凑数组字段顺序见 `meta.run_metric_fields`：`[judge, tokens, min, corrections, nudges]`。不全则 Mean judge / U-Corr / Tok / Min / SSR 显示「—」。`pass_at_1` / `pass_squared` 与 `task_runs` / `task_outcomes` 不一致时脚本直接退出。

## License

Private demo for internal review.
