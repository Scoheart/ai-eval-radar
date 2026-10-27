#!/usr/bin/env python3
from __future__ import annotations

from chart_styles import STYLES

import argparse
import base64
import json
from decimal import ROUND_HALF_UP, Decimal
import random
import re
from pathlib import Path
from typing import Any

SHARED_CSS = STYLES['S0']

CHART1_CSS = SHARED_CSS + STYLES['S1']

DETAIL_CSS = SHARED_CSS + STYLES['S2']

MATRIX_CSS = SHARED_CSS + STYLES['S3']


# Brand marks: copied unchanged from Scoheart/mux (see assets/icons/SOURCES.md).
# The icon follows the data: meta.harness_icon / model_icon / user_sim_icon.
# Missing or empty -> text only. Named but not found -> hard error. Never falls back to OpenAI.
_ICON_DIR = Path(__file__).resolve().parent / "assets" / "icons"

def _icon_aliases() -> dict[str, str]:
    f = _ICON_DIR / "aliases.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}

def resolve_icon(name: str | None) -> Path | None:
    if not name:
        return None
    stem = _icon_aliases().get(name.strip().lower(), name.strip().lower())
    for ext in (".svg", ".png"):
        f = _ICON_DIR / f"{stem}{ext}"
        if f.exists():
            return f
    raise SystemExit(f"Icon {name!r} not found in {_ICON_DIR} (.svg/.png). Add it from mux or clear the meta field.")

def _icon_html(name: str | None) -> str:
    f = resolve_icon(name)
    if f is None:
        return ""
    if f.suffix == ".svg":
        raw = f.read_text(encoding="utf-8")
        raw = re.sub(r"<title>.*?</title>", "", raw, flags=re.S)
        # Unique ids so several inlined SVGs (masks/filters) don't collide.
        pref = f"i{f.stem.replace('-', '')}_"
        raw = re.sub(r'id="([^"]+)"', lambda m: f'id="{pref}{m.group(1)}"', raw)
        raw = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{pref}{m.group(1)})', raw)
        return raw.replace("<svg ", '<svg class="brand-icon" aria-hidden="true" ', 1)
    b64 = base64.b64encode(f.read_bytes()).decode("ascii")
    return f'<img class="brand-icon" alt="" src="data:image/png;base64,{b64}" />'

def brand_chip(label: str, icon: str | None = None) -> str:
    return f'<span class="brand-chip">{_icon_html(icon)}<span class="brand-label">{label}</span></span>'

def brand_subtitle(meta: dict[str, Any], rest: str) -> str:
    harness = meta.get("harness", "")
    model = meta.get("model", "")
    user_sim = meta.get("user_sim_model", "")
    parts = [brand_chip(harness, meta.get("harness_icon")), brand_chip(model, meta.get("model_icon"))]
    if user_sim:
        parts.append(brand_chip(f"User sim · {user_sim}", meta.get("user_sim_icon")))
    sep = '<span class="brand-sep">·</span>'
    return sep.join(parts) + sep + f'<span class="brand-rest">{rest}</span>'


# Column headers use the paper's exact spellings (pass@1, pass², Mean judge, U-Corr,
# Tok./task, Min./task), so keep their case instead of upper-casing them.
_VERBATIM_HEADERS = """
.table thead th, .matrix thead th { text-transform: none; letter-spacing: 0.01em; }
"""
DETAIL_CSS += _VERBATIM_HEADERS
MATRIX_CSS += _VERBATIM_HEADERS

# Chart 1 extra column: vs Baseline (paired-bootstrap CI underneath).
CHART1_CSS += """
.table thead th.col-skill { width: 16%; }
.table thead th.col-bar { width: 19%; }
.table thead th.col-metric { width: 7%; }
.table thead th.col-metric.wide { width: 9%; }
.table thead th.col-vs { text-align: center; width: 13%; }
.axis { margin-right: 0; }
.vs-agg { display: flex; flex-direction: column; align-items: center; gap: 2px; font-variant-numeric: tabular-nums; }
.vs-agg .vs-delta { font-size: 13px; font-weight: 600; }
.vs-agg .vs-delta.pos { color: #059669; }
.vs-agg .vs-delta.neg { color: #dc2626; }
.vs-agg .vs-delta.zero, .vs-agg .vs-delta.base { color: var(--muted); font-weight: 500; }
.vs-agg .vs-ci { font-size: 10.5px; color: var(--muted); font-weight: 400; }
""" + _VERBATIM_HEADERS

BOOTSTRAP_B = 10000
BOOTSTRAP_SEED = 20261010

PASS_THRESHOLD = 0.85

from i18n_packs import I18N, METRIC_HEADERS, t, skill_display_name


def round_judge(j: float) -> float:
    """SWE-Together: the judge score is rounded to 2 dp before the >= 0.85 pass check."""
    return round(float(j), 2)


def judge_passes(j: float) -> bool:
    return round_judge(j) >= PASS_THRESHOLD


def fmt_judge(v: float, dp: int = 2) -> str:
    """Half-up rounding (avoids float artifacts such as 0.45 -> 0.44).

    Per-task averages use 2 dp (per-replicate judges are 2 dp); the aggregate
    Mean judge uses 3 dp, as in the paper's Table 2 (e.g. 0.801).
    """
    q = Decimal(1).scaleb(-dp)
    return str(Decimal(repr(round(float(v), 9))).quantize(q, rounding=ROUND_HALF_UP))

DEFAULT_RUN_FIELDS = ["judge", "tokens", "min", "corrections", "nudges"]


def load_data(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    expand_run_metrics(data)
    return data


def expand_run_metrics(data: dict[str, Any]) -> None:
    """Expand compact per-run arrays into dicts, in place.

    data.json stores task_run_metrics[task][run] as a list ordered by
    meta.run_metric_fields (default: judge, tokens, min, corrections, nudges).
    Dict entries are accepted as-is.
    """
    fields = (data.get("meta") or {}).get("run_metric_fields") or DEFAULT_RUN_FIELDS
    for s in data.get("skills") or []:
        out = []
        for pair in s.get("task_run_metrics") or []:
            if pair is None:
                out.append(None)
                continue
            runs = []
            for m in pair:
                if isinstance(m, (list, tuple)):
                    runs.append(dict(zip(fields, m)))
                else:
                    runs.append(m)
            out.append(runs)
        s["task_run_metrics"] = out

def ordered_skills(skills: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Baseline first, then skills ranked by Mean Judge (desc), as the paper's leaderboard.

    Falls back to Pass@1 for a skill whose per-run judges are incomplete.
    """
    base = [s for s in skills if s.get("is_baseline")]

    def rank_key(s: dict[str, Any]) -> tuple[int, float, float]:
        n = len(s.get("task_outcomes") or [])
        mj = aggregate_metric(s, "judge", n, 2)
        return (1 if mj is not None else 0, mj if mj is not None else 0.0, float(s["pass_at_1"]))

    rest = sorted([s for s in skills if not s.get("is_baseline")], key=rank_key, reverse=True)
    return base + rest

def skill_palette(skills: list[dict[str, Any]]) -> list[dict[str, str]]:
    blues = [
        {"solid": "#2563EB", "hatch": "#93C5FD", "dot": "#2563EB"},
        {"solid": "#3B82F6", "hatch": "#BFDBFE", "dot": "#3B82F6"},
        {"solid": "#60A5FA", "hatch": "#DBEAFE", "dot": "#60A5FA"},
        {"solid": "#93C5FD", "hatch": "#EFF6FF", "dot": "#93C5FD"},
    ]
    out: list[dict[str, str]] = []
    bi = 0
    for s in skills:
        if s.get("is_baseline"):
            out.append({"solid": "#9CA3AF", "hatch": "#D1D5DB", "dot": "#9CA3AF"})
        else:
            out.append(blues[min(bi, len(blues) - 1)])
            bi += 1
    return out

def pct_label(v: float) -> str:
    if abs(v - round(v)) < 1e-6:
        return f"{int(round(v))}%"
    return f"{v:.2f}".rstrip("0").rstrip(".") + "%"

def parse_tokens(val: Any) -> float | None:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().lower().replace(",", "")
    m = re.match(r"^([0-9]*\.?[0-9]+)\s*k$", s)
    if m:
        return float(m.group(1)) * 1000.0
    try:
        return float(s)
    except ValueError:
        return None

def fmt_tokens(val: float | None) -> str:
    if val is None:
        return "—"
    return f"{val / 1000.0:.1f}k"

def run_user_correction(m: dict[str, Any] | None) -> float | None:
    """SWE-Together User Correction for one run: N_correction + 0.2 * N_nudge."""
    if not m or m.get("corrections") is None or m.get("nudges") is None:
        return None
    return int(m["corrections"]) + 0.2 * int(m["nudges"])


def task_user_correction(run_metrics: list[dict[str, Any]] | None) -> float | None:
    """Mean of per-run User Correction over the k runs of one task."""
    vals = [v for v in (run_user_correction(m) for m in (run_metrics or [])) if v is not None]
    return (sum(vals) / len(vals)) if vals else None


def run_metric_value(m: dict[str, Any] | None, key: str) -> float | None:
    if not m:
        return None
    if key == "correction":
        return run_user_correction(m)
    if key == "tokens":
        return parse_tokens(m.get("tokens"))
    v = m.get(key)
    if v is None:
        return None
    return round_judge(v) if key == "judge" else float(v)


def aggregate_metric(skill: dict[str, Any], key: str, n_tasks: int, k: int) -> float | None:
    """Task-equal mean of the per-task run mean (same order for every metric).

    key is one of judge / correction / tokens / min. Computed only when ALL
    n_tasks x k runs have a value; otherwise None (shown as "—"), so a partial
    subset is never averaged.
    """
    trm = skill.get("task_run_metrics") or []
    if n_tasks <= 0 or len(trm) != n_tasks:
        return None
    per_task = []
    for pair in trm:
        if not pair or len(pair) != k:
            return None
        vals = [run_metric_value(m, key) for m in pair]
        if any(v is None for v in vals):
            return None
        per_task.append(sum(vals) / k)
    return sum(per_task) / n_tasks


def aggregate_ssr(skill: dict[str, Any], n_tasks: int, k: int) -> float | None:
    """SSR (%): a task counts when the mean of its k rounded judges is >= 0.85.

    Needs every task x run judge; otherwise None.
    """
    trm = skill.get("task_run_metrics") or []
    if n_tasks <= 0 or len(trm) != n_tasks:
        return None
    hits = 0
    for pair in trm:
        if not pair or len(pair) != k:
            return None
        js = [run_metric_value(m, "judge") for m in pair]
        if any(j is None for j in js):
            return None
        if sum(js) / k >= PASS_THRESHOLD - 1e-9:
            hits += 1
    return hits / n_tasks * 100.0


def task_pass_fracs(skill: dict[str, Any]) -> list[float]:
    """Per-task Pass@1 as a fraction (0 / 0.5 / 1 for k=2)."""
    return [task_pass_at_1_pct(o, r) / 100.0 for o, r in zip(skill["task_outcomes"], skill["task_runs"])]


def paired_bootstrap_ci(a: list[float], b: list[float], n_boot: int = BOOTSTRAP_B,
                        seed: int = BOOTSTRAP_SEED) -> tuple[float, float]:
    """95% percentile CI (pp) of mean(a - b), resampling task indices with replacement.

    The same resampled indices are used for skill and baseline (paired). A fresh
    RNG with a fixed seed per call keeps results reproducible and identical
    index draws across skills.
    """
    n = len(a)
    diffs = [x - y for x, y in zip(a, b)]
    rng = random.Random(seed)
    means = []
    for _ in range(n_boot):
        tot = 0.0
        for _ in range(n):
            tot += diffs[rng.randrange(n)]
        means.append(tot / n * 100.0)
    means.sort()

    def q(p: float) -> float:
        return means[min(n_boot - 1, max(0, int(round(p * (n_boot - 1)))))]

    return q(0.025), q(0.975)


def fmt_pp(v: float, signed: bool = True) -> str:
    if abs(v) < 1e-9:
        return "0"
    txt = f"{v:.2f}".rstrip("0").rstrip(".")
    if signed and v > 0:
        txt = "+" + txt
    return txt


def aggregate_user_correction(skill: dict[str, Any], n_tasks: int, k: int = 2) -> float | None:
    """Task-equal mean of per-task User Correction. None unless every run has counts."""
    return aggregate_metric(skill, "correction", n_tasks, k)


def avg_metrics(run_metrics: list[dict[str, Any]] | None) -> dict[str, Any]:
    """Average judge/tokens/min across available runs; correction from per-run counts."""
    if not run_metrics:
        return {"judge": None, "correction": None, "tokens": None, "min": None}
    judges, corrs, toks, mins = [], [], [], []
    for m in run_metrics:
        if m is None:
            continue
        if m.get("judge") is not None:
            judges.append(round_judge(m["judge"]))
        uc = run_user_correction(m)
        if uc is not None:
            corrs.append(uc)
        tv = parse_tokens(m.get("tokens"))
        if tv is not None:
            toks.append(tv)
        if m.get("min") is not None:
            mins.append(float(m["min"]))
    return {
        "judge": (sum(judges) / len(judges)) if judges else None,
        "correction": (sum(corrs) / len(corrs)) if corrs else None,
        "tokens": (sum(toks) / len(toks)) if toks else None,
        "min": (sum(mins) / len(mins)) if mins else None,
    }

def task_pass_at_1_pct(outcome: str, runs: list[bool] | None = None) -> float:
    """Single-task Pass@1 (SWE-Together): per-run pass rate averaged over the k runs.

    With k=2 this is 0 / 50 / 100. ("At least one run passes" would be pass@2.)
    """
    if runs is not None and len(runs) >= 1:
        return 100.0 * sum(1 for r in runs if r) / len(runs)
    return {"both": 100.0, "one": 50.0}.get(outcome, 0.0)


def aggregate_pass_at_1_pct(outcomes: list[str]) -> float:
    """Mean of per-task Pass@1 = (2*#both + #one) / (2N) * 100 for k=2."""
    n = len(outcomes)
    both = sum(1 for o in outcomes if o == "both")
    one = sum(1 for o in outcomes if o == "one")
    return (2 * both + one) / (2 * n) * 100.0 if n else 0.0

def verify_reconcile(skills: list[dict[str, Any]], n_tasks: int) -> None:
    for s in skills:
        outs = s.get("task_outcomes") or []
        if len(outs) != n_tasks:
            raise SystemExit(f"Outcome length mismatch for {s['name']}")
        both = sum(1 for o in outs if o == "both")
        one = sum(1 for o in outs if o == "one")
        p2 = both / n_tasks * 100.0
        p1 = aggregate_pass_at_1_pct(outs)
        runs_all = s.get("task_runs") or []
        p1_runs = sum(task_pass_at_1_pct(o, r) for o, r in zip(outs, runs_all)) / n_tasks
        if abs(p1_runs - p1) > 1e-6:
            raise SystemExit(f"Pass@1 runs/outcomes mismatch for {s['name']}: {p1_runs} vs {p1}")
        if abs(p2 - float(s["pass_squared"])) > 1e-6 or abs(p1 - float(s["pass_at_1"])) > 1e-6:
            raise SystemExit(f"Reconcile fail {s['name']}: {p2}/{p1} vs {s['pass_squared']}/{s['pass_at_1']}")
        runs = s.get("task_runs") or []
        # Hard check: every replicate's pass flag must equal round(j, 2) >= 0.85.
        for ti, pair_m in enumerate(s.get("task_run_metrics") or []):
            for ri, m in enumerate(pair_m or []):
                j = (m or {}).get("judge")
                if j is None:
                    continue
                passed = bool(runs[ti][ri])
                if judge_passes(j) != passed:
                    raise SystemExit(
                        f"Judge/pass mismatch {s['name']} task {ti + 1} rep {ri + 1}: "
                        f"judge={j} (round={round_judge(j)}) but passed={passed}"
                    )
        ssr = aggregate_ssr(s, n_tasks, len(runs[0]) if runs else 2)
        if p2 > p1 + 1e-9:
            raise SystemExit(f"pass\u00b2 > pass@1 for {s['name']}: {p2} > {p1}")
        if ssr is not None and ssr < p2 - 1e-9:
            raise SystemExit(f"SSR < pass\u00b2 for {s['name']}: {ssr} < {p2}")
        for ti, o in enumerate(outs):
            pair = runs[ti]
            n_pass = sum(1 for x in pair if x)
            expect = {"both": 2, "one": 1, "none": 0}[o]
            if n_pass != expect:
                raise SystemExit(f"Run/outcome mismatch {s['name']} task {ti}")

def find_task_index(data: dict[str, Any], task_id: str) -> int:
    tasks = data.get("tasks") or []
    for i, t in enumerate(tasks):
        if str(t.get("id", "")).lower() == task_id.lower():
            return i
        tid = str(t.get("id", ""))
        if tid.lstrip("Tt").lstrip("0") == task_id.lstrip("Tt").lstrip("0") and task_id.strip():
            if tid.replace("T", "").replace("t", "").isdigit() or True:
                raw = re.sub(r"^t", "", task_id, flags=re.I)
                if raw.isdigit() and int(raw) == i + 1:
                    return i
    raise SystemExit(f"Unknown task id: {task_id!r}. Known: {[t['id'] for t in tasks[:5]]}...")

def shell(title: str, subtitle: str, legend_html: str, body: str, css: str, watermark: str, extra: str = "", header_extra: str = "", lang: str = "en") -> str:
    legend_block = ""
    if legend_html.strip():
        legend_block = f"""        <div class="legend">
{legend_html}
        </div>
"""
    html_lang = "zh-CN" if lang == "zh" else "en"
    return f"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
{css}
  </style>
</head>
<body>
  <div class="page">
    <div class="card">
      <div class="header">
        <div class="title">{title}</div>
        {header_extra}
        <div class="subtitle">{subtitle}</div>
{legend_block}      </div>
{body}
{extra}
      <div class="watermark">{watermark}</div>
    </div>
  </div>
</body>
</html>
"""

def render_leaderboard(data: dict[str, Any], lang: str = "en") -> str:
    meta = data.get("meta", {})
    legend = data.get("legend") or {}
    skills = ordered_skills(list(data["skills"]))
    palette = skill_palette(skills)
    x_max = float(meta.get("x_max", 80))
    x_ticks = meta.get("x_ticks", [0, 20, 40, 60, 80])
    k = int(meta.get("k", 2))
    title = t(lang, "title_lb")
    meta_h = meta.get("harness", "Codex CLI")
    meta_m = meta.get("model", "GPT-6 Luna")
    subtitle = brand_subtitle(meta, t(lang, "subtitle_rest_lb", k=k))
    watermark = t(lang, "watermark")
    bold: dict[str, set[int]] = {key: set() for key in ("judge", "correction", "tokens", "min")}
    n_tasks = len(data.get("tasks") or [])
    agg = {key: [aggregate_metric(s, key, n_tasks, k) for s in skills] for key in bold}
    agg["ssr"] = [aggregate_ssr(s, n_tasks, k) for s in skills]
    agg["pass1"] = [float(s["pass_at_1"]) for s in skills]
    agg["pass2"] = [float(s["pass_squared"]) for s in skills]
    for key in ("ssr", "pass1", "pass2"):
        bold[key] = set()
    baseline = next((s for s in skills if s.get("is_baseline")), None)
    base_fracs = task_pass_fracs(baseline) if baseline else None
    for key, maximize in (("pass1", True), ("ssr", True), ("pass2", True), ("judge", True), ("correction", False), ("tokens", False), ("min", False)):
        cand = [(v, i) for i, v in enumerate(agg[key]) if v is not None and not skills[i].get("is_baseline")]
        if cand:
            best = (max(cand) if maximize else min(cand))[0]
            bold[key] = {i for v, i in cand if abs(v - best) < 1e-9}

    rows: list[str] = []
    for i, s in enumerate(skills):
        colors = palette[i]
        is_base = bool(s.get("is_baseline"))
        p2, p1 = float(s["pass_squared"]), float(s["pass_at_1"])
        solid_pct = max(0.0, min(100.0, (p2 / x_max) * 100.0))
        full_pct = max(0.0, min(100.0, (p1 / x_max) * 100.0))
        hatch_w = max(0.0, full_pct - solid_pct)
        solid_round = " round-full" if hatch_w < 0.05 else ""
        name_cls = "skill-name baseline" if is_base else "skill-name"
        hatch_style = (
            f"left:{solid_pct:.4f}%;width:{hatch_w:.4f}%;"
            f"background:repeating-linear-gradient(-45deg,{colors['hatch']},{colors['hatch']} 2px,"
            f"{colors['solid']} 2px,{colors['solid']} 3.5px);"
        )

        if is_base or base_fracs is None:
            vs_cell = '<div class="vs-agg"><div class="vs-delta base">—</div></div>'
        else:
            delta = p1 - float(baseline["pass_at_1"])
            lo, hi = paired_bootstrap_ci(task_pass_fracs(s), base_fracs)
            dcls = "zero" if abs(delta) < 1e-9 else ("pos" if delta > 0 else "neg")
            vs_cell = (
                f'<div class="vs-agg"><div class="vs-delta {dcls}">{fmt_pp(delta)} pp</div>'
                f'<div class="vs-ci">[{fmt_pp(lo)}, {fmt_pp(hi)}]</div></div>'
            )

        def metric_cell(key: str) -> str:
            v = agg[key][i]
            if v is None:
                text, cls = "—", "metric empty"
            elif key in ("ssr", "pass1", "pass2"):
                text, cls = pct_label(float(v)), "metric"
            elif key == "tokens":
                text, cls = fmt_tokens(float(v)), "metric"
            elif key == "judge":
                text, cls = fmt_judge(v, 3), "metric"
            elif key == "correction":
                text, cls = f"{float(v):.2f}", "metric"
            else:
                text, cls = f"{float(v):.1f}", "metric"
            if i in bold[key]:
                cls += " best"
            return f'<td class="col-metric"><div class="{cls}">{text}</div></td>'

        rows.append(f"""
        <tr>
          <td class="col-skill"><div class="skill-cell">
            <span class="dot" style="background:{colors['dot']}"></span>
            <span class="{name_cls}">{skill_display_name(s, lang)}</span>
          </div></td>
          <td class="col-bar"><div class="bar-wrap">
            <div class="track">
              <div class="bar-hatch" style="{hatch_style}"></div>
              <div class="bar-solid{solid_round}" style="width:{solid_pct:.4f}%;background:{colors['solid']}"></div>
            </div>
          </div></td>
          {metric_cell('pass1')}{metric_cell('ssr')}{metric_cell('pass2')}{metric_cell('judge')}{metric_cell('correction')}{metric_cell('tokens')}{metric_cell('min')}
          <td class="col-vs">{vs_cell}</td>
        </tr>""")

    ticks = "".join(
        f'<div class="axis-tick" style="left:{(float(t)/x_max)*100:.4f}%"><span>{int(t)}%</span></div>'
        for t in x_ticks
    )
    body = f"""
      <table class="table">
        <thead><tr>
          <th class="col-skill">{t(lang, "skill")}</th><th class="col-bar"></th>
          <th class="col-metric">{METRIC_HEADERS["pass1"]}</th><th class="col-metric">{METRIC_HEADERS["ssr"]}</th><th class="col-metric">{METRIC_HEADERS["pass2"]}</th>
          <th class="col-metric wide">{METRIC_HEADERS["judge"]}</th><th class="col-metric wide">{METRIC_HEADERS["ucorr"]}</th>
          <th class="col-metric wide">{METRIC_HEADERS["tokens"]}</th><th class="col-metric wide">{METRIC_HEADERS["mins"]}</th>
          <th class="col-vs">{t(lang, "vs_baseline")}</th>
        </tr></thead>
        <tbody>
{''.join(rows)}
        <tr class="axis-row"><td></td><td class="col-bar"><div class="axis"><div class="axis-line"></div>{ticks}</div></td><td colspan="8"></td></tr>
        </tbody>
      </table>"""
    extra = f'<div class="note">{t(lang, "sort_note")}</div>'
    legend = f"""
          <div class="legend-item"><span class="swatch solid"></span>{legend.get('solid', 'pass²')}</div>
          <div class="legend-item"><span class="swatch hatch"></span>{legend.get('hatched', 'pass@1 − pass²')}</div>"""
    return shell(title, subtitle, legend, body, CHART1_CSS, watermark, extra, lang=lang)

def render_task_detail(data: dict[str, Any], task_id: str, lang: str = "en") -> str:
    meta = data.get("meta", {})
    skills = ordered_skills(list(data["skills"]))
    palette = skill_palette(skills)
    ti = find_task_index(data, task_id)
    task = data["tasks"][ti]
    tid = task["id"]
    watermark = t(lang, "watermark")
    harness = meta.get("harness", "Codex CLI")
    model = meta.get("model", "GPT-6 Luna")
    k = meta.get("k", 2)
    repo = task.get("repo", "—")
    title = f"{tid} · {repo}"
    subtitle = brand_subtitle(meta, t(lang, "subtitle_rest_task", k=k))
    baseline = next(s for s in skills if s.get("is_baseline"))
    base_outcome = baseline["task_outcomes"][ti]
    base_runs = baseline["task_runs"][ti]
    base_p1 = task_pass_at_1_pct(base_outcome, base_runs)
    scored: dict[str, list[tuple[float, int]]] = {k: [] for k in ("judge", "correction", "tokens", "min")}
    row_avgs: list[dict[str, Any]] = []
    for i, s in enumerate(skills):
        metrics_pair = (s.get("task_run_metrics") or [None] * len(s["task_outcomes"]))[ti]
        avg = avg_metrics(metrics_pair)
        row_avgs.append(avg)
        if s.get("is_baseline"):
            continue
        for key, maximize in (("judge", True), ("correction", False), ("tokens", False), ("min", False)):
            v = avg.get(key)
            if v is None:
                continue
            scored[key].append((float(v), i))

    bold: dict[str, set[int]] = {k: set() for k in scored}
    for key, maximize in (("judge", True), ("correction", False), ("tokens", False), ("min", False)):
        if not scored[key]:
            continue
        target = max(scored[key])[0] if maximize else min(scored[key])[0]
        for val, i in scored[key]:
            if val == target:
                bold[key].add(i)

    rows = []
    for i, s in enumerate(skills):
        colors = palette[i]
        is_base = bool(s.get("is_baseline"))
        outcome = s["task_outcomes"][ti]
        runs = s["task_runs"][ti]
        r1, r2 = bool(runs[0]), bool(runs[1])
        n_pass = int(r1) + int(r2)
        expect = {"both": 2, "one": 1, "none": 0}[outcome]
        if n_pass != expect:
            raise SystemExit(f"Inconsistent runs for {s['name']} on {tid}")

        pass2_ok = r1 and r2
        p1 = task_pass_at_1_pct(outcome, runs)
        delta = p1 - base_p1

        avg = row_avgs[i]

        def pill(ok: bool) -> str:
            if ok:
                return '<span class="pill pass">✓</span>'
            return '<span class="pill fail">✗</span>'

        def pass2_cell() -> str:
            if pass2_ok:
                return '<span class="pill pass">✓</span>'
            return '<span class="pill dash">—</span>'

        def metric_html(key: str) -> str:
            v = avg.get(key)
            if v is None:
                return '<div class="metric empty">—</div>'
            if key == "judge":
                text = fmt_judge(v)
            elif key == "correction":
                text = f"{v:.2f}"
            elif key == "tokens":
                text = fmt_tokens(v)
            else:
                text = f"{v:.1f}"
            cls = "metric best" if i in bold[key] else "metric"
            return f'<div class="{cls}">{text}</div>'

        if is_base:
            vs_html = '<div class="vs-cell"><div class="vs-delta base">—</div></div>'
        else:
            if abs(delta) < 1e-9:
                dcls, dtxt = "zero", "0 pp"
            elif delta > 0:
                dcls, dtxt = "pos", f"+{delta:.0f} pp"
            else:
                dcls, dtxt = "neg", f"{delta:.0f} pp"
            vs_html = f'<div class="vs-cell"><div class="vs-delta {dcls}">{dtxt}</div></div>'

        name_cls = "skill-name baseline" if is_base else "skill-name"
        rows.append(f"""
        <tr>
          <td class="col-skill"><div class="skill-cell">
            <span class="dot" style="background:{colors['dot']}"></span>
            <span class="{name_cls}">{skill_display_name(s, lang)}</span>
          </div></td>
          <td>{pill(r1)}</td>
          <td>{pill(r2)}</td>
          <td>{pass2_cell()}</td>
          <td>{metric_html('judge')}</td>
          <td>{metric_html('correction')}</td>
          <td>{metric_html('tokens')}</td>
          <td>{metric_html('min')}</td>
          <td class="col-vs">{vs_html}</td>
        </tr>""")

    desc = task.get("description") or task.get("label", "")
    header_extra = f'        <div class="task-desc">{desc}</div>\n' if desc else ""
    legend = ""
    body = f"""
      <table class="table">
        <thead>
          <tr>
            <th class="col-skill">{t(lang, "skill")}</th>
            <th class="col-run">{t(lang, "rep1")}</th>
            <th class="col-run">{t(lang, "rep2")}</th>
            <th class="col-pass2">{METRIC_HEADERS["pass2_short"]}</th>
            <th class="col-metric">{METRIC_HEADERS["judge"]}</th>
            <th class="col-metric">{METRIC_HEADERS["ucorr"]}</th>
            <th class="col-metric">{METRIC_HEADERS["tokens"]}</th>
            <th class="col-metric">{METRIC_HEADERS["mins"]}</th>
            <th class="col-vs">{t(lang, "vs_baseline")}</th>
          </tr>
        </thead>
        <tbody>
{''.join(rows)}
        </tbody>
      </table>
"""
    extra = ""
    return shell(title, subtitle, legend, body, DETAIL_CSS, watermark, extra, header_extra, lang=lang)

def render_task_matrix(data: dict[str, Any], lang: str = "en") -> str:
    meta = data.get("meta", {})
    legend = data.get("legend") or {}
    skills = ordered_skills(list(data["skills"]))
    palette = skill_palette(skills)
    tasks = data.get("tasks") or []
    n_tasks = len(tasks)
    verify_reconcile(skills, n_tasks)
    k = int(meta.get("k", 2))
    title = t(lang, "title_matrix")
    meta_h = meta.get("harness", "Codex CLI")
    meta_m = meta.get("model", "GPT-6 Luna")
    subtitle = brand_subtitle(meta, t(lang, "subtitle_rest_matrix", k=k))
    watermark = t(lang, "watermark")

    th_tasks = "".join(
        f'<th class="task-col" title="{t.get("label", t["id"])}">{t["id"].replace("T", "")}</th>'
        for t in tasks
    )
    rows = []
    for si, s in enumerate(skills):
        colors = palette[si]
        is_base = bool(s.get("is_baseline"))
        name_cls = "skill-name baseline" if is_base else "skill-name"
        outs = s["task_outcomes"]
        runs = s["task_runs"]
        both = sum(1 for o in outs if o == "both")
        one = sum(1 for o in outs if o == "one")
        p2 = both / n_tasks * 100.0
        p1 = aggregate_pass_at_1_pct(outs)
        cells = []
        for ti, o in enumerate(outs):
            r1, r2 = runs[ti]
            cells.append(
                f'<td><div class="cell-mark" title="{o}">'
                f'<div class="runs"><span class="{"y" if r1 else "n"}">{"✓" if r1 else "✗"}</span>'
                f'<span class="{"y" if r2 else "n"}">{"✓" if r2 else "✗"}</span></div></div></td>'
            )
        rows.append(f"""
        <tr>
          <td class="sticky-col"><div class="skill-cell">
            <span class="dot" style="background:{colors['dot']}"></span>
            <span class="{name_cls}">{skill_display_name(s, lang)}</span>
          </div></td>
          {''.join(cells)}
          <td class="summary">{pct_label(p2)}<span class="summary-sub">pass²</span></td>
          <td class="summary">{pct_label(p1)}<span class="summary-sub">pass@1</span></td>
        </tr>""")

    body = f"""
      <div class="matrix-scroll"><table class="matrix">
        <thead><tr>
          <th class="sticky-col">{t(lang, "skill")}</th>{th_tasks}
          <th class="summary">{METRIC_HEADERS["pass2_short"]}</th><th class="summary">pass@1</th>
        </tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table></div>"""
    legend_html = f"""
          <div class="legend-item"><span class="chip both">✓✓</span>{t(lang, "legend_both")}</div>
          <div class="legend-item"><span class="chip one">✓✗</span>{t(lang, "legend_one")}</div>
          <div class="legend-item"><span class="chip none">✗✗</span>{t(lang, "legend_none")}</div>"""
    extra = f'<div class="note">{t(lang, "matrix_note")}</div>'
    return shell(title, subtitle, legend_html, body, MATRIX_CSS, watermark, extra, lang=lang)

def write(path: Path, html: str) -> None:
    path.write_text(html, encoding="utf-8")
    print(f"Wrote {path}")

def main() -> None:
    here = Path(__file__).resolve().parent
    p = argparse.ArgumentParser(description="Render Skill HTML charts from data.json")
    p.add_argument("--data", type=Path, default=here / "data.json")
    p.add_argument("--task", type=str, default=None, help="Task id for detail page, e.g. T01")
    p.add_argument("--all-tasks", action="store_true", help="Also render all task detail pages")
    p.add_argument("--no-matrix", action="store_true", help="Skip optional matrix HTML")
    p.add_argument("--lang", choices=("en", "zh"), default="en",
                   help="UI language pack (metric headers stay English in both)")
    p.add_argument("--both-langs", action="store_true",
                   help="Emit .en.html and .zh.html (and EN aliases without suffix)")
    p.add_argument("--out1", type=Path, default=None)
    p.add_argument("--out-matrix", type=Path, default=None)
    args = p.parse_args()

    data = load_data(args.data)
    skills = ordered_skills(list(data["skills"]))
    n_tasks = len(data.get("tasks") or [])
    if n_tasks:
        verify_reconcile(skills, n_tasks)

    langs = ("en", "zh") if args.both_langs else (args.lang,)

    def emit_task(tid: str, lang: str) -> None:
        html = render_task_detail(data, tid, lang)
        write(here / f"skill_task_{tid}.{lang}.html", html)
        if lang == "en":
            write(here / f"skill_task_{tid}.html", html)

    if args.task:
        tid = data["tasks"][find_task_index(data, args.task)]["id"]
        for lang in langs:
            emit_task(tid, lang)
        return

    for lang in langs:
        lb = render_leaderboard(data, lang)
        write(here / f"skill_leaderboard.{lang}.html", lb)
        if lang == "en":
            out1 = args.out1 or (here / "skill_leaderboard.html")
            write(out1, lb)
        if not args.no_matrix:
            mx = render_task_matrix(data, lang)
            write(here / f"skill_task_matrix.{lang}.html", mx)
            if lang == "en":
                outm = args.out_matrix or (here / "skill_task_matrix.html")
                write(outm, mx)

    demo_id = None
    for i, task in enumerate(data["tasks"]):
        outs = [s["task_outcomes"][i] for s in skills]
        if len(set(outs)) >= 3:
            demo_id = task["id"]
            break
    if demo_id is None:
        demo_id = data["tasks"][0]["id"]
    for lang in langs:
        emit_task(demo_id, lang)

    if args.all_tasks:
        for task in data["tasks"]:
            for lang in langs:
                emit_task(task["id"], lang)

if __name__ == "__main__":
    main()
