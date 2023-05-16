# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

project = "SDP Pointing Offset Calibration Pipeline"
copyright = "2023, SKA Organisation"
author = "See CONTRIBUTORS"
release = "0.0.0"

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath("../.."))
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
    "numpy",
    "numpy.core.multiarray",
    "katpoint",
    "scikits",
    "python-casacore",
    "pyuvdata",
    "matplotlib",
    "ska-sdp-datamodels",
    "ska-sdp-func-python",
    "pandas",
    "uncertainties",
    "scipy",
]

templates_path = ["_templates"]
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
html_context = {
    "favicon": "img/favicon_mono.ico",
    "logo": "img/logo.png",
    "theme_logo_only": True,
    "display_github": False,  # Integrate GitHub
    "github_user": "",  # Username
    "github_repo": "ska-sdp-wflow-pointing-offset",  # Repo name
    "github_version": "master",  # Version
    "conf_py_path": "/src/",  # Path in the checkout to the docs root
}

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
