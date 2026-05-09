.PHONY: build upload clean

build:
	python -m build

upload:
	twine upload dist/*

clean:
	rm -rf dist
