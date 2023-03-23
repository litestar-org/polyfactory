project = "Polyfactory"
copyright = "2023, Starlite API"
author = "Starlite API"
release = "2.0.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

napoleon_google_docstring = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_attr_annotations = True

suppress_warnings = [
    "autosectionlabel.*",
    "ref.python",  # TODO: remove when https://github.com/sphinx-doc/sphinx/issues/4961 is fixed
]

html_theme = "starlite_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ["style.css"]
html_show_sourcelink = False
html_title = "Starlite Project | Polyfactory"

html_additional_pages = {"index": "landing.html"}

html_theme_options = {
    "github_repo_name": "polyfactory",
    "use_edit_page_button": False,
    "extra_navbar_items": {
        "Documentation": "reference/index",
        "Community": {
            "Contribution guide": "community/contribution-guide/index",
            "Code of Conduct": "https://github.com/starlite-api/.github/blob/main/CODE_OF_CONDUCT.md",
        },
        "About": {
            "Organization": "about/organization",
            "Releases": "about/releases",
        },
    },
}

html_context = {
    "navbar_items": {
        "Documentation": "reference/index",
        "Community": {
            "Contribution guide": "community/contribution-guide/index",
            "Code of Conduct": "https://github.com/starlite-api/.github/blob/main/CODE_OF_CONDUCT.md",
        },
        "About": {
            "Organization": "about/organization",
            "Releases": "about/releases",
        },
    }
}
