### `src/server/get_static_image.py`
### MCP server resource for serving a static image
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
import os
import base64
import streamlit as st
from . import mcp
import sys
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.snowflake_connector import SnowflakeStageConnector

@mcp.resource(uri="resource://Image.png", name="get_static_image", description="This offers a static image file.", mime_type="image/png")
def get_static_image() -> bytes:
    """Static image file."""

    # Check if Snowflake integration is enabled
    if 'SNOWFLAKE' in st.secrets and st.secrets.get('USE_SNOWFLAKE', 'True').lower() == 'true':
        try:
            # Get the image from Snowflake Stage
            sf_connector = SnowflakeStageConnector()
            encoded = sf_connector.get_base64_from_stage("Image.png")
            return encoded
        except Exception as e:
            print(f"Error retrieving image from Snowflake: {e}")
            # Fall back to local storage if Snowflake fails
            pass
    
    # Fallback to local file system if Snowflake is not configured or fails
    resource_dir = os.path.join(os.path.dirname(__file__), "../assets")
    image_path = os.path.join(resource_dir, "Image.png")
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded
