:orphan:

====================
Polyfactory Releases
====================

This document outlines the release structure, versioning, and stability guarantees for the Polyfactory library.

Version Numbering
-----------------

This library follows the `Semantic Versioning standard <https://semver.org/>`_, using the ``<major>.<minor>.<patch>``
schema:

**Major**
    Backwards incompatible changes have been made

**Minor**
    Functionality was added in a backwards compatible manner

**Patch**
    Bugfixes were applied in a backwards compatible manner

Pre-release Versions
++++++++++++++++++++

Before a new major release, we will make ``alpha``, ``beta``, and release candidate (``rc``) releases, numbered as
``<major>.<minor>.<patch><release_type><number>``. For example, ``2.0.0alpha1``, ``2.0.0beta1``, ``2.0.0rc1``.

- ``alpha``
    Early developer preview. Features may not be complete and breaking changes can occur.

- ``beta``
    More stable preview release. Feature complete, no major breaking changes expected.

- ``rc``
    Release candidate. Feature freeze, only bugfixes until final release.
    Suitable for testing migration to the upcoming major release.

Long-term Support Releases (LTS)
--------------------------------

Major releases are designated as LTS releases for the life of that major release series.
These releases will receive bugfixes for a guaranteed period of time as defined in
`Supported Versions <#supported-versions>`_.

Deprecation Policy
------------------

When a feature is going to be removed, a deprecation warning will be added in a **minor** release.
The feature will continue to work for all releases in that major series, and will be removed in the next major release.

For example, if a deprecation warning is added in ``1.1``, the feature will work throughout all ``1.x`` releases,
and be removed in ``2.0``.

Supported Versions
------------------

At any time, the Litestar organization will actively support:

- The current major release series
- The previous major release series
- Any other designated LTS releases (Special cases)

For example, if the current release is ``2.0``, we will actively support ``2.x`` and ``1.x``.
When ``3.0`` is released, we will drop support for ``1.x``.

Bugfixes will be applied to the current major release, and selectively backported to older
supported versions based on severity and feasibility.

Release Process
---------------

Each major release cycle consists of a few phases:

#. **Planning**: Define roadmap, spec out major features. Work should begin on implementation.
#. **Development**: Active development on planned features. Ends with an alpha release and branch of ``A.B.x``
   branch from `main`.
#. **Bugfixes**: Only bugfixes, no new features. Progressively release beta, release candidates.
   Feature freeze at RC. Become more selective with backports to avoid regressions.
