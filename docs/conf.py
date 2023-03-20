project = 'Polyfactory'
copyright = "2023, The Starlite API Project"
author = "Starlite API Project"
release = '2.0.0'

extensions = [
    "sphinx.ext.autodoc",
    'sphinx.ext.napoleon',
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
