import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Project root directory
    PROJECT_ROOT = Path(__file__).parent.absolute()
    
    # Data directory paths
    DATA_DIR = PROJECT_ROOT / "data"
    
    # LLM Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-4.1"  # Standardized to latest working model
    
    # Agent-specific model overrides (optional)
    INTENT_PARSER_MODEL = os.getenv("INTENT_PARSER_MODEL", "gpt-4.1")
    QUERY_GENERATOR_MODEL = os.getenv("QUERY_GENERATOR_MODEL", "gpt-4.1")
    
    # Model parameters
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    
    # Kaggle Configuration
    KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME")
    KAGGLE_KEY = os.getenv("KAGGLE_KEY")
    KAGGLE_DATASET = "dharmik34/bank-term-deposit-subscription"
    
    # Auto-detect CSV filename (handles different download names)
    @classmethod
    def get_csv_path(cls):
        """Auto-detect the actual CSV filename in data directory"""
        possible_names = [
            "bank-full.csv",
            "bank.csv", 
            "bank_deposit.csv",
            "bank-term-deposit.csv"
        ]
        
        for name in possible_names:
            path = cls.DATA_DIR / name
            if path.exists():
                return path
                
        # Default to expected name if none found
        return cls.DATA_DIR / "bank-full.csv"
    
    # Database paths (cross-platform) - will be set after class definition
    DATABASE_SQLITE_PATH = DATA_DIR / "bank_deposit.db"
    
    # Agent Settings
    MAX_QUERY_ROWS = int(os.getenv("MAX_QUERY_ROWS", "100000"))
    VALIDATION_SAMPLE_SIZE = int(os.getenv("VALIDATION_SAMPLE_SIZE", "5"))
    
    # Query Generation Settings
    DEFAULT_QUERY_LIMIT = int(os.getenv("DEFAULT_QUERY_LIMIT", "100000"))
    QUERY_TIMEOUT_SECONDS = int(os.getenv("QUERY_TIMEOUT_SECONDS", "30"))
    
    # Validation Settings
    MAX_SAFE_ROWS = int(os.getenv("MAX_SAFE_ROWS", "100000"))
    WARNING_ROW_THRESHOLD = int(os.getenv("WARNING_ROW_THRESHOLD", "50000"))
    
    # Performance Settings
    PROCESSING_TIMEOUT_MS = int(os.getenv("PROCESSING_TIMEOUT_MS", "30000"))
    ENABLE_QUERY_OPTIMIZATION = os.getenv("ENABLE_QUERY_OPTIMIZATION", "true").lower() == "true"
    
    # Agent-specific timeouts
    INTENT_PARSER_TIMEOUT = int(os.getenv("INTENT_PARSER_TIMEOUT", "15"))
    QUERY_GENERATOR_TIMEOUT = int(os.getenv("QUERY_GENERATOR_TIMEOUT", "20"))
    VALIDATION_TIMEOUT = int(os.getenv("VALIDATION_TIMEOUT", "10"))
    ACTIVATION_TIMEOUT = int(os.getenv("ACTIVATION_TIMEOUT", "25"))
    
    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def get_project_root(cls):
        """Get absolute project root path (cross-platform)"""
        return cls.PROJECT_ROOT.absolute()
    
    @classmethod
    def get_main_py_path(cls):
        """Get absolute path to main.py for Claude config"""
        return cls.PROJECT_ROOT / "main.py"
    
    @classmethod
    def generate_claude_config(cls):
        """Generate portable Claude Desktop config"""
        return {
            "mcpServers": {
                "segmentation-agent": {
                    "command": "python",
                    "args": ["main.py"],
                    "cwd": str(cls.get_project_root()),
                    "env": {
                        "OPENAI_API_KEY": cls.OPENAI_API_KEY or "your-openai-api-key-here",
                        "KAGGLE_USERNAME": cls.KAGGLE_USERNAME or "your-kaggle-username",
                        "KAGGLE_KEY": cls.KAGGLE_KEY or "your-kaggle-key"
                    }
                }
            }
        }
    
    @classmethod
    def validate_paths(cls):
        """Validate all required paths exist"""
        issues = []
        
        if not cls.get_csv_path().exists():
            issues.append(f"CSV file not found: {cls.get_csv_path()}")
        
        if not cls.DATA_DIR.exists():
            issues.append(f"Data directory not found: {cls.DATA_DIR}")
        
        return issues
    
    @classmethod
    def validate_config(cls):
        """Validate configuration values"""
        issues = []
        warnings = []
        
        # Validate numeric ranges
        if cls.MAX_QUERY_ROWS <= 0:
            issues.append("MAX_QUERY_ROWS must be positive")
        elif cls.MAX_QUERY_ROWS > 1000000:
            warnings.append("MAX_QUERY_ROWS is very large, may impact performance")
            
        if cls.OPENAI_TEMPERATURE < 0 or cls.OPENAI_TEMPERATURE > 2:
            issues.append("OPENAI_TEMPERATURE must be between 0 and 2")
            
        if cls.OPENAI_MAX_TOKENS <= 0 or cls.OPENAI_MAX_TOKENS > 4000:
            issues.append("OPENAI_MAX_TOKENS must be between 1 and 4000")
            
        # Validate API key
        if not cls.OPENAI_API_KEY:
            warnings.append("OPENAI_API_KEY not set - AI features will be disabled")
            
        return {"issues": issues, "warnings": warnings}
    
    @classmethod
    def get_agent_config(cls, agent_name: str):
        """Get configuration for specific agent"""
        base_config = {
            "model": cls.OPENAI_MODEL,
            "temperature": cls.OPENAI_TEMPERATURE,
            "max_tokens": cls.OPENAI_MAX_TOKENS,
            "timeout": cls.PROCESSING_TIMEOUT_MS // 1000
        }
        
        # Agent-specific overrides
        agent_configs = {
            "intent_parser": {
                "model": cls.INTENT_PARSER_MODEL,
                "timeout": cls.INTENT_PARSER_TIMEOUT,
                "temperature": cls.OPENAI_TEMPERATURE
            },
            "query_generator": {
                "model": cls.QUERY_GENERATOR_MODEL,
                "timeout": cls.QUERY_GENERATOR_TIMEOUT,
                "max_query_rows": cls.MAX_QUERY_ROWS,
                "default_limit": cls.DEFAULT_QUERY_LIMIT
            },
            "validation": {
                "sample_size": cls.VALIDATION_SAMPLE_SIZE,
                "timeout": cls.VALIDATION_TIMEOUT,
                "max_safe_rows": cls.MAX_SAFE_ROWS,
                "warning_threshold": cls.WARNING_ROW_THRESHOLD
            },
            "activation": {
                "timeout": cls.ACTIVATION_TIMEOUT,
                "max_query_rows": cls.MAX_QUERY_ROWS
            }
        }
        
        if agent_name in agent_configs:
            base_config.update(agent_configs[agent_name])
            
        return base_config
    
    @classmethod
    def setup_project_structure(cls):
        """Create required directories and generate portable Claude config"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        
        # Validate configuration
        validation = cls.validate_config()
        if validation["issues"]:
            print("⚠️  Configuration issues found:")
            for issue in validation["issues"]:
                print(f"  - {issue}")
        if validation["warnings"]:
            print("⚠️  Configuration warnings:")
            for warning in validation["warnings"]:
                print(f"  - {warning}")
        
        # Generate portable Claude config
        claude_config = cls.generate_claude_config()
        
        config_path = cls.PROJECT_ROOT / "claude_mcp_config_generated.json"
        with open(config_path, 'w') as f:
            json.dump(claude_config, f, indent=2)
        
        print(f"Generated portable Claude config: {config_path}")
        return config_path

# Set dynamic paths after class definition
Config.DATABASE_CSV_PATH = Config.get_csv_path()
Config.DATABASE_PATH = str(Config.DATABASE_CSV_PATH)  # Legacy compatibility