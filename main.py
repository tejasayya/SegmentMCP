#!/usr/bin/env python3
import mcp.server
import asyncio
from typing import Any
import json

from config import Config
from database.kaggle_connector import KaggleConnector
from agents.intent_parser import IntentParserAgent
from agents.data_mapper import DataMapperAgent
from agents.query_generator import QueryGeneratorAgent
from agents.validation_agent import ValidationAgent
from agents.activation_agent import ActivationAgent

# Create MCP server instance
server = mcp.server.FastMCP("segmentation-agent")

class SegmentationMCPServer:
    def __init__(self):
        self.config = Config()
        self.db_connector = None
        self.agents = {}
        
    async def initialize(self):
        """Initialize all components"""
        print("Initializing Segmentation MCP Server...")
        
        # Initialize database
        self.db_connector = await KaggleConnector(
            self.config.KAGGLE_DATASET
        ).initialize()
        
        # Initialize agents
        try:
            self.agents["intent_parser"] = IntentParserAgent(self.config.OPENAI_API_KEY)
        except Exception as e:
            print(f"Warning: Could not initialize IntentParserAgent: {e}")
            self.agents["intent_parser"] = None
            
        self.agents["data_mapper"] = DataMapperAgent(self.db_connector)
        
        try:
            self.agents["query_generator"] = QueryGeneratorAgent(
                self.config.OPENAI_API_KEY, 
                self.db_connector
            )
        except Exception as e:
            print(f"Warning: Could not initialize QueryGeneratorAgent: {e}")
            self.agents["query_generator"] = None
            
        self.agents["validation"] = ValidationAgent(self.db_connector)
        self.agents["activation"] = ActivationAgent(self.db_connector)
        
        print("Segmentation MCP Server initialized successfully!")
    
    async def create_segment(self, natural_language_query: str) -> str:
        """
        Create a customer segment from natural language description.
        
        Args:
            natural_language_query: Description of desired customer segment in plain English
            
        Returns:
            JSON string with segment creation results
        """
        try:
            print(f"Processing query: {natural_language_query}")
            
            # Check if required agents are available
            if not self.agents["intent_parser"]:
                return json.dumps({
                    "status": "error",
                    "error": "Intent parser agent not available (OpenAI initialization failed)",
                    "query": natural_language_query
                })
            
            if not self.agents["query_generator"]:
                return json.dumps({
                    "status": "error", 
                    "error": "Query generator agent not available (OpenAI initialization failed)",
                    "query": natural_language_query
                })
            
            # Step 1: Intent Parsing
            print("Step 1: Intent Parsing...")
            intent_result = await self.agents["intent_parser"].parse_intent(natural_language_query)
            print(f"Parsed criteria: {intent_result.parsed_criteria.dict()}")
            
            # Step 2: Data Mapping
            print("Step 2: Data Mapping...")
            mapping_result = await self.agents["data_mapper"].map_criteria_to_schema(
                intent_result.parsed_criteria
            )
            print(f"Field mappings: {mapping_result.field_mappings}")
            
            # Step 3: Query Generation
            print("Step 3: Query Generation...")
            query_result = await self.agents["query_generator"].generate_optimized_query(
                intent_result.parsed_criteria,
                mapping_result
            )
            print(f"Generated query: {query_result.sql_query}")
            
            # Step 4: Validation
            print("Step 4: Query Validation...")
            validation_result = await self.agents["validation"].validate_query(
                query_result.sql_query
            )
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
                query_result.sql_query,
                f"Segment_for_{natural_language_query[:20]}..."
            )
            print(f"Activation: {activation_result.success}, Customers: {activation_result.customer_count}")
            
            # Compile final result
            result = {
                "status": "success" if activation_result.success else "activation_failed",
                "segment_id": activation_result.segment_id,
                "customer_count": activation_result.customer_count,
                "downstream_systems": activation_result.downstream_systems,
                "generated_query": query_result.sql_query,
                "validation_sample": validation_result.sample_data,
                "estimated_rows": query_result.estimated_rows,
                "processing_steps": {
                    "intent_parsing": intent_result.dict(),
                    "data_mapping": mapping_result.dict(),
                    "query_generation": query_result.dict(),
                    "validation": validation_result.dict()
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_result = {
                "status": "error",
                "error": str(e),
                "query": natural_language_query
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
segmentation_server = None

@server.tool()
async def create_segment(natural_language_query: str) -> str:
    """
    Create a customer segment from natural language description.
    
    Args:
        natural_language_query: Description of desired customer segment in plain English
        
    Returns:
        JSON string with segment creation results
    """
    return await segmentation_server.create_segment(natural_language_query)

@server.tool()
async def get_segment_info(segment_id: str) -> str:
    """Get information about a created segment"""
    return await segmentation_server.get_segment_info(segment_id)

@server.tool()
async def get_database_schema() -> str:
    """Get the current database schema information"""
    return await segmentation_server.get_database_schema()

async def main():
    global segmentation_server
    
    # Create and initialize server
    segmentation_server = SegmentationMCPServer()
    await segmentation_server.initialize()
    
    # Run the MCP server using stdio
    await server.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())