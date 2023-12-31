test:
	poetry run python -m pytest

watch-test:
	find py_loans tests -name "*.py" | entr make test

test-coverage:
	poetry run coverage run -m pytest
	poetry run coverage combine
	poetry run coverage report -m

type-check:
	poetry run python -m mypy py_loans tests

watch-type-check:
	find py_loans tests -name "*.py" | entr make type-check

fmt:
	poetry run black --preview py_loans tests
	poetry run flake8 py_loans tests

fmt-check:
	poetry run black --preview --check py_loans tests
	poetry run flake8 py_loans tests

docs-build:
	poetry run mkdocs build

watch-docs-build:
	poetry run mkdocs serve -a localhost:8005

check: fmt-check type-check docs-build
