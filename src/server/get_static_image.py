### `src/server/get_static_image.py`
### MCP server resource for serving a static image
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
import os
import base64
from . import mcp

@mcp.resource(uri="resource://Image.png", name="get_static_image", description="This offers a static image file.", mime_type="image/png")
def get_static_image() -> bytes:
    """Static image file."""

    # Returning a base64-encoded string of the image
    resource_dir = os.path.join(os.path.dirname(__file__), "../assets")
    image_path = os.path.join(resource_dir, "Image.png")
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded
