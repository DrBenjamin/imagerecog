from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.sse import sse_client


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_sse_server(self, server_url: str):
        """Connecting to an MCP server running with SSE transport"""
        # Storing the context managers so they stay alive
        self._streams_context = sse_client(url=server_url)
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session: ClientSession = await self._session_context.__aenter__()

        # Initializing
        try:
            await self.session.initialize()
            print("Initialized SSE client and connected.")
        except Exception as e:
            print(f"Failed to initialize SSE client: {e}")
            await self._session_context.__aexit__(None, None, None)
            await self._streams_context.__aexit__(None, None, None)
            return

        # Listing available tools to verify connection
        try:
            print("\n\nTools available:",
                  ", ".join(tool.name for tool in (await self.session.list_tools()).tools))
            print("\nPrompts available:",
                  ", ".join(prompt.name for prompt in (await self.session.list_prompts()).prompts))
            print("\nResources available:",
                  ", ".join(resource.name for resource in (await self.session.list_resources()).resources))
            print("\nResource Templates available:",
                  ", ".join(resource.name for resource in (await self.session.list_resource_templates()).resourceTemplates))
        except Exception as e:
            print(f"{e}")