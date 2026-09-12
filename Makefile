.PHONY: check test lint fix

check:
	python manage.py check
	python manage.py makemigrations --check --dry-run

test:
	coverage run -m pytest
	coverage report

lint:
	ruff check core/

fix:
	ruff check core/ --fix
	autoflake --remove-all-unused-imports --in-place --recursive core/
