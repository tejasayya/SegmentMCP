#!/usr/bin/env python3
"""
Verify that all required dependencies are installed and can be imported
"""

def test_import(module_name, description):
    """Test importing a module"""
    try:
        __import__(module_name)
        print(f"✅ {description}")
        return True
    except ImportError as e:
        print(f"❌ {description} - {e}")
        return False

def main():
    """Test all required imports"""
    print("🔍 Verifying Dependencies...")
    print("=" * 50)
    
    success_count = 0
    total_count = 0
    
    # Core dependencies
    dependencies = [
        ("mcp.server", "MCP Server Framework"),
        ("openai", "OpenAI API Client"),
        ("pydantic", "Pydantic Data Validation"),
        ("pandas", "Pandas Data Processing"),
        ("numpy", "NumPy Numerical Computing"),
        ("sqlalchemy", "SQLAlchemy Database ORM"),
        ("kaggle", "Kaggle API Client"),
        ("httpx", "HTTPX HTTP Client"),
        ("fastapi", "FastAPI Web Framework"),
        ("uvicorn", "Uvicorn ASGI Server"),
        ("dotenv", "Python Dotenv"),
        ("requests", "Requests HTTP Library"),
        ("asyncio", "Asyncio Async Support"),
        ("typing_extensions", "Typing Extensions"),
        ("json", "JSON Support (built-in)"),
        ("re", "Regular Expressions (built-in)"),
        ("os", "Operating System Interface (built-in)"),
        ("uuid", "UUID Generation (built-in)"),
        ("sqlite3", "SQLite Database (built-in)"),
        ("subprocess", "Subprocess Management (built-in)"),
        ("sys", "System-specific Parameters (built-in)"),
        ("pathlib", "Path Handling (built-in)"),
        ("enum", "Enumerations (built-in)"),
    ]
    
    for module, description in dependencies:
        if test_import(module, description):
            success_count += 1
        total_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {success_count}/{total_count} dependencies available")
    
    if success_count == total_count:
        print("🎉 All dependencies are properly installed!")
        
        # Test core functionality
        print("\n🧪 Testing Core Functionality...")
        try:
            # Test MCP server creation
            import mcp.server
            server = mcp.server.FastMCP("test")
            print("✅ MCP server creation works")
            
            # Test Pydantic models
            from pydantic import BaseModel
            class TestModel(BaseModel):
                name: str
            test_obj = TestModel(name="test")
            print("✅ Pydantic models work")
            
            # Test pandas
            import pandas as pd
            df = pd.DataFrame({"test": [1, 2, 3]})
            print("✅ Pandas DataFrame creation works")
            
            # Test SQLAlchemy
            from sqlalchemy import create_engine
            engine = create_engine("sqlite:///:memory:")
            print("✅ SQLAlchemy engine creation works")
            
            print("\n🎉 All core functionality tests passed!")
            return True
            
        except Exception as e:
            print(f"❌ Core functionality test failed: {e}")
            return False
    else:
        print("❌ Some dependencies are missing. Please run:")
        print("   pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)