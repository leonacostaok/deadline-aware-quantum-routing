.PHONY: test reproduce paper check

test:
	python3 -m unittest discover -s tests -v

reproduce:
	python3 scripts/reproduce.py

paper:
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error paper.tex

check: test
	python3 scripts/reproduce.py --check
	$(MAKE) paper
