#!/usr/bin/env python3
"""
Schema validation and testing script
"""
import json
from models.schemas import (
    SegmentCriteria, IntentResult, DataMapping, QueryResult, 
    ValidationResult, ActivationResult, APIResponse, AgentConfig,
    SchemaValidator
)

def test_all_schemas():
    """Test all schema definitions with sample data"""
    print("🔍 Testing Schema Definitions...")
    
    # Test SegmentCriteria
    try:
        criteria = SegmentCriteria(
            conditions=[
                {"field": "age", "operator": ">", "value": 30},
                {"field": "marital", "operator": "=", "value": "married"}
            ],
            logical_operators=["AND"]
        )
        print("✅ SegmentCriteria: Valid")
    except Exception as e:
        print(f"❌ SegmentCriteria: {e}")
    
    # Test IntentResult
    try:
        intent = IntentResult(
            parsed_criteria=criteria,
            confidence=0.95,
            ambiguous_terms=["premium"],
            parsing_notes=["Successfully parsed query"]
        )
        print("✅ IntentResult: Valid")
    except Exception as e:
        print(f"❌ IntentResult: {e}")
    
    # Test DataMapping
    try:
        mapping = DataMapping(
            business_terms={"age": "age", "married": "marital"},
            table_mappings={"customers": "bank_customers"},
            field_mappings={"age": "age", "marital": "marital"}
        )
        print("✅ DataMapping: Valid")
    except Exception as e:
        print(f"❌ DataMapping: {e}")
    
    # Test QueryResult
    try:
        query_result = QueryResult(
            sql_query="SELECT * FROM bank_customers WHERE age > 30",
            optimized=True,
            estimated_rows=1500,
            tables_used=["bank_customers"],
            optimization_notes=["Added LIMIT clause"]
        )
        print("✅ QueryResult: Valid")
    except Exception as e:
        print(f"❌ QueryResult: {e}")
    
    # Test ValidationResult
    try:
        validation = ValidationResult(
            is_valid=True,
            issues=[],
            warnings=["Large result set"],
            sample_data=[{"age": 35, "marital": "married"}],
            row_count=1500
        )
        print("✅ ValidationResult: Valid")
    except Exception as e:
        print(f"❌ ValidationResult: {e}")
    
    # Test ActivationResult
    try:
        activation = ActivationResult(
            success=True,
            segment_id="SEG_ABC123",
            customer_count=1500,
            downstream_systems=["CRM_System", "Email_Platform"],
            issues=[],
            query_used="SELECT * FROM bank_customers WHERE age > 30"
        )
        print("✅ ActivationResult: Valid")
    except Exception as e:
        print(f"❌ ActivationResult: {e}")
    
    # Test APIResponse
    try:
        api_response = APIResponse(
            status="success",
            data={"segment_id": "SEG_ABC123"},
            errors=[],
            warnings=["Large dataset"],
            metadata={"processing_time": 1250}
        )
        print("✅ APIResponse: Valid")
    except Exception as e:
        print(f"❌ APIResponse: {e}")
    
    # Test AgentConfig
    try:
        config = AgentConfig(
            model_name="gpt-4.1",
            temperature=0.1,
            max_tokens=1000,
            timeout_seconds=30
        )
        print("✅ AgentConfig: Valid")
    except Exception as e:
        print(f"❌ AgentConfig: {e}")

def validate_schema_consistency():
    """Validate schema consistency using SchemaValidator"""
    print("\n🔍 Validating Schema Consistency...")
    
    issues = SchemaValidator.validate_all_schemas()
    
    if not issues:
        print("✅ All schemas are consistent!")
    else:
        print("❌ Schema consistency issues found:")
        for issue in issues:
            print(f"  - {issue}")

def generate_schema_documentation():
    """Generate schema documentation"""
    print("\n📚 Generating Schema Documentation...")
    
    schemas = SchemaValidator.get_schema_info()
    
    doc_path = "schema_documentation.json"
    with open(doc_path, 'w') as f:
        json.dump(schemas, f, indent=2)
    
    print(f"✅ Schema documentation saved to: {doc_path}")
    
    # Print summary
    print(f"\n📊 Schema Summary:")
    for name, schema in schemas.items():
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        print(f"  - {name}: {len(properties)} fields ({len(required)} required)")

def test_error_cases():
    """Test error cases and validation"""
    print("\n🧪 Testing Error Cases...")
    
    # Test invalid customer count
    try:
        ActivationResult(
            success=True,
            segment_id="SEG_TEST",
            customer_count=-1,  # Invalid negative count
            downstream_systems=[]
        )
        print("❌ Negative customer count validation failed")
    except ValueError:
        print("✅ Negative customer count properly rejected")
    
    # Test invalid confidence score
    try:
        IntentResult(
            parsed_criteria=SegmentCriteria(conditions=[{"field": "age", "operator": ">", "value": 30}]),
            confidence=1.5,  # Invalid > 1.0
            ambiguous_terms=[]
        )
        print("❌ Invalid confidence score validation failed")
    except ValueError:
        print("✅ Invalid confidence score properly rejected")
    
    # Test invalid logical operators
    try:
        SegmentCriteria(
            conditions=[
                {"field": "age", "operator": ">", "value": 30},
                {"field": "marital", "operator": "=", "value": "married"}
            ],
            logical_operators=["AND", "OR", "AND"]  # Too many operators
        )
        print("❌ Invalid logical operators validation failed")
    except ValueError:
        print("✅ Invalid logical operators properly rejected")

def main():
    """Run all schema tests"""
    print("🚀 Schema Validation Suite")
    print("=" * 50)
    
    test_all_schemas()
    validate_schema_consistency()
    test_error_cases()
    generate_schema_documentation()
    
    print("\n✅ Schema validation complete!")

if __name__ == "__main__":
    main()