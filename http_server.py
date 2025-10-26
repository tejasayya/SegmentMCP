#!/usr/bin/env python3
"""
HTTP wrapper for the Segmentation MCP Server
Allows HTTP requests to the MCP functionality
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import uvicorn
from main import SegmentationMCPServer

app = FastAPI(title="Segmentation MCP HTTP API", version="1.0.0")

# Global server instance
segmentation_server = None

class SegmentQuery(BaseModel):
    query: str

class SegmentInfoRequest(BaseModel):
    segment_id: str

@app.on_event("startup")
async def startup_event():
    """Initialize the segmentation server on startup"""
    global segmentation_server
    segmentation_server = SegmentationMCPServer()
    await segmentation_server.initialize()
    print("HTTP server started and segmentation server initialized!")

@app.post("/create-segment")
async def create_segment_endpoint(request: SegmentQuery):
    """
    Create a customer segment from natural language description.
    
    Body: {"query": "Description of desired customer segment in plain English"}
    """
    try:
        result = await segmentation_server.create_segment(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/segment/{segment_id}")
async def get_segment_info_endpoint(segment_id: str):
    """Get information about a created segment"""
    try:
        result = await segmentation_server.get_segment_info(segment_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schema")
async def get_database_schema_endpoint():
    """Get the current database schema information"""
    try:
        result = await segmentation_server.get_database_schema()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Segmentation MCP HTTP API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)