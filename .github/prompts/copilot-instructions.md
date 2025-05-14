# Copilot Instructions for BenBox

Dearest Copilot,
this project is an Agent AI app utilizing
MCP (Model Context Protocol) tools. The agent system uses the
[Agent Development Kit](https://google.github.io/adk-docs/) which is a
Python first approach. The backend is a Streamlit app that serves as a client to
the MCP server tools. It has an inbuild RAG (retrieval-augmented generation)
system to store and retrieve documents as vectors for similarity search.

An Angular mobile app is also included which utilizes the Streamlit client 
application (as iframe embedded).

When generating code snippets or explanations, please follow these guidelines:

1. Output always in Markdown.

2. When referring to a file in this repo, link using `#file:<relative_path>`.
   - Angular mobile app: [src/app/app.components.ts](#file:src/app/app.components.ts)
   - Streamlit client app: [app.py](#file:app.py)
   - MCPClient class: [src/client.py](#file:src/client.py)
   - MCP server [src/server.py](#file:src/server.py)
   - MCP server tools: [src/server/*](#file:src/server/*)

3. Code‑block format for changes or new files:
    ````python
    // filepath: #file:<relative_path>
    # ...existing code...
    def my_new_function(...):
        ...
    # ...existing code...
    ````

4. Comments format:
   - Use `#` for comments
   - Start comments with 'Setting', 'Creating', 'Adding', 'Updating' etc.
     (always the gerund form) and before it add an empty line if not the
     beginning of a code block or function.

5. Adhere to PEP 8:
   - 4‑space indentation, snake_case names
   - Imports at the top of the file
   - Docstrings in Google or NumPy style

6. Preserve existing patterns:
   - Use `@st.cache_resource` for expensive initializations
   - Store and retrieve state via `st.session_state.get("key", default)`

7. File I/O:
   - Use `os.path.join(...)` and `os.makedirs(..., exist_ok=True)`
   - Handle missing directories before writing files

8. Error handling & logging:
   - Import and configure `logger = logging.getLogger(__name__)`
   - Raise clear exceptions on invalid inputs

9. Testing:
    - Add or update tests under `tests/`
    - Use `pytest` fixtures to mock `st.session_state`

10. Business case:
   - The app is designed to be a user-friendly interface for healthcare service
       providers in Germany to learn about HIS (Hospital Information System) or
       other healthcare software. It provides a platform for users to ask,
      learn, and understand the software, with a focus on the German healthcare system.
   - Different media formats are supported, including text, images, and videos.
   - It is not a medical advice tool and should not be used for medical diagnosis or
       treatment.