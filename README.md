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

**Important:** Open `paper/agents-unite-paper.pdf` in a desktop PDF viewer (Preview, Evince, Adobe Reader) before you push. Cursor's built-in PDF preview sometimes shows *"unable to render code block"* for TikZ/pgfplots figures even when the PDF is valid. If the chart and tables look correct externally, the PDF is fine to publish.

Manual checklist:

1. Figure 1 (cost bar chart) renders with all five bars labeled
2. Tables and citations show no `??` placeholders
3. Code/command snippet in Section 5 is readable inside its box

Only push after `make verify` passes **and** the external PDF viewer looks correct.

## Clean

```bash
make clean
```
