#!/usr/bin/env python3
"""
Configuration usage validation script
Checks that all config values are actually used in the codebase
"""
import ast
import os
from pathlib import Path
from config import Config

class ConfigUsageValidator:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_attributes = self._get_config_attributes()
        self.usage_map = {}
        
    def _get_config_attributes(self):
        """Get all configuration attributes from Config class"""
        attributes = []
        for attr in dir(Config):
            if not attr.startswith('_') and not callable(getattr(Config, attr)):
                # Skip methods and private attributes
                if attr not in ['PROJECT_ROOT', 'DATA_DIR', 'DATABASE_CSV_PATH', 'DATABASE_PATH', 'DATABASE_SQLITE_PATH']:
                    attributes.append(attr)
        return attributes
    
    def scan_file_for_config_usage(self, file_path):
        """Scan a Python file for config usage"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for Config.ATTRIBUTE_NAME patterns
            for attr in self.config_attributes:
                # Convert attribute name to config key format
                config_key = attr.lower().replace('_', '_')
                
                patterns = [
                    f"Config.{attr}",
                    f"Config().{attr}",
                    f"self.config['{config_key}']",
                    f"config['{config_key}']",
                    f"self.config[\"{config_key}\"]",
                    f"config[\"{config_key}\"]",
                    # Common config access patterns
                    f"self.config['model']",
                    f"self.config['temperature']", 
                    f"self.config['max_tokens']",
                    f"self.config['timeout']",
                    f"self.config['default_limit']",
                    f"self.config['sample_size']",
                    f"self.config['max_safe_rows']",
                    f"self.config['warning_threshold']"
                ]
                
                for pattern in patterns:
                    if pattern in content:
                        if attr not in self.usage_map:
                            self.usage_map[attr] = []
                        self.usage_map[attr].append({
                            'file': str(file_path.relative_to(self.project_root)),
                            'pattern': pattern
                        })
                        
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
    
    def scan_project(self):
        """Scan entire project for config usage"""
        python_files = []
        
        # Scan main directory
        for file_path in self.project_root.glob("*.py"):
            python_files.append(file_path)
            
        # Scan subdirectories
        for subdir in ['agents', 'database', 'models']:
            subdir_path = self.project_root / subdir
            if subdir_path.exists():
                for file_path in subdir_path.glob("*.py"):
                    python_files.append(file_path)
        
        for file_path in python_files:
            self.scan_file_for_config_usage(file_path)
    
    def generate_report(self):
        """Generate usage report"""
        print("🔍 Configuration Usage Report")
        print("=" * 50)
        
        used_configs = set(self.usage_map.keys())
        all_configs = set(self.config_attributes)
        unused_configs = all_configs - used_configs
        
        print(f"\n📊 Summary:")
        print(f"  Total config values: {len(all_configs)}")
        print(f"  Used config values: {len(used_configs)}")
        print(f"  Unused config values: {len(unused_configs)}")
        
        if used_configs:
            print(f"\n✅ Used Configuration Values:")
            for attr in sorted(used_configs):
                print(f"  - {attr}")
                for usage in self.usage_map[attr]:
                    print(f"    └─ {usage['file']}: {usage['pattern']}")
        
        if unused_configs:
            print(f"\n⚠️  Unused Configuration Values:")
            for attr in sorted(unused_configs):
                value = getattr(Config, attr)
                print(f"  - {attr} = {value}")
        
        return {
            'used': list(used_configs),
            'unused': list(unused_configs),
            'usage_details': self.usage_map
        }

def test_config_values():
    """Test that all config values are valid"""
    print("\n🧪 Testing Configuration Values...")
    
    validation = Config.validate_config()
    
    if validation["issues"]:
        print("❌ Configuration Issues:")
        for issue in validation["issues"]:
            print(f"  - {issue}")
    else:
        print("✅ No configuration issues found")
        
    if validation["warnings"]:
        print("⚠️  Configuration Warnings:")
        for warning in validation["warnings"]:
            print(f"  - {warning}")
    
    return validation

def test_agent_configs():
    """Test agent-specific configurations"""
    print("\n🤖 Testing Agent Configurations...")
    
    agents = ["intent_parser", "query_generator", "validation", "activation"]
    
    for agent in agents:
        try:
            config = Config.get_agent_config(agent)
            print(f"✅ {agent}: {len(config)} config values")
            
            # Show key config values
            key_values = []
            if 'model' in config:
                key_values.append(f"model={config['model']}")
            if 'timeout' in config:
                key_values.append(f"timeout={config['timeout']}s")
            if 'temperature' in config:
                key_values.append(f"temp={config['temperature']}")
                
            if key_values:
                print(f"    └─ {', '.join(key_values)}")
                
        except Exception as e:
            print(f"❌ {agent}: {e}")

def main():
    """Run configuration validation"""
    print("🚀 Configuration Usage Validation")
    print("=" * 50)
    
    # Test config values
    test_config_values()
    
    # Test agent configs
    test_agent_configs()
    
    # Scan for usage
    validator = ConfigUsageValidator()
    validator.scan_project()
    report = validator.generate_report()
    
    # Recommendations
    if report['unused']:
        print(f"\n💡 Recommendations:")
        print("  Consider removing unused config values or implementing their usage")
        print("  This will keep the configuration clean and maintainable")
    
    print(f"\n✅ Configuration validation complete!")

if __name__ == "__main__":
    main()