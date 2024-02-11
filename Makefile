# Makefile for nsequence project

.PHONY: install test bump coverage clean

# Install dependencies
install:
	pip install nsequence[dev]

# Run tests
test:
	pytest

# Build
build:
	python -m build && twine check dist/*

# Upload to TestPYPI
test-pypi-upload:
	twine upload -r testpypi dist/*

# Upload to PYPI
# pypi-upload:
#	twine upload dist/*

# Bump version
bump:
	@echo "Please run the bumping command directly for the meantime using bumpver"

# Coverage
coverage:
	pytest --cov=nsequence --cov-report html

# Clean
clean:
	rm -rf build/ dist/ *.egg-info/ .coverage htmlcov
