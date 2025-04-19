all: analysis.pdf

analysis.pdf: $(shell ls *.tex)
	pdflatex season-analysis.tex

clean:
	$(RM) *.dvi *.aux *.out *.log *.blg *.bbl *.mtc* *~ *.maf _region_.tex
	rubber --clean

vclean mrproper: clean
	$(RM) *.toc *.lof *.lot *.pdf *.ice *.gz
