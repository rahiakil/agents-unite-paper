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

arxiv: paper/agents-unite-paper.tex paper/references.bib paper/agents-unite-paper.bbl paper/00README.XXX
	rm -f arxiv-submission.zip arxiv-submission.tar.gz
	zip -j arxiv-submission.zip paper/agents-unite-paper.tex paper/references.bib paper/agents-unite-paper.bbl paper/00README.XXX
	tar -czf arxiv-submission.tar.gz -C paper agents-unite-paper.tex references.bib agents-unite-paper.bbl 00README.XXX

clean:
	rm -f paper/*.aux paper/*.bbl paper/*.blg paper/*.log paper/*.out paper/*.pdf paper.zip arxiv-submission.zip

research:
	@echo "Research brief: research/RESEARCH.md"
