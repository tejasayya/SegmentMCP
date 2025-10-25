from models.schemas import DataMapping, SegmentCriteria
from database.kaggle_connector import KaggleConnector
from typing import Dict, Any

class DataMapperAgent:
    def __init__(self, db_connector: KaggleConnector):
        self.db_connector = db_connector
        self.business_glossary = {
            "subscription": "y",  # Term deposit subscription
            "deposit": "y",
            "balance": "balance",
            "loan": "loan",
            "housing": "housing",
            "job": "job",
            "age": "age",
            "contact": "contact",
            "campaign": "campaign",
            "previous": "previous",
            "duration": "duration"
        }
    
    async def map_criteria_to_schema(self, criteria: SegmentCriteria) -> DataMapping:
        """Map business terms to actual database schema"""
        schema_info = self.db_connector.get_schema()
        
        field_mappings = {}
        table_mappings = {"customers": "bank_customers"}
        
        # Map each condition field to database field
        for condition in criteria.conditions:
            business_field = condition["field"].lower()
            db_field = self._map_field(business_field, schema_info)
            field_mappings[business_field] = db_field
        
        return DataMapping(
            business_terms=self.business_glossary,
            table_mappings=table_mappings,
            field_mappings=field_mappings
        )
    
    def _map_field(self, business_field: str, schema_info: Dict[str, Any]) -> str:
        """Map business field name to database field name"""
        # First check business glossary
        if business_field in self.business_glossary:
            return self.business_glossary[business_field]
        
        # Then check if it exists in schema
        available_columns = list(schema_info["columns"].keys())
        for column in available_columns:
            if business_field.lower() in column.lower() or column.lower() in business_field.lower():
                return column
        
        # If no direct match, return the original (will be validated later)
        return business_field