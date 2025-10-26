#!/usr/bin/env python3
"""
Installation and setup script for Segmentation MCP Server
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing requirements"):
        return False
    
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating .env file template...")
    env_template = """# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Kaggle API Configuration  
KAGGLE_USERNAME=your-kaggle-username
KAGGLE_KEY=your-kaggle-key

# Optional: Kaggle Dataset
KAGGLE_DATASET=dharmik34/bank-term-deposit-subscription
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_template)
        print("✅ .env file created successfully")
        print("⚠️  Please edit .env file with your actual API keys")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def test_installation():
    """Test if installation works"""
    print("🧪 Testing installation...")
    
    # Test imports
    try:
        import mcp.server
        import pandas
        import sqlalchemy
        print("✅ Core dependencies imported successfully")
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    # Test demo server initialization
    try:
        print("🔄 Testing demo server initialization...")
        result = subprocess.run([sys.executable, "-c", """
import sys
sys.path.append('.')
from demo_server import DemoSegmentationServer
print('Demo server can be imported successfully')
"""], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Demo server initialization test passed")
        else:
            print(f"❌ Demo server test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Demo server test failed: {e}")
        return False
    
    return True

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 Installation completed successfully!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("1. Edit .env file with your API keys:")
    print("   - Get OpenAI API key from: https://platform.openai.com/api-keys")
    print("   - Get Kaggle credentials from: https://www.kaggle.com/settings/account")
    print("\n2. Test the server:")
    print("   python demo_server.py              # Demo mode (no OpenAI required)")
    print("   python demo_http_wrapper.py        # HTTP API on port 8001")
    print("   python test_demo_direct.py         # Run tests")
    print("\n3. Connect to Claude Desktop:")
    print("   - Add server config to Claude Desktop settings")
    print("   - See README.md for detailed instructions")
    print("\n📚 Documentation:")
    print("   - README.md - Complete setup and usage guide")
    print("   - http://localhost:8001/docs - API documentation (when HTTP wrapper is running)")
    print("\n🆘 Need help?")
    print("   - Check README.md for troubleshooting")
    print("   - Run 'python test_demo_direct.py' to test functionality")

def main():
    """Main installation process"""
    print("🚀 Segmentation MCP Server Installation")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Installation failed during dependency installation")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("❌ Installation failed during .env file creation")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("❌ Installation completed but tests failed")
        print("⚠️  You may need to configure API keys in .env file")
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()