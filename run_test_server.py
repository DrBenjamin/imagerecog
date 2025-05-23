### `run_test_server.py`
### Simple script to run a test MCP server on a different port
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
import uvicorn
import asyncio
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from mcp.server.fastmcp import FastMCP
from mcp.server import Server

# Define a port different from the main server
PORT = 8081
HOST = "0.0.0.0"

# Create a basic MCP server with minimal functionality
mcp_server = FastMCP(
    "TestRemoteServer",
    capabilities={
        "resources": {
            "subscribe": True,
            "listChanged": True
        },
        "prompts": {
            "listChanged": True
        }
    }
)._mcp_server

# Register a simple test tool
@mcp_server.tool()
async def remote_test_tool(message: str) -> str:
    """A simple test tool hosted on the remote server."""
    return f"Remote server processed: {message}"

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Creating a Starlette application for the MCP server with SSE."""
    sse = SseServerTransport("/messages/")
    
    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            try:
                await mcp_server.run(
                    read_stream,
                    write_stream,
                    mcp_server.create_initialization_options(),
                )
            except asyncio.CancelledError:
                # Exiting gracefully when client disconnects
                return

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

if __name__ == "__main__":
    print(f"Starting test MCP server on http://{HOST}:{PORT}")
    print("This server provides the 'remote_test_tool' for testing remote MCP functionality")
    print("Press Ctrl+C to stop the server")
    
    starlette_app = create_starlette_app(mcp_server, debug=True)
    uvicorn.run(starlette_app, host=HOST, port=PORT)