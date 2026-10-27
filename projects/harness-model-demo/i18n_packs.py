from __future__ import annotations
from typing import Any

# UI chrome only. Paper metric headers stay English in every language pack.
I18N = {
    "en": {
        "skill": "Skill",
        "vs_baseline": "vs Baseline",
        "rep1": "Rep 1",
        "rep2": "Rep 2",
        "sort_note": "Sorted by Mean judge (paper Table 2) · 95% CI: paired bootstrap over tasks (not in paper)",
        "matrix_note": "Optional overview. Prefer <code>python3 render_html.py --task T01</code> for the single-task detail chart.",
        "watermark": "Illustrative Data — Not Actual Benchmark Results",
        "replicates": "replicates",
        "baseline_suffix": " (baseline)",
        "legend_both": "Both replicates pass (pass²)",
        "legend_one": "One replicate only",
        "legend_none": "Neither replicate",
        "title_lb": "Skill Effectiveness on SWE-Together",
        "title_matrix": "Per-Task Outcomes on SWE-Together",
        "subtitle_lb": "Codex CLI · GPT-6 Luna · SWE-Together · k = {k} replicates",
        "subtitle_task": "{harness} · {model} · k = {k} replicates",
        "subtitle_matrix": "Codex CLI · GPT-6 Luna · SWE-Together · k = {k} replicates",
    },
    "zh": {
        "skill": "技能",
        "vs_baseline": "相对基线",
        "rep1": "第1次复现",
        "rep2": "第2次复现",
        "sort_note": "按 Mean judge 排序（论文 Table 2）· 95% 置信区间：按题配对 bootstrap（非论文口径）",
        "matrix_note": "可选总览。单任务明细请用 <code>python3 render_html.py --task T01 --lang zh</code>。",
        "watermark": "演示数据 — 非真实评测结果",
        "replicates": "次复现",
        "baseline_suffix": "（基线）",
        "legend_both": "两次复现均通过（pass²）",
        "legend_one": "仅一次复现通过",
        "legend_none": "两次复现均未通过",
        "title_lb": "Skill Effectiveness on SWE-Together",
        "title_matrix": "Per-Task Outcomes on SWE-Together",
        "subtitle_lb": "Codex CLI · GPT-6 Luna · SWE-Together · k = {k} 次复现",
        "subtitle_task": "{harness} · {model} · k = {k} 次复现",
        "subtitle_matrix": "Codex CLI · GPT-6 Luna · SWE-Together · k = {k} 次复现",
    },
}

# Paper Table 2 headers — identical in every language pack.
METRIC_HEADERS = {
    "pass1": "pass@1 ↑",
    "ssr": "SSR ↑",
    "pass2": "pass² ↑",
    "judge": "Mean judge ↑",
    "ucorr": "U-Corr ↓",
    "tokens": "Tok./task",
    "mins": "Min./task",
    "pass2_short": "pass²",
}


def t(lang: str, key: str, **kwargs) -> str:
    pack = I18N.get(lang) or I18N["en"]
    text = pack.get(key) or I18N["en"][key]
    return text.format(**kwargs) if kwargs else text


def skill_display_name(s: dict[str, Any], lang: str) -> str:
    """Product names stay English; only the '(baseline)' chrome is localized."""
    name = s["name"]
    if s.get("is_baseline"):
        for suf in (" (baseline)", "（基线）"):
            if name.endswith(suf):
                name = name[: -len(suf)]
                break
        return name + t(lang, "baseline_suffix")
    return name


