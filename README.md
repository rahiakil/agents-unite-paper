# Agents Unite Paper

Six-page research paper for [Agents Unite](https://github.com/rahiakil/agents-unite), a Git-native proof-of-trust ledger for distributed financial intelligence.

## Contents

| Path | Description |
|------|-------------|
| `paper/agents-unite-paper.tex` | LaTeX source |
| `paper/agents-unite-paper.pdf` | Compiled paper |
| `paper/references.bib` | Bibliography |
| `poster/agents-unite-poster.tex` | Conference poster source |
| `poster/agents-unite-poster.pdf` | Compiled 36×48 in poster |
| `submission/ci2026-poster.tex` | ACM CI 2026 poster writeup source |
| `submission/ci2026-poster.pdf` | ACM CI 2026 poster writeup (submit to EasyChair) |
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

## Conference poster

Build the 36×48 inch portrait poster:

```bash
make poster
```

Output: `poster/agents-unite-poster.pdf`

The poster summarizes the problem, architecture, economics, leader-election flow, and future directions for conference submission. To change size (for example A0), edit `paperwidth` / `paperheight` in `poster/agents-unite-poster.tex`.

## ACM CI 2026 poster submission

Build the 2-page ACM-formatted poster writeup for [ACM Collective Intelligence 2026 Posters & Demos](https://ci.acm.org/2026/posters-demos.html):

```bash
make ci-poster
```

Output: `submission/ci2026-poster.pdf`

Requirements met:
- ACM `acmart` manuscript format
- Non-anonymous (author included)
- Main body under 2 pages; references may extend beyond
- Deadline: July 16, 2026 (11:59 pm AoE)
- Submit via EasyChair; select **CI** topic affiliation

## Paper zip

Always refresh the submission zip after paper changes:

```bash
make zip
```

Output: `paper.zip` (tex + pdf + bib at repo root). Cursor is configured (`.cursor/rules/paper-zip.mdc`) to recreate this zip whenever the paper is edited, rebuilt, committed, or pushed.

## arXiv submission

Create the source archive uploaded to arXiv:

```bash
make arxiv
```

Output: `arxiv-submission.zip` and `arxiv-submission.tar.gz`, containing the LaTeX source, bibliography database, generated `.bbl` file, and a `00README.XXX` metadata file. arXiv generally prefers the `.tar.gz`. The paper identifies Parag (RIG AI, `parag@rigai.co`) as its author.

Before uploading, verify that the source compiles cleanly with pdflatex and that the generated `.bbl` is present.

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
