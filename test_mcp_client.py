#!/usr/bin/env python3
"""
Simple MCP client to test the segmentation server
"""
import json
import subprocess
import asyncio

def send_jsonrpc_request(method, params=None):
    """Send a JSON-RPC request to the MCP server"""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    return json.dumps(request)

def test_server():
    """Test the MCP server with sample requests"""
    
    # Start the server process
    process = subprocess.Popen(
        ["python", "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Initialize the server
        init_request = send_jsonrpc_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        })
        
        print("Sending initialize request:")
        print(init_request)
        
        process.stdin.write(init_request + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print("Initialize response:", response.strip())
        
        # Send initialized notification
        initialized = send_jsonrpc_request("notifications/initialized")
        process.stdin.write(initialized + "\n")
        process.stdin.flush()
        
        # List available tools
        list_tools_request = send_jsonrpc_request("tools/list")
        print("\nSending list tools request:")
        print(list_tools_request)
        
        process.stdin.write(list_tools_request + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        print("List tools response:", response.strip())
        
        # Test create_segment tool
        segment_request = send_jsonrpc_request("tools/call", {
            "name": "create_segment",
            "arguments": {
                "natural_language_query": "Customers who have a housing loan and balance over 1000"
            }
        })
        
        print("\nSending create segment request:")
        print(segment_request)
        
        process.stdin.write(segment_request + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        print("Create segment response:", response.strip())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        process.terminate()

if __name__ == "__main__":
    test_server()