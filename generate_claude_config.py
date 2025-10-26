#!/usr/bin/env python3
"""
Generate portable Claude Desktop configuration
"""
import json
from config import Config

def main():
    """Generate portable Claude Desktop config with correct paths"""
    print("Generating portable Claude Desktop configuration...")
    
    # Setup project structure and generate config
    config_path = Config.setup_project_structure()
    
    # Validate paths
    issues = Config.validate_paths()
    if issues:
        print("\nPath validation issues found:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nNote: Some issues are expected if you haven't downloaded the dataset yet.")
    else:
        print("✅ All paths validated successfully!")
    
    # Display the generated config
    claude_config = Config.generate_claude_config()
    print(f"\n📁 Project root: {Config.get_project_root()}")
    print(f"📄 Main script: {Config.get_main_py_path()}")
    print(f"📊 Data directory: {Config.DATA_DIR}")
    print(f"📈 CSV path: {Config.get_csv_path()}")
    print(f"🗄️  SQLite path: {Config.DATABASE_SQLITE_PATH}")
    
    print(f"\n✅ Generated Claude config saved to: {config_path}")
    print("\nTo use this config:")
    print("1. Copy the contents of claude_mcp_config_generated.json")
    print("2. Add it to your Claude Desktop configuration file:")
    print("   - Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
    print("   - macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("   - Linux: ~/.config/claude/claude_desktop_config.json")

if __name__ == "__main__":
    main()