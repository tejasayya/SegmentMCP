#!/usr/bin/env python3
"""
Direct test of the demo server functionality
"""
import asyncio
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from demo_server import DemoSegmentationServer

async def test_demo_server():
    """Test the demo server directly"""
    print("Testing Demo Segmentation Server...")
    
    # Initialize server
    server = DemoSegmentationServer()
    await server.initialize()
    
    # Test queries
    test_queries = [
        "Customers who have a housing loan and balance over 1000",
        "Married customers with age over 30", 
        "Customers with housing loan",
        "Customers with balance over 5000"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Testing query: {query}")
        print('='*60)
        
        try:
            result = await server.create_segment_demo(query)
            print("Result:")
            print(result)
        except Exception as e:
            print(f"Error: {e}")
    
    # Test schema
    print(f"\n{'='*60}")
    print("Testing database schema...")
    print('='*60)
    
    try:
        schema = await server.get_database_schema()
        print("Schema (first 500 chars):")
        print(schema[:500] + "..." if len(schema) > 500 else schema)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_demo_server())