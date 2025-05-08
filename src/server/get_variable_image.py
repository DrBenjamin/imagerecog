### `src/server/get_variable_image.py`
### MCP server resource for serving a variable image
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
import os
import base64
from . import mcp

@mcp.resource(uri="resource://{image}", name="get_variable_image", description="This offers a variable image file.", mime_type="image/png")
def get_variable_image(image: str) -> bytes:
    """Variable image file."""

    # Returning a base64-encoded string of the image
    resource_dir = os.path.join(os.path.dirname(__file__), "../assets")
    image_path = os.path.join(resource_dir, image)
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded
