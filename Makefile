.PHONY: all paper clean research verify zip arxiv

all: paper zip

paper:
	cd paper && pdflatex -interaction=nonstopmode agents-unite-paper.tex
	cd paper && bibtex agents-unite-paper
	cd paper && pdflatex -interaction=nonstopmode agents-unite-paper.tex
	cd paper && pdflatex -interaction=nonstopmode agents-unite-paper.tex

verify:
	./scripts/verify-pdf.sh

zip: paper/agents-unite-paper.tex paper/agents-unite-paper.pdf paper/references.bib
	rm -f paper.zip
	zip -j paper.zip paper/agents-unite-paper.tex paper/agents-unite-paper.pdf paper/references.bib

arxiv: paper/agents-unite-paper.tex paper/references.bib paper/agents-unite-paper.bbl
	rm -f arxiv-submission.zip
	zip -j arxiv-submission.zip paper/agents-unite-paper.tex paper/references.bib paper/agents-unite-paper.bbl

clean:
	rm -f paper/*.aux paper/*.bbl paper/*.blg paper/*.log paper/*.out paper/*.pdf paper.zip arxiv-submission.zip

research:
	@echo "Research brief: research/RESEARCH.md"
