# SegmentMCP - AI-Powered Customer Segmentation Server

## 🎯 Overview

SegmentMCP is an intelligent Model Context Protocol (MCP) server that transforms natural language queries into actionable customer segments. It bridges the gap between business stakeholders who think in plain English and technical systems that require structured SQL queries, enabling democratized access to customer data insights.

## 🚀 Problem Statement

### The Challenge
Modern businesses struggle with customer segmentation due to several key barriers:

1. **Technical Complexity**: Marketing teams need SQL knowledge to create customer segments
2. **Time-to-Insight**: Manual query writing and validation takes hours or days
3. **Error-Prone Process**: Hand-written SQL queries often contain syntax errors or logical mistakes
4. **Limited Accessibility**: Only technical users can create and modify customer segments
5. **Inconsistent Results**: Different team members create different queries for similar business requirements

### The Solution
SegmentMCP eliminates these barriers by providing:
- **Natural Language Interface**: "Find married customers over 30 with housing loans"
- **Automated SQL Generation**: AI-powered query creation with optimization
- **Built-in Validation**: Automatic query testing and error detection
- **Processing Transparency**: Complete breakdown of all processing steps in response
- **Integration Ready Architecture**: Framework for connecting to downstream systems

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │───▶│   MCP Server     │───▶│  Kaggle Dataset │
│ (Claude/Custom) │    │  (FastMCP)       │    │ (45K+ records)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Agent Pipeline │
                       │                  │
                       │ 1. Intent Parser │ ← GPT-4.1
                       │ 2. Data Mapper   │ ← Rule-based
                       │ 3. Query Gen     │ ← GPT-4.1  
                       │ 4. Validator     │ ← Rule-based
                       │ 5. Activator     │ ← Simulation
                       └──────────────────┘
```

### Agent-Based Processing Pipeline

1. **Intent Parser Agent** - Converts natural language to structured criteria using GPT-4.1
2. **Data Mapper Agent** - Maps business terms to database schema fields
3. **Query Generator Agent** - Creates optimized SQL queries with AI assistance
4. **Validation Agent** - Tests queries for syntax, performance, and safety
5. **Activation Agent** - Executes segments and integrates with downstream systems

## 📁 Project Structure

```
SegmentMCP/
├── agents/                    # AI processing agents
│   ├── intent_parser.py      # Natural language → criteria
│   ├── data_mapper.py        # Business terms → DB fields  
│   ├── query_generator.py    # Criteria → SQL
│   ├── validation_agent.py   # SQL validation & testing
│   └── activation_agent.py   # Segment execution
├── database/
│   └── kaggle_connector.py   # Dataset management
├── models/
│   └── schemas.py            # Pydantic data models
├── data/                     # Dataset storage
│   ├── bank-full.csv        # Bank customer dataset
│   └── bank_deposit.db      # SQLite database
├── main.py                   # Core MCP server
├── demo_server.py           # Demo mode (no OpenAI)
├── http_server.py           # Direct HTTP API
├── http_wrapper.py          # MCP protocol wrapper
├── demo_http_wrapper.py     # Demo HTTP wrapper
├── config.py                # Configuration management
├── generate_claude_config.py # Claude Desktop setup
├── validate_schemas.py      # Schema validation
├── validate_config_usage.py # Config usage checker
├── test_config_integration.py # Config testing
└── requirements.txt         # Dependencies
```

## 📊 Dataset Information

### **Bank Customer Dataset**
- **Source**: Kaggle "Bank Term Deposit Subscription" dataset
- **Records**: 45,211 bank customers
- **Columns**: 17 attributes including demographics, financial, and campaign data
- **Format**: CSV with semicolon delimiter
- **Storage**: Automatically converted to SQLite for querying

### **Key Data Fields**
- **Demographics**: age, job, marital status, education
- **Financial**: balance, housing loan, personal loan, default status
- **Campaign**: contact method, duration, campaign number, previous contacts
- **Target**: term deposit subscription (yes/no)

### **Data Processing**
- Automatic CSV detection and loading
- SQLite conversion for efficient querying  
- Schema introspection and validation
- Sample data generation for testing

### **Current Data Source Support**
- **Primary**: Single Kaggle dataset connector
- **Architecture**: Extensible connector pattern ready for additional sources
- **Storage**: Local SQLite database with CSV import
- **Future**: Framework supports PostgreSQL, MySQL, BigQuery connectors

## ✨ Features

### 🧠 Intelligent Query Processing
- **Natural Language Understanding**: Parse complex business requirements using GPT-4.1
- **Context-Aware Mapping**: Automatically map business terms to database fields
- **Query Optimization**: Generate efficient SQL with automatic LIMIT clauses and optimization
- **Error Prevention**: Built-in validation prevents dangerous operations (DELETE, UPDATE, DROP)

### 🔒 Safety & Validation
- **Operation Restrictions**: Blocks DELETE, UPDATE, DROP operations
- **Performance Limits**: Automatic LIMIT clauses and row count warnings
- **Syntax Validation**: Pre-execution query testing
- **Input Validation**: Query structure and content validation
- **Read-Only Access**: Database operations limited to SELECT statements

### 🔌 Integration Ready
- **MCP Protocol**: Native support for AI assistant integration
- **REST API**: HTTP endpoints for web applications  
- **Extensible Architecture**: Framework ready for multiple data sources
- **Simulated Downstream Activation**: Returns integration targets for CRM, email, analytics systems

*Note: Current version simulates downstream integrations. Real API connections require additional development.*

### 📊 Comprehensive Results
- **Sample Data Preview**: See actual customer records before activation
- **Processing Transparency**: Complete breakdown of all agent processing steps with timestamps
- **Performance Metrics**: Processing time tracking, query execution time, and row count estimates
- **Confidence Scoring**: Basic confidence reporting and ambiguous term detection
- **Validation Results**: Detailed validation reports with warnings and error detection
- **Schema Information**: Complete database schema with sample values and data types

## 🛠️ Implementation Use Cases

### 1. Marketing Campaign Management
```json
{
  "query": "High-value customers who haven't been contacted in 6 months",
  "use_case": "Re-engagement campaign targeting",
  "output": "Segment for email marketing platform"
}
```

### 2. Risk Assessment
```json
{
  "query": "Customers with loans but negative balance trends",
  "use_case": "Credit risk monitoring",
  "output": "Alert list for risk management team"
}
```

### 3. Product Recommendations
```json
{
  "query": "Young professionals without housing loans",
  "use_case": "Mortgage product targeting",
  "output": "Prospect list for sales team"
}
```

### 4. Customer Success
```json
{
  "query": "Long-term customers with declining engagement",
  "use_case": "Churn prevention",
  "output": "Priority list for customer success managers"
}
```

### 5. Compliance Reporting
```json
{
  "query": "All customers contacted more than regulatory limit",
  "use_case": "Compliance monitoring",
  "output": "Audit report for regulatory team"
}
```

## 📈 Output Utilization

### Integration Architecture (Framework Ready)

The system provides a foundation for integrating with downstream systems:

#### **Current Implementation**
- **Simulated Activations**: Returns list of target systems for segments (simulation only)
- **Processing Results**: Complete customer data and SQL queries for export
- **Segment Storage**: In-memory segment management with unique IDs
- **API Structure**: Framework ready for webhook and API integrations

#### **Integration Framework (Not Yet Implemented)** 
- **CRM Systems**: Architecture supports Salesforce, HubSpot, Pipedrive integration
- **Email Platforms**: Framework ready for Mailchimp, SendGrid connections
- **Ad Platforms**: Structure prepared for Facebook, Google, LinkedIn APIs
- **Analytics Tools**: Design supports Tableau, Power BI data export

*Note: Current version provides the framework and simulated responses. Real API integrations require additional development work.*

### Business Process Integration

#### **Marketing Workflows**
```
Natural Language Query → Segment Creation → Campaign Launch → Performance Tracking
```

#### **Sales Processes**
```
Lead Qualification → Segment Assignment → Automated Outreach → Conversion Tracking
```

#### **Customer Success**
```
Health Score Monitoring → Risk Segment Identification → Intervention Campaigns → Retention Metrics
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- OpenAI API Key
- Kaggle API credentials (optional, for dataset access)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/tejasayya/SegmentMCP.git
cd SegmentMCP
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
# Create .env file
OPENAI_API_KEY=your_openai_api_key_here
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_key
```

4. **Generate portable Claude Desktop config**
```bash
python generate_claude_config.py
```
This creates `claude_mcp_config_generated.json` with correct paths for your system.

**What this does:**
- Generates cross-platform Claude Desktop configuration
- Auto-detects project paths and data directories
- Validates configuration and reports issues
- Creates portable config that works on any system

5. **Validate schemas and configuration (optional)**
```bash
python validate_schemas.py          # Validate data schemas
python validate_config_usage.py     # Check config usage
python test_config_integration.py   # Test config integration
```
These validate schemas, check configuration usage, and test integration.

## 🧪 Validation & Testing Tools

The project includes comprehensive validation and testing infrastructure:

### **Schema Validation**
```bash
python validate_schemas.py
```
- Validates all Pydantic schemas
- Tests error cases and edge conditions  
- Generates schema documentation
- Ensures data model consistency

### **Configuration Validation**
```bash
python validate_config_usage.py
```
- Checks all config values are actually used
- Identifies unused configuration
- Validates config value ranges
- Tests environment variable overrides

### **Integration Testing**
```bash
python test_config_integration.py
```
- Tests agent configuration loading
- Validates config integration across components
- Checks environment variable support
- Tests configuration validation logic

### **Direct Testing**
```bash
python test_demo_direct.py      # Test demo server directly
python test_http_requests.py    # Test HTTP endpoints
python test_mcp_client.py       # Test MCP protocol
```

4. **Choose your server mode**

**Note on OpenAI Version**: If you encounter OpenAI compatibility issues, you may need to upgrade:
```bash
pip install openai>=2.0.0  # Upgrade from 1.35.15 if needed
```

## 🎯 Server Options

### Option 1: Full MCP Server (Production)
```bash
python main.py
```
- ✅ Complete AI-powered natural language processing
- ✅ Requires OpenAI API key
- ✅ For Claude Desktop integration
- ✅ Full agent pipeline with GPT

### Option 2: Demo Mode (No OpenAI Required)
```bash
python demo_server.py
```
- ✅ Rule-based query parsing (no AI)
- ✅ Works without OpenAI API key
- ✅ Good for testing and development
- ❌ Limited to predefined patterns

### Option 3: HTTP Testing Interfaces

For Postman/HTTP API testing, choose one approach:

#### A) Direct HTTP Server (Recommended for development)
```bash
python http_server.py
# Server runs on http://localhost:8001
```
- **Pros**: Fast, reliable, easy debugging, direct method calls
- **Cons**: Bypasses MCP protocol validation
- **Use for**: Daily development, Postman testing, rapid iteration

#### B) MCP Protocol Wrapper (Protocol validation)
```bash
python http_wrapper.py
# Server runs on http://localhost:8001
```
- **Pros**: Tests actual MCP implementation, protocol-compliant, validates MCP server
- **Cons**: More complex, subprocess overhead, harder debugging
- **Use for**: Validating MCP server works correctly, protocol testing

#### C) Demo HTTP Wrapper (No OpenAI)
```bash
python demo_http_wrapper.py
# Server runs on http://localhost:8002
```
- **Pros**: Works without OpenAI API, good for basic testing, no API costs
- **Cons**: Limited to rule-based parsing, no AI capabilities
- **Use for**: Testing without API costs, basic functionality validation

## 🤔 Which Server Should You Use?

| Use Case | Recommended Server | Why |
|----------|-------------------|-----|
| **Claude Desktop Integration** | `main.py` | Full MCP protocol with AI |
| **Development/Testing** | `http_server.py` | Fast HTTP testing with Postman |
| **MCP Protocol Validation** | `http_wrapper.py` | Ensures MCP server works correctly |
| **No OpenAI API Key** | `demo_server.py` or `demo_http_wrapper.py` | Works without API costs |
| **Production Deployment** | `main.py` | Complete feature set |

5. **Test the API**
```bash
curl -X POST "http://localhost:8001/create-segment" \
     -H "Content-Type: application/json" \
     -d '{"query": "Married customers with age over 30"}'
```

### MCP Integration

For AI assistant integration, run the MCP server:
```bash
python main.py
```

## 🔧 Architecture Decisions

### Why Multiple Server Files?

This project provides multiple ways to run the server to address different development and deployment needs:

#### **Core MCP Server (`main.py`)**
- **Purpose**: Production MCP server for Claude Desktop
- **Features**: Full AI pipeline with OpenAI integration
- **Protocol**: Pure MCP via stdio

#### **Demo Version (`demo_server.py`)**
- **Purpose**: Development without API costs
- **Features**: Rule-based parsing, no OpenAI dependency
- **Why**: Allows testing core functionality without API keys

#### **HTTP Interfaces - Two Approaches**

**Direct Integration (`http_server.py`)**
- **Approach**: Directly imports and uses `SegmentationMCPServer` class
- **Reasoning**: Faster development, easier debugging, reliable for testing
- **Trade-off**: Bypasses MCP protocol, but better for HTTP API needs

**Protocol Wrapper (`http_wrapper.py`)**
- **Approach**: Starts MCP server as subprocess, communicates via JSON-RPC
- **Reasoning**: Tests actual MCP implementation, validates protocol compliance
- **Trade-off**: More complex, but ensures MCP server actually works

#### **Why Both HTTP Approaches?**

1. **Development Speed**: `http_server.py` for fast iteration and Postman testing
2. **Protocol Validation**: `http_wrapper.py` to ensure MCP server works correctly
3. **Different Needs**: Direct calls vs. protocol testing serve different purposes

### OpenAI Version Compatibility

**Issue**: The project initially used `openai>=1.30.0,<1.36.0` but users may encounter compatibility issues.

**Solution**: Upgrade to `openai>=2.0.0` if you face initialization errors:
```bash
pip install openai>=2.0.0
```

**Why**: Newer OpenAI versions have different client initialization patterns and better stability.

## 📡 API Reference

### Create Segment
**POST** `/create-segment`

Create a customer segment from natural language description.

**Request Body:**
```json
{
  "query": "Description of desired customer segment in plain English"
}
```

**Response:**
```json
{
  "status": "success",
  "segment_id": "SEG_ABCD1234",
  "customer_count": 1500,
  "downstream_systems": ["CRM_System", "Email_Marketing_Platform", "Ad_Platform"],
  "generated_query": "SELECT * FROM bank_customers WHERE marital = 'married' AND age > 30 LIMIT 1000",
  "validation_sample": [
    {"age": 35, "job": "management", "marital": "married", "balance": 2143, "housing": "yes"},
    {"age": 42, "job": "technician", "marital": "married", "balance": 1506, "housing": "no"}
  ],
  "estimated_rows": 1500,
  "processing_steps": {
    "intent_parsing": {
      "parsed_criteria": {
        "conditions": [{"field": "marital", "operator": "=", "value": "married"}, {"field": "age", "operator": ">", "value": 30}],
        "logical_operators": ["AND"]
      },
      "confidence": 0.9,
      "ambiguous_terms": [],
      "parsing_notes": ["Successfully parsed natural language query"],
      "timestamp": "2024-01-15T10:30:01Z",
      "processing_time_ms": 1250
    },
    "data_mapping": {
      "business_terms": {"age": "age", "marital": "marital"},
      "table_mappings": {"customers": "bank_customers"},
      "field_mappings": {"marital": "marital", "age": "age"},
      "timestamp": "2024-01-15T10:30:02Z",
      "processing_time_ms": 150
    },
    "query_generation": {
      "sql_query": "SELECT * FROM bank_customers WHERE marital = 'married' AND age > 30 LIMIT 1000",
      "optimized": true,
      "estimated_rows": 1500,
      "tables_used": ["bank_customers"],
      "optimization_notes": ["Added LIMIT clause for safety"],
      "timestamp": "2024-01-15T10:30:03Z",
      "processing_time_ms": 800
    },
    "validation": {
      "is_valid": true,
      "issues": [],
      "warnings": ["Query returns large number of rows: 1500"],
      "sample_data": [
        {"age": 35, "job": "management", "marital": "married", "balance": 2143},
        {"age": 42, "job": "technician", "marital": "married", "balance": 1506}
      ],
      "row_count": 1500,
      "timestamp": "2024-01-15T10:30:04Z",
      "processing_time_ms": 200
    }
  }
}
```

### Get Segment Info
**GET** `/segment/{segment_id}`

Retrieve information about a created segment.

### Get Database Schema
**GET** `/schema`

Get current database schema information.

### Health Check
**GET** `/health`

Server health status endpoint.

## ⚙️ Advanced Configuration

### **Environment Variables**
All configuration values support environment variable overrides:

```bash
# Model Configuration
export OPENAI_MODEL="gpt-4.1"
export OPENAI_TEMPERATURE="0.1" 
export OPENAI_MAX_TOKENS="1000"

# Agent-Specific Models
export INTENT_PARSER_MODEL="gpt-4.1"
export QUERY_GENERATOR_MODEL="gpt-4.1"

# Performance Settings
export MAX_QUERY_ROWS="1000"
export DEFAULT_QUERY_LIMIT="1000"
export VALIDATION_SAMPLE_SIZE="5"
export MAX_SAFE_ROWS="100000"
export WARNING_ROW_THRESHOLD="50000"

# Timeouts
export INTENT_PARSER_TIMEOUT="15"
export QUERY_GENERATOR_TIMEOUT="20" 
export VALIDATION_TIMEOUT="10"
export ACTIVATION_TIMEOUT="25"
```

### **Agent Configuration**
Each agent loads configuration automatically:
- **Intent Parser**: Model selection, temperature, timeout settings
- **Query Generator**: Model, optimization rules, query limits, safety settings
- **Validator**: Performance thresholds, sample sizes, row count limits
- **Activator**: Timeout settings, downstream system configuration

### **Basic Environment Variables**
- `OPENAI_API_KEY`: Required for AI-powered query generation
- `OPENAI_MODEL`: Model to use (default: gpt-4.1)
- `KAGGLE_USERNAME`: For dataset access
- `KAGGLE_KEY`: Kaggle API key
- `DATABASE_PATH`: Path to local database file
- `MAX_QUERY_ROWS`: Maximum rows per query (default: 1000)

## 🔍 Example Queries

### Basic Segmentation
```
"Customers over 25 years old"
"Married customers with housing loans"
"High balance customers without personal loans"
```

### Advanced Criteria
```
"Customers contacted more than 3 times but never converted"
"Young professionals with tertiary education and no defaults"
"Retired customers with high balances who were contacted in May"
```

### Business-Specific Terms
```
"High-value prospects for mortgage products"
"At-risk customers for retention campaigns"
"Premium customers for exclusive offers"
```

## 🛡️ Security Considerations

### Data Protection
- No sensitive data stored in logs
- Read-only database access (SELECT operations only)
- Query validation prevents dangerous operations
- Local data processing (no external data transmission)

### Access Control
- OpenAI API key required for AI features
- Local file system access only
- Framework ready for authentication systems

### Compliance
- Local data processing maintains privacy
- Processing transparency for audit requirements
- Framework supports compliance features

## ⚠️ Current Limitations

### What's Simulated (Not Real)
- **Downstream Integrations**: Returns system names but doesn't actually connect to CRM/email platforms
- **Multi-Database**: Only supports single Kaggle dataset, not multiple data sources
- **Advanced Security**: Basic validation only, not full parameterized queries

### What's Real & Working
- **MCP Protocol**: Full implementation with Claude Desktop integration
- **AI Processing**: Real GPT-4.1 integration for natural language processing
- **SQL Generation**: Actual query creation and validation
- **HTTP APIs**: Working REST endpoints for testing and integration
- **Comprehensive Validation**: Extensive testing and validation infrastructure


## 🆘 Support

### Built-in Validation Tools
- `python validate_schemas.py` - Comprehensive schema validation
- `python validate_config_usage.py` - Configuration usage analysis  
- `python test_config_integration.py` - Integration testing
- `python generate_claude_config.py` - Setup assistance

### Community
- [GitHub Issues](https://github.com/tejasayya/SegmentMCP/issues) - Bug reports and feature requests
- [GitHub Discussions](https://github.com/tejasayya/SegmentMCP/discussions)

---
