# Python interpreter selection:
# 1. An explicitly passed PYTHON (make PYTHON=...) always wins.
# 2. An already activated virtual environment (or CI's setup-python) is used as-is.
# 3. Otherwise the project's .venv is used if it exists.
# 4. Otherwise fall back to the system python3.
VENV_DIR := .venv
ifndef PYTHON
  ifdef VIRTUAL_ENV
    PYTHON := python
  else ifneq ($(wildcard $(VENV_DIR)/bin/python),)
    PYTHON := $(abspath $(VENV_DIR)/bin/python)
  else ifneq ($(wildcard $(VENV_DIR)/Scripts/python.exe),)
    PYTHON := $(abspath $(VENV_DIR)/Scripts/python.exe)
  else
    PYTHON := python3
  endif
endif

# Comma-separated list of modules to generate, e.g. make stubs MODULES=xbmc,xbmcgui
MODULES ?=

DOCS_DIR := docs
DOCS_BUILD_DIR := $(DOCS_DIR)/_build

.PHONY: stubs docs build upload clean full-clean clean-docs

stubs:
	$(PYTHON) -m kodistubs_generator $(MODULES)

docs:
	$(PYTHON) -m sphinx -b html -d $(DOCS_BUILD_DIR)/doctrees $(DOCS_DIR) $(DOCS_BUILD_DIR)/html

build:
	$(PYTHON) -m build

upload:
	$(PYTHON) -m twine upload dist/*

# Removes setuptools artifacts only, keeping the generator's SWIG cache in build/swig.
clean:
	rm -rf build/lib build/bdist.* dist *.egg-info src/*.egg-info

# Also removes the SWIG XML cache and Doxygen XML so that `make stubs` regenerates them from scratch.
full-clean: clean
	rm -rf build doxygen/xml

clean-docs:
	rm -rf $(DOCS_BUILD_DIR)/html $(DOCS_BUILD_DIR)/doctrees
