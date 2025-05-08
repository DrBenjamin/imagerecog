### `src/server/get_static_image.py`
### MCP server prompt
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
from typing import Any
from . import mcp

@mcp.prompt()
def review_code(code: str) -> list[dict[str, Any]]:
    """Reviewing code and returning a summary."""
    return [
        {
            "role": "assistant",
            "content": f"Please review the following code:\n\n{code}"
        }
    ]
