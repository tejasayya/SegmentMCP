from models.schemas import ValidationResult
from database.kaggle_connector import KaggleConnector
import re
import time

class ValidationAgent:
    def __init__(self, db_connector: KaggleConnector):
        self.db_connector = db_connector
        # Import here to avoid circular imports
        from config import Config
        self.config = Config.get_agent_config("validation")
    
    async def validate_query(self, query: str) -> ValidationResult:
        """Validate SQL query for safety and sanity"""
        start_time = time.time()
        
        issues = []
        warnings = []
        
        # Safety checks
        if self._has_dangerous_operations(query):
            issues.append("Query contains dangerous operations (DELETE, UPDATE, DROP, etc.)")
        
        # Performance warnings
        if "SELECT *" in query.upper():
            warnings.append("Query uses SELECT * which may impact performance")
        
        # Syntax validation by attempting to explain/run
        try:
            # Clean the query first - remove semicolons and extra whitespace
            clean_query = query.strip().rstrip(';').strip()
            
            # Create a sample query without conflicting LIMIT clauses using config
            sample_query = clean_query
            sample_limit = f" LIMIT {self.config['sample_size']}"
            if "LIMIT" in clean_query.upper():
                # Replace existing LIMIT with a smaller one for sampling
                sample_query = re.sub(r'\s+LIMIT\s+\d+', sample_limit, clean_query, flags=re.IGNORECASE)
            else:
                sample_query = clean_query + sample_limit
                
            sample_data = await self.db_connector.execute_query(sample_query)
            row_count = await self._get_query_row_count(query)
            
            if row_count == 0:
                issues.append("Query returns 0 rows - check criteria")
            elif row_count > self.config["max_safe_rows"]:
                warnings.append(f"Query returns very large number of rows: {row_count} - consider adding more filters")
            elif row_count > self.config["warning_threshold"]:
                warnings.append(f"Query returns large number of rows: {row_count}")
                
        except Exception as e:
            issues.append(f"Query execution failed: {str(e)}")
            sample_data = []
            row_count = 0
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            sample_data=sample_data,
            row_count=row_count,
            processing_time_ms=processing_time
        )
    
    def _has_dangerous_operations(self, query: str) -> bool:
        """Check for dangerous SQL operations"""
        dangerous_patterns = [
            r'\bDELETE\b', r'\bUPDATE\b', r'\bDROP\b', 
            r'\bALTER\b', r'\bINSERT\b', r'\bCREATE\b',
            r'\bTRUNCATE\b'
        ]
        
        query_upper = query.upper()
        return any(re.search(pattern, query_upper) for pattern in dangerous_patterns)
    
    async def _get_query_row_count(self, query: str) -> int:
        """Get the number of rows the query returns"""
        try:
            # Clean the query and remove LIMIT clause for counting
            clean_query = query.strip().rstrip(';').strip()
            count_base_query = re.sub(r'\s+LIMIT\s+\d+', '', clean_query, flags=re.IGNORECASE)
            count_query = f"SELECT COUNT(*) as count FROM ({count_base_query})"
            result = await self.db_connector.execute_query(count_query)
            return result[0]["count"] if result else 0
        except:
            return 0