# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

import haskpy


# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'HaskPy'
# NOTE: Correct year is used automatically
copyright = '2019-2020, Jaakko Luttinen'
author = 'Jaakko Luttinen'

# The short X.Y version
version = haskpy.__version__
# The full version, including alpha/beta/rc tags
release = haskpy.__version__


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    #'sphinxcontrib.fulltoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    "haskpy.autoclass",
    "numpydoc",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = None

# Generate autosummary pages automatically (sphinx-autogen)
autosummary_generate = True

# Whether to show `some.package.function` or just `function`. Unfortunately,
# this doesn't affect the TOCs created by autosummary..
add_module_names = False

# For numpydoc options, see:
# https://numpydoc.readthedocs.io/en/latest/install.html

# Numpydoc toctree doesn't work nicely.. It doesn't follow the same filtering
# as what Sphinx normally uses. So, one cannot remove test_*, assert_*,
# sample_* methods from it. Also, one cannot add __eq__, __matmul__ and other
# such methods to it. These can all be controlled for Sphinx itself, but for
# some reason, numpydoc doesn't follow that. If we want a toctree, maybe create
# it ourselves?
numpydoc_class_members_toctree = False
numpydoc_show_class_members = False

autodoc_default_options = {
    # 'members': 'var1, var2',
    'member-order': 'alphabetical',
    #'member-order': 'groupwise',
    #'member-order': 'bysource',
    #'special-members': None, #True, #'__init__',
    'undoc-members': True,
    'exclude-members': ','.join([
        '__attrs_attrs__',
        '__bases__',
        '__basicsize__',
        '__class__',
        '__delattr__',
        '__doc__',
        '__dict__',
        '__dictoffset__',
        '__dir__',
        '__flags__',
        '__format__',
        '__getattribute__',
        '__init__',
        '__init_subclass__',
        '__instancecheck__',
        '__itemsize__',
        '__module__',
        '__mro__',
        '__name__',
        '__new__',
        '__prepare__',
        '__qualname__',
        '__reduce__',
        '__reduce_ex__',
        '__repr__',
        '__setattr__',
        '__sizeof__',
        '__str__',
        '__subclasscheck__',
        '__subclasses__',
        '__subclasshook__',
        '__text_signature__',
        '__weakref__',
        '__weakrefoffset__',
        'mro',
    ])
}


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'HaskPydoc'


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'HaskPy.tex', 'HaskPy Documentation',
     'Jaakko Luttinen', 'manual'),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'haskpy', 'HaskPy Documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'HaskPy', 'HaskPy Documentation',
     author, 'HaskPy', 'One line description of project.',
     'Miscellaneous'),
]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']


# -- Extension configuration -------------------------------------------------

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True
