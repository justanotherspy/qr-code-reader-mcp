"""MCP Server for QR Code Reader."""

import asyncio
import logging
from typing import Any

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from . import __version__

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create server instance
server = Server("qr-code-reader")


@server.list_tools()  # type: ignore[misc,no-untyped-call]
async def handle_list_tools() -> list[types.Tool]:
    """List available MCP tools."""
    return [
        types.Tool(
            name="qr_code_read",
            description="Read and decode QR codes from images",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to the image file containing QR code",
                    },
                    "image_data": {
                        "type": "string",
                        "description": "Base64 encoded image data (alternative to image_path)",  # noqa: E501
                    },
                },
                "oneOf": [
                    {"required": ["image_path"]},
                    {"required": ["image_data"]},
                ],
            },
        ),
    ]


@server.call_tool()  # type: ignore[misc]
async def handle_call_tool(
    name: str, arguments: dict[str, Any]
) -> list[types.TextContent]:
    """Handle tool execution requests."""
    if name == "qr_code_read":
        try:
            # Import QR code reader functionality
            from .qr_reader import read_qr_code

            # Extract arguments
            image_path = arguments.get("image_path")
            image_data = arguments.get("image_data")

            # Validate input
            if not image_path and not image_data:
                return [
                    types.TextContent(
                        type="text",
                        text="Error: Either image_path or image_data must be provided",
                    )
                ]

            # Read QR code
            result = await read_qr_code(image_path=image_path, image_data=image_data)

            return [
                types.TextContent(
                    type="text",
                    text=f"QR Code decoded successfully: {result}",
                )
            ]

        except ImportError:
            return [
                types.TextContent(
                    type="text",
                    text="Error: QR code reader module not yet implemented",
                )
            ]
        except Exception as e:
            logger.error(f"Error reading QR code: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=f"Error reading QR code: {str(e)}",
                )
            ]
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main() -> None:
    """Main entry point for the QR Code Reader MCP server."""
    logger.info(f"QR Code Reader MCP Server v{__version__} starting...")

    # Server options
    options = InitializationOptions(
        server_name="qr-code-reader",
        server_version=__version__,
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            options,
        )


if __name__ == "__main__":
    asyncio.run(main())
