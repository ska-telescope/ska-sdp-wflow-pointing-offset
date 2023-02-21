# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

project = 'SDP Pointing Offset Calibration Pipeline'
copyright = '2023, SKA Organisation'
author = 'See CONTRIBUTORS'
release = '0.0.0'

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath("../../src"))


def setup(app):
    app.add_css_file("css/custom.css")
    app.add_js_file("js/github.js")


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx_automodapi.automodapi",
    "sphinx_automodapi.smart_resolver",
]


autodoc_mock_imports = [
    "astropy",
    "numpy",
    "katpoint", 
    "katdal",
    "scikits-fitting",
    "python-casacore", 
    "pyuvdata",
    "matplotlib",
]

templates_path = ['_templates']
exclude_patterns = []
# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = [".rst", ".md"]
# source_suffix = '.rst'

# The master toctree document.
master_doc = "index"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
