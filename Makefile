.PHONY: docs

docs-clean:
	rm -rf docs/_build

docs-serve:
	sphinx-autobuild docs docs/_build/ -j auto --watch polyfactory

docs: docs-clean
	sphinx-build -M html docs docs/_build/ -a -j auto -W --keep-going

test:
	pytest tests

coverage:
	pytest tests --cov=polyfactory
	coverage html
