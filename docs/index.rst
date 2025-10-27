:layout: landing
:description: Polyfactory is a simple and powerful mock data generation library.

.. container::
    :name: home-head

    .. container::

        .. raw:: html

            <div class="title-with-logo">
               <div class="brand-text">Polyfactory</div>
            </div>

        .. container:: badges
           :name: badges

            .. image:: https://img.shields.io/github/actions/workflow/status/litestar-org/polyfactory/publish.yml?labelColor=202235&logo=github&logoColor=edb641
               :alt: GitHub Actions Latest Release Workflow Status

            .. image:: https://img.shields.io/github/actions/workflow/status/litestar-org/polyfactory/ci.yml?labelColor=202235&logo=github&logoColor=edb641
               :alt: GitHub Actions CI Workflow Status

            .. image:: https://img.shields.io/github/actions/workflow/status/litestar-org/polyfactory/docs.yml?labelColor=202235&logo=github&logoColor=edb641
               :alt: GitHub Actions Docs Build Workflow Status

            .. image:: https://img.shields.io/codecov/c/github/litestar-org/polyfactory?labelColor=202235&logo=codecov&logoColor=edb641
               :alt: Coverage

            .. image:: https://img.shields.io/pypi/v/polyfactory?labelColor=202235&color=edb641&logo=python&logoColor=edb641
               :alt: PyPI Version

            .. image:: https://img.shields.io/github/all-contributors/litestar-org/polyfactory?labelColor=202235&color=edb641&logoColor=edb641
               :alt: Contributor Count

            .. image:: https://img.shields.io/pypi/dm/polyfactory?logo=python&label=polyfactory%20downloads&labelColor=202235&color=edb641&logoColor=edb641
               :alt: PyPI Downloads

            .. image:: https://img.shields.io/pypi/pyversions/polyfactory?labelColor=202235&color=edb641&logo=python&logoColor=edb641
               :alt: Supported Python Versions

.. rst-class:: lead

   Polyfactory is a simple and powerful mock data generation library, based around type
   hints and supporting :doc:`dataclasses <python:library/dataclasses>`, :class:`TypedDicts <typing.TypedDict>`,
   Pydantic models, :class:`msgspec Struct's <msgspec.Struct>` and more.

.. container:: buttons wrap

   .. raw:: html

      <a href="getting-started.html" class="btn-no-wrap">Get Started</a>
      <a href="usage/index.html" class="btn-no-wrap">Usage Docs</a>
      <a href="reference/index.html" class="btn-no-wrap">API Docs</a>
      <a href="https://blog.litestar.dev" class="btn-no-wrap">Blog</a>

.. grid:: 1 1 2 2
    :padding: 0
    :gutter: 2

    .. grid-item-card:: :octicon:`versions` Changelog
      :link: changelog
      :link-type: doc

      The latest updates and enhancements to Polyfactory

    .. grid-item-card:: :octicon:`comment-discussion` Discussions
      :link: https://github.com/litestar-org/polyfactory/discussions

      Join discussions, pose questions, or share insights.

    .. grid-item-card:: :octicon:`issue-opened` Issues
      :link: https://github.com/litestar-org/polyfactory/issues

      Report issues or suggest new features.

    .. grid-item-card:: :octicon:`beaker` Contributing
      :link: contribution-guide
      :link-type: doc

      Contribute to Litestar's growth with code, docs, and more.

.. toctree::
    :titlesonly:
    :caption: Documentation
    :hidden:

    getting-started
    usage/index
    migration_guide/index
    reference/index

.. toctree::
    :titlesonly:
    :caption: Contributing
    :hidden:

    changelog
    contribution-guide
    Available Issues <https://github.com/search?q=user%3Alitestar-org+state%3Aopen+label%3A%22good+first+issue%22+++no%3Aassignee+repo%3A%22polyfactory%22&type=issues>
    Code of Conduct <https://github.com/litestar-org/.github?tab=coc-ov-file#readme>
