from models.schemas import QueryResult, SegmentCriteria, DataMapping
from openai import OpenAI
import re

class QueryGeneratorAgent:
    def __init__(self, openai_api_key: str, db_connector, model: str = None):
        self.client = OpenAI(api_key=openai_api_key)
        # Import here to avoid circular imports
        from config import Config
        self.config = Config.get_agent_config("query_generator")
        self.model = model or self.config["model"]
        self.db_connector = db_connector
    
    async def generate_optimized_query(self, criteria: SegmentCriteria, mapping: DataMapping) -> QueryResult:
        """Generate optimized SQL query from mapped criteria"""
        import time
        start_time = time.time()
        
        schema_info = self.db_connector.get_schema()
        columns_info = "\n".join([f"- {col}: {info['dtype']}" for col, info in schema_info["columns"].items()])
        
        prompt = f"""
        Generate an optimized SQL query for the following segment criteria:
        
        Criteria: {criteria.dict()}
        Field Mappings: {mapping.field_mappings}
        
        Database Schema:
        Table: bank_customers
        Columns:
        {columns_info}
        
        Rules:
        1. Use exact column names from the schema
        2. Optimize for performance
        3. Handle data types correctly (strings need quotes, numbers don't)
        4. Return only the SQL query, no explanations, no semicolons
        5. Use WHERE clause with proper conditions
        6. Select all columns: SELECT *
        7. Do NOT include semicolons or multiple statements
        
        Example: 
        Input: field "age" > 30 AND field "housing" = "yes"
        Output: SELECT * FROM bank_customers WHERE age > 30 AND housing = 'yes'
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"],
                timeout=self.config["timeout"]
            )
            
            sql_query = response.choices[0].message.content.strip()
            # Clean up the query - remove code blocks and semicolons
            sql_query = re.sub(r'```sql|```', '', sql_query).strip()
            sql_query = sql_query.rstrip(';').strip()
            
            # Validate and optimize the query
            optimized_query = await self._optimize_query(sql_query)
            
            processing_time = int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0
            
            return QueryResult(
                sql_query=optimized_query,
                optimized=True,
                estimated_rows=await self._estimate_rows(optimized_query),
                tables_used=["bank_customers"],
                processing_time_ms=processing_time,
                optimization_notes=["Added LIMIT clause for safety", "Cleaned SQL formatting"]
            )
            
        except Exception as e:
            raise Exception(f"Query generation failed: {str(e)}")
    
    async def _optimize_query(self, query: str) -> str:
        """Apply basic query optimizations"""
        # Clean up the query first - remove semicolons and extra whitespace
        query = query.strip().rstrip(';').strip()
        
        # Add LIMIT for safety in initial queries using config value
        if "LIMIT" not in query.upper():
            query += f" LIMIT {self.config['default_limit']}"
        return query
    
    async def _estimate_rows(self, query: str) -> int:
        """Estimate number of rows the query will return"""
        try:
            # Remove LIMIT for count estimation using config value
            limit_clause = f"LIMIT {self.config['default_limit']}"
            count_query = query.upper().replace(limit_clause.upper(), "")
            count_query = f"SELECT COUNT(*) as count FROM ({count_query})"
            
            result = await self.db_connector.execute_query(count_query)
            return result[0]["count"] if result else 0
        except:
            return 0  # Return 0 if estimation fails