#!/usr/bin/env python3
"""
HTTP wrapper for the demo MCP server
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import json
import asyncio
import uvicorn

app = FastAPI(title="Demo Segmentation MCP HTTP Wrapper", version="1.0.0")

class SegmentRequest(BaseModel):
    query: str

class SegmentResponse(BaseModel):
    result: dict

# Global process handle
mcp_process = None

async def send_mcp_request(method: str, params: dict = None):
    """Send request to MCP server via stdio"""
    global mcp_process
    
    if not mcp_process:
        # Start MCP server
        mcp_process = subprocess.Popen(
            ["python", "demo_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Initialize the server
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "demo-http-wrapper", "version": "1.0.0"}
            }
        }
        
        mcp_process.stdin.write(json.dumps(init_request) + "\n")
        mcp_process.stdin.flush()
        
        # Read initialize response
        response = mcp_process.stdout.readline()
        
        # Send initialized notification
        initialized = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        mcp_process.stdin.write(json.dumps(initialized) + "\n")
        mcp_process.stdin.flush()
    
    # Send the actual request
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": method,
        "params": params or {}
    }
    
    mcp_process.stdin.write(json.dumps(request) + "\n")
    mcp_process.stdin.flush()
    
    # Read response
    response_line = mcp_process.stdout.readline()
    try:
        return json.loads(response_line.strip())
    except json.JSONDecodeError:
        return {"error": "Invalid response from MCP server", "raw": response_line}

@app.post("/create-segment", response_model=SegmentResponse)
async def create_segment(request: SegmentRequest):
    """Create a customer segment from natural language (Demo Mode)"""
    try:
        response = await send_mcp_request("tools/call", {
            "name": "create_segment",
            "arguments": {
                "natural_language_query": request.query
            }
        })
        return SegmentResponse(result=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools")
async def list_tools():
    """List available MCP tools"""
    try:
        response = await send_mcp_request("tools/list")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schema")
async def get_schema():
    """Get database schema"""
    try:
        response = await send_mcp_request("tools/call", {
            "name": "get_database_schema",
            "arguments": {}
        })
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint with usage instructions"""
    return {
        "message": "Demo Segmentation MCP Server HTTP Wrapper",
        "endpoints": {
            "POST /create-segment": "Create customer segment from natural language",
            "GET /tools": "List available tools", 
            "GET /schema": "Get database schema",
            "GET /docs": "API documentation"
        },
        "demo_mode": True,
        "sample_queries": [
            "Customers who have a housing loan and balance over 1000",
            "Married customers with age over 30",
            "Customers with housing loan",
            "Customers with balance over 5000"
        ]
    }

if __name__ == "__main__":
    print("Starting Demo HTTP wrapper for MCP server...")
    print("Available endpoints:")
    print("  POST /create-segment - Create customer segment (Demo Mode)")
    print("  GET /tools - List available tools")
    print("  GET /schema - Get database schema")
    print("  GET / - Usage instructions")
    print("\nServer will run on http://localhost:8001")
    print("API docs available at http://localhost:8001/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)