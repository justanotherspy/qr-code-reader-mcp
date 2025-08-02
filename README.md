# QR Code Reader MCP Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Docker](https://img.shields.io/badge/docker-enabled-blue)](https://www.docker.com/)

An MCP (Model Context Protocol) server that reads QR codes from images using OpenCV computer vision. The server provides a single `qr_code_read` tool that takes an image input and returns the decoded QR code value to AI agents.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (for containerized deployment)

### Development Setup

```bash
# Install dependencies
make install-dev

# Run tests
make test

# Run with coverage
make coverage

# Lint and format
make check

# Run the server (placeholder)
make run
```

### Docker Deployment

```bash
# Build container
make docker-build

# Run in container
make docker-run

# Development mode with hot-reload
make docker-dev
```

## 📖 Project Status

**Current Phase: Phase 1 Complete ✅**

- ✅ Python project setup with uv package management
- ✅ Development tools configured (pytest, black, ruff, mypy)
- ✅ Comprehensive Makefile with 14+ commands
- ✅ Git repository with GitHub integration
- ✅ Project structure and basic tests
- 🚧 **Next:** MCP server implementation + Docker containerization

See [TASKS.md](TASKS.md) for detailed development roadmap.

## 🏗️ Architecture

- **Language:** Python 3.10+
- **Package Management:** uv
- **Computer Vision:** OpenCV
- **Protocol:** Model Context Protocol (MCP)
- **Testing:** pytest with coverage
- **Containerization:** Docker
- **Development:** Claude Code + comprehensive Makefile

## 🔧 Development Tools

- **Formatting:** black
- **Linting:** ruff + mypy
- **Testing:** pytest + pytest-cov
- **Git Workflow:** Feature branches + GitHub PR workflow
- **Container:** Docker with optimized multi-stage builds
- **Security:** semgrep static analysis

## 📁 Project Structure

```
src/
├── qr_code_reader/
│   ├── __init__.py          # Package initialization
│   └── server.py            # MCP server (placeholder)
tests/
├── test_init.py             # Basic package tests
└── ...                      # Additional test modules
```

## 🐳 Docker Usage

The application is designed to run as a containerized MCP server:

```bash
# Build the image
make docker-build

# Run the server
make docker-run

# Development with volume mounts
make docker-dev

# Run tests in container
make docker-test
```

## 🤝 Contributing

We use a git workflow with feature branches and pull requests:

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add . && git commit -m "Your changes"

# Push and create PR
git push -u origin feature/your-feature
gh pr create --title "Your Feature" --body "Description"
```

## 📋 Available Commands

Run `make help` to see all available commands:

- `make install` - Install dependencies
- `make test` - Run tests
- `make coverage` - Run tests with coverage
- `make lint` - Run linting checks
- `make format` - Format code
- `make check` - Run all checks
- `make run` - Run the MCP server
- `make docker-*` - Docker operations
- `make clean` - Clean build artifacts

## 🎯 MCP Tool Interface

Once implemented, the server will provide:

- **Tool Name:** `qr_code_read`
- **Input:** Image file (PNG, JPG, etc.)
- **Output:** Decoded QR code string value
- **Error Handling:** Graceful handling of invalid images or missing QR codes