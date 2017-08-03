all: coverage-html lint doc

test:
	py.test

coverage:
	py.test --cov datary

coverage-html:
	py.test --cov-report html

diagram:
	pyreverse -o png -p diagram datary --ignore test

diagram-all:
	pyreverse -o png -p diagram datary

lint:
	pep8
	pylint datary

doc:
	cd docs && $(MAKE) html

clean-doc:
	cd docs && $(MAKE) clean
