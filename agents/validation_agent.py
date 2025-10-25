from models.schemas import ValidationResult
from database.kaggle_connector import KaggleConnector
import re

class ValidationAgent:
    def __init__(self, db_connector: KaggleConnector):
        self.db_connector = db_connector
    
    async def validate_query(self, query: str) -> ValidationResult:
        """Validate SQL query for safety and sanity"""
        
        issues = []
        
        # Safety checks
        if self._has_dangerous_operations(query):
            issues.append("Query contains dangerous operations (DELETE, UPDATE, DROP, etc.)")
        
        # Syntax validation by attempting to explain/run
        try:
            # Create a sample query without conflicting LIMIT clauses
            sample_query = query
            if "LIMIT" in query.upper():
                # Replace existing LIMIT with a smaller one for sampling
                sample_query = re.sub(r'\s+LIMIT\s+\d+', ' LIMIT 5', query, flags=re.IGNORECASE)
            else:
                sample_query = query + " LIMIT 5"
                
            sample_data = await self.db_connector.execute_query(sample_query)
            row_count = await self._get_query_row_count(query)
            
            if row_count == 0:
                issues.append("Query returns 0 rows - check criteria")
            elif row_count > 10000:
                issues.append(f"Query returns large number of rows: {row_count}")
                
        except Exception as e:
            issues.append(f"Query execution failed: {str(e)}")
            sample_data = []
            row_count = 0
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            sample_data=sample_data,
            row_count=row_count
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
            # Remove LIMIT clause for counting
            count_base_query = re.sub(r'\s+LIMIT\s+\d+', '', query, flags=re.IGNORECASE)
            count_query = f"SELECT COUNT(*) as count FROM ({count_base_query})"
            result = await self.db_connector.execute_query(count_query)
            return result[0]["count"] if result else 0
        except:
            return 0