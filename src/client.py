### `src/client.py`
### MCP client for Streamlit app
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
from typing import Optional, Dict
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.sse import sse_client


class MCPClient:
    def __init__(self):
        self.primary_session: Optional[ClientSession] = None
        self.remote_sessions: Dict[str, ClientSession] = {}
        self.exit_stack = AsyncExitStack()
        
    async def connect_to_sse_server(self, server_url: str, is_primary: bool = True):
        """Connecting to an MCP server running with SSE transport
        
        Args:
            server_url: The URL of the SSE server to connect to
            is_primary: If True, this connection becomes the primary session (default)
                        If False, adds this as a remote session with server_url as the key
        """
        # Storing the context managers so they stay alive
        streams_context = sse_client(url=server_url)
        streams = await streams_context.__aenter__()

        session_context = ClientSession(*streams)
        session: ClientSession = await session_context.__aenter__()

        # Initializing
        try:
            await session.initialize()
            print(f"Initialized SSE client and connected to {server_url}.")
        except Exception as e:
            print(f"Failed to initialize SSE client for {server_url}: {e}")
            await session_context.__aexit__(None, None, None)
            await streams_context.__aexit__(None, None, None)
            return
            
        # Store the contexts to keep them alive
        if is_primary:
            self._streams_context = streams_context
            self._session_context = session_context
            self.primary_session = session
            self.session = self.primary_session  # For backward compatibility
        else:
            # Store these in dicts keyed by server_url
            key = server_url
            self.remote_sessions[key] = session
            # Also store the context managers (not strictly necessary but good for cleanup)
            if not hasattr(self, '_remote_streams_contexts'):
                self._remote_streams_contexts = {}
            if not hasattr(self, '_remote_session_contexts'):
                self._remote_session_contexts = {}
            self._remote_streams_contexts[key] = streams_context
            self._remote_session_contexts[key] = session_context

        # Listing available tools to verify connection
        try:
            tools_list = ", ".join(tool.name for tool in (await session.list_tools()).tools)
            print(f"\n\nTools available on {server_url}:", tools_list)
            print(f"\nPrompts available on {server_url}:",
                  ", ".join(prompt.name for prompt in (await session.list_prompts()).prompts))
            print(f"\nResources available on {server_url}:",
                  ", ".join(resource.name for resource in (await session.list_resources()).resources))
            print(f"\nResource Templates available on {server_url}:",
                  ", ".join(resource.name for resource in (await session.list_resource_templates()).resourceTemplates))
            return tools_list
        except Exception as e:
            print(f"{e}")
            return ""