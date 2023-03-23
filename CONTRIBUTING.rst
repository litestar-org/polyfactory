Contribution Guide
==================

Setting up the environment
--------------------------

1. Install `poetry <https://python-poetry.org/>`_
2. Run ``poetry install`` to create a `virtual environment <https://docs.python.org/3/tutorial/venv.html>`_ and install
   the dependencies
3. If you're working on the documentation and need to build it locally, install the extra dependencies with ``poetry install --with docs``
4. Install `pre-commit <https://pre-commit.com/>`_
5. Run ``pre-commit install`` to install pre-commit hooks

Code contributions
------------------

Workflow
++++++++

1. `Fork <https://github.com/starlite-api/polyfactory/fork>`_ the upstream repository and clone the fork locally.
2. Install `poetry <https://python-poetry.org/>`_, and install the project's dependencies with ``poetry install``.
3. Install `pre-commit <https://pre-commit.com/>`_ by running ``pre-commit install``.
4. Make whatever changes and additions you wish and commit these - please try to keep your commit history clean.
   1. .. note:: 100% tests are mandatory.
5. Once you are ready, add a PR in the main repo.
6. Create a pull request to the main repository with an explanation of your changes.

.. note:: The test suite requires having an instance of MongoDB available. You can launch one using the root level
docker-compose config with ``docker-compose up --detach``, or by any other means.

Project documentation
---------------------

The documentation is located in the ``/docs`` directory and is built with `ReST <https://docutils.sourceforge.io/rst.html>`_
and `Sphinx <https://www.sphinx-doc.org/en/master/>`_. If you're unfamiliar with any of those,
`ReStructuredText primer <https://www.sphinx-doc.org/en/master/lib/usage/restructuredtext/basics.html>`_ and
`Sphinx quickstart <https://www.sphinx-doc.org/en/master/lib/usage/quickstart.html>`_ are recommended reads.

Docs theme and appearance
+++++++++++++++++++++++++

We welcome contributions that enhance / improve the appearance and usability of the docs. We use a custom theme that
inherits the `PyData Sphinx Theme Furo <https://pydata-sphinx-theme.readthedocs.io/en/latest/>`_ theme, which comes
with a lot of options out of the box. If you wish to contribute to the docs style / setup, or static site generation,
you should consult the theme docs as a first step.

Running the docs locally
++++++++++++++++++++++++

To run or build the docs locally, you need to first install the required dependencies:

``poetry install --with docs``

Then you can serve the documentation with ``make docs-serve``, or build them with ``make docs``

Writing and editing docs
++++++++++++++++++++++++

We welcome contributions that enhance / improve the content of the docs. Feel free to add examples, clarify text,
restructure the docs etc., but make sure to follow these guidelines:

- Write text in idiomatic english, using simple language
- Keep examples simple and self contained
- Provide links where applicable
- Use `intersphinx <https://www.sphinx-doc.org/en/master/lib/usage/extensions/intersphinx.html>`_ wherever possible when
  referencing external libraries
- Provide diagrams using `mermaidjs <https://mermaid.js.org/>`_ where applicable and possible


Creating a new release
----------------------

1. Update changelog.md
2. Increment the version in `pyproject.toml <pyproject.toml>`_
3. Commit and push.
4. In GitHub go to the `releases tab <https://github.com/starlite-api/polyfactory/releases>`_
5. Pick "`Draft a new release <https://github.com/starlite-api/polyfactory/releases/new>`_"
6. Give it a title and a tag, both ``vX.X.X``
7. Fill in the release description, you can let GitHub do it for you and then edit as needed.
8. Publish the release.
9. Look under the action pane and make sure the release action runs correctly
