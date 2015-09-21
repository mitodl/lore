# -*- coding: utf-8 -*-
import sys
import os
import sphinx_bootstrap_theme

#pylint: skip-file

sys.path.insert(0, os.path.abspath('..'))

# django-specific configuration
os.environ['DJANGO_SETTINGS_MODULE'] = 'lore.settings'
# -- General configuration ------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinxcontrib.napoleon',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'LORE'
copyright = u'2015, MIT Office of Digital Learning'

version = '0.11.0'
release = '0.11.0'

exclude_patterns = ['_build']
pygments_style = 'sphinx'


# -- Options for HTML output ----------------------------------------------

html_theme = 'bootstrap'

html_theme_options = {
    'bootswatch_theme': 'cosmo',
}

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()

# The name for this set of Sphinx documents.  If None, it defaults to
html_title = "<project> v<release> documentation"

# A shorter title for the navigation bar.  Default is the same as html_title.
html_short_title = "<project> v<release> doc"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = 'LOREdoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    ('index', 'LORE.tex', u'LORE Documentation',
     u'MIT Office of Digital Learning', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'lore', u'LORE Documentation',
     [u'MIT Office of Digital Learning'], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    ('index', 'LORE', u'LORE Documentation',
     u'MIT Office of Digital Learning', 'LORE',
     'One line description of project.',
     'Miscellaneous'),
]

# -- Monkey-patch to hide 'non-local image warnings' -------------------
# The following explanation is taken from the source...
#
# ...I found this necessary because I want the sphinx-build -W to emit
# "warnings as errors" as part of my test & build infrastructure, to ensure
# that there are no mistakes in the documentation -- I know very well that
# I'm using nonlocal image URI's and I'm OK with that, but I don't want to
# ignore the other warnings.
#
# source: http://stackoverflow.com/a/28778969/875546
import sphinx.environment
from docutils.utils import get_source_line

def _warn_node(self, msg, node):
    if not msg.startswith('nonlocal image URI found:'):
        self._warnfunc(msg, '%s:%s' % get_source_line(node))

sphinx.environment.BuildEnvironment.warn_node = _warn_node
