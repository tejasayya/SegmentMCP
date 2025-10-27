#!/usr/bin/env python3
import mcp.server
import asyncio
from typing import Any
import json
import sys
import logging

from config import Config
from database.kaggle_connector import KaggleConnector
from agents.intent_parser import IntentParserAgent
from agents.data_mapper import DataMapperAgent
from agents.query_generator import QueryGeneratorAgent
from agents.validation_agent import ValidationAgent
from agents.activation_agent import ActivationAgent

# Configure logging to stderr so stdout is reserved for MCP JSON
logging.basicConfig(level=logging.INFO, stream=sys.stderr,
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Create MCP server instance
server = mcp.server.FastMCP("segmentation-agent")

class SegmentationMCPServer:
    def __init__(self):
        self.config = Config()
        self.db_connector = None
        self.agents = {}
        
    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing Segmentation MCP Server...")
        
        # Initialize database
        self.db_connector = await KaggleConnector(
            self.config.KAGGLE_DATASET
        ).initialize()
        
        # Initialize agents with consistent error handling
        agents_to_initialize = [
            ("data_mapper", DataMapperAgent, [self.db_connector]),
            ("validation", ValidationAgent, [self.db_connector]),
            ("activation", ActivationAgent, [self.db_connector]),
            ("intent_parser", IntentParserAgent, [self.config.OPENAI_API_KEY, self.config.INTENT_PARSER_MODEL]),
            ("query_generator", QueryGeneratorAgent, [self.config.OPENAI_API_KEY, self.db_connector, self.config.QUERY_GENERATOR_MODEL])
        ]

        for agent_name, agent_class, args in agents_to_initialize:
            try:
                self.agents[agent_name] = agent_class(*args)
                logger.info("%s initialized", agent_name)
            except Exception as e:
                logger.warning("%s unavailable: %s", agent_name, e)
                self.agents[agent_name] = None
        
        logger.info("Segmentation MCP Server initialized successfully!")
    
    async def create_segment(self, natural_language_query: str) -> dict:
        """
        Create a customer segment from natural language description.
        
        Args:
            natural_language_query: Description of desired customer segment in plain English
            
        Returns:
            dict with segment creation results
        """
        try:
            logger.info("Processing query: %s", natural_language_query)
            
            # Check if required agents are available
            if not self.agents.get("intent_parser"):
                return {
                    "status": "error",
                    "error": "Intent parser agent not available (OpenAI initialization failed)",
                    "query": natural_language_query
                }
            
            if not self.agents.get("query_generator"):
                return {
                    "status": "error", 
                    "error": "Query generator agent not available (OpenAI initialization failed)",
                    "query": natural_language_query
                }
            
            # Step 1: Intent Parsing
            logger.info("Step 1: Intent Parsing...")
            intent_result = await self.agents["intent_parser"].parse_intent(natural_language_query)
            parsed_criteria = _to_primitive(getattr(intent_result, "parsed_criteria", intent_result))
            logger.info("Parsed criteria: %s", parsed_criteria)
            
            # Step 2: Data Mapping
            logger.info("Step 2: Data Mapping...")
            mapping_result = await self.agents["data_mapper"].map_criteria_to_schema(
                getattr(intent_result, "parsed_criteria", intent_result)
            )
            field_mappings = _to_primitive(getattr(mapping_result, "field_mappings", mapping_result))
            logger.info("Field mappings: %s", field_mappings)
            
            # Step 3: Query Generation
            logger.info("Step 3: Query Generation...")
            query_result = await self.agents["query_generator"].generate_optimized_query(
                getattr(intent_result, "parsed_criteria", intent_result),
                mapping_result
            )
            sql_query = getattr(query_result, "sql_query", str(query_result))
            logger.info("Generated query: %s", sql_query)
            
            # Step 4: Validation
            logger.info("Step 4: Query Validation...")
            validation_result = await self.agents["validation"].validate_query(
                sql_query
            )
            is_valid = getattr(validation_result, "is_valid", True)
            issues = getattr(validation_result, "issues", [])
            sample_data = getattr(validation_result, "sample_data", [])
            logger.info("Validation: %s, Issues: %s", is_valid, _to_primitive(issues))
            
            # Check for critical validation issues (exclude large row count warnings)
            critical_issues = [issue for issue in issues 
                             if isinstance(issue, str) and not issue.startswith("Query returns large number of rows")] if isinstance(issues, list) else []
            
            if critical_issues:
                return {
                    "status": "validation_failed",
                    "issues": critical_issues,
                    "sample_data": _to_primitive(sample_data)
                }
            
            # Step 5: Activation
            logger.info("Step 5: Segment Activation...")
            activation_result = await self.agents["activation"].activate_segment(
                sql_query,
                f"Segment_for_{natural_language_query[:20]}..."
            )
            success = getattr(activation_result, "success", False)
            customer_count = getattr(activation_result, "customer_count", 0)
            segment_id = getattr(activation_result, "segment_id", None)
            downstream_systems = getattr(activation_result, "downstream_systems", [])
            logger.info("Activation: %s, Customers: %s", success, customer_count)
            
            # Compile final result
            result = {
                "status": "success" if success else "activation_failed",
                "segment_id": segment_id,
                "customer_count": customer_count,
                "downstream_systems": _to_primitive(downstream_systems),
                "generated_query": sql_query,
                "validation_sample": _to_primitive(sample_data),
                "estimated_rows": getattr(query_result, "estimated_rows", None),
                "processing_steps": {
                    "intent_parsing": _to_primitive(intent_result),
                    "data_mapping": _to_primitive(mapping_result),
                    "query_generation": _to_primitive(query_result),
                    "validation": _to_primitive(validation_result),
                    "activation": _to_primitive(activation_result)
                }
            }
            
            return result
            
        except Exception as e:
            logger.exception("Error while creating segment")
            error_result = {
                "status": "error",
                "error": str(e),
                "query": natural_language_query
            }
            return error_result
    
    async def get_segment_info(self, segment_id: str) -> dict:
        """Get information about a created segment"""
        activation_agent = self.agents.get("activation")
        if activation_agent and segment_id in getattr(activation_agent, "active_segments", {}):
            segment = activation_agent.active_segments[segment_id]
            return {
                "segment_id": segment_id,
                "name": segment.get("name"),
                "customer_count": segment.get("customer_count"),
                "query": segment.get("query")
            }
        else:
            return {"error": "Segment not found"}
    
    async def get_database_schema(self) -> dict:
        """Get the current database schema information"""
        schema = self.db_connector.get_schema()
        # ensure schema is a dict/primitive serializable structure
        return _to_primitive(schema)

# Helper: convert objects to primitives for safe JSON serialization

def _to_primitive(obj: Any) -> Any:
    """Attempt to convert common objects to JSON-serializable primitives.
    Falls back to string() when necessary.
    """
    # If it's already a primitive JSON type, return as-is
    if obj is None or isinstance(obj, (str, int, float, bool, list, dict)):
        # recursively convert lists/dicts
        if isinstance(obj, list):
            return [_to_primitive(o) for o in obj]
        if isinstance(obj, dict):
            return {k: _to_primitive(v) for k, v in obj.items()}
        return obj

    # pydantic / objects with dict()
    if hasattr(obj, "dict"):
        try:
            return _to_primitive(obj.dict())
        except Exception:
            pass
    if hasattr(obj, "__dict__"):
        try:
            return {k: _to_primitive(v) for k, v in vars(obj).items()}
        except Exception:
            pass

    # Fallback to string representation
    try:
        return str(obj)
    except Exception:
        return {"unserializable": True}

# safe serializer for wrappers

def safe_serialize(obj: Any) -> str:
    try:
        return json.dumps(obj, indent=2, default=lambda o: str(o))
    except Exception:
        return json.dumps(_to_primitive(obj), indent=2)

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
    result = await segmentation_server.create_segment(natural_language_query)
    return safe_serialize(result)

@server.tool()
async def get_segment_info(segment_id: str) -> str:
    """Get information about a created segment"""
    result = await segmentation_server.get_segment_info(segment_id)
    return safe_serialize(result)

@server.tool()
async def get_database_schema() -> str:
    """Get the current database schema information"""
    result = await segmentation_server.get_database_schema()
    return safe_serialize(result)

async def main():
    global segmentation_server
    
    # Create and initialize server
    segmentation_server = SegmentationMCPServer()
    await segmentation_server.initialize()
    
    # Run the MCP server using stdio
    await server.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())
