### `test_remote_mcp.py`
### Test script for remote MCP connections
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
import asyncio
import os
import sys
from src.client import MCPClient

# Test configuration
PRIMARY_SERVER = "http://localhost:8080/sse"
REMOTE_SERVER = "http://localhost:8081/sse"  # Adjust to your test setup

async def test_remote_connections():
    """Test connecting to multiple MCP servers and tool discovery"""
    # Initialize client
    client = MCPClient()
    
    # Connect to primary server
    print(f"Connecting to primary server: {PRIMARY_SERVER}")
    await client.connect_to_sse_server(server_url=PRIMARY_SERVER, is_primary=True)
    
    if not client.primary_session:
        print("Failed to connect to primary server")
        return False
    
    # Connect to remote server
    print(f"\nConnecting to remote server: {REMOTE_SERVER}")
    tools = await client.connect_to_sse_server(server_url=REMOTE_SERVER, is_primary=False)
    
    if REMOTE_SERVER not in client.remote_sessions:
        print("Failed to connect to remote server")
        return False
    
    # Verify tool discovery
    print("\nVerifying tool discovery:")
    if not tools:
        print("No tools discovered on remote server")
    else:
        print(f"Tools discovered on remote server: {tools}")
    
    return True

if __name__ == "__main__":
    print("\n=== Testing Remote MCP Connections ===\n")
    
    try:
        success = asyncio.run(test_remote_connections())
        if success:
            print("\n✅ Remote MCP connection test passed!")
            sys.exit(0)
        else:
            print("\n❌ Remote MCP connection test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        sys.exit(1)