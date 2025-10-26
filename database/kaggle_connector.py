import pandas as pd
import os
import kaggle
from sqlalchemy import create_engine, text
import sqlite3
from typing import List, Dict, Any
import asyncio

class KaggleConnector:
    def __init__(self, dataset_name: str):
        from config import Config
        self.dataset_name = dataset_name
        self.csv_path = str(Config.get_csv_path())  # Use centralized path detection
        self.db_path = str(Config.DATABASE_SQLITE_PATH)  # Use centralized SQLite path
        self.engine = None
        self.df = None
        
    async def initialize(self):
        """Download and setup the Kaggle dataset"""
        from config import Config
        
        if not os.path.exists(self.csv_path):
            # Ensure data directory exists using Config
            Config.DATA_DIR.mkdir(exist_ok=True)
            print(f"Downloading dataset {self.dataset_name}...")
            kaggle.api.dataset_download_files(
                self.dataset_name, 
                path=str(Config.DATA_DIR), 
                unzip=True
            )
            # Update csv_path after download in case filename differs
            self.csv_path = str(Config.get_csv_path())
        
        # Load data with semicolon delimiter
        self.df = pd.read_csv(self.csv_path, delimiter=';')
        print(f"Dataset loaded with {len(self.df)} rows and {len(self.df.columns)} columns")
        print("Columns:", self.df.columns.tolist())
        
        # Create SQLite database for querying
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        self.df.to_sql('bank_customers', self.engine, if_exists='replace', index=False)
        
        return self
    
    def get_schema(self) -> Dict[str, Any]:
        """Get database schema information"""
        if self.df is None:
            raise ValueError("Database not initialized")
        
        schema_info = {
            "table_name": "bank_customers",
            "columns": {},
            "sample_data": self.df.head(3).to_dict('records')
        }
        
        for column in self.df.columns:
            schema_info["columns"][column] = {
                "dtype": str(self.df[column].dtype),
                "unique_values": self.df[column].nunique(),
                "sample_values": self.df[column].dropna().head(3).tolist()
            }
        
        return schema_info
    
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                columns = result.keys()
                rows = result.fetchall()
                
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
    
    async def get_sample_data(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get sample data for validation"""
        return await self.execute_query(f"SELECT * FROM bank_customers LIMIT {limit}")