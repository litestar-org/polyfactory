Contributing
==================

Setting up the environment
--------------------------

1. Install `Pizza Delivery Man <https://pdm.fming.dev/latest/>`_
2. Run ``pdm install -G:all`` to create a `virtual environment <https://docs.python.org/3/tutorial/venv.html>`_ and install
   the dependencies
3. If you're working on the documentation and need to build it locally, install the extra dependencies with ``pdm install -G:docs``
4. Install `pre-commit <https://pre-commit.com/>`_
5. Run ``pre-commit install`` to install pre-commit hooks

Code contributions
------------------

Workflow
++++++++

1. `Fork <https://github.com/litestar-org/polyfactory/fork>`_ the `Polyfactory repository <https://github.com/litestar-org/polyfactory>`_
2. Clone your fork locally with git
3. `Set up the environment <#setting-up-the-environment>`_
4. Make your changes
5. (Optional) Run ``pre-commit run --all-files`` to run linters and formatters. This step is optional and will be executed
   automatically by git before you make a commit, but you may want to run it manually in order to apply fixes
6. Commit your changes to git
7. Push the changes to your fork
8. Open a `pull request <https://docs.github.com/en/pull-requests>`_. Give the pull request a descriptive title
   indicating what it changes. If it has a corresponding open issue.
   For example a pull request that fixes issue ``bug: Increased stack size making it impossible to find needle``
   could be titled ``fix: Make needles easier to find by applying fire to haystack``

.. tip:: Pull requests and commits all need to follow the
    `Conventional Commit format <https://www.conventionalcommits.org>`_

Project documentation
---------------------

The documentation is located in the ``/docs`` directory and is built with `ReST <https://docutils.sourceforge.io/rst.html>`_
and `Sphinx <https://www.sphinx-doc.org/en/master/>`_. If you're unfamiliar with any of those,
`ReStructuredText primer <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_ and
`Sphinx quickstart <https://www.sphinx-doc.org/en/master/usage/quickstart.html>`_ are recommended reads.

Docs theme and appearance
+++++++++++++++++++++++++

We welcome contributions that enhance / improve the appearance and usability of the docs. We use a custom theme that
inherits the `Shibuya theme <https://shibuya.lepture.com/>`_, which comes with a lot of options out of the box.
If you wish to contribute to the docs style / setup, or static site generation, you should consult the theme docs
as a first step.

Running the docs locally
++++++++++++++++++++++++

To run or build the docs locally, you need to first install the required dependencies:

.. code-block:: console
    :caption: Installing the docs dependencies

    pdm install -G:docs

Then you can serve the documentation with ``make docs-serve``, or build them with ``make docs``

Writing and editing docs
++++++++++++++++++++++++

We welcome contributions that enhance / improve the content of the docs. Feel free to add examples, clarify text,
restructure the docs etc., but make sure to follow these guidelines:

- Write text in idiomatic english, using simple language
- Keep examples simple and self contained
- Provide links where applicable
- Use `intersphinx <https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html>`_ wherever possible when
  referencing external libraries
- Provide diagrams using `mermaidjs <https://mermaid.js.org/>`_ where applicable and possible

Creating a new release
----------------------

1. Increment the version in ``pyproject.toml``
    .. note:: The version should follow `semantic versioning <https://semver.org/>`_ and `PEP 440 <https://www.python.org/dev/peps/pep-0440/>`_.
2. Commit and push.
3. In GitHub go to the `releases tab <https://github.com/litestar-org/polyfactory/releases>`_
4. Pick "`Draft a new release <https://github.com/litestar-org/polyfactory/releases/new>`_"
5. Give it a title and a tag, both ``vX.X.X``
6. Fill in the release description. You can let GitHub do it for you and then edit as needed.
7. Publish the release.
8. Go to `Actions <https://github.com/litestar-org/polyfactory/actions>`_ and approve the workflow
9. Check that the workflow runs successfully
