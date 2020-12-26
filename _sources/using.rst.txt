Using Kodistubs
===============

Writing Code
------------

The main purpose of Kodistubs is to help you to write Kodi addon code in various
:abbr:`IDEs(Integrated Development Environments)` by providing code completion,
quick access to Kodi Python API docstrings, and code inspection (linting)
in IDEs that provide this feature.

When developing Python addons for Kodi it is strongly recommended to use
`virtual environments`_ to isolate your development dependencies. Virtual
environments are supported by all popular Python IDEs.

You can install Kodistubs in your working Python virtual environment
either from sources using :file:`setup.py` script::

  python setup.py install

or directly from PyPI using ``pip``::

  pip install Kodistubs

Below are the examples of autocompletion and docstrings pup-ups in popular
Python IDEs:

.. figure:: _static/pycharm_autocompletion.jpg

    **Code completion and a docstring pop-up in PyCharm**

PyCharm docstrings pop-ups partially support reStructuredText formatting.

.. figure:: _static/pycharm_docstring.png

    **Function docstring pop-up in PyCharm**

.. figure:: _static/pydev_autocompletion.jpg

     **Code completion and a docstring pop-up in Eclipse/PyDev**

.. figure:: _static/ptvs_autocompletion.jpg

    **Code completion and a docstring pop-up in Visual Studio**

.. figure:: _static/vscode-autocompletion.png

    **Code completion and a docstring pop-up in Visual Studio Code**

.. figure:: _static/sublime_text_anaconda.jpg

    **Code completion and a docstring pop-up in Sublime Text 3**

.. _virtual environments: https://virtualenv.pypa.io/en/latest/

Type Annotations
----------------

Kodistubs include `PEP-484`_ type annotations for all functions and methods
so you can use `mypy`_ or other compatible tool to check types of function/method
arguments and return values in your code.

.. code-block:: python
  :emphasize-lines: 1

  def getInfoLabel(cLine: str) -> str:
      """
      Get a info label

      :param infotag: string - infoTag for value you want returned.
      :return: InfoLabel as a string

      List of InfoTags - http://kodi.wiki/view/InfoLabels

      Example::

          ..
          label = xbmc.getInfoLabel('Weather.Conditions')
          ..
      """
      return ""

Some IDEs, for example PyCharm, support type annotation and provide warnings
about type incompatibility.

.. note::
  ``Union[type1, type2]`` means that a function or a method accepts or returns
  either ``type1`` or ``type2``.

.. _PEP-484: https://www.python.org/dev/peps/pep-0484/
.. _mypy: http://mypy-lang.org/

Testing Code
------------

You can use Kodistubs in combination with some mocking library, e.g. `mock`_,
to write unit tests for your addon code.

.. _mock: https://pypi.python.org/pypi/mock

Documenting Code
----------------

Currently `Sphinx`_ is *de facto* the standard tool for documenting Python code. But for generating
documentation from docstrings it requires that your modules can be imported without any side-effects
(i.e. exceptions). If you want to document your addon with Sphinx, add Kodi stubs folder to
:data:`sys.path` of :file:`conf.py` file in your Sphinx project and in most cases your addon modules will be
imported without issues. Just don't forget to protect your module-level exetutable code with
``if __name__ == '__main__'`` condition.

Also the root URL of this documentation (without :file:`index.html`) can be used as a reference point
for `intersphinx`_. For example::

    intersphinx_mapping = {
        'https://docs.python.org/3.8: None,
        'http://romanvm.github.io/Kodistubs': None,  # Reference to Kodi stubs
    }

This will enable cross-references to Kodi Python API objects in your Sphinx-generated documentation.

.. _Sphinx: http://www.sphinx-doc.org/en/stable/
.. _intersphinx: http://www.sphinx-doc.org/en/stable/ext/intersphinx.html
