### `src/server/image_recognition.py`
### MCP server tool for image recognition
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
import streamlit as st
import base64
import io
import json
from PIL import Image as PILImage
from ollama import AsyncClient
from openai import AsyncAzureOpenAI
from . import mcp

@mcp.tool()
async def image_recognition(image_bytes: bytes | str) -> str:
    """Creating an image recognition text and a thumbnail from provided image bytes.
       Returns a JSON string with keys 'description' and 'image_bytes'."""

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

    # Encoding Base64 style the thumbnail for JSON transport
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Generating a description for the image through a locally running model via threadpool
    ollama = st.secrets.get('LLM_LOCAL', "False").lower() == "true"
    if ollama:
        # Calling Ollama API
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
        # Use Azure OpenAI Studio instead of official OpenAI API
        azure_openai_secrets = st.secrets['AZURE_OPENAI']
        client = AsyncAzureOpenAI(
            api_key=azure_openai_secrets['AZURE_OPENAI_API_KEY'],
            azure_endpoint=azure_openai_secrets['AZURE_OPENAI_ENDPOINT'],
            api_version=azure_openai_secrets.get('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
        )
        resp = await client.chat.completions.create(
            model=azure_openai_secrets['AZURE_OPENAI_MODEL'],
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{st.secrets['MCP']['MCP_SYSTEM_PROMPT']}"
                        }
                    ],
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
