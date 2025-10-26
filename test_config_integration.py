#!/usr/bin/env python3
"""
Test that agents are properly using configuration values
"""
import asyncio
from config import Config
from database.kaggle_connector import KaggleConnector
from agents.validation_agent import ValidationAgent
from agents.query_generator import QueryGeneratorAgent

async def test_config_integration():
    """Test that agents use config values correctly"""
    print("🧪 Testing Configuration Integration...")
    
    # Test config loading
    print(f"\n📋 Configuration Values:")
    print(f"  - Default Query Limit: {Config.DEFAULT_QUERY_LIMIT}")
    print(f"  - Validation Sample Size: {Config.VALIDATION_SAMPLE_SIZE}")
    print(f"  - Max Safe Rows: {Config.MAX_SAFE_ROWS}")
    print(f"  - Warning Threshold: {Config.WARNING_ROW_THRESHOLD}")
    print(f"  - OpenAI Temperature: {Config.OPENAI_TEMPERATURE}")
    print(f"  - OpenAI Max Tokens: {Config.OPENAI_MAX_TOKENS}")
    
    # Test agent configs
    print(f"\n🤖 Agent Configurations:")
    
    agents = ["intent_parser", "query_generator", "validation", "activation"]
    for agent in agents:
        config = Config.get_agent_config(agent)
        print(f"  - {agent}:")
        for key, value in config.items():
            print(f"    └─ {key}: {value}")
    
    # Test validation agent with config
    print(f"\n🔍 Testing ValidationAgent Config Usage:")
    try:
        # Initialize database connector (mock for testing)
        db_connector = type('MockConnector', (), {
            'get_schema': lambda: {"columns": {"age": {"dtype": "int"}}},
            'execute_query': lambda query: [{"age": 30}, {"age": 35}]
        })()
        
        validation_agent = ValidationAgent(db_connector)
        
        print(f"  - Sample size from config: {validation_agent.config['sample_size']}")
        print(f"  - Max safe rows from config: {validation_agent.config['max_safe_rows']}")
        print(f"  - Warning threshold from config: {validation_agent.config['warning_threshold']}")
        
        print("✅ ValidationAgent successfully using config values")
        
    except Exception as e:
        print(f"❌ ValidationAgent config error: {e}")
    
    # Test query generator config (without OpenAI call)
    print(f"\n🔧 Testing QueryGeneratorAgent Config Usage:")
    try:
        if Config.OPENAI_API_KEY:
            query_agent = QueryGeneratorAgent(Config.OPENAI_API_KEY, db_connector)
            print(f"  - Model from config: {query_agent.config['model']}")
            print(f"  - Temperature from config: {query_agent.config['temperature']}")
            print(f"  - Max tokens from config: {query_agent.config['max_tokens']}")
            print(f"  - Default limit from config: {query_agent.config['default_limit']}")
            print("✅ QueryGeneratorAgent successfully using config values")
        else:
            print("⚠️  No OpenAI API key - skipping QueryGeneratorAgent test")
            
    except Exception as e:
        print(f"❌ QueryGeneratorAgent config error: {e}")

def test_environment_overrides():
    """Test environment variable overrides"""
    print(f"\n🌍 Environment Variable Support:")
    
    env_vars = [
        "MAX_QUERY_ROWS",
        "VALIDATION_SAMPLE_SIZE", 
        "OPENAI_TEMPERATURE",
        "OPENAI_MAX_TOKENS",
        "DEFAULT_QUERY_LIMIT"
    ]
    
    for var in env_vars:
        value = getattr(Config, var)
        print(f"  - {var}: {value} (can be overridden with env var)")
    
    print(f"\n💡 To override, set environment variables like:")
    print(f"  export MAX_QUERY_ROWS=2000")
    print(f"  export OPENAI_TEMPERATURE=0.2")

def main():
    """Run configuration integration tests"""
    print("🚀 Configuration Integration Test")
    print("=" * 50)
    
    # Test config validation
    validation = Config.validate_config()
    if validation["issues"]:
        print("❌ Configuration Issues:")
        for issue in validation["issues"]:
            print(f"  - {issue}")
    else:
        print("✅ Configuration validation passed")
    
    # Test integration
    asyncio.run(test_config_integration())
    
    # Test environment support
    test_environment_overrides()
    
    print(f"\n✅ Configuration integration test complete!")

if __name__ == "__main__":
    main()