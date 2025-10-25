#!/usr/bin/env python3
"""
Test the HTTP wrapper with sample requests
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_create_segment():
    """Test creating a customer segment"""
    print("Testing create segment...")
    
    response = requests.post(f"{BASE_URL}/create-segment", json={
        "query": "Customers who have a housing loan and balance over 1000"
    })
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_list_tools():
    """Test listing available tools"""
    print("Testing list tools...")
    
    response = requests.get(f"{BASE_URL}/tools")
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_get_schema():
    """Test getting database schema"""
    print("Testing get schema...")
    
    response = requests.get(f"{BASE_URL}/schema")
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

if __name__ == "__main__":
    print("Testing MCP Server via HTTP wrapper...")
    print("=" * 50)
    
    try:
        test_list_tools()
        test_get_schema()
        test_create_segment()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure http_wrapper.py is running.")
    except Exception as e:
        print(f"Error: {e}")