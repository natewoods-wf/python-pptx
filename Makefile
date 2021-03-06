PYTHON      = $(shell test -x bin/python && echo bin/python || \
                      echo `which python`)
BEHAVE      = behave
SETUP       = $(PYTHON) ./setup.py

.PHONY: accept clean coverage readme register sdist upload

help:
	@echo "Please use \`make <target>' where <target> is one or more of"
	@echo "  accept    run acceptance tests using behave"
	@echo "  clean     delete intermediate work product and start fresh"
	@echo "  coverage  run nosetests with coverage"
	@echo "  readme    update README.html from README.rst"
	@echo "  register  update metadata (README.rst) on PyPI"
	@echo "  test      run tests using setup.py"
	@echo "  sdist     generate a source distribution into dist/"
	@echo "  upload    upload distribution tarball to PyPI"

accept:
	$(BEHAVE) --stop

clean:
	find . -type f -name \*.pyc -exec rm {} \;
	find . -type f -name .DS_Store -exec rm {} \;
	rm -rf dist *.egg-info .coverage

coverage:
	py.test --cov-report term-missing --cov=pptx --cov=tests

readme:
	rst2html README.rst >README.html
	open README.html

register:
	$(SETUP) register

sdist:
	$(SETUP) sdist

test:
	$(SETUP) test

upload:
	$(SETUP) sdist upload
