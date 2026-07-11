.PHONY: all paper clean research verify zip

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

clean:
	rm -f paper/*.aux paper/*.bbl paper/*.blg paper/*.log paper/*.out paper/*.pdf paper.zip

research:
	@echo "Research brief: research/RESEARCH.md"
