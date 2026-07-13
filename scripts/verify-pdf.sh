#!/usr/bin/env bash
# Verify the compiled PDF is healthy before committing or pushing.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PDF="$ROOT/paper/agents-unite-paper.pdf"
LOG="$ROOT/paper/agents-unite-paper.log"
TEX="$ROOT/paper/agents-unite-paper.tex"

cd "$ROOT"

echo "==> Building paper..."
make paper

if [[ ! -f "$PDF" ]]; then
  echo "FAIL: PDF not found at $PDF"
  exit 1
fi

if grep -E '^!' "$LOG" >/dev/null 2>&1; then
  echo "FAIL: LaTeX errors found in $LOG"
  grep -E '^!' "$LOG" || true
  exit 1
fi

if grep -i 'fatal error' "$LOG" >/dev/null 2>&1; then
  echo "FAIL: Fatal LaTeX error in $LOG"
  exit 1
fi

PAGES="$(pdfinfo "$PDF" 2>/dev/null | awk '/Pages:/ {print $2}')"
if [[ -z "${PAGES:-}" ]]; then
  echo "WARN: pdfinfo not installed; skipping page-count check"
else
  if [[ "$PAGES" -lt 5 ]]; then
    echo "FAIL: Expected at least 5 pages, got $PAGES"
    exit 1
  fi
  echo "OK: PDF has $PAGES pages"
fi

SIZE="$(wc -c < "$PDF")"
if [[ "$SIZE" -lt 50000 ]]; then
  echo "FAIL: PDF looks too small ($SIZE bytes); build may be corrupt"
  exit 1
fi
echo "OK: PDF size is $SIZE bytes"

if command -v pdffonts >/dev/null 2>&1; then
  echo "OK: pdffonts available (open PDF externally to confirm charts render)"
fi

echo ""
echo "Manual check required before push:"
echo "  1. Do NOT rely on Cursor's inline PDF tab (shows 'Unable to render code block')."
echo "  2. Open externally: xdg-open paper/agents-unite-paper.pdf"
echo "  3. Confirm all figures (cost, coverage, collisions, consensus) and tables render."
echo "  4. Confirm no missing citations (??) in the text."
echo ""
echo "PASS: Automated PDF checks succeeded."
