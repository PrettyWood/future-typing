.DEFAULT_GOAL := all
black = black future_typing tests --exclude tests/test_future_typing.py
isort = isort future_typing tests

.PHONY: all
all: lint test

.PHONY: install
install:
	pip install -U pip
	pip install -e .[test]

.PHONY: install-dev
install-dev: install
	pip install -e .[dev]
	pre-commit install

.PHONY: test
test:
	pytest --cov future_typing --cov-report=term-missing --cov-report=xml\
           --ignore tests/test_future_typing.py

.PHONY: format
format:
	${isort}
	${black}

.PHONY: lint
lint:
	flake8 future_typing tests
	${isort} --check-only --df
	${black} --diff --check
	mypy future_typing

.PHONY: build
build:
	python setup.py sdist bdist_wheel

.PHONY: upload
upload:
	twine upload dist/*

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf coverage.xml
	rm -rf build
	rm -rf dist
	python setup.py clean
