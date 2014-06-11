# -*- coding: utf-8 -*-
#
# OmeroPy API documentation build configuration file, created by
# sphinx-quickstart on Mon Jul 23 12:22:32 2012.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import datetime
import sys, os
import os.path

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath(os.path.join('..','..','dist','lib','python')))
sys.path.insert(0, os.path.abspath(os.path.join('..','..','dist','lib','python','omeroweb')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'omeroweb.settings'
sys.path.insert(0, os.path.join('..', 'sphinx', 'common'))
from conf import *

# -- General configuration -----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions += ['sphinx.ext.autodoc', 'sphinx.ext.autosummary', 'sphinx.ext.todo', 'sphinx.ext.coverage', 'sphinx.ext.pngmath']

# General information about the project.
project = u'OmeroPy API'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
release = os.environ.get('OMERO_RELEASE', 'UNKNOWN')

# -- Options for HTML output ---------------------------------------------------

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = '../sphinx/common/images/ome-tight.svg'

# The suffix of source filenames.
source_suffix = '.rst'

# Output file base name for HTML help builder.
htmlhelp_basename = 'OmeroPyAPIdoc'

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = ['../sphinx/common/themes']

# -- Options for LaTeX output --------------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'OmeroPyAPI.tex', u'OmeroPy API Documentation',
   u'OME Consortium', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'omeropyapi', u'OmeroPy API Documentation',
     [u'OME Consortium'], 1)
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output ------------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  ('index', 'OmeroPyAPI', u'OmeroPy API Documentation',
   u'OME Consortium', 'OmeroPyAPI', 'One line description of project.',
   'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'


# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'http://docs.python.org/': None}
