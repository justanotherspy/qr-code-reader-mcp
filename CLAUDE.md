# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server written in Python that provides QR code reading functionality. The server takes an image as input and uses OpenCV for computer vision to detect and decode QR codes, returning the decoded value to AI agents.

**Current Status:** Phase 1 Complete - Project foundation established with Python 3.10+, uv package management, comprehensive Makefile, git repository, and development tools configured.

## Technology Stack

- **Language**: Python 3.10+
- **Package Management**: uv
- **Computer Vision**: OpenCV
- **Protocol**: Model Context Protocol (MCP)
- **Testing**: pytest with coverage
- **Containerization**: Docker
- **Build System**: Makefile
- **Version Control**: Git with GitHub integration

## Development Commands

The project uses a comprehensive Makefile for development tasks:

```bash
# Setup and Installation
make install          # Install dependencies
make install-dev      # Install with dev dependencies

# Development
make run             # Run the MCP server
make test            # Run tests
make coverage        # Run tests with coverage report
make lint            # Run linting checks (ruff + mypy)
make format          # Format code (black + ruff)
make check           # Run all checks (format-check + lint + test)

# Docker Operations
make docker-build    # Build Docker image
make docker-run      # Run container
make docker-dev      # Development mode with volume mounts
make docker-test     # Run tests in container

# Utilities
make clean           # Clean build artifacts
make build           # Build Python package
make help            # Show all available commands
```

## Git Workflow

**IMPORTANT**: Always use feature branch workflow with pull requests:

```bash
# Create feature branch
git checkout -b feature/description

# Make changes and commit
git add .
git commit -m "description"

# Push and create PR
git push -u origin feature/description
gh pr create --title "Title" --body "Description"
```

Available tools:
- `gh` CLI for GitHub operations
- `semgrep` for security static analysis

## Docker Containerization

**CRITICAL**: This application MUST always run as a Docker container for MCP server testing.

Key principles:
- All server deployments use Docker containers
- Development environment supports both local and containerized workflows
- Multi-stage builds for optimized production images
- Security scanning with container best practices
- Volume mounts for development hot-reloading

Container workflow:
```bash
make docker-build    # Build optimized image
make docker-run      # Run production container
make docker-dev      # Development with hot-reload
```

## MCP Server Architecture

The server implements a single MCP tool:
- **Tool Name**: `qr_code_read`
- **Input**: Image file (PNG, JPG, etc.)
- **Processing**: Uses OpenCV to detect and decode QR codes
- **Output**: Decoded QR code value as string
- **Error Handling**: Graceful handling of invalid images or missing QR codes

## Project Structure

```
src/
├── qr_code_reader/
│   ├── __init__.py          # Package initialization
│   └── server.py            # MCP server implementation
tests/
├── __init__.py
├── test_init.py             # Basic package tests
└── test_*.py                # Additional test modules
```

## Development Notes

- **Python Version**: Requires Python 3.10+ (MCP library requirement)
- **Package Management**: Use `uv` for all dependency operations
- **Code Quality**: All code must pass `make check` (formatting, linting, tests)
- **Testing**: Maintain >90% test coverage
- **Container First**: Always test in containerized environment
- **Security**: Run `semgrep` for security analysis
- **Documentation**: Keep README.md and TASKS.md updated with progress

## Testing Guidelines

- Use pytest for all testing
- Maintain test coverage >90%
- Create test fixtures for QR code images
- Test error scenarios (invalid images, no QR codes)
- Test containerized deployment

## Common Development Tasks

1. **Starting new feature**: Create branch, implement, test, PR
2. **Running tests**: `make test` or `make coverage`
3. **Code quality**: `make check` before commits
4. **Container testing**: `make docker-test`
5. **Security scan**: `semgrep --config=auto src/`