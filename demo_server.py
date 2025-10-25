#!/usr/bin/env python3
"""
Demo MCP server without OpenAI dependency for testing
"""
import mcp.server
import asyncio
import json
import re

from config import Config
from database.kaggle_connector import KaggleConnector
from agents.data_mapper import DataMapperAgent
from agents.validation_agent import ValidationAgent
from agents.activation_agent import ActivationAgent
from models.schemas import SegmentCriteria

# Create MCP server instance
server = mcp.server.FastMCP("segmentation-demo")

class DemoSegmentationServer:
    def __init__(self):
        self.config = Config()
        self.db_connector = None
        self.agents = {}
        
    async def initialize(self):
        """Initialize all components"""
        print("Initializing Demo Segmentation MCP Server...")
        
        # Initialize database
        self.db_connector = await KaggleConnector(
            self.config.KAGGLE_DATASET
        ).initialize()
        
        # Initialize non-OpenAI agents only
        self.agents["data_mapper"] = DataMapperAgent(self.db_connector)
        self.agents["validation"] = ValidationAgent(self.db_connector)
        self.agents["activation"] = ActivationAgent(self.db_connector)
        
        print("Demo Segmentation MCP Server initialized successfully!")
    
    async def create_segment_demo(self, natural_language_query: str) -> str:
        """Demo version that creates segments with predefined rules"""
        try:
            print(f"Processing demo query: {natural_language_query}")
            
            # Simple rule-based parsing for demo
            conditions = []
            
            if "housing loan" in natural_language_query.lower():
                conditions.append({"field": "housing", "operator": "=", "value": "yes"})
            
            if "balance over" in natural_language_query.lower():
                # Extract number after "over"
                match = re.search(r'over\s+(\d+)', natural_language_query.lower())
                if match:
                    amount = int(match.group(1))
                    conditions.append({"field": "balance", "operator": ">", "value": amount})
            
            if "married" in natural_language_query.lower():
                conditions.append({"field": "marital", "operator": "=", "value": "married"})
                
            if "age over" in natural_language_query.lower() or "age >" in natural_language_query.lower():
                match = re.search(r'age\s+(?:over|>)\s+(\d+)', natural_language_query.lower())
                if match:
                    age = int(match.group(1))
                    conditions.append({"field": "age", "operator": ">", "value": age})
            
            if not conditions:
                # Default demo query
                conditions = [
                    {"field": "housing", "operator": "=", "value": "yes"},
                    {"field": "balance", "operator": ">", "value": 1000}
                ]
            
            # Create criteria
            criteria = SegmentCriteria(
                conditions=conditions,
                logical_operators=["AND"] * (len(conditions) - 1) if len(conditions) > 1 else []
            )
            
            print(f"Demo parsed criteria: {criteria.dict()}")
            
            # Step 2: Data Mapping
            print("Step 2: Data Mapping...")
            mapping_result = await self.agents["data_mapper"].map_criteria_to_schema(criteria)
            print(f"Field mappings: {mapping_result.field_mappings}")
            
            # Step 3: Generate simple SQL query
            print("Step 3: Simple Query Generation...")
            where_clauses = []
            for condition in conditions:
                field = condition["field"]
                operator = condition["operator"]
                value = condition["value"]
                
                if isinstance(value, str):
                    where_clauses.append(f"{field} {operator} '{value}'")
                else:
                    where_clauses.append(f"{field} {operator} {value}")
            
            sql_query = f"SELECT * FROM bank_customers WHERE {' AND '.join(where_clauses)} LIMIT 1000"
            print(f"Generated query: {sql_query}")
            
            # Step 4: Validation
            print("Step 4: Query Validation...")
            validation_result = await self.agents["validation"].validate_query(sql_query)
            print(f"Validation: {validation_result.is_valid}, Issues: {validation_result.issues}")
            
            if not validation_result.is_valid:
                return json.dumps({
                    "status": "validation_failed",
                    "issues": validation_result.issues,
                    "sample_data": validation_result.sample_data
                })
            
            # Step 5: Activation
            print("Step 5: Segment Activation...")
            activation_result = await self.agents["activation"].activate_segment(
                sql_query,
                f"Demo_Segment_{len(natural_language_query)}"
            )
            print(f"Activation: {activation_result.success}, Customers: {activation_result.customer_count}")
            
            # Compile final result
            result = {
                "status": "success" if activation_result.success else "activation_failed",
                "segment_id": activation_result.segment_id,
                "customer_count": activation_result.customer_count,
                "downstream_systems": activation_result.downstream_systems,
                "generated_query": sql_query,
                "validation_sample": validation_result.sample_data,
                "demo_mode": True,
                "parsed_conditions": conditions,
                "processing_steps": {
                    "data_mapping": mapping_result.dict(),
                    "validation": validation_result.dict()
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_result = {
                "status": "error",
                "error": str(e),
                "query": natural_language_query,
                "demo_mode": True
            }
            return json.dumps(error_result, indent=2)
    
    async def get_segment_info(self, segment_id: str) -> str:
        """Get information about a created segment"""
        activation_agent = self.agents["activation"]
        if segment_id in activation_agent.active_segments:
            segment = activation_agent.active_segments[segment_id]
            return json.dumps({
                "segment_id": segment_id,
                "name": segment["name"],
                "customer_count": segment["customer_count"],
                "query": segment["query"]
            }, indent=2)
        else:
            return json.dumps({"error": "Segment not found"}, indent=2)
    
    async def get_database_schema(self) -> str:
        """Get the current database schema information"""
        schema = self.db_connector.get_schema()
        return json.dumps(schema, indent=2)

# Global server instance
demo_server = None

@server.tool()
async def create_segment(natural_language_query: str) -> str:
    """Create a customer segment from natural language description (Demo Mode)"""
    return await demo_server.create_segment_demo(natural_language_query)

@server.tool()
async def get_segment_info(segment_id: str) -> str:
    """Get information about a created segment"""
    return await demo_server.get_segment_info(segment_id)

@server.tool()
async def get_database_schema() -> str:
    """Get the current database schema information"""
    return await demo_server.get_database_schema()

async def main():
    global demo_server
    
    # Create and initialize server
    demo_server = DemoSegmentationServer()
    await demo_server.initialize()
    
    # Run the MCP server using stdio
    await server.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())