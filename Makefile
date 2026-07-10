.PHONY: all paper clean research verify

all: paper

paper:
	cd paper && pdflatex -interaction=nonstopmode agents-unite-paper.tex
	cd paper && bibtex agents-unite-paper
	cd paper && pdflatex -interaction=nonstopmode agents-unite-paper.tex
	cd paper && pdflatex -interaction=nonstopmode agents-unite-paper.tex

verify:
	./scripts/verify-pdf.sh

clean:
	rm -f paper/*.aux paper/*.bbl paper/*.blg paper/*.log paper/*.out paper/*.pdf

research:
	@echo "Research brief: research/RESEARCH.md"
