### `app.py`
### Streamlit MCP client app
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
import base64
import threading
import asyncio
import io
from PIL import Image
from src.client import MCPClient
from typing import Union, Dict, Any
import json
import streamlit as st
import logging
logging.getLogger("langchain").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Setting the page config
st.set_page_config(
    page_title="BenBox",
    page_icon=":robot:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Retrieving query parameters from the URL
raw_query_list = st.query_params.get_all("query")
try:
    st.session_state.query = [
                                int(q) 
                                for q in raw_query_list
                            ][0]
except:
    st.session_state.query = 0

# Initializing a single global MCPClient
_mcp_client = MCPClient()

# Creating persistent event loop for MCP client
_mcp_loop = asyncio.new_event_loop()

# Tool to MCP server mapping (populated during connection)
_tool_server_map = {}


# Function to suppress async errors
def _suppress_async_errors(loop, context):
    msg = context.get("message", "")
    if "aclose(): asynchronous generator is already running" in msg or \
       "Attempted to exit cancel scope" in msg:
        return
    loop.default_exception_handler(context)


_mcp_loop.set_exception_handler(_suppress_async_errors)
logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("anyio").setLevel(logging.ERROR)

threading.Thread(target=_mcp_loop.run_forever, daemon=True).start()

# Ensuring we connect to the proper primary SSE endpoint
primary_mcp_base_url = st.secrets["MCP"]["MCP_URL"].rstrip("/")
primary_sse_url = f"{primary_mcp_base_url}/sse"

# Connect to primary MCP server
connect_future = asyncio.run_coroutine_threadsafe(
    _mcp_client.connect_to_sse_server(server_url=primary_sse_url, is_primary=True),
    _mcp_loop
)
try:
    # Blocking until the MCP client session is ready
    primary_tools = connect_future.result(timeout=10000)
    # Map each tool to this server for routing
    if primary_tools:
        for tool in primary_tools.split(", "):
            _tool_server_map[tool] = "primary"
except Exception as e:
    st.error(f"Failed to connect to primary MCP server: {e}")

# Connect to any remote MCP servers if configured
if "REMOTE_MCP_SERVERS" in st.secrets["MCP"]:
    remote_servers = st.secrets["MCP"]["REMOTE_MCP_SERVERS"]
    if isinstance(remote_servers, dict):
        for server_name, server_url in remote_servers.items():
            remote_url = server_url.rstrip("/")
            remote_sse_url = f"{remote_url}/sse"
            
            remote_connect_future = asyncio.run_coroutine_threadsafe(
                _mcp_client.connect_to_sse_server(server_url=remote_sse_url, is_primary=False),
                _mcp_loop
            )
            try:
                remote_tools = remote_connect_future.result(timeout=10000)
                # Map each tool to this remote server for routing
                if remote_tools:
                    for tool in remote_tools.split(", "):
                        _tool_server_map[tool] = remote_url
            except Exception as e:
                st.error(f"Failed to connect to remote MCP server {server_name}: {e}")


# Function to get the appropriate session for a tool
def _get_session_for_tool(tool_name: str):
    if tool_name in _tool_server_map:
        server_key = _tool_server_map[tool_name]
        if server_key == "primary":
            return _mcp_client.primary_session
        else:
            return _mcp_client.remote_sessions.get(server_key)
    # Default to primary session if tool not found in map
    return _mcp_client.primary_session


# Function to call the MCP tool
def call_mcp_tool_image_recognition(tool_input: Union[str, bytes]) -> tuple[str, bytes]:
    """Sending input to MCP via the SSE-backed session and return the description and raw image bytes."""

    # Accepting only image data here
    if isinstance(tool_input, str):
        raise RuntimeError("MCP image_recognition tool expects image bytes, received text input.")

    # Encoding binary input as base64 string for JSON serialization
    if isinstance(tool_input, (bytes, bytearray)):
        payload = base64.b64encode(tool_input).decode("utf-8")
    else:
        payload = tool_input
    
    async def _invoke():
        print(f"Calling MCP tool with input...")
        
        # Get the appropriate session
        session = _get_session_for_tool("image_recognition")

        # Using correct parameter name matching server-side image_recognition signature
        result = await session.call_tool(
            "image_recognition", {"image_bytes": payload}
        )
        print(f"Received MCP tool result!")
        return result

    # Scheduling invocation on persistent loop
    execution = asyncio.run_coroutine_threadsafe(_invoke(), _mcp_loop).result()

    # Extracting JSON text from the first TextContent in the response
    content = execution.content
    text_obj = content[0]
    json_str = getattr(text_obj, 'text', text_obj)
    parsed = json.loads(json_str)
    description = parsed.get('description', '')
    image_bytes_b64 = parsed.get('image_bytes', '')
    raw = base64.b64decode(image_bytes_b64) if isinstance(
        image_bytes_b64, str) else image_bytes_b64
    return description, raw


def call_mcp_generic(input: str, params: dict={}) -> str:
    """Calling an MCP resource or prompt by name with given parameters and return its text output."""
    async def _invoke():
        # Select the appropriate session based on the operation
        session = _mcp_client.primary_session  # Default to primary
        
        # For tool-based operations, try to route to the appropriate server
        if "review_code" in input:
            session = _get_session_for_tool("review_code")
        
        # Using `read_resource` for URIs with scheme and `get_prompt` for prompts
        if "Static image file" in input:
            result = await session.read_resource("resource://Image.png")
        elif "Variable image file" in input:
            uri = f"resource://{params.get('image', '')}"
            result = await session.read_resource(uri)
        else:
            result = await session.get_prompt(input, params)
        return result
    execution = asyncio.run_coroutine_threadsafe(_invoke(), _mcp_loop).result()

    # Handling prompt results which have .messages instead of .content
    if hasattr(execution, "messages"):
        msgs = execution.messages
        if msgs and isinstance(msgs[0], dict):
            return msgs[0].get("content", "")
        first_msg = msgs[0]
        return getattr(first_msg, "text", str(first_msg))

    # Handling resource reads returning sequence of contents or ResourceReadResult
    contents = execution
    if hasattr(execution, "contents"):
        contents = execution.contents
    if isinstance(contents, (list, tuple)) and contents:
        first = contents[0]
        return getattr(first, "text", getattr(first, "contents", str(first)))

    # Fallback to string representation
    return str(execution)


# Menu
func_choice = st.selectbox(
    "Select MCP function",
    ("🌌 Static Image", "🏞️ Variable Image", "💻 Review Code", "🩻 Image Recognition"),
    index=st.session_state.query if st.session_state.query else 0,
)

if func_choice == "🌌 Static Image":
    st.title("🌌 Static Image")
    if st.button("Fetch Image"):
        with st.spinner("Fetching image from MCP..."):
            response = call_mcp_generic("Static image file")

        # Parsing data URL and decode base64 to bytes, then display
        try:
            parts = response.split(",", 1)
            b64 = parts[1] if len(parts) > 1 else parts[0]
            raw_bytes = base64.b64decode(b64)
            img = Image.open(io.BytesIO(raw_bytes))
            st.image(img, caption="Image.png", use_container_width=True)
        except Exception as e:
            st.error(f"Failed to display image: {e}")

elif func_choice == "🏞️ Variable Image":
    st.title("🏞️ Variable Image")
    image_name = st.text_input("Enter image name", value="Image.png")
    if st.button("Fetch Variable Image"):
        with st.spinner("Fetching image from MCP..."):
            response = call_mcp_generic("Variable image file", {"image": image_name})

        # Parsing data URL and decode base64 to bytes, then display
        try:
            parts = response.split(",", 1)
            b64 = parts[1] if len(parts) > 1 else parts[0]
            raw_bytes = base64.b64decode(b64)
            img = Image.open(io.BytesIO(raw_bytes))
            st.image(img, caption=image_name, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to display image: {e}")

elif func_choice == "💻 Review Code":
    st.title("💻 Review Code")
    code_input = st.text_area("Enter code to review")
    if st.button("Review"):
        with st.spinner("Reviewing code via MCP..."):
            feedback = call_mcp_generic("review_code", {"code": code_input})
        st.write("**Review Feedback:**")
        st.code(feedback)

else:  # Image Recognition
    st.title("🩻 Image Recognition")
    uploaded = st.file_uploader(
        "Upload an image to thumbnail", type=["png", "jpg", "jpeg"]
    )
    if uploaded:
        img_bytes = uploaded.read()
        with st.spinner("Waiting for MCP tool response..."):
            description, raw_bytes = call_mcp_tool_image_recognition(img_bytes)
        st.write(f"**Beschreibung:** {description}")
        thumb = Image.open(io.BytesIO(raw_bytes))
        st.image(thumb, caption="Thumbnail", use_container_width=True)
