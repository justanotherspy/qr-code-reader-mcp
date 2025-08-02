.PHONY: install test coverage lint format run clean help

# Variables
PYTHON := uv run python
PYTEST := uv run pytest
BLACK := uv run black
RUFF := uv run ruff
MYPY := uv run mypy

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync

install-dev: ## Install development dependencies
	uv sync --extra dev

test: ## Run tests
	$(PYTEST)

coverage: ## Run tests with coverage
	$(PYTEST) --cov=src --cov-report=term-missing --cov-report=html

lint: ## Run linting checks
	$(RUFF) check src tests
	$(MYPY) src

format: ## Format code
	$(BLACK) src tests
	$(RUFF) format src tests

format-check: ## Check code formatting
	$(BLACK) --check src tests
	$(RUFF) format --check src tests

run: ## Run the MCP server
	$(PYTHON) -m qr_code_reader.server

clean: ## Clean up build artifacts and cache
	rm -rf .venv
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	uv build

check: format-check lint test ## Run all checks (format, lint, test)