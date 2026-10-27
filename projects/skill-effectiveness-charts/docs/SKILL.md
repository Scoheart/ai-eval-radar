---
name: Skill eval charts
description: >-
  When you have Skill-effectiveness eval JSON (or need HTML/PNG charts comparing
  Skills under a fixed harness/model): validate the data contract, render
  leaderboard (+ optional per-task) via the chart repo, export screenshots, and
  self-check Pass@1 / SSR / Table 2 columns. Not for unrelated plotting.
---

# Skill eval charts

Render **Skill effectiveness** leaderboards from eval JSON. Variable = Skill; harness/model are fixed by the dataset. Implementation lives in the chart repo; this skill is the portable recipe only—**do not embed demo numbers**.

## When to use

- User has (or asks you to produce) **evaluation results as JSON** and wants Skill comparison charts.
- User asks for **平均表 / 单任务评测图 / Skill leaderboard** in the SWE-Together Table 2 style.

## When not to use

- Generic matplotlib/excel charts unrelated to Skill eval.
- Changing paper metric definitions without an explicit ask (point at `docs/metrics/` instead).

## Inputs

1. **Eval JSON** matching the chart repo `data.json` contract (see repo `AGENTS.md` / README):
   - `meta` (incl. `k`, `run_metric_fields`)
   - `skills[]` with `task_outcomes`, `task_runs`, `task_run_metrics`, `pass_at_1`, `pass_squared`, optional `is_baseline`
   - `tasks[]` for ids / titles
2. **Chart repo checkout** (clone if missing): `Scoheart/skill-effectiveness-charts`  
   Working tree root = directory that contains `render_html.py` and `data.json`.

Replace or merge the eval JSON into that repo’s `data.json` (or pass an explicit data path only if the renderer already supports it; default is overwrite/update `data.json` in the checkout).

## Steps

1. **Read** repo `AGENTS.md` (hard rules) and skim README “30 秒跑通”.
2. **Validate JSON** against the contract: required keys present; for each skill, `len(task_outcomes) == len(tasks)`; `task_runs` length matches; no hand-edited HTML as source of truth.
3. **Write** the eval JSON to `data.json` in the chart repo (backup previous demo file if you need to restore later).
4. **Render** from repo root (Python stdlib only):
   ```bash
   python3 render_html.py --both-langs
   python3 render_html.py --task T01 --both-langs   # optional; use the task id requested
   ```
5. **Optional PNG** (PNG is gitignored; keep local or attach in chat):
   - Open the generated HTML with Chrome headless `--screenshot=...` (same pattern as `docs/metrics/export_png.sh`).
   - Default exports: leaderboard + requested task page (en and/or zh as asked).
6. **Self-check** before delivery (fail the task if any fail):
   - Exit code 0 from `render_html.py` (includes `verify_reconcile`).
   - **Pass@1** per task is **0 / 50 / 100** when `k=2` (mean of per-run pass); never label “≥1 run passed” as Pass@1.
   - **SSR ≥ pass²**; column headers match Table 2 spellings (`pass@1 ↑`, `SSR ↑`, `pass² ↑`, `Mean judge ↑`, `U-Corr ↓`, `Tok./task`, `Min./task`).
   - No `PLACEHOLDER`, `__LOAD_FROM_FILE__`, or `.part*` / stitcher stubs in `render_html.py` or outputs.
   - Outputs present: average leaderboard HTML; per-task HTML if `--task` was used; matrix HTML is optional extras from the same render.
7. **Deliver** HTML paths and/or PNG attachments. Mention watermark if data is still illustrative. Do **not** push broken stubs; full-file or proper `git push` only if the user asked to update the remote.

## Outputs (expected)

| Kind | Typical files |
|------|----------------|
| Average table | `skill_leaderboard.en.html` / `.zh.html` |
| Single task | `skill_task_<ID>.en.html` / `.zh.html` |
| Matrix (optional) | `skill_task_matrix.en.html` / `.zh.html` |
| Formula cards (reference) | `docs/metrics/metrics_{en,zh}.html` — do not regenerate unless asked |

## Hard rules

- Unique render entry: `python3 render_html.py` — do not invent a second renderer.
- Change numbers only via JSON; do not patch digits into HTML.
- Metric names stay English in zh UI.
- Paired bootstrap CI on vs-Baseline is **extra vs paper**; do not call it a paper metric.
- Never split-push `render_html.py`.

## Pointers

- Repo README / `AGENTS.md` = source of truth for commands and acceptance checks.
- `docs/metrics/` = formula explanations only.
