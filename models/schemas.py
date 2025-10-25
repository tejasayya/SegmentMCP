from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum

class AgentStep(str, Enum):
    INTENT_PARSING = "intent_parsing"
    DATA_MAPPING = "data_mapping"
    QUERY_GENERATION = "query_generation"
    VALIDATION = "validation"
    ACTIVATION = "activation"

class SegmentCriteria(BaseModel):
    conditions: List[Dict[str, Any]]
    logical_operators: List[str] = ["AND"]

class IntentResult(BaseModel):
    parsed_criteria: SegmentCriteria
    confidence: float
    ambiguous_terms: List[str]

class DataMapping(BaseModel):
    business_terms: Dict[str, str]  # business_term -> schema_field
    table_mappings: Dict[str, str]  # logical_table -> physical_table
    field_mappings: Dict[str, str]  # business_field -> db_field

class QueryResult(BaseModel):
    sql_query: str
    optimized: bool
    estimated_rows: int
    tables_used: List[str]

class ValidationResult(BaseModel):
    is_valid: bool
    issues: List[str]
    sample_data: List[Dict]
    row_count: int

class ActivationResult(BaseModel):
    success: bool
    segment_id: Optional[str] = None
    customer_count: int
    downstream_systems: List[str]