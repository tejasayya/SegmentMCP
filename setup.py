#!/usr/bin/env python3
import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def setup_kaggle():
    """Setup Kaggle API credentials"""
    kaggle_dir = os.path.expanduser("~/.kaggle")
    os.makedirs(kaggle_dir, exist_ok=True)
    
    # You'll need to place your kaggle.json here
    print("Please ensure your kaggle.json is placed in ~/.kaggle/")

if __name__ == "__main__":
    install_requirements()
    setup_kaggle()
    print("Setup completed! Run 'python main.py' to start the MCP server.")