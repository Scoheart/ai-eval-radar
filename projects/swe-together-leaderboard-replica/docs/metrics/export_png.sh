#!/usr/bin/env bash
# Export metrics formula charts to PNG via Chrome headless.
# Usage: ./export_png.sh [en|zh|both]
set -euo pipefail
cd "$(dirname "$0")"
LANGS="${1:-both}"
export_one() {
  local lang="$1"
  local html="metrics_${lang}.html"
  local out="swe_together_metrics_${lang}.png"
  google-chrome --headless --disable-gpu --no-sandbox \
    --window-size=1100,900 \
    --screenshot="$out" \
    "file://$(pwd)/$html"
  echo "Wrote $(pwd)/$out"
}
case "$LANGS" in
  en) export_one en ;;
  zh) export_one zh ;;
  both) export_one en; export_one zh ;;
  *) echo "Usage: $0 [en|zh|both]" >&2; exit 1 ;;
esac
