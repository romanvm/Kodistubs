import sys
import os

sys.path.insert(0, os.path.abspath('..'))
import kodistubs_meta

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
]

autodoc_member_order = 'bysource'
autodoc_default_options = {
    'members': True,
    'show-inheritance': True,
}
autosummary_generate = True
intersphinx_mapping = {'https://docs.python.org/3.8': None}

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'Kodistubs'
copyright = u'{0}, {1}'.format(kodistubs_meta.YEAR, kodistubs_meta.AUTHOR)
author = kodistubs_meta.AUTHOR

version = kodistubs_meta.VERSION

language = None

exclude_patterns = ['_build']

pygments_style = 'sphinx'

todo_include_todos = False

html_theme = 'alabaster'

html_theme_options = {
    'github_button': True,
    'github_type': 'star&v=2',
    'github_user': 'romanvm',
    'github_repo': 'Kodistubs',
    'github_banner': True,
    'font_family': 'Georgia',
}

html_static_path = ['_static']

html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
    ]
}

html_show_sourcelink = False

html_show_copyright = True

htmlhelp_basename = 'Kodistubsdoc'
