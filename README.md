# Segmentation MCP Server

A Model Context Protocol (MCP) server for creating customer segments from natural language queries using bank customer data.

## Features

- 🤖 **Natural Language Processing**: Convert plain English queries into SQL segments
- 📊 **Real Data**: Uses Kaggle bank customer dataset (45,211 records)
- 🔍 **Query Validation**: Automatic SQL validation and optimization
- 🎯 **Segment Activation**: Simulates activation in downstream systems
- 🌐 **Multiple Interfaces**: MCP protocol + HTTP API wrapper
- ✅ **Demo Mode**: Works without OpenAI API for testing

## Quick Start

### 1. Installation

```bash
# Clone or download the project
cd SegmentMCP

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file with your API keys:

```env
OPENAI_API_KEY=your-openai-api-key-here
KAGGLE_USERNAME=your-kaggle-username
KAGGLE_KEY=your-kaggle-key
```

### 3. Run the Server

#### Option A: Demo Mode (No OpenAI required)
```bash
python demo_server.py
```

#### Option B: Full Mode (Requires OpenAI API)
```bash
python main.py
```

#### Option C: HTTP API Wrapper
```bash
python demo_http_wrapper.py
# Server runs on http://localhost:8001
```

## Usage Examples

### HTTP API

```bash
# Create a segment
curl -X POST http://localhost:8001/create-segment \
  -H "Content-Type: application/json" \
  -d '{"query": "Customers who have a housing loan and balance over 1000"}'

# Get database schema
curl http://localhost:8001/schema

# List available tools
curl http://localhost:8001/tools
```

### Sample Queries

- `"Customers who have a housing loan and balance over 1000"`
- `"Married customers with age over 30"`
- `"Customers with balance over 5000"`
- `"Customers with housing loan"`

### MCP Integration (Claude Desktop)

Add to your Claude Desktop config file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "segmentation-agent": {
      "command": "python",
      "args": ["C:\\path\\to\\SegmentMCP\\demo_server.py"],
      "env": {
        "OPENAI_API_KEY": "your-key-here",
        "KAGGLE_USERNAME": "your-username",
        "KAGGLE_KEY": "your-kaggle-key"
      }
    }
  }
}
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │───▶│   MCP Server     │───▶│   Kaggle Data   │
│ (Claude/Custom) │    │  (FastMCP)       │    │  (Bank Dataset) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Agent Pipeline │
                    │                  │
                    │ 1. Intent Parser │
                    │ 2. Data Mapper   │
                    │ 3. Query Gen     │
                    │ 4. Validator     │
                    │ 5. Activator     │
                    └──────────────────┘
```

## Available Tools

### 1. `create_segment`
Creates customer segments from natural language descriptions.

**Input**: `natural_language_query` (string)
**Output**: JSON with segment details, customer count, and sample data

### 2. `get_segment_info`
Retrieves information about a created segment.

**Input**: `segment_id` (string)
**Output**: Segment details and metadata

### 3. `get_database_schema`
Returns the database schema and sample data.

**Input**: None
**Output**: Complete schema with column types and sample values

## Dataset Information

The server uses the "Bank Term Deposit Subscription" dataset from Kaggle:
- **Records**: 45,211 bank customers
- **Columns**: 17 attributes (age, job, marital, education, balance, etc.)
- **Target**: Term deposit subscription (y/n)

### Key Columns:
- `age`: Customer age
- `job`: Job type (management, technician, etc.)
- `marital`: Marital status (married, single, divorced)
- `education`: Education level
- `balance`: Average yearly balance
- `housing`: Has housing loan (yes/no)
- `loan`: Has personal loan (yes/no)
- `y`: Subscribed to term deposit (yes/no)

## Development

### Project Structure
```
SegmentMCP/
├── agents/              # AI agents for processing
│   ├── intent_parser.py    # Natural language → criteria
│   ├── data_mapper.py      # Business terms → DB fields
│   ├── query_generator.py  # Criteria → SQL
│   ├── validation_agent.py # SQL validation
│   └── activation_agent.py # Segment activation
├── database/            # Data connectors
│   └── kaggle_connector.py # Kaggle dataset handler
├── models/              # Data schemas
│   └── schemas.py          # Pydantic models
├── main.py              # Full MCP server
├── demo_server.py       # Demo MCP server
├── demo_http_wrapper.py # HTTP API wrapper
└── requirements.txt     # Dependencies
```

### Testing

```bash
# Test demo server directly
python test_demo_direct.py

# Test HTTP API
python test_http_requests.py

# Test MCP protocol
python test_mcp_client.py
```

## Troubleshooting

### Common Issues

1. **OpenAI API Quota Exceeded**
   - Use `demo_server.py` instead of `main.py`
   - Demo mode works without OpenAI API

2. **Kaggle Authentication**
   - Ensure `KAGGLE_USERNAME` and `KAGGLE_KEY` are set
   - Download kaggle.json from Kaggle account settings

3. **Dependency Conflicts**
   - Use the exact versions in `requirements.txt`
   - Consider using a virtual environment

4. **MCP Connection Issues**
   - Ensure Claude Desktop config path is correct
   - Check that the Python path in config is absolute

### Version Compatibility

- **Python**: 3.8+
- **OpenAI**: 1.30.0-1.35.0 (for compatibility)
- **httpx**: 0.25.0 (specific version required)
- **MCP**: 1.0.0+

## License

This project is for educational and demonstration purposes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request