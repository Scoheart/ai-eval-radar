#!/usr/bin/env python3
"""Local demo only: render harness or model leaderboard using same engine."""
import argparse
from pathlib import Path
import i18n_packs
import render_html as rh

def apply_axis(axis: str) -> str:
    if axis == "harness":
        i18n_packs.I18N["en"]["skill"] = "Harness"
        i18n_packs.I18N["zh"]["skill"] = "Harness"
        i18n_packs.I18N["en"]["title_lb"] = "Harness Effectiveness on SWE-Together"
        i18n_packs.I18N["zh"]["title_lb"] = "Harness Effectiveness on SWE-Together"
        i18n_packs.I18N["en"]["subtitle_lb"] = "GPT-6 Luna · No Skill · SWE-Together · k = {k} replicates"
        i18n_packs.I18N["zh"]["subtitle_lb"] = "GPT-6 Luna · No Skill · SWE-Together · k = {k} 次复现"
        return "harness_leaderboard"
    i18n_packs.I18N["en"]["skill"] = "Model"
    i18n_packs.I18N["zh"]["skill"] = "Model"
    i18n_packs.I18N["en"]["title_lb"] = "Model Effectiveness on SWE-Together"
    i18n_packs.I18N["zh"]["title_lb"] = "Model Effectiveness on SWE-Together"
    i18n_packs.I18N["en"]["subtitle_lb"] = "Codex CLI · No Skill · SWE-Together · k = {k} replicates"
    i18n_packs.I18N["zh"]["subtitle_lb"] = "Codex CLI · No Skill · SWE-Together · k = {k} 次复现"
    return "model_leaderboard"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--axis", choices=["harness", "model"], required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--both-langs", action="store_true")
    args = ap.parse_args()
    out_base = apply_axis(args.axis)
    data = rh.load_data(Path(args.data))
    langs = ["en", "zh"] if args.both_langs else ["en"]
    for lang in langs:
        html = rh.render_leaderboard(data, lang=lang)
        path = Path(f"{out_base}.{lang}.html" if args.both_langs else f"{out_base}.html")
        path.write_text(html, encoding="utf-8")
        print("Wrote", path)
        if args.both_langs and lang == "en":
            Path(f"{out_base}.html").write_text(html, encoding="utf-8")
            print("Wrote", f"{out_base}.html")

if __name__ == "__main__":
    main()
