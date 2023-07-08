import datetime
import sys
from configparser import ConfigParser
from pathlib import Path

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

setup_cfg = project_dir / 'setup.cfg'

config = ConfigParser()
config.read([setup_cfg])
metadata = config['metadata']

VERSION = metadata['version']
AUTHOR = metadata['author']
YEAR = datetime.datetime.now().year

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
intersphinx_mapping = {'python': ('https://docs.python.org/3.10', None)}

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'Kodistubs'
copyright = u'{0}, {1}'.format(YEAR, AUTHOR)
author = AUTHOR

version = VERSION

language = 'en'

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
