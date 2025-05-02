from typing import Any
from mcp.server.fastmcp import FastMCP
from PIL import Image as PILImage
import io
import base64
import json
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn
import asyncio
from ollama import AsyncClient
from openai import AsyncOpenAI
import os
import streamlit as st
import ast

# Choosing between Ollama (local) and OpenAI API
ollama = ast.literal_eval(f"{st.secrets['LLM_LOCAL']}")

# Defining a User-Agent header constant
USER_AGENT = "BenBox/0.3.0"

# Initializing FastMCP server with prompt capabilities (SSE)
mcp = FastMCP(
    "BenBox",
    capabilities={
        "resources": {
            "subscribe": True,
            "listChanged": True
        },
        "prompts": {
            "listChanged": True
            }
        }
)


# Defining the static resource
@mcp.resource(uri="resource://Image.png", name="get_static_image", description="This offers a static image file.", mime_type="image/png") 
def get_static_image() -> bytes:
    """Static image file."""

    # Returning a base64-encoded string of the image
    resource_dir = os.path.join(os.path.dirname(__file__), "assets")
    image_path = os.path.join(resource_dir, "Image.png")
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded


# Defining the template resource
@mcp.resource(uri="resource://{image}", name="get_variable_image", description="This offers a variable image file.", mime_type="image/png") 
def get_variable_image(image: str) -> bytes:
    """Variable image file."""

    # Returning a base64-encoded string of the image
    resource_dir = os.path.join(os.path.dirname(__file__), "assets")
    image_path = os.path.join(resource_dir, image)
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded


# Defining the code review prompt
@mcp.prompt()
def review_code(code: str) -> list[dict[str, Any]]:
    """Reviewing code and returning a summary."""
    return [
        {
            "role": "assistant",
            "content": f"Please review the following code:\n\n{code}"
        }
    ]


# Defining the image recognition tool
@mcp.tool()
async def image_recognition(image_bytes: bytes | str) -> str:
    """Creating an image recognition text and a thumbnail from provided image bytes.
       Returns a JSON string with keys "description" and "image_bytes"."""

    # Decoding base64 string if provided, ensure we have raw bytes
    if isinstance(image_bytes, str):
        image_bytes = base64.b64decode(image_bytes)
    elif not isinstance(image_bytes, (bytes, bytearray)):
        raise ValueError(
            "image_recognition expects bytes or base64 string for image_bytes")
    img = PILImage.open(io.BytesIO(image_bytes))
    img.thumbnail((400, 400))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Base64-encoding the thumbnail for JSON transport
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Generating a description for the image through a locally running model via threadpool
    if ollama:
        # Ollama API call
        async_client = AsyncClient(
            host=f"{st.secrets['OLLAMA']['OLLAMA_URL']}")
        resp = await async_client.chat(
            model=f"{st.secrets['OLLAMA']['OLLAMA_MODEL']}",
            messages=[
                {
                    "role": "system",
                    "content": f"{st.secrets['MCP']['MCP_SYSTEM_PROMPT']}",
                    "role": "user",
                    "content": f"{st.secrets['MCP']['MCP_USER_PROMPT']}",
                    "images": [encoded]
                }
            ],
            stream=False
        )
        description = resp.message.content
    else:
        # OpenAI API response
        client = AsyncOpenAI(
            api_key=f"{st.secrets['OPENAI']['OPENAI_API_KEY']}")
        resp = await client.chat.completions.create(
            model=f"{st.secrets['OPENAI']['OPENAI_MODEL']}",
            messages=[
                {
                    "role": "system",
                    "content":
                     [{
                         "type": "text",
                         "text": f"{st.secrets['MCP']['MCP_SYSTEM_PROMPT']}"
                     }],
                    "role": "user",
                    "content": [
                         {
                             "type": "text",
                             "text": f"{st.secrets['MCP']['MCP_USER_PROMPT']}"
                         },
                         {
                             "type": "image_url",
                             "image_url": {
                                 "url": f"data:image/jpeg;base64,{encoded}"
                             }
                         }
                     ],
                }
            ]
        )
        description = resp.choices[0].message.content

    # Returning a JSON object with description and base64 image for JSON transport
    return json.dumps({"description": description, "image_bytes": encoded})


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
                # client disconnected, exit gracefully
                return

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


if __name__ == "__main__":
    mcp_server = mcp._mcp_server  # noqa: WPS437
    import argparse
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080,
                        help='Port to listen on')
    args = parser.parse_args()

    # Binding SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)
    uvicorn.run(starlette_app, host=args.host, port=args.port)
