# Copilot Instructions for imagerecog

Dearest Copilot,
this project is a is (or will be in some later iterations) Agent AI app utilizing
MCP (Model Context Protocol) tools. The agent system uses the
[Agent Development Kit](https://google.github.io/adk-docs/) which is a
Python first approach. The backend is a Streamlit app that serves as a client to
the MCP server tools.

Angular mobile app is also included which utilizes the Streamlit client application
(as iframe embedded).

When generating code snippets or explanations, please follow these guidelines:

1. Output always in Markdown.
2. When referring to a file in this repo, link using `#file:<relative_path>`.
   - Angular mobile app: [mobile/src/app/app.components.ts](#file:mobile/src/app/app.components.ts)
   - Streamlit client app: [mobile/app.py](#file:mobile/app.py)
   - MCPClient class: [mobile/src/client.py](#file:mobile/src/client.py)
   - MCP server [mobile/src/server.py](#file:mobile/src/server.py)

3. Code‑block format for changes or new files:
    ````python
    // filepath: #file:<relative_path>
    # ...existing code...
    def my_new_function(...):
        ...
    # ...existing code...
    ````

4. Adhere to PEP 8:
   - 4‑space indentation, snake_case names
   - Imports at the top of the file
   - Docstrings in Google or NumPy style

5. Preserve existing patterns:
   - Use `@st.cache_resource` for expensive initializations
   - Store and retrieve state via `st.session_state.get("key", default)`

6. File I/O:
   - Use `os.path.join(...)` and `os.makedirs(..., exist_ok=True)`
   - Handle missing directories before writing files

7. Error handling & logging:
   - Import and configure `logger = logging.getLogger(__name__)`
   - Raise clear exceptions on invalid inputs

8. Testing:
    - Add or update tests under `tests/`
    - Use `pytest` fixtures to mock `st.session_state`