# SWE-Together metrics formula charts

Self-contained KaTeX HTML cards explaining the paper's metric definitions (`pass@1`, `SSR`, `pass²`, `Mean judge`, `U-Corr`, `Tok./task`, `Min./task`). Metric names stay English in both language packs; only surrounding annotations differ.

| File | Language |
|------|----------|
| `metrics_en.html` | English chrome |
| `metrics_zh.html` | Chinese chrome |
| `export_png.sh` | Chrome headless PNG export |

## Open / serve

```bash
# From repo root — open the file directly, or:
python3 -m http.server 8000
# then visit http://localhost:8000/docs/metrics/metrics_en.html
#          or http://localhost:8000/docs/metrics/metrics_zh.html
```

Needs network once for the KaTeX CDN (`cdn.jsdelivr.net`).

## Screenshot (Chrome headless)

```bash
cd docs/metrics
./export_png.sh both
# or:
google-chrome --headless --disable-gpu --no-sandbox \
  --window-size=1100,900 \
  --screenshot=swe_together_metrics_en.png \
  "file://$(pwd)/metrics_en.html"
```

Do not edit the HTML metric formulas unless aligning with a paper revision.
