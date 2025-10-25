from models.schemas import QueryResult, SegmentCriteria, DataMapping
from openai import OpenAI
import re

class QueryGeneratorAgent:
    def __init__(self, openai_api_key: str, db_connector):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = "gpt-3.5-turbo"  # Use a model that's available with most API keys
        self.db_connector = db_connector
    
    async def generate_optimized_query(self, criteria: SegmentCriteria, mapping: DataMapping) -> QueryResult:
        """Generate optimized SQL query from mapped criteria"""
        
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
        4. Return only the SQL query, no explanations
        5. Use WHERE clause with proper conditions
        6. Select all columns: SELECT *
        
        Example: 
        Input: field "age" > 30 AND field "housing" = "yes"
        Output: SELECT * FROM bank_customers WHERE age > 30 AND housing = 'yes'
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            sql_query = response.choices[0].message.content.strip()
            # Clean up the query
            sql_query = re.sub(r'```sql|```', '', sql_query).strip()
            
            # Validate and optimize the query
            optimized_query = await self._optimize_query(sql_query)
            
            return QueryResult(
                sql_query=optimized_query,
                optimized=True,
                estimated_rows=await self._estimate_rows(optimized_query),
                tables_used=["bank_customers"]
            )
            
        except Exception as e:
            raise Exception(f"Query generation failed: {str(e)}")
    
    async def _optimize_query(self, query: str) -> str:
        """Apply basic query optimizations"""
        # Add LIMIT for safety in initial queries
        if "LIMIT" not in query.upper():
            query += " LIMIT 1000"
        return query
    
    async def _estimate_rows(self, query: str) -> int:
        """Estimate number of rows the query will return"""
        try:
            # Remove LIMIT for count estimation
            count_query = query.upper().replace("LIMIT 1000", "")
            count_query = f"SELECT COUNT(*) as count FROM ({count_query})"
            
            result = await self.db_connector.execute_query(count_query)
            return result[0]["count"] if result else 0
        except:
            return 0  # Return 0 if estimation fails