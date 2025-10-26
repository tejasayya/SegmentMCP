from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class AgentStep(str, Enum):
    INTENT_PARSING = "intent_parsing"
    DATA_MAPPING = "data_mapping"
    QUERY_GENERATION = "query_generation"
    VALIDATION = "validation"
    ACTIVATION = "activation"

# Base class for all results with common fields
class BaseResult(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    processing_time_ms: Optional[int] = Field(None, ge=0, description="Processing time in milliseconds")

class SegmentCriteria(BaseModel):
    conditions: List[Dict[str, Any]] = Field(..., min_items=1, description="List of segment conditions")
    logical_operators: List[str] = Field(default=["AND"], description="Operators connecting conditions")
    
    @validator('logical_operators')
    def validate_operators(cls, v, values):
        if 'conditions' in values and len(values['conditions']) > 1:
            if len(v) != len(values['conditions']) - 1:
                raise ValueError('Number of logical operators must be one less than number of conditions')
        return v

class IntentResult(BaseResult):
    parsed_criteria: SegmentCriteria
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for parsing")
    ambiguous_terms: List[str] = Field(default_factory=list, description="Terms that were ambiguous")
    parsing_notes: List[str] = Field(default_factory=list, description="Additional parsing information")

class DataMapping(BaseResult):
    business_terms: Dict[str, str] = Field(default_factory=dict, description="business_term -> schema_field")
    table_mappings: Dict[str, str] = Field(default_factory=dict, description="logical_table -> physical_table")
    field_mappings: Dict[str, str] = Field(default_factory=dict, description="business_field -> db_field")

class QueryResult(BaseResult):
    sql_query: str = Field(..., min_length=1, description="Generated SQL query")
    optimized: bool = Field(default=False, description="Whether query was optimized")
    estimated_rows: int = Field(..., ge=0, description="Estimated number of rows")
    tables_used: List[str] = Field(default_factory=list, description="Database tables used")
    optimization_notes: List[str] = Field(default_factory=list, description="Query optimization notes")

class ValidationResult(BaseResult):
    is_valid: bool = Field(..., description="Whether validation passed")
    issues: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    sample_data: List[Dict] = Field(default_factory=list, description="Sample query results")
    row_count: int = Field(..., ge=0, description="Total number of rows")

class ActivationResult(BaseResult):
    success: bool = Field(..., description="Whether activation succeeded")
    segment_id: Optional[str] = Field(None, description="Generated segment identifier")
    customer_count: int = Field(..., ge=0, description="Number of customers in segment")
    downstream_systems: List[str] = Field(default_factory=list, description="Systems where segment was activated")
    issues: List[str] = Field(default_factory=list, description="Activation errors or issues")
    query_used: Optional[str] = Field(None, description="SQL query used for activation")
    
    @validator('customer_count')
    def validate_customer_count(cls, v):
        if v < 0:
            raise ValueError('Customer count cannot be negative')
        return v

# API Response wrapper for HTTP endpoints
class APIResponse(BaseModel):
    status: str = Field(..., pattern="^(success|error|warning)$", description="Response status")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

# Configuration schemas
class AgentConfig(BaseModel):
    model_name: str = Field(..., description="AI model name")
    temperature: float = Field(0.1, ge=0.0, le=2.0, description="Model temperature")
    max_tokens: int = Field(1000, gt=0, le=4000, description="Maximum tokens")
    timeout_seconds: int = Field(30, gt=0, le=300, description="Request timeout")

# Schema validation utilities
class SchemaValidator:
    @staticmethod
    def validate_all_schemas():
        """Validate all schema definitions are consistent"""
        issues = []
        
        # Check that all Result classes have required fields
        result_classes = [ActivationResult, ValidationResult, QueryResult, IntentResult, DataMapping]
        
        for cls in result_classes:
            if not hasattr(cls, '__fields__'):
                issues.append(f"{cls.__name__} is not a proper Pydantic model")
                continue
                
            # Check for common fields from BaseResult
            if not issubclass(cls, BaseResult):
                issues.append(f"{cls.__name__} should inherit from BaseResult")
                
        return issues
    
    @staticmethod
    def get_schema_info():
        """Get information about all schemas"""
        schemas = {
            'SegmentCriteria': SegmentCriteria.schema(),
            'IntentResult': IntentResult.schema(),
            'DataMapping': DataMapping.schema(),
            'QueryResult': QueryResult.schema(),
            'ValidationResult': ValidationResult.schema(),
            'ActivationResult': ActivationResult.schema(),
            'APIResponse': APIResponse.schema(),
            'AgentConfig': AgentConfig.schema()
        }
        return schemas