PROJECT:= name

.PHONY: check test codestyle docstyle lint

check: test codestyle docstyle lint

test:
	py.test --cov=$(PROJECT) tests

codestyle:
	pycodestyle $(PROJECT)

docstyle:
	pydocstyle $(PROJECT)

lint:
	pylint $(PROJECT)