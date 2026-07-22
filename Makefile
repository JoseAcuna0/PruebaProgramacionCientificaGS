#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = gamescout
PYTHON_VERSION = 3.11
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python dependencies
.PHONY: install
install:
	conda env update --name $(PROJECT_NAME) --file environment.yml --prune

## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8, black, and isort
.PHONY: lint
lint:
	flake8 --max-line-length 100 gamescout tests app
	isort --check --diff gamescout tests app
	black --check --line-length 100 gamescout tests app

## Format source code with black and isort
.PHONY: format
format:
	isort gamescout tests app
	black --line-length 100 gamescout tests app

## Run main application pipeline
.PHONY: run
run:
	$(PYTHON_INTERPRETER) -m gamescout.main

## Run Streamlit dashboard
.PHONY: dashboard
dashboard:
	python -m streamlit run app/dashboard.py

## Run tests
.PHONY: test
test:
	python -m pytest tests

## Set up Python interpreter environment
.PHONY: create_environment
create_environment:
	conda env create --name $(PROJECT_NAME) -f environment.yml
	@echo ">>> conda env created. Activate with:\nconda activate $(PROJECT_NAME)"

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)