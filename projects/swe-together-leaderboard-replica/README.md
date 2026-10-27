# Skill Effectiveness Charts（HTML）

固定 **Harness = Codex CLI**、**Model = GPT-6 Luna**，只对比不同 **Skill** 配置的效果（No Skill / Workbench / Superpowers / Custom）。HTML+CSS 出图，共用一份 `data.json`。

Skill Effectiveness leaderboard charts (HTML+CSS). Variable = Skill; harness/model fixed. **Demo data only — all numbers are illustrative, not real benchmark results.**

## 指标 / Metrics

术语与 [SWE-Together 论文](https://arxiv.org/html/2606.29957) §2.3 及 Table 2 表头逐字一致：`pass@1 ↑`、`SSR ↑`、`pass² ↑`、`Mean judge ↑`、`U-Corr ↓`、`Tok./task`、`Min./task`，每题 `k = 2` replicates。每个 replicate 的 judge 先 round 到 2 位小数，**round(j, 2) ≥ τ = 0.85 记为通过**。

| 指标（论文写法） | 含义 |
|------|------|
| **pass@1 ↑** | 单个 replicate 的通过率在 k = 2 个 replicates 间取平均，再跨任务平均。单任务为 0 / 50 / 100；汇总 = (2·#两个都过 + #仅一个过) / (2N) |
| **SSR ↑** | 每个任务取 k = 2 个 replicates 的 judge 平均 j̄_t，j̄_t ≥ 0.85 记 1，否则 0；再跨任务平均 |
| **pass² ↑** | 两个 replicates 都通过的任务比例（不是 pass@1 的平方） |
| **Mean judge ↑** | 每个 replicate 的 judge（2 位小数），先在任务内平均，再跨任务平均；平均表按论文 Table 2 显示 3 位小数，单任务页显示 2 位 |
| **U-Corr ↓** | User Correction：每个 replicate = N_correction + 0.2 × N_nudge；先在任务内各 replicates 间平均，再跨任务平均（每个任务权重相同） |
| **Tok./task**, **Min./task** | 每任务的 tokens 与 wall-clock 分钟数，平均顺序同上 |
| **vs Baseline** | 相对 No Skill 的 pass@1 差值（百分点）；单任务为 0 / ±50 / ±100 pp |
| **95% CI** | 平均表 vs Baseline 下方灰色区间：按任务配对 bootstrap（40 个任务有放回重采样，skill 与 baseline 用同一组索引），B=10000，seed=20261010，取 2.5/97.5 百分位。paired bootstrap CI is an addition on top of SWE-Together, not part of the paper（我们额外加的，不是论文里的） |

排序：非 baseline 行按 Mean judge 降序（论文 Table 2：“Models are ranked by mean judge score”）；togetherbench.com 网站则按 pass@1 排序，这里跟论文。

> 注意：旧版图表里的「k 个 replicates 中至少一个通过」其实是 **pass@2**，不是 pass@1，已改为论文口径。

条形图：实心 = pass²；斜线 = pass@1 − pass²。平均表列顺序（与论文 Table 2 一致）：Skill | 条形图 | pass@1 ↑ | SSR ↑ | pass² ↑ | Mean judge ↑ | U-Corr ↓ | Tok./task | Min./task | vs Baseline（含 95% CI，最后一列）。没有 ⋆ Reference 行（我们没有跑 reference patch）。单任务页列：Rep 1 / Rep 2 / pass² / Mean judge ↑ / U-Corr ↓ / Tok./task / Min./task / vs Baseline。

`data.json` 中 `task_run_metrics[任务][replicate]` 为紧凑数组，字段顺序见 `meta.run_metric_fields`：`[judge, tokens, min, corrections, nudges]`（`corrections` = 明确纠正数，`nudges` = 暗示数）。U-Corr 由脚本按上式计算，不再手填；Mean judge / U-Corr / Tok./task / Min./task / SSR 都只在 40 个任务 × 2 个 replicates 数据齐全时计算，否则显示「—」。各 skill 的 `pass_at_1` / `pass_squared` 会与 `task_runs` / `task_outcomes` 自动对账，不一致时脚本报错退出。

## 演示数据水印

演示 `data.json` 中的所有数字（通过情况、judge、U-Corr 计数、tokens、时间）都是虚构的示意数据，带固定水印（请勿缩短）：

`Illustrative Data — Not Actual Benchmark Results`

## 用法

无需虚拟环境，仅 Python 标准库。

```bash
# 改 data.json 后重新生成平均表 + 可选矩阵（默认英文 UI）
python3 render_html.py

# 同时输出英/中两套（推荐）
python3 render_html.py --both-langs
python3 render_html.py --task T01 --both-langs

# 只生成中文 UI chrome
python3 render_html.py --lang zh
python3 render_html.py --task T01 --lang zh

# 本地预览
python3 -m http.server
# 打开 http://localhost:8000/skill_leaderboard.en.html 或 .zh.html
# 或 http://localhost:8000/skill_task_T01.en.html / .zh.html
```

### 语言 / Language packs

`--lang en|zh`（默认 `en`）只翻译 UI chrome（表头「技能 / Skill」、相对基线、排序说明、水印、复现标签等）。**论文 Table 2 指标名在两种语言中保持英文不变**：`pass@1 ↑`、`SSR ↑`、`pass² ↑`、`Mean judge ↑`、`U-Corr ↓`、`Tok./task`、`Min./task`。Skill 产品名（No Skill / Workbench / Superpowers / Custom）、仓库名与任务描述也不翻译。

输出：
- `skill_leaderboard.en.html` / `skill_leaderboard.zh.html`
- `skill_task_T01.en.html` / `skill_task_T01.zh.html`
- 无后缀的 `skill_leaderboard.html` / `skill_task_T01.html` 是英文版别名

仓库根目录即真实源码，**没有** `unpack_assets` 步骤。

## 文件布局

| 文件 | 说明 |
|------|------|
| `render_html.py` | 从 `data.json` 生成 HTML（含 pass@1 / SSR / U-Corr 计算、对账与 bootstrap CI） |
| `chart_styles.py` | 图表 CSS（由 `render_html.py` 引用） |
| `data.json` | 演示数据（skills / tasks / replicates / 每个 replicate 的 judge、tokens、min、corrections、nudges） |
| `skill_leaderboard.en.html` / `.zh.html` | 图1：全任务平均条形表（英/中 UI） |
| `skill_leaderboard.html` | 英文版别名 |
| `skill_task_T01.en.html` / `.zh.html` | 图2：单任务明细（英/中 UI） |
| `skill_task_T01.html` | 英文版别名 |
| `skill_task_matrix.en.html` / `.zh.html` | 可选：40 任务矩阵总览 |
| `requirements.txt` | 无第三方依赖说明 |
| `.gitignore` | 忽略 .venv / 缓存 / 生成 PNG |


## 指标公式图 / Metrics formula charts

笔杆公式卡（英/中）在 [`docs/metrics/`](docs/metrics/)：`metrics_en.html`、`metrics_zh.html`。指标名保持英文；可用 `docs/metrics/export_png.sh` 或 Chrome headless 导出 PNG。详见 [`docs/metrics/README.md`](docs/metrics/README.md)。

## License

Private demo for internal review.
