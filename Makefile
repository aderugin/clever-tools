# Makefile for Sphinx documentation
#
CHECK=\033[32m✔\033[39m
HR=\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = build

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) docs

# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) docs


main: coverage dirhtml

coverage:
	coverage run --source=clever test/manage.py test -v 0
	coverage html
	@echo "clever and coverage:                                  ${CHECK} Done"

test:
	python tests/manage.py
	@echo "Test                                                  ${CHECK} Done"

install:
	pip install -r requirements.txt.txt
	npm install
	@echo "Installation                                          ${CHECK} Done"


clean:
	-rm -rf $(BUILDDIR)/*

html:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "The HTML pages are in $(BUILDDIR)/html."
	@echo "Documentation updated                                 ${CHECK} Done"

dirhtml:
	$(SPHINXBUILD) -b dirhtml $(ALLSPHINXOPTS) $(BUILDDIR)/dirhtml
	@echo
	@echo "The HTML pages are in $(BUILDDIR)/dirhtml."
	@echo "Documentation updated                                 ${CHECK} Done"

singlehtml:
	$(SPHINXBUILD) -b singlehtml $(ALLSPHINXOPTS) $(BUILDDIR)/singlehtml
	@echo
	@echo "The HTML page is in $(BUILDDIR)/singlehtml."
	@echo "Documentation updated                                 ${CHECK} Done"
