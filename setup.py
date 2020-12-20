# coding: utf-8

from io import open
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from kodistubs_meta import AUTHOR, EMAIL, VERSION

with open('README.rst', encoding='utf-8') as fo:
    long_descr = fo.read()

setup(
    name='Kodistubs',
    version=VERSION,
    py_modules=[
        'xbmc', 'xbmcaddon', 'xbmcgui', 'xbmcplugin', 'xbmcvfs', 'xbmcdrm'
    ],
    zip_safe=False,
    python_requires='>=3.6',
    description='Stub modules that re-create Kodi Python API',
    long_description=long_descr,
    author=AUTHOR,  # The new Kodistubs have been generated from scratch
    author_email=EMAIL,
    url='https://github.com/romanvm/Kodistubs',
    license='GPLv3',
    keywords="kodi documentation inspection",
    classifiers=[
        'Environment :: Plugins',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ]
)
