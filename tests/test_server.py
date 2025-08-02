"""Tests for MCP server functionality."""

from unittest.mock import patch

import mcp.types as types
import pytest

from qr_code_reader.server import handle_call_tool, handle_list_tools


class TestMCPServer:
    """Test suite for MCP server."""

    @pytest.mark.asyncio
    async def test_handle_list_tools(self):
        """Test that list_tools returns the expected tool definition."""
        tools = await handle_list_tools()

        assert len(tools) == 1
        tool = tools[0]

        assert tool.name == "qr_code_read"
        assert "Read and decode QR codes from images" in tool.description
        assert "inputSchema" in tool.__dict__

        # Check schema structure
        schema = tool.inputSchema
        assert schema["type"] == "object"
        assert "image_path" in schema["properties"]
        assert "image_data" in schema["properties"]
        assert "oneOf" in schema

    @pytest.mark.asyncio
    async def test_handle_call_tool_unknown_tool(self):
        """Test that unknown tool raises ValueError."""
        with pytest.raises(ValueError, match="Unknown tool: unknown_tool"):
            await handle_call_tool("unknown_tool", {})

    @pytest.mark.asyncio
    @patch("qr_code_reader.qr_reader.read_qr_code")
    async def test_handle_call_tool_qr_code_read_success(self, mock_read_qr):
        """Test successful QR code reading through MCP tool."""
        mock_read_qr.return_value = "https://example.com"

        result = await handle_call_tool(
            "qr_code_read", {"image_path": "/fake/path.jpg"}
        )

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "QR Code decoded successfully: https://example.com" in result[0].text

        mock_read_qr.assert_called_once_with(
            image_path="/fake/path.jpg", image_data=None
        )

    @pytest.mark.asyncio
    @patch("qr_code_reader.qr_reader.read_qr_code")
    async def test_handle_call_tool_qr_code_read_with_base64(self, mock_read_qr):
        """Test QR code reading with base64 data."""
        mock_read_qr.return_value = "test_data"

        result = await handle_call_tool("qr_code_read", {"image_data": "base64_data"})

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "QR Code decoded successfully: test_data" in result[0].text

        mock_read_qr.assert_called_once_with(image_path=None, image_data="base64_data")

    @pytest.mark.asyncio
    async def test_handle_call_tool_no_arguments(self):
        """Test QR code tool with no arguments."""
        result = await handle_call_tool("qr_code_read", {})

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert (
            "Error: Either image_path or image_data must be provided" in result[0].text
        )

    @pytest.mark.asyncio
    async def test_handle_call_tool_import_error(self):
        """Test handling of ImportError when qr_reader module is not available."""
        # Patch the import statement in the server module
        with patch.dict("sys.modules", {"qr_code_reader.qr_reader": None}):
            result = await handle_call_tool(
                "qr_code_read", {"image_path": "/fake/path.jpg"}
            )

            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert "Error: QR code reader module not yet implemented" in result[0].text

    @pytest.mark.asyncio
    @patch("qr_code_reader.qr_reader.read_qr_code")
    async def test_handle_call_tool_general_exception(self, mock_read_qr):
        """Test handling of general exceptions during QR code reading."""
        mock_read_qr.side_effect = Exception("Something went wrong")

        result = await handle_call_tool(
            "qr_code_read", {"image_path": "/fake/path.jpg"}
        )

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Error reading QR code: Something went wrong" in result[0].text

    @pytest.mark.asyncio
    @patch("qr_code_reader.server.logger")
    @patch("qr_code_reader.qr_reader.read_qr_code")
    async def test_handle_call_tool_logs_error(self, mock_read_qr, mock_logger):
        """Test that errors are properly logged."""
        mock_read_qr.side_effect = Exception("Test error")

        await handle_call_tool("qr_code_read", {"image_path": "/fake/path.jpg"})

        mock_logger.error.assert_called_once()
        args = mock_logger.error.call_args[0]
        assert "Error reading QR code: Test error" in args[0]
