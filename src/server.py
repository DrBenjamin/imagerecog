### `src/server.py`
### MCP server
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
import uvicorn
import asyncio
import streamlit as st
import ast
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
from server import mcp
from starlette.staticfiles import StaticFiles

# Choosing between Ollama (local) and OpenAI API
ollama = ast.literal_eval(f"{st.secrets['LLM_LOCAL']}")

# Defining a User-Agent header constant
USER_AGENT = "BenBox/0.3.0"


# Setting up the FastMCP server with capabilities
def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Creating a Starlette application that can server the provided mcp server with SSE."""

    sse = SseServerTransport("/messages/")
    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
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
            Mount("/", app=StaticFiles(directory="static", html=True), name="static"),
        ],
    )


if __name__ == "__main__":
    mcp_server = mcp._mcp_server
    import argparse
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080,
                        help='Port to listen on')
    args = parser.parse_args()

    # Binding SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)
    uvicorn.run(starlette_app, host=args.host, port=args.port)
