# QR Code Reader MCP Server

This is an MCP server that takes in an Image and uses CV to read the QR code in the image and return to the AI Agent the resulting decoded value from the QR code.

This project will be written in Python and use uv for package management.
We use Claude Code for development.

# Development and Design

We use unit testing and coverage to ensure safety. The MCP server should take in a single instruction which is qr_code_read and it takes in an Image and loads it into OpenCV to read the QR code in the image.

We use a Makefile for common commands.