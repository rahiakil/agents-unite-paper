#!/usr/bin/env bash
# Install LaTeX toolchain for building agents-unite-paper (Debian/Ubuntu/WSL).
set -euo pipefail

if ! command -v apt-get >/dev/null 2>&1; then
  echo "apt-get not found. Install TeX Live manually: https://www.tug.org/texlive/"
  exit 1
fi

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  texlive-latex-base \
  texlive-latex-extra \
  texlive-fonts-recommended \
  texlive-bibtex-extra \
  make

echo "Done. Run: make verify"
