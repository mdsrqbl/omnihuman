# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "OmniHuman"
copyright = "2024, Mudassar Iqbal"
author = "Mudassar Iqbal"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.linkcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_rtd_dark_mode",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

default_dark_mode = False
source_encoding = "utf-8"
autosummary_generate = True
intersphinx_mapping = {"python": ("https://docs.python.org/3/", None)}

from typing import Optional

import requests


def linkcode_resolve(domain, info) -> Optional[str]:
    """
    Generates a URL for the given domain and module information.

    Parameters:
        domain (str): The domain of the link.
        info (dict): The module information.

    Returns:
        str | None: The generated URL or None if the URL is not valid.
    """

    if domain != "py":
        return None
    if not info["module"]:
        return None

    filename = info["module"].replace(".", "/")
    base_url = "https://github.com/mdsrqbl/omnihuman/blob/main/"
    for slug in [filename, f"{filename}/__init__.py", f"{filename}.py"]:
        url = base_url + slug
        try:
            if requests.head(base_url + slug, timeout=20).status_code == 200:
                return url
        except:
            pass

    return None


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_logo = "https://github.com/user-attachments/assets/69a319dc-9880-464e-a895-d04640824a12"
