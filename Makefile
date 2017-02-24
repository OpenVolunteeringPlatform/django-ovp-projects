test:
	@python ovp_projects/tests/runtests.py

lint:
	@pylint ovp_projects

clean-pycache:
	@rm -r **/__pycache__

clean: clean-pycache

.PHONY: clean


