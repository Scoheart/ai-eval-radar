#!/usr/bin/env python3
"""
Paper-table layout for Skill Effectiveness (SWE-Together style panel).

Fixed harness/model; rows = Skill configs. Reads data.json → PNG + SVG.
Optional Inter fonts: place Inter-Regular.ttf / Inter-Bold.ttf under ./fonts/.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyBboxPatch


# Canvas white; card is light gray inset with padding
COLOR_BG = "#FFFFFF"
COLOR_CARD = "#ECEEF2"
COLOR_ROW_A = "#FFFFFF"
COLOR_ROW_B = "#F7F8FA"
COLOR_TRACK = "#E4E6EB"
COLOR_TEXT = "#111827"
COLOR_MUTED = "#6B7280"
COLOR_HEADER = "#9CA3AF"
COLOR_SEP = "#E8EAED"
COLOR_WATERMARK = "#D1D5DB"

BLUE_ACCENT = "#2563EB"
BLUE_MID = "#5B9AF5"
BLUE_LIGHT = "#93C5FD"
HATCH_ACCENT = "#A8C7FC"
HATCH_MID = "#C7DBFE"
HATCH_LIGHT = "#DCE8FE"
GRAY_SOLID = "#9CA3AF"
GRAY_HATCH = "#D8DBE0"
GRAY_EDGE = "#9CA3AF"
DOT_BASE = "#9CA3AF"


def _setup_fonts() -> str:
    sibling = Path(__file__).resolve().parent / "fonts"
    for fname in ("Inter-Regular.ttf", "Inter-Bold.ttf"):
        fp = sibling / fname
        if fp.is_file():
            try:
                font_manager.fontManager.addfont(str(fp))
            except Exception:
                pass
    candidates = ["Inter", "Helvetica", "Liberation Sans", "DejaVu Sans"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = next((c for c in candidates if c in available), "DejaVu Sans")
    mpl.rcParams["font.family"] = "sans-serif"
    mpl.rcParams["font.sans-serif"] = [chosen, "DejaVu Sans", "sans-serif"]
    mpl.rcParams["axes.unicode_minus"] = False
    mpl.rcParams["hatch.linewidth"] = 0.55
    return chosen


def load_data(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _parse_tokens(val: Any) -> float | None:
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


def ordered_skills(skills: list[dict[str, Any]]) -> list[dict[str, Any]]:
    base = [s for s in skills if s.get("is_baseline")]
    rest = sorted(
        [s for s in skills if not s.get("is_baseline")],
        key=lambda s: float(s["pass_at_1"]),
        reverse=True,
    )
    return base + rest


def skill_colors(skills: list[dict[str, Any]]) -> list[tuple[str, str, str, str]]:
    """(solid, hatch_fill, hatch_edge, dot) per ordered skill."""
    out: list[tuple[str, str, str, str]] = []
    blues = [
        (BLUE_ACCENT, HATCH_ACCENT, BLUE_ACCENT, BLUE_ACCENT),
        (BLUE_MID, HATCH_MID, BLUE_MID, BLUE_MID),
        (BLUE_LIGHT, HATCH_LIGHT, BLUE_LIGHT, BLUE_LIGHT),
    ]
    bi = 0
    for s in skills:
        if s.get("is_baseline"):
            out.append((GRAY_SOLID, GRAY_HATCH, GRAY_EDGE, DOT_BASE))
        else:
            out.append(blues[min(bi, len(blues) - 1)])
            bi += 1
    return out


def best_flags(skills: list[dict[str, Any]]) -> dict[str, set[int]]:
    flags: dict[str, set[int]] = {k: set() for k in ("judge", "correction", "tokens", "min")}
    non = [(i, s) for i, s in enumerate(skills) if not s.get("is_baseline")]

    def collect(key: str, maximize: bool) -> None:
        scored: list[tuple[float, int]] = []
        for i, s in non:
            v = s.get(key)
            num = _parse_tokens(v) if key == "tokens" else (None if v is None else float(v))
            if num is None:
                continue
            scored.append((num, i))
        if not scored:
            return
        target = max(scored)[0] if maximize else min(scored)[0]
        for num, i in scored:
            if num == target:
                flags[key].add(i)

    collect("judge", True)
    collect("correction", False)
    collect("tokens", False)
    collect("min", False)
    return flags


def _fmt(v: Any, kind: str) -> str:
    if v is None:
        return "—"
    if kind == "judge":
        return f"{float(v):.3f}"
    if kind == "correction":
        return f"{float(v):.2f}"
    if kind == "tokens":
        return str(v)
    if kind == "min":
        return f"{float(v):.1f}"
    return str(v)


def _pct_label(v: float) -> str:
    if abs(v - round(v)) < 1e-6:
        return f"{int(round(v))}%"
    return f"{v:.1f}%"


def _rbox(ax, x, y, w, h, fc, ec="none", lw=0.0, hatch=None, z=2, rad=None):
    if w <= 0 or h <= 0:
        return None
    r = rad if rad is not None else min(h * 0.48, 0.42)
    p = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.0,rounding_size={r}",
        facecolor=fc,
        edgecolor=ec if hatch or ec != "none" else "none",
        linewidth=lw if hatch or ec != "none" else 0.0,
        zorder=z,
    )
    if hatch:
        p.set_hatch(hatch)
        p.set_edgecolor(ec if ec != "none" else fc)
        p.set_linewidth(max(lw, 0.4))
    ax.add_patch(p)
    return p


def draw(data: dict[str, Any], out_png: Path, out_svg: Path) -> None:
    _setup_fonts()
    meta = data.get("meta", {})
    legend = data.get("legend") or {"solid": "Pass²", "hatched": "Pass@1 − Pass²"}
    skills = ordered_skills(list(data["skills"]))
    colors = skill_colors(skills)
    bold = best_flags(skills)
    n = len(skills)
    x_max = float(meta.get("x_max", 80))
    x_ticks = meta.get("x_ticks", [0, 20, 40, 60, 80])
    watermark = meta.get(
        "watermark", "Illustrative Data — Not Actual Benchmark Results"
    )
    title = meta.get("title", "Skill Effectiveness on SWE-Together")
    subtitle = meta.get("subtitle", "Codex CLI · GPT-6 Luna · SWE-Together · k=2")

    # White canvas; gray card inset with visible margin
    fig_w, fig_h = 14.5, 5.6
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=250, facecolor=COLOR_BG)
    # Leave margin so card is not flush to edge
    ax = fig.add_axes([0.035, 0.045, 0.93, 0.91])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    ax.set_facecolor(COLOR_BG)

    # Light-gray rounded card with internal padding
    card_x, card_y = 3.5, 8.0
    card_w, card_h = 93.0, 84.5
    _rbox(ax, card_x, card_y, card_w, card_h, COLOR_CARD, z=0, rad=1.6)

    # Content inset inside card
    pad_l = card_x + 2.8
    pad_r = card_x + card_w - 2.8

    # Title + subtitle inside card
    ax.text(
        pad_l, 88.8, title,
        ha="left", va="center", fontsize=14.0,
        fontweight="bold", color=COLOR_TEXT, zorder=3,
    )
    ax.text(
        pad_l, 84.2, subtitle,
        ha="left", va="center", fontsize=8.6,
        color=COLOR_MUTED, zorder=3,
    )

    # Legend under subtitle
    leg_y = 79.2
    _rbox(ax, pad_l, leg_y - 0.6, 1.55, 1.2, BLUE_ACCENT, z=3, rad=0.2)
    ax.text(
        pad_l + 2.0, leg_y, legend.get("solid", "Pass²"),
        ha="left", va="center", fontsize=7.8, color=COLOR_MUTED, zorder=3,
    )
    hx = pad_l + 10.5
    _rbox(
        ax, hx, leg_y - 0.6, 1.55, 1.2, HATCH_ACCENT,
        ec=BLUE_ACCENT, lw=0.4, hatch="////", z=3, rad=0.2,
    )
    ax.text(
        hx + 2.0, leg_y, legend.get("hatched", "Pass@1 − Pass²"),
        ha="left", va="center", fontsize=7.8, color=COLOR_MUTED, zorder=3,
    )

    # Column layout — widen metric columns, leave room so they aren't crushed
    # SKILL | BAR (to 80%) | tip labels | JUDGE | CORRECTION | TOKENS | MIN
    col_dot_x = pad_l + 0.55
    col_skill_x = pad_l + 1.9
    col_bar_x0 = 22.0
    col_bar_x1 = 52.0   # slightly narrower bar so metrics get more room
    # Metric columns evenly spaced with generous centers
    col_judge_x = 61.5
    col_corr_x = 72.8
    col_tok_x = 83.8
    col_min_x = 93.5

    header_y = 73.8
    body_top = header_y - 1.4
    body_bot = 18.5
    row_h = (body_top - body_bot) / n
    bar_h = row_h * 0.34
    track_h = bar_h * 1.35

    # Small gray UPPERCASE headers
    hk = dict(fontsize=7.2, color=COLOR_HEADER, fontweight="bold", va="center", zorder=4)
    ax.text(col_skill_x, header_y, "SKILL", ha="left", **hk)
    ax.text(col_judge_x, header_y, "JUDGE ↑", ha="center", **hk)
    ax.text(col_corr_x, header_y, "CORRECTION ↓", ha="center", **hk)
    ax.text(col_tok_x, header_y, "TOKENS", ha="center", **hk)
    ax.text(col_min_x, header_y, "MIN", ha="center", **hk)

    # Header rule across content width
    ax.plot(
        [pad_l, pad_r], [header_y - 1.3, header_y - 1.3],
        color=COLOR_SEP, lw=0.7, zorder=3,
    )

    bar_span = col_bar_x1 - col_bar_x0

    def px(pct: float) -> float:
        return col_bar_x0 + (pct / x_max) * bar_span

    row_left = pad_l - 0.4
    row_right = pad_r + 0.4
    row_w = row_right - row_left

    for i, s in enumerate(skills):
        yc = body_top - (i + 0.5) * row_h
        y0 = yc - bar_h / 2
        ty0 = yc - track_h / 2
        solid_c, hatch_c, hatch_e, dot_c = colors[i]
        is_base = bool(s.get("is_baseline"))

        # Zebra row background (full content width, slight round)
        row_fc = COLOR_ROW_A if i % 2 == 0 else COLOR_ROW_B
        row_y = body_top - (i + 1) * row_h
        _rbox(
            ax, row_left, row_y, row_w, row_h,
            row_fc, z=1, rad=0.25,
        )

        # Subtle separator
        if i > 0:
            sy = body_top - i * row_h
            ax.plot(
                [pad_l, pad_r], [sy, sy],
                color=COLOR_SEP, lw=0.35, zorder=2,
            )

        # Colored dot before skill name
        ax.add_patch(
            Circle(
                (col_dot_x, yc),
                0.48,
                facecolor=dot_c,
                edgecolor="none",
                zorder=4,
            )
        )

        ax.text(
            col_skill_x, yc, s["name"],
            ha="left", va="center",
            fontsize=9.4 if not is_base else 9.0,
            color=COLOR_MUTED if is_base else COLOR_TEXT,
            fontweight="normal", zorder=4,
        )

        p2 = float(s["pass_squared"])
        p1 = float(s["pass_at_1"])

        # Rounded track full width to 80%
        _rbox(
            ax, col_bar_x0, ty0, px(x_max) - col_bar_x0, track_h,
            COLOR_TRACK, z=2, rad=track_h * 0.48,
        )

        # Full hatched silhouette then solid overlay
        full_w = px(p1) - col_bar_x0
        _rbox(
            ax, col_bar_x0, y0, full_w, bar_h, hatch_c,
            ec=hatch_e, lw=0.35, hatch="////", z=3, rad=bar_h * 0.48,
        )
        solid_w = px(p2) - col_bar_x0
        _rbox(
            ax, col_bar_x0, y0, solid_w, bar_h, solid_c,
            z=4, rad=min(bar_h * 0.48, solid_w * 0.4),
        )

        # White Pass² % inside solid — one size smaller than tip
        if solid_w > 2.5:
            ax.text(
                col_bar_x0 + solid_w * 0.5, yc, _pct_label(p2),
                ha="center", va="center", fontsize=6.8,
                color="#FFFFFF", fontweight="bold", zorder=6,
            )

        # Bold Pass@1 at tip
        ax.text(
            px(p1) + 0.55, yc, _pct_label(p1),
            ha="left", va="center", fontsize=8.8,
            color=COLOR_TEXT, fontweight="bold", zorder=6,
        )

        def cell(x: float, text: str, is_b: bool) -> None:
            ax.text(
                x, yc, text,
                ha="center", va="center", fontsize=9.0,
                color=COLOR_MUTED if text == "—" else COLOR_TEXT,
                fontweight="bold" if is_b else "normal", zorder=4,
            )

        cell(col_judge_x, _fmt(s.get("judge"), "judge"), i in bold["judge"])
        cell(col_corr_x, _fmt(s.get("correction"), "correction"), i in bold["correction"])
        cell(col_tok_x, _fmt(s.get("tokens"), "tokens"), i in bold["tokens"])
        cell(col_min_x, _fmt(s.get("min"), "min"), i in bold["min"])

    # Axis under bars only
    ay = body_bot - 0.2
    ax.plot(
        [col_bar_x0, px(x_max)], [ay + 1.2, ay + 1.2],
        color="#D1D5DB", lw=0.6, zorder=2,
    )
    for t in x_ticks:
        tx = px(float(t))
        ax.plot([tx, tx], [ay + 1.2, ay + 1.7], color=COLOR_MUTED, lw=0.5)
        ax.text(
            tx, ay + 0.25, f"{int(t)}%",
            ha="center", va="top", fontsize=6.8, color=COLOR_MUTED, zorder=3,
        )

    # Watermark below card
    ax.text(
        50, 4.0, watermark,
        ha="center", va="center", fontsize=7.0,
        color=COLOR_WATERMARK, style="italic", zorder=5,
    )

    out_png.parent.mkdir(parents=True, exist_ok=True)
    for path, dpi in ((out_png, 250), (out_svg, None)):
        kw = dict(
            facecolor=COLOR_BG,
            edgecolor="none",
            bbox_inches="tight",
            pad_inches=0.28,  # outer margin so card isn't flush
        )
        if dpi:
            kw["dpi"] = dpi
        fig.savefig(path, **kw)
    plt.close(fig)

    try:
        from PIL import Image

        im = Image.open(out_png)
        if im.width < 2400:
            sc = 2400 / im.width
            im.resize((2400, int(im.height * sc)), Image.Resampling.LANCZOS).save(out_png)
    except Exception:
        pass


def main() -> None:
    here = Path(__file__).resolve().parent
    p = argparse.ArgumentParser(description="Skill table in SWE-Together paper layout")
    p.add_argument("--data", type=Path, default=here / "data.json")
    p.add_argument("--png", type=Path, default=here / "swe_together_leaderboard.png")
    p.add_argument("--svg", type=Path, default=here / "swe_together_leaderboard.svg")
    args = p.parse_args()
    draw(load_data(args.data), args.png, args.svg)
    print(f"Wrote {args.png}")
    print(f"Wrote {args.svg}")


if __name__ == "__main__":
    main()
