# Makefile for Sphinx documentation
#
CHECK=\033[32m✔\033[39m
HR=\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
BUILD_DIR     = build
COVERAGE_FILES = .coverage htmlcov/ profiles/

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILD_DIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) docs

# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) docs


main: coverage dirhtml

coverage:
	-coverage run --source=clever tests/manage.py test -v 2
	coverage html
	@echo "clever and coverage:                                  ${CHECK} Done"

test:
	python tests/manage.py test -v 2
	@echo "Test                                                  ${CHECK} Done"

install:
	pip install -r requirements.pip
	@echo "Installation                                          ${CHECK} Done"

clean:
	-rm -rf $(BUILD_DIR)/
	-rm -rf $(COVERAGE_FILES)

html:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILD_DIR)/html
	@echo
	@echo "The HTML pages are in $(BUILD_DIR)/html."
	@echo "Documentation updated                                 ${CHECK} Done"

dirhtml:
	$(SPHINXBUILD) -b dirhtml $(ALLSPHINXOPTS) $(BUILD_DIR)/dirhtml
	@echo
	@echo "The HTML pages are in $(BUILD_DIR)/dirhtml."
	@echo "Documentation updated                                 ${CHECK} Done"

singlehtml:
	$(SPHINXBUILD) -b singlehtml $(ALLSPHINXOPTS) $(BUILD_DIR)/singlehtml
	@echo
	@echo "The HTML page is in $(BUILD_DIR)/singlehtml."
	@echo "Documentation updated                                 ${CHECK} Done"

rundoc: dirhtml
	@echo
	@echo "Start simple http server"

	gnome-open http://localhost:9000
	cd $(BUILD_DIR)/dirhtml/ && python -m SimpleHTTPServer 9000
