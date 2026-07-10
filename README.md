# Agents Unite Paper

Six-page research paper for [Agents Unite](https://github.com/rahiakil/agents-unite), a Git-native proof-of-trust ledger for distributed financial intelligence.

## Contents

| Path | Description |
|------|-------------|
| `paper/agents-unite-paper.tex` | LaTeX source |
| `paper/agents-unite-paper.pdf` | Compiled paper |
| `paper/references.bib` | Bibliography |
| `research/RESEARCH.md` | Research brief and citations |

## Requirements

- TeX Live (pdflatex, bibtex)
- Make

On Debian/Ubuntu/WSL:

```bash
sudo apt-get install -y texlive-latex-base texlive-latex-extra \
  texlive-fonts-recommended texlive-bibtex-extra make
```

## Build

```bash
make paper
```

Output: `paper/agents-unite-paper.pdf`

## Verify before pushing

Always run the verification script after editing the LaTeX source:

```bash
make verify
```

This rebuilds the PDF and checks for LaTeX errors, page count, and file size.

**Important:** Cursor's built-in PDF tab often shows *"Unable to render code block"* because it tries to text-parse binary PDFs. Use one of these instead:

1. **Right-click** `paper/agents-unite-paper.pdf` → **Reveal in File Explorer** → open with Preview/Adobe/Evince
2. **Terminal:** `xdg-open paper/agents-unite-paper.pdf` (Linux) or `open paper/agents-unite-paper.pdf` (macOS)
3. This repo sets `.vscode/settings.json` to prefer the system PDF handler over Cursor's inline viewer

The PDF itself is valid if `make verify` passes and an external viewer shows 6 pages with Figure 1 (cost chart) and all tables.

Manual checklist:

1. Figure 1 (cost bar chart) renders with all five bars labeled
2. Tables and citations show no `??` placeholders
3. Code/command snippet in Section 5 is readable inside its box

Only push after `make verify` passes **and** the external PDF viewer looks correct.

## Clean

```bash
make clean
```
