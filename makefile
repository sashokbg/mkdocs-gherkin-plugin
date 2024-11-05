.PHONY: clean

clean:
	rm -rf build
	rm -rf dist

build:
	python3 -m pip install --upgrade build
	python3 -m build
