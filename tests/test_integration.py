"""Integration tests for MCP server end-to-end functionality."""

import asyncio
import base64
import logging
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, patch

import mcp.server.stdio
import mcp.types as types
import pytest
import qrcode
from PIL import Image

from qr_code_reader.server import handle_call_tool, handle_list_tools, main, server


class TestMCPIntegration:
    """Integration tests for MCP server functionality."""

    @pytest.fixture
    def sample_qr_image_path(self):
        """Create a temporary QR code image file for testing."""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("https://example.com/test")
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img.save(f.name)
            yield f.name

        # Cleanup
        Path(f.name).unlink(missing_ok=True)

    @pytest.fixture
    def sample_qr_image_base64(self):
        """Create a base64 encoded QR code image for testing."""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("test data for base64")
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_data = buffer.getvalue()

        return base64.b64encode(img_data).decode("utf-8")

    @pytest.mark.asyncio
    async def test_server_startup_and_shutdown(self):
        """Test that MCP server can start up and shut down gracefully."""
        # Mock the stdio streams
        read_stream = AsyncMock()
        write_stream = AsyncMock()

        # Mock the stdio_server context manager
        mock_stdio = AsyncMock()
        mock_stdio.__aenter__.return_value = (read_stream, write_stream)
        mock_stdio.__aexit__.return_value = None

        # Mock server.run to avoid hanging
        async def mock_run(*args, **kwargs):
            # Simulate server running briefly then shutting down
            await asyncio.sleep(0.01)
            return True

        with patch("mcp.server.stdio.stdio_server", return_value=mock_stdio):
            with patch.object(server, "run", side_effect=mock_run):
                # This should complete without hanging
                await main()

        # Verify stdio server was called
        mock_stdio.__aenter__.assert_called_once()
        mock_stdio.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_mcp_tool_registration(self):
        """Verify that MCP tools are properly registered and discoverable."""
        tools = await handle_list_tools()

        # Should have exactly one tool registered
        assert len(tools) == 1

        tool = tools[0]
        assert isinstance(tool, types.Tool)
        assert tool.name == "qr_code_read"
        assert "Read and decode QR codes from images" in tool.description

        # Verify schema structure
        schema = tool.inputSchema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "image_path" in schema["properties"]
        assert "image_data" in schema["properties"]
        assert "oneOf" in schema

        # Verify input validation schema
        required_schemas = schema["oneOf"]
        assert len(required_schemas) == 2
        assert {"required": ["image_path"]} in required_schemas
        assert {"required": ["image_data"]} in required_schemas

    @pytest.mark.asyncio
    async def test_end_to_end_image_processing_workflow_file_path(
        self, sample_qr_image_path
    ):
        """Test complete end-to-end workflow with file path input."""
        # Test the complete workflow from tool call to response
        result = await handle_call_tool(
            "qr_code_read", {"image_path": sample_qr_image_path}
        )

        # Verify response format
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert result[0].type == "text"

        # Verify successful QR code reading
        assert "QR Code decoded successfully:" in result[0].text
        assert "https://example.com/test" in result[0].text

    @pytest.mark.asyncio
    async def test_end_to_end_image_processing_workflow_base64(
        self, sample_qr_image_base64
    ):
        """Test complete end-to-end workflow with base64 input."""
        # Test the complete workflow from tool call to response
        result = await handle_call_tool(
            "qr_code_read", {"image_data": sample_qr_image_base64}
        )

        # Verify response format
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert result[0].type == "text"

        # Verify successful QR code reading
        assert "QR Code decoded successfully:" in result[0].text
        assert "test data for base64" in result[0].text

    @pytest.mark.asyncio
    async def test_response_format_validation_success(self, sample_qr_image_path):
        """Validate that successful responses follow the expected format."""
        result = await handle_call_tool(
            "qr_code_read", {"image_path": sample_qr_image_path}
        )

        # Response should be a list of TextContent
        assert isinstance(result, list)
        assert len(result) == 1

        content = result[0]
        assert isinstance(content, types.TextContent)
        assert hasattr(content, "type")
        assert hasattr(content, "text")
        assert content.type == "text"
        assert isinstance(content.text, str)
        assert content.text.startswith("QR Code decoded successfully:")

    @pytest.mark.asyncio
    async def test_response_format_validation_error(self):
        """Validate that error responses follow the expected format."""
        # Test with no arguments to trigger validation error
        result = await handle_call_tool("qr_code_read", {})

        # Response should be a list of TextContent
        assert isinstance(result, list)
        assert len(result) == 1

        content = result[0]
        assert isinstance(content, types.TextContent)
        assert hasattr(content, "type")
        assert hasattr(content, "text")
        assert content.type == "text"
        assert isinstance(content.text, str)
        assert content.text.startswith("Error:")

    @pytest.mark.asyncio
    async def test_error_handling_invalid_image_path(self):
        """Test error handling for invalid image paths."""
        result = await handle_call_tool(
            "qr_code_read", {"image_path": "/nonexistent/path/image.jpg"}
        )

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Error reading QR code:" in result[0].text

    @pytest.mark.asyncio
    async def test_error_handling_invalid_base64(self):
        """Test error handling for invalid base64 data."""
        result = await handle_call_tool(
            "qr_code_read", {"image_data": "invalid_base64_data"}
        )

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Error reading QR code:" in result[0].text

    @pytest.mark.asyncio
    async def test_error_handling_no_qr_code_in_image(self):
        """Test error handling when image contains no QR code."""
        # Create an image without QR code
        img = Image.new("RGB", (100, 100), color="white")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img.save(f.name)

            result = await handle_call_tool("qr_code_read", {"image_path": f.name})

            # Cleanup
            Path(f.name).unlink(missing_ok=True)

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Error reading QR code:" in result[0].text

    @pytest.mark.asyncio
    async def test_error_handling_missing_arguments(self):
        """Test error handling when required arguments are missing."""
        result = await handle_call_tool("qr_code_read", {})

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert (
            "Error: Either image_path or image_data must be provided" in result[0].text
        )

    @pytest.mark.asyncio
    async def test_error_handling_unknown_tool(self):
        """Test error handling for unknown tool calls."""
        with pytest.raises(ValueError, match="Unknown tool: nonexistent_tool"):
            await handle_call_tool("nonexistent_tool", {})

    @pytest.mark.asyncio
    async def test_logging_configuration(self):
        """Test that logging is properly configured."""
        logger = logging.getLogger("qr_code_reader.server")

        # Verify logger exists and has correct level
        assert logger is not None
        assert logger.level <= logging.INFO

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, sample_qr_image_path):
        """Test that server can handle multiple concurrent requests."""
        # Create multiple concurrent requests
        tasks = []
        for _ in range(5):
            task = handle_call_tool(
                "qr_code_read", {"image_path": sample_qr_image_path}
            )
            tasks.append(task)

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)

        # Verify all requests succeeded
        assert len(results) == 5
        for result in results:
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert "QR Code decoded successfully:" in result[0].text
            assert "https://example.com/test" in result[0].text

    @pytest.mark.asyncio
    async def test_server_capabilities(self):
        """Test that server capabilities are properly configured."""
        capabilities = server.get_capabilities(
            notification_options=mcp.server.NotificationOptions(),
            experimental_capabilities={},
        )

        assert capabilities is not None
        assert hasattr(capabilities, "tools")
        # MCP server should support tools capability
        assert capabilities.tools is not None

    @pytest.mark.asyncio
    async def test_server_version_and_metadata(self):
        """Test that server metadata is properly configured."""
        from qr_code_reader import __version__

        # Version should be defined
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0

        # Server should have correct name
        assert server.name == "qr-code-reader"
