# (c) 2018, Roman Miroshnychenko <roman1972@gmail.com>
# License: GPL v.3
# This file is needed for docs

import datetime
from configparser import ConfigParser
from pathlib import Path

project_dir = Path(__file__).resolve().parent
setup_cfg = project_dir / 'setup.cfg'

config = ConfigParser()
config.read([setup_cfg])
metadata = config['metadata']

VERSION = metadata['version']
AUTHOR = metadata['author']
EMAIL = metadata['author_email']
YEAR = datetime.datetime.now().year
