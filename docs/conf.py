from __future__ import annotations

import sys
from datetime import datetime
from functools import partial
from typing import TYPE_CHECKING, Any
from unittest import mock

from polyfactory.__metadata__ import __project__, __version__

if TYPE_CHECKING:
    from sphinx.addnodes import document
    from sphinx.application import Sphinx

for mod_name in ("beanie", "odmantic"):
    sys.modules[mod_name] = mock.Mock()

PY_CLASS = "py:class"
PY_RE = r"py:.*"

# -- Environmental Data ------------------------------------------------------

# -- Project information -----------------------------------------------------
current_year = datetime.now().year
project = __project__
copyright = f"{current_year}, Litestar Organization"
release = __version__

extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_design",
    "auto_pytabs.sphinx_ext",
    "sphinx_copybutton",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_toolbox.collapse",
    "sphinx_togglebutton",
    "sphinx_paramlinks",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "faker": ("https://faker.readthedocs.io/en/master/", None),
    "pytest": ("https://docs.pytest.org/en/latest/", None),
    "msgspec": ("https://jcristharif.com/msgspec/", None),
}

nitpicky = True
nitpick_ignore = [
    (PY_CLASS, "BaseModel"),
    (PY_CLASS, "Decimal"),
    (PY_CLASS, "Faker"),
    (PY_CLASS, "FieldInfo"),
    (PY_CLASS, "Random"),
    (PY_CLASS, "Scope"),
    (PY_CLASS, "T"),
    (PY_CLASS, "F"),
    (PY_CLASS, "P"),
    (PY_CLASS, "P.args"),
    (PY_CLASS, "P.kwargs"),
    (PY_CLASS, "Self"),
    (PY_CLASS, "TypeGuard"),
    (PY_CLASS, "date"),
    (PY_CLASS, "tzinfo"),
    (PY_CLASS, "BeanieDocumentFactory"),
    (PY_CLASS, "OdmanticModelFactory"),
    (PY_CLASS, "ModelField"),
    (PY_CLASS, "Session"),
    (PY_CLASS, "AsyncSession"),
]
nitpick_ignore_regex = [
    (PY_RE, r"typing_extensions.*"),
    (PY_RE, r"polyfactory.*\.T"),
    (PY_RE, r"polyfactory.*\.P"),
    (PY_RE, r".*TypedDictT"),
    (PY_RE, r"pydantic.*"),
    (PY_RE, r"msgspec.*"),
]

suppress_warnings = [
    "autosectionlabel.*",
    "ref.python",  # TODO: remove when https://github.com/sphinx-doc/sphinx/issues/4961 is fixed
    "config.cache",
]

napoleon_google_docstring = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_attr_annotations = True

autoclass_content = "class"
autodoc_class_signature = "separated"
autodoc_default_options = {
    "special-members": True,
    "show-inheritance": True,
    "members": True,
    "exclude-members": "__init_subclass__,__weakref__,__subclasshook__",
}
autodoc_member_order = "bysource"
autodoc_typehints_format = "short"

auto_pytabs_min_version = (3, 8)
auto_pytabs_max_version = (3, 11)
auto_pytabs_compat_mode = True

autosectionlabel_prefix_document = True
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Style configuration -----------------------------------------------------
html_theme = "litestar_sphinx_theme"
html_title = "Polyfactory"
# pygments_style = "lightbulb"
todo_include_todos = True

html_static_path = ["_static"]
templates_path = ["_templates"]
html_js_files = ["versioning.js"]
html_css_files = ["style.css"]

html_show_sourcelink = True
html_copy_source = True

html_context = {
    "source_type": "github",
    "source_user": "litestar-org",
    "source_repo": "polyfactory",
    "current_version": "latest",
    "versions": [
        ("latest", "/latest"),
        ("development", "/main"),
    ],
    "version": release,
}

html_theme_options = {
    "logo_target": "/",
    "github_repo_name": "polyfactory",
    "github_url": "https://github.com/litestar-org/polyfactory",
    "navigation_with_keys": True,
    "nav_links": [
        {"title": "Home", "url": "index"},
        {
            "title": "Community",
            "children": [
                {
                    "title": "Contributing",
                    "summary": "Learn how to contribute to the Type Lens project",
                    "url": "contribution-guide",
                    "icon": "contributing",
                },
                {
                    "title": "Code of Conduct",
                    "summary": "Review the etiquette for interacting with the Litestar community",
                    "url": "https://github.com/litestar-org/.github?tab=coc-ov-file",
                    "icon": "coc",
                },
                {
                    "title": "Security",
                    "summary": "Overview of Litestar's security protocols",
                    "url": "https://github.com/litestar-org/.github?tab=coc-ov-file#security-ov-file",
                    "icon": "coc",
                },
            ],
        },
        {
            "title": "About",
            "children": [
                {
                    "title": "Litestar Organization",
                    "summary": "Details about the Litestar organization",
                    "url": "https://litestar.dev/about/organization",
                    "icon": "org",
                },
                {
                    "title": "Releases",
                    "summary": "Explore the release process, versioning, and deprecation policy for Litestar",
                    "url": "releases",
                    "icon": "releases",
                },
            ],
        },
        {
            "title": "Release notes",
            "children": [
                {
                    "title": "Changelog",
                    "url": "changelog",
                    "summary": "All changes in the current major version",
                },
            ],
        },
        {
            "title": "Help",
            "children": [
                {
                    "title": "Discord Help Forum",
                    "summary": "Dedicated Discord help forum",
                    "url": "https://discord.gg/litestar",
                    "icon": "coc",
                },
                {
                    "title": "GitHub Discussions",
                    "summary": "GitHub Discussions",
                    "url": "https://github.com/litestar-org/polyfactory/discussions",
                    "icon": "coc",
                },
                {
                    "title": "Stack Overflow",
                    "summary": "We monitor the <code><b>polyfactory</b></code> tag on Stack Overflow",
                    "url": "https://stackoverflow.com/questions/tagged/polyfactory",
                    "icon": "coc",
                },
            ],
        },
        {"title": "Sponsor", "url": "https://github.com/sponsors/Litestar-Org", "icon": "heart"},
    ],
}


def update_html_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, Any],
    doctree: document,
) -> None:
    context["generate_toctree_html"] = partial(context["generate_toctree_html"], startdepth=0)


def delayed_setup(app: Sphinx) -> None:
    """When running linkcheck Shibuya causes a build failure, and checking
    the builder in the initial `setup` function call is not possible, so the check
    and extension setup has to be delayed until the builder is initialized.
    """
    if app.builder.name == "linkcheck":
        return

    app.setup_extension("shibuya")


def setup(app: Sphinx) -> dict[str, bool]:
    app.connect("builder-inited", delayed_setup, priority=0)
    app.setup_extension("litestar_sphinx_theme")
    return {"parallel_read_safe": True, "parallel_write_safe": True}
