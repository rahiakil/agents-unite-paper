# Agents Unite Paper

Six-page research paper for [Agents Unite](https://github.com/rahiakil/agents-unite) — a Git-native proof-of-trust ledger for distributed financial intelligence.

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

## Clean

```bash
make clean
```
