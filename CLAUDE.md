# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server written in Python that provides QR code reading functionality. The server takes an image as input and uses OpenCV for computer vision to detect and decode QR codes, returning the decoded value to AI agents.

## Technology Stack

- **Language**: Python
- **Package Management**: uv
- **Computer Vision**: OpenCV
- **Testing**: Unit testing with coverage
- **Build System**: Makefile

## Development Commands

The project uses a Makefile for common development tasks:

```bash
# Install dependencies
uv sync

# Run the MCP server
uv run python src/main.py

# Run tests
make test

# Run tests with coverage
make coverage

# Lint code
make lint

# Format code
make format
```

## MCP Server Architecture

The server implements a single MCP tool:
- **Tool Name**: `qr_code_read`
- **Input**: Image file
- **Processing**: Uses OpenCV to detect and decode QR codes
- **Output**: Decoded QR code value as string

## Project Structure

This is currently a new project with only a README.md file. The expected structure will be:

```
src/
├── main.py          # MCP server entry point
├── qr_reader.py     # QR code detection and decoding logic
└── tests/           # Unit tests
```

## Development Notes

- Uses unit testing and coverage to ensure code safety
- Follow Python best practices for MCP server development
- OpenCV integration for image processing and QR code detection