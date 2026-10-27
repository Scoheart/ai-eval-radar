#!/usr/bin/env python3
"""
Reusable Skill Effectiveness leaderboard chart (community / publication style).

Reads skill evaluation results from JSON and exports PNG + SVG.
Not a model leaderboard — compares Skill configurations under fixed
harness / model / benchmark.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Patch, PathPatch, FancyBboxPatch
from matplotlib.transforms import Affine2D, Bbox, TransformedBbox
from lxml import etree
from svgpath2mpl import parse_path


# --- community-chart palette (one accent for top skill only) ---
ACCENT_PASS2 = "#2563EB"
ACCENT_UNSTABLE = "#BFDBFE"
GRAY_PASS2 = "#9CA3AF"
GRAY_UNSTABLE = "#E5E7EB"
BASE_PASS2 = "#C7CBD1"
BASE_UNSTABLE = "#EEF0F2"
COLOR_BASELINE_LINE = "#D1D5DB"
COLOR_TEXT = "#111827"
COLOR_MUTED = "#6B7280"
COLOR_LABEL = "#374151"
COLOR_GRID = "#F1F3F5"
COLOR_BG = "#FFFFFF"
COLOR_UPLIFT_POS = "#059669"
COLOR_UPLIFT_NEG = "#DC2626"
COLOR_WATERMARK = "#D1D5DB"


def _setup_fonts() -> str:
    """Prefer static Inter Regular/Bold; keep Noto CJK as CJK fallback."""
    script_fonts = Path(__file__).resolve().parent / "fonts"
    for fname in ("Inter-Regular.ttf", "Inter-Bold.ttf"):
        fp = script_fonts / fname
        if fp.is_file():
            try:
                font_manager.fontManager.addfont(str(fp))
            except Exception:
                pass

    candidates = [
        "Inter",
        "Helvetica",
        "Liberation Sans",
        "DejaVu Sans",
        "Noto Sans CJK SC",
        "Noto Sans",
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = next((c for c in candidates if c in available), "DejaVu Sans")
    mpl.rcParams["font.family"] = "sans-serif"
    mpl.rcParams["font.sans-serif"] = [
        chosen,
        "Noto Sans CJK SC",
        "DejaVu Sans",
        "sans-serif",
    ]
    mpl.rcParams["axes.unicode_minus"] = False
    return chosen


def load_data(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if "skills" not in data or not isinstance(data["skills"], list):
        raise ValueError("JSON must contain a non-empty 'skills' list")
    if not data["skills"]:
        raise ValueError("'skills' list is empty")
    return data


def validate_and_prepare(
    data: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], bool]:
    meta = data.get("meta") or {}
    k = int(meta.get("k", 2))
    baseline_name = meta.get("baseline_name", "No Skill")

    skills: list[dict[str, Any]] = []
    for raw in data["skills"]:
        name = str(raw["name"])
        p1 = float(raw["pass_at_1"])
        p2_raw = raw.get("pass_squared", None)

        if not (0.0 <= p1 <= 100.0):
            raise ValueError(f"{name}: pass_at_1={p1} out of range [0, 100]")

        if p2_raw is None or k < 2:
            p2 = None
        else:
            p2 = float(p2_raw)
            if not (0.0 <= p2 <= 100.0):
                raise ValueError(f"{name}: pass_squared={p2} out of range [0, 100]")
            if p2 > p1:
                raise ValueError(
                    f"{name}: pass_squared ({p2}) > pass_at_1 ({p1}) — "
                    "require 0 ≤ Pass² ≤ Pass@1 ≤ 100"
                )

        is_baseline = bool(raw.get("is_baseline", False)) or name == baseline_name
        skills.append(
            {
                "name": name,
                "pass_at_1": p1,
                "pass_squared": p2,
                "is_baseline": is_baseline,
            }
        )

    has_pass2 = k >= 2 and all(s["pass_squared"] is not None for s in skills)
    if not has_pass2:
        for s in skills:
            s["pass_squared"] = None

    baselines = [s for s in skills if s["is_baseline"]]
    if not baselines:
        for s in skills:
            if s["name"] == baseline_name:
                s["is_baseline"] = True
                baselines = [s]
                break
        if not baselines:
            skills[0]["is_baseline"] = True
            baselines = [skills[0]]
            print(
                f"Warning: no baseline marked; using '{skills[0]['name']}'",
                file=sys.stderr,
            )
    if len(baselines) > 1:
        raise ValueError("Multiple baseline skills marked; keep exactly one")

    baseline_p1 = baselines[0]["pass_at_1"]
    for s in skills:
        s["uplift_pp"] = round(s["pass_at_1"] - baseline_p1, 1)

    skills.sort(key=lambda s: s["pass_at_1"], reverse=True)
    return skills, meta, has_pass2


def _png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as f:
        sig = f.read(8)
        if sig[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Not a PNG: {path}")
        while True:
            length = struct.unpack(">I", f.read(4))[0]
            ctype = f.read(4)
            chunk = f.read(length)
            f.read(4)
            if ctype == b"IHDR":
                w, h = struct.unpack(">II", chunk[:8])
                return w, h


def _row_colors(s: dict[str, Any], is_top: bool) -> tuple[str, str]:
    if s["is_baseline"]:
        return BASE_PASS2, BASE_UNSTABLE
    if is_top:
        return ACCENT_PASS2, ACCENT_UNSTABLE
    return GRAY_PASS2, GRAY_UNSTABLE


def _display_name(name: str) -> str:
    """Drop trailing ' Skill' for cleaner Y labels; keep 'No Skill' intact."""
    if name.strip() == "No Skill":
        return "No Skill"
    return re.sub(r"\s+Skill$", "", name).strip() or name


def _resolve_logo_path(raw: str | None, base_dir: Path) -> Path | None:
    if not raw:
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = (base_dir / path).resolve()
    return path if path.is_file() else None


def _load_svg_mpl_paths(svg_path: Path):
    """Parse SVG path elements into matplotlib Path objects (vector)."""
    root = etree.parse(str(svg_path)).getroot()
    mpl_paths = []
    for el in root.xpath(".//*[local-name()=\"path\"]"):
        d = el.get("d")
        if d:
            mpl_paths.append(parse_path(d))
    if not mpl_paths:
        raise ValueError(f"No <path> elements in SVG: {svg_path}")
    return mpl_paths


def _add_svg_logo_fig(
    fig,
    svg_path: Path,
    x_left: float,
    y_center: float,
    height: float,
    color: str = "#6B7280",
) -> float:
    """
    Draw SVG logo as vector PathPatches in figure coordinates.
    Returns the right edge x (figure fraction) after the logo.
    """
    mpl_paths = _load_svg_mpl_paths(svg_path)
    # Union bbox in SVG user units
    xs, ys = [], []
    for mp in mpl_paths:
        verts = mp.vertices
        xs.extend(verts[:, 0])
        ys.extend(verts[:, 1])
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    bw = max(maxx - minx, 1e-6)
    bh = max(maxy - miny, 1e-6)
    scale = height / bh
    width = bw * scale
    # Place bottom-left at (x_left, y_center - height/2)
    x0 = x_left
    y0 = y_center - height / 2.0

    for mp in mpl_paths:
        # Transform SVG coords → figure fraction (flip Y: SVG down vs figure up)
        verts = mp.vertices.copy()
        verts[:, 0] = (verts[:, 0] - minx) * scale + x0
        verts[:, 1] = y0 + height - (verts[:, 1] - miny) * scale
        new_path = type(mp)(verts, mp.codes)
        patch = PathPatch(
            new_path,
            facecolor=color,
            edgecolor="none",
            transform=fig.transFigure,
            clip_on=False,
            zorder=10,
        )
        fig.add_artist(patch)
    return x_left + width



def draw(
    skills: list[dict[str, Any]],
    meta: dict[str, Any],
    has_pass2: bool,
    out_png: Path,
    out_svg: Path,
) -> None:
    _setup_fonts()

    n = len(skills)
    # 16:9 @ 200 dpi → 3200×1800
    fig_w, fig_h = 16.0, 9.0
    dpi = 200

    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_facecolor(COLOR_BG)

    # Roomier row pitch; thin bars ~32% of pitch
    row_pitch = 1.70
    bar_height = row_pitch * 0.32
    y_pos = [i * row_pitch for i in range(n)]

    baseline_p1 = next(s["pass_at_1"] for s in skills if s["is_baseline"])
    x_max = 124.0  # ample right margin for tip labels

    for gx in (0, 20, 40, 60, 80, 100):
        ax.axvline(gx, color=COLOR_GRID, linewidth=0.9, zorder=0)

    ax.axvline(
        baseline_p1,
        color=COLOR_BASELINE_LINE,
        linestyle=(0, (3.5, 2.5)),
        linewidth=1.1,
        zorder=1,
        alpha=0.95,
    )
    # "baseline" sits clearly below % ticks, above first bar
    ax.text(
        baseline_p1,
        y_pos[0] - row_pitch * 0.42,
        "baseline",
        ha="center",
        va="bottom",
        fontsize=10,
        color=COLOR_MUTED,
        clip_on=False,
        zorder=6,
    )

    for i, s in enumerate(skills):
        y = y_pos[i]
        p1 = s["pass_at_1"]
        is_top = i == 0 and not s["is_baseline"]
        c_pass2, c_unst = _row_colors(s, is_top=is_top)
        if i == 0 and s["is_baseline"]:
            c_pass2, c_unst = BASE_PASS2, BASE_UNSTABLE

        if has_pass2:
            p2 = float(s["pass_squared"])
            unstable = p1 - p2
            ax.barh(
                y,
                p2,
                height=bar_height,
                left=0,
                color=c_pass2,
                edgecolor="none",
                zorder=3,
            )
            if unstable > 0:
                ax.barh(
                    y,
                    unstable,
                    height=bar_height,
                    left=p2,
                    color=c_unst,
                    edgecolor="none",
                    zorder=3,
                )
        else:
            ax.barh(
                y,
                p1,
                height=bar_height,
                left=0,
                color=c_pass2,
                edgecolor="none",
                zorder=3,
            )

        # Tip: more gap after bar, then % , then uplift
        x_tip = p1 + 2.8
        t_pass = ax.text(
            x_tip,
            y,
            f"{p1:.1f}%",
            va="center",
            ha="left",
            fontsize=12,
            fontweight="bold" if (i == 0 and not s["is_baseline"]) else "normal",
            color=COLOR_TEXT,
            zorder=5,
            clip_on=False,
        )
        if not s["is_baseline"]:
            fig.canvas.draw()
            bb = t_pass.get_window_extent(renderer=fig.canvas.get_renderer())
            x_after, _ = ax.transData.inverted().transform((bb.x1, bb.y0))
            u = s["uplift_pp"]
            sign = "+" if u > 0 else ""
            uplift_str = f"{sign}{u:.1f}"
            if u > 0:
                uplift_color = COLOR_UPLIFT_POS
            elif u < 0:
                uplift_color = COLOR_UPLIFT_NEG
            else:
                uplift_color = COLOR_MUTED
            ax.text(
                x_after + 2.2,
                y,
                uplift_str,
                va="center",
                ha="left",
                fontsize=11,
                fontweight="normal",
                color=uplift_color,
                zorder=5,
                clip_on=False,
            )

    # Y labels: drop "Skill"
    y_labels = [_display_name(s["name"]) for s in skills]
    y_weights = []
    for i, s in enumerate(skills):
        if i == 0 and not s["is_baseline"]:
            y_weights.append("bold")
        else:
            y_weights.append("normal")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels, fontsize=13, color=COLOR_LABEL)
    for tick_label, weight, i in zip(ax.get_yticklabels(), y_weights, range(n)):
        tick_label.set_fontweight(weight)
        if i == 0 and not skills[0]["is_baseline"]:
            tick_label.set_color(COLOR_TEXT)
        elif skills[i]["is_baseline"]:
            tick_label.set_color(COLOR_MUTED)
        else:
            tick_label.set_color(COLOR_LABEL)

    ax.invert_yaxis()
    y_top = y_pos[0] - row_pitch * 0.85  # room for % ticks + baseline label
    y_bot = y_pos[-1] + row_pitch * 0.60
    ax.set_ylim(y_bot, y_top)
    ax.set_xlim(0, x_max)

    ax.xaxis.tick_top()
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xticklabels(
        ["0%", "20%", "40%", "60%", "80%", "100%"],
        fontsize=10,
        color=COLOR_MUTED,
    )
    ax.tick_params(axis="x", length=0, pad=10, colors=COLOR_MUTED)
    ax.tick_params(axis="y", length=0, pad=18)  # more gap: names → bars

    for spine in ax.spines.values():
        spine.set_visible(False)

    # Title + subtitle with optional harness logo (Codex only; model is text-only)
    title = "Skill Effectiveness on SWE-Together"
    harness = meta.get("harness", "Codex CLI")
    model = meta.get("model", "GPT-6 Luna")
    benchmark = meta.get("benchmark", "SWE-Together")
    k = meta.get("k", 2)

    # Slightly smaller plot area → more canvas breathing room
    left, right = 0.20, 0.86
    top, bottom = 0.68, 0.11
    plt.subplots_adjust(left=left, right=right, top=top, bottom=bottom)

    fig.text(
        left,
        0.960,
        title,
        ha="left",
        va="top",
        fontsize=22,
        fontweight="bold",
        color=COLOR_TEXT,
    )

    # Subtitle row: [logo] Codex CLI · GPT-6 Luna · SWE-Together · k=2
    # More gap under title
    sub_y = 0.888
    sub_fontsize = 12
    logo_h = 0.018  # ~ subtitle cap height in figure fraction
    cursor_x = left
    script_dir = Path(__file__).resolve().parent
    harness_logo = _resolve_logo_path(meta.get("harness_logo"), script_dir)
    # model_logo intentionally ignored even if set — no second OpenAI mark

    if harness_logo is not None:
        try:
            cursor_x = _add_svg_logo_fig(
                fig,
                harness_logo,
                cursor_x,
                sub_y,
                logo_h,
                color=COLOR_MUTED,
            )
            cursor_x += 0.006  # gap logo → text
        except Exception as exc:
            print(f"Warning: could not draw harness logo ({exc})", file=sys.stderr)

    # Build subtitle as sequential text pieces so logo sits left of harness name
    pieces = [
        (harness, COLOR_MUTED),
        (" · ", COLOR_MUTED),
        (model, COLOR_MUTED),
        (" · ", COLOR_MUTED),
        (f"{benchmark} · k={k}", COLOR_MUTED),
    ]
    # Draw with fig.text; advance x using renderer widths
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for text, color in pieces:
        t_artist = fig.text(
            cursor_x,
            sub_y,
            text,
            ha="left",
            va="center",
            fontsize=sub_fontsize,
            color=color,
        )
        fig.canvas.draw()
        bb = t_artist.get_window_extent(renderer=renderer)
        # Convert pixel right edge to figure fraction
        inv = fig.transFigure.inverted()
        x1, _ = inv.transform((bb.x1, bb.y0))
        cursor_x = x1

    # Legend: ONLY Pass² and Pass@1 − Pass² (no baseline line)
    if has_pass2:
        legend_handles = [
            Patch(facecolor=ACCENT_PASS2, edgecolor="none", label="Pass²"),
            Patch(facecolor=ACCENT_UNSTABLE, edgecolor="none", label="Pass@1 − Pass²"),
        ]
    else:
        legend_handles = [
            Patch(facecolor=ACCENT_PASS2, edgecolor="none", label="Pass@1"),
        ]

    fig.legend(
        handles=legend_handles,
        loc="upper left",
        bbox_to_anchor=(left, 0.840),  # clear of subtitle + above plot ticks
        ncol=2,
        frameon=False,
        fontsize=11,
        handlelength=1.5,
        handleheight=0.95,
        columnspacing=1.6,
        labelcolor=COLOR_MUTED,
    )

    # No bottom harness footer — subtitle carries that info
    fig.text(
        0.96,
        0.04,
        "Illustrative Data — Not Actual Benchmark Results",
        ha="right",
        va="center",
        fontsize=8,
        color=COLOR_WATERMARK,
        style="italic",
    )

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=dpi, facecolor=COLOR_BG, edgecolor="none")
    fig.savefig(out_svg, facecolor=COLOR_BG, edgecolor="none")
    plt.close(fig)

    w, h = _png_size(out_png)
    if w < 3200 or h < 1800:
        print(f"Warning: PNG is {w}×{h}, expected ≥3200×1800", file=sys.stderr)
    else:
        print(f"PNG OK: {w}×{h}")


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Draw Skill Effectiveness leaderboard (community style)"
    )
    parser.add_argument(
        "data",
        nargs="?",
        default=str(script_dir / "data.json"),
        help="Path to JSON results (default: data.json next to this script)",
    )
    parser.add_argument(
        "--out-dir",
        default=str(script_dir),
        help="Output directory for PNG/SVG (default: script directory)",
    )
    args = parser.parse_args()

    data_path = Path(args.data).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_png = out_dir / "skill_effectiveness.png"
    out_svg = out_dir / "skill_effectiveness.svg"

    data = load_data(data_path)
    skills, meta, has_pass2 = validate_and_prepare(data)
    draw(skills, meta, has_pass2, out_png, out_svg)

    print(f"Wrote {out_png}")
    print(f"Wrote {out_svg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
