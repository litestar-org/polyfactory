.PHONY: docs

install:
	poetry install --extras full --with docs --no-ansi --sync
	pre-commit install
.PHONY: install

docs-clean:
	rm -rf docs/_build

docs-serve: docs-clean
	poetry run sphinx-autobuild docs docs/_build/ -j auto --watch polyfactory

docs: docs-clean
	poetry run sphinx-build -M html docs docs/_build/ -a -j auto -W --keep-going

test:
	poetry run pytest tests docs/examples

coverage:
	poetry run pytest tests --cov=polyfactory
	poetry run coverage html

format:
	poetry run pre-commit run --all-files
