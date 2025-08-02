.PHONY: install test coverage lint format run clean help docker-build docker-run docker-dev docker-test docker-clean docker-shell

# Variables
PYTHON := uv run python
PYTEST := uv run pytest
BLACK := uv run black
RUFF := uv run ruff
MYPY := uv run mypy
DOCKER_IMAGE := qr-code-reader-mcp
DOCKER_TAG := latest

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

# Docker targets
docker-build: ## Build Docker image
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run: ## Run Docker container
	docker run --rm -p 8000:8000 --name qr-code-reader $(DOCKER_IMAGE):$(DOCKER_TAG)

docker-dev: ## Run Docker container in development mode with volume mounts
	docker run --rm -it \
		-p 8000:8000 \
		-v $(PWD)/src:/app/src \
		-v $(PWD)/tests:/app/tests \
		--name qr-code-reader-dev \
		$(DOCKER_IMAGE):$(DOCKER_TAG) \
		/bin/bash

docker-test: ## Run tests in Docker container
	docker run --rm \
		-v $(PWD)/src:/app/src \
		-v $(PWD)/tests:/app/tests \
		$(DOCKER_IMAGE):$(DOCKER_TAG) \
		make test

docker-clean: ## Remove Docker images and containers
	docker stop qr-code-reader qr-code-reader-dev 2>/dev/null || true
	docker rm qr-code-reader qr-code-reader-dev 2>/dev/null || true
	docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) 2>/dev/null || true

docker-shell: ## Open shell in Docker container
	docker run --rm -it \
		-v $(PWD):/app \
		--workdir /app \
		$(DOCKER_IMAGE):$(DOCKER_TAG) \
		/bin/bash