# Makefile for nsequence project

.PHONY: install test bump coverage clean

# Install dependencies
install:
	pip install nsequence[dev]

# Run tests
test:
	pytest

# Run tests
build:
	python -m build && twine check dist/*

# Bump version
bump:
	@echo "Please run the bumping command directly for the meantime using bumpver"

# Coverage
coverage:
	pytest --cov=nsequence --cov-report html

# Clean
clean:
	rm -rf build/ dist/ *.egg-info/ .coverage htmlcov
