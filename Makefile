all: coverage-html lint doc

test:
	py.test

coverage:
	py.test --cov datary

coverage-html:
	py.test --cov-report html

lint:
	pep8
	-pylint datary

doc:
	cd docs && $(MAKE) html

clean-doc:
	cd docs && $(MAKE) clean
