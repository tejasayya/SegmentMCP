import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-4"
    
    # Kaggle Configuration
    KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME")
    KAGGLE_KEY = os.getenv("KAGGLE_KEY")
    KAGGLE_DATASET = "dharmik34/bank-term-deposit-subscription"
    
    # Database
    DATABASE_PATH = "data/bank_deposit.csv"
    
    # Agent Settings
    MAX_QUERY_ROWS = 1000
    VALIDATION_SAMPLE_SIZE = 10